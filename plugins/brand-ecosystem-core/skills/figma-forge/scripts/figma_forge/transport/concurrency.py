"""figma-forge concurrency detection — v1.2.0.

Detects whether a Figma file was modified by another editor between a
baseline snapshot and a later check — the classic "someone else was
editing while my build ran" hazard. The mechanism is intentionally
simple and channel-agnostic: it compares the file's ``last_modified``
timestamp (from :meth:`TransportAdapter.get_file`) at two points in
time.

Usage shape
-----------

.. code-block:: python

    baseline = transport.get_file(key=file_key).last_modified
    # ... run the build ...
    report = check_concurrency(transport, file_key=file_key,
                               baseline_modified=baseline)
    if report.has_concurrent_edit:
        warn(report.detail)

The check is **best-effort**. Capture-mode adapters
(``PluginCaptureTransport``) cannot read live file state and raise
``CapabilityUnsupportedError`` from ``get_file``; in that case the
report is returned with ``checked=False`` rather than failing the
build. A baseline of ``""`` (empty) — common for adapters that don't
populate ``last_modified`` — also yields ``checked=False``, since
there is nothing meaningful to compare.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import CapabilityUnsupportedError, TransportError
from .protocol import TransportAdapter


@dataclass(frozen=True)
class ConcurrencyReport:
    """The result of a concurrency check.

    Attributes
    ----------
    file_key:
        The file that was checked.
    baseline_modified:
        The ``last_modified`` timestamp captured before the build.
    current_modified:
        The ``last_modified`` timestamp at check time. Empty when the
        check could not be performed.
    has_concurrent_edit:
        ``True`` when ``current_modified`` differs from
        ``baseline_modified`` (and both are non-empty) — i.e. the file
        changed during the window. ``False`` when unchanged or
        unchecked.
    checked:
        ``True`` when a meaningful comparison was made (both
        timestamps available); ``False`` when the adapter could not
        read live state or the baseline was empty.
    detail:
        A human-readable summary suitable for a warning message.
    """

    file_key: str
    baseline_modified: str
    current_modified: str
    has_concurrent_edit: bool
    checked: bool
    detail: str = ""


def check_concurrency(
    transport: TransportAdapter, *, file_key: str, baseline_modified: str,
) -> ConcurrencyReport:
    """Compare the file's current ``last_modified`` against a baseline.

    Returns a :class:`ConcurrencyReport`. Never raises for the normal
    "can't check" cases (unsupported adapter, empty baseline); those
    are reported as ``checked=False``. Genuinely unexpected transport
    errors are also swallowed into ``checked=False`` with the error in
    ``detail``, because a concurrency check should never be the thing
    that fails an otherwise-successful build.
    """
    if not baseline_modified:
        return ConcurrencyReport(
            file_key=file_key, baseline_modified="", current_modified="",
            has_concurrent_edit=False, checked=False,
            detail="No baseline timestamp available; concurrency not checked.",
        )

    try:
        current = transport.get_file(key=file_key).last_modified
    except CapabilityUnsupportedError:
        return ConcurrencyReport(
            file_key=file_key, baseline_modified=baseline_modified,
            current_modified="", has_concurrent_edit=False, checked=False,
            detail=(f"Adapter {transport.adapter_id()} cannot read live "
                    f"file state; concurrency not checked."),
        )
    except TransportError as e:
        return ConcurrencyReport(
            file_key=file_key, baseline_modified=baseline_modified,
            current_modified="", has_concurrent_edit=False, checked=False,
            detail=f"Concurrency check failed: {e}",
        )

    if not current:
        return ConcurrencyReport(
            file_key=file_key, baseline_modified=baseline_modified,
            current_modified="", has_concurrent_edit=False, checked=False,
            detail="Current timestamp unavailable; concurrency not checked.",
        )

    changed = current != baseline_modified
    detail = (
        f"⚠ File {file_key} was modified during the build "
        f"(baseline {baseline_modified} → now {current}). "
        f"Another editor may have made concurrent changes."
        if changed else
        f"File {file_key} unchanged during the build ({current})."
    )
    return ConcurrencyReport(
        file_key=file_key, baseline_modified=baseline_modified,
        current_modified=current, has_concurrent_edit=changed,
        checked=True, detail=detail,
    )


__all__ = ["ConcurrencyReport", "check_concurrency"]
