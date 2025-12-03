"""
MAGScore 6.1 — Psychology Module v2
====================================
Extraction des signaux psychologiques et comportementaux.

Comportements associés :
    PSY_01 : Frustration Active (last_15_min)
        - fouls_spike
        - protest_pattern
    PSY_02 : Résilience (last_15_min)
        - high_defensive_recovery
        - late_pressing_effort

Ces signaux DOIVENT correspondre EXACTEMENT aux clés de BEHAVIOR_DEFINITIONS.
"""

from typing import Dict, Any


class PsychologyModule:
    """
    Module d'extraction des signaux psychologiques.
    
    Analyse les patterns de frustration, résilience et concentration
    à partir des données normalisées (RAW DATA ONLY).
    
    Méthodes obligatoires :
        - compute_global(normalized_data) -> Dict[str, float]
        - compute_last_15(normalized_data) -> Dict[str, float]
    """
    
    def __init__(self) -> None:
        """Initialise le module psychologique."""
        self._default_value = 0.0
    
    def compute_global(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux psychologiques sur la période globale (0-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - fouls_spike: float (0.0-1.0)
            - protest_pattern: float (0.0-1.0)
            - high_defensive_recovery: float (0.0-1.0)
            - late_pressing_effort: float (0.0-1.0)
        """
        stats = normalized_data.get("stats", normalized_data)
        
        # --- FOULS_SPIKE ---
        # Basé sur le nombre de fautes commises
        fouls = float(stats.get("fouls", stats.get("fouls_committed", 0)))
        yellow_cards = float(stats.get("yellow_cards", 0))
        red_cards = float(stats.get("red_cards", 0))
        
        # Pondérer les cartons dans le calcul de frustration
        foul_score = fouls + (yellow_cards * 3) + (red_cards * 6)
        fouls_spike_raw = foul_score / 20  # ~20 = frustration élevée
        fouls_spike = min(1.0, max(0.0, fouls_spike_raw))
        
        # --- PROTEST_PATTERN ---
        # Indicateur composite basé sur cartons et fautes tactiques
        # Plus de jaunes = plus de protestations probables
        protest_score = (yellow_cards * 2) + (red_cards * 3)
        if fouls > 10:
            protest_score += (fouls - 10) * 0.3
        protest_pattern_raw = protest_score / 6
        protest_pattern = min(1.0, max(0.0, protest_pattern_raw))
        
        # --- HIGH_DEFENSIVE_RECOVERY ---
        # Basé sur les interceptions, tacles et récupérations
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        clearances = float(stats.get("clearances", 0))
        
        recovery_actions = interceptions + tackles + clearances
        high_defensive_recovery_raw = recovery_actions / 40
        high_defensive_recovery = min(1.0, max(0.0, high_defensive_recovery_raw))
        
        # --- LATE_PRESSING_EFFORT ---
        # En global, mesure la capacité à maintenir le pressing
        # Basé sur les récupérations et duels
        duels_won = float(stats.get("duels_won", 0))
        ball_recoveries = float(stats.get("ball_recoveries", 
                                          stats.get("recoveries", interceptions)))
        
        pressing_effort = (duels_won + ball_recoveries) / 30
        late_pressing_effort = min(1.0, max(0.0, pressing_effort))
        
        return {
            "fouls_spike": round(fouls_spike, 3),
            "protest_pattern": round(protest_pattern, 3),
            "high_defensive_recovery": round(high_defensive_recovery, 3),
            "late_pressing_effort": round(late_pressing_effort, 3),
        }
    
    def compute_last_15(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux psychologiques sur les 15 dernières minutes (75-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - fouls_spike: float (0.0-1.0)
            - protest_pattern: float (0.0-1.0)
            - high_defensive_recovery: float (0.0-1.0)
            - late_pressing_effort: float (0.0-1.0)
        """
        # Chercher les données last_15_min si disponibles
        last_15_data = normalized_data.get("last_15_min", normalized_data.get("money_time", {}))
        global_stats = normalized_data.get("stats", normalized_data)
        
        if last_15_data:
            stats = last_15_data
        else:
            stats = global_stats
        
        # --- FOULS_SPIKE ---
        # Plus sensible en fin de match (seuils ajustés)
        fouls = float(stats.get("fouls", stats.get("fouls_committed", 0)))
        yellow_cards = float(stats.get("yellow_cards", 0))
        red_cards = float(stats.get("red_cards", 0))
        
        # En fin de match, moins de fautes nécessaires pour spike
        foul_score = fouls + (yellow_cards * 4) + (red_cards * 8)
        fouls_spike_raw = foul_score / 8  # Seuil réduit pour 15 min
        fouls_spike = min(1.0, max(0.0, fouls_spike_raw))
        
        # --- PROTEST_PATTERN ---
        # Accentué en fin de match
        protest_score = (yellow_cards * 3) + (red_cards * 4)
        if fouls > 3:
            protest_score += (fouls - 3) * 0.5
        protest_pattern_raw = protest_score / 4
        protest_pattern = min(1.0, max(0.0, protest_pattern_raw))
        
        # --- HIGH_DEFENSIVE_RECOVERY ---
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        clearances = float(stats.get("clearances", 0))
        blocks = float(stats.get("blocks", stats.get("shots_blocked", 0)))
        
        # En fin de match, moins d'actions nécessaires pour démontrer résilience
        recovery_actions = interceptions + tackles + clearances + blocks
        high_defensive_recovery_raw = recovery_actions / 12
        high_defensive_recovery = min(1.0, max(0.0, high_defensive_recovery_raw))
        
        # --- LATE_PRESSING_EFFORT ---
        # Spécifiquement important en fin de match
        duels_won = float(stats.get("duels_won", 0))
        ball_recoveries = float(stats.get("ball_recoveries", 
                                          stats.get("recoveries", interceptions)))
        sprints = float(stats.get("sprints", stats.get("sprint_count", 0)))
        
        # Combinaison de duels, récupérations et sprints
        pressing_effort = (duels_won + ball_recoveries + sprints) / 15
        late_pressing_effort = min(1.0, max(0.0, pressing_effort))
        
        return {
            "fouls_spike": round(fouls_spike, 3),
            "protest_pattern": round(protest_pattern, 3),
            "high_defensive_recovery": round(high_defensive_recovery, 3),
            "late_pressing_effort": round(late_pressing_effort, 3),
        }
    
    # =========================================================================
    # LEGACY METHODS (rétrocompatibilité)
    # =========================================================================
    
    def extract_signals(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Méthode legacy pour rétrocompatibilité.
        Retourne les signaux globaux.
        """
        return self.compute_global(normalized_data)
