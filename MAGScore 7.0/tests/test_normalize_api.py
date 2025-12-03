"""
MAGScore 6.1 — Tests: Normalize API (Raw Data Sanitizer)
=========================================================
Tests du sanitizer de données API.

Vérifie :
    - Rejet des métriques opaques (blacklist)
    - Conservation des données brutes (whitelist)
    - Validation de l'intégrité
    - Normalisation des données de match
"""

import pytest
from magscore.external.normalize_api import (
    normalize,
    normalize_match_data,
    is_opaque_metric,
    is_raw_metric,
    validate_data_integrity,
    get_rejected_metrics,
    OPAQUE_METRICS_BLACKLIST,
    RAW_DATA_WHITELIST,
)


class TestNormalizeFunction:
    """Tests de la fonction normalize()."""
    
    def test_empty_data(self):
        """Données vides retournent dict vide."""
        result = normalize({})
        assert result == {}
    
    def test_none_data(self):
        """Données None retournent dict vide."""
        result = normalize(None)
        assert result == {}
    
    def test_preserves_raw_data(self):
        """Les données brutes doivent être conservées."""
        raw = {
            "shots": 12,
            "passes": 340,
            "fouls": 15
        }
        
        result = normalize(raw)
        
        assert result["shots"] == 12
        assert result["passes"] == 340
        assert result["fouls"] == 15
    
    def test_rejects_opaque_metrics(self):
        """Les métriques opaques doivent être rejetées."""
        raw = {
            "shots": 12,
            "momentum": 0.75,
            "pressure_index": 45,
            "passes": 340
        }
        
        result = normalize(raw)
        
        assert "shots" in result
        assert "passes" in result
        assert "momentum" not in result
        assert "pressure_index" not in result
    
    def test_normalizes_keys_to_lowercase(self):
        """Les clés doivent être normalisées en lowercase."""
        raw = {
            "Shots": 12,
            "PASSES": 340
        }
        
        result = normalize(raw)
        
        assert "shots" in result
        assert "passes" in result


class TestOpaqueMetricsBlacklist:
    """Tests de la blacklist des métriques opaques."""
    
    def test_momentum_is_opaque(self):
        """momentum doit être opaque."""
        assert is_opaque_metric("momentum")
        assert is_opaque_metric("MOMENTUM")
        assert is_opaque_metric("Momentum")
    
    def test_pressure_index_is_opaque(self):
        """pressure_index doit être opaque."""
        assert is_opaque_metric("pressure_index")
    
    def test_attack_strength_is_opaque(self):
        """attack_strength doit être opaque."""
        assert is_opaque_metric("attack_strength")
    
    def test_defense_rating_is_opaque(self):
        """defense_rating doit être opaque."""
        assert is_opaque_metric("defense_rating")
    
    def test_power_rating_is_opaque(self):
        """power_rating doit être opaque."""
        assert is_opaque_metric("power_rating")
    
    def test_win_probability_is_opaque(self):
        """win_probability doit être opaque."""
        assert is_opaque_metric("win_probability")
    
    def test_goal_threat_is_opaque(self):
        """goal_threat doit être opaque."""
        assert is_opaque_metric("goal_threat")
    
    def test_shots_is_not_opaque(self):
        """shots ne doit PAS être opaque."""
        assert not is_opaque_metric("shots")
    
    def test_passes_is_not_opaque(self):
        """passes ne doit PAS être opaque."""
        assert not is_opaque_metric("passes")


class TestRawDataWhitelist:
    """Tests de la whitelist des données brutes."""
    
    def test_shots_is_raw(self):
        """shots doit être raw."""
        assert is_raw_metric("shots")
        assert is_raw_metric("shots_total")
        assert is_raw_metric("shots_on_target")
    
    def test_passes_is_raw(self):
        """passes doit être raw."""
        assert is_raw_metric("passes")
        assert is_raw_metric("passes_total")
    
    def test_fouls_is_raw(self):
        """fouls doit être raw."""
        assert is_raw_metric("fouls")
        assert is_raw_metric("fouls_committed")
    
    def test_possession_is_raw(self):
        """possession doit être raw."""
        assert is_raw_metric("possession")
        assert is_raw_metric("possession_percentage")
    
    def test_duels_is_raw(self):
        """duels doit être raw."""
        assert is_raw_metric("duels")
        assert is_raw_metric("duels_won")
    
    def test_xg_is_raw(self):
        """xG doit être raw (si fourni brut par l'API)."""
        assert is_raw_metric("xg")
        assert is_raw_metric("expected_goals")


class TestNormalizeMatchData:
    """Tests de normalize_match_data()."""
    
    def test_empty_match_data(self):
        """Données de match vides retournent None."""
        result = normalize_match_data({})
        assert result is None
    
    def test_basic_match_data(self):
        """Données de match basiques sont normalisées."""
        raw = {
            "match_id": "12345",
            "timestamp": "2025-01-01T15:00:00Z",
            "home_team": {
                "shots": 12,
                "momentum": 0.8
            },
            "away_team": {
                "shots": 8,
                "pressure_index": 55
            }
        }
        
        result = normalize_match_data(raw)
        
        assert result is not None
        assert result["match_id"] == "12345"
        assert "shots" in result["home_team"]
        assert "momentum" not in result["home_team"]
        assert "shots" in result["away_team"]
        assert "pressure_index" not in result["away_team"]
    
    def test_match_data_has_metadata(self):
        """Les données de match doivent avoir des métadonnées."""
        raw = {
            "match_id": "12345",
            "home_team": {"shots": 10},
            "away_team": {"shots": 8}
        }
        
        result = normalize_match_data(raw)
        
        assert "metadata" in result
        assert result["metadata"]["sanitized"] is True


class TestValidateDataIntegrity:
    """Tests de validate_data_integrity()."""
    
    def test_clean_data_is_valid(self):
        """Données propres doivent être valides."""
        clean_data = {
            "shots": 12,
            "passes": 340,
            "fouls": 15
        }
        
        is_valid, issues = validate_data_integrity(clean_data)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_opaque_metric_detected(self):
        """Les métriques opaques doivent être détectées."""
        dirty_data = {
            "shots": 12,
            "momentum": 0.75
        }
        
        is_valid, issues = validate_data_integrity(dirty_data)
        
        assert not is_valid
        assert len(issues) > 0


class TestGetRejectedMetrics:
    """Tests de get_rejected_metrics()."""
    
    def test_returns_rejected_keys(self):
        """Doit retourner les clés qui seraient rejetées."""
        raw = {
            "shots": 12,
            "momentum": 0.75,
            "pressure_index": 45,
            "passes": 340
        }
        
        rejected = get_rejected_metrics(raw)
        
        assert "momentum" in rejected
        assert "pressure_index" in rejected
        assert "shots" not in rejected
        assert "passes" not in rejected
    
    def test_empty_if_no_rejected(self):
        """Liste vide si rien à rejeter."""
        clean = {
            "shots": 12,
            "passes": 340
        }
        
        rejected = get_rejected_metrics(clean)
        
        assert len(rejected) == 0


class TestBlacklistCompleteness:
    """Tests de complétude de la blacklist."""
    
    def test_blacklist_contains_required_metrics(self):
        """La blacklist doit contenir les métriques requises par SPEC."""
        required = [
            "momentum",
            "pressure_index",
            "attack_strength",
            "defense_rating",
            "power_rating",
        ]
        
        for metric in required:
            assert metric in OPAQUE_METRICS_BLACKLIST, f"Manquant: {metric}"
    
    def test_blacklist_is_frozen(self):
        """La blacklist doit être immuable."""
        assert isinstance(OPAQUE_METRICS_BLACKLIST, frozenset)
    
    def test_whitelist_is_frozen(self):
        """La whitelist doit être immuable."""
        assert isinstance(RAW_DATA_WHITELIST, frozenset)
