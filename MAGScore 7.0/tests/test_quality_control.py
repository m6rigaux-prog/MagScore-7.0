"""
MAGScore 6.3 — Tests: Quality Control Engine v1
================================================
Tests fonctionnels pour QualityControlEngine v1 (filet de sécurité interne).

QualityControlEngine v1 :
    - Détection de contradictions entre comportements
    - Validation patterns ↔ behaviors
    - Validation flow ↔ behaviors/patterns
    - Validation du rapport texte (longueur, sections, lexique)
    - Validation du JSON final

Vision : NO CHANCE — ONLY PATTERNS
"""

import pytest

from magscore.engine.quality_control import (
    QualityControlEngine,
    QualityControlError,
    QUALITY_CONTROL_VERSION,
    MIN_REPORT_LENGTH,
    MAX_REPORT_LENGTH,
    REQUIRED_SECTIONS,
    REQUIRED_DISCLAIMER,
    create_quality_control_engine,
)


# =============================================================================
# FIXTURES — ENGINE
# =============================================================================

@pytest.fixture
def qc_engine():
    """Fixture : instance de QualityControlEngine."""
    return QualityControlEngine()


# =============================================================================
# FIXTURES — BEHAVIORS
# =============================================================================

@pytest.fixture
def behaviors_valid():
    """Comportements valides sans contradiction."""
    return [
        {
            "code": "STB_01",
            "label": "Effondrement Structurel",
            "category": "stability",
            "intensity": 0.75,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
        {
            "code": "PSY_01",
            "label": "Frustration Active",
            "category": "psychology",
            "intensity": 0.8,
            "time_slice": "last_15_min",
            "status": "ACTIVE",
        },
    ]


@pytest.fixture
def behaviors_stb_contradiction():
    """Contradiction STB_01 et STB_02 actifs simultanément."""
    return [
        {"code": "STB_01", "status": "ACTIVE"},
        {"code": "STB_02", "status": "ACTIVE"},
    ]


@pytest.fixture
def behaviors_int_contradiction():
    """Contradiction INT_01 et INT_02 actifs simultanément."""
    return [
        {"code": "INT_01", "status": "ACTIVE"},
        {"code": "INT_02", "status": "ACTIVE"},
    ]


@pytest.fixture
def behaviors_psy_contradiction():
    """Contradiction PSY_01 et PSY_02 actifs simultanément."""
    return [
        {"code": "PSY_01", "status": "ACTIVE"},
        {"code": "PSY_02", "status": "ACTIVE"},
    ]


@pytest.fixture
def behaviors_empty():
    """Liste de comportements vide (match neutre)."""
    return []


# =============================================================================
# FIXTURES — PATTERNS
# =============================================================================

@pytest.fixture
def patterns_valid(behaviors_valid):
    """Patterns valides correspondant aux behaviors."""
    return [
        {
            "pattern_code": "PTN_01",
            "label": "Perte de contrôle sous pression",
            "sources": ["STB_01", "PSY_01"],
            "category": "composite",
        }
    ]


@pytest.fixture
def patterns_invalid_sources():
    """Pattern avec sources non présentes dans behaviors."""
    return [
        {
            "pattern_code": "PTN_01",
            "label": "Perte de contrôle sous pression",
            "sources": ["STB_01", "PSY_01", "INT_02"],  # INT_02 non présent
            "category": "composite",
        }
    ]


@pytest.fixture
def patterns_empty():
    """Liste de patterns vide."""
    return []


# =============================================================================
# FIXTURES — FLOW
# =============================================================================

@pytest.fixture
def flow_valid():
    """Flow valide (liste de strings simples)."""
    return [
        "Phase 1 : Stabilisation initiale",
        "Phase 2 : Effondrement défensif final",
    ]


@pytest.fixture
def flow_with_codes_valid():
    """Flow structuré avec codes valides."""
    return [
        {"label": "Phase 1 - Effondrement", "codes": ["STB_01"]},
        {"label": "Phase 2 - Frustration", "codes": ["PSY_01"]},
    ]


@pytest.fixture
def flow_with_unknown_codes():
    """Flow structuré avec codes inconnus."""
    return [
        {"label": "Phase 1 - Test", "codes": ["UNKNOWN_CODE"]},
    ]


# =============================================================================
# FIXTURES — REPORTS
# =============================================================================

@pytest.fixture
def report_valid():
    """Rapport valide avec toutes les sections et longueur correcte."""
    return """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1

2) Indicateurs structurels
Les indicateurs montrent une dynamique particulière dans ce match.

3) Lecture comportementale
L'analyse comportementale révèle des patterns intéressants.

4) Patterns narratifs
PTN_01 : Perte de contrôle sous pression détecté.

5) Match Flow
Phase 1 : Stabilisation initiale
Phase 2 : Effondrement défensif final

6) Points clés à retenir
- Observation de la dynamique structurelle
- Analyse des comportements

7) Synthèse neutre
Cette analyse décrit uniquement les dynamiques observées.

[This analysis describes dynamics only and is not a prediction.]
"""


@pytest.fixture
def report_with_forbidden_word():
    """Rapport contenant un mot interdit (pari)."""
    return """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1

2) Indicateurs structurels
Ce match est un bon pari pour les observateurs.

3) Lecture comportementale
L'analyse comportementale révèle des patterns.

4) Patterns narratifs
Aucun pattern détecté.

5) Match Flow
Phase 1 : Stabilisation
Phase 2 : Phase finale

6) Points clés à retenir
- Points d'observation

7) Synthèse neutre
Analyse neutre.

[This analysis describes dynamics only and is not a prediction.]
"""


@pytest.fixture
def report_too_short():
    """Rapport trop court (< 250 caractères)."""
    return "1) Contexte\nMatch\n2) Indicateurs\nOK\n3) Lecture\nRAS"


@pytest.fixture
def report_too_long():
    """Rapport trop long (> 3000 caractères)."""
    base_text = """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1. Ce match oppose deux équipes.

2) Indicateurs structurels
Les indicateurs structurels montrent une dynamique particulière.

3) Lecture comportementale
L'analyse comportementale révèle des patterns intéressants.

4) Patterns narratifs
Aucun pattern composite détecté dans ce match.

5) Match Flow
Phase 1 : Stabilisation initiale
Phase 2 : Phase finale

6) Points clés à retenir
- Observation de la dynamique structurelle
- Analyse des comportements

7) Synthèse neutre
Cette analyse décrit uniquement les dynamiques observées.
"""
    # Répéter pour dépasser 3000 caractères
    return (base_text * 10) + "\n[This analysis describes dynamics only and is not a prediction.]"


@pytest.fixture
def report_missing_sections():
    """Rapport incomplet (sections manquantes)."""
    return """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1

3) Lecture comportementale
Analyse des comportements. Voici une analyse détaillée du match.

7) Synthèse neutre
Synthèse de l'analyse comportementale du match.

[This analysis describes dynamics only and is not a prediction.]
""" + ("x" * 200)  # Padding pour atteindre longueur minimale


@pytest.fixture
def report_missing_disclaimer():
    """Rapport sans disclaimer."""
    return """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1

2) Indicateurs structurels
Les indicateurs montrent une dynamique particulière.

3) Lecture comportementale
L'analyse comportementale révèle des patterns intéressants.

4) Patterns narratifs
Aucun pattern détecté.

5) Match Flow
Phase 1 : Stabilisation
Phase 2 : Phase finale

6) Points clés à retenir
- Observation de la dynamique

7) Synthèse neutre
Cette analyse décrit uniquement les dynamiques observées.
"""


# =============================================================================
# FIXTURES — FINAL PAYLOAD
# =============================================================================

@pytest.fixture
def payload_valid(behaviors_valid, patterns_valid, flow_valid, report_valid):
    """Payload final valide avec toutes les clés."""
    return {
        "behaviors": behaviors_valid,
        "patterns": patterns_valid,
        "flow": flow_valid,
        "report": report_valid,
        "meta": {
            "pipeline_version": "2.6",
            "quality_control_version": "1.0",
        }
    }


@pytest.fixture
def payload_missing_keys():
    """Payload final avec des clés manquantes."""
    return {
        "behaviors": [],
        "patterns": [],
        # "flow" manquant
        # "report" manquant
        "meta": {}
    }


@pytest.fixture
def payload_wrong_types():
    """Payload avec types incorrects."""
    return {
        "behaviors": "should be list",  # Wrong type
        "patterns": [],
        "flow": [],
        "report": "",
        "meta": {}
    }


@pytest.fixture
def payload_neutral_match():
    """Payload pour un match neutre (behaviors vide mais rapport structuré)."""
    neutral_report = """
1) Contexte du match
Paris FC vs Lyon United - Ligue 1

2) Indicateurs structurels
Les indicateurs ne montrent pas de dynamique marquante.

3) Lecture comportementale
Aucun comportement significatif détecté.

4) Patterns narratifs
Aucun pattern composite identifié.

5) Match Flow
Phase 1 : Stabilisation
Phase 2 : Phase finale

6) Points clés à retenir
- Match équilibré sans signal fort

7) Synthèse neutre
Ce match présente une dynamique neutre sans comportement marquant.

[This analysis describes dynamics only and is not a prediction.]
"""
    return {
        "behaviors": [],
        "patterns": [],
        "flow": ["Phase 1 : Stabilisation", "Phase 2 : Phase finale"],
        "report": neutral_report,
        "meta": {"pipeline_version": "2.6"}
    }


# =============================================================================
# TESTS: ENGINE INSTANTIATION
# =============================================================================

class TestQualityControlEngineInstantiation:
    """Tests d'instanciation du QualityControlEngine."""
    
    def test_qc_engine_instantiation(self):
        """QualityControlEngine peut être instancié."""
        qc = QualityControlEngine()
        assert qc is not None
    
    def test_qc_error_exception_exists(self):
        """QualityControlError est une sous-classe de Exception."""
        assert issubclass(QualityControlError, Exception)
    
    def test_validate_method_exists(self, qc_engine):
        """La méthode validate existe et est callable."""
        assert hasattr(qc_engine, 'validate')
        assert callable(qc_engine.validate)
    
    def test_factory_function(self):
        """Factory function crée une instance."""
        qc = create_quality_control_engine()
        assert isinstance(qc, QualityControlEngine)
    
    def test_version(self, qc_engine):
        """La version est correcte."""
        assert qc_engine.version == "1.0"
        assert QUALITY_CONTROL_VERSION == "1.0"


# =============================================================================
# TESTS: CONTRADICTIONS COMPORTEMENTS — STB
# =============================================================================

class TestContradictionSTB:
    """Tests de contradiction entre STB_01 et STB_02."""
    
    def test_contradiction_stb(self, qc_engine, behaviors_stb_contradiction, report_valid):
        """STB_01 et STB_02 actifs simultanément → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors_stb_contradiction,
                patterns=[],
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors_stb_contradiction,
                    "patterns": [],
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "STB" in str(exc_info.value)


# =============================================================================
# TESTS: CONTRADICTIONS COMPORTEMENTS — INT
# =============================================================================

class TestContradictionINT:
    """Tests de contradiction entre INT_01 et INT_02."""
    
    def test_contradiction_int(self, qc_engine, behaviors_int_contradiction, report_valid):
        """INT_01 et INT_02 simultanés → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors_int_contradiction,
                patterns=[],
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors_int_contradiction,
                    "patterns": [],
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "INT" in str(exc_info.value)


# =============================================================================
# TESTS: CONTRADICTIONS COMPORTEMENTS — PSY
# =============================================================================

class TestContradictionPSY:
    """Tests de contradiction entre PSY_01 et PSY_02."""
    
    def test_contradiction_psy(self, qc_engine, behaviors_psy_contradiction, report_valid):
        """PSY_01 et PSY_02 simultanés → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors_psy_contradiction,
                patterns=[],
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors_psy_contradiction,
                    "patterns": [],
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "PSY" in str(exc_info.value)


# =============================================================================
# TESTS: PATTERNS ↔ BEHAVIORS
# =============================================================================

class TestPatternBehaviorValidation:
    """Tests de validation patterns ↔ behaviors."""
    
    def test_invalid_pattern_sources_fail(
        self, qc_engine, behaviors_valid, patterns_invalid_sources, report_valid
    ):
        """Pattern avec sources non présentes → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors_valid,
                patterns=patterns_invalid_sources,
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors_valid,
                    "patterns": patterns_invalid_sources,
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "source" in str(exc_info.value).lower() or "INT_02" in str(exc_info.value)
    
    def test_valid_pattern_sources_pass(
        self, qc_engine, behaviors_valid, patterns_valid, report_valid
    ):
        """Pattern avec sources valides → pas d'erreur."""
        # Ne doit pas lever d'exception
        qc_engine.validate(
            behaviors=behaviors_valid,
            patterns=patterns_valid,
            flow=[],
            report_text=report_valid,
            final_payload={
                "behaviors": behaviors_valid,
                "patterns": patterns_valid,
                "flow": [],
                "report": report_valid,
                "meta": {},
            },
        )


# =============================================================================
# TESTS: FLOW ↔ BEHAVIORS / PATTERNS
# =============================================================================

class TestFlowValidation:
    """Tests de validation flow ↔ behaviors/patterns."""
    
    def test_flow_with_valid_codes_pass(
        self, qc_engine, behaviors_valid, flow_with_codes_valid, report_valid
    ):
        """Flow avec codes valides → pas d'erreur."""
        qc_engine.validate(
            behaviors=behaviors_valid,
            patterns=[],
            flow=flow_with_codes_valid,
            report_text=report_valid,
            final_payload={
                "behaviors": behaviors_valid,
                "patterns": [],
                "flow": flow_with_codes_valid,
                "report": report_valid,
                "meta": {},
            },
        )
    
    def test_flow_with_unknown_codes_fail(
        self, qc_engine, behaviors_valid, flow_with_unknown_codes, report_valid
    ):
        """Flow avec codes inconnus → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors_valid,
                patterns=[],
                flow=flow_with_unknown_codes,
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors_valid,
                    "patterns": [],
                    "flow": flow_with_unknown_codes,
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "UNKNOWN_CODE" in str(exc_info.value) or "flow" in str(exc_info.value).lower()
    
    def test_flow_simple_strings_pass(
        self, qc_engine, behaviors_valid, flow_valid, report_valid
    ):
        """Flow avec strings simples (sans codes) → pas de validation structurelle."""
        qc_engine.validate(
            behaviors=behaviors_valid,
            patterns=[],
            flow=flow_valid,
            report_text=report_valid,
            final_payload={
                "behaviors": behaviors_valid,
                "patterns": [],
                "flow": flow_valid,
                "report": report_valid,
                "meta": {},
            },
        )


# =============================================================================
# TESTS: RAPPORT TEXTE — LEXICON GUARD INTEGRATION
# =============================================================================

class TestLexiconGuardIntegration:
    """Tests d'intégration avec LexiconGuard."""
    
    def test_lexicon_guard_integration(self, qc_engine, report_with_forbidden_word):
        """Rapport avec mot interdit → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text=report_with_forbidden_word,
                final_payload={
                    "behaviors": [],
                    "patterns": [],
                    "flow": [],
                    "report": report_with_forbidden_word,
                    "meta": {},
                },
            )
        assert "pari" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()


# =============================================================================
# TESTS: RAPPORT TEXTE — LONGUEUR
# =============================================================================

class TestReportLength:
    """Tests de longueur du rapport."""
    
    def test_report_too_short_fails(self, qc_engine, report_too_short):
        """Rapport < 250 caractères → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text=report_too_short,
                final_payload={
                    "behaviors": [],
                    "patterns": [],
                    "flow": [],
                    "report": report_too_short,
                    "meta": {},
                },
            )
        assert "short" in str(exc_info.value).lower() or "250" in str(exc_info.value)
    
    def test_report_too_long_fails(self, qc_engine, report_too_long):
        """Rapport > 3000 caractères → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text=report_too_long,
                final_payload={
                    "behaviors": [],
                    "patterns": [],
                    "flow": [],
                    "report": report_too_long,
                    "meta": {},
                },
            )
        assert "long" in str(exc_info.value).lower() or "3000" in str(exc_info.value)
    
    def test_report_length_constants(self):
        """Vérifier les constantes de longueur."""
        assert MIN_REPORT_LENGTH == 250
        assert MAX_REPORT_LENGTH == 3000


# =============================================================================
# TESTS: RAPPORT TEXTE — SECTIONS
# =============================================================================

class TestReportSections:
    """Tests des sections du rapport."""
    
    def test_missing_sections_fail(self, qc_engine, report_missing_sections):
        """Rapport sans toutes les sections → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text=report_missing_sections,
                final_payload={
                    "behaviors": [],
                    "patterns": [],
                    "flow": [],
                    "report": report_missing_sections,
                    "meta": {},
                },
            )
        assert "section" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()
    
    def test_valid_sections_pass(self, qc_engine, report_valid):
        """Rapport avec toutes les sections → pas d'erreur."""
        qc_engine.validate(
            behaviors=[],
            patterns=[],
            flow=[],
            report_text=report_valid,
            final_payload={
                "behaviors": [],
                "patterns": [],
                "flow": [],
                "report": report_valid,
                "meta": {},
            },
        )
    
    def test_required_sections_list(self):
        """Vérifier la liste des sections obligatoires."""
        assert len(REQUIRED_SECTIONS) == 7
        assert "Contexte du match" in REQUIRED_SECTIONS
        assert "Synthèse neutre" in REQUIRED_SECTIONS


# =============================================================================
# TESTS: RAPPORT TEXTE — DISCLAIMER
# =============================================================================

class TestReportDisclaimer:
    """Tests du disclaimer du rapport."""
    
    def test_missing_disclaimer_fails(self, qc_engine, report_missing_disclaimer):
        """Rapport sans disclaimer → QC doit lever une erreur."""
        # Ajouter du padding pour atteindre la longueur minimale
        padded_report = report_missing_disclaimer + ("x" * 100)
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text=padded_report,
                final_payload={
                    "behaviors": [],
                    "patterns": [],
                    "flow": [],
                    "report": padded_report,
                    "meta": {},
                },
            )
        assert "disclaimer" in str(exc_info.value).lower()
    
    def test_disclaimer_constant(self):
        """Vérifier la constante disclaimer."""
        assert REQUIRED_DISCLAIMER == "[This analysis describes dynamics only and is not a prediction.]"


# =============================================================================
# TESTS: JSON FINAL
# =============================================================================

class TestFinalPayloadValidation:
    """Tests de validation du payload JSON final."""
    
    def test_invalid_json_fails(self, qc_engine, payload_missing_keys):
        """Payload sans clés obligatoires → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=payload_missing_keys.get("behaviors", []),
                patterns=payload_missing_keys.get("patterns", []),
                flow=payload_missing_keys.get("flow", []),
                report_text=payload_missing_keys.get("report", ""),
                final_payload=payload_missing_keys,
            )
        assert "missing" in str(exc_info.value).lower() or "key" in str(exc_info.value).lower()
    
    def test_wrong_types_fail(self, qc_engine, payload_wrong_types):
        """Payload avec types incorrects → QC doit lever une erreur."""
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=[],
                patterns=[],
                flow=[],
                report_text="",
                final_payload=payload_wrong_types,
            )
        assert "type" in str(exc_info.value).lower() or "behaviors" in str(exc_info.value).lower()
    
    def test_empty_behaviors_allowed(self, qc_engine, payload_neutral_match):
        """Match neutre (behaviors vide) → QC doit accepter."""
        qc_engine.validate(
            behaviors=payload_neutral_match["behaviors"],
            patterns=payload_neutral_match["patterns"],
            flow=payload_neutral_match["flow"],
            report_text=payload_neutral_match["report"],
            final_payload=payload_neutral_match,
        )
    
    def test_valid_payload_passes(self, qc_engine, payload_valid):
        """Payload complet et cohérent → pas d'erreur."""
        qc_engine.validate(
            behaviors=payload_valid["behaviors"],
            patterns=payload_valid["patterns"],
            flow=payload_valid["flow"],
            report_text=payload_valid["report"],
            final_payload=payload_valid,
        )


# =============================================================================
# TESTS ADDITIONNELS: EDGE CASES
# =============================================================================

class TestQualityControlEdgeCases:
    """Tests des cas limites pour QualityControlEngine."""
    
    def test_multiple_contradictions_detected(self, qc_engine, report_valid):
        """Plusieurs contradictions → au moins la première déclenche l'erreur."""
        combined = [
            {"code": "STB_01", "status": "ACTIVE"},
            {"code": "STB_02", "status": "ACTIVE"},
            {"code": "INT_01", "status": "ACTIVE"},
            {"code": "INT_02", "status": "ACTIVE"},
        ]
        with pytest.raises(QualityControlError):
            qc_engine.validate(
                behaviors=combined,
                patterns=[],
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": combined,
                    "patterns": [],
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
    
    def test_behavior_without_status_treated_as_active(self, qc_engine, report_valid):
        """Comportement sans status → considéré comme ACTIVE."""
        behaviors = [
            {"code": "STB_01"},  # Pas de status
            {"code": "STB_02"},  # Pas de status
        ]
        with pytest.raises(QualityControlError) as exc_info:
            qc_engine.validate(
                behaviors=behaviors,
                patterns=[],
                flow=[],
                report_text=report_valid,
                final_payload={
                    "behaviors": behaviors,
                    "patterns": [],
                    "flow": [],
                    "report": report_valid,
                    "meta": {},
                },
            )
        assert "STB" in str(exc_info.value)
    
    def test_inactive_behaviors_ignored_in_contradiction(self, qc_engine, report_valid):
        """Comportements INACTIVE ne déclenchent pas de contradiction."""
        behaviors = [
            {"code": "STB_01", "status": "ACTIVE"},
            {"code": "STB_02", "status": "INACTIVE"},  # Inactif
        ]
        # Ne doit pas lever d'exception
        qc_engine.validate(
            behaviors=behaviors,
            patterns=[],
            flow=[],
            report_text=report_valid,
            final_payload={
                "behaviors": behaviors,
                "patterns": [],
                "flow": [],
                "report": report_valid,
                "meta": {},
            },
        )
    
    def test_empty_patterns_with_empty_behaviors_pass(self, qc_engine, report_valid):
        """Patterns vides avec behaviors vides → pas d'erreur."""
        qc_engine.validate(
            behaviors=[],
            patterns=[],
            flow=[],
            report_text=report_valid,
            final_payload={
                "behaviors": [],
                "patterns": [],
                "flow": [],
                "report": report_valid,
                "meta": {},
            },
        )
    
    def test_qc_error_has_violations_attribute(self):
        """QualityControlError a l'attribut violations."""
        error = QualityControlError("test", violations=["v1", "v2"], category="test")
        assert error.violations == ["v1", "v2"]
        assert error.category == "test"
    
    def test_pattern_code_also_valid_in_flow(self, qc_engine, report_valid):
        """Les pattern_codes sont aussi valides dans le flow."""
        behaviors = [{"code": "STB_01", "status": "ACTIVE"}]
        patterns = [{"pattern_code": "PTN_01", "sources": ["STB_01"]}]
        flow = [{"label": "Phase test", "codes": ["PTN_01"]}]
        
        qc_engine.validate(
            behaviors=behaviors,
            patterns=patterns,
            flow=flow,
            report_text=report_valid,
            final_payload={
                "behaviors": behaviors,
                "patterns": patterns,
                "flow": flow,
                "report": report_valid,
                "meta": {},
            },
        )
