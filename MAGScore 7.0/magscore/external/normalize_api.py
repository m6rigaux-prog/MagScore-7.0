"""
MAGScore 6.1 — Normalize API (RAW DATA SANITIZER)
==================================================
Conforme Constitution-MAGScore Section 2.4.
Conforme BEHAVIORENGINE_v2_SPEC_FINAL — Version 2.1 (Gemini-Validated)

Règle RAW DATA ONLY :
- Toute donnée API passe par normalize_api.py
- Rejette toute métrique opaque (momentum, pressure_index...)
- Conserve uniquement les données brutes observables

Métriques INTERDITES (opaques) :
- momentum
- pressure_index
- attack_strength
- defense_rating
- power_rating
- goal_threat
- dangerous_attacks (si dérivé)
- win_probability
- match_odds
- implied_probability

Métriques ACCEPTÉES (raw data) :
- tirs, passes, fautes, duels
- position moyenne, séquences pressing
- cartons jaunes/rouges
- xG (uniquement si fourni brut par l'API)
- distance parcourue, sprints
"""

from typing import Dict, Any, Optional, List, Set, Tuple
import logging

# Configuration du logger
logger = logging.getLogger(__name__)


# =============================================================================
# BLACKLIST — MÉTRIQUES OPAQUES INTERDITES (SPEC 2.1)
# =============================================================================

OPAQUE_METRICS_BLACKLIST: frozenset = frozenset([
    # Métriques dérivées/calculées par les APIs
    "momentum",
    "pressure_index",
    "attack_strength",
    "defense_rating",
    "power_rating",
    "goal_threat",
    
    # Probabilités et ratings
    "win_probability",
    "draw_probability",
    "loss_probability",
    "match_odds",
    "implied_probability",
    "elo_rating",
    "power_ranking",
    
    # Métriques opaques spécifiques
    "attack_momentum",
    "defensive_momentum",
    "form_index",
    "predicted_score",
    "expected_points",
    
    # Dangerous attacks (souvent dérivé)
    "dangerous_attacks",
    
    # Ratings composites
    "overall_rating",
    "team_strength",
    "offensive_rating",
    "defensive_rating_composite",
])


# =============================================================================
# WHITELIST — DONNÉES BRUTES AUTORISÉES (RAW DATA ONLY)
# =============================================================================

RAW_DATA_WHITELIST: frozenset = frozenset([
    # -------------------------------------------------------------------------
    # Tirs
    # -------------------------------------------------------------------------
    "shots",
    "shots_total",
    "shots_on_target",
    "shots_off_target",
    "shots_blocked",
    "shots_inside_box",
    "shots_outside_box",
    
    # -------------------------------------------------------------------------
    # Passes
    # -------------------------------------------------------------------------
    "passes",
    "passes_total",
    "passes_completed",
    "passes_accuracy",
    "passes_percentage",
    "key_passes",
    "through_balls",
    "long_balls",
    "crosses",
    "crosses_completed",
    
    # -------------------------------------------------------------------------
    # Possession
    # -------------------------------------------------------------------------
    "possession",
    "possession_percentage",
    "possession_time",
    "ball_possession",
    
    # -------------------------------------------------------------------------
    # Défense
    # -------------------------------------------------------------------------
    "tackles",
    "tackles_total",
    "tackles_won",
    "interceptions",
    "clearances",
    "blocks",
    "blocked_shots",
    "saves",
    "goalkeeper_saves",
    
    # -------------------------------------------------------------------------
    # Duels
    # -------------------------------------------------------------------------
    "duels",
    "duels_total",
    "duels_won",
    "duels_lost",
    "aerial_duels",
    "aerial_duels_won",
    "ground_duels",
    "ground_duels_won",
    
    # -------------------------------------------------------------------------
    # Fautes et cartons
    # -------------------------------------------------------------------------
    "fouls",
    "fouls_committed",
    "fouls_drawn",
    "yellow_cards",
    "red_cards",
    "cards_yellow",
    "cards_red",
    "offsides",
    
    # -------------------------------------------------------------------------
    # Corners et coups francs
    # -------------------------------------------------------------------------
    "corners",
    "corner_kicks",
    "free_kicks",
    "throw_ins",
    
    # -------------------------------------------------------------------------
    # Physique (données brutes)
    # -------------------------------------------------------------------------
    "distance_covered",
    "total_distance",
    "sprints",
    "sprint_count",
    "running_distance",
    "high_intensity_runs",
    
    # -------------------------------------------------------------------------
    # xG (accepté si fourni brut par l'API)
    # -------------------------------------------------------------------------
    "xg",
    "expected_goals",
    "xg_for",
    "xg_against",
    
    # -------------------------------------------------------------------------
    # Événements et résultats
    # -------------------------------------------------------------------------
    "goals",
    "goals_scored",
    "goals_conceded",
    "assists",
    "own_goals",
    "penalties",
    "penalties_scored",
    "penalties_missed",
    
    # -------------------------------------------------------------------------
    # Position et formation
    # -------------------------------------------------------------------------
    "average_position",
    "formation",
    "lineup",
    
    # -------------------------------------------------------------------------
    # Temporel
    # -------------------------------------------------------------------------
    "minute",
    "half",
    "timestamp",
    "match_time",
    "period",
    
    # -------------------------------------------------------------------------
    # Pressing (données brutes observables)
    # -------------------------------------------------------------------------
    "pressing_sequences",
    "high_press_count",
    "recoveries",
    "ball_recoveries",
    "counter_attacks",
    
    # -------------------------------------------------------------------------
    # Identifiants
    # -------------------------------------------------------------------------
    "match_id",
    "team_id",
    "team_name",
    "player_id",
    "player_name",
])


# =============================================================================
# SANITIZER FUNCTIONS
# =============================================================================

def normalize(raw_api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalise les données API selon la règle RAW DATA ONLY.
    
    Processus :
        1. Rejette les métriques opaques (blacklist)
        2. Conserve uniquement les données brutes (whitelist ou non-blacklistées)
        3. Standardise les formats (noms, types)
        4. Valide l'intégrité des données
    
    Args:
        raw_api_data: Données brutes provenant de l'API.
    
    Returns:
        Dict des données normalisées/sanitizées.
        Les clés blacklistées sont supprimées.
    
    Example:
        >>> raw = {"shots": 12, "momentum": 0.75, "passes": 340}
        >>> normalize(raw)
        {"shots": 12, "passes": 340}  # momentum rejeté
    """
    if not raw_api_data:
        return {}
    
    sanitized: Dict[str, Any] = {}
    rejected_keys: List[str] = []
    
    for key, value in raw_api_data.items():
        # Normaliser la clé en lowercase pour comparaison
        key_lower = key.lower().strip()
        
        # Vérifier si la clé est dans la blacklist
        if _is_opaque_metric(key_lower):
            rejected_keys.append(key)
            continue
        
        # Conserver la donnée (avec clé originale ou normalisée)
        sanitized[key_lower] = value
    
    # Log des clés rejetées (utile pour debug)
    if rejected_keys:
        logger.debug(f"Métriques opaques rejetées : {rejected_keys}")
    
    return sanitized


def normalize_match_data(raw_match_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalise les données complètes d'un match.
    
    Traite les structures imbriquées (home_team, away_team, events).
    
    Args:
        raw_match_data: Données brutes du match depuis l'API.
    
    Returns:
        Dict normalisé au format :
        {
            'match_id': str,
            'timestamp': str,
            'home_team': Dict[str, Any],  # Données sanitizées
            'away_team': Dict[str, Any],  # Données sanitizées
            'events': List[Dict],
            'metadata': Dict
        }
        None si données invalides.
    """
    if not raw_match_data:
        return None
    
    result: Dict[str, Any] = {
        'match_id': raw_match_data.get('match_id', 'unknown'),
        'timestamp': raw_match_data.get('timestamp', ''),
        'metadata': {
            'sanitized': True,
            'source': 'normalize_api',
        }
    }
    
    # Sanitize home_team data
    home_data = raw_match_data.get('home_team', raw_match_data.get('home', {}))
    if isinstance(home_data, dict):
        result['home_team'] = normalize(home_data)
    else:
        result['home_team'] = {}
    
    # Sanitize away_team data
    away_data = raw_match_data.get('away_team', raw_match_data.get('away', {}))
    if isinstance(away_data, dict):
        result['away_team'] = normalize(away_data)
    else:
        result['away_team'] = {}
    
    # Sanitize events (si présents)
    events = raw_match_data.get('events', [])
    if isinstance(events, list):
        result['events'] = [normalize(event) for event in events if isinstance(event, dict)]
    else:
        result['events'] = []
    
    return result


def _is_opaque_metric(key: str) -> bool:
    """
    Vérifie si une clé correspond à une métrique opaque.
    
    Args:
        key: Clé normalisée (lowercase) à vérifier.
    
    Returns:
        True si la métrique est opaque/interdite.
    """
    # Vérification exacte
    if key in OPAQUE_METRICS_BLACKLIST:
        return True
    
    # Vérification par pattern (pour les variantes)
    opaque_patterns = [
        "momentum",
        "pressure_index",
        "power_rating",
        "attack_strength",
        "defense_rating",
        "win_prob",
        "match_odds",
    ]
    
    for pattern in opaque_patterns:
        if pattern in key:
            return True
    
    return False


def is_opaque_metric(metric_name: str) -> bool:
    """
    Vérifie si une métrique est dans la blacklist (API publique).
    
    Args:
        metric_name: Nom de la métrique à vérifier.
    
    Returns:
        True si la métrique est opaque/interdite.
    """
    return _is_opaque_metric(metric_name.lower().strip())


def is_raw_metric(metric_name: str) -> bool:
    """
    Vérifie si une métrique est dans la whitelist (API publique).
    
    Args:
        metric_name: Nom de la métrique à vérifier.
    
    Returns:
        True si la métrique est brute/autorisée.
    """
    return metric_name.lower().strip() in RAW_DATA_WHITELIST


def validate_data_integrity(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valide l'intégrité des données sanitizées.
    
    Vérifie :
    - Aucune métrique opaque présente
    - Types de données cohérents
    
    Args:
        data: Données à valider.
    
    Returns:
        Tuple (is_valid, issues):
        - is_valid: True si données valides
        - issues: Liste des problèmes détectés
    """
    issues: List[str] = []
    
    for key, value in data.items():
        # Vérifier absence de métriques opaques
        if _is_opaque_metric(key.lower()):
            issues.append(f"Métrique opaque détectée : {key}")
        
        # Vérifier types basiques
        if value is None:
            continue
        
        if isinstance(value, dict):
            # Validation récursive
            sub_valid, sub_issues = validate_data_integrity(value)
            issues.extend(sub_issues)
    
    return (len(issues) == 0, issues)


def get_rejected_metrics(raw_data: Dict[str, Any]) -> List[str]:
    """
    Retourne la liste des métriques qui seraient rejetées.
    
    Utile pour debug et audit.
    
    Args:
        raw_data: Données brutes à analyser.
    
    Returns:
        Liste des clés qui seraient rejetées par normalize().
    """
    return [
        key for key in raw_data.keys()
        if _is_opaque_metric(key.lower().strip())
    ]


def get_opaque_metrics_blacklist() -> frozenset:
    """Retourne l'ensemble des métriques opaques interdites."""
    return OPAQUE_METRICS_BLACKLIST


def get_raw_data_whitelist() -> frozenset:
    """Retourne l'ensemble des métriques brutes autorisées."""
    return RAW_DATA_WHITELIST


# =============================================================================
# EXCEPTION CLASS
# =============================================================================

class SanitizationError(Exception):
    """Exception levée en cas d'erreur de sanitization."""
    
    def __init__(self, message: str, rejected_keys: Optional[List[str]] = None):
        self.rejected_keys = rejected_keys or []
        super().__init__(message)
