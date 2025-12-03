"""
MAGScore 7.0 — Pipeline v2.7
=============================
Conforme Constitution-MAGScore Section 6.

Orchestration complète (MAGScore 7.0) :
    raw_data -> normalize -> modules_signaux -> SignalMemory.smooth() 
    -> VisionEngine (si dispo) -> BehaviorEngine 
    -> PatternEngine v2 -> MatchFlow v1.1 
    -> MemoryEngine -> AnalysisBot v3.2 
    -> LexiconGuard -> QualityControlEngine v1

Pipeline neutre :
    API → normalize_api → modules_signaux → signal_memory → vision_engine
    → behavior_engine → pattern_engine → match_flow → memory_engine 
    → analysis_bot → lexicon_guard → quality_control

Règle absolue : Aucune prédiction.
"""

from typing import Dict, Any, Optional, List

from ..external.normalize_api import normalize
from ..modules.stability import StabilityModule
from ..modules.intensity import IntensityModule
from ..modules.psychology import PsychologyModule
from ..modules.cohesion import CohesionModule
from ..engine.behavior_engine import BehaviorEngine
from ..engine.pattern_engine import PatternEngine
from ..engine.signal_memory import SignalMemory
from ..engine.match_flow import MatchFlowReconstructor
from ..engine.quality_control import QualityControlEngine, QualityControlError
from ..engine.vision_engine import VisionEngine, VisionEngineError
from ..engine.memory_engine import MemoryEngine, ForbiddenDataError
from ..bots.analysis_bot import AnalysisBot
from .lexicon_guard import validate as validate_lexicon, LexiconGuardError


# =============================================================================
# PIPELINE VERSION
# =============================================================================

PIPELINE_VERSION = "2.7"


# =============================================================================
# EXCEPTIONS
# =============================================================================

class PipelineError(Exception):
    """Exception levée en cas d'erreur du pipeline."""
    pass


class NormalizationError(PipelineError):
    """Exception levée en cas d'erreur de normalisation."""
    pass


class SignalExtractionError(PipelineError):
    """Exception levée en cas d'erreur d'extraction de signaux."""
    pass


class ReportGenerationError(PipelineError):
    """Exception levée en cas d'erreur de génération du rapport."""
    pass


class LexiconViolationError(PipelineError):
    """Exception levée en cas de violation du lexique."""
    pass


class QualityControlViolationError(PipelineError):
    """Exception levée en cas d'échec du contrôle qualité."""
    pass


# =============================================================================
# PIPELINE v2.7
# =============================================================================

class Pipeline:
    """
    Pipeline principal MAGScore 7.0 v2.7.
    
    Orchestration complète (MAGScore 7.0) :
        1. Normalisation des données brutes (normalize_api)
        2. Extraction des signaux (4 modules)
        3. Lissage des signaux (SignalMemory v1)
        4. Traitement visuel optionnel (VisionEngine v1) ← NOUVEAU
        5. Calcul des comportements (BehaviorEngine v2.3)
        6. Détection des patterns (PatternEngine v2) ← MIS À JOUR
        7. Reconstruction du flow (MatchFlowReconstructor v1.1)
        8. Stockage mémoire sécurisé (MemoryEngine v1) ← NOUVEAU
        9. Génération du rapport (AnalysisBot v3.2) ← MIS À JOUR
        10. Validation lexicale (LexiconGuard v2)
        11. Contrôle qualité final (QualityControlEngine v1)
    
    Vision : NO CHANCE — ONLY PATTERNS
    Aucune prédiction, aucune influence.
    """
    
    def __init__(self, enable_vision: bool = True, enable_memory: bool = True) -> None:
        """
        Initialise le pipeline avec tous les composants.
        
        Args:
            enable_vision: Active le traitement visuel (7.0).
            enable_memory: Active le stockage mémoire (7.0).
        """
        # Modules de signaux
        self.stability_module = StabilityModule()
        self.intensity_module = IntensityModule()
        self.psychology_module = PsychologyModule()
        self.cohesion_module = CohesionModule()
        
        # Lisseur de signaux
        self.signal_memory = SignalMemory(max_memory=3)
        
        # Moteur comportemental
        self.behavior_engine = BehaviorEngine()
        
        # Pattern Engine v2 (avec support visuel)
        self.pattern_engine = PatternEngine(enable_visual=enable_vision)
        
        # Match Flow Reconstructor v1.1
        self.match_flow = MatchFlowReconstructor()
        
        # Bot d'analyse v3.2
        self.analysis_bot = AnalysisBot()
        
        # Quality Control Engine v1
        self.quality_control = QualityControlEngine()
        
        # Vision Engine v1 (NOUVEAU 7.0)
        self._enable_vision = enable_vision
        self.vision_engine = VisionEngine() if enable_vision else None
        
        # Memory Engine v1 (NOUVEAU 7.0)
        self._enable_memory = enable_memory
        self.memory_engine = MemoryEngine() if enable_memory else None
    
    def run_analysis(
        self, 
        raw_match_data: Dict[str, Any], 
        metadata: Dict[str, Any],
        video_url: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute l'analyse complète avec support visuel et mémoire (7.0).
        
        Args:
            raw_match_data: Données brutes du match (format API).
            metadata: Informations sur le match.
                      {
                          "home_team": str,
                          "away_team": str,
                          "competition": str (optionnel),
                          "kickoff_time": str (optionnel),
                          "opposing_style": str (optionnel, pour mémoire)
                      }
            video_url: URL du flux vidéo (optionnel, 7.0).
            team_id: ID de l'équipe pour la mémoire (optionnel, 7.0).
        
        Returns:
            Dict contenant :
            {
                "behaviors": List[Dict],
                "patterns": List[Dict],
                "flow": List[str],
                "report": str,
                "visual_signals": List[str] (si vidéo),
                "historical_context": Dict (si mémoire),
                "meta": {
                    "pipeline_version": str,
                    "behavior_engine_version": str,
                    "pattern_engine_version": str,
                    "vision_engine_version": str (si actif),
                    "memory_engine_version": str (si actif),
                    ...
                }
            }
        
        Raises:
            NormalizationError: Si la normalisation échoue.
            SignalExtractionError: Si l'extraction des signaux échoue.
            ReportGenerationError: Si la génération du rapport échoue.
            LexiconViolationError: Si le rapport contient des termes interdits.
            QualityControlViolationError: Si le contrôle qualité échoue.
        """
        try:
            # =================================================================
            # ÉTAPE 1: Normalisation
            # =================================================================
            normalized = normalize(raw_match_data)
            
        except Exception as e:
            raise NormalizationError(f"Normalization failed: {str(e)}") from e
        
        try:
            # =================================================================
            # ÉTAPE 2: Extraction des signaux bruts (globaux et last_15)
            # =================================================================
            
            # Stability
            stability_global = self.stability_module.compute_global(normalized)
            stability_last15 = self.stability_module.compute_last_15(normalized)
            
            # Intensity
            intensity_global = self.intensity_module.compute_global(normalized)
            intensity_last15 = self.intensity_module.compute_last_15(normalized)
            
            # Psychology
            psychology_global = self.psychology_module.compute_global(normalized)
            psychology_last15 = self.psychology_module.compute_last_15(normalized)
            
            # Cohesion (auxiliaire)
            cohesion_global = self.cohesion_module.compute_global(normalized)
            cohesion_last15 = self.cohesion_module.compute_last_15(normalized)
            
        except Exception as e:
            raise SignalExtractionError(f"Signal extraction failed: {str(e)}") from e
        
        # =====================================================================
        # ÉTAPE 3: Construction des signaux RAW par catégorie
        # =====================================================================
        
        signals_raw = {
            "stability": stability_global,
            "intensity": intensity_global,
            "psychology": psychology_global,
            "cohesion": cohesion_global,
        }
        
        # =====================================================================
        # ÉTAPE 4: Lissage des signaux (SignalMemory v1)
        # =====================================================================
        
        signals_smoothed = self.signal_memory.smooth(signals_raw)
        
        # =====================================================================
        # ÉTAPE 4.5: Traitement visuel (VisionEngine v1 - 7.0)
        # =====================================================================
        
        visual_signals: List[str] = []
        visual_raw: Dict[str, float] = {}
        
        if self._enable_vision and video_url and self.vision_engine:
            try:
                visual_result = self.vision_engine.process_and_discretize(video_url)
                visual_signals = visual_result.discrete
                visual_raw = visual_result.raw
            except VisionEngineError as e:
                # Vision non critique, continuer sans
                pass
        
        # =====================================================================
        # ÉTAPE 5: Construction des time_slices avec signaux lissés
        # =====================================================================
        
        time_slices = {
            "global": {
                **signals_smoothed.get("stability", stability_global),
                **signals_smoothed.get("intensity", intensity_global),
                **signals_smoothed.get("psychology", psychology_global),
                **signals_smoothed.get("cohesion", cohesion_global),
            },
            "last_15_min": {
                **stability_last15,
                **intensity_last15,
                **psychology_last15,
                **cohesion_last15,
            },
        }
        
        # =====================================================================
        # ÉTAPE 6: Calcul des comportements (BehaviorEngine v2.3)
        # =====================================================================
        
        behavior_state = self.behavior_engine.compute_behaviors(
            signals_smoothed, 
            time_slices
        )
        
        behaviors = behavior_state.get("behaviors", [])
        
        # =====================================================================
        # ÉTAPE 7: Détection des patterns (PatternEngine v2)
        # =====================================================================
        
        patterns = self.pattern_engine.compute_patterns(
            behaviors,
            visual_signals=visual_signals if visual_signals else None
        )
        
        # =====================================================================
        # ÉTAPE 8: Reconstruction du flow (MatchFlow v1.1)
        # =====================================================================
        
        flow = self.match_flow.reconstruct(behaviors)
        
        # =====================================================================
        # ÉTAPE 8.5: Stockage mémoire sécurisé (MemoryEngine v1 - 7.0)
        # =====================================================================
        
        historical_context: Dict[str, Any] = {}
        
        if self._enable_memory and team_id and self.memory_engine:
            try:
                # Récupérer le contexte historique AVANT d'ajouter le nouvel épisode
                opposing_style = metadata.get("opposing_style", "")
                historical_context = self.memory_engine.get_historical_context(
                    team_id, opposing_style
                )
                
                # Ingérer le nouvel épisode (SÉCURISÉ)
                self.memory_engine.ingest(
                    team_id=team_id,
                    data={
                        "match_id": f"{metadata.get('home_team', 'A')}_{metadata.get('away_team', 'B')}",
                        "behaviors": [b.get("code", "") for b in behaviors if b.get("status") == "ACTIVE"],
                        "patterns": [p.get("pattern_code", "") for p in patterns],
                        "flow_phases": [f.split(" : ", 1)[-1] if " : " in f else f for f in flow],
                        "opposing_style": opposing_style,
                        # NOTE: Pas de score, result, odds ici (SÉCURITÉ)
                    },
                    strict=True
                )
            except ForbiddenDataError:
                # Ne devrait jamais arriver avec les données du pipeline
                pass
        
        try:
            # =================================================================
            # ÉTAPE 9: Génération du rapport (AnalysisBot v3.2)
            # =================================================================
            
            report = self.analysis_bot.generate_report(
                metadata, 
                behavior_state, 
                patterns, 
                flow,
                historical_context=historical_context if historical_context else None
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Report generation failed: {str(e)}") from e
        
        try:
            # =================================================================
            # ÉTAPE 10: Validation lexicale (garde-fou)
            # =================================================================
            
            validate_lexicon(report)
            
        except LexiconGuardError as e:
            raise LexiconViolationError(
                f"Report contains forbidden terms: {e.violations}"
            ) from e
        
        # =====================================================================
        # ÉTAPE 11: Construction du résultat final
        # =====================================================================
        
        final_payload = {
            "behaviors": behaviors,
            "patterns": patterns,
            "flow": flow,
            "report": report,
            "meta": {
                "pipeline_version": PIPELINE_VERSION,
                "behavior_engine_version": behavior_state["meta"].get("version", "unknown"),
                "pattern_engine_version": self.pattern_engine.version,
                "signal_memory_version": self.signal_memory.version,
                "match_flow_version": self.match_flow.version,
                "quality_control_version": self.quality_control.version,
                "behaviors_detected": behavior_state["meta"].get("behaviors_detected", 0),
                "patterns_detected": len(patterns),
                "recency_model": behavior_state["meta"].get("recency_model", "unknown"),
            },
        }
        
        # Ajouter les infos 7.0 si actives
        if self._enable_vision and self.vision_engine:
            final_payload["visual_signals"] = visual_signals
            final_payload["visual_raw"] = visual_raw
            final_payload["meta"]["vision_engine_version"] = self.vision_engine.version
        
        if self._enable_memory and self.memory_engine:
            final_payload["historical_context"] = historical_context
            final_payload["meta"]["memory_engine_version"] = self.memory_engine.version
        
        try:
            # =================================================================
            # ÉTAPE 12: Contrôle qualité final (QualityControlEngine v1)
            # =================================================================
            
            self.quality_control.validate(
                behaviors=behaviors,
                patterns=patterns,
                flow=flow,
                report_text=report,
                final_payload=final_payload
            )
            
        except QualityControlError as e:
            raise QualityControlViolationError(
                f"Quality control failed: {str(e)}"
            ) from e
        
        return final_payload
    
    # =========================================================================
    # LEGACY METHODS (rétrocompatibilité)
    # =========================================================================
    
    def run(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Méthode legacy - non implémentée (nécessite API handler).
        
        Args:
            match_id: Identifiant unique du match.
        
        Returns:
            None (méthode legacy).
        """
        return {
            "match_id": match_id,
            "status": "not_implemented",
            "message": "Use run_analysis() with raw data instead",
        }
    
    def run_from_data(
        self, 
        raw_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Méthode legacy - redirige vers run_analysis.
        
        Args:
            raw_data: Données brutes au format API.
            metadata: Métadonnées optionnelles.
        
        Returns:
            Même format que run_analysis().
        """
        if metadata is None:
            metadata = {
                "home_team": "Team A",
                "away_team": "Team B",
            }
        
        return self.run_analysis(raw_data, metadata)
    
    def _extract_all_signals(
        self, 
        normalized_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Extrait les signaux de tous les modules.
        
        Args:
            normalized_data: Données normalisées.
        
        Returns:
            Dict avec signaux par module.
        """
        return {
            "stability": self.stability_module.compute_global(normalized_data),
            "intensity": self.intensity_module.compute_global(normalized_data),
            "psychology": self.psychology_module.compute_global(normalized_data),
            "cohesion": self.cohesion_module.compute_global(normalized_data),
        }
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """
        Valide la sortie du pipeline.
        
        Args:
            result: Résultat du pipeline.
        
        Returns:
            True si valide.
        """
        try:
            report = result.get("report", "")
            validate_lexicon(report)
            return True
        except LexiconGuardError:
            return False
