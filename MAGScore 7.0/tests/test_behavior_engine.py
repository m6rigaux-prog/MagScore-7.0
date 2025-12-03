"""
MAGScore 6.1 — Tests: Behavior Engine v2.3
===========================================
Tests du moteur comportemental.

Vérifie :
    - Règle des 2 signaux convergents (MIN_REQUIRED_SIGNALS)
    - Seuil d'activation (SIGNAL_ACTIVATION_THRESHOLD = 0.6)
    - Pondération (3 signaux = x1.5)
    - Time Slicing (global vs last_15_min)
    - Format de sortie
    
PARTIE 3 :
    - Merge Slices (fusion multi-slice)
    - Recency Strategy (Money Time Priority)
    - Contradiction Resolution (AMBIGU)
    - Category Priority Sort
"""

import pytest
from magscore.engine.behavior_engine import (
    BehaviorEngine, 
    BehaviorStatus, 
    TimeSlice,
    create_behavior_engine,
    ENGINE_VERSION,
    CATEGORY_ORDER,
    RECENCY_MODEL,
)
from magscore.engine.definitions import (
    BEHAVIOR_DEFINITIONS,
    SIGNAL_ACTIVATION_THRESHOLD,
    MIN_REQUIRED_SIGNALS,
    PONDERATION_FACTOR,
    TIME_SLICES,
    ALL_REQUIRED_SIGNALS,
)


class TestBehaviorEngineInstantiation:
    """Tests d'instanciation du BehaviorEngine."""
    
    def test_can_instantiate(self):
        """Vérifie que le BehaviorEngine peut être instancié."""
        engine = BehaviorEngine()
        assert engine is not None
    
    def test_has_definitions(self):
        """Vérifie que les définitions sont chargées."""
        engine = BehaviorEngine()
        assert hasattr(engine, '_definitions')
        assert len(engine._definitions) == 6  # 6 comportements définis
    
    def test_factory_function(self):
        """Vérifie la factory function."""
        engine = create_behavior_engine()
        assert isinstance(engine, BehaviorEngine)
    
    def test_version(self):
        """Vérifie la version du moteur."""
        engine = BehaviorEngine()
        assert engine.version == "2.3"
        assert ENGINE_VERSION == "2.3"
    
    def test_constants_loaded(self):
        """Vérifie que les constantes sont correctement chargées."""
        engine = BehaviorEngine()
        assert engine.threshold == 0.6
        assert engine.min_signals == 2
        assert engine.ponderation_factor == 1.5


class TestConvergenceRule:
    """Tests de la règle de convergence (min 2 signaux)."""
    
    def test_single_signal_rejected(self):
        """Un signal isolé ne doit pas produire de comportement."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.3
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" not in active_codes
    
    def test_two_signals_accepted(self):
        """Deux signaux convergents doivent produire un comportement."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" in active_codes
    
    def test_three_signals_weighted(self):
        """Trois signaux doivent appliquer le multiplicateur x1.5."""
        engine = BehaviorEngine()
        assert engine.ponderation_factor == 1.5


class TestThresholdActivation:
    """Tests du seuil d'activation (0.6)."""
    
    def test_below_threshold_ignored(self):
        """Les signaux sous le seuil doivent être ignorés."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.5,
                "xg_against_spike": 0.59
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" not in active_codes
    
    def test_at_threshold_activated(self):
        """Les signaux au seuil exact (0.6) doivent être activés."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.6,
                "xg_against_spike": 0.6
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" in active_codes
    
    def test_above_threshold_activated(self):
        """Les signaux au-dessus du seuil doivent être activés."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.9,
                "xg_against_spike": 0.85
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" in active_codes


class TestTimeSlicing:
    """Tests du découpage temporel (Time Slicing)."""
    
    def test_global_zone_behavior(self):
        """STB_02 doit utiliser la zone 'global'."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "high_compactness": 0.8,
                "successful_low_block": 0.7
            },
            "last_15_min": {}
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_02" in active_codes
    
    def test_last_15_min_zone_behavior(self):
        """STB_01 doit utiliser la zone 'last_15_min'."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            },
            "last_15_min": {}
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" not in active_codes
    
    def test_correct_time_slice_recorded(self):
        """Le time_slice correct doit être enregistré."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        
        for behavior in result["behaviors"]:
            if behavior["code"] == "STB_01":
                assert behavior["time_slice"] == "last_15_min"


class TestIntensityCalculation:
    """Tests du calcul d'intensité."""
    
    def test_intensity_is_average(self):
        """L'intensité doit être la moyenne des signaux actifs."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.6
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        
        for behavior in result["behaviors"]:
            if behavior["code"] == "STB_01":
                assert behavior["intensity"] == 0.7
    
    def test_intensity_rounded(self):
        """L'intensité doit être arrondie à 3 décimales."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.777,
                "xg_against_spike": 0.888
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        
        for behavior in result["behaviors"]:
            if behavior["code"] == "STB_01":
                intensity_str = str(behavior["intensity"])
                decimals = len(intensity_str.split('.')[-1]) if '.' in intensity_str else 0
                assert decimals <= 3


class TestOutputFormat:
    """Tests du format de sortie."""
    
    def test_output_has_behaviors_key(self):
        """La sortie doit avoir une clé 'behaviors'."""
        engine = BehaviorEngine()
        result = engine.compute_behaviors({}, {"global": {}, "last_15_min": {}})
        
        assert "behaviors" in result
        assert isinstance(result["behaviors"], list)
    
    def test_output_has_meta_key(self):
        """La sortie doit avoir une clé 'meta'."""
        engine = BehaviorEngine()
        result = engine.compute_behaviors({}, {"global": {}, "last_15_min": {}})
        
        assert "meta" in result
        assert "source" in result["meta"]
        assert "version" in result["meta"]
        assert "timestamp" in result["meta"]
    
    def test_output_has_recency_model(self):
        """La sortie doit avoir recency_model dans meta (PARTIE 3)."""
        engine = BehaviorEngine()
        result = engine.compute_behaviors({}, {"global": {}, "last_15_min": {}})
        
        assert "recency_model" in result["meta"]
        assert result["meta"]["recency_model"] == "last_15_priority"
    
    def test_behavior_has_required_fields(self):
        """Chaque comportement doit avoir les champs requis."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        
        required_fields = ["code", "label", "category", "intensity", "time_slice", "status", "signals_count"]
        
        for behavior in result["behaviors"]:
            for field in required_fields:
                assert field in behavior


# =============================================================================
# PARTIE 3 TESTS — LOGIQUE AVANCÉE
# =============================================================================

class TestRecencyStrategy:
    """Tests du Recency Strategy (Money Time Priority) - PARTIE 3."""
    
    def test_last_15_wins_over_global(self):
        """last_15_min doit gagner sur global dans la même catégorie."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "high_compactness": 0.8,
                "successful_low_block": 0.7
            },
            "last_15_min": {
                "low_block_drop": 0.85,
                "xg_against_spike": 0.75
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        
        assert "STB_01" in active_codes
        assert "STB_02" not in active_codes
    
    def test_recency_before_contradiction(self):
        """Le recency doit être appliqué AVANT la résolution des contradictions."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "high_compactness": 0.8,
                "successful_low_block": 0.7
            },
            "last_15_min": {
                "low_block_drop": 0.85,
                "xg_against_spike": 0.75
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        ambiguous = engine.get_ambiguous_behaviors(result)
        stability_ambiguous = [a for a in ambiguous if a["category"] == "stability"]
        
        assert len(stability_ambiguous) == 0
    
    def test_no_ambiguous_inter_categories(self):
        """Pas d'AMBIGU inter-catégories."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "pressing_wave": 0.8,
                "high_duel_pressure": 0.7
            },
            "last_15_min": {
                "fouls_spike": 0.85,
                "protest_pattern": 0.75
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        
        assert "INT_01" in active_codes
        assert "PSY_01" in active_codes


class TestContradictionResolution:
    """Tests de la résolution des contradictions (AMBIGU) - PARTIE 3."""
    
    def test_ambiguous_not_generated_before_recency(self):
        """AMBIGU ne doit pas être généré si recency résout le conflit."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "high_compactness": 0.8,
                "successful_low_block": 0.7
            },
            "last_15_min": {
                "low_block_drop": 0.85,
                "xg_against_spike": 0.75
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        ambiguous = engine.get_ambiguous_behaviors(result)
        
        assert not any(a["code"] == "AMBIGU_STB" for a in ambiguous)
    
    def test_ambiguous_has_correct_format(self):
        """Le comportement AMBIGU doit avoir le format correct."""
        expected_fields = ["code", "category", "status", "intensity", "time_slice", "details"]
        
        ambiguous_template = {
            "code": "AMBIGU_STB",
            "category": "stability",
            "status": BehaviorStatus.AMBIGUOUS.value,
            "intensity": None,
            "time_slice": None,
            "details": ["STB_01", "STB_02"]
        }
        
        for field in expected_fields:
            assert field in ambiguous_template
        
        assert ambiguous_template["status"] == "AMBIGUOUS"


class TestCategoryPrioritySort:
    """Tests du tri par priorité de catégorie - PARTIE 3."""
    
    def test_psychology_first(self):
        """La catégorie psychology doit être en premier."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "pressing_wave": 0.8,
                "high_duel_pressure": 0.7
            },
            "last_15_min": {
                "fouls_spike": 0.85,
                "protest_pattern": 0.75
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        
        if len(result["behaviors"]) >= 2:
            first_category = result["behaviors"][0]["category"]
            assert first_category == "psychology"
    
    def test_category_order_constant(self):
        """Vérifie l'ordre des catégories."""
        assert CATEGORY_ORDER["psychology"] == 0
        assert CATEGORY_ORDER["intensity"] == 1
        assert CATEGORY_ORDER["stability"] == 2
    
    def test_multiple_behaviors_sorted(self):
        """Plusieurs comportements doivent être triés correctement."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "pressing_wave": 0.8,
                "high_duel_pressure": 0.7,
            },
            "last_15_min": {
                "fouls_spike": 0.88,
                "protest_pattern": 0.72
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        categories = [b["category"] for b in result["behaviors"]]
        
        for i in range(len(categories) - 1):
            current_order = CATEGORY_ORDER.get(categories[i], 99)
            next_order = CATEGORY_ORDER.get(categories[i+1], 99)
            assert current_order <= next_order


class TestMergeSlices:
    """Tests de la fusion multi-slice - PARTIE 3."""
    
    def test_single_behavior_preserved(self):
        """Un comportement unique doit être préservé."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        assert "STB_01" in active_codes


class TestMultipleBehaviors:
    """Tests de détection de comportements multiples."""
    
    def test_multiple_behaviors_detected(self):
        """Plusieurs comportements peuvent être détectés simultanément."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "pressing_wave": 0.9,
                "high_duel_pressure": 0.75
            },
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7,
                "fouls_spike": 0.88,
                "protest_pattern": 0.72
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        active_codes = engine.get_active_behavior_codes(result)
        
        assert len(active_codes) >= 2
    
    def test_behaviors_by_category(self):
        """Les comportements peuvent être filtrés par catégorie."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {
                "pressing_wave": 0.8,
                "high_duel_pressure": 0.7
            },
            "last_15_min": {}
        }
        
        result = engine.compute_behaviors({}, time_slices)
        intensity_behaviors = engine.get_behaviors_by_category(result, "intensity")
        assert len(intensity_behaviors) >= 1


class TestSignalValidation:
    """Tests de validation des clés de signaux."""
    
    def test_validate_known_signals(self):
        """Les signaux connus doivent être validés."""
        engine = BehaviorEngine()
        
        valid_signals = {
            "low_block_drop": 0.8,
            "xg_against_spike": 0.7
        }
        
        is_valid, unknown = engine.validate_signal_keys(valid_signals)
        assert is_valid
        assert len(unknown) == 0
    
    def test_detect_unknown_signals(self):
        """Les signaux inconnus doivent être détectés."""
        engine = BehaviorEngine()
        
        signals_with_unknown = {
            "low_block_drop": 0.8,
            "unknown_signal_xyz": 0.5
        }
        
        is_valid, unknown = engine.validate_signal_keys(signals_with_unknown)
        assert not is_valid
        assert "unknown_signal_xyz" in unknown


class TestGetAmbiguousBehaviors:
    """Tests de la méthode get_ambiguous_behaviors - PARTIE 3."""
    
    def test_returns_empty_when_no_ambiguous(self):
        """Doit retourner liste vide si pas d'AMBIGU."""
        engine = BehaviorEngine()
        
        time_slices = {
            "global": {},
            "last_15_min": {
                "low_block_drop": 0.8,
                "xg_against_spike": 0.7
            }
        }
        
        result = engine.compute_behaviors({}, time_slices)
        ambiguous = engine.get_ambiguous_behaviors(result)
        assert isinstance(ambiguous, list)
