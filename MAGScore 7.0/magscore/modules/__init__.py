"""
MAGScore 6.1 — Modules d'extraction de signaux
================================================
Conforme Constitution-MAGScore.

Chaque module extrait les signaux bruts de son domaine :
- StabilityModule : signaux de stabilité structurelle
- IntensityModule : signaux d'intensité physique
- PsychologyModule : signaux psychologiques
- CohesionModule : signaux de cohésion collective
"""

from .stability import StabilityModule
from .intensity import IntensityModule
from .psychology import PsychologyModule
from .cohesion import CohesionModule

__all__ = [
    "StabilityModule",
    "IntensityModule",
    "PsychologyModule",
    "CohesionModule",
]
