"""
MAGScore 7.0 — Behavior & Vision Definitions
==============================================
Conforme Constitution-MAGScore Section 2.5.
Conforme BEHAVIORENGINE_v2_SPEC_FINAL — Version 2.1 (Gemini-Validated)
Conforme Plan MAGScore 7.0 v2 — Vision & Memory (Gemini-Validated)

Mapping comportemental officiel :
    STB_01 : Effondrement Structurel
    STB_02 : Verrouillage Tactique
    INT_01 : Surge de Pressing
    INT_02 : Déclin Physique
    PSY_01 : Frustration Active
    PSY_02 : Résilience

Mapping visuel (7.0) :
    VIS_LOW : Signal visuel faible (0.0-0.3)
    VIS_MED : Signal visuel moyen (0.3-0.7)
    VIS_HIGH : Signal visuel fort (0.7-1.0)

Ces définitions sont la source de vérité pour IntelliSense et validation.

IMPORTANT: Les clés 'required_signals' DOIVENT correspondre EXACTEMENT
aux clés produites par les modules de signaux (modules/*.py).
"""

from typing import Dict, Any, List, FrozenSet, Optional
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# CONSTANTES GLOBALES — SPEC 2.1
# =============================================================================

# Seuil d'activation d'un signal (Constitution 2.1)
SIGNAL_ACTIVATION_THRESHOLD: float = 0.6

# Nombre minimum de signaux pour activer un comportement (Constitution 2.1)
MIN_REQUIRED_SIGNALS: int = 2

# Facteur de pondération si 3 signaux convergents (Constitution 2.6)
PONDERATION_FACTOR: float = 1.5

# Tranches temporelles disponibles (Constitution 2.7 - Time Slicing)
TIME_SLICES: List[str] = ["global", "last_15_min"]


# =============================================================================
# MAGSCORE 7.0 — DATACLASSES
# =============================================================================

@dataclass
class Frame:
    """
    Représente un échantillon de frame vidéo analysé (MAGScore 7.0).
    
    Attributes:
        timestamp: Horodatage de la frame.
        metrics: Métriques brutes extraites (ex: density_def, optical_flow_avg).
    """
    timestamp: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class VisualSignal:
    """
    Représente un signal visuel extrait et discrétisé (MAGScore 7.0).
    
    Attributes:
        raw: Signaux bruts avec valeurs float (0.0-1.0).
        discrete: Codes discrets pour PatternEngine (ex: ["VIS_CLUSTER_MED"]).
    """
    raw: Dict[str, float] = field(default_factory=dict)
    discrete: List[str] = field(default_factory=list)


@dataclass
class Episode:
    """
    Représente un épisode de mémoire pour une équipe (MAGScore 7.0).
    
    RÈGLE DE SÉCURITÉ ABSOLUE:
        - INTERDIT de stocker: score, result, winner, odds, bet
        - Uniquement la structure comportementale
    
    Attributes:
        match_id: Identifiant unique du match.
        timestamp: Horodatage de l'épisode.
        opposing_style: Style de jeu adverse (ex: "HIGH_PRESS_POSSESSION").
        behaviors: Codes comportements détectés (ex: ["STB_02", "INT_01"]).
        patterns: Codes patterns détectés (ex: ["PTN_04", "PTN_05"]).
        flow_phases: Labels des phases du flow (ex: ["Contrôle tactique"]).
    """
    match_id: str
    timestamp: datetime
    opposing_style: str = ""
    behaviors: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    flow_phases: List[str] = field(default_factory=list)
    
    # NOTE: score, result, winner, odds sont INTERDITS


@dataclass
class SemanticMemory:
    """
    Mémoire sémantique agrégée pour une équipe (MAGScore 7.0).
    
    Attributes:
        pattern_frequency: Fréquence de chaque pattern (ex: {"PTN_04": 0.52}).
        last_updated: Date de dernière mise à jour.
    """
    pattern_frequency: Dict[str, float] = field(default_factory=dict)
    last_updated: Optional[datetime] = None


@dataclass
class TeamMemory:
    """
    Mémoire complète d'une équipe (MAGScore 7.0).
    
    Attributes:
        team_id: Identifiant unique de l'équipe.
        episodes: Liste des épisodes (FIFO, max 10).
        semantic: Mémoire sémantique agrégée.
    """
    team_id: str
    episodes: List[Episode] = field(default_factory=list)
    semantic: SemanticMemory = field(default_factory=SemanticMemory)


# =============================================================================
# MAGSCORE 7.0 — VISUAL SIGNALS MAPPING
# =============================================================================

# Seuils de discrétisation des signaux visuels
VISUAL_THRESHOLDS = {
    "LOW": (0.0, 0.3),
    "MED": (0.3, 0.7),
    "HIGH": (0.7, 1.0),
}

# Codes de signaux visuels discrets
VISUAL_SIGNAL_CODES = {
    "VIS_LOW": "Signal visuel faible",
    "VIS_MED": "Signal visuel moyen",
    "VIS_HIGH": "Signal visuel fort",
    "VIS_CLUSTER_LOW": "Concentration faible de joueurs",
    "VIS_CLUSTER_MED": "Concentration moyenne de joueurs",
    "VIS_CLUSTER_HIGH": "Concentration élevée de joueurs",
    "VIS_PRESS_LOW": "Pressing visuel faible",
    "VIS_PRESS_MED": "Pressing visuel moyen",
    "VIS_PRESS_HIGH": "Pressing visuel fort",
}

# Signaux visuels requis pour les patterns mixtes (v2)
VISUAL_REQUIRED_SIGNALS: FrozenSet[str] = frozenset([
    "VIS_CLUSTER_LOW",
    "VIS_CLUSTER_MED",
    "VIS_CLUSTER_HIGH",
    "VIS_PRESS_LOW",
    "VIS_PRESS_MED",
    "VIS_PRESS_HIGH",
])


# =============================================================================
# MAGSCORE 7.0 — MEMORY SECURITY
# =============================================================================

# Clés STRICTEMENT INTERDITES dans les épisodes de mémoire
FORBIDDEN_MEMORY_KEYS: FrozenSet[str] = frozenset([
    "score",
    "result",
    "winner",
    "loser",
    "odds",
    "bet",
    "betting",
    "cote",
    "pari",
    "prono",
    "prediction",
    "final_score",
    "match_result",
])


# =============================================================================
# BEHAVIOR DEFINITIONS — SOURCE DE VÉRITÉ (SPEC 2.1)
# =============================================================================

BEHAVIOR_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    
    # -------------------------------------------------------------------------
    # STABILITY BEHAVIORS (STB)
    # -------------------------------------------------------------------------
    
    "STB_01": {
        "code": "STB_01",
        "name": "Effondrement Structurel",
        "name_en": "Structural Collapse",
        "category": "stability",
        "description": (
            "Perte de cohésion défensive observable. "
            "L'équipe ne maintient plus sa structure tactique de base."
        ),
        "required_signals": ["low_block_drop", "xg_against_spike"],
        "priority_zone": "last_15_min",
        "contradicts": ["STB_02"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
    
    "STB_02": {
        "code": "STB_02",
        "name": "Verrouillage Tactique",
        "name_en": "Tactical Lock",
        "category": "stability",
        "description": (
            "Structure défensive maintenue avec discipline. "
            "L'équipe absorbe la pression sans rupture."
        ),
        "required_signals": ["high_compactness", "successful_low_block"],
        "priority_zone": "global",
        "contradicts": ["STB_01"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
    
    # -------------------------------------------------------------------------
    # INTENSITY BEHAVIORS (INT)
    # -------------------------------------------------------------------------
    
    "INT_01": {
        "code": "INT_01",
        "name": "Surge de Pressing",
        "name_en": "Pressing Surge",
        "category": "intensity",
        "description": (
            "Augmentation notable de l'intensité du pressing. "
            "L'équipe récupère le ballon plus haut sur le terrain."
        ),
        "required_signals": ["pressing_wave", "high_duel_pressure"],
        "priority_zone": "global",
        "contradicts": ["INT_02"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
    
    "INT_02": {
        "code": "INT_02",
        "name": "Déclin Physique",
        "name_en": "Physical Decline",
        "category": "intensity",
        "description": (
            "Baisse observable de l'intensité physique. "
            "Les courses diminuent, les duels sont évités."
        ),
        "required_signals": ["running_distance_drop", "duel_loss_spike"],
        "priority_zone": "last_15_min",
        "contradicts": ["INT_01"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
    
    # -------------------------------------------------------------------------
    # PSYCHOLOGY BEHAVIORS (PSY)
    # -------------------------------------------------------------------------
    
    "PSY_01": {
        "code": "PSY_01",
        "name": "Frustration Active",
        "name_en": "Active Frustration",
        "category": "psychology",
        "description": (
            "Signes visibles de frustration collective. "
            "Fautes tactiques, protestations, perte de concentration."
        ),
        "required_signals": ["fouls_spike", "protest_pattern"],
        "priority_zone": "last_15_min",
        "contradicts": ["PSY_02"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
    
    "PSY_02": {
        "code": "PSY_02",
        "name": "Résilience",
        "name_en": "Resilience",
        "category": "psychology",
        "description": (
            "Capacité à maintenir le niveau malgré l'adversité. "
            "L'équipe reste concentrée après un événement négatif."
        ),
        "required_signals": ["high_defensive_recovery", "late_pressing_effort"],
        "priority_zone": "last_15_min",
        "contradicts": ["PSY_01"],
        "min_convergence": MIN_REQUIRED_SIGNALS,
    },
}


# =============================================================================
# SIGNAL KEYS REGISTRY — MAPPING OBLIGATOIRE
# =============================================================================

# Tous les signaux requis par les comportements
# Les modules DOIVENT produire ces clés exactes
ALL_REQUIRED_SIGNALS: FrozenSet[str] = frozenset([
    # STB_01
    "low_block_drop",
    "xg_against_spike",
    # STB_02
    "high_compactness",
    "successful_low_block",
    # INT_01
    "pressing_wave",
    "high_duel_pressure",
    # INT_02
    "running_distance_drop",
    "duel_loss_spike",
    # PSY_01
    "fouls_spike",
    "protest_pattern",
    # PSY_02
    "high_defensive_recovery",
    "late_pressing_effort",
])

# Mapping signal -> module source attendu
SIGNAL_TO_MODULE: Dict[str, str] = {
    # Stability signals
    "low_block_drop": "stability",
    "xg_against_spike": "stability",
    "high_compactness": "stability",
    "successful_low_block": "stability",
    # Intensity signals
    "pressing_wave": "intensity",
    "high_duel_pressure": "intensity",
    "running_distance_drop": "intensity",
    "duel_loss_spike": "intensity",
    # Psychology signals
    "fouls_spike": "psychology",
    "protest_pattern": "psychology",
    "high_defensive_recovery": "psychology",
    "late_pressing_effort": "psychology",
}


# =============================================================================
# CONTRADICTION MAP — PAIRES INCOMPATIBLES
# =============================================================================

CONTRADICTION_PAIRS: List[tuple] = [
    ("STB_01", "STB_02"),  # Effondrement vs Verrouillage
    ("INT_01", "INT_02"),  # Surge vs Déclin
    ("PSY_01", "PSY_02"),  # Frustration vs Résilience
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_behavior(code: str) -> Dict[str, Any]:
    """
    Récupère la définition d'un comportement par son code.
    
    Args:
        code: Code du comportement (ex: "STB_01")
    
    Returns:
        Définition complète du comportement.
    
    Raises:
        KeyError: Si le code n'existe pas.
    """
    if code not in BEHAVIOR_DEFINITIONS:
        raise KeyError(f"Comportement inconnu : {code}")
    return BEHAVIOR_DEFINITIONS[code]


def get_behaviors_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Récupère tous les comportements d'une catégorie.
    
    Args:
        category: Catégorie ('stability', 'intensity', 'psychology')
    
    Returns:
        Liste des comportements de cette catégorie.
    """
    return [
        behavior 
        for behavior in BEHAVIOR_DEFINITIONS.values() 
        if behavior["category"] == category
    ]


def get_behaviors_by_priority_zone(zone: str) -> List[Dict[str, Any]]:
    """
    Récupère tous les comportements d'une zone de priorité.
    
    Args:
        zone: Zone ('global' ou 'last_15_min')
    
    Returns:
        Liste des comportements de cette zone.
    """
    return [
        behavior
        for behavior in BEHAVIOR_DEFINITIONS.values()
        if behavior["priority_zone"] == zone
    ]


def get_contradicting_behaviors(code: str) -> List[str]:
    """
    Récupère les codes des comportements en contradiction.
    
    Args:
        code: Code du comportement de référence.
    
    Returns:
        Liste des codes en contradiction.
    """
    behavior = get_behavior(code)
    return behavior.get("contradicts", [])


def are_behaviors_contradicting(code_a: str, code_b: str) -> bool:
    """
    Vérifie si deux comportements sont en contradiction.
    
    Args:
        code_a: Premier code comportement.
        code_b: Second code comportement.
    
    Returns:
        True si les comportements sont incompatibles.
    """
    for pair in CONTRADICTION_PAIRS:
        if code_a in pair and code_b in pair:
            return True
    return False


def validate_behavior_code(code: str) -> bool:
    """
    Vérifie si un code de comportement est valide.
    
    Args:
        code: Code à vérifier.
    
    Returns:
        True si le code est valide.
    """
    return code in BEHAVIOR_DEFINITIONS


def validate_signal_key(key: str) -> bool:
    """
    Vérifie si une clé de signal est reconnue.
    
    Args:
        key: Clé de signal à vérifier.
    
    Returns:
        True si la clé est dans le registre officiel.
    """
    return key in ALL_REQUIRED_SIGNALS


def get_required_signals_for_behavior(code: str) -> List[str]:
    """
    Récupère les signaux requis pour un comportement.
    
    Args:
        code: Code du comportement.
    
    Returns:
        Liste des clés de signaux requis.
    """
    behavior = get_behavior(code)
    return behavior["required_signals"]


def discretize_visual_signal(value: float, signal_type: str = "VIS") -> str:
    """
    Convertit une valeur float en code discret pour le PatternEngine (7.0).
    
    Args:
        value: Valeur entre 0.0 et 1.0.
        signal_type: Préfixe du type de signal (ex: "VIS_CLUSTER", "VIS_PRESS").
    
    Returns:
        Code discret (ex: "VIS_CLUSTER_HIGH").
    """
    if value < 0.0:
        value = 0.0
    elif value > 1.0:
        value = 1.0
    
    if value <= VISUAL_THRESHOLDS["LOW"][1]:
        return f"{signal_type}_LOW"
    elif value <= VISUAL_THRESHOLDS["MED"][1]:
        return f"{signal_type}_MED"
    else:
        return f"{signal_type}_HIGH"


def is_forbidden_memory_key(key: str) -> bool:
    """
    Vérifie si une clé est interdite dans la mémoire (7.0 - SÉCURITÉ).
    
    Args:
        key: Clé à vérifier.
    
    Returns:
        True si la clé est interdite.
    """
    key_lower = key.lower()
    return key_lower in FORBIDDEN_MEMORY_KEYS


# =============================================================================
# CATEGORY & CODE CONSTANTS
# =============================================================================

CATEGORIES: List[str] = ["stability", "intensity", "psychology"]

BEHAVIOR_CODES: List[str] = list(BEHAVIOR_DEFINITIONS.keys())

PRIORITY_ZONES: List[str] = ["global", "last_15_min"]
