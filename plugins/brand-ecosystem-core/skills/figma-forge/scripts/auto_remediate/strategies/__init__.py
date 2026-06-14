"""figma-forge auto-remediate strategies package.

Each module in this package defines one :class:`RemediationStrategy`
subclass and uses the :func:`@register_strategy(gate_id)` decorator to
self-register into the strategy registry. Importing this package
side-effect-loads all strategies.

v0.3.0-alpha.1 strategies (MVP):
    g13_alias_resolution         — G13 DTCG alias path normalizer
    g14_icons_are_components     — G14 SVG canonical normalizer
    g17_code_connect_badges      — G17 Code Connect mapping generator

v0.3.0-beta strategies (Sprint 2-3):
    g02_composite_typography     — G02 composite typography → text-styles router
    g07_variant_matrix           — G07 variant Cartesian product auto-calc
    g08_component_naming         — G08 snake_case → PascalCase rewriter

v0.3.0-rc strategies (Sprint 4-5):
    g15_icon_size_grid           — G15 icon dimension grid snapping
"""

from . import g02_composite_typography  # noqa: F401
from . import g07_variant_matrix  # noqa: F401
from . import g08_component_naming  # noqa: F401
from . import g13_alias_resolution  # noqa: F401
from . import g14_icons_are_components  # noqa: F401
from . import g15_icon_size_grid  # noqa: F401
from . import g17_code_connect_badges  # noqa: F401

__all__ = [
    "g02_composite_typography",
    "g07_variant_matrix",
    "g08_component_naming",
    "g13_alias_resolution",
    "g14_icons_are_components",
    "g15_icon_size_grid",
    "g17_code_connect_badges",
]
