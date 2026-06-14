"""figma-forge transport router — v1.1.0-alpha.

The router selects, per operation, which adapter to dispatch to,
based on:

1. **Operator preference** — an ordered list of adapter ids
2. **Capability availability** — adapter must claim to support the op
3. **Authentication availability** — adapter must have valid credentials

When no preferred adapter can satisfy the operation, the router falls
back to the stub adapter and logs a warning so the operator can see
which operations were not actually applied.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .capability_matrix import (
    ADAPTER_STUB,
    adapters_supporting,
    capability,
)
from .errors import CapabilityUnsupportedError
from .protocol import TransportAdapter

logger = logging.getLogger("figma_forge.transport.router")


@dataclass
class TransportRouter:
    """Selects per-operation adapter from a preference-ordered set.

    Parameters
    ----------
    adapters:
        Dict mapping adapter_id → adapter instance. **Must** include
        the stub adapter at id ``"stub"`` as the always-available
        fallback; the router enforces this at construction.
    preferences:
        Ordered list of adapter ids. For each operation, the router
        tries each preference in order and returns the first adapter
        that supports the operation **and** has its credentials
        present.

    Example
    -------
    >>> router = TransportRouter(
    ...     adapters={
    ...         "stub": StubTransport(),
    ...         "plugin-capture": PluginCaptureTransport(),
    ...         "rest-v1": RestTransport(),
    ...     },
    ...     preferences=["rest-v1", "plugin-capture", "stub"],
    ... )
    >>> adapter = router.select("create_variable_collection")
    >>> # → RestTransport if PAT set, else PluginCaptureTransport, else StubTransport
    """

    adapters: dict[str, TransportAdapter]
    preferences: list[str] = field(default_factory=list)
    fallback_warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if ADAPTER_STUB not in self.adapters:
            raise ValueError(
                "TransportRouter requires a stub adapter at id 'stub' as "
                "the always-available fallback."
            )
        if not self.preferences:
            # Default preferences: REST → PluginCapture → Stub
            self.preferences = list(self.adapters.keys())
            if ADAPTER_STUB in self.preferences:
                self.preferences.remove(ADAPTER_STUB)
            self.preferences.append(ADAPTER_STUB)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select(self, operation: str) -> TransportAdapter:
        """Return the adapter that should handle ``operation``.

        Iterates the preference list:
        - skips adapters not in ``self.adapters``
        - skips adapters whose ``supports(operation)`` returns False
        - skips adapters whose ``authentication_required().needs_credentials``
          is True but credentials are absent (when the adapter exposes
          a ``has_credentials()`` method)
        Falls back to the stub adapter when no preference matches.
        """
        for adapter_id in self.preferences:
            adapter = self.adapters.get(adapter_id)
            if adapter is None:
                continue
            if not adapter.supports(operation):
                continue
            # Credential gate: if adapter declares it needs credentials,
            # check whether it claims to have them.
            auth = adapter.authentication_required()
            if auth.needs_credentials:
                if hasattr(adapter, "has_credentials"):
                    if not adapter.has_credentials():
                        logger.debug(
                            "router: %s declines %s (no credentials)",
                            adapter_id, operation,
                        )
                        continue
            return adapter
        # Final fallback: stub
        msg = (
            f"router: no preferred adapter supports '{operation}'; "
            f"falling back to stub. Preference order was "
            f"{self.preferences}."
        )
        logger.warning(msg)
        self.fallback_warnings.append(msg)
        return self.adapters[ADAPTER_STUB]

    # ------------------------------------------------------------------
    # Diagnostic queries
    # ------------------------------------------------------------------

    def candidate_chain(self, operation: str) -> list[str]:
        """Return the candidate adapter ids in preference order.

        Diagnostic helper — shows what the router would consider
        for ``operation``, irrespective of credential availability.
        """
        return [
            adapter_id
            for adapter_id in self.preferences
            if adapter_id in self.adapters
            and self.adapters[adapter_id].supports(operation)
        ]

    def coverage_summary(self, operations: list[str]) -> dict[str, list[str]]:
        """For each operation, list the adapters that would handle it.

        Returns ``{operation: [adapter_id_chain, ...]}``. Useful for
        printing a pre-run "this is what will happen" summary.
        """
        return {op: self.candidate_chain(op) for op in operations}


__all__ = ["TransportRouter"]
