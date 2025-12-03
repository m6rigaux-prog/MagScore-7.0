"""
MAGScore 6.3 — Match Flow Reconstruction v1.1
==============================================
Reconstruction de la chronologie du match basée sur time_slice.

Fonctionnement :
    - global → phase de fond (début/milieu de match)
    - last_15_min → phase finale (Money Time)

Nouveautés v1.1 :
    - Détection de rupture (STB_01 + INT_02)
    - Labels de phases améliorés
    - Mapping comportement → phase plus précis

Règles :
    - Minimum 2 phases
    - Maximum 5 phases
    - Basé uniquement sur les comportements actifs
    - Chronologie du fond vers le final

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any, List, Set


# =============================================================================
# VERSION
# =============================================================================

MATCH_FLOW_VERSION = "1.1"


# =============================================================================
# PHASE MAPPING — LABELS PAR COMPORTEMENT ET TIME_SLICE
# =============================================================================

# Format: (behavior_code, time_slice) -> label de phase
PHASE_LABELS: Dict[tuple, str] = {
    # --- STABILITY ---
    ("STB_01", "global"): "Fragilité structurelle",
    ("STB_01", "last_15_min"): "Effondrement défensif final",
    ("STB_02", "global"): "Contrôle tactique",
    ("STB_02", "last_15_min"): "Verrouillage tardif",
    
    # --- INTENSITY ---
    ("INT_01", "global"): "Intensité active",
    ("INT_01", "last_15_min"): "Pressing final",
    ("INT_02", "global"): "Fatigue précoce",
    ("INT_02", "last_15_min"): "Déclin physique final",
    
    # --- PSYCHOLOGY ---
    ("PSY_01", "global"): "Tension émotionnelle",
    ("PSY_01", "last_15_min"): "Frustration finale",
    ("PSY_02", "global"): "Résilience mentale",
    ("PSY_02", "last_15_min"): "Résistance finale",
}

# Labels par défaut si comportement non mappé
DEFAULT_GLOBAL_LABEL = "Phase de stabilisation"
DEFAULT_LAST15_LABEL = "Phase finale"

# Limites
MIN_PHASES = 2
MAX_PHASES = 5

# Combinaison de rupture (v1.1)
RUPTURE_CODES = {"STB_01", "INT_02"}
RUPTURE_LABEL = "Rupture structurelle"


# =============================================================================
# MATCH FLOW RECONSTRUCTOR
# =============================================================================

class MatchFlowReconstructor:
    """
    Reconstruit la chronologie du match à partir des comportements.
    
    Utilise l'attribut time_slice pour déduire la chronologie :
        - global → phase de fond
        - last_15_min → phase finale
    
    Nouveautés v1.1 :
        - Détection de rupture (STB_01 + INT_02 en last_15_min)
        - Labels de phases plus précis
    
    Exemple de sortie :
        [
            "Phase 1 : Contrôle tactique",
            "Phase 2 : Rupture structurelle"
        ]
    """
    
    def __init__(self) -> None:
        """Initialise le Match Flow Reconstructor."""
        self._phase_labels = PHASE_LABELS
        self._version = MATCH_FLOW_VERSION
    
    @property
    def version(self) -> str:
        """Retourne la version du Match Flow Reconstructor."""
        return self._version
    
    def reconstruct(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Reconstruit la chronologie du match.
        
        Args:
            behaviors: Liste des comportements détectés par BehaviorEngine.
                       Chaque comportement doit avoir :
                       - "code": str (ex: "STB_01")
                       - "status": str (ex: "ACTIVE")
                       - "time_slice": str ("global" ou "last_15_min")
        
        Returns:
            Liste des phases au format :
            ["Phase 1 : Label", "Phase 2 : Label", ...]
            
            Minimum 2 phases, maximum 5 phases.
        """
        # Séparer les comportements par time_slice
        global_behaviors: List[Dict[str, Any]] = []
        last15_behaviors: List[Dict[str, Any]] = []
        last15_codes: Set[str] = set()
        
        for behavior in behaviors:
            if behavior.get("status") != "ACTIVE":
                continue
            
            code = behavior.get("code", "")
            if code.startswith("AMBIGU"):
                continue
            
            time_slice = behavior.get("time_slice", "global")
            
            if time_slice == "last_15_min":
                last15_behaviors.append(behavior)
                last15_codes.add(code)
            else:
                global_behaviors.append(behavior)
        
        # Construire les phases
        phases: List[str] = []
        
        # Phase(s) de fond (global)
        global_phases = self._build_phases(global_behaviors, "global")
        phases.extend(global_phases)
        
        # Vérifier la rupture (v1.1)
        has_rupture = RUPTURE_CODES.issubset(last15_codes)
        
        # Phase(s) finale(s) (last_15_min)
        if has_rupture:
            # Insérer la phase de rupture en premier des finales
            final_phases = self._build_phases_with_rupture(last15_behaviors)
        else:
            final_phases = self._build_phases(last15_behaviors, "last_15_min")
        
        phases.extend(final_phases)
        
        # Appliquer les limites
        phases = self._apply_limits(phases)
        
        # Numéroter les phases
        numbered_phases = [
            f"Phase {i+1} : {phase}" 
            for i, phase in enumerate(phases)
        ]
        
        return numbered_phases
    
    def _build_phases(
        self, 
        behaviors: List[Dict[str, Any]],
        time_slice: str
    ) -> List[str]:
        """
        Construit les labels de phases pour un time_slice.
        
        Args:
            behaviors: Comportements de ce time_slice.
            time_slice: "global" ou "last_15_min".
        
        Returns:
            Liste des labels de phases.
        """
        if not behaviors:
            return []
        
        phases: List[str] = []
        seen_labels: Set[str] = set()
        
        # Ordre de priorité par catégorie
        category_order = {"stability": 0, "intensity": 1, "psychology": 2}
        
        # Trier par catégorie
        sorted_behaviors = sorted(
            behaviors,
            key=lambda b: category_order.get(b.get("category", ""), 99)
        )
        
        for behavior in sorted_behaviors:
            code = behavior.get("code", "")
            
            # Chercher le label correspondant
            key = (code, time_slice)
            label = self._phase_labels.get(key)
            
            if not label:
                # Label par défaut
                if time_slice == "last_15_min":
                    label = DEFAULT_LAST15_LABEL
                else:
                    label = DEFAULT_GLOBAL_LABEL
            
            # Éviter les doublons
            if label not in seen_labels:
                phases.append(label)
                seen_labels.add(label)
        
        return phases
    
    def _build_phases_with_rupture(
        self,
        last15_behaviors: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Construit les phases finales avec détection de rupture (v1.1).
        
        Si STB_01 + INT_02 sont présents en last_15_min, ajoute une phase
        "Rupture structurelle" qui remplace les phases individuelles.
        
        Args:
            last15_behaviors: Comportements de la phase finale.
        
        Returns:
            Liste des labels de phases finales.
        """
        phases: List[str] = []
        seen_labels: Set[str] = set()
        rupture_codes_found: Set[str] = set()
        
        # Ordre de priorité par catégorie
        category_order = {"stability": 0, "intensity": 1, "psychology": 2}
        
        # Trier par catégorie
        sorted_behaviors = sorted(
            last15_behaviors,
            key=lambda b: category_order.get(b.get("category", ""), 99)
        )
        
        # D'abord, identifier les codes de rupture
        for behavior in sorted_behaviors:
            code = behavior.get("code", "")
            if code in RUPTURE_CODES:
                rupture_codes_found.add(code)
        
        # Si rupture complète, ajouter la phase de rupture
        if rupture_codes_found == RUPTURE_CODES:
            phases.append(RUPTURE_LABEL)
            seen_labels.add(RUPTURE_LABEL)
        
        # Ajouter les autres phases (hors rupture)
        for behavior in sorted_behaviors:
            code = behavior.get("code", "")
            
            # Si c'est un code de rupture et qu'on a déjà la phase rupture, skip
            if code in RUPTURE_CODES and RUPTURE_LABEL in seen_labels:
                continue
            
            key = (code, "last_15_min")
            label = self._phase_labels.get(key, DEFAULT_LAST15_LABEL)
            
            if label not in seen_labels:
                phases.append(label)
                seen_labels.add(label)
        
        return phases
    
    def _apply_limits(self, phases: List[str]) -> List[str]:
        """
        Applique les limites min/max aux phases.
        
        Args:
            phases: Liste brute des phases.
        
        Returns:
            Liste avec limites appliquées.
        """
        if not phases:
            # Minimum 2 phases par défaut
            return [
                DEFAULT_GLOBAL_LABEL,
                DEFAULT_LAST15_LABEL
            ]
        
        if len(phases) < MIN_PHASES:
            # Compléter pour atteindre le minimum
            while len(phases) < MIN_PHASES:
                if DEFAULT_LAST15_LABEL not in phases:
                    phases.append(DEFAULT_LAST15_LABEL)
                else:
                    phases.insert(0, DEFAULT_GLOBAL_LABEL)
        
        if len(phases) > MAX_PHASES:
            # Tronquer au maximum
            phases = phases[:MAX_PHASES]
        
        return phases
    
    def get_phase_label(self, code: str, time_slice: str) -> str:
        """
        Récupère le label de phase pour un comportement.
        
        Args:
            code: Code du comportement (ex: "STB_01").
            time_slice: Time slice ("global" ou "last_15_min").
        
        Returns:
            Label de phase.
        """
        key = (code, time_slice)
        label = self._phase_labels.get(key)
        
        if not label:
            if time_slice == "last_15_min":
                return DEFAULT_LAST15_LABEL
            return DEFAULT_GLOBAL_LABEL
        
        return label
    
    def detect_rupture(self, behaviors: List[Dict[str, Any]]) -> bool:
        """
        Détecte si une rupture est présente (v1.1).
        
        Une rupture est détectée quand STB_01 + INT_02 sont actifs
        en phase last_15_min.
        
        Args:
            behaviors: Liste des comportements.
        
        Returns:
            True si rupture détectée.
        """
        last15_codes: Set[str] = set()
        
        for behavior in behaviors:
            if behavior.get("status") != "ACTIVE":
                continue
            
            code = behavior.get("code", "")
            time_slice = behavior.get("time_slice", "global")
            
            if time_slice == "last_15_min":
                last15_codes.add(code)
        
        return RUPTURE_CODES.issubset(last15_codes)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_match_flow_reconstructor() -> MatchFlowReconstructor:
    """
    Factory function pour créer un MatchFlowReconstructor.
    
    Returns:
        Instance de MatchFlowReconstructor.
    """
    return MatchFlowReconstructor()
