"""
MAGScore 6.1 — Cohesion Module v2
==================================
Extraction des signaux de cohésion collective.

Ce module analyse la coordination et l'harmonie collective.
Il ne produit pas de comportements directement dans BEHAVIOR_DEFINITIONS
mais fournit des signaux auxiliaires pour l'analyse contextuelle.

Signaux auxiliaires extraits :
    - passing_accuracy_score
    - possession_control
    - team_coordination
    - collective_movement
"""

from typing import Dict, Any


class CohesionModule:
    """
    Module d'extraction des signaux de cohésion.
    
    Analyse la coordination collective et l'harmonie d'équipe
    à partir des données normalisées (RAW DATA ONLY).
    
    Note: Ce module produit des signaux auxiliaires qui enrichissent
    l'analyse mais ne sont pas directement liés aux comportements
    définis dans BEHAVIOR_DEFINITIONS.
    
    Méthodes obligatoires :
        - compute_global(normalized_data) -> Dict[str, float]
        - compute_last_15(normalized_data) -> Dict[str, float]
    """
    
    def __init__(self) -> None:
        """Initialise le module de cohésion."""
        self._default_value = 0.0
    
    def compute_global(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux de cohésion sur la période globale (0-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les signaux auxiliaires :
            - passing_accuracy_score: float (0.0-1.0)
            - possession_control: float (0.0-1.0)
            - team_coordination: float (0.0-1.0)
            - collective_movement: float (0.0-1.0)
        """
        stats = normalized_data.get("stats", normalized_data)
        
        # --- PASSING_ACCURACY_SCORE ---
        passes_total = float(stats.get("passes", stats.get("passes_total", 400)))
        passes_completed = float(stats.get("passes_completed", passes_total * 0.8))
        passes_accuracy = float(stats.get("passes_accuracy", 
                                          stats.get("pass_accuracy", 0)))
        
        if passes_accuracy > 0:
            passing_accuracy_score = min(1.0, passes_accuracy / 100)
        elif passes_total > 0:
            passing_accuracy_score = passes_completed / passes_total
        else:
            passing_accuracy_score = 0.5
        
        # --- POSSESSION_CONTROL ---
        possession = float(stats.get("possession", 
                                      stats.get("possession_percentage", 50)))
        
        # Normaliser: 50% = 0.5, 70% = 0.9
        if possession > 0:
            possession_control = min(1.0, (possession - 30) / 50)
        else:
            possession_control = 0.5
        possession_control = max(0.0, possession_control)
        
        # --- TEAM_COORDINATION ---
        # Basé sur les passes clés et les assists
        key_passes = float(stats.get("key_passes", 0))
        assists = float(stats.get("assists", 0))
        
        coordination_score = (key_passes * 2 + assists * 5) / 20
        team_coordination = min(1.0, max(0.0, coordination_score))
        
        # --- COLLECTIVE_MOVEMENT ---
        # Basé sur la distance parcourue et les sprints
        distance = float(stats.get("distance_covered", 
                                   stats.get("running_distance", 100)))
        sprints = float(stats.get("sprints", stats.get("sprint_count", 0)))
        
        if distance > 0:
            movement_score = (distance / 110) * 0.5 + (sprints / 150) * 0.5
        else:
            movement_score = 0.5
        collective_movement = min(1.0, max(0.0, movement_score))
        
        return {
            "passing_accuracy_score": round(passing_accuracy_score, 3),
            "possession_control": round(possession_control, 3),
            "team_coordination": round(team_coordination, 3),
            "collective_movement": round(collective_movement, 3),
        }
    
    def compute_last_15(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux de cohésion sur les 15 dernières minutes (75-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les signaux auxiliaires :
            - passing_accuracy_score: float (0.0-1.0)
            - possession_control: float (0.0-1.0)
            - team_coordination: float (0.0-1.0)
            - collective_movement: float (0.0-1.0)
        """
        # Chercher les données last_15_min si disponibles
        last_15_data = normalized_data.get("last_15_min", normalized_data.get("money_time", {}))
        
        if last_15_data:
            stats = last_15_data
        else:
            stats = normalized_data.get("stats", normalized_data)
        
        # --- PASSING_ACCURACY_SCORE ---
        passes_total = float(stats.get("passes", stats.get("passes_total", 70)))
        passes_completed = float(stats.get("passes_completed", passes_total * 0.75))
        passes_accuracy = float(stats.get("passes_accuracy", 
                                          stats.get("pass_accuracy", 0)))
        
        if passes_accuracy > 0:
            passing_accuracy_score = min(1.0, passes_accuracy / 100)
        elif passes_total > 0:
            passing_accuracy_score = passes_completed / passes_total
        else:
            passing_accuracy_score = 0.5
        
        # --- POSSESSION_CONTROL ---
        possession = float(stats.get("possession", 
                                      stats.get("possession_percentage", 50)))
        
        if possession > 0:
            possession_control = min(1.0, (possession - 30) / 50)
        else:
            possession_control = 0.5
        possession_control = max(0.0, possession_control)
        
        # --- TEAM_COORDINATION ---
        key_passes = float(stats.get("key_passes", 0))
        assists = float(stats.get("assists", 0))
        
        # Seuils ajustés pour 15 min
        coordination_score = (key_passes * 3 + assists * 6) / 12
        team_coordination = min(1.0, max(0.0, coordination_score))
        
        # --- COLLECTIVE_MOVEMENT ---
        distance = float(stats.get("distance_covered", 
                                   stats.get("running_distance", 15)))
        sprints = float(stats.get("sprints", stats.get("sprint_count", 0)))
        
        # Ajusté pour 15 min (~1/6 du match)
        if distance > 0:
            movement_score = (distance / 18) * 0.5 + (sprints / 25) * 0.5
        else:
            movement_score = 0.5
        collective_movement = min(1.0, max(0.0, movement_score))
        
        return {
            "passing_accuracy_score": round(passing_accuracy_score, 3),
            "possession_control": round(possession_control, 3),
            "team_coordination": round(team_coordination, 3),
            "collective_movement": round(collective_movement, 3),
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
