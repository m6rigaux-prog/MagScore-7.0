"""
MAGScore 6.3 — Tests: Match Flow Reconstructor v1.1
====================================================
Tests fonctionnels pour MatchFlowReconstructor v1.1 (chronologie fond → final).

Nouveautés v1.1 :
    - Chronologie fond → final améliorée
    - Mapping de phases par comportement
    - Détection de ruptures (STB_01 + INT_02)
    - Labels de phases plus précis
    - Minimum 2 phases, maximum 5 phases

Vision : NO CHANCE — ONLY PATTERNS
"""

import pytest

from magscore.engine.match_flow import (
    MatchFlowReconstructor,
    MATCH_FLOW_VERSION,
    PHASE_LABELS,
    MIN_PHASES,
    MAX_PHASES,
    RUPTURE_LABEL,
    create_match_flow_reconstructor,
)


# =============================================================================
# FIXTURES — ENGINE
# =============================================================================

@pytest.fixture
def flow_engine():
    """Fixture : instance de MatchFlowReconstructor."""
    return MatchFlowReconstructor()


# =============================================================================
# FIXTURES — BEHAVIORS
# =============================================================================

@pytest.fixture
def behaviors_global_and_final():
    """Comportements avec time_slice global et last_15_min."""
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
            "code": "STB_01",
            "label": "Effondrement Structurel",
            "category": "stability",
            "intensity": 0.75,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_only_global():
    """Comportements uniquement globaux."""
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
    ]


@pytest.fixture
def behaviors_only_final():
    """Comportements uniquement en phase finale."""
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
def behaviors_rupture():
    """Comportements indiquant une rupture (STB_01 + INT_02)."""
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
            "code": "INT_02",
            "label": "Déclin Physique",
            "category": "intensity",
            "intensity": 0.7,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_complete_flow():
    """Comportements pour un flow complet avec plusieurs phases."""
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
def behaviors_for_phase_mapping():
    """Comportements spécifiques pour tester le mapping de phases."""
    return [
        {"code": "STB_02", "status": "ACTIVE", "time_slice": "global", "category": "stability"},
        {"code": "INT_01", "status": "ACTIVE", "time_slice": "global", "category": "intensity"},
        {"code": "STB_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "stability"},
        {"code": "PSY_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"},
        {"code": "INT_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "intensity"},
        {"code": "PSY_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"},
    ]


# =============================================================================
# TESTS: ENGINE INSTANTIATION
# =============================================================================

class TestFlowEngineInstantiation:
    """Tests d'instanciation du MatchFlowReconstructor."""
    
    def test_can_instantiate(self):
        """MatchFlowReconstructor peut être instancié."""
        reconstructor = MatchFlowReconstructor()
        assert reconstructor is not None
    
    def test_factory_function(self):
        """Factory function crée une instance."""
        reconstructor = create_match_flow_reconstructor()
        assert isinstance(reconstructor, MatchFlowReconstructor)
    
    def test_version(self):
        """La version est 1.1."""
        reconstructor = MatchFlowReconstructor()
        assert reconstructor.version == "1.1"
        assert MATCH_FLOW_VERSION == "1.1"


# =============================================================================
# TESTS: FLOW GLOBAL THEN FINAL
# =============================================================================

class TestFlowGlobalThenFinal:
    """Tests du flow global puis final."""
    
    def test_flow_global_then_final(self, flow_engine, behaviors_global_and_final):
        """Global + last_15_min → phases de fond suivies de phases finales."""
        flow = flow_engine.reconstruct(behaviors_global_and_final)
        
        assert len(flow) >= 2
        
        # La première phase devrait être "Contrôle tactique" (global)
        assert "Contrôle tactique" in flow[0]
        
        # La dernière phase devrait contenir "Effondrement" (final)
        assert any("Effondrement" in phase for phase in flow)


# =============================================================================
# TESTS: FLOW ONLY GLOBAL
# =============================================================================

class TestFlowOnlyGlobal:
    """Tests du flow avec uniquement des comportements globaux."""
    
    def test_flow_only_global(self, flow_engine, behaviors_only_global):
        """Seulement global → au moins 2 phases."""
        flow = flow_engine.reconstruct(behaviors_only_global)
        assert len(flow) >= 2


# =============================================================================
# TESTS: FLOW ONLY FINAL
# =============================================================================

class TestFlowOnlyFinal:
    """Tests du flow avec uniquement des comportements finaux."""
    
    def test_flow_only_final(self, flow_engine, behaviors_only_final):
        """Seulement last_15_min → 2 phases minimum."""
        flow = flow_engine.reconstruct(behaviors_only_final)
        assert len(flow) >= 2


# =============================================================================
# TESTS: FLOW ORDER
# =============================================================================

class TestFlowOrder:
    """Tests de l'ordre des phases dans le flow."""
    
    def test_flow_order(self, flow_engine, behaviors_global_and_final):
        """Les phases sont numérotées correctement."""
        flow = flow_engine.reconstruct(behaviors_global_and_final)
        
        for i, phase in enumerate(flow):
            assert f"Phase {i+1}" in phase


# =============================================================================
# TESTS: FLOW MIN PHASES
# =============================================================================

class TestFlowMinPhases:
    """Tests du minimum de phases."""
    
    def test_flow_min_phases(self, flow_engine):
        """Au moins 2 phases même avec liste vide."""
        # Cas : liste vide
        flow_empty = flow_engine.reconstruct([])
        assert len(flow_empty) >= MIN_PHASES
        assert len(flow_empty) >= 2
        
        # Cas : un seul comportement
        single = [{"code": "STB_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "stability"}]
        flow_single = flow_engine.reconstruct(single)
        assert len(flow_single) >= 2


# =============================================================================
# TESTS: FLOW MAX PHASES
# =============================================================================

class TestFlowMaxPhases:
    """Tests du maximum de phases."""
    
    def test_flow_max_phases(self, flow_engine, behaviors_complete_flow):
        """Maximum 5 phases même avec beaucoup de comportements."""
        flow = flow_engine.reconstruct(behaviors_complete_flow)
        
        assert len(flow) <= MAX_PHASES
        assert len(flow) <= 5


# =============================================================================
# TESTS: FLOW PHASE MAPPING
# =============================================================================

class TestFlowPhaseMapping:
    """Tests du mapping comportement → label de phase."""
    
    def test_flow_phase_mapping(self, flow_engine, behaviors_for_phase_mapping):
        """Les comportements produisent les labels de phase attendus."""
        flow = flow_engine.reconstruct(behaviors_for_phase_mapping)
        flow_text = " ".join(flow)
        
        # Au moins quelques labels attendus doivent être présents
        # (avec limite de 5 phases, tous ne seront pas présents)
        expected_some = ["Contrôle", "Intensité", "Effondrement", "Frustration", "Déclin", "Résistance", "Rupture"]
        matches = sum(1 for label in expected_some if label in flow_text)
        assert matches >= 2
    
    def test_stb02_produces_controle(self, flow_engine):
        """STB_02 global → 'Contrôle tactique'."""
        behaviors = [{"code": "STB_02", "status": "ACTIVE", "time_slice": "global", "category": "stability"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Contrôle" in phase for phase in flow)
    
    def test_int01_produces_intensite(self, flow_engine):
        """INT_01 global → 'Intensité active'."""
        behaviors = [{"code": "INT_01", "status": "ACTIVE", "time_slice": "global", "category": "intensity"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Intensité" in phase for phase in flow)
    
    def test_stb01_produces_effondrement(self, flow_engine):
        """STB_01 last_15_min → 'Effondrement défensif final'."""
        behaviors = [{"code": "STB_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "stability"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Effondrement" in phase for phase in flow)
    
    def test_psy01_produces_tension(self, flow_engine):
        """PSY_01 last_15_min → 'Frustration finale'."""
        behaviors = [{"code": "PSY_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Frustration" in phase for phase in flow)
    
    def test_int02_produces_declin(self, flow_engine):
        """INT_02 last_15_min → 'Déclin physique final'."""
        behaviors = [{"code": "INT_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "intensity"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Déclin" in phase for phase in flow)
    
    def test_psy02_produces_resilience(self, flow_engine):
        """PSY_02 last_15_min → 'Résistance finale'."""
        behaviors = [{"code": "PSY_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"}]
        flow = flow_engine.reconstruct(behaviors)
        assert any("Résistance" in phase for phase in flow)


# =============================================================================
# TESTS: FLOW RUPTURE DETECTION
# =============================================================================

class TestFlowRuptureDetection:
    """Tests de détection de rupture dans le flow."""
    
    def test_flow_rupture_detected(self, flow_engine, behaviors_rupture):
        """STB_01 + INT_02 → 'Rupture structurelle'."""
        flow = flow_engine.reconstruct(behaviors_rupture)
        flow_text = " ".join(flow).lower()
        
        # Vérifier qu'une notion de rupture/crise est présente
        rupture_keywords = ["rupture", "effondrement", "déclin"]
        has_rupture = any(kw in flow_text for kw in rupture_keywords)
        assert has_rupture
    
    def test_detect_rupture_method(self, flow_engine, behaviors_rupture):
        """La méthode detect_rupture fonctionne."""
        assert flow_engine.detect_rupture(behaviors_rupture) is True
        
        # Sans les deux codes
        no_rupture = [{"code": "STB_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "stability"}]
        assert flow_engine.detect_rupture(no_rupture) is False
    
    def test_rupture_label_present(self, flow_engine, behaviors_rupture):
        """Le label de rupture apparaît dans le flow."""
        flow = flow_engine.reconstruct(behaviors_rupture)
        flow_text = " ".join(flow)
        
        assert RUPTURE_LABEL in flow_text


# =============================================================================
# TESTS ADDITIONNELS: EDGE CASES
# =============================================================================

class TestFlowEdgeCases:
    """Tests des cas limites pour MatchFlowReconstructor v1.1."""
    
    def test_empty_behaviors_list(self, flow_engine):
        """Liste vide → phases par défaut."""
        flow = flow_engine.reconstruct([])
        assert len(flow) >= 2
    
    def test_ignores_ambiguous_behaviors(self, flow_engine):
        """Les comportements AMBIGUOUS sont ignorés."""
        behaviors = [
            {"code": "AMBIGU_STB", "status": "AMBIGUOUS", "time_slice": None, "category": "stability"},
        ]
        flow = flow_engine.reconstruct(behaviors)
        assert len(flow) >= 2  # Phases par défaut
    
    def test_phases_are_numbered_correctly(self, flow_engine, behaviors_global_and_final):
        """Les phases sont correctement numérotées."""
        flow = flow_engine.reconstruct(behaviors_global_and_final)
        
        for i, phase in enumerate(flow):
            assert phase.startswith(f"Phase {i+1} :")
    
    def test_no_duplicate_phases(self, flow_engine, behaviors_complete_flow):
        """Pas de phases dupliquées."""
        flow = flow_engine.reconstruct(behaviors_complete_flow)
        
        # Extraire les labels (sans les numéros)
        labels = [phase.split(" : ", 1)[1] if " : " in phase else phase for phase in flow]
        assert len(labels) == len(set(labels))
    
    def test_get_phase_label(self, flow_engine):
        """get_phase_label retourne le bon label."""
        label = flow_engine.get_phase_label("STB_02", "global")
        assert label == "Contrôle tactique"
        
        label = flow_engine.get_phase_label("STB_01", "last_15_min")
        assert label == "Effondrement défensif final"
        
        # Code inconnu → défaut
        label = flow_engine.get_phase_label("UNKNOWN", "global")
        assert label == "Phase de stabilisation"
