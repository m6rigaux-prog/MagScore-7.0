"""
MAGScore 6.1 — Bots Module
===========================
Contient les bots conformes à la Constitution :
- AnalysisBot : génère des rapports neutres
- SupportBot : collecte passive des retours
"""

from .analysis_bot import AnalysisBot
from .support_bot import SupportBot

__all__ = ["AnalysisBot", "SupportBot"]
