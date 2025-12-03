"""
MAGScore 6.1 — Stability Module v2
===================================
Extraction des signaux de stabilité structurelle.

Comportements associés :
    STB_01 : Effondrement Structurel (last_15_min)
        - low_block_drop
        - xg_against_spike
    STB_02 : Verrouillage Tactique (global)
        - high_compactness
        - successful_low_block

Ces signaux DOIVENT correspondre EXACTEMENT aux clés de BEHAVIOR_DEFINITIONS.
"""

from typing import Dict, Any


class StabilityModule:
    """
    Module d'extraction des signaux de stabilité.
    
    Analyse la structure défensive et la cohésion positionnelle
    à partir des données normalisées (RAW DATA ONLY).
    
    Méthodes obligatoires :
        - compute_global(normalized_data) -> Dict[str, float]
        - compute_last_15(normalized_data) -> Dict[str, float]
    """
    
    def __init__(self) -> None:
        """Initialise le module de stabilité."""
        self._default_value = 0.0
    
    def compute_global(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux de stabilité sur la période globale (0-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - low_block_drop: float (0.0-1.0)
            - xg_against_spike: float (0.0-1.0)
            - high_compactness: float (0.0-1.0)
            - successful_low_block: float (0.0-1.0)
        """
        # Extraire les données pertinentes
        stats = normalized_data.get("stats", normalized_data)
        
        # --- HIGH_COMPACTNESS ---
        # Basé sur le ratio d'interceptions + tacles réussis vs tirs concédés
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        shots_against = float(stats.get("shots_conceded", stats.get("shots_against", 5)))
        
        # Plus d'interceptions/tacles et moins de tirs = plus compact
        defensive_actions = interceptions + tackles
        if shots_against > 0:
            compactness_raw = defensive_actions / (shots_against * 3)  # Normalize
        else:
            compactness_raw = defensive_actions / 15  # Fallback
        high_compactness = min(1.0, max(0.0, compactness_raw))
        
        # --- SUCCESSFUL_LOW_BLOCK ---
        # Basé sur les dégagements, blocks et tirs bloqués
        clearances = float(stats.get("clearances", 0))
        blocks = float(stats.get("blocks", stats.get("shots_blocked", 0)))
        saves = float(stats.get("saves", 0))
        
        # Plus de dégagements et blocks = low block réussi
        low_block_actions = clearances + blocks + saves
        successful_low_block_raw = low_block_actions / 20  # Normalize sur ~20 actions
        successful_low_block = min(1.0, max(0.0, successful_low_block_raw))
        
        # --- LOW_BLOCK_DROP ---
        # Inverse de la solidité défensive - utilisé pour effondrement
        # Si on a peu de récupérations mais beaucoup de tirs contre
        shots_on_target_against = float(stats.get("shots_on_target_against", 
                                                   stats.get("shots_on_target_conceded", 2)))
        if defensive_actions > 0:
            drop_ratio = shots_on_target_against / (defensive_actions + 1)
        else:
            drop_ratio = shots_on_target_against / 5
        low_block_drop = min(1.0, max(0.0, drop_ratio))
        
        # --- XG_AGAINST_SPIKE ---
        # Basé sur xG concédé si disponible, sinon estimation via tirs
        xg_against = float(stats.get("xg_against", stats.get("expected_goals_against", 0)))
        if xg_against > 0:
            xg_spike = min(1.0, xg_against / 2.0)  # 2.0 xG = spike max
        else:
            # Estimation via tirs cadrés concédés
            xg_spike = min(1.0, shots_on_target_against / 6)
        xg_against_spike = xg_spike
        
        return {
            "low_block_drop": round(low_block_drop, 3),
            "xg_against_spike": round(xg_against_spike, 3),
            "high_compactness": round(high_compactness, 3),
            "successful_low_block": round(successful_low_block, 3),
        }
    
    def compute_last_15(self, normalized_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule les signaux de stabilité sur les 15 dernières minutes (75-90').
        
        Args:
            normalized_data: Données provenant de normalize_api.normalize().
        
        Returns:
            Dict avec les clés obligatoires :
            - low_block_drop: float (0.0-1.0)
            - xg_against_spike: float (0.0-1.0)
            - high_compactness: float (0.0-1.0)
            - successful_low_block: float (0.0-1.0)
        """
        # Chercher les données last_15_min si disponibles
        last_15_data = normalized_data.get("last_15_min", normalized_data.get("money_time", {}))
        
        if last_15_data:
            stats = last_15_data
        else:
            # Fallback: utiliser les données globales avec ajustement
            stats = normalized_data.get("stats", normalized_data)
        
        # --- Calculs similaires à global mais pondérés pour la fin de match ---
        
        interceptions = float(stats.get("interceptions", 0))
        tackles = float(stats.get("tackles", stats.get("tackles_won", 0)))
        shots_against = float(stats.get("shots_conceded", stats.get("shots_against", 2)))
        
        # En fin de match, moins d'actions défensives = potentiel effondrement
        defensive_actions = interceptions + tackles
        
        # HIGH_COMPACTNESS (peut diminuer en fin de match)
        if shots_against > 0:
            compactness_raw = defensive_actions / (shots_against * 2)
        else:
            compactness_raw = defensive_actions / 10
        high_compactness = min(1.0, max(0.0, compactness_raw))
        
        # SUCCESSFUL_LOW_BLOCK
        clearances = float(stats.get("clearances", 0))
        blocks = float(stats.get("blocks", stats.get("shots_blocked", 0)))
        saves = float(stats.get("saves", 0))
        low_block_actions = clearances + blocks + saves
        successful_low_block_raw = low_block_actions / 10  # Échelle réduite pour 15 min
        successful_low_block = min(1.0, max(0.0, successful_low_block_raw))
        
        # LOW_BLOCK_DROP (plus sensible en fin de match)
        shots_on_target_against = float(stats.get("shots_on_target_against",
                                                   stats.get("shots_on_target_conceded", 1)))
        # Multiplier pour sensibilité fin de match
        drop_ratio = (shots_on_target_against * 1.5) / (defensive_actions + 1)
        low_block_drop = min(1.0, max(0.0, drop_ratio))
        
        # XG_AGAINST_SPIKE
        xg_against = float(stats.get("xg_against", stats.get("expected_goals_against", 0)))
        if xg_against > 0:
            xg_spike = min(1.0, xg_against / 1.0)  # Seuil plus bas pour 15 min
        else:
            xg_spike = min(1.0, shots_on_target_against / 3)
        xg_against_spike = xg_spike
        
        return {
            "low_block_drop": round(low_block_drop, 3),
            "xg_against_spike": round(xg_against_spike, 3),
            "high_compactness": round(high_compactness, 3),
            "successful_low_block": round(successful_low_block, 3),
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
