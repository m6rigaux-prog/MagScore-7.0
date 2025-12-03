"""
MAGScore 6.1 — Intensity Module v2
===================================
Extraction des signaux d'intensité physique et de pressing.

Comportements associés :
    INT_01 : Surge de Pressing (global)
        - pressing_wave
        - high_duel_pressure
    INT_02 : Déclin Physique (last_15_min)
        - running_distance_drop
        - duel_loss_spike

Ces signaux DOIVENT correspondre EXACTEMENT aux clés de BEHAVIOR_DEFINITIONS.
"""

from typing import Dict, Any


class IntensityModule:
    """
    Module d'extraction des signaux d'intensité.
    
    Analyse l'intensité physique, le pressing et les duels
    à partir des données normalisées (RAW DATA ONLY).
    
    Méthodes obligatoires :
        - compute_global(normalized_data) -> Dict[str, float]
        - compute_last_15(normalized_data) -> Dict[str, float]
    """
    
    def __init__(self) -> None:
        """Initialise le module d'intensité."""
        self._default_value = 0.0
    
    def compute_global(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux d'intensité sur la période globale (0-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - pressing_wave: float (0.0-1.0)
            - high_duel_pressure: float (0.0-1.0)
            - running_distance_drop: float (0.0-1.0)
            - duel_loss_spike: float (0.0-1.0)
        """
        stats = normalized_data.get("stats", normalized_data)
        
        # --- PRESSING_WAVE ---
        # Basé sur les récupérations hautes et les passes interceptées
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        ball_recoveries = float(stats.get("ball_recoveries", 
                                          stats.get("recoveries", interceptions + tackles)))
        
        # Plus de récupérations = pressing efficace
        pressing_actions = ball_recoveries + interceptions
        pressing_wave_raw = pressing_actions / 25  # ~25 récupérations = pressing intense
        pressing_wave = min(1.0, max(0.0, pressing_wave_raw))
        
        # --- HIGH_DUEL_PRESSURE ---
        # Basé sur le ratio de duels gagnés
        duels_total = float(stats.get("duels", stats.get("duels_total", 50)))
        duels_won = float(stats.get("duels_won", duels_total * 0.5))
        
        if duels_total > 0:
            duel_win_ratio = duels_won / duels_total
        else:
            duel_win_ratio = 0.5
        
        # Ajuster pour que > 55% de duels gagnés = haute pression
        high_duel_pressure = min(1.0, max(0.0, (duel_win_ratio - 0.3) / 0.4))
        
        # --- RUNNING_DISTANCE_DROP ---
        # En global, pas de "drop" détectable (besoin de comparaison temporelle)
        # On initialise bas et on laisse last_15 gérer
        distance = float(stats.get("distance_covered", stats.get("running_distance", 0)))
        sprints = float(stats.get("sprints", stats.get("sprint_count", 0)))
        
        # Si données disponibles, calculer un ratio de fatigue potentielle
        if distance > 0 and sprints > 0:
            # Ratio sprints/distance - si bas = fatigue potentielle
            sprint_ratio = sprints / (distance / 1000)  # sprints par km
            running_distance_drop = max(0.0, min(1.0, 0.5 - sprint_ratio / 20))
        else:
            running_distance_drop = 0.3  # Valeur neutre
        
        # --- DUEL_LOSS_SPIKE ---
        # Inverse du ratio de duels gagnés
        if duels_total > 0:
            duels_lost = duels_total - duels_won
            duel_loss_ratio = duels_lost / duels_total
        else:
            duel_loss_ratio = 0.5
        
        # Spike si > 50% de duels perdus
        duel_loss_spike = min(1.0, max(0.0, (duel_loss_ratio - 0.3) / 0.4))
        
        return {
            "pressing_wave": round(pressing_wave, 3),
            "high_duel_pressure": round(high_duel_pressure, 3),
            "running_distance_drop": round(running_distance_drop, 3),
            "duel_loss_spike": round(duel_loss_spike, 3),
        }
    
    def compute_last_15(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux d'intensité sur les 15 dernières minutes (75-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - pressing_wave: float (0.0-1.0)
            - high_duel_pressure: float (0.0-1.0)
            - running_distance_drop: float (0.0-1.0)
            - duel_loss_spike: float (0.0-1.0)
        """
        # Chercher les données last_15_min si disponibles
        last_15_data = normalized_data.get("last_15_min", normalized_data.get("money_time", {}))
        global_stats = normalized_data.get("stats", normalized_data)
        
        if last_15_data:
            stats = last_15_data
        else:
            stats = global_stats
        
        # --- PRESSING_WAVE ---
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        ball_recoveries = float(stats.get("ball_recoveries", 
                                          stats.get("recoveries", interceptions + tackles)))
        
        # Seuil ajusté pour 15 minutes (~4-5 récupérations = bon pressing)
        pressing_actions = ball_recoveries + interceptions
        pressing_wave_raw = pressing_actions / 8
        pressing_wave = min(1.0, max(0.0, pressing_wave_raw))
        
        # --- HIGH_DUEL_PRESSURE ---
        duels_total = float(stats.get("duels", stats.get("duels_total", 15)))
        duels_won = float(stats.get("duels_won", duels_total * 0.5))
        
        if duels_total > 0:
            duel_win_ratio = duels_won / duels_total
        else:
            duel_win_ratio = 0.5
        
        high_duel_pressure = min(1.0, max(0.0, (duel_win_ratio - 0.3) / 0.4))
        
        # --- RUNNING_DISTANCE_DROP ---
        # Comparer distance last_15 vs moyenne attendue
        distance_last_15 = float(stats.get("distance_covered", 
                                           stats.get("running_distance", 0)))
        distance_global = float(global_stats.get("distance_covered",
                                                  global_stats.get("running_distance", 0)))
        
        # Calculer la drop en fin de match
        if distance_global > 0 and distance_last_15 > 0:
            # Attendu: ~1/6 de la distance totale dans les 15 dernières min
            expected_last_15 = distance_global / 6
            if expected_last_15 > 0:
                drop_ratio = 1.0 - (distance_last_15 / expected_last_15)
                running_distance_drop = max(0.0, min(1.0, drop_ratio + 0.3))
            else:
                running_distance_drop = 0.5
        else:
            # Sans données précises, utiliser les sprints comme proxy
            sprints = float(stats.get("sprints", stats.get("sprint_count", 2)))
            running_distance_drop = max(0.0, min(1.0, 0.8 - sprints / 10))
        
        # --- DUEL_LOSS_SPIKE ---
        # Plus sensible en fin de match
        if duels_total > 0:
            duels_lost = duels_total - duels_won
            duel_loss_ratio = duels_lost / duels_total
        else:
            duel_loss_ratio = 0.5
        
        # Spike accentué en fin de match
        duel_loss_spike = min(1.0, max(0.0, (duel_loss_ratio - 0.25) / 0.35))
        
        return {
            "pressing_wave": round(pressing_wave, 3),
            "high_duel_pressure": round(high_duel_pressure, 3),
            "running_distance_drop": round(running_distance_drop, 3),
            "duel_loss_spike": round(duel_loss_spike, 3),
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
