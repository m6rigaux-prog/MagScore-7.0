"""
MAGScore 7.0 — Pattern Engine v2
=================================
Détection de patterns composites à partir des comportements.

Un Pattern = combinaison de comportements STB/INT/PSY qui forment
un schéma narratif cohérent.

Nouveautés v2 (MAGScore 7.0) :
    - Patterns mixtes Stats + Vision (VIS_*)
    - Support des signaux visuels discrétisés
    - Patterns triples (3 comportements)
    - Priorité TRIPLE > DOUBLE > VISUAL
    - Déduplication avancée
    - Validation d'intégrité des sources

Règles :
    - Patterns basés sur des règles prédéfinies (PATTERN_RULES)
    - Aucune invention de patterns
    - Catégorie toujours "composite"
    - Sources = liste des comportements contributeurs

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any, List, FrozenSet, Optional, Set


# =============================================================================
# VERSION
# =============================================================================

PATTERN_ENGINE_VERSION = "2.0"


# =============================================================================
# PATTERN RULES — TABLE DE RÈGLES
# =============================================================================

# Mapping : frozenset(behavior_codes) -> (pattern_code, label)
# Trié par taille : triples en premier pour priorité
PATTERN_RULES: Dict[FrozenSet[str], tuple] = {
    # ==========================================================================
    # PATTERNS TRIPLES (priorité haute)
    # ==========================================================================
    
    # --- Triple Désintégration ---
    frozenset(["STB_01", "PSY_01", "INT_02"]): (
        "PTN_03", 
        "Désintégration complète"
    ),
    
    # --- Triple Contrôle Total ---
    frozenset(["STB_02", "INT_01", "PSY_02"]): (
        "PTN_07", 
        "Contrôle total"
    ),
    
    # ==========================================================================
    # PATTERNS DOUBLES (priorité normale)
    # ==========================================================================
    
    # --- Patterns de Perte de Contrôle ---
    frozenset(["STB_01", "PSY_01"]): (
        "PTN_01", 
        "Perte de contrôle sous pression"
    ),
    frozenset(["STB_01", "INT_02"]): (
        "PTN_02", 
        "Effondrement par fatigue"
    ),
    
    # --- Patterns de Domination ---
    frozenset(["STB_02", "INT_01"]): (
        "PTN_04", 
        "Domination tactique active"
    ),
    frozenset(["STB_02", "PSY_02"]): (
        "PTN_05", 
        "Résilience organisée"
    ),
    frozenset(["INT_01", "PSY_02"]): (
        "PTN_06", 
        "Pressing mental"
    ),
    
    # --- Patterns Mixtes ---
    frozenset(["INT_01", "PSY_01"]): (
        "PTN_08", 
        "Agressivité désordonnée"
    ),
    frozenset(["INT_02", "PSY_01"]): (
        "PTN_09", 
        "Déclin émotionnel"
    ),
    frozenset(["INT_02", "PSY_02"]): (
        "PTN_10", 
        "Résilience sous fatigue"
    ),
    
    # --- Patterns Structurels Purs ---
    frozenset(["STB_01", "INT_01"]): (
        "PTN_11", 
        "Chaos offensif"
    ),
    frozenset(["STB_02", "INT_02"]): (
        "PTN_12", 
        "Verrouillage défensif tardif"
    ),
}


# =============================================================================
# PATTERN RULES V2 — PATTERNS MIXTES STATS + VISION (MAGScore 7.0)
# =============================================================================

PATTERN_RULES_V2: Dict[FrozenSet[str], tuple] = {
    # ==========================================================================
    # PATTERNS VISUELS + COMPORTEMENTAUX (7.0)
    # ==========================================================================
    
    # --- Défense sous siège visuel ---
    frozenset(["STB_01", "VIS_PRESS_HIGH"]): (
        "PTN_VIS_01", 
        "Défense sous siège visuel"
    ),
    
    # --- Pressing visuel intense ---
    frozenset(["INT_01", "VIS_CLUSTER_HIGH"]): (
        "PTN_VIS_02", 
        "Pressing concentré visuellement"
    ),
    
    # --- Désorganisation visuelle ---
    frozenset(["STB_01", "VIS_CLUSTER_LOW"]): (
        "PTN_VIS_03", 
        "Désorganisation spatiale visible"
    ),
    
    # --- Contrôle visuel total ---
    frozenset(["STB_02", "VIS_PRESS_LOW"]): (
        "PTN_VIS_04", 
        "Contrôle visuel de l'espace"
    ),
    
    # --- Intensité visuelle en déclin ---
    frozenset(["INT_02", "VIS_FLOW_LOW"]): (
        "PTN_VIS_05", 
        "Ralentissement visuel du jeu"
    ),
    
    # --- Triple visuel : Siège complet ---
    frozenset(["STB_01", "INT_02", "VIS_PRESS_HIGH"]): (
        "PTN_VIS_06", 
        "Siège défensif complet"
    ),
}


# =============================================================================
# PATTERN ENGINE
# =============================================================================

class PatternEngine:
    """
    Moteur de détection de patterns composites v2.
    
    Analyse les comportements détectés par BehaviorEngine et identifie
    des patterns narratifs basés sur leurs combinaisons.
    
    Nouveautés v2 (MAGScore 7.0) :
        - Support des signaux visuels (VIS_*)
        - Patterns mixtes Stats + Vision
        - Priorité TRIPLE > DOUBLE > VISUAL
        - Déduplication avancée
    
    Exemple :
        STB_01 + PSY_01 → PTN_01 "Perte de contrôle sous pression"
        STB_01 + PSY_01 + INT_02 → PTN_03 "Désintégration complète"
        STB_01 + VIS_PRESS_HIGH → PTN_VIS_01 "Défense sous siège visuel"
    """
    
    def __init__(self, enable_visual: bool = True) -> None:
        """
        Initialise le Pattern Engine.
        
        Args:
            enable_visual: Active les patterns visuels (v2).
        """
        self._rules = PATTERN_RULES
        self._rules_v2 = PATTERN_RULES_V2 if enable_visual else {}
        self._enable_visual = enable_visual
        self._version = PATTERN_ENGINE_VERSION
    
    @property
    def version(self) -> str:
        """Retourne la version du Pattern Engine."""
        return self._version
    
    def compute_patterns(
        self, 
        behaviors: List[Dict[str, Any]],
        visual_signals: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Détecte les patterns à partir des comportements et signaux visuels.
        
        Args:
            behaviors: Liste des comportements détectés par BehaviorEngine.
                       Chaque comportement doit avoir au minimum:
                       - "code": str (ex: "STB_01")
                       - "status": str (ex: "ACTIVE")
            visual_signals: Liste des codes visuels discrets (v2).
                            Ex: ["VIS_PRESS_HIGH", "VIS_CLUSTER_MED"]
        
        Returns:
            Liste des patterns détectés au format:
            [
                {
                    "pattern_code": str,      # Ex: "PTN_01"
                    "label": str,             # Ex: "Perte de contrôle sous pression"
                    "sources": List[str],     # Ex: ["STB_01", "PSY_01"]
                    "category": "composite"
                },
                ...
            ]
        
        Note v2:
            - Les patterns triples ont priorité sur les doubles
            - Les patterns visuels sont traités après les comportementaux
            - Les codes utilisés par un triple ne peuvent pas former de doubles
        """
        # Extraire les codes des comportements actifs uniquement
        active_codes = self._extract_active_codes(behaviors)
        
        # Ajouter les signaux visuels si disponibles
        all_codes = set(active_codes)
        if visual_signals and self._enable_visual:
            all_codes.update(visual_signals)
        
        if len(all_codes) < 2:
            # Pas assez de signaux pour former un pattern
            return []
        
        patterns: List[Dict[str, Any]] = []
        used_codes: Set[str] = set()
        seen_pattern_codes: Set[str] = set()
        
        # 1. D'abord les patterns comportementaux (priorité)
        sorted_rules = sorted(
            self._rules.items(),
            key=lambda x: (-len(x[0]), x[1][0])  # -taille, puis code pattern
        )
        
        for rule_set, (pattern_code, label) in sorted_rules:
            # Vérifier que tous les codes requis sont présents
            if not rule_set.issubset(active_codes):
                continue
            
            # Éviter les doublons de patterns
            if pattern_code in seen_pattern_codes:
                continue
            
            # Pour les triples : pas de contrainte sur used_codes
            # Pour les doubles : vérifier qu'au moins un code n'est pas déjà utilisé
            if len(rule_set) == 3:
                # Triple : toujours accepté si tous les codes sont présents
                patterns.append({
                    "pattern_code": pattern_code,
                    "label": label,
                    "sources": sorted(list(rule_set)),
                    "category": "composite",
                })
                seen_pattern_codes.add(pattern_code)
                used_codes.update(rule_set)
            else:
                # Double : ne pas créer si tous les codes sont déjà utilisés par un triple
                if rule_set.issubset(used_codes):
                    continue
                
                patterns.append({
                    "pattern_code": pattern_code,
                    "label": label,
                    "sources": sorted(list(rule_set)),
                    "category": "composite",
                })
                seen_pattern_codes.add(pattern_code)
                used_codes.update(rule_set)
        
        # 2. Ensuite les patterns visuels (v2)
        if self._enable_visual and visual_signals:
            sorted_v2_rules = sorted(
                self._rules_v2.items(),
                key=lambda x: (-len(x[0]), x[1][0])
            )
            
            for rule_set, (pattern_code, label) in sorted_v2_rules:
                # Vérifier que tous les codes requis sont présents
                if not rule_set.issubset(all_codes):
                    continue
                
                # Éviter les doublons
                if pattern_code in seen_pattern_codes:
                    continue
                
                patterns.append({
                    "pattern_code": pattern_code,
                    "label": label,
                    "sources": sorted(list(rule_set)),
                    "category": "composite_visual",
                })
                seen_pattern_codes.add(pattern_code)
        
        return patterns
    
    def _extract_active_codes(
        self, 
        behaviors: List[Dict[str, Any]]
    ) -> FrozenSet[str]:
        """
        Extrait les codes des comportements actifs.
        
        Args:
            behaviors: Liste des comportements.
        
        Returns:
            FrozenSet des codes actifs.
        """
        active: Set[str] = set()
        
        for behavior in behaviors:
            status = behavior.get("status", "")
            code = behavior.get("code", "")
            
            # Ignorer les comportements AMBIGUOUS ou invalides
            if status == "ACTIVE" and code and not code.startswith("AMBIGU"):
                active.add(code)
        
        return frozenset(active)
    
    def get_pattern_by_code(self, pattern_code: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un pattern par son code.
        
        Args:
            pattern_code: Code du pattern (ex: "PTN_01" ou "PTN_VIS_01").
        
        Returns:
            Dict avec les infos du pattern, ou None si non trouvé.
        """
        # Chercher dans les patterns comportementaux
        for rule_set, (code, label) in self._rules.items():
            if code == pattern_code:
                return {
                    "pattern_code": code,
                    "label": label,
                    "sources": sorted(list(rule_set)),
                    "category": "composite",
                }
        
        # Chercher dans les patterns visuels (v2)
        if self._enable_visual:
            for rule_set, (code, label) in self._rules_v2.items():
                if code == pattern_code:
                    return {
                        "pattern_code": code,
                        "label": label,
                        "sources": sorted(list(rule_set)),
                        "category": "composite_visual",
                    }
        
        return None
    
    def get_all_pattern_codes(self) -> List[str]:
        """
        Retourne tous les codes de patterns disponibles.
        
        Returns:
            Liste des codes (ex: ["PTN_01", "PTN_02", ..., "PTN_VIS_01"]).
        """
        codes = [code for _, (code, _) in self._rules.items()]
        
        if self._enable_visual:
            codes.extend([code for _, (code, _) in self._rules_v2.items()])
        
        return sorted(codes)
    
    def is_triple_pattern(self, pattern_code: str) -> bool:
        """
        Vérifie si un pattern est un triple (3 sources).
        
        Args:
            pattern_code: Code du pattern.
        
        Returns:
            True si le pattern a 3 sources.
        """
        for rule_set, (code, _) in self._rules.items():
            if code == pattern_code:
                return len(rule_set) == 3
        
        if self._enable_visual:
            for rule_set, (code, _) in self._rules_v2.items():
                if code == pattern_code:
                    return len(rule_set) == 3
        
        return False
    
    def is_visual_pattern(self, pattern_code: str) -> bool:
        """
        Vérifie si un pattern est un pattern visuel (v2).
        
        Args:
            pattern_code: Code du pattern.
        
        Returns:
            True si le pattern est dans PATTERN_RULES_V2.
        """
        if not self._enable_visual:
            return False
        
        return any(
            code == pattern_code 
            for _, (code, _) in self._rules_v2.items()
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_pattern_engine() -> PatternEngine:
    """
    Factory function pour créer un PatternEngine.
    
    Returns:
        Instance de PatternEngine.
    """
    return PatternEngine()
