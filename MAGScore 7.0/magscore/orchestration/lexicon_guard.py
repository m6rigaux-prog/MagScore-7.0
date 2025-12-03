"""
MAGScore 6.1 — Lexicon Guard v2
================================
Conforme Constitution-MAGScore Section 3.4.
Garde-fou final pour bloquer tout vocabulaire interdit.

IMPORTANT: Ce module est le DERNIER rempart avant la sortie.
Aucune auto-correction : en cas de violation, une exception est levée.

Lexique autorisé : stabilité, intensité, cohésion, dynamique, contrôle, pression
Lexique interdit : pari, cote, favori, value, prono, bankroll, etc.
"""

from typing import List, Tuple, Optional, Iterable


# =============================================================================
# EXCEPTION
# =============================================================================

class LexiconGuardError(Exception):
    """
    Exception levée lorsque le rapport contient du vocabulaire interdit.
    
    Attributes:
        violations: Liste des termes interdits détectés.
        text: Texte original (optionnel).
    """
    
    def __init__(self, violations: List[str], text: Optional[str] = None):
        self.violations = violations
        self.text = text
        message = f"Forbidden term detected: {violations[0]}" if len(violations) == 1 else \
                  f"Forbidden terms detected: {', '.join(violations)}"
        super().__init__(message)


# =============================================================================
# BLACKLIST — VOCABULAIRE INTERDIT (SPEC PARTIE 4)
# =============================================================================

BLACKLIST: Iterable[str] = frozenset([
    # --- Termes de paris directs ---
    "pari",
    "parier",
    "mise",
    "miser",
    "cote",
    "cotes",
    "odd",
    "odds",
    
    # --- Bankroll / Gestion ---
    "bankroll",
    "bankrol",
    
    # --- Pronostics ---
    "prono",
    "pronos",
    "pronostic",
    "pronostics",
    "tip",
    "tips",
    
    # --- Value betting ---
    "value",
    "value bet",
    "valuebet",
    "surebet",
    "sure bet",
    
    # --- Termes de gain ---
    "jackpot",
    "gain",
    "gains",
    "profit",
    
    # --- Prédictions / Certitude ---
    "gagnera",
    "gagnant",
    "perdra",
    "perdant",
    "garanti",
    "garantie",
    "sûr",
    "sure",
    "certain",
    "certaine",
    "écrasera",
    "dominera",
    "fixe",
    
    # --- Probabilités ---
    "probabilité",
    "probabilités",
    "probability",
    "chance",
    "chances",
    
    # --- Favoris ---
    "favori",
    "favorite",
    "favoris",
    "underdog",
    "outsider",
    
    # --- Bookmakers ---
    "bookmaker",
    "bookmakers",
    "bookie",
    "book",
    "sportsbook",
    "betting",
    "bet",
    "bets",
    
    # --- Conseils ---
    "conseil",
    "conseils",
    "recommande",
    "recommandation",
    "jouer",
    "joue",
    
    # --- Termes péjoratifs ---
    "craquage",
    "passoire",
    "nul",
    "catastrophique",
    "lamentable",
    "désastre",
    
    # --- Lock / Banker ---
    "lock",
    "banker",
    "safe",
])


# =============================================================================
# WHITELIST — TERMES AUTORISÉS (référence)
# =============================================================================

WHITELIST: Iterable[str] = frozenset([
    # Analyse structurelle
    "stabilité",
    "stability",
    "structure",
    "structurel",
    "structural",
    
    # Intensité
    "intensité",
    "intensity",
    "pressing",
    "physique",
    "physical",
    
    # Cohésion
    "cohésion",
    "cohesion",
    "collectif",
    "collective",
    "coordination",
    
    # Dynamique
    "dynamique",
    "dynamics",
    "dynamic",
    "tendance",
    "trend",
    
    # Contrôle
    "contrôle",
    "control",
    "maîtrise",
    "mastery",
    
    # Pression
    "pression",
    "pressure",
    
    # Comportements
    "comportement",
    "behavior",
    "behaviour",
    "signal",
    "signals",
    "pattern",
    "patterns",
    
    # Observation
    "observation",
    "analyse",
    "analysis",
    "lecture",
    "reading",
    
    # Phases
    "phase",
    "phases",
    "domination",
    "recul",
])


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate(text: str) -> None:
    """
    Vérifie que le texte ne contient aucun terme interdit.
    
    ATTENTION: Cette fonction lève une exception si un terme interdit
    est détecté. Aucune auto-correction n'est effectuée.
    
    Args:
        text: Texte à valider.
    
    Raises:
        LexiconGuardError: Si un terme interdit est détecté.
    """
    if text is None:
        return
    
    violations = find_violations(text)
    
    if violations:
        raise LexiconGuardError(violations, text)


def find_violations(text: str) -> List[str]:
    """
    Trouve tous les termes interdits dans un texte.
    
    Utilise des word boundaries pour éviter les faux positifs
    (ex: "Paris" ne doit pas matcher "pari").
    
    Args:
        text: Texte à analyser.
    
    Returns:
        Liste des termes interdits trouvés (sans doublons).
    """
    import re
    
    if not text:
        return []
    
    lowered = text.lower()
    violations = []
    
    for forbidden in BLACKLIST:
        # Utiliser word boundaries pour matcher des mots entiers
        # \b = word boundary
        pattern = r'\b' + re.escape(forbidden) + r'\b'
        if re.search(pattern, lowered):
            if forbidden not in violations:
                violations.append(forbidden)
    
    return violations


def is_clean(text: str) -> bool:
    """
    Vérifie si un texte est propre (aucun terme interdit).
    
    Args:
        text: Texte à vérifier.
    
    Returns:
        True si aucun terme interdit n'est trouvé.
    """
    return len(find_violations(text)) == 0


def is_term_forbidden(term: str) -> bool:
    """
    Vérifie si un terme spécifique est interdit.
    
    Args:
        term: Terme à vérifier.
    
    Returns:
        True si le terme est dans la blacklist.
    """
    return term.lower().strip() in BLACKLIST


def is_term_allowed(term: str) -> bool:
    """
    Vérifie si un terme spécifique est explicitement autorisé.
    
    Args:
        term: Terme à vérifier.
    
    Returns:
        True si le terme est dans la whitelist.
    """
    return term.lower().strip() in WHITELIST


def get_blacklist() -> frozenset:
    """Retourne l'ensemble des termes interdits."""
    return BLACKLIST


def get_whitelist() -> frozenset:
    """Retourne l'ensemble des termes autorisés."""
    return WHITELIST


# =============================================================================
# LEGACY ALIASES (rétrocompatibilité)
# =============================================================================

FORBIDDEN_TERMS = BLACKLIST
ALLOWED_TERMS = WHITELIST

def get_forbidden_terms() -> frozenset:
    """Alias legacy pour get_blacklist()."""
    return BLACKLIST

def get_allowed_terms() -> frozenset:
    """Alias legacy pour get_whitelist()."""
    return WHITELIST


# Alias pour la classe d'exception legacy
LexiconViolationError = LexiconGuardError
