"""
MAGScore 6.1 — Tests: PARTIE 4 Integration
==========================================
Tests d'intégration pour la chaîne complète :
    normalize_api -> modules -> BehaviorEngine -> AnalysisBot -> LexiconGuard

Vérifie :
    - Modules v2 (compute_global / compute_last_15)
    - Pipeline v2 (run_analysis)
    - AnalysisBot v2 (generate_report)
    - LexiconGuard v2 (validate)
"""

import pytest
from magscore.orchestration.pipeline import (
    Pipeline,
    PIPELINE_VERSION,
    LexiconViolationError,
)
from magscore.orchestration.lexicon_guard import (
    validate,
    find_violations,
    is_clean,
    LexiconGuardError,
    BLACKLIST,
    WHITELIST,
)
from magscore.bots.analysis_bot import AnalysisBot
from magscore.modules.stability import StabilityModule
from magscore.modules.intensity import IntensityModule
from magscore.modules.psychology import PsychologyModule
from magscore.modules.cohesion import CohesionModule


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_raw_data():
    """Données brutes de test."""
    return {
        "stats": {
            "shots": 15,
            "shots_on_target": 6,
            "passes": 450,
            "passes_completed": 380,
            "possession": 55,
            "fouls": 12,
            "yellow_cards": 2,
            "red_cards": 0,
            "interceptions": 8,
            "tackles": 18,
            "clearances": 12,
            "blocks": 4,
            "saves": 3,
            "duels": 45,
            "duels_won": 25,
            "distance_covered": 105,
            "sprints": 120,
        },
        "last_15_min": {
            "shots": 4,
            "shots_on_target": 2,
            "fouls": 4,
            "yellow_cards": 1,
            "interceptions": 2,
            "tackles": 5,
            "clearances": 3,
            "duels": 12,
            "duels_won": 5,
        }
    }


@pytest.fixture
def sample_metadata():
    """Métadonnées de test."""
    return {
        "home_team": "Paris FC",
        "away_team": "Lyon United",
        "competition": "Ligue 1",
        "kickoff_time": "2025-12-02T20:45:00Z",
    }


# =============================================================================
# TESTS: MODULES v2
# =============================================================================

class TestModulesV2Interface:
    """Tests de l'interface des modules v2."""
    
    def test_stability_module_has_compute_methods(self):
        """StabilityModule doit avoir compute_global et compute_last_15."""
        module = StabilityModule()
        assert hasattr(module, 'compute_global')
        assert hasattr(module, 'compute_last_15')
        assert callable(module.compute_global)
        assert callable(module.compute_last_15)
    
    def test_intensity_module_has_compute_methods(self):
        """IntensityModule doit avoir compute_global et compute_last_15."""
        module = IntensityModule()
        assert hasattr(module, 'compute_global')
        assert hasattr(module, 'compute_last_15')
    
    def test_psychology_module_has_compute_methods(self):
        """PsychologyModule doit avoir compute_global et compute_last_15."""
        module = PsychologyModule()
        assert hasattr(module, 'compute_global')
        assert hasattr(module, 'compute_last_15')
    
    def test_cohesion_module_has_compute_methods(self):
        """CohesionModule doit avoir compute_global et compute_last_15."""
        module = CohesionModule()
        assert hasattr(module, 'compute_global')
        assert hasattr(module, 'compute_last_15')


class TestModulesV2Output:
    """Tests des sorties des modules v2."""
    
    def test_stability_outputs_required_keys(self, sample_raw_data):
        """StabilityModule doit retourner les clés obligatoires."""
        module = StabilityModule()
        result = module.compute_global(sample_raw_data)
        
        required_keys = [
            "low_block_drop",
            "xg_against_spike",
            "high_compactness",
            "successful_low_block",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
            assert isinstance(result[key], float)
            assert 0.0 <= result[key] <= 1.5  # Max avec pondération
    
    def test_intensity_outputs_required_keys(self, sample_raw_data):
        """IntensityModule doit retourner les clés obligatoires."""
        module = IntensityModule()
        result = module.compute_global(sample_raw_data)
        
        required_keys = [
            "pressing_wave",
            "high_duel_pressure",
            "running_distance_drop",
            "duel_loss_spike",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
            assert isinstance(result[key], float)
    
    def test_psychology_outputs_required_keys(self, sample_raw_data):
        """PsychologyModule doit retourner les clés obligatoires."""
        module = PsychologyModule()
        result = module.compute_global(sample_raw_data)
        
        required_keys = [
            "fouls_spike",
            "protest_pattern",
            "high_defensive_recovery",
            "late_pressing_effort",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
            assert isinstance(result[key], float)
    
    def test_last_15_differs_from_global(self, sample_raw_data):
        """compute_last_15 peut différer de compute_global."""
        module = StabilityModule()
        
        global_result = module.compute_global(sample_raw_data)
        last_15_result = module.compute_last_15(sample_raw_data)
        
        # Les deux doivent avoir les mêmes clés
        assert set(global_result.keys()) == set(last_15_result.keys())


# =============================================================================
# TESTS: PIPELINE v2
# =============================================================================

class TestPipelineV2:
    """Tests du Pipeline v2.5 (PARTIE 5)."""
    
    def test_pipeline_version(self):
        """Vérifie la version du pipeline (mise à jour 7.0)."""
        assert PIPELINE_VERSION == "2.7"
    
    def test_pipeline_has_run_analysis(self):
        """Pipeline doit avoir la méthode run_analysis."""
        pipeline = Pipeline()
        assert hasattr(pipeline, 'run_analysis')
        assert callable(pipeline.run_analysis)
    
    def test_run_analysis_returns_expected_structure(self, sample_raw_data, sample_metadata):
        """run_analysis doit retourner la structure attendue."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        assert "behaviors" in result
        assert "report" in result
        assert "meta" in result
        
        assert "pipeline_version" in result["meta"]
        assert "behavior_engine_version" in result["meta"]
    
    def test_run_analysis_produces_report(self, sample_raw_data, sample_metadata):
        """run_analysis doit produire un rapport textuel."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        report = result["report"]
        
        assert isinstance(report, str)
        assert len(report) > 100
        assert "1) Contexte du match" in report
        assert "7) Synthèse neutre" in report  # v2.5 has 7 sections
    
    def test_report_contains_disclaimer(self, sample_raw_data, sample_metadata):
        """Le rapport doit contenir le disclaimer."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        report = result["report"]
        assert "This analysis describes dynamics only and is not a prediction." in report
    
    def test_report_is_lexicon_clean(self, sample_raw_data, sample_metadata):
        """Le rapport ne doit contenir aucun terme interdit."""
        pipeline = Pipeline()
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        report = result["report"]
        
        # Le rapport a déjà été validé, mais vérifions
        assert is_clean(report)


# =============================================================================
# TESTS: LEXICON GUARD v2
# =============================================================================

class TestLexiconGuardV2:
    """Tests du LexiconGuard v2."""
    
    def test_validate_raises_on_forbidden(self):
        """validate doit lever une exception sur terme interdit."""
        with pytest.raises(LexiconGuardError):
            validate("This is a surebet for tonight!")
    
    def test_validate_passes_clean_text(self):
        """validate ne doit pas lever d'exception sur texte propre."""
        clean_text = "The team shows good stability and intensity."
        validate(clean_text)  # Ne doit pas lever
    
    def test_find_violations_returns_list(self):
        """find_violations doit retourner une liste."""
        text = "This is a pari with value bet potential."
        violations = find_violations(text)
        
        assert isinstance(violations, list)
        assert "pari" in violations
        assert "value" in violations
    
    def test_blacklist_contains_required_terms(self):
        """La blacklist doit contenir les termes requis."""
        required = ["pari", "parier", "mise", "cote", "odds", "bankroll", 
                    "prono", "value", "surebet", "jackpot", "gagnera",
                    "gagnant", "garanti", "probabilité", "favori", "favorite"]
        
        for term in required:
            assert term in BLACKLIST, f"Missing from blacklist: {term}"
    
    def test_whitelist_contains_neutral_terms(self):
        """La whitelist doit contenir les termes neutres."""
        neutral = ["stabilité", "intensité", "cohésion", "dynamique",
                   "contrôle", "pression", "comportement", "pattern"]
        
        for term in neutral:
            assert term in WHITELIST, f"Missing from whitelist: {term}"


# =============================================================================
# TESTS: ANALYSIS BOT v2
# =============================================================================

class TestAnalysisBotV2:
    """Tests de l'AnalysisBot v2."""
    
    def test_generate_report_interface(self):
        """generate_report doit accepter metadata et behavior_state."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {"behaviors": [], "meta": {"version": "2.3"}}
        
        report = bot.generate_report(metadata, behavior_state)
        
        assert isinstance(report, str)
    
    def test_report_has_five_sections(self):
        """Le rapport doit avoir 5 sections."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "Team A", "away_team": "Team B"}
        behavior_state = {"behaviors": [], "meta": {}}
        
        report = bot.generate_report(metadata, behavior_state)
        
        # v3 has 7 sections
        assert "1) Contexte du match" in report
        assert "2) Indicateurs structurels" in report
        assert "3) Lecture comportementale" in report
        assert "4) Patterns narratifs" in report
        assert "5) Match Flow" in report
        assert "6) Points clés à retenir" in report
        assert "7) Synthèse neutre" in report
    
    def test_report_mentions_teams(self):
        """Le rapport doit mentionner les équipes."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "Manchester City", "away_team": "Liverpool"}
        behavior_state = {"behaviors": [], "meta": {}}
        
        report = bot.generate_report(metadata, behavior_state)
        
        assert "Manchester City" in report
        assert "Liverpool" in report
    
    def test_report_with_behaviors(self):
        """Le rapport doit décrire les comportements détectés."""
        bot = AnalysisBot()
        
        metadata = {"home_team": "A", "away_team": "B"}
        behavior_state = {
            "behaviors": [
                {
                    "code": "STB_01",
                    "label": "Effondrement Structurel",
                    "category": "stability",
                    "intensity": 0.75,
                    "time_slice": "last_15_min",
                    "status": "ACTIVE",
                }
            ],
            "meta": {"version": "2.3"}
        }
        
        report = bot.generate_report(metadata, behavior_state)
        
        # Le rapport doit mentionner quelque chose sur la stabilité
        assert "stability" in report.lower() or "structural" in report.lower()


# =============================================================================
# TESTS: FULL INTEGRATION
# =============================================================================

class TestFullIntegration:
    """Tests d'intégration complète de la chaîne."""
    
    def test_end_to_end_pipeline(self, sample_raw_data, sample_metadata):
        """Test complet de bout en bout."""
        pipeline = Pipeline()
        
        # Exécuter l'analyse
        result = pipeline.run_analysis(sample_raw_data, sample_metadata)
        
        # Vérifier la structure
        assert "behaviors" in result
        assert "report" in result
        assert "meta" in result
        
        # Vérifier le rapport
        report = result["report"]
        assert isinstance(report, str)
        assert len(report) > 0
        
        # Vérifier l'absence de termes interdits
        violations = find_violations(report)
        assert len(violations) == 0, f"Found violations: {violations}"
        
        # Vérifier le disclaimer
        assert "prediction" in report.lower()
    
    def test_empty_data_handled(self, sample_metadata):
        """Le pipeline doit gérer les données vides."""
        pipeline = Pipeline()
        
        result = pipeline.run_analysis({}, sample_metadata)
        
        assert "report" in result
        assert isinstance(result["report"], str)
