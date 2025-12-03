"""
MAGScore 6.2 — Orchestration Module v2.5
=========================================
Orchestre le pipeline complet et valide la conformité.

Contient :
- Pipeline v2.5 : orchestrateur principal avec PatternEngine, SignalMemory, MatchFlow
- lexicon_guard v2 : validation du vocabulaire
"""

from .pipeline import (
    Pipeline,
    PipelineError,
    NormalizationError,
    SignalExtractionError,
    ReportGenerationError,
    LexiconViolationError,
    PIPELINE_VERSION,
)
from .lexicon_guard import (
    validate,
    find_violations,
    is_clean,
    is_term_forbidden,
    is_term_allowed,
    LexiconGuardError,
    BLACKLIST,
    WHITELIST,
)

__all__ = [
    # Pipeline v2.5
    "Pipeline",
    "PipelineError",
    "NormalizationError",
    "SignalExtractionError",
    "ReportGenerationError",
    "LexiconViolationError",
    "PIPELINE_VERSION",
    # Lexicon Guard v2
    "validate",
    "find_violations",
    "is_clean",
    "is_term_forbidden",
    "is_term_allowed",
    "LexiconGuardError",
    "BLACKLIST",
    "WHITELIST",
]
