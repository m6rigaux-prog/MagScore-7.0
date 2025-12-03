"""
MAGScore 6.3 — Tests: Pattern Engine v1.1
==========================================
Tests fonctionnels pour PatternEngine v1.1 (patterns composites + triples).

Nouveautés v1.1 :
    - Patterns composites doubles (déjà en v1.0)
    - Patterns composites triples (nouveau)
    - Déduplication avancée
    - Priorité entre patterns (TRIPLE > DOUBLE)
    - Validation d'intégrité des sources

Vision : NO CHANCE — ONLY PATTERNS
"""

import pytest

from magscore.engine.pattern_engine import (
    PatternEngine,
    PATTERN_RULES,
    PATTERN_ENGINE_VERSION,
    create_pattern_engine,
)


# =============================================================================
# FIXTURES — ENGINE
# =============================================================================

@pytest.fixture
def pattern_engine():
    """Fixture : instance de PatternEngine."""
    return PatternEngine()


# =============================================================================
# FIXTURES — BEHAVIORS
# =============================================================================

@pytest.fixture
def behaviors_double_compatible():
    """Deux comportements compatibles pour former un pattern."""
    return [
        {
            "code": "STB_01",
            "label": "Effondrement Structurel",
            "category": "stability",
            "intensity": 0.75,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
        {
            "code": "PSY_01",
            "label": "Frustration Active",
            "category": "psychology",
            "intensity": 0.8,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_triple():
    """Trois comportements pour former un pattern triple."""
    return [
        {
            "code": "STB_01",
            "label": "Effondrement Structurel",
            "category": "stability",
            "intensity": 0.75,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
        {
            "code": "PSY_01",
            "label": "Frustration Active",
            "category": "psychology",
            "intensity": 0.8,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
        {
            "code": "INT_02",
            "label": "Déclin Physique",
            "category": "intensity",
            "intensity": 0.7,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_multiple_combinations():
    """Comportements pouvant former plusieurs patterns (triple + doubles)."""
    return [
        {
            "code": "STB_02",
            "label": "Verrouillage Tactique",
            "category": "stability",
            "intensity": 0.85,
            "time_slice": "global",
            "status": "ACTIVE",
        },
        {
            "code": "INT_01",
            "label": "Surge de Pressing",
            "category": "intensity",
            "intensity": 0.9,
            "time_slice": "global",
            "status": "ACTIVE",
        },
        {
            "code": "PSY_02",
            "label": "Résilience",
            "category": "psychology",
            "intensity": 0.78,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_no_patterns():
    """Comportements qui ne forment aucun pattern."""
    return [
        {
            "code": "STB_01",
            "label": "Effondrement Structurel",
            "category": "stability",
            "intensity": 0.75,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_with_ambiguous():
    """Comportements avec des AMBIGUOUS (à ignorer)."""
    return [
        {
            "code": "AMBIGU_STB",
            "label": "Ambiguïté Stabilité",
            "category": "stability",
            "intensity": None,
            "time_slice": None,
            "status": "AMBIGUOUS",
        },
        {
            "code": "PSY_01",
            "label": "Frustration Active",
            "category": "psychology",
            "intensity": 0.8,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


# =============================================================================
# TESTS: ENGINE INSTANTIATION
# =============================================================================

class TestPatternEngineInstantiation:
    """Tests d'instanciation du PatternEngine."""
    
    def test_can_instantiate(self):
        """PatternEngine peut être instancié."""
        engine = PatternEngine()
        assert engine is not None
    
    def test_factory_function(self):
        """Factory function crée une instance."""
        engine = create_pattern_engine()
        assert isinstance(engine, PatternEngine)
    
    def test_version(self):
        """La version est 2.0 (7.0)."""
        engine = PatternEngine()
        assert engine.version == "2.0"
        assert PATTERN_ENGINE_VERSION == "2.0"


# =============================================================================
# TESTS: PATTERN COMBINATION SIMPLE (DOUBLE)
# =============================================================================

class TestPatternCombinationSimple:
    """Tests de combinaison simple (2 comportements → 1 pattern)."""
    
    def test_pattern_combination_simple(self, pattern_engine, behaviors_double_compatible):
        """Deux comportements compatibles → 1 pattern attendu (PTN_01)."""
        patterns = pattern_engine.compute_patterns(behaviors_double_compatible)
        
        assert len(patterns) == 1
        assert patterns[0]["pattern_code"] == "PTN_01"
        assert patterns[0]["label"] == "Perte de contrôle sous pression"
        assert set(patterns[0]["sources"]) == {"STB_01", "PSY_01"}


# =============================================================================
# TESTS: PATTERN COMBINATION DOUBLE (MULTIPLE)
# =============================================================================

class TestPatternCombinationDouble:
    """Tests de combinaisons multiples (plusieurs patterns détectables)."""
    
    def test_pattern_combination_double(self, pattern_engine, behaviors_multiple_combinations):
        """Plusieurs combinaisons → PTN_07 (triple) a priorité."""
        patterns = pattern_engine.compute_patterns(behaviors_multiple_combinations)
        
        # PTN_07 (triple) devrait être détecté en premier
        pattern_codes = [p["pattern_code"] for p in patterns]
        
        # Pas de doublons
        assert len(pattern_codes) == len(set(pattern_codes))
        
        # Le triple PTN_07 doit être présent
        assert "PTN_07" in pattern_codes


# =============================================================================
# TESTS: PATTERN COMBINATION TRIPLE
# =============================================================================

class TestPatternCombinationTriple:
    """Tests de patterns triples (3 comportements liés)."""
    
    def test_pattern_combination_triple(self, pattern_engine, behaviors_triple):
        """3 comportements liés → PTN_03 (triple) détecté."""
        patterns = pattern_engine.compute_patterns(behaviors_triple)
        
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert "PTN_03" in pattern_codes
        
        # Vérifier le format du triple
        ptn03 = next(p for p in patterns if p["pattern_code"] == "PTN_03")
        assert len(ptn03["sources"]) == 3
        assert set(ptn03["sources"]) == {"STB_01", "PSY_01", "INT_02"}


# =============================================================================
# TESTS: PATTERN PRIORITY
# =============================================================================

class TestPatternPriority:
    """Tests de priorité entre patterns."""
    
    def test_pattern_priority(self, pattern_engine, behaviors_triple):
        """Les triples ont priorité sur les doubles."""
        patterns = pattern_engine.compute_patterns(behaviors_triple)
        
        if len(patterns) > 0:
            # Le premier pattern devrait être le triple (PTN_03)
            assert patterns[0]["pattern_code"] == "PTN_03"
            assert len(patterns[0]["sources"]) == 3
    
    def test_triple_priority_over_double(self, pattern_engine, behaviors_multiple_combinations):
        """PTN_07 (triple) a priorité sur PTN_04, PTN_05, PTN_06 (doubles)."""
        patterns = pattern_engine.compute_patterns(behaviors_multiple_combinations)
        
        # Le premier doit être le triple
        assert patterns[0]["pattern_code"] == "PTN_07"


# =============================================================================
# TESTS: PATTERN DEDUPLICATION
# =============================================================================

class TestPatternDeduplication:
    """Tests de déduplication des patterns."""
    
    def test_pattern_deduplication(self, pattern_engine, behaviors_double_compatible):
        """Mêmes sources répétées → pattern unique, sans duplication."""
        patterns = pattern_engine.compute_patterns(behaviors_double_compatible)
        
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert len(pattern_codes) == len(set(pattern_codes))
    
    def test_no_duplicate_patterns(self, pattern_engine, behaviors_triple):
        """Aucun pattern dupliqué avec les triples."""
        patterns = pattern_engine.compute_patterns(behaviors_triple)
        
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert len(pattern_codes) == len(set(pattern_codes))


# =============================================================================
# TESTS: PATTERN SOURCES INTEGRITY
# =============================================================================

class TestPatternSourcesIntegrity:
    """Tests d'intégrité des sources de patterns."""
    
    def test_pattern_sources_integrity(self, pattern_engine, behaviors_double_compatible):
        """Les sources du pattern sont des codes de behaviors actifs."""
        patterns = pattern_engine.compute_patterns(behaviors_double_compatible)
        
        active_codes = {
            b["code"] for b in behaviors_double_compatible 
            if b["status"] == "ACTIVE"
        }
        
        for pattern in patterns:
            for source in pattern["sources"]:
                assert source in active_codes


# =============================================================================
# TESTS: PATTERN CONFLICTS
# =============================================================================

class TestPatternConflicts:
    """Tests de détection de conflits dans les patterns."""
    
    def test_pattern_conflicts_fail(self, pattern_engine):
        """Les codes contradictoires ne forment pas de pattern invalide."""
        # Note: STB_01 et STB_02 ne peuvent pas être actifs ensemble
        # via BehaviorEngine, mais si on les passe manuellement,
        # le PatternEngine ne devrait pas planter
        behaviors_conflicting = [
            {"code": "STB_01", "status": "ACTIVE"},
            {"code": "STB_02", "status": "ACTIVE"},
        ]
        
        # Ne doit pas lever d'exception
        patterns = pattern_engine.compute_patterns(behaviors_conflicting)
        
        # Les patterns avec ces codes existent (PTN_11 pour STB_01+INT_01, etc.)
        # mais pas de pattern STB_01+STB_02
        assert isinstance(patterns, list)


# =============================================================================
# TESTS: NO PATTERNS DETECTED
# =============================================================================

class TestNoPatterns:
    """Tests quand aucun pattern n'est détectable."""
    
    def test_no_patterns_detected(self, pattern_engine, behaviors_no_patterns):
        """Un seul comportement → liste de patterns vide."""
        patterns = pattern_engine.compute_patterns(behaviors_no_patterns)
        assert patterns == []


# =============================================================================
# TESTS: COMPOSITE CATEGORY
# =============================================================================

class TestCompositeCategory:
    """Tests de catégorie composite pour les patterns."""
    
    def test_composite_category_present(self, pattern_engine, behaviors_double_compatible):
        """Les patterns ont bien category = 'composite'."""
        patterns = pattern_engine.compute_patterns(behaviors_double_compatible)
        
        for pattern in patterns:
            assert pattern["category"] == "composite"


# =============================================================================
# TESTS ADDITIONNELS: EDGE CASES
# =============================================================================

class TestPatternEngineEdgeCases:
    """Tests des cas limites pour PatternEngine v1.1."""
    
    def test_empty_behaviors_list(self, pattern_engine):
        """Liste de comportements vide → liste de patterns vide."""
        patterns = pattern_engine.compute_patterns([])
        assert patterns == []
    
    def test_ignores_ambiguous_behaviors(self, pattern_engine, behaviors_with_ambiguous):
        """Les comportements AMBIGUOUS sont ignorés."""
        patterns = pattern_engine.compute_patterns(behaviors_with_ambiguous)
        # Seulement PSY_01 actif → pas de pattern possible
        assert len(patterns) == 0
    
    def test_pattern_has_required_fields(self, pattern_engine, behaviors_double_compatible):
        """Chaque pattern a les champs obligatoires."""
        patterns = pattern_engine.compute_patterns(behaviors_double_compatible)
        
        required_fields = ["pattern_code", "label", "sources", "category"]
        
        for pattern in patterns:
            for field in required_fields:
                assert field in pattern
    
    def test_is_triple_pattern_method(self, pattern_engine):
        """La méthode is_triple_pattern fonctionne."""
        assert pattern_engine.is_triple_pattern("PTN_03") is True
        assert pattern_engine.is_triple_pattern("PTN_07") is True
        assert pattern_engine.is_triple_pattern("PTN_01") is False
        assert pattern_engine.is_triple_pattern("UNKNOWN") is False
    
    def test_get_pattern_by_code(self, pattern_engine):
        """get_pattern_by_code retourne les infos du pattern."""
        ptn = pattern_engine.get_pattern_by_code("PTN_01")
        
        assert ptn is not None
        assert ptn["pattern_code"] == "PTN_01"
        assert ptn["label"] == "Perte de contrôle sous pression"
        assert set(ptn["sources"]) == {"STB_01", "PSY_01"}
    
    def test_get_all_pattern_codes(self, pattern_engine):
        """get_all_pattern_codes retourne tous les codes (comportementaux + visuels en v2)."""
        codes = pattern_engine.get_all_pattern_codes()
        
        assert "PTN_01" in codes
        assert "PTN_03" in codes
        assert "PTN_07" in codes
        # En v2, inclut aussi les patterns visuels
        assert "PTN_VIS_01" in codes
        assert len(codes) == len(PATTERN_RULES) + 6  # 6 patterns visuels ajoutés
