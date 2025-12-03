"""
MAGScore 6.1 — Behavior Engine v2.3
====================================
Conforme Constitution-MAGScore Section 2.
Conforme BEHAVIORENGINE_v2_SPEC_FINAL — Version 2.3 (Gemini-Validated)

Règles obligatoires :
- 2.1 Convergence obligatoire : minimum 2 signaux convergents
- 2.2 Signaux isolés interdits : un signal seul = aucune valeur
- 2.3 Contexte tactique prioritaire : signal contradictoire au plan = ignoré
- 2.6 Pondération : 3 signaux = x1.5, contradictoires = AMBIGU
- 2.7 Annulation intelligente : comportements opposés -> récent domine

Time Slicing : global vs last_15_min
Recency Model : last_15_priority (Money Time ne doit jamais être écrasé)
Raw Data Only : dépend du Sanitizer (normalize_api.py)

ORDRE D'ORCHESTRATION (Gemini-Validated) :
    1. _merge_slices()           → Fusion multi-slice
    2. _apply_recency_strategy() → Recency AVANT contradictions
    3. _resolve_contradictions() → AMBIGU si conflit reste
    4. _sort_by_priority()       → Tri final par catégorie
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .definitions import (
    BEHAVIOR_DEFINITIONS,
    SIGNAL_ACTIVATION_THRESHOLD,
    MIN_REQUIRED_SIGNALS,
    PONDERATION_FACTOR,
    TIME_SLICES,
    CONTRADICTION_PAIRS,
    are_behaviors_contradicting,
    ALL_REQUIRED_SIGNALS,
    CATEGORIES,
)


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class BehaviorStatus(Enum):
    """Statut d'un comportement détecté."""
    ACTIVE = "ACTIVE"            # Comportement confirmé (≥2 signaux actifs)
    INACTIVE = "INACTIVE"        # Pas assez de signaux
    AMBIGUOUS = "AMBIGUOUS"      # Signaux contradictoires détectés
    CANCELLED = "CANCELLED"      # Annulé par comportement plus récent


class TimeSlice(Enum):
    """Découpage temporel du match pour le Time Slicing."""
    GLOBAL = "global"
    LAST_15_MIN = "last_15_min"


# Version du moteur
ENGINE_VERSION = "2.3"

# Ordre de priorité des catégories (affichage)
# psychology > intensity > stability
CATEGORY_ORDER: Dict[str, int] = {
    "psychology": 0,
    "intensity": 1,
    "stability": 2,
}

# Recency model
RECENCY_MODEL = "last_15_priority"


# =============================================================================
# BEHAVIOR ENGINE v2.3
# =============================================================================

class BehaviorEngine:
    """
    Behavior Engine v2.3 — Moteur de détection comportementale.
    
    Pipeline complet :
        Signaux normalisés → Activation par seuil → Convergence → 
        Pondération → Merge Slices → Recency Strategy → 
        Resolve Contradictions → Sort by Priority
    
    Règles critiques (SPEC 2.3) :
        1. SIGNAL_ACTIVATION_THRESHOLD = 0.6
        2. MIN_REQUIRED_SIGNALS = 2
        3. PONDERATION_FACTOR = 1.5 (si 3 signaux)
        4. Time Slicing : global vs last_15_min
        5. Recency Strategy : last_15_min gagne toujours (Money Time)
        6. Contradiction handling → AMBIGUOUS (après recency)
        7. Category priority : psychology > intensity > stability
        8. Raw Data Only (vérifié par normalize_api.py)
    
    Comportements détectables :
        STB_01 : Effondrement Structurel (last_15_min)
        STB_02 : Verrouillage Tactique (global)
        INT_01 : Surge de Pressing (global)
        INT_02 : Déclin Physique (last_15_min)
        PSY_01 : Frustration Active (last_15_min)
        PSY_02 : Résilience (last_15_min)
    """
    
    def __init__(self) -> None:
        """Initialise le BehaviorEngine avec les définitions officielles."""
        self._definitions = BEHAVIOR_DEFINITIONS
        self._threshold = SIGNAL_ACTIVATION_THRESHOLD
        self._min_signals = MIN_REQUIRED_SIGNALS
        self._ponderation = PONDERATION_FACTOR
    
    def compute_behaviors(
        self, 
        signals: Dict[str, float],
        time_slices: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Calcule les comportements à partir des signaux par time slice.
        
        Args:
            signals: Dictionnaire plat des signaux (legacy, non utilisé si time_slices fourni).
            time_slices: Signaux organisés par tranche temporelle.
                         Format: {
                             "global": {"signal_key": value, ...},
                             "last_15_min": {"signal_key": value, ...}
                         }
        
        Returns:
            Dict contenant :
            {
                'behaviors': List[Dict],  # Comportements détectés
                'meta': {
                    'source': str,
                    'version': str,
                    'timestamp': str,
                    'signals_processed': int,
                    'behaviors_detected': int,
                    'recency_model': str
                }
            }
        """
        behaviors: List[Dict[str, Any]] = []
        signals_processed = 0
        
        # =====================================================================
        # PHASE 1 : Détection brute des comportements
        # =====================================================================
        
        for code, spec in self._definitions.items():
            
            required_signals = spec["required_signals"]
            priority_zone = spec["priority_zone"]
            category = spec["category"]
            
            # Extraire la bonne slice (global ou last_15_min)
            slice_data = time_slices.get(priority_zone, {})
            
            # Récupérer les valeurs des signaux dans la slice
            extracted_values: List[float] = []
            for sig_key in required_signals:
                value = slice_data.get(sig_key, 0.0)
                extracted_values.append(float(value))
                signals_processed += 1
            
            # Activation par seuil (SIGNAL_ACTIVATION_THRESHOLD = 0.6)
            active_signals: List[float] = [
                v for v in extracted_values
                if v >= self._threshold
            ]
            
            # Vérifier convergence minimum (MIN_REQUIRED_SIGNALS = 2)
            if len(active_signals) < self._min_signals:
                continue
            
            # Calcul de l'intensité brute (moyenne des signaux actifs)
            intensity = sum(active_signals) / len(active_signals)
            
            # Appliquer pondération si 3 signaux actifs (PONDERATION_FACTOR = 1.5)
            if len(active_signals) >= 3:
                intensity *= self._ponderation
            
            # Construire le comportement détecté
            behavior_result = {
                "code": code,
                "label": spec["name"],
                "label_en": spec.get("name_en", spec["name"]),
                "category": category,
                "intensity": round(float(intensity), 3),
                "time_slice": priority_zone,
                "status": BehaviorStatus.ACTIVE.value,
                "signals_count": len(active_signals),
                "signals_required": len(required_signals),
                "raw_values": extracted_values,
            }
            
            behaviors.append(behavior_result)
        
        # =====================================================================
        # PHASE 2 : Orchestration avancée (ORDRE GEMINI-VALIDATED)
        # =====================================================================
        
        # (1) Fusion Multi-Slice
        behaviors = self._merge_slices(behaviors)
        
        # (2) Recency Strategy (AVANT contradictions - Money Time Priority)
        behaviors = self._apply_recency_strategy(behaviors)
        
        # (3) Résolution des Contradictions → AMBIGU
        behaviors = self._resolve_contradictions(behaviors)
        
        # (4) Tri par Priorité Inter-Catégories
        behaviors = self._sort_by_priority(behaviors)
        
        # =====================================================================
        # PHASE 3 : Construction de la réponse finale
        # =====================================================================
        
        return {
            "behaviors": behaviors,
            "meta": {
                "source": "BehaviorEngine",
                "version": ENGINE_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "signals_processed": signals_processed,
                "behaviors_detected": len([b for b in behaviors if b.get("status") == BehaviorStatus.ACTIVE.value]),
                "time_slices_used": list(time_slices.keys()),
                "recency_model": RECENCY_MODEL,
            }
        }
    
    # =========================================================================
    # PHASE 2 FUNCTIONS — ORCHESTRATION AVANCÉE
    # =========================================================================
    
    def _merge_slices(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fusion Multi-Slice (Global + Last15).
        
        Règles :
            - Si un comportement existe dans global + last_15_min → garder last_15_min
            - Sinon : conserver simplement la version unique
        
        Args:
            behaviors: Liste des comportements bruts détectés.
        
        Returns:
            Liste après fusion (doublons supprimés, last_15_min prioritaire).
        """
        if not behaviors:
            return behaviors
        
        # Grouper par code
        by_code: Dict[str, List[Dict[str, Any]]] = {}
        for b in behaviors:
            code = b["code"]
            if code not in by_code:
                by_code[code] = []
            by_code[code].append(b)
        
        merged: List[Dict[str, Any]] = []
        
        for code, variants in by_code.items():
            if len(variants) == 1:
                # Version unique → conserver
                merged.append(variants[0])
            else:
                # Plusieurs versions → priorité à last_15_min
                last_15_variant = next(
                    (v for v in variants if v["time_slice"] == "last_15_min"),
                    None
                )
                if last_15_variant:
                    merged.append(last_15_variant)
                else:
                    # Pas de last_15_min, garder le premier global
                    merged.append(variants[0])
        
        return merged
    
    def _apply_recency_strategy(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recency Strategy — DOIT ARRIVER AVANT LES CONTRADICTIONS.
        
        Règle Money Time :
            Lorsqu'un conflit existe entre deux comportements d'une même catégorie,
            mais provenant de slices différentes, le comportement issu de 
            last_15_min gagne automatiquement et le comportement global est supprimé.
        
        Cas possibles :
            | Comportement A | Comportement B | Action                           |
            |----------------|----------------|----------------------------------|
            | global         | last_15_min    | Garder last_15_min               |
            | last_15_min    | global         | Garder last_15_min               |
            | global         | global         | Passer à résolution contradictions|
            | last_15_min    | last_15_min    | Passer à résolution contradictions|
        
        Args:
            behaviors: Liste des comportements après merge.
        
        Returns:
            Liste après application du recency strategy.
        """
        if not behaviors:
            return behaviors
        
        # Grouper par catégorie
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for b in behaviors:
            cat = b["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(b)
        
        result: List[Dict[str, Any]] = []
        
        for category, cat_behaviors in by_category.items():
            if len(cat_behaviors) <= 1:
                # Une seule comportement dans cette catégorie → conserver
                result.extend(cat_behaviors)
                continue
            
            # Vérifier si on a un conflit inter-slice
            # (un comportement global et un comportement last_15_min)
            global_behaviors = [b for b in cat_behaviors if b["time_slice"] == "global"]
            last_15_behaviors = [b for b in cat_behaviors if b["time_slice"] == "last_15_min"]
            
            if global_behaviors and last_15_behaviors:
                # Conflit inter-slice détecté → Recency Strategy
                # GARDER UNIQUEMENT last_15_min (Money Time Priority)
                result.extend(last_15_behaviors)
                # Les comportements global sont supprimés (non ajoutés)
            else:
                # Pas de conflit inter-slice → passer à contradiction resolution
                # (même slice pour tous les comportements de cette catégorie)
                result.extend(cat_behaviors)
        
        return result
    
    def _resolve_contradictions(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Résolution des Contradictions → AMBIGU.
        
        Cette étape arrive APRÈS le recency strategy.
        
        Règle :
            Si après recency strategy il reste encore deux comportements 
            contradictoires dans une même catégorie (ex: STB_01 et STB_02),
            alors on supprime les deux et on crée un comportement AMBIGU.
        
        ⚠️ AMBIGU ne doit JAMAIS être généré avant le recency strategy.
        ⚠️ AMBIGU ne doit JAMAIS être généré inter-catégories.
        
        Args:
            behaviors: Liste des comportements après recency strategy.
        
        Returns:
            Liste avec comportements contradictoires remplacés par AMBIGU.
        """
        if not behaviors:
            return behaviors
        
        # Grouper par catégorie
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for b in behaviors:
            cat = b["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(b)
        
        result: List[Dict[str, Any]] = []
        
        for category, cat_behaviors in by_category.items():
            if len(cat_behaviors) <= 1:
                # Une seule comportement → pas de contradiction possible
                result.extend(cat_behaviors)
                continue
            
            # Vérifier les contradictions dans cette catégorie
            codes = [b["code"] for b in cat_behaviors]
            contradiction_found = False
            contradicting_codes: List[str] = []
            
            # Vérifier chaque paire de codes
            for i, code_a in enumerate(codes):
                for code_b in codes[i+1:]:
                    if are_behaviors_contradicting(code_a, code_b):
                        contradiction_found = True
                        if code_a not in contradicting_codes:
                            contradicting_codes.append(code_a)
                        if code_b not in contradicting_codes:
                            contradicting_codes.append(code_b)
            
            if contradiction_found:
                # Créer un comportement AMBIGU
                category_abbrev = category[:3].upper()  # STB, INT, PSY
                ambiguous_behavior = {
                    "code": f"AMBIGU_{category_abbrev}",
                    "label": f"Ambiguïté {category.capitalize()}",
                    "label_en": f"Ambiguous {category.capitalize()}",
                    "category": category,
                    "intensity": None,
                    "time_slice": None,
                    "status": BehaviorStatus.AMBIGUOUS.value,
                    "signals_count": None,
                    "signals_required": None,
                    "raw_values": None,
                    "details": contradicting_codes,
                }
                result.append(ambiguous_behavior)
                
                # Ajouter les comportements non-contradictoires de cette catégorie
                for b in cat_behaviors:
                    if b["code"] not in contradicting_codes:
                        result.append(b)
            else:
                # Pas de contradiction → conserver tous les comportements
                result.extend(cat_behaviors)
        
        return result
    
    def _sort_by_priority(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Tri par Priorité Inter-Catégories.
        
        Ordre de priorité (affichage) :
            1. psychology (0)
            2. intensity (1)
            3. stability (2)
        
        Args:
            behaviors: Liste des comportements après résolution contradictions.
        
        Returns:
            Liste triée par priorité de catégorie.
        """
        if not behaviors:
            return behaviors
        
        return sorted(
            behaviors,
            key=lambda b: CATEGORY_ORDER.get(b.get("category", ""), 99)
        )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def compute_from_flat_signals(
        self,
        signals: Dict[str, float],
        current_minute: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcule les comportements à partir de signaux plats (sans time slicing).
        
        Cette méthode construit automatiquement les time slices si current_minute
        est fourni, sinon utilise tous les signaux comme "global".
        
        Args:
            signals: Dictionnaire plat {signal_key: value}
            current_minute: Minute actuelle du match (optionnel).
                           Si >= 75, les signaux sont aussi dans "last_15_min".
        
        Returns:
            Même format que compute_behaviors().
        """
        # Construire les time slices
        time_slices: Dict[str, Dict[str, float]] = {
            "global": signals.copy()
        }
        
        # Si on est dans les 15 dernières minutes (minute >= 75)
        if current_minute is not None and current_minute >= 75:
            time_slices["last_15_min"] = signals.copy()
        else:
            time_slices["last_15_min"] = {}
        
        return self.compute_behaviors({}, time_slices)
    
    def get_active_behavior_codes(
        self,
        result: Dict[str, Any]
    ) -> List[str]:
        """
        Extrait les codes des comportements actifs d'un résultat.
        
        Args:
            result: Résultat de compute_behaviors().
        
        Returns:
            Liste des codes actifs (ex: ["STB_01", "INT_02"])
        """
        return [
            b["code"]
            for b in result.get("behaviors", [])
            if b.get("status") == BehaviorStatus.ACTIVE.value
        ]
    
    def get_ambiguous_behaviors(
        self,
        result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extrait les comportements ambigus d'un résultat.
        
        Args:
            result: Résultat de compute_behaviors().
        
        Returns:
            Liste des comportements avec status AMBIGUOUS.
        """
        return [
            b for b in result.get("behaviors", [])
            if b.get("status") == BehaviorStatus.AMBIGUOUS.value
        ]
    
    def get_behaviors_by_category(
        self,
        result: Dict[str, Any],
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Filtre les comportements par catégorie.
        
        Args:
            result: Résultat de compute_behaviors().
            category: Catégorie à filtrer ('stability', 'intensity', 'psychology').
        
        Returns:
            Liste des comportements de cette catégorie.
        """
        return [
            b for b in result.get("behaviors", [])
            if b.get("category") == category
        ]
    
    def validate_signal_keys(
        self,
        signals: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Valide que les clés de signaux sont reconnues.
        
        Args:
            signals: Dictionnaire de signaux à valider.
        
        Returns:
            Tuple (is_valid, unknown_keys):
            - is_valid: True si toutes les clés sont reconnues
            - unknown_keys: Liste des clés non reconnues
        """
        unknown = [
            key for key in signals.keys()
            if key not in ALL_REQUIRED_SIGNALS
        ]
        return (len(unknown) == 0, unknown)
    
    @property
    def threshold(self) -> float:
        """Retourne le seuil d'activation."""
        return self._threshold
    
    @property
    def min_signals(self) -> int:
        """Retourne le nombre minimum de signaux requis."""
        return self._min_signals
    
    @property
    def ponderation_factor(self) -> float:
        """Retourne le facteur de pondération."""
        return self._ponderation
    
    @property
    def version(self) -> str:
        """Retourne la version du moteur."""
        return ENGINE_VERSION


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_behavior_engine() -> BehaviorEngine:
    """
    Factory function pour créer une instance de BehaviorEngine.
    
    Returns:
        Instance configurée du BehaviorEngine v2.3.
    """
    return BehaviorEngine()
