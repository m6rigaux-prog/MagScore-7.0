"""
MAGScore 6.1 — Support Bot
===========================
Conforme Constitution-MAGScore Section 4.

Règles de passivité totale :
- Ne pose aucune question
- Ne clarifie pas
- Ne reformule pas
- Ne conseille pas
- Ne ressemble pas à une IA
"""

from typing import Dict, Any, Optional
from datetime import datetime


class SupportBot:
    """
    Bot passif pour la collecte des retours utilisateur.
    
    Format de sortie unique (Constitution 4.2) :
        REÇU
        TYPE: (...)
        CONTENU: (...)
        TRAITEMENT: ENREGISTRÉ
    
    Règle messages courts (Constitution 4.3) :
        Si message < 4 mots : NOTE: CONTENU COURT
    """
    
    MIN_WORDS_THRESHOLD = 4
    
    def __init__(self) -> None:
        """Initialise le SupportBot."""
        self._records: list = []
    
    def record(self, message: str) -> Dict[str, Any]:
        """
        Enregistre un message utilisateur de manière passive.
        
        Args:
            message: Message brut de l'utilisateur.
        
        Returns:
            Dict au format :
            {
                'status': 'REÇU',
                'type': str,
                'contenu': str,
                'traitement': 'ENREGISTRÉ',
                'note': Optional[str]  # Si contenu court
            }
        """
        pass
    
    def _classify_message_type(self, message: str) -> str:
        """
        Classifie le type de message (feedback, question, autre).
        
        Args:
            message: Message à classifier.
        
        Returns:
            Type du message.
        """
        pass
    
    def _is_short_content(self, message: str) -> bool:
        """
        Vérifie si le message contient moins de 4 mots.
        
        Args:
            message: Message à vérifier.
        
        Returns:
            True si < 4 mots.
        """
        pass
    
    def get_records(self) -> list:
        """Retourne tous les enregistrements."""
        pass
