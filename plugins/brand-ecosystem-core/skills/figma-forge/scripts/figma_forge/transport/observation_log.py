"""figma-forge cross-build observation persistence — v1.5.0-beta.1.

A file-backed append log for :class:`ConcurrencyObservation` records,
enabling adaptive-concurrency smoothing to span process boundaries.

Why persist observations
-------------------------

v1.5.0-alpha.2 introduced multi-batch smoothing
(``AdaptiveConcurrency.window``), but the observation history lived
in a :class:`RestTransport` instance attribute — it evaporated when
the transport instance was garbage-collected or the process exited.
For a single long-running build that issues several batches, that's
fine. But for the common CI/CD pattern — each build is a fresh
process, each issues one batch — the window never accumulated more
than one observation, so smoothing was inert exactly where it was
most wanted.

``ObservationLog`` closes that gap. It writes each observation to a
JSONL file as the build runs, and seeds a new transport's history
from the file's recent records at construction. Smoothing then spans
builds: build N+1 sees builds N, N-1, … N-window+1.

Format
------

One JSON object per line (JSONL), each wrapping a serialized
observation with a log-supplied timestamp::

    {"logged_at": "2026-05-28T12:34:56.789+00:00",
     "observation": {"requests_total": 90, "requests_429": 6, ...}}

The wrapper keeps the log's own metadata (``logged_at``) separate
from the observation's fields, so :class:`ConcurrencyObservation`
itself never needs a timestamp field — the v1.4 dataclass is
unchanged.

Durability
----------

- **Append under an exclusive file lock** (``fcntl.flock`` on POSIX,
  ``msvcrt.locking`` on Windows, best-effort no-op elsewhere) so
  concurrent processes don't interleave partial lines.
- **Atomic trim**: when the file grows past ``max_records × 2``, the
  log rewrites it to the last ``max_records`` lines via a temp file
  and ``os.replace`` — amortized O(1) per append, never leaving a
  half-written file.
- **Corrupted-record tolerance**: a line that fails to parse is
  skipped on read, never raising. A crash mid-write (leaving a
  partial final line) costs at most one observation.

Usage
-----

.. code-block:: python

    import figma_forge as ff

    log = ff.ObservationLog("figma-forge-history.jsonl", max_records=100)
    rest = ff.RestTransport(
        pat="...",
        batch=ff.BatchPolicy(
            max_concurrency=4,
            adaptive=ff.AdaptiveConcurrency(window=5),
        ),
        observation_log=log,
    )
    # On construction, rest seeds its history from log's recent records.
    # On commit_session, rest appends the new observation to log.
    # Next build (new process) picks up where this one left off.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import socket
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from .adaptive_concurrency import ConcurrencyObservation


# ---- Per-process shard identity (v1.7.0-alpha.2) ----------------------
# A shard ID must be unique per concurrent writer and stable for that
# writer's lifetime (RFC v1.7 §5.2). It combines three tokens:
#   - pid: distinguishes processes on one host
#   - host token: a short stable hash of the hostname, so processes on
#     different hosts sharing a network mount don't collide on pid
#   - start token: a per-process nonce minted once at import, so a
#     reused pid (after a process exits) doesn't alias the old shard
# None of the tokens contains a '.', keeping shard filenames safe for
# the `{stem}.*{suffix}` glob and the `os.path` suffix logic.

def _compute_host_token() -> str:
    try:
        host = socket.gethostname() or "unknown"
    except Exception:  # pragma: no cover — gethostname is robust
        host = "unknown"
    return hashlib.sha256(host.encode("utf-8")).hexdigest()[:8]


_HOST_TOKEN = _compute_host_token()
_PROCESS_START_TOKEN = uuid4().hex[:8]


def _shard_id() -> str:
    """Return this process's shard identity: ``pid-host-start``."""
    return f"{os.getpid()}-{_HOST_TOKEN}-{_PROCESS_START_TOKEN}"


# Default age past which a *foreign* shard (one written by another
# process, not this one, and not the bare single-file path) is
# considered dead and reaped by compact() (RFC v1.7 §5.3). One week
# is deliberately conservative: a shard's mtime is the time of its
# last append, so a week of silence means the writing process is long
# gone (or so slow it has effectively stopped). Operators who want
# more aggressive cleanup pass a smaller value; passing None disables
# reaping entirely.
_DEFAULT_REAP_AFTER_SECONDS = 7 * 24 * 3600  # 604800.0

# Platform-aware advisory file locking. fcntl on POSIX, msvcrt on
# Windows, best-effort no-op elsewhere. Locking is a durability
# nicety, not a correctness requirement — the log tolerates the
# absence of it (worst case: two concurrent appends interleave, and
# the corrupted-record tolerance on read drops the mangled line).
try:
    import fcntl
    _LOCK_BACKEND = "fcntl"
except ImportError:  # pragma: no cover — non-POSIX
    try:
        import msvcrt
        _LOCK_BACKEND = "msvcrt"
    except ImportError:  # pragma: no cover — exotic platform
        _LOCK_BACKEND = "none"


@contextmanager
def _exclusive_lock(file_handle) -> Iterator[None]:
    """Best-effort exclusive lock around a file write."""
    if _LOCK_BACKEND == "fcntl":
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    elif _LOCK_BACKEND == "msvcrt":  # pragma: no cover — Windows
        try:
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
            yield
        finally:
            try:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
    else:  # pragma: no cover — no locking available
        yield


@dataclasses.dataclass
class ObservationLog:
    """A file-backed append log of :class:`ConcurrencyObservation`.

    Not frozen — the log wraps mutable on-disk state. The config
    fields (``path``, ``max_records``) are set at construction and
    not mutated thereafter; the mutation happens in the file.

    Parameters
    ----------
    path:
        Path to the JSONL file. Created on first append (including
        parent directories). Read methods tolerate a missing file
        (return empty).
    max_records:
        Soft cap on retained records. The file is trimmed to this
        many lines when it grows past ``max_records × 2`` — so the
        on-disk file may transiently hold up to ``2 × max_records``
        lines between trims, but ``read_recent`` always returns at
        most the requested count. Must be ``>= 1``. In sharded mode
        the cap applies *per shard*.
    shard_per_process:
        When ``True`` (v1.7.0-alpha.2), each writer process appends
        to its own shard file (``{stem}.{shard-id}{suffix}``) instead
        of the single shared ``path``. **Sharded appends take no
        exclusive lock** — each process owns its shard exclusively,
        which is the entire point: it sidesteps network-filesystem
        lock contention in high-fan-out CI. ``read_recent`` then
        globs all shards (plus a bare single-file ``path`` if present,
        for mode cross-compatibility) and merges them by ``logged_at``
        into one chronological stream. ``compact`` compacts each shard
        independently. Default ``False`` — byte-for-byte the v1.6
        single-file behavior. Dead-shard reaping (cleaning up shards
        from exited processes) arrives in v1.7.0-beta.1.
    """

    path: str | Path
    max_records: int = 100
    shard_per_process: bool = False

    def __post_init__(self) -> None:
        if self.max_records < 1:
            raise ValueError(
                f"max_records must be >= 1 (got {self.max_records})"
            )
        # Normalize to Path for internal use.
        self._path = Path(self.path)

    def _shard_path(self) -> Path:
        """This process's shard file: ``{stem}.{shard-id}{suffix}``."""
        return self._path.parent / (
            f"{self._path.stem}.{_shard_id()}{self._path.suffix}"
        )

    def _all_shard_paths(self) -> list[Path]:
        """All shard files plus a bare single-file path if present.

        Globs ``{stem}.*{suffix}`` for shards and includes a bare
        ``{stem}{suffix}`` if it exists, so a directory that mixes
        single-file and sharded history (e.g. after flipping the
        flag) is read completely — a mode switch never silently drops
        history (RFC v1.7 §5.4). Returns a deterministic order: bare
        first, then shards sorted by filename.
        """
        parent = self._path.parent
        if not parent.exists():
            return []
        stem, suffix = self._path.stem, self._path.suffix
        paths: list[Path] = []
        bare = parent / f"{stem}{suffix}"
        if bare.exists():
            paths.append(bare)
        paths.extend(sorted(parent.glob(f"{stem}.*{suffix}")))
        return paths

    def append(self, observation: ConcurrencyObservation) -> None:
        """Append one observation to the log.

        Wraps the observation with a UTC ``logged_at`` timestamp,
        serializes to a single JSONL line, and writes it. In
        single-file mode the write is guarded by an exclusive file
        lock; in sharded mode (``shard_per_process=True``) each
        process writes to its own shard **without a lock** (it owns
        the shard exclusively). Triggers an atomic per-file trim if
        the target has grown past ``max_records × 2``.
        """
        target = self._shard_path() if self.shard_per_process else self._path
        target.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "observation": dataclasses.asdict(observation),
        }
        line = json.dumps(record, ensure_ascii=False) + "\n"
        if self.shard_per_process:
            # Lock-free: this process exclusively owns its shard, so
            # there is no concurrent writer to interleave with. This
            # is the whole reason sharding exists.
            with open(target, "a", encoding="utf-8") as fh:
                fh.write(line)
        else:
            with open(target, "a", encoding="utf-8") as fh:
                with _exclusive_lock(fh):
                    fh.write(line)
        self._trim_if_needed(target)

    def read_recent(self, n: int | None = None) -> list[ConcurrencyObservation]:
        """Return the most recent observations, oldest-first.

        Parameters
        ----------
        n:
            Maximum number of observations to return (the most
            recent ``n``). ``None`` returns all retained records.

        Corrupted lines (unparseable JSON, missing fields, wrong
        shape) are silently skipped — the log never raises on read.
        A missing file returns an empty list. In sharded mode, all
        shards (plus a bare single-file path if present) are merged
        by ``logged_at`` into one oldest-first stream before the
        most-recent ``n`` are taken.
        """
        if self.shard_per_process:
            return self._read_recent_sharded(n)
        if not self._path.exists():
            return []
        out: list[ConcurrencyObservation] = []
        try:
            text = self._path.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover — race with deletion
            return []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            obs = _parse_line(line)
            if obs is not None:
                out.append(obs)
        if n is not None and n >= 0:
            return out[-n:] if n else []
        return out

    def _read_recent_sharded(
        self, n: int | None = None
    ) -> list[ConcurrencyObservation]:
        """Merge all shards by ``logged_at``, oldest-first, last ``n``.

        ISO-8601 UTC timestamps (what :meth:`append` writes) sort
        lexicographically in chronological order. A record with no
        ``logged_at`` (a bare/legacy line) carries an empty string,
        which sorts first — treated as oldest. The sort is stable, so
        records sharing a timestamp keep their per-shard read order.
        """
        records: list[tuple[str, ConcurrencyObservation]] = []
        for shard in self._all_shard_paths():
            try:
                text = shard.read_text(encoding="utf-8")
            except OSError:  # pragma: no cover — race with deletion
                continue
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                rec = _parse_record(line)
                if rec is not None:
                    records.append(rec)
        records.sort(key=lambda r: r[0])
        out = [obs for _, obs in records]
        if n is not None and n >= 0:
            return out[-n:] if n else []
        return out

    def __len__(self) -> int:
        """Number of valid (parseable) records currently in the file."""
        return len(self.read_recent())

    def clear(self) -> None:
        """Remove all records.

        In single-file mode, deletes the file if present. In sharded
        mode, deletes every shard (plus a bare single-file path if
        present) — ``clear`` means all records, across all writers.
        """
        if self.shard_per_process:
            for shard in self._all_shard_paths():
                try:
                    shard.unlink()
                except OSError:  # pragma: no cover — race with deletion
                    pass
        elif self._path.exists():
            self._path.unlink()

    def compact(
        self,
        keep: int | None = None,
        *,
        reap_after_seconds: "float | None" = _DEFAULT_REAP_AFTER_SECONDS,
    ) -> int:
        """Rewrite the log to its last ``keep`` valid records on demand.

        Unlike the automatic amortized trim (which only fires when the
        file grows past ``max_records × 2`` during an append),
        ``compact`` runs **unconditionally** — operators call it to
        reclaim space at a known-quiet moment (e.g. the end of a CI
        run) or to purge accumulated corruption. The rewrite is atomic
        (temp file + ``os.replace``) and runs under the same exclusive
        lock as :meth:`append`, so it is safe against concurrent
        writers.

        Two things are removed:

        1. **Corrupted / blank lines** — any line that does not parse
           into a valid record is dropped, regardless of ``keep``.
        2. **Overflow records** — if more than ``keep`` valid records
           remain after step 1, the oldest are dropped, keeping the
           most recent ``keep``.

        Dead-shard reaping (v1.7.0-beta.1, sharded mode only)
        -----------------------------------------------------

        In sharded mode, ``compact`` additionally **reaps dead
        shards** — shard files left behind by processes that have
        exited. A shard is reaped when its mtime (the time of its last
        append) is older than ``reap_after_seconds``. Two files are
        **never** reaped, regardless of age:

        - **This process's own shard** — it is alive and may still
          append.
        - **A bare single-file ``path``** — it belongs to the legacy
          single-file mode, not to any dead process; an operator may
          keep it intentionally, so reaping leaves it alone (it is
          still compacted in place).

        Reaping is **on by default** with a conservative one-week
        threshold; pass ``reap_after_seconds=None`` to disable it (the
        v1.7.0-alpha.2 behavior — compact each shard, reap none). The
        records in a reaped shard count toward the returned removed
        total. In single-file mode the parameter is ignored (there
        are no shards).

        Parameters
        ----------
        keep:
            How many of the most recent valid records to retain.
            ``None`` (default) keeps ``max_records``. Must be ``>= 1``
            when given — to drop everything, use :meth:`clear`.
        reap_after_seconds:
            Age (seconds) past which a foreign shard is reaped.
            Default one week; ``None`` disables reaping. Ignored in
            single-file mode.

        Returns
        -------
        int:
            The number of lines removed (corrupted lines plus overflow
            records, plus all records in any reaped shards). ``0`` if
            nothing needed removing — in which case no file is
            rewritten or deleted. In sharded mode, this is the total
            across all shards.
        """
        if keep is None:
            keep = self.max_records
        if keep < 1:
            raise ValueError(f"keep must be >= 1 (got {keep}); use clear() to drop all")
        if not self.shard_per_process:
            return self._compact_one(self._path, keep)
        # Sharded: compact each shard, and reap dead foreign shards.
        own = self._shard_path()
        bare = self._path.parent / f"{self._path.stem}{self._path.suffix}"
        now = time.time()
        total_removed = 0
        for shard in self._all_shard_paths():
            if (
                reap_after_seconds is not None
                and shard != own       # our shard is alive
                and shard != bare      # bare file is not a dead process
            ):
                try:
                    age = now - shard.stat().st_mtime
                except OSError:  # pragma: no cover — race with deletion
                    age = 0.0
                if age > reap_after_seconds:
                    total_removed += self._reap_shard(shard)
                    continue
            total_removed += self._compact_one(shard, keep)
        return total_removed

    def _reap_shard(self, path: Path) -> int:
        """Delete a dead shard, returning its valid record count.

        Counts the non-empty lines (so the tally matches compact's
        "lines removed" semantics), then unlinks the file. Tolerant of
        a concurrent deletion — a vanished shard contributes 0.
        """
        removed = 0
        try:
            removed = len(
                [ln for ln in path.read_text(encoding="utf-8").splitlines()
                 if ln.strip()]
            )
        except OSError:  # pragma: no cover — race with deletion
            return 0
        try:
            path.unlink()
        except OSError:  # pragma: no cover — race with deletion
            pass
        return removed

    def _compact_one(self, path: Path, keep: int) -> int:
        """Compact a single file to its last ``keep`` valid records.

        Atomic (temp + ``os.replace``) under an exclusive lock. In
        sharded mode the lock is uncontended (one writer per shard);
        in single-file mode it guards against concurrent appends.
        Returns the number of lines removed.
        """
        if not path.exists():
            return 0
        with open(path, "a", encoding="utf-8") as lock_fh:
            with _exclusive_lock(lock_fh):
                try:
                    lines = path.read_text(encoding="utf-8").splitlines()
                except OSError:  # pragma: no cover — race with deletion
                    return 0
                non_empty = [ln for ln in lines if ln.strip()]
                before = len(non_empty)
                valid = [ln for ln in non_empty if _parse_line(ln) is not None]
                kept = valid[-keep:]
                removed = before - len(kept)
                if removed <= 0:
                    # Already clean and within budget — don't rewrite.
                    return 0
                tmp = path.with_suffix(path.suffix + ".tmp")
                tmp.write_text(
                    ("\n".join(kept) + "\n") if kept else "",
                    encoding="utf-8",
                )
                os.replace(tmp, path)
                return removed

    def _trim_if_needed(self, target: "Path | None" = None) -> None:
        """Rewrite a file to the last ``max_records`` lines if it has
        grown past ``max_records × 2``.

        Operates on ``target`` (the shard just appended to, in sharded
        mode) or ``self._path`` (single-file mode). Amortized O(1) per
        append: the expensive full rewrite happens only once every
        ``max_records`` appends. Atomic via temp file + ``os.replace``
        — a crash during trim leaves either the old file intact or the
        new file complete, never a partial.
        """
        path = target if target is not None else self._path
        if not path.exists():
            return
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:  # pragma: no cover — race
            return
        # Only count non-empty lines toward the threshold.
        non_empty = [ln for ln in lines if ln.strip()]
        if len(non_empty) <= self.max_records * 2:
            return
        keep = non_empty[-self.max_records:]
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text("\n".join(keep) + "\n", encoding="utf-8")
        os.replace(tmp, path)


def _parse_record(line: str) -> "tuple[str, ConcurrencyObservation] | None":
    """Parse one JSONL line into ``(logged_at, observation)``, or None.

    Like :func:`_parse_line` but also returns the wrapper's
    ``logged_at`` string (empty string for a bare observation dict
    with no wrapper). The timestamp is needed to merge records across
    shards in chronological order (v1.7.0-alpha.2). Returns None for
    any parse failure.
    """
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    logged_at = obj.get("logged_at", "")
    if not isinstance(logged_at, str):
        logged_at = ""
    obs_dict = obj.get("observation", obj)
    if not isinstance(obs_dict, dict):
        return None
    allowed = {f.name for f in dataclasses.fields(ConcurrencyObservation)}
    filtered = {k: v for k, v in obs_dict.items() if k in allowed}
    try:
        return (logged_at, ConcurrencyObservation(**filtered))
    except TypeError:
        # Missing a required field, or wrong type.
        return None


def _parse_line(line: str) -> ConcurrencyObservation | None:
    """Parse one JSONL line into a ConcurrencyObservation, or None.

    Accepts both the wrapper format ``{"logged_at": ...,
    "observation": {...}}`` and a bare observation dict (forward/
    backward tolerant). Returns None for any parse failure.
    """
    rec = _parse_record(line)
    return rec[1] if rec is not None else None


__all__ = ["ObservationLog"]
