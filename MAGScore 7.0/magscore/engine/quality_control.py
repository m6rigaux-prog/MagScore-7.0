"""
MAGScore 6.3 — Quality Control Engine v1
=========================================
Filet de sécurité interne pour la validation de cohérence.

QualityControlEngine v1 :
    - Détection de contradictions entre comportements (STB, INT, PSY)
    - Validation patterns ↔ behaviors
    - Validation flow ↔ behaviors/patterns
    - Validation du rapport texte (longueur, sections, lexique)
    - Validation du JSON final

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any, List, Set

from magscore.orchestration.lexicon_guard import (
    validate as lexicon_validate,
    LexiconGuardError,
)


# =============================================================================
# VERSION
# =============================================================================

QUALITY_CONTROL_VERSION = "1.0"


# =============================================================================
# CONSTANTES DE VALIDATION
# =============================================================================

# Longueur du rapport
MIN_REPORT_LENGTH = 250
MAX_REPORT_LENGTH = 3000

# Sections obligatoires du rapport (version simplifiée pour matching flexible)
REQUIRED_SECTIONS = [
    "Contexte du match",
    "Indicateurs structurels",
    "Lecture comportementale",
    "Patterns narratifs",
    "Match Flow",
    "Points clés à retenir",
    "Synthèse neutre",
]

# Disclaimer obligatoire
REQUIRED_DISCLAIMER = "[This analysis describes dynamics only and is not a prediction.]"

# Paires de comportements contradictoires
CONTRADICTORY_PAIRS = [
    ("STB_01", "STB_02", "Structural contradiction: STB_01 & STB_02"),
    ("INT_01", "INT_02", "Intensity contradiction: INT_01 & INT_02"),
    ("PSY_01", "PSY_02", "Psychology contradiction: PSY_01 & PSY_02"),
]

# Clés obligatoires dans le payload final
REQUIRED_KEYS = {"behaviors", "patterns", "flow", "report", "meta"}


# =============================================================================
# EXCEPTION
# =============================================================================

class QualityControlError(Exception):
    """
    Exception levée lorsque la validation QC échoue.
    
    Attributes:
        violations: Liste des problèmes détectés.
        category: Catégorie de l'erreur (contradiction, report, pattern, flow, payload).
    """
    
    def __init__(
        self, 
        message: str, 
        violations: List[str] = None, 
        category: str = "general"
    ):
        self.violations = violations or []
        self.category = category
        super().__init__(message)


# =============================================================================
# QUALITY CONTROL ENGINE
# =============================================================================

class QualityControlEngine:
    """
    Moteur de contrôle qualité pour MAGScore.
    
    Valide la cohérence globale du résultat MAGScore avant publication.
    Ce moteur est le dernier rempart de sécurité interne.
    
    Validations effectuées :
        1. Structure du payload JSON final
        2. Rapport texte (longueur, sections, lexique, disclaimer)
        3. Contradictions entre comportements (STB, INT, PSY)
        4. Intégrité des sources de patterns
        5. Cohérence flow ↔ behaviors/patterns
    """
    
    REQUIRED_KEYS = REQUIRED_KEYS
    
    def __init__(self) -> None:
        """Initialise le Quality Control Engine."""
        self._version = QUALITY_CONTROL_VERSION
    
    @property
    def version(self) -> str:
        """Retourne la version du Quality Control Engine."""
        return self._version
    
    def validate(
        self,
        behaviors: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        flow: List[Any],
        report_text: str,
        final_payload: Dict[str, Any]
    ) -> None:
        """
        Valide la cohérence globale du résultat MAGScore.
        
        Ne retourne rien si tout est cohérent.
        Lève QualityControlError si une incohérence critique est détectée.
        
        Args:
            behaviors: Liste des comportements détectés par BehaviorEngine.
            patterns: Liste des patterns détectés par PatternEngine.
            flow: Liste des phases reconstruites par MatchFlowReconstructor.
            report_text: Texte du rapport généré par AnalysisBot.
            final_payload: Payload JSON final complet.
        
        Raises:
            QualityControlError: Si une incohérence est détectée.
        """
        # 1. Valider la structure JSON
        self._check_json_structure(final_payload)
        
        # 2. Valider le rapport texte
        self._check_report(report_text)
        
        # 3. Valider les contradictions de comportements
        self._check_contradictions(behaviors)
        
        # 4. Valider l'intégrité des sources de patterns
        self._check_pattern_sources(behaviors, patterns)
        
        # 5. Valider la cohérence flow ↔ behaviors/patterns
        self._check_flow_coherence(behaviors, patterns, flow)
    
    def _check_json_structure(self, final_payload: Dict[str, Any]) -> None:
        """
        Valide la structure du payload JSON final.
        
        Vérifie que :
            - Toutes les clés obligatoires sont présentes
            - Les types des valeurs sont corrects
        
        Args:
            final_payload: Payload JSON final.
        
        Raises:
            QualityControlError: Si une clé manque ou un type est incorrect.
        """
        # Vérifier les clés manquantes
        missing_keys = self.REQUIRED_KEYS - set(final_payload.keys())
        if missing_keys:
            raise QualityControlError(
                f"Missing required key: {', '.join(sorted(missing_keys))}",
                violations=list(missing_keys),
                category="payload"
            )
        
        # Vérifier les types
        type_checks = [
            ("behaviors", list),
            ("patterns", list),
            ("flow", list),
            ("report", str),
            ("meta", dict),
        ]
        
        for key, expected_type in type_checks:
            value = final_payload.get(key)
            if not isinstance(value, expected_type):
                actual_type = type(value).__name__
                raise QualityControlError(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, got {actual_type}",
                    violations=[key],
                    category="payload"
                )
    
    def _check_report(self, report_text: str) -> None:
        """
        Valide le rapport texte.
        
        Vérifie :
            - Longueur (250-3000 caractères)
            - Présence des 7 sections obligatoires
            - Présence du disclaimer
            - Absence de termes interdits (via LexiconGuard)
        
        Args:
            report_text: Texte du rapport.
        
        Raises:
            QualityControlError: Si le rapport ne respecte pas les contraintes.
        """
        # Vérifier la longueur minimale
        if len(report_text) < MIN_REPORT_LENGTH:
            raise QualityControlError(
                f"Report too short: {len(report_text)} chars (min: {MIN_REPORT_LENGTH})",
                violations=["length"],
                category="report"
            )
        
        # Vérifier la longueur maximale
        if len(report_text) > MAX_REPORT_LENGTH:
            raise QualityControlError(
                f"Report too long: {len(report_text)} chars (max: {MAX_REPORT_LENGTH})",
                violations=["length"],
                category="report"
            )
        
        # Vérifier les sections obligatoires
        missing_sections = []
        for section in REQUIRED_SECTIONS:
            if section not in report_text:
                missing_sections.append(section)
        
        if missing_sections:
            raise QualityControlError(
                f"Missing section: {', '.join(missing_sections)}",
                violations=missing_sections,
                category="report"
            )
        
        # Vérifier le disclaimer
        if REQUIRED_DISCLAIMER not in report_text:
            raise QualityControlError(
                "Missing disclaimer",
                violations=["disclaimer"],
                category="report"
            )
        
        # Vérifier via LexiconGuard
        try:
            lexicon_validate(report_text)
        except LexiconGuardError as e:
            raise QualityControlError(
                f"Forbidden term detected: {', '.join(e.violations)}",
                violations=e.violations,
                category="lexicon"
            )
    
    def _check_contradictions(self, behaviors: List[Dict[str, Any]]) -> None:
        """
        Valide l'absence de contradictions entre comportements.
        
        Vérifie que les paires contradictoires ne sont pas actives simultanément :
            - STB_01 et STB_02
            - INT_01 et INT_02
            - PSY_01 et PSY_02
        
        Args:
            behaviors: Liste des comportements.
        
        Raises:
            QualityControlError: Si une contradiction est détectée.
        """
        # Extraire les codes actifs
        active_codes: Set[str] = set()
        for behavior in behaviors:
            code = behavior.get("code", "")
            status = behavior.get("status", "ACTIVE")
            
            # Considérer comme actif si status == "ACTIVE" ou si pas de status
            if status == "ACTIVE" or "status" not in behavior:
                active_codes.add(code)
        
        # Vérifier les paires contradictoires
        for code1, code2, error_message in CONTRADICTORY_PAIRS:
            if code1 in active_codes and code2 in active_codes:
                raise QualityControlError(
                    error_message,
                    violations=[code1, code2],
                    category="contradiction"
                )
    
    def _check_pattern_sources(
        self,
        behaviors: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]]
    ) -> None:
        """
        Valide que les sources des patterns existent dans behaviors.
        
        Args:
            behaviors: Liste des comportements.
            patterns: Liste des patterns.
        
        Raises:
            QualityControlError: Si une source de pattern n'existe pas.
        """
        # Récupérer les codes disponibles dans behaviors
        available_codes: Set[str] = {
            b.get("code", "") for b in behaviors
        }
        
        # Vérifier chaque pattern
        for pattern in patterns:
            sources = pattern.get("sources", [])
            for source in sources:
                if source not in available_codes:
                    raise QualityControlError(
                        f"Pattern source not found in behaviors: {source}",
                        violations=[source],
                        category="pattern"
                    )
    
    def _check_flow_coherence(
        self,
        behaviors: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        flow: List[Any]
    ) -> None:
        """
        Valide la cohérence du flow avec behaviors et patterns.
        
        Pour la v1 du QC, on vérifie que les codes mentionnés dans le flow
        (via le champ "codes" si présent) existent dans behaviors ou patterns.
        
        Convention pour les tests :
            Le flow peut être :
            - Une liste de strings (labels simples) → pas de validation structurelle
            - Une liste de dicts avec "codes" → validation des codes
        
        Args:
            behaviors: Liste des comportements.
            patterns: Liste des patterns.
            flow: Liste des phases du flow.
        
        Raises:
            QualityControlError: Si le flow référence un code inconnu.
        """
        # Construire l'ensemble des codes connus
        known_codes: Set[str] = set()
        
        # Ajouter les codes des behaviors
        for behavior in behaviors:
            code = behavior.get("code", "")
            if code:
                known_codes.add(code)
        
        # Ajouter les codes et sources des patterns
        for pattern in patterns:
            pattern_code = pattern.get("pattern_code", "")
            if pattern_code:
                known_codes.add(pattern_code)
            
            sources = pattern.get("sources", [])
            for source in sources:
                known_codes.add(source)
        
        # Vérifier chaque phase du flow
        for phase in flow:
            # Si la phase est un dict avec un champ "codes"
            if isinstance(phase, dict):
                phase_codes = phase.get("codes", [])
                for code in phase_codes:
                    if code not in known_codes:
                        raise QualityControlError(
                            f"Flow references unknown code: {code}",
                            violations=[code],
                            category="flow"
                        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_quality_control_engine() -> QualityControlEngine:
    """
    Factory function pour créer un QualityControlEngine.
    
    Returns:
        Instance de QualityControlEngine.
    """
    return QualityControlEngine()
