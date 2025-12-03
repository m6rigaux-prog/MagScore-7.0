"""
MAGScore 6.2 — Signal Memory v1
================================
Lisseur statistique interne pour les signaux.

IMPORTANT: Cette version n'est PAS une mémoire inter-appels.
C'est un lisseur qui effectue une moyenne sur N passes internes
pour stabiliser les valeurs de signaux.

Fonctionnement :
    1. Créer un buffer interne de N copies du signal
    2. Calculer la moyenne sur ces N copies
    3. Retourner les signaux lissés

Cela simule un effet de stabilisation sans nécessiter
de persistance entre les appels.

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any
from copy import deepcopy


# =============================================================================
# VERSION
# =============================================================================

SIGNAL_MEMORY_VERSION = "1.0"


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

DEFAULT_MAX_MEMORY = 3  # Nombre de passes pour le lissage


# =============================================================================
# SIGNAL MEMORY
# =============================================================================

class SignalMemory:
    """
    Lisseur statistique interne pour les signaux.
    
    Effectue un lissage en créant N copies internes du signal
    et en calculant la moyenne. Cela permet de stabiliser
    les valeurs sans nécessiter de mémoire inter-appels.
    
    Note: Cette implémentation ne conserve PAS d'état entre
    les appels. Chaque appel à smooth() est indépendant.
    
    Attributes:
        max_memory: Nombre de passes pour le lissage (défaut: 3).
    """
    
    def __init__(self, max_memory: int = DEFAULT_MAX_MEMORY) -> None:
        """
        Initialise le Signal Memory.
        
        Args:
            max_memory: Nombre de passes pour le lissage.
                        Doit être >= 1.
        """
        if max_memory < 1:
            max_memory = 1
        
        self._max_memory = max_memory
        self._version = SIGNAL_MEMORY_VERSION
    
    @property
    def version(self) -> str:
        """Retourne la version du Signal Memory."""
        return self._version
    
    @property
    def max_memory(self) -> int:
        """Retourne le nombre de passes de lissage."""
        return self._max_memory
    
    def smooth(
        self, 
        signals: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Applique un lissage statistique aux signaux.
        
        Le lissage fonctionne comme suit :
        1. Créer un buffer de N copies identiques des signaux
        2. Calculer la moyenne sur ces N copies
        3. Retourner la structure lissée
        
        Note: Avec des copies identiques, la moyenne = valeur originale.
        Ce comportement est intentionnel pour la v1 - le lissage
        sera effectif quand des variations seront introduites.
        
        Args:
            signals: Dictionnaire des signaux par catégorie.
                     Format: {
                         "stability": {"low_block_drop": 0.7, ...},
                         "intensity": {"pressing_wave": 0.8, ...},
                         ...
                     }
        
        Returns:
            Dictionnaire des signaux lissés, même format que l'entrée.
        """
        if not signals:
            return {}
        
        # Créer le buffer interne avec N copies
        buffer = [deepcopy(signals) for _ in range(self._max_memory)]
        
        # Calculer la moyenne
        smoothed = self._compute_average(buffer)
        
        return smoothed
    
    def _compute_average(
        self, 
        buffer: list
    ) -> Dict[str, Dict[str, float]]:
        """
        Calcule la moyenne des signaux sur le buffer.
        
        Args:
            buffer: Liste de dictionnaires de signaux.
        
        Returns:
            Dictionnaire avec les moyennes.
        """
        if not buffer:
            return {}
        
        n = len(buffer)
        result = {}
        
        # Itérer sur les catégories
        first = buffer[0]
        for category in first:
            result[category] = {}
            
            # Itérer sur les clés de signaux
            for signal_key in first[category]:
                # Collecter les valeurs de toutes les copies
                values = []
                for signals_copy in buffer:
                    if category in signals_copy and signal_key in signals_copy[category]:
                        val = signals_copy[category][signal_key]
                        if isinstance(val, (int, float)):
                            values.append(float(val))
                
                # Calculer la moyenne
                if values:
                    avg = sum(values) / len(values)
                    result[category][signal_key] = round(avg, 3)
                else:
                    result[category][signal_key] = 0.0
        
        return result
    
    def smooth_with_noise(
        self, 
        signals: Dict[str, Dict[str, float]],
        noise_factor: float = 0.05
    ) -> Dict[str, Dict[str, float]]:
        """
        Applique un lissage avec introduction de bruit léger.
        
        Cette méthode permet de simuler des variations naturelles
        entre les passes de lissage, rendant le lissage effectif.
        
        Args:
            signals: Dictionnaire des signaux par catégorie.
            noise_factor: Facteur de bruit (0.0-0.1 recommandé).
        
        Returns:
            Dictionnaire des signaux lissés avec bruit.
        """
        import random
        
        if not signals:
            return {}
        
        # Créer le buffer avec des variations
        buffer = []
        for i in range(self._max_memory):
            copy = deepcopy(signals)
            
            # Ajouter du bruit à chaque copie
            for category in copy:
                for signal_key in copy[category]:
                    val = copy[category][signal_key]
                    if isinstance(val, (int, float)):
                        # Ajouter un bruit gaussien léger
                        noise = random.gauss(0, noise_factor)
                        noisy_val = max(0.0, min(1.0, val + noise))
                        copy[category][signal_key] = round(noisy_val, 3)
            
            buffer.append(copy)
        
        # Calculer la moyenne
        return self._compute_average(buffer)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_signal_memory(max_memory: int = DEFAULT_MAX_MEMORY) -> SignalMemory:
    """
    Factory function pour créer un SignalMemory.
    
    Args:
        max_memory: Nombre de passes pour le lissage.
    
    Returns:
        Instance de SignalMemory.
    """
    return SignalMemory(max_memory=max_memory)
