"""
MAGScore 6.2 — Engine Module
=============================
Contient le cœur du système comportemental :
- BehaviorEngine : moteur de détection des comportements v2.3
- PatternEngine : détection de patterns composites v1.0
- SignalMemory : lisseur statistique v1.0
- MatchFlowReconstructor : reconstruction chronologique v1.0
- BEHAVIOR_DEFINITIONS : définitions officielles des comportements
- Constantes : seuils, facteurs de pondération, time slices
"""

from .behavior_engine import (
    BehaviorEngine,
    BehaviorStatus,
    TimeSlice,
    create_behavior_engine,
    ENGINE_VERSION,
)

from .pattern_engine import (
    PatternEngine,
    PATTERN_RULES,
    PATTERN_ENGINE_VERSION,
    create_pattern_engine,
)

from .signal_memory import (
    SignalMemory,
    SIGNAL_MEMORY_VERSION,
    DEFAULT_MAX_MEMORY,
    create_signal_memory,
)

from .match_flow import (
    MatchFlowReconstructor,
    MATCH_FLOW_VERSION,
    PHASE_LABELS,
    MIN_PHASES,
    MAX_PHASES,
    create_match_flow_reconstructor,
)

from .definitions import (
    BEHAVIOR_DEFINITIONS,
    SIGNAL_ACTIVATION_THRESHOLD,
    MIN_REQUIRED_SIGNALS,
    PONDERATION_FACTOR,
    TIME_SLICES,
    CONTRADICTION_PAIRS,
    ALL_REQUIRED_SIGNALS,
    SIGNAL_TO_MODULE,
    CATEGORIES,
    BEHAVIOR_CODES,
    PRIORITY_ZONES,
    get_behavior,
    get_behaviors_by_category,
    get_behaviors_by_priority_zone,
    get_contradicting_behaviors,
    are_behaviors_contradicting,
    validate_behavior_code,
    validate_signal_key,
    get_required_signals_for_behavior,
)

__all__ = [
    # BehaviorEngine
    "BehaviorEngine",
    "BehaviorStatus",
    "TimeSlice",
    "create_behavior_engine",
    "ENGINE_VERSION",
    # PatternEngine (PARTIE 5)
    "PatternEngine",
    "PATTERN_RULES",
    "PATTERN_ENGINE_VERSION",
    "create_pattern_engine",
    # SignalMemory (PARTIE 5)
    "SignalMemory",
    "SIGNAL_MEMORY_VERSION",
    "DEFAULT_MAX_MEMORY",
    "create_signal_memory",
    # MatchFlowReconstructor (PARTIE 5)
    "MatchFlowReconstructor",
    "MATCH_FLOW_VERSION",
    "PHASE_LABELS",
    "MIN_PHASES",
    "MAX_PHASES",
    "create_match_flow_reconstructor",
    # Definitions
    "BEHAVIOR_DEFINITIONS",
    # Constants
    "SIGNAL_ACTIVATION_THRESHOLD",
    "MIN_REQUIRED_SIGNALS",
    "PONDERATION_FACTOR",
    "TIME_SLICES",
    "CONTRADICTION_PAIRS",
    "ALL_REQUIRED_SIGNALS",
    "SIGNAL_TO_MODULE",
    "CATEGORIES",
    "BEHAVIOR_CODES",
    "PRIORITY_ZONES",
    # Helper functions
    "get_behavior",
    "get_behaviors_by_category",
    "get_behaviors_by_priority_zone",
    "get_contradicting_behaviors",
    "are_behaviors_contradicting",
    "validate_behavior_code",
    "validate_signal_key",
    "get_required_signals_for_behavior",
]
