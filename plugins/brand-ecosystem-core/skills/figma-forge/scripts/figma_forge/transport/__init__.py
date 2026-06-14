"""figma-forge transport layer — v1.1.0-alpha.

Public re-exports for the transport package. Composes with the
top-level ``figma_forge`` package; downstream code should import via
``import figma_forge as ff`` rather than reaching directly into
submodules.
"""

from .capability_matrix import (
    ADAPTER_MCP_CURSOR,
    ADAPTER_PLUGIN_CAPTURE,
    ADAPTER_REST,
    ADAPTER_STUB,
    CAPABILITY_MATRIX,
    CapabilityCell,
    CapabilityLevel,
    adapters_supporting,
    capability,
    supported_operations,
)
from .errors import (
    AuthenticationError,
    AuthorizationError,
    CapabilityUnsupportedError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    TransportError,
    UpstreamUnavailableError,
    ValidationError,
)
from .backoff import BackoffPolicy
from .batch_policy import BatchPolicy
from .adaptive_concurrency import AdaptiveConcurrency, ConcurrencyObservation
from .observation_log import ObservationLog
from .concurrency import ConcurrencyReport, check_concurrency
from .plan_validation import PlanValidationReport, PriorState, validate_mcp_plan
from .plan_runner import PlanRunner, PlanRunResult, StepResult, DispatchResponse
from .plan_graph import plan_execution_layers
from .mcp_cursor import McpCursorTransport
from .plugin_capture import PluginCaptureTransport
from .protocol import (
    TRANSPORT_OPERATIONS,
    AuthRequirement,
    CodeConnectMapping,
    CodeConnectRef,
    CollectionRef,
    ComponentGeometry,
    ComponentRef,
    ComponentSetRef,
    InstanceRef,
    Effect,
    FileKind,
    FileRef,
    PageRef,
    Paint,
    PaintType,
    PublishRef,
    SessionResult,
    SessionToken,
    StyleRef,
    TextStyleProperties,
    TransportAdapter,
    VariableRef,
    VariableType,
    VariableValue,
    VariantSpec,
)
from .rest import RestTransport
from .router import TransportRouter
from .stub import StubTransport

__all__ = [
    # Protocol & types
    "TransportAdapter",
    "TRANSPORT_OPERATIONS",
    "FileRef", "PageRef", "CollectionRef", "VariableRef",
    "StyleRef", "ComponentRef", "ComponentSetRef",
    "CodeConnectRef", "PublishRef", "InstanceRef",
    "Paint", "PaintType", "TextStyleProperties", "Effect",
    "ComponentGeometry", "VariantSpec", "CodeConnectMapping",
    "SessionToken", "SessionResult", "AuthRequirement",
    "FileKind", "VariableType", "VariableValue",
    # Errors
    "TransportError",
    "AuthenticationError", "AuthorizationError",
    "NotFoundError", "ValidationError", "ConflictError",
    "RateLimitError", "CapabilityUnsupportedError",
    "UpstreamUnavailableError",
    # Adapters
    "StubTransport", "PluginCaptureTransport", "RestTransport",
    "McpCursorTransport",
    # Backoff
    "BackoffPolicy",
    "BatchPolicy",
    "AdaptiveConcurrency", "ConcurrencyObservation",
    "ObservationLog",
    # Concurrency
    "ConcurrencyReport", "check_concurrency",
    # Plan validation
    "PlanValidationReport", "PriorState", "validate_mcp_plan",
    # Plan runner
    "PlanRunner", "PlanRunResult", "StepResult", "DispatchResponse",
    "plan_execution_layers",
    # Router & capability
    "TransportRouter",
    "ADAPTER_STUB", "ADAPTER_PLUGIN_CAPTURE",
    "ADAPTER_REST", "ADAPTER_MCP_CURSOR",
    "CAPABILITY_MATRIX", "CapabilityCell", "CapabilityLevel",
    "adapters_supporting", "supported_operations", "capability",
]
