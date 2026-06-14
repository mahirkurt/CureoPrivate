"""figma-forge transport error model — v1.1.0-alpha.

A single exception hierarchy that every transport adapter raises
into, so pipeline code can `except TransportError` regardless of
which channel actually fired.

Adapter-specific errors are caught at the adapter boundary and
re-raised as one of these normalized shapes. Each carries
``adapter_id`` and ``operation`` for diagnostic traceability without
leaking channel-specific minutiae upward.
"""

from __future__ import annotations


class TransportError(Exception):
    """Base class for any error originating in a transport adapter.

    Always carries the offending operation name and the adapter id so
    that diagnostics can pinpoint the failure even after the error
    bubbles up through the pipeline runner.

    Parameters
    ----------
    message:
        Human-readable description of the failure.
    operation:
        The transport operation that triggered the error (e.g.
        ``"create_variable_collection"``). Use ``""`` for errors
        raised outside of an operation context.
    adapter_id:
        The stable identifier of the adapter that raised the error
        (e.g. ``"rest-v1"``, ``"plugin-capture"``).
    cause:
        The original channel-specific exception, when applicable.
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str = "",
        adapter_id: str = "",
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.adapter_id = adapter_id
        self.cause = cause

    def __str__(self) -> str:  # pragma: no cover
        parts = [self.args[0] if self.args else self.__class__.__name__]
        if self.operation:
            parts.append(f"op={self.operation}")
        if self.adapter_id:
            parts.append(f"adapter={self.adapter_id}")
        return " · ".join(parts)


# ---------------------------------------------------------------------------
# Subclasses — one per failure mode
# ---------------------------------------------------------------------------

class AuthenticationError(TransportError):
    """Credential is missing or invalid (e.g. Figma PAT not set, expired)."""


class AuthorizationError(TransportError):
    """Credential is valid but lacks the required scope or plan tier.

    Common case: a non-Enterprise PAT trying to call the Variables
    endpoint — the request authenticates but is forbidden.
    """


class NotFoundError(TransportError):
    """The requested resource (file, variable, collection) does not exist."""


class ValidationError(TransportError):
    """The operation arguments violate Figma's constraints.

    Examples: invalid mode name, type mismatch in variable value,
    component variant axes don't form a valid product.
    """


class ConflictError(TransportError):
    """The operation would conflict with existing state.

    Idempotency guard: an adapter raises this rather than silently
    overwriting unless the caller passed an explicit ``update=True``.
    """


class RateLimitError(TransportError):
    """The channel rate-limited the request.

    Carries a ``retry_after_seconds`` hint when the upstream provided
    one (e.g. ``Retry-After`` HTTP header). Pipeline can back off.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: float | None = None,
        **kwargs,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class CapabilityUnsupportedError(TransportError):
    """The adapter doesn't implement the requested operation.

    Routed-pipeline code expects to catch this and fall through to
    the next adapter in the preference list. Direct callers should
    treat it as a programming error.
    """


class UpstreamUnavailableError(TransportError):
    """The channel itself is down (network, service outage, etc.).

    Distinguished from ``RateLimitError`` (retry possible after delay)
    and from per-operation failures (the channel itself is intact).
    """


__all__ = [
    "TransportError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "CapabilityUnsupportedError",
    "UpstreamUnavailableError",
]
