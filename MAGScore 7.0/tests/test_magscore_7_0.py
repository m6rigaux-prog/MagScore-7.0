"""
MAGScore 7.0 — Tests d'intégration
===================================
Tests pour les nouveaux composants de MAGScore 7.0 :
    - VisionEngine v1
    - MemoryEngine v1 (sécurité)
    - PatternEngine v2 (patterns visuels)
    - Pipeline v2.7
    - AnalysisBot v3.2

Vision : NO CHANCE — ONLY PATTERNS
"""

import pytest
from datetime import datetime

from magscore.engine.definitions import (
    Episode,
    Frame,
    VisualSignal,
    TeamMemory,
    SemanticMemory,
    FORBIDDEN_MEMORY_KEYS,
    discretize_visual_signal,
    is_forbidden_memory_key,
)
from magscore.engine.vision_engine import (
    VisionEngine,
    VisionSignalExtractor,
    VideoStreamHandler,
    VISION_ENGINE_VERSION,
)
from magscore.engine.memory_engine import (
    MemoryEngine,
    EpisodicMemory,
    ForbiddenDataError,
    MEMORY_ENGINE_VERSION,
)
from magscore.engine.pattern_engine import (
    PatternEngine,
    PATTERN_ENGINE_VERSION,
    PATTERN_RULES_V2,
)
from magscore.orchestration.pipeline import (
    Pipeline,
    PIPELINE_VERSION,
)
from magscore.bots.analysis_bot import AnalysisBot


# =============================================================================
# TESTS: DEFINITIONS (Dataclasses)
# =============================================================================

class TestDefinitionsDataclasses:
    """Tests des nouvelles dataclasses 7.0."""
    
    def test_episode_creation(self):
        """Episode peut être créé avec tous les champs."""
        episode = Episode(
            match_id="TEST_001",
            timestamp=datetime.now(),
            opposing_style="HIGH_PRESS_POSSESSION",
            behaviors=["STB_02", "INT_01"],
            patterns=["PTN_04"],
            flow_phases=["Contrôle tactique"]
        )
        
        assert episode.match_id == "TEST_001"
        assert episode.opposing_style == "HIGH_PRESS_POSSESSION"
        assert "STB_02" in episode.behaviors
    
    def test_frame_creation(self):
        """Frame peut être créé."""
        frame = Frame(
            timestamp=datetime.now(),
            metrics={"density_def": 0.7, "optical_flow_avg": 0.3}
        )
        
        assert "density_def" in frame.metrics
        assert frame.metrics["density_def"] == 0.7
    
    def test_visual_signal_creation(self):
        """VisualSignal peut être créé."""
        vs = VisualSignal(
            raw={"density_def": 0.8},
            discrete=["VIS_DEF_HIGH"]
        )
        
        assert vs.raw["density_def"] == 0.8
        assert "VIS_DEF_HIGH" in vs.discrete
    
    def test_discretize_visual_signal(self):
        """discretize_visual_signal fonctionne correctement."""
        assert discretize_visual_signal(0.1, "VIS_DEF") == "VIS_DEF_LOW"
        assert discretize_visual_signal(0.5, "VIS_DEF") == "VIS_DEF_MED"
        assert discretize_visual_signal(0.9, "VIS_DEF") == "VIS_DEF_HIGH"
    
    def test_is_forbidden_memory_key(self):
        """is_forbidden_memory_key détecte les clés interdites."""
        assert is_forbidden_memory_key("score") is True
        assert is_forbidden_memory_key("result") is True
        assert is_forbidden_memory_key("odds") is True
        assert is_forbidden_memory_key("winner") is True
        assert is_forbidden_memory_key("behaviors") is False
        assert is_forbidden_memory_key("patterns") is False


# =============================================================================
# TESTS: VISION ENGINE
# =============================================================================

class TestVisionEngine:
    """Tests du VisionEngine v1."""
    
    def test_version(self):
        """Version est 1.0."""
        assert VISION_ENGINE_VERSION == "1.0"
        engine = VisionEngine()
        assert engine.version == "1.0"
    
    def test_instantiation(self):
        """VisionEngine peut être instancié."""
        engine = VisionEngine()
        assert engine is not None
    
    def test_discretize_returns_list(self):
        """discretize retourne une liste de codes."""
        engine = VisionEngine()
        raw_signals = {
            "density_def": 0.8,
            "density_off": 0.3,
            "optical_flow_avg": 0.5,
            "cluster_density": 0.9,
        }
        
        discrete = engine.discretize(raw_signals)
        
        assert isinstance(discrete, list)
        assert len(discrete) == 4


class TestVisionSignalExtractor:
    """Tests du VisionSignalExtractor."""
    
    def test_instantiation(self):
        """VisionSignalExtractor peut être instancié."""
        extractor = VisionSignalExtractor()
        assert extractor is not None
    
    def test_discretize_signals(self):
        """discretize_signals retourne un VisualSignal."""
        extractor = VisionSignalExtractor()
        
        raw = {"density_def": 0.8, "optical_flow_avg": 0.2}
        result = extractor.discretize_signals(raw)
        
        assert isinstance(result, VisualSignal)
        assert result.raw == raw
        assert len(result.discrete) >= 1


# =============================================================================
# TESTS: MEMORY ENGINE — SÉCURITÉ CRITIQUE
# =============================================================================

class TestMemoryEngineSecurity:
    """Tests de sécurité du MemoryEngine — CRITIQUE."""
    
    def test_version(self):
        """Version est 1.0."""
        assert MEMORY_ENGINE_VERSION == "1.0"
        engine = MemoryEngine()
        assert engine.version == "1.0"
    
    def test_instantiation(self):
        """MemoryEngine peut être instancié."""
        engine = MemoryEngine()
        assert engine is not None
    
    def test_ingest_valid_data(self):
        """ingest accepte les données valides."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02", "INT_01"],
            "patterns": ["PTN_04"],
            "flow_phases": ["Contrôle tactique"],
            "opposing_style": "HIGH_PRESS",
        }
        
        episode = engine.ingest("FC_TEST", data)
        
        assert episode.match_id == "TEST_001"
        assert "STB_02" in episode.behaviors
    
    def test_ingest_rejects_score_strict(self):
        """ingest REJETTE les données avec score (mode strict)."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02"],
            "score": "2-1",  # INTERDIT
        }
        
        with pytest.raises(ForbiddenDataError):
            engine.ingest("FC_TEST", data, strict=True)
    
    def test_ingest_rejects_result_strict(self):
        """ingest REJETTE les données avec result (mode strict)."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02"],
            "result": "win",  # INTERDIT
        }
        
        with pytest.raises(ForbiddenDataError):
            engine.ingest("FC_TEST", data, strict=True)
    
    def test_ingest_rejects_odds_strict(self):
        """ingest REJETTE les données avec odds (mode strict)."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02"],
            "odds": 1.85,  # INTERDIT
        }
        
        with pytest.raises(ForbiddenDataError):
            engine.ingest("FC_TEST", data, strict=True)
    
    def test_ingest_rejects_winner_strict(self):
        """ingest REJETTE les données avec winner (mode strict)."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02"],
            "winner": "FC_TEST",  # INTERDIT
        }
        
        with pytest.raises(ForbiddenDataError):
            engine.ingest("FC_TEST", data, strict=True)
    
    def test_ingest_filters_score_non_strict(self):
        """ingest FILTRE les données avec score (mode non-strict)."""
        engine = MemoryEngine()
        
        data = {
            "match_id": "TEST_001",
            "behaviors": ["STB_02"],
            "score": "2-1",  # INTERDIT - sera filtré
        }
        
        # Ne doit pas lever d'exception
        episode = engine.ingest("FC_TEST", data, strict=False)
        
        assert episode.match_id == "TEST_001"
    
    def test_get_pattern_frequency(self):
        """get_pattern_frequency retourne la fréquence."""
        engine = MemoryEngine()
        
        # Ajouter plusieurs épisodes avec le même pattern
        for i in range(5):
            engine.ingest("FC_TEST", {
                "match_id": f"TEST_{i}",
                "patterns": ["PTN_04", "PTN_05"] if i % 2 == 0 else ["PTN_04"],
            })
        
        freq = engine.get_pattern_frequency("FC_TEST", "PTN_04")
        assert freq > 0
    
    def test_get_historical_context(self):
        """get_historical_context retourne le contexte."""
        engine = MemoryEngine()
        
        # Ajouter des épisodes
        for i in range(3):
            engine.ingest("FC_TEST", {
                "match_id": f"TEST_{i}",
                "patterns": ["PTN_04"],
                "opposing_style": "HIGH_PRESS" if i < 2 else "LOW_BLOCK",
            })
        
        context = engine.get_historical_context("FC_TEST", "HIGH_PRESS")
        
        assert context["total_episodes"] == 3
        assert context["vs_style"] is not None
        assert context["vs_style"]["episodes_count"] == 2


class TestEpisodicMemory:
    """Tests de la mémoire épisodique."""
    
    def test_fifo_limit(self):
        """La mémoire est limitée (FIFO)."""
        memory = EpisodicMemory(max_episodes=3)
        
        for i in range(5):
            episode = Episode(
                match_id=f"TEST_{i}",
                timestamp=datetime.now(),
            )
            memory.add(episode)
        
        assert memory.count == 3
        # Les plus anciens ont été supprimés
        episodes = memory.episodes
        assert episodes[0].match_id == "TEST_2"


# =============================================================================
# TESTS: PATTERN ENGINE v2
# =============================================================================

class TestPatternEngineV2:
    """Tests du PatternEngine v2 (patterns visuels)."""
    
    def test_version(self):
        """Version est 2.0."""
        assert PATTERN_ENGINE_VERSION == "2.0"
        engine = PatternEngine()
        assert engine.version == "2.0"
    
    def test_visual_patterns_defined(self):
        """Les patterns visuels sont définis."""
        assert "PTN_VIS_01" in [code for _, (code, _) in PATTERN_RULES_V2.items()]
    
    def test_compute_patterns_with_visual(self):
        """compute_patterns détecte les patterns visuels."""
        engine = PatternEngine(enable_visual=True)
        
        behaviors = [
            {"code": "STB_01", "status": "ACTIVE"},
        ]
        visual_signals = ["VIS_PRESS_HIGH"]
        
        patterns = engine.compute_patterns(behaviors, visual_signals=visual_signals)
        
        # Devrait détecter PTN_VIS_01 (STB_01 + VIS_PRESS_HIGH)
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert "PTN_VIS_01" in pattern_codes
    
    def test_is_visual_pattern(self):
        """is_visual_pattern fonctionne."""
        engine = PatternEngine(enable_visual=True)
        
        assert engine.is_visual_pattern("PTN_VIS_01") is True
        assert engine.is_visual_pattern("PTN_01") is False
    
    def test_visual_disabled(self):
        """Les patterns visuels sont ignorés si désactivés."""
        engine = PatternEngine(enable_visual=False)
        
        behaviors = [
            {"code": "STB_01", "status": "ACTIVE"},
        ]
        visual_signals = ["VIS_PRESS_HIGH"]
        
        patterns = engine.compute_patterns(behaviors, visual_signals=visual_signals)
        
        # Pas de pattern visuel
        pattern_codes = [p["pattern_code"] for p in patterns]
        assert "PTN_VIS_01" not in pattern_codes


# =============================================================================
# TESTS: PIPELINE v2.7
# =============================================================================

class TestPipelineV27:
    """Tests du Pipeline v2.7."""
    
    @pytest.fixture
    def raw_data_valid(self):
        """Données brutes valides."""
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
    def metadata(self):
        """Métadonnées de match."""
        return {
            "home_team": "Team A",
            "away_team": "Team B",
            "competition": "Test League",
        }
    
    def test_version(self):
        """Version est 2.7."""
        assert PIPELINE_VERSION == "2.7"
    
    def test_has_vision_engine(self):
        """Pipeline a un VisionEngine."""
        pipeline = Pipeline(enable_vision=True)
        assert hasattr(pipeline, 'vision_engine')
        assert pipeline.vision_engine is not None
    
    def test_has_memory_engine(self):
        """Pipeline a un MemoryEngine."""
        pipeline = Pipeline(enable_memory=True)
        assert hasattr(pipeline, 'memory_engine')
        assert pipeline.memory_engine is not None
    
    def test_run_analysis_basic(self, raw_data_valid, metadata):
        """run_analysis fonctionne sans vidéo ni mémoire."""
        pipeline = Pipeline(enable_vision=False, enable_memory=False)
        result = pipeline.run_analysis(raw_data_valid, metadata)
        
        assert "behaviors" in result
        assert "patterns" in result
        assert "flow" in result
        assert "report" in result
        assert "meta" in result
    
    def test_run_analysis_with_memory(self, raw_data_valid, metadata):
        """run_analysis fonctionne avec mémoire."""
        pipeline = Pipeline(enable_vision=False, enable_memory=True)
        
        result = pipeline.run_analysis(
            raw_data_valid, 
            metadata,
            team_id="FC_TEST"
        )
        
        assert "historical_context" in result
        assert result["meta"]["memory_engine_version"] == "1.0"
    
    def test_meta_contains_all_versions(self, raw_data_valid, metadata):
        """meta contient toutes les versions."""
        pipeline = Pipeline(enable_vision=True, enable_memory=True)
        result = pipeline.run_analysis(raw_data_valid, metadata)
        
        meta = result["meta"]
        assert meta["pipeline_version"] == "2.7"
        assert meta["pattern_engine_version"] == "2.0"
        assert "memory_engine_version" in meta
        assert "vision_engine_version" in meta


# =============================================================================
# TESTS: ANALYSIS BOT v3.2
# =============================================================================

class TestAnalysisBotV32:
    """Tests de l'AnalysisBot v3.2."""
    
    def test_version(self):
        """Version est 3.2."""
        bot = AnalysisBot()
        assert bot.VERSION == "3.2"
    
    def test_generate_report_with_historical_context(self):
        """generate_report accepte historical_context."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        patterns = [{"pattern_code": "PTN_04", "label": "Test", "sources": ["STB_02", "INT_01"], "category": "composite"}]
        flow = ["Phase 1 : Test"]
        historical_context = {
            "total_episodes": 5,
            "pattern_tendencies": {"PTN_04": 0.6},
            "vs_style": None,
        }
        
        report = bot.generate_report(
            metadata, 
            behavior_state, 
            patterns, 
            flow,
            historical_context=historical_context
        )
        
        assert "Historical context" in report
        assert "Historically" in report
    
    def test_report_never_mentions_win(self):
        """Le rapport ne mentionne JAMAIS 'win', 'won', 'victory'."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {}}
        historical_context = {
            "total_episodes": 5,
            "pattern_tendencies": {"PTN_04": 0.8},
        }
        
        report = bot.generate_report(
            metadata, 
            behavior_state, 
            historical_context=historical_context
        )
        
        report_lower = report.lower()
        assert "won" not in report_lower
        assert "victory" not in report_lower
        # "win" peut apparaître dans d'autres mots, vérifions le contexte
        assert "they won" not in report_lower
        assert "they have won" not in report_lower

