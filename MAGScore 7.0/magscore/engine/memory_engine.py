"""
MAGScore 7.0 — Memory Engine v1
================================
Gestion de la mémoire épisodique et sémantique.

RÈGLE D'OR (SÉCURITÉ ABSOLUE) :
    INTERDICTION de stocker :
        - score final
        - résultat du match (Gagné/Perdu)
        - données de cotes/betting
    
    UNIQUEMENT la structure comportementale.

Fonctionnalités :
    - Mémoire épisodique (FIFO, 10 derniers matchs)
    - Mémoire sémantique (fréquences de patterns agrégées)
    - Filtrage de sécurité automatique

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging
import json

from .definitions import (
    Episode,
    SemanticMemory,
    TeamMemory,
    FORBIDDEN_MEMORY_KEYS,
    is_forbidden_memory_key,
)


# =============================================================================
# VERSION
# =============================================================================

MEMORY_ENGINE_VERSION = "1.0"


# =============================================================================
# CONSTANTS
# =============================================================================

MAX_EPISODES = 10  # Stockage FIFO des 10 derniers matchs


# =============================================================================
# EXCEPTIONS
# =============================================================================

class MemoryEngineError(Exception):
    """Exception levée par le MemoryEngine."""
    pass


class ForbiddenDataError(MemoryEngineError):
    """Exception levée lors d'une tentative d'injection de données interdites."""
    pass


# =============================================================================
# EPISODIC MEMORY
# =============================================================================

class EpisodicMemory:
    """
    Gère la mémoire épisodique d'une équipe (FIFO).
    
    Stocke les N derniers épisodes (matchs) avec leurs comportements,
    patterns et phases de flow.
    
    SÉCURITÉ : Filtre automatiquement les données interdites.
    """
    
    def __init__(self, max_episodes: int = MAX_EPISODES) -> None:
        """
        Initialise la mémoire épisodique.
        
        Args:
            max_episodes: Nombre maximum d'épisodes à conserver.
        """
        self._episodes: List[Episode] = []
        self._max_episodes = max_episodes
        self._logger = logging.getLogger(__name__)
    
    @property
    def episodes(self) -> List[Episode]:
        """Retourne la liste des épisodes."""
        return self._episodes.copy()
    
    @property
    def count(self) -> int:
        """Retourne le nombre d'épisodes."""
        return len(self._episodes)
    
    def add(self, episode: Episode) -> None:
        """
        Ajoute un épisode (FIFO).
        
        Args:
            episode: Épisode à ajouter.
        
        Note:
            Si le maximum est atteint, l'épisode le plus ancien est supprimé.
        """
        self._episodes.append(episode)
        
        # FIFO : supprimer le plus ancien si nécessaire
        while len(self._episodes) > self._max_episodes:
            removed = self._episodes.pop(0)
            self._logger.debug(f"Épisode FIFO supprimé: {removed.match_id}")
    
    def get_recent(self, n: int = 5) -> List[Episode]:
        """
        Récupère les N épisodes les plus récents.
        
        Args:
            n: Nombre d'épisodes à récupérer.
        
        Returns:
            Liste des N épisodes les plus récents.
        """
        return self._episodes[-n:]
    
    def get_by_opposing_style(self, style: str) -> List[Episode]:
        """
        Récupère les épisodes contre un style de jeu spécifique.
        
        Args:
            style: Style de jeu adverse (ex: "HIGH_PRESS_POSSESSION").
        
        Returns:
            Liste des épisodes correspondants.
        """
        return [
            ep for ep in self._episodes 
            if ep.opposing_style == style
        ]
    
    def clear(self) -> None:
        """Efface tous les épisodes."""
        self._episodes.clear()
        self._logger.info("Mémoire épisodique effacée")


# =============================================================================
# MEMORY ENGINE
# =============================================================================

class MemoryEngine:
    """
    Moteur de mémoire principal MAGScore 7.0.
    
    Orchestre la mémoire épisodique et sémantique :
        - Ingestion sécurisée des données
        - Agrégation des fréquences de patterns
        - Requêtes contextuelles
    
    RÈGLE DE SÉCURITÉ ABSOLUE :
        La méthode ingest() filtre ou rejette automatiquement
        toute donnée interdite (score, result, odds, etc.).
    """
    
    def __init__(self) -> None:
        """Initialise le Memory Engine."""
        self._memories: Dict[str, TeamMemory] = {}
        self._version = MEMORY_ENGINE_VERSION
        self._logger = logging.getLogger(__name__)
    
    @property
    def version(self) -> str:
        """Retourne la version du Memory Engine."""
        return self._version
    
    def ingest(
        self, 
        team_id: str, 
        data: Dict[str, Any],
        strict: bool = True
    ) -> Episode:
        """
        Ingère des données comportementales pour une équipe.
        
        SÉCURITÉ : Cette méthode filtre automatiquement les données interdites.
        
        Args:
            team_id: Identifiant de l'équipe.
            data: Données à ingérer. Format attendu :
                  {
                      "match_id": str,
                      "behaviors": List[str],
                      "patterns": List[str],
                      "flow_phases": List[str],
                      "opposing_style": str (optionnel)
                  }
            strict: Si True, lève une exception sur données interdites.
                    Si False, filtre silencieusement.
        
        Returns:
            Episode créé et stocké.
        
        Raises:
            ForbiddenDataError: Si strict=True et données interdites détectées.
        """
        # ====================================================================
        # CONTRÔLE DE SÉCURITÉ — CRITIQUE
        # ====================================================================
        
        forbidden_found = self._check_forbidden_keys(data)
        
        if forbidden_found:
            self._logger.warning(
                f"Données interdites détectées pour {team_id}: {forbidden_found}"
            )
            
            if strict:
                raise ForbiddenDataError(
                    f"Tentative d'injection de données interdites: {forbidden_found}"
                )
            else:
                # Filtrer les clés interdites
                data = self._sanitize_data(data)
        
        # ====================================================================
        # ASSERTIONS DE SÉCURITÉ
        # ====================================================================
        
        assert "score" not in data, "SÉCURITÉ: score interdit"
        assert "result" not in data, "SÉCURITÉ: result interdit"
        assert "winner" not in data, "SÉCURITÉ: winner interdit"
        assert "odds" not in data, "SÉCURITÉ: odds interdit"
        
        # ====================================================================
        # CRÉATION DE L'ÉPISODE
        # ====================================================================
        
        # Initialiser la mémoire de l'équipe si nécessaire
        if team_id not in self._memories:
            self._memories[team_id] = TeamMemory(team_id=team_id)
        
        team_memory = self._memories[team_id]
        
        # Créer l'épisode
        episode = Episode(
            match_id=data.get("match_id", f"{team_id}_{datetime.now().isoformat()}"),
            timestamp=datetime.now(),
            opposing_style=data.get("opposing_style", ""),
            behaviors=data.get("behaviors", []),
            patterns=data.get("patterns", []),
            flow_phases=data.get("flow_phases", []),
        )
        
        # Ajouter à la mémoire épisodique
        if team_memory.episodes is None:
            team_memory.episodes = []
        
        team_memory.episodes.append(episode)
        
        # FIFO: limiter à MAX_EPISODES
        while len(team_memory.episodes) > MAX_EPISODES:
            team_memory.episodes.pop(0)
        
        # Mettre à jour la mémoire sémantique
        self._update_semantic_memory(team_memory, episode)
        
        self._logger.info(
            f"Épisode ingéré pour {team_id}: {episode.match_id}"
        )
        
        return episode
    
    def _check_forbidden_keys(self, data: Dict[str, Any]) -> Set[str]:
        """
        Vérifie la présence de clés interdites dans les données.
        
        Args:
            data: Données à vérifier.
        
        Returns:
            Set des clés interdites trouvées.
        """
        forbidden_found: Set[str] = set()
        
        def check_dict(d: Dict[str, Any], prefix: str = "") -> None:
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if is_forbidden_memory_key(key):
                    forbidden_found.add(full_key)
                
                # Vérifier récursivement les dicts imbriqués
                if isinstance(value, dict):
                    check_dict(value, full_key)
        
        check_dict(data)
        return forbidden_found
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supprime les clés interdites des données.
        
        Args:
            data: Données à nettoyer.
        
        Returns:
            Données nettoyées.
        """
        sanitized: Dict[str, Any] = {}
        
        for key, value in data.items():
            if is_forbidden_memory_key(key):
                continue
            
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _update_semantic_memory(
        self, 
        team_memory: TeamMemory, 
        episode: Episode
    ) -> None:
        """
        Met à jour la mémoire sémantique avec un nouvel épisode.
        
        Args:
            team_memory: Mémoire de l'équipe.
            episode: Nouvel épisode.
        """
        if team_memory.semantic is None:
            team_memory.semantic = SemanticMemory()
        
        semantic = team_memory.semantic
        
        # Recalculer les fréquences de patterns
        all_patterns: List[str] = []
        for ep in team_memory.episodes:
            all_patterns.extend(ep.patterns)
        
        if all_patterns:
            pattern_counts: Dict[str, int] = {}
            for pattern in all_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            total = len(all_patterns)
            semantic.pattern_frequency = {
                p: count / total 
                for p, count in pattern_counts.items()
            }
        
        semantic.last_updated = datetime.now()
    
    def get_team_memory(self, team_id: str) -> Optional[TeamMemory]:
        """
        Récupère la mémoire complète d'une équipe.
        
        Args:
            team_id: Identifiant de l'équipe.
        
        Returns:
            TeamMemory ou None si non trouvée.
        """
        return self._memories.get(team_id)
    
    def get_recent_episodes(
        self, 
        team_id: str, 
        n: int = 5
    ) -> List[Episode]:
        """
        Récupère les N épisodes les plus récents d'une équipe.
        
        Args:
            team_id: Identifiant de l'équipe.
            n: Nombre d'épisodes à récupérer.
        
        Returns:
            Liste des épisodes.
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None or not team_memory.episodes:
            return []
        
        return team_memory.episodes[-n:]
    
    def get_pattern_history(
        self, 
        team_id: str, 
        pattern_code: str
    ) -> List[Episode]:
        """
        Récupère les épisodes où un pattern spécifique a été détecté.
        
        Args:
            team_id: Identifiant de l'équipe.
            pattern_code: Code du pattern (ex: "PTN_04").
        
        Returns:
            Liste des épisodes avec ce pattern.
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None or not team_memory.episodes:
            return []
        
        return [
            ep for ep in team_memory.episodes 
            if pattern_code in ep.patterns
        ]
    
    def get_episodes_vs_style(
        self, 
        team_id: str, 
        opposing_style: str
    ) -> List[Episode]:
        """
        Récupère les épisodes contre un style de jeu spécifique.
        
        Args:
            team_id: Identifiant de l'équipe.
            opposing_style: Style de jeu adverse.
        
        Returns:
            Liste des épisodes correspondants.
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None or not team_memory.episodes:
            return []
        
        return [
            ep for ep in team_memory.episodes 
            if ep.opposing_style == opposing_style
        ]
    
    def get_pattern_frequency(
        self, 
        team_id: str, 
        pattern_code: str
    ) -> float:
        """
        Récupère la fréquence d'un pattern pour une équipe.
        
        Args:
            team_id: Identifiant de l'équipe.
            pattern_code: Code du pattern.
        
        Returns:
            Fréquence entre 0.0 et 1.0.
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None or team_memory.semantic is None:
            return 0.0
        
        return team_memory.semantic.pattern_frequency.get(pattern_code, 0.0)
    
    def get_historical_context(
        self, 
        team_id: str, 
        opposing_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère un contexte historique pour l'AnalysisBot.
        
        Args:
            team_id: Identifiant de l'équipe.
            opposing_style: Style adverse pour filtrage (optionnel).
        
        Returns:
            Dict avec contexte historique :
            {
                "total_episodes": int,
                "pattern_tendencies": Dict[str, float],
                "vs_style": {
                    "episodes_count": int,
                    "common_patterns": List[str],
                }
            }
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None:
            return {
                "total_episodes": 0,
                "pattern_tendencies": {},
                "vs_style": None,
            }
        
        context = {
            "total_episodes": len(team_memory.episodes) if team_memory.episodes else 0,
            "pattern_tendencies": (
                team_memory.semantic.pattern_frequency 
                if team_memory.semantic else {}
            ),
        }
        
        # Contexte contre un style spécifique
        if opposing_style:
            vs_episodes = self.get_episodes_vs_style(team_id, opposing_style)
            
            if vs_episodes:
                # Trouver les patterns les plus fréquents contre ce style
                pattern_counts: Dict[str, int] = {}
                for ep in vs_episodes:
                    for p in ep.patterns:
                        pattern_counts[p] = pattern_counts.get(p, 0) + 1
                
                sorted_patterns = sorted(
                    pattern_counts.keys(),
                    key=lambda p: pattern_counts[p],
                    reverse=True
                )
                
                context["vs_style"] = {
                    "opposing_style": opposing_style,
                    "episodes_count": len(vs_episodes),
                    "common_patterns": sorted_patterns[:3],
                }
            else:
                context["vs_style"] = None
        else:
            context["vs_style"] = None
        
        return context
    
    def export_team_memory(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Exporte la mémoire d'une équipe en format JSON-serializable.
        
        Args:
            team_id: Identifiant de l'équipe.
        
        Returns:
            Dict exportable ou None.
        """
        team_memory = self._memories.get(team_id)
        
        if team_memory is None:
            return None
        
        return {
            "team_id": team_memory.team_id,
            "episodes": [
                {
                    "match_id": ep.match_id,
                    "timestamp": ep.timestamp.isoformat(),
                    "opposing_style": ep.opposing_style,
                    "behaviors": ep.behaviors,
                    "patterns": ep.patterns,
                    "flow_phases": ep.flow_phases,
                }
                for ep in team_memory.episodes
            ] if team_memory.episodes else [],
            "semantic": {
                "pattern_frequency": (
                    team_memory.semantic.pattern_frequency 
                    if team_memory.semantic else {}
                ),
                "last_updated": (
                    team_memory.semantic.last_updated.isoformat() 
                    if team_memory.semantic and team_memory.semantic.last_updated 
                    else None
                ),
            },
        }
    
    def clear_team_memory(self, team_id: str) -> None:
        """
        Efface la mémoire d'une équipe.
        
        Args:
            team_id: Identifiant de l'équipe.
        """
        if team_id in self._memories:
            del self._memories[team_id]
            self._logger.info(f"Mémoire effacée pour {team_id}")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_memory_engine() -> MemoryEngine:
    """
    Factory function pour créer un MemoryEngine.
    
    Returns:
        Instance de MemoryEngine.
    """
    return MemoryEngine()

