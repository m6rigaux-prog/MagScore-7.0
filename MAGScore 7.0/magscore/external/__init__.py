"""
MAGScore 6.1 — External Module
===============================
Gestion des données externes et normalisation API.

Contient :
- api_handler : gestionnaire des appels API (NE PAS MODIFIER)
- normalize_api : normalisation RAW DATA ONLY (Sanitizer)
"""

from .normalize_api import (
    normalize,
    normalize_match_data,
    is_opaque_metric,
    is_raw_metric,
    validate_data_integrity,
    get_rejected_metrics,
    get_opaque_metrics_blacklist,
    get_raw_data_whitelist,
    SanitizationError,
    OPAQUE_METRICS_BLACKLIST,
    RAW_DATA_WHITELIST,
)

__all__ = [
    # Main functions
    "normalize",
    "normalize_match_data",
    # Validation functions
    "is_opaque_metric",
    "is_raw_metric",
    "validate_data_integrity",
    "get_rejected_metrics",
    # Getters
    "get_opaque_metrics_blacklist",
    "get_raw_data_whitelist",
    # Exception
    "SanitizationError",
    # Constants
    "OPAQUE_METRICS_BLACKLIST",
    "RAW_DATA_WHITELIST",
]
