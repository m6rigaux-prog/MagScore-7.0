"""
MAGScore 6.2 — Tests: PARTIE 5 Integration
==========================================
Tests d'intégration pour les nouveaux composants PARTIE 5 :
    - PatternEngine v1
    - SignalMemory v1
    - MatchFlowReconstructor v1
    - Pipeline v2.5
    - AnalysisBot v3 (7 sections)

Vérifie :
    - Détection de patterns composites
    - Lissage des signaux (interne, pas inter-appels)
    - Reconstruction chronologique (time_slice → phases)
    - Intégration complète dans le pipeline
"""

import pytest
from magscore.engine.pattern_engine import (
    PatternEngine,
    PATTERN_RULES,
    PATTERN_ENGINE_VERSION,
    create_pattern_engine,
)
from magscore.engine.signal_memory import (
    SignalMemory,
    SIGNAL_MEMORY_VERSION,
    DEFAULT_MAX_MEMORY,
    create_signal_memory,
)
from magscore.engine.match_flow import (
    MatchFlowReconstructor,
    MATCH_FLOW_VERSION,
    PHASE_LABELS,
    MIN_PHASES,
    MAX_PHASES,
    create_match_flow_reconstructor,
)
from magscore.orchestration.pipeline import Pipeline, PIPELINE_VERSION
from magscore.bots.analysis_bot import AnalysisBot


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_behaviors_active():
    """Comportements actifs pour tests de patterns."""
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
def sample_signals():
    """Signaux pour tests de lissage."""
    return {
        "stability": {
            "low_block_drop": 0.7,
            "xg_against_spike": 0.6,
            "high_compactness": 0.5,
            "successful_low_block": 0.4,
        },
        "intensity": {
            "pressing_wave": 0.8,
            "high_duel_pressure": 0.7,
            "running_distance_drop": 0.3,
            "duel_loss_spike": 0.4,
        },
    }


@pytest.fixture
def sample_raw_data():
    """Données brutes de test."""
    return {
        "stats": {
            "shots": 15,
            "shots_on_target": 6,
            "passes": 450,
            "possession": 55,
            "fouls": 12,
            "yellow_cards": 2,
            "interceptions": 8,
            "tackles": 18,
            "clearances": 12,
            "duels": 45,
            "duels_won": 25,
        },
        "last_15_min": {
            "shots": 4,
            "fouls": 5,
            "yellow_cards": 1,
            "interceptions": 2,
            "tackles": 3,
            "duels": 12,
            "duels_won": 4,
        }
    }


@pytest.fixture
def sample_metadata():
    """Métadonnées de test."""
    return {
        "home_team": "Paris FC",
        "away_team": "Lyon United",
        "competition": "Ligue 1",
    }


# =============================================================================
# TESTS: PATTERN ENGINE v1
# =============================================================================

class TestPatternEngine:
    """Tests du PatternEngine v1."""
    
    def test_can_instantiate(self):
        """PatternEngine peut être instancié."""
        engine = PatternEngine()
        assert engine is not None
    
    def test_factory_function(self):
        """Factory function fonctionne."""
        engine = create_pattern_engine()
        assert isinstance(engine, PatternEngine)
    
    def test_version(self):
        """Vérifie la version du PatternEngine (mise à jour v2.0 en 7.0)."""
        engine = PatternEngine()
        assert engine.version == "2.0"
        assert PATTERN_ENGINE_VERSION == "2.0"
    
    def test_compute_patterns_method_exists(self):
        """compute_patterns existe et est callable."""
        engine = PatternEngine()
        assert hasattr(engine, 'compute_patterns')
        assert callable(engine.compute_patterns)
    
    def test_compute_patterns_returns_list(self, sample_behaviors_active):
        """compute_patterns retourne une liste."""
        engine = PatternEngine()
        patterns = engine.compute_patterns(sample_behaviors_active)
        assert isinstance(patterns, list)
    
    def test_pattern_detection_stb01_psy01(self, sample_behaviors_active):
        """Détecte PTN_01 (STB_01 + PSY_01)."""
        engine = PatternEngine()
        patterns = engine.compute_patterns(sample_behaviors_active)
        
        # STB_01 + PSY_01 → PTN_01 "Perte de contrôle sous pression"
        assert len(patterns) >= 1
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert "PTN_01" in pattern_codes
    
    def test_pattern_has_required_fields(self, sample_behaviors_active):
        """Les patterns ont les champs obligatoires."""
        engine = PatternEngine()
        patterns = engine.compute_patterns(sample_behaviors_active)
        
        for pattern in patterns:
            assert "pattern_code" in pattern
            assert "label" in pattern
            assert "sources" in pattern
            assert "category" in pattern
            assert pattern["category"] == "composite"
    
    def test_no_pattern_with_single_behavior(self):
        """Aucun pattern avec un seul comportement."""
        engine = PatternEngine()
        single_behavior = [
            {"code": "STB_01", "status": "ACTIVE"}
        ]
        patterns = engine.compute_patterns(single_behavior)
        assert len(patterns) == 0
    
    def test_ignores_ambiguous_behaviors(self):
        """Ignore les comportements AMBIGUOUS."""
        engine = PatternEngine()
        behaviors = [
            {"code": "STB_01", "status": "AMBIGUOUS"},
            {"code": "PSY_01", "status": "ACTIVE"},
        ]
        patterns = engine.compute_patterns(behaviors)
        assert len(patterns) == 0


class TestPatternRules:
    """Tests des règles de patterns."""
    
    def test_pattern_rules_not_empty(self):
        """PATTERN_RULES n'est pas vide."""
        assert len(PATTERN_RULES) > 0
    
    def test_pattern_rules_has_ptn01(self):
        """PTN_01 existe dans les règles."""
        has_ptn01 = any(
            code == "PTN_01" 
            for _, (code, _) in PATTERN_RULES.items()
        )
        assert has_ptn01
    
    def test_get_all_pattern_codes(self):
        """get_all_pattern_codes retourne tous les codes (v2 inclut visuels)."""
        engine = PatternEngine()
        codes = engine.get_all_pattern_codes()
        # En v2, inclut les patterns comportementaux (12) + visuels (6) = 18
        assert len(codes) == len(PATTERN_RULES) + 6


# =============================================================================
# TESTS: SIGNAL MEMORY v1
# =============================================================================

class TestSignalMemory:
    """Tests du SignalMemory v1."""
    
    def test_can_instantiate(self):
        """SignalMemory peut être instancié."""
        memory = SignalMemory()
        assert memory is not None
    
    def test_factory_function(self):
        """Factory function fonctionne."""
        memory = create_signal_memory()
        assert isinstance(memory, SignalMemory)
    
    def test_version(self):
        """Vérifie la version du SignalMemory."""
        memory = SignalMemory()
        assert memory.version == "1.0"
        assert SIGNAL_MEMORY_VERSION == "1.0"
    
    def test_default_max_memory(self):
        """max_memory par défaut est 3."""
        memory = SignalMemory()
        assert memory.max_memory == 3
        assert DEFAULT_MAX_MEMORY == 3
    
    def test_custom_max_memory(self):
        """max_memory personnalisé fonctionne."""
        memory = SignalMemory(max_memory=5)
        assert memory.max_memory == 5
    
    def test_smooth_method_exists(self):
        """smooth existe et est callable."""
        memory = SignalMemory()
        assert hasattr(memory, 'smooth')
        assert callable(memory.smooth)
    
    def test_smooth_returns_dict(self, sample_signals):
        """smooth retourne un dictionnaire."""
        memory = SignalMemory()
        smoothed = memory.smooth(sample_signals)
        assert isinstance(smoothed, dict)
    
    def test_smooth_preserves_structure(self, sample_signals):
        """smooth préserve la structure des signaux."""
        memory = SignalMemory()
        smoothed = memory.smooth(sample_signals)
        
        # Même catégories
        assert set(smoothed.keys()) == set(sample_signals.keys())
        
        # Même clés dans chaque catégorie
        for category in sample_signals:
            assert set(smoothed[category].keys()) == set(sample_signals[category].keys())
    
    def test_smooth_values_in_range(self, sample_signals):
        """Les valeurs lissées sont dans [0, 1]."""
        memory = SignalMemory()
        smoothed = memory.smooth(sample_signals)
        
        for category in smoothed:
            for key, value in smoothed[category].items():
                assert 0.0 <= value <= 1.0, f"{key} = {value} is out of range"
    
    def test_no_inter_call_memory(self, sample_signals):
        """Pas de mémoire inter-appels."""
        memory = SignalMemory()
        
        # Premier appel
        smoothed1 = memory.smooth(sample_signals)
        
        # Modifier les signaux
        modified_signals = {
            "stability": {"low_block_drop": 0.1},
            "intensity": {"pressing_wave": 0.2},
        }
        
        # Deuxième appel
        smoothed2 = memory.smooth(modified_signals)
        
        # Les valeurs ne doivent PAS être influencées par le premier appel
        assert smoothed2["stability"]["low_block_drop"] == 0.1
        assert smoothed2["intensity"]["pressing_wave"] == 0.2
    
    def test_smooth_empty_returns_empty(self):
        """smooth({}) retourne {}."""
        memory = SignalMemory()
        smoothed = memory.smooth({})
        assert smoothed == {}


# =============================================================================
# TESTS: MATCH FLOW RECONSTRUCTOR v1
# =============================================================================

class TestMatchFlowReconstructor:
    """Tests du MatchFlowReconstructor v1."""
    
    def test_can_instantiate(self):
        """MatchFlowReconstructor peut être instancié."""
        reconstructor = MatchFlowReconstructor()
        assert reconstructor is not None
    
    def test_factory_function(self):
        """Factory function fonctionne."""
        reconstructor = create_match_flow_reconstructor()
        assert isinstance(reconstructor, MatchFlowReconstructor)
    
    def test_version(self):
        """Vérifie la version du MatchFlowReconstructor (mise à jour v1.1)."""
        reconstructor = MatchFlowReconstructor()
        assert reconstructor.version == "1.1"
        assert MATCH_FLOW_VERSION == "1.1"
    
    def test_reconstruct_method_exists(self):
        """reconstruct existe et est callable."""
        reconstructor = MatchFlowReconstructor()
        assert hasattr(reconstructor, 'reconstruct')
        assert callable(reconstructor.reconstruct)
    
    def test_reconstruct_returns_list(self, sample_behaviors_active):
        """reconstruct retourne une liste."""
        reconstructor = MatchFlowReconstructor()
        flow = reconstructor.reconstruct(sample_behaviors_active)
        assert isinstance(flow, list)
    
    def test_min_phases(self):
        """Minimum 2 phases."""
        reconstructor = MatchFlowReconstructor()
        flow = reconstructor.reconstruct([])
        assert len(flow) >= MIN_PHASES
        assert len(flow) >= 2
    
    def test_max_phases(self):
        """Maximum 5 phases."""
        # Créer beaucoup de comportements
        many_behaviors = [
            {"code": "STB_01", "status": "ACTIVE", "time_slice": "global", "category": "stability"},
            {"code": "STB_02", "status": "ACTIVE", "time_slice": "global", "category": "stability"},
            {"code": "INT_01", "status": "ACTIVE", "time_slice": "global", "category": "intensity"},
            {"code": "INT_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "intensity"},
            {"code": "PSY_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"},
            {"code": "PSY_02", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"},
        ]
        
        reconstructor = MatchFlowReconstructor()
        flow = reconstructor.reconstruct(many_behaviors)
        
        assert len(flow) <= MAX_PHASES
        assert len(flow) <= 5
    
    def test_phases_are_numbered(self, sample_behaviors_active):
        """Les phases sont numérotées."""
        reconstructor = MatchFlowReconstructor()
        flow = reconstructor.reconstruct(sample_behaviors_active)
        
        for i, phase in enumerate(flow):
            assert phase.startswith(f"Phase {i+1} :")
    
    def test_global_before_last15(self):
        """Les phases global viennent avant last_15_min."""
        behaviors = [
            {"code": "STB_02", "status": "ACTIVE", "time_slice": "global", "category": "stability"},
            {"code": "PSY_01", "status": "ACTIVE", "time_slice": "last_15_min", "category": "psychology"},
        ]
        
        reconstructor = MatchFlowReconstructor()
        flow = reconstructor.reconstruct(behaviors)
        
        # La première phase devrait être "Contrôle tactique" (global)
        # La dernière devrait être "Frustration finale" (last_15)
        assert "Contrôle tactique" in flow[0]


class TestPhaseLabels:
    """Tests des labels de phases."""
    
    def test_phase_labels_not_empty(self):
        """PHASE_LABELS n'est pas vide."""
        assert len(PHASE_LABELS) > 0
    
    def test_stb02_global_label(self):
        """STB_02 global → Contrôle tactique."""
        label = PHASE_LABELS.get(("STB_02", "global"))
        assert label == "Contrôle tactique"
    
    def test_stb01_last15_label(self):
        """STB_01 last_15_min → Effondrement défensif final."""
        label = PHASE_LABELS.get(("STB_01", "last_15_min"))
        assert label == "Effondrement défensif final"


# =============================================================================
# TESTS: PIPELINE v2.5 INTEGRATION
# =============================================================================

class TestPipelineV25:
    """Tests du Pipeline v2.5 (mise à jour v2.7 en 7.0)."""
    
    def test_pipeline_version(self):
        """Vérifie la version du pipeline (mise à jour v2.7)."""
        assert PIPELINE_VERSION == "2.7"
    
    def test_has_pattern_engine(self):
        """Pipeline a un PatternEngine."""
        pipeline = Pipeline()
        assert hasattr(pipeline, 'pattern_engine')
        assert isinstance(pipeline.pattern_engine, PatternEngine)
    
    def test_has_signal_memory(self):
        """Pipeline a un SignalMemory."""
        pipeline = Pipeline()
        assert hasattr(pipeline, 'signal_memory')
        assert isinstance(pipeline.signal_memory, SignalMemory)
    
    def test_has_match_flow(self):
        """Pipeline a un MatchFlowReconstructor."""
        pipeline = Pipeline()
        assert hasattr(pipeline, 'match_flow')
        assert isinstance(pipeline.match_flow, MatchFlowReconstructor)
    
    def test_result_has_patterns(self, sample_raw_data, sample_metadata):
        """Le résultat contient 'patterns'."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        assert "patterns" in result
        assert isinstance(result["patterns"], list)
    
    def test_result_has_flow(self, sample_raw_data, sample_metadata):
        """Le résultat contient 'flow'."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        assert "flow" in result
        assert isinstance(result["flow"], list)
    
    def test_meta_has_versions(self, sample_raw_data, sample_metadata):
        """Les métadonnées contiennent les versions."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        meta = result["meta"]
        assert "pattern_engine_version" in meta
        assert "signal_memory_version" in meta
        assert "match_flow_version" in meta
        assert "patterns_detected" in meta


# =============================================================================
# TESTS: ANALYSIS BOT v3
# =============================================================================

class TestAnalysisBotV3:
    """Tests de l'AnalysisBot v3."""
    
    def test_version(self):
        """Vérifie la version de l'AnalysisBot (mise à jour v3.2 en 7.0)."""
        bot = AnalysisBot()
        assert bot.VERSION == "3.2"
    
    def test_generate_report_accepts_patterns_and_flow(self):
        """generate_report accepte patterns et flow."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        patterns = [{"pattern_code": "PTN_01", "label": "Test", "sources": []}]
        flow = ["Phase 1 : Test"]
        
        report = bot.generate_report(metadata, behavior_state, patterns, flow)
        assert isinstance(report, str)
    
    def test_report_has_seven_sections(self):
        """Le rapport a 7 sections."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        
        report = bot.generate_report(metadata, behavior_state)
        
        assert "1) Contexte du match" in report
        assert "2) Indicateurs structurels" in report
        assert "3) Lecture comportementale" in report
        assert "4) Patterns narratifs" in report
        assert "5) Match Flow" in report
        assert "6) Points clés à retenir" in report
        assert "7) Synthèse neutre" in report
    
    def test_patterns_section_content(self):
        """La section patterns affiche les patterns."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        patterns = [
            {
                "pattern_code": "PTN_01",
                "label": "Perte de contrôle sous pression",
                "sources": ["STB_01", "PSY_01"],
                "category": "composite",  # Ajouté pour v3.2
            }
        ]
        
        report = bot.generate_report(metadata, behavior_state, patterns, [])
        
        assert "PTN_01" in report
        assert "Perte de contrôle sous pression" in report
        assert "STB_01 + PSY_01" in report
    
    def test_flow_section_content(self):
        """La section flow affiche les phases."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        flow = [
            "Phase 1 : Contrôle tactique",
            "Phase 2 : Effondrement final",
        ]
        
        report = bot.generate_report(metadata, behavior_state, [], flow)
        
        assert "Phase 1 : Contrôle tactique" in report
        assert "Phase 2 : Effondrement final" in report


# =============================================================================
# TESTS: FULL INTEGRATION PARTIE 5
# =============================================================================

class TestFullIntegrationPartie5:
    """Tests d'intégration complète PARTIE 5."""
    
    def test_end_to_end_with_patterns(self, sample_raw_data, sample_metadata):
        """Test complet avec détection de patterns."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        # Vérifier la structure
        assert "behaviors" in result
        assert "patterns" in result
        assert "flow" in result
        assert "report" in result
        
        # Vérifier que le rapport est propre
        from magscore.orchestration.lexicon_guard import is_clean
        assert is_clean(result["report"])
    
    def test_report_mentions_patterns_in_synthesis(self, sample_raw_data, sample_metadata):
        """La synthèse mentionne les patterns si présents."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        report = result["report"]
        patterns = result["patterns"]
        
        # Si des patterns sont détectés, ils doivent être mentionnés
        if patterns:
            # La synthèse doit mentionner le narrative
            assert "narrative" in report.lower() or "pattern" in report.lower() or "dynamic" in report.lower()
