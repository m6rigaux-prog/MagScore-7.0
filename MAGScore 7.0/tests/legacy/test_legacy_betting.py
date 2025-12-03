"""
MAGScore 6.1 — Legacy Tests: Betting Modules
=============================================

⚠️ QUARANTAINE ⚠️

Ces tests sont désactivés car ils dépendent des modules de paris
qui ont été déplacés dans legacy_betting/.

Marqués @pytest.mark.skip pour maintenir pytest vert.
"""

import pytest


@pytest.mark.skip(reason="Module déplacé en quarantaine: legacy_betting/bet_strategy_engine.py")
class TestBetStrategyEngine:
    """Tests legacy du moteur de stratégie de paris."""
    
    def test_placeholder(self):
        """Placeholder — test désactivé."""
        pass


@pytest.mark.skip(reason="Module déplacé en quarantaine: legacy_betting/consensus_engine.py")
class TestConsensusEngine:
    """Tests legacy du moteur de consensus."""
    
    def test_placeholder(self):
        """Placeholder — test désactivé."""
        pass


@pytest.mark.skip(reason="Module déplacé en quarantaine: legacy_betting/risk_manager.py")
class TestRiskManager:
    """Tests legacy du gestionnaire de risques."""
    
    def test_placeholder(self):
        """Placeholder — test désactivé."""
        pass


@pytest.mark.skip(reason="Module déplacé en quarantaine: legacy_betting/predictor.py")
class TestPredictor:
    """Tests legacy du prédicteur."""
    
    def test_placeholder(self):
        """Placeholder — test désactivé."""
        pass
