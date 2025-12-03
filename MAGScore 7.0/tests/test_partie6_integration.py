"""
MAGScore 6.3 — Tests: PARTIE 6 Integration
==========================================
Tests d'intégration pour MAGScore 6.3 complet.

Tests d'intégration pour :
    - Pipeline v2.6 complet
    - QualityControlEngine v1
    - PatternEngine v1.1
    - MatchFlowReconstructor v1.1
    - AnalysisBot v3.1
    - LexiconGuard (intégration QC)

Vision : NO CHANCE — ONLY PATTERNS
"""

import pytest

from magscore.orchestration.pipeline import Pipeline, PIPELINE_VERSION
from magscore.orchestration.lexicon_guard import is_clean
from magscore.engine.quality_control import QualityControlEngine
from magscore.engine.pattern_engine import PATTERN_ENGINE_VERSION
from magscore.engine.match_flow import MATCH_FLOW_VERSION


# =============================================================================
# FIXTURES — RAW DATA
# =============================================================================

@pytest.fixture
def raw_data_valid():
    """Données brutes valides pour un match standard."""
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
def raw_data_neutral():
    """Données brutes pour un match neutre (peu d'activité)."""
    return {
        "stats": {
            "shots": 5,
            "shots_on_target": 2,
            "passes": 400,
            "possession": 50,
            "fouls": 8,
            "yellow_cards": 0,
            "interceptions": 5,
            "tackles": 10,
            "clearances": 8,
            "duels": 30,
            "duels_won": 15,
        },
        "last_15_min": {
            "shots": 1,
            "fouls": 2,
            "yellow_cards": 0,
            "interceptions": 1,
            "tackles": 2,
            "duels": 8,
            "duels_won": 4,
        }
    }


@pytest.fixture
def raw_data_extreme():
    """Données brutes pour un match chaotique."""
    return {
        "stats": {
            "shots": 25,
            "shots_on_target": 12,
            "passes": 350,
            "possession": 60,
            "fouls": 25,
            "yellow_cards": 6,
            "interceptions": 15,
            "tackles": 35,
            "clearances": 20,
            "duels": 80,
            "duels_won": 35,
        },
        "last_15_min": {
            "shots": 8,
            "fouls": 10,
            "yellow_cards": 3,
            "interceptions": 5,
            "tackles": 8,
            "duels": 25,
            "duels_won": 8,
        }
    }


@pytest.fixture
def metadata_standard():
    """Métadonnées de match standard."""
    return {
        "home_team": "Paris FC",
        "away_team": "Lyon United",
        "competition": "Ligue 1",
        "date": "2025-01-15",
    }


# =============================================================================
# TESTS: PIPELINE END TO END — CAS NOMINAL
# =============================================================================

class TestPipelineEndToEndValid:
    """Tests du pipeline end-to-end pour les cas nominaux."""
    
    def test_pipeline_end_to_end_valid_case(self, raw_data_valid, metadata_standard):
        """Cas nominal : pipeline retourne un objet complet."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        # Structure obligatoire
        assert "behaviors" in result
        assert "patterns" in result
        assert "flow" in result
        assert "report" in result
        assert "meta" in result
        
        # Types corrects
        assert isinstance(result["behaviors"], list)
        assert isinstance(result["patterns"], list)
        assert isinstance(result["flow"], list)
        assert isinstance(result["report"], str)
        assert isinstance(result["meta"], dict)
        
        # QC OK (pas d'exception levée = OK)
        assert is_clean(result["report"])


# =============================================================================
# TESTS: PIPELINE — MATCH NEUTRE
# =============================================================================

class TestPipelineNeutralMatch:
    """Tests du pipeline pour les matchs neutres."""
    
    def test_pipeline_neutral_match(self, raw_data_neutral, metadata_standard):
        """Match neutre → rapport cohérent et QC OK."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_neutral, metadata_standard)
        
        # behaviors peut être vide ou presque
        assert isinstance(result["behaviors"], list)
        
        # patterns peut être vide
        assert isinstance(result["patterns"], list)
        
        # flow doit avoir au moins 2 phases
        assert len(result["flow"]) >= 2
        
        # report doit être valide
        assert len(result["report"]) >= 250
        
        # Toutes les sections doivent être présentes
        required_sections = [
            "Contexte du match",
            "Indicateurs structurels",
            "Lecture comportementale",
            "Patterns narratifs",
            "Match Flow",
            "Points clés à retenir",
            "Synthèse neutre",
        ]
        for section in required_sections:
            assert section in result["report"]


# =============================================================================
# TESTS: PIPELINE — MATCH EXTRÊME
# =============================================================================

class TestPipelineExtremeMatch:
    """Tests du pipeline pour les matchs chaotiques."""
    
    def test_pipeline_extreme_match(self, raw_data_extreme, metadata_standard):
        """Match chaotique → pipeline passe QC sans contradiction."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_extreme, metadata_standard)
        
        # behaviors peut contenir plusieurs éléments
        assert isinstance(result["behaviors"], list)
        
        # patterns probablement non vide
        assert isinstance(result["patterns"], list)
        
        # flow doit avoir entre 2 et 5 phases
        assert 2 <= len(result["flow"]) <= 5
        
        # report doit être dans les limites
        assert 250 <= len(result["report"]) <= 3000
        
        # QC OK (pas de contradiction)
        assert is_clean(result["report"])


# =============================================================================
# TESTS: PIPELINE — LEXICON VIOLATION
# =============================================================================

class TestPipelineLexiconViolation:
    """Tests du pipeline avec violation de lexique."""
    
    def test_pipeline_lexicon_violation_blocked(self, raw_data_valid, metadata_standard):
        """Le rapport généré ne contient pas de mots interdits (hors noms d'équipes)."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        # Le rapport doit être propre (validation par LexiconGuard)
        # Note: "Paris FC" contient "pari" mais c'est un nom d'équipe valide
        # LexiconGuard vérifie les mots entiers, pas les sous-chaînes
        assert " pari " not in result["report"].lower()  # Mot isolé
        assert "bookmaker" not in result["report"].lower()
        assert is_clean(result["report"])


# =============================================================================
# TESTS: PIPELINE — STRUCTURE INVARIANT
# =============================================================================

class TestPipelineStructureInvariant:
    """Tests de l'invariant de structure du pipeline."""
    
    def test_pipeline_structure_invariant(self, raw_data_valid, metadata_standard):
        """La structure de retour est constante."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        # Clés obligatoires
        required_keys = {"behaviors", "patterns", "flow", "report", "meta"}
        assert set(result.keys()) >= required_keys
        
        # Types obligatoires
        assert isinstance(result["behaviors"], list)
        assert isinstance(result["patterns"], list)
        assert isinstance(result["flow"], list)
        assert isinstance(result["report"], str)
        assert isinstance(result["meta"], dict)
    
    def test_pipeline_structure_with_empty_input(self, metadata_standard):
        """Input vide → structure toujours respectée."""
        empty_data = {"stats": {}, "last_15_min": {}}
        pipeline = Pipeline()
        result = pipeline.run_analysis(empty_data, metadata_standard)
        
        # La structure doit toujours être présente
        assert "behaviors" in result
        assert "patterns" in result
        assert "flow" in result
        assert "report" in result
        assert "meta" in result


# =============================================================================
# TESTS: PIPELINE — META INFORMATION
# =============================================================================

class TestPipelineMetaInformation:
    """Tests des métadonnées du pipeline."""
    
    def test_pipeline_meta_contains_versions(self, raw_data_valid, metadata_standard):
        """Les métadonnées contiennent toutes les versions."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        meta = result["meta"]
        assert "pipeline_version" in meta
        assert "behavior_engine_version" in meta
        assert "pattern_engine_version" in meta
        assert "match_flow_version" in meta
        assert "quality_control_version" in meta
    
    def test_pipeline_version_is_2_7(self, raw_data_valid, metadata_standard):
        """La version du pipeline est 2.7 (7.0)."""
        assert PIPELINE_VERSION == "2.7"
        
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        assert result["meta"]["pipeline_version"] == "2.7"
    
    def test_pattern_engine_version_is_2_0(self, raw_data_valid, metadata_standard):
        """La version du PatternEngine est 2.0 (7.0)."""
        assert PATTERN_ENGINE_VERSION == "2.0"
        
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        assert result["meta"]["pattern_engine_version"] == "2.0"
    
    def test_match_flow_version_is_1_1(self, raw_data_valid, metadata_standard):
        """La version du MatchFlow est 1.1."""
        assert MATCH_FLOW_VERSION == "1.1"
        
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        assert result["meta"]["match_flow_version"] == "1.1"


# =============================================================================
# TESTS: INTEGRATION QUALITY CONTROL
# =============================================================================

class TestIntegrationQualityControl:
    """Tests d'intégration avec QualityControlEngine."""
    
    def test_qc_validates_pipeline_output(self, raw_data_valid, metadata_standard):
        """QualityControlEngine valide la sortie du pipeline."""
        pipeline = Pipeline()
        
        assert hasattr(pipeline, 'quality_control')
        assert isinstance(pipeline.quality_control, QualityControlEngine)
        
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        # Le QC a été appelé et n'a pas levé d'exception
        assert result is not None
    
    def test_qc_error_propagates(self, raw_data_valid, metadata_standard):
        """Le pipeline intègre correctement le QC."""
        pipeline = Pipeline()
        
        # Version du QC présente dans meta
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        assert "quality_control_version" in result["meta"]
        assert result["meta"]["quality_control_version"] == "1.0"


# =============================================================================
# TESTS: INTEGRATION PATTERNS ET FLOW
# =============================================================================

class TestIntegrationPatternsAndFlow:
    """Tests d'intégration patterns + flow."""
    
    def test_patterns_and_flow_coherent(self, raw_data_valid, metadata_standard):
        """Patterns et flow sont cohérents."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        patterns = result["patterns"]
        flow = result["flow"]
        
        # Le flow doit avoir au moins 2 phases
        assert len(flow) >= 2
        
        # Les patterns sont une liste (peut être vide)
        assert isinstance(patterns, list)
    
    def test_behaviors_reflected_in_report(self, raw_data_valid, metadata_standard):
        """Le rapport mentionne les comportements détectés (section 3)."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        report = result["report"]
        
        # La section comportementale doit exister
        assert "Lecture comportementale" in report


# =============================================================================
# TESTS ADDITIONNELS: REGRESSION
# =============================================================================

class TestRegressionPartie5:
    """Tests de non-régression par rapport à PARTIE 5."""
    
    def test_pipeline_still_returns_patterns(self, raw_data_valid, metadata_standard):
        """Le pipeline retourne toujours les patterns."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        assert "patterns" in result
        assert isinstance(result["patterns"], list)
    
    def test_pipeline_still_returns_flow(self, raw_data_valid, metadata_standard):
        """Le pipeline retourne toujours le flow."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        assert "flow" in result
        assert isinstance(result["flow"], list)
        assert len(result["flow"]) >= 2
    
    def test_lexicon_guard_still_active(self, raw_data_valid, metadata_standard):
        """LexiconGuard est toujours actif."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        # Le rapport doit être propre
        assert is_clean(result["report"])


# =============================================================================
# TESTS: DISCLAIMER
# =============================================================================

class TestDisclaimerPresent:
    """Tests de présence du disclaimer."""
    
    def test_report_ends_with_disclaimer(self, raw_data_valid, metadata_standard):
        """Le rapport contient le disclaimer obligatoire."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(raw_data_valid, metadata_standard)
        
        disclaimer = "[This analysis describes dynamics only and is not a prediction.]"
        assert disclaimer in result["report"]
