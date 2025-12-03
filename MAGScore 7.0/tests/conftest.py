"""
MAGScore 6.1 — Pytest Configuration
=====================================
Configuration centralisée pour la suite de tests.
Fixtures adaptées à BehaviorEngine v2.1 et Raw Data Sanitizer.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


# =============================================================================
# FIXTURES — DONNÉES NORMALISÉES
# =============================================================================

@pytest.fixture
def sample_normalized_data():
    """Fixture : données normalisées de test (format API sanitizé)."""
    return {
        'match_id': 'test_match_001',
        'timestamp': '2025-01-01T15:00:00Z',
        'home_team': {
            'name': 'Team A',
            'possession_percentage': 55,
            'shots_total': 8,
            'shots_on_target': 3,
            'fouls_committed': 12,
            'duels_won': 45,
            'passes_completed': 320,
        },
        'away_team': {
            'name': 'Team B',
            'possession_percentage': 45,
            'shots_total': 6,
            'shots_on_target': 2,
            'fouls_committed': 8,
            'duels_won': 38,
            'passes_completed': 280,
        },
        'events': [],
        'metadata': {
            'source': 'test',
            'sanitized': True
        }
    }


@pytest.fixture
def sample_raw_api_data():
    """Fixture : données API brutes (avant sanitization)."""
    return {
        'match_id': 'test_match_001',
        'shots': 14,
        'passes': 600,
        'fouls': 20,
        'possession': 55,
        'momentum': 0.75,           # Doit être rejeté
        'pressure_index': 45,       # Doit être rejeté
        'attack_strength': 80,      # Doit être rejeté
    }


# =============================================================================
# FIXTURES — TIME SLICES
# =============================================================================

@pytest.fixture
def sample_time_slices_stb01():
    """Fixture : time slices pour activer STB_01 (Effondrement Structurel)."""
    return {
        "global": {},
        "last_15_min": {
            "low_block_drop": 0.8,
            "xg_against_spike": 0.75
        }
    }


@pytest.fixture
def sample_time_slices_stb02():
    """Fixture : time slices pour activer STB_02 (Verrouillage Tactique)."""
    return {
        "global": {
            "high_compactness": 0.85,
            "successful_low_block": 0.78
        },
        "last_15_min": {}
    }


@pytest.fixture
def sample_time_slices_int01():
    """Fixture : time slices pour activer INT_01 (Surge de Pressing)."""
    return {
        "global": {
            "pressing_wave": 0.9,
            "high_duel_pressure": 0.82
        },
        "last_15_min": {}
    }


@pytest.fixture
def sample_time_slices_int02():
    """Fixture : time slices pour activer INT_02 (Déclin Physique)."""
    return {
        "global": {},
        "last_15_min": {
            "running_distance_drop": 0.7,
            "duel_loss_spike": 0.65
        }
    }


@pytest.fixture
def sample_time_slices_psy01():
    """Fixture : time slices pour activer PSY_01 (Frustration Active)."""
    return {
        "global": {},
        "last_15_min": {
            "fouls_spike": 0.88,
            "protest_pattern": 0.72
        }
    }


@pytest.fixture
def sample_time_slices_psy02():
    """Fixture : time slices pour activer PSY_02 (Résilience)."""
    return {
        "global": {},
        "last_15_min": {
            "high_defensive_recovery": 0.85,
            "late_pressing_effort": 0.8
        }
    }


@pytest.fixture
def sample_time_slices_empty():
    """Fixture : time slices vides (aucun comportement)."""
    return {
        "global": {},
        "last_15_min": {}
    }


@pytest.fixture
def sample_time_slices_below_threshold():
    """Fixture : time slices avec signaux sous le seuil (0.6)."""
    return {
        "global": {
            "high_compactness": 0.5,       # < 0.6
            "successful_low_block": 0.55   # < 0.6
        },
        "last_15_min": {
            "low_block_drop": 0.4,         # < 0.6
            "xg_against_spike": 0.3        # < 0.6
        }
    }


@pytest.fixture
def sample_time_slices_multiple():
    """Fixture : time slices pour activer plusieurs comportements."""
    return {
        "global": {
            "high_compactness": 0.85,
            "successful_low_block": 0.78,
            "pressing_wave": 0.9,
            "high_duel_pressure": 0.82
        },
        "last_15_min": {
            "low_block_drop": 0.8,
            "xg_against_spike": 0.75,
            "fouls_spike": 0.88,
            "protest_pattern": 0.72
        }
    }


# =============================================================================
# FIXTURES — SIGNAUX PLATS
# =============================================================================

@pytest.fixture
def sample_signals_flat():
    """Fixture : signaux dans un format plat (sans time slicing)."""
    return {
        "low_block_drop": 0.8,
        "xg_against_spike": 0.75,
        "high_compactness": 0.85,
        "successful_low_block": 0.78,
    }


# =============================================================================
# FIXTURES — ÉTAT COMPORTEMENTAL
# =============================================================================

@pytest.fixture
def sample_behavioral_state():
    """Fixture : état comportemental de test (résultat du BehaviorEngine)."""
    return {
        'match_id': 'test_match_001',
        'behaviors': [
            {
                'code': 'STB_01',
                'label': 'Effondrement Structurel',
                'category': 'stability',
                'intensity': 0.775,
                'time_slice': 'last_15_min',
                'status': 'ACTIVE',
                'signals_count': 2,
            }
        ],
        'meta': {
            'source': 'BehaviorEngine',
            'version': '2.1',
            'timestamp': '2025-01-01T15:35:00Z'
        }
    }


# =============================================================================
# FIXTURES — CONSTANTES
# =============================================================================

@pytest.fixture
def engine_constants():
    """Fixture : constantes du BehaviorEngine."""
    return {
        'threshold': 0.6,
        'min_signals': 2,
        'ponderation': 1.5,
        'time_slices': ['global', 'last_15_min']
    }
