"""
MAGScore 7.0 — Analysis Bot v3.2
=================================
Conforme Constitution-MAGScore Section 3.
Génère un rapport d'analyse neutre basé sur l'état comportemental.

Règles :
- Ton neutre, clair, professionnel
- Aucun style émotionnel, aucune validation
- Aucun conseil, aucune orientation de décision
- Aucune référence bookmaker
- Disclaimer obligatoire à la fin

Structure imposée (7 sections) :
    1. Contexte du match
    2. Indicateurs structurels
    3. Lecture comportementale
    4. Patterns narratifs (+ contexte historique 7.0)
    5. Match Flow
    6. Points clés
    7. Synthèse neutre + disclaimer

Nouveautés v3.2 (MAGScore 7.0) :
    - Support du contexte historique
    - Peut dire "Historiquement, cette équipe réagit par [Pattern X]"
    - JAMAIS "Ils ont gagné le dernier match comme ça"
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class AnalysisBot:
    """
    Génère un rapport d'analyse neutre basé sur l'état comportemental.
    
    Structure imposée (Constitution 3.1 + v3.2) :
        1. Contexte du match
        2. Indicateurs structurels
        3. Lecture comportementale
        4. Patterns narratifs (+ contexte historique)
        5. Match Flow
        6. Points clés
        7. Synthèse neutre + disclaimer obligatoire
    
    Nouveautés v3.2 :
        - Support du contexte historique (MemoryEngine)
        - AUTORISÉ: "Historiquement, cette équipe réagit par [Pattern X]"
        - INTERDIT: "Ils ont gagné le dernier match comme ça"
    
    Disclaimer obligatoire :
        "This analysis describes dynamics only and is not a prediction."
    
    Lexique autorisé : stabilité, intensité, cohésion, dynamique, contrôle, pression
    Lexique interdit : favori, probabilité, value, pari, cote, etc.
    """
    
    DISCLAIMER = "This analysis describes dynamics only and is not a prediction."
    VERSION = "3.2"
    
    # Mapping des codes comportements vers descriptions neutres
    BEHAVIOR_DESCRIPTIONS = {
        "STB_01": "structural instability detected in defensive organization",
        "STB_02": "defensive structure maintained with discipline",
        "INT_01": "increased pressing intensity observed",
        "INT_02": "physical decline indicators present",
        "PSY_01": "signs of collective frustration detected",
        "PSY_02": "resilience patterns observed under pressure",
        "AMBIGU_STB": "conflicting stability signals detected",
        "AMBIGU_INT": "conflicting intensity signals detected",
        "AMBIGU_PSY": "conflicting psychological signals detected",
    }
    
    # Mapping catégories vers noms affichables
    CATEGORY_LABELS = {
        "stability": "Structural Stability",
        "intensity": "Physical Intensity",
        "psychology": "Psychological State",
    }
    
    def __init__(self) -> None:
        """Initialise l'AnalysisBot."""
        pass
    
    def generate_report(
        self, 
        metadata: Dict[str, Any], 
        behavior_state: Dict[str, Any],
        patterns: Optional[List[Dict[str, Any]]] = None,
        flow: Optional[List[str]] = None,
        historical_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Génère un rapport d'analyse structuré à partir des métadonnées,
        de l'état comportemental, des patterns et du flow.
        
        Args:
            metadata: Informations sur le match.
                      {
                          "home_team": str,
                          "away_team": str,
                          "competition": str (optionnel),
                          "kickoff_time": str (optionnel),
                      }
            behavior_state: État comportemental provenant du BehaviorEngine v2.3.
                           {
                               "behaviors": List[Dict],
                               "meta": Dict
                           }
            patterns: Liste des patterns composites.
                      [{"pattern_code": str, "label": str, "sources": List}, ...]
            flow: Chronologie du match.
                  ["Phase 1 : ...", "Phase 2 : ...", ...]
            historical_context: Contexte historique de la mémoire (7.0).
                               {
                                   "total_episodes": int,
                                   "pattern_tendencies": Dict[str, float],
                                   "vs_style": {...}
                               }
        
        Returns:
            Rapport textuel structuré en 7 sections.
        """
        # Valeurs par défaut
        if patterns is None:
            patterns = []
        if flow is None:
            flow = []
        if historical_context is None:
            historical_context = {}
        
        # Extraire les données
        home_team = metadata.get("home_team", "Team A")
        away_team = metadata.get("away_team", "Team B")
        competition = metadata.get("competition", "")
        kickoff = metadata.get("kickoff_time", "")
        
        behaviors = behavior_state.get("behaviors", [])
        meta = behavior_state.get("meta", {})
        
        # Construire les 7 sections
        section_1 = self._build_context_section(home_team, away_team, competition, kickoff)
        section_2 = self._build_structural_section(behaviors)
        section_3 = self._build_behavioral_section(behaviors, home_team, away_team)
        section_4 = self._build_patterns_section(patterns, historical_context)
        section_5 = self._build_flow_section(flow)
        section_6 = self._build_key_points_section(behaviors, patterns, home_team, away_team, historical_context)
        section_7 = self._build_synthesis_section(behaviors, patterns, home_team, away_team)
        
        # Assembler le rapport
        report = f"""1) Contexte du match
{section_1}

2) Indicateurs structurels
{section_2}

3) Lecture comportementale
{section_3}

4) Patterns narratifs
{section_4}

5) Match Flow
{section_5}

6) Points clés à retenir
{section_6}

7) Synthèse neutre
{section_7}

[{self.DISCLAIMER}]"""
        
        return report
    
    def _build_context_section(
        self, 
        home_team: str, 
        away_team: str, 
        competition: str,
        kickoff: str
    ) -> str:
        """
        Construit la section 1 : Contexte du match.
        """
        lines = []
        lines.append(f"{home_team} vs {away_team}")
        
        if competition:
            lines.append(f"Competition: {competition}")
        
        if kickoff:
            try:
                if "T" in kickoff:
                    dt = datetime.fromisoformat(kickoff.replace("Z", "+00:00"))
                    lines.append(f"Kickoff: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
                else:
                    lines.append(f"Kickoff: {kickoff}")
            except (ValueError, AttributeError):
                lines.append(f"Kickoff: {kickoff}")
        
        lines.append("This analysis is based on observed behavioral patterns.")
        
        return "\n".join(lines)
    
    def _build_structural_section(self, behaviors: List[Dict[str, Any]]) -> str:
        """
        Construit la section 2 : Indicateurs structurels.
        """
        stability_behaviors = [
            b for b in behaviors 
            if b.get("category") == "stability"
        ]
        
        if not stability_behaviors:
            return "No significant structural indicators detected at this time."
        
        lines = []
        for behavior in stability_behaviors:
            code = behavior.get("code", "")
            status = behavior.get("status", "")
            intensity = behavior.get("intensity")
            time_slice = behavior.get("time_slice", "global")
            
            description = self.BEHAVIOR_DESCRIPTIONS.get(code, "structural pattern observed")
            
            if status == "ACTIVE":
                intensity_text = self._intensity_to_text(intensity)
                time_text = "in final phase" if time_slice == "last_15_min" else "throughout match"
                lines.append(f"- {description.capitalize()} ({intensity_text} intensity, {time_text})")
            elif status == "AMBIGUOUS":
                lines.append(f"- Mixed signals: {description}")
        
        return "\n".join(lines) if lines else "Structural indicators within normal range."
    
    def _build_behavioral_section(
        self, 
        behaviors: List[Dict[str, Any]],
        home_team: str,
        away_team: str
    ) -> str:
        """
        Construit la section 3 : Lecture comportementale.
        """
        if not behaviors:
            return "No significant behavioral patterns detected."
        
        lines = []
        
        # Grouper par catégorie
        by_category: Dict[str, List[Dict]] = {}
        for b in behaviors:
            cat = b.get("category", "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(b)
        
        # Générer le texte par catégorie (ordre: psychology > intensity > stability)
        for category in ["psychology", "intensity", "stability"]:
            if category not in by_category:
                continue
            
            cat_behaviors = by_category[category]
            cat_label = self.CATEGORY_LABELS.get(category, category.capitalize())
            
            lines.append(f"{cat_label}:")
            
            for behavior in cat_behaviors:
                code = behavior.get("code", "")
                status = behavior.get("status", "")
                description = self.BEHAVIOR_DESCRIPTIONS.get(code, "pattern observed")
                
                if status == "ACTIVE":
                    lines.append(f"  - {description.capitalize()}")
                elif status == "AMBIGUOUS":
                    details = behavior.get("details", [])
                    lines.append(f"  - Conflicting signals: {', '.join(details)}")
        
        return "\n".join(lines) if lines else "Behavioral patterns within expected range."
    
    def _build_patterns_section(
        self, 
        patterns: List[Dict[str, Any]],
        historical_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construit la section 4 : Patterns narratifs (v3.2 avec contexte historique).
        
        Args:
            patterns: Liste des patterns composites détectés.
            historical_context: Contexte historique (7.0).
        
        Returns:
            Texte de la section patterns.
        """
        if not patterns:
            return "No composite patterns identified from current behavioral data."
        
        lines = []
        
        # Distinguer les patterns triples, doubles et visuels
        triple_patterns = [p for p in patterns if len(p.get("sources", [])) == 3]
        double_patterns = [
            p for p in patterns 
            if len(p.get("sources", [])) == 2 and p.get("category") == "composite"
        ]
        visual_patterns = [p for p in patterns if p.get("category") == "composite_visual"]
        
        if triple_patterns:
            lines.append("Primary composite patterns (high significance):")
            for pattern in triple_patterns:
                code = pattern.get("pattern_code", "")
                label = pattern.get("label", "Unknown pattern")
                sources = pattern.get("sources", [])
                sources_text = " + ".join(sources) if sources else "N/A"
                lines.append(f"  - {label} ({code})")
                lines.append(f"      Sources: {sources_text}")
        
        if double_patterns:
            if triple_patterns:
                lines.append("")
                lines.append("Secondary composite patterns:")
            else:
                lines.append("Composite patterns identified:")
            
            for pattern in double_patterns:
                code = pattern.get("pattern_code", "")
                label = pattern.get("label", "Unknown pattern")
                sources = pattern.get("sources", [])
                sources_text = " + ".join(sources) if sources else "N/A"
                lines.append(f"  - {label} ({code})")
                lines.append(f"      Sources: {sources_text}")
        
        # Patterns visuels (7.0)
        if visual_patterns:
            lines.append("")
            lines.append("Visual composite patterns:")
            for pattern in visual_patterns:
                code = pattern.get("pattern_code", "")
                label = pattern.get("label", "Unknown pattern")
                sources = pattern.get("sources", [])
                sources_text = " + ".join(sources) if sources else "N/A"
                lines.append(f"  - {label} ({code})")
                lines.append(f"      Sources: {sources_text}")
        
        # Contexte historique (7.0)
        if historical_context and historical_context.get("total_episodes", 0) > 0:
            lines.append("")
            lines.append("Historical context:")
            
            # Tendances de patterns
            tendencies = historical_context.get("pattern_tendencies", {})
            if tendencies:
                # Trouver le pattern le plus fréquent parmi ceux détectés
                current_codes = [p.get("pattern_code", "") for p in patterns]
                for code in current_codes:
                    if code in tendencies:
                        freq = tendencies[code]
                        if freq > 0.3:
                            lines.append(
                                f"  - Historically, this team shows {code} "
                                f"in {int(freq * 100)}% of analyzed matches"
                            )
                            break
            
            # Contexte contre ce style de jeu
            vs_style = historical_context.get("vs_style")
            if vs_style and vs_style.get("common_patterns"):
                style = vs_style.get("opposing_style", "this style")
                common = vs_style["common_patterns"][:2]
                if common:
                    lines.append(
                        f"  - Against {style}, typical responses include: {', '.join(common)}"
                    )
        
        return "\n".join(lines)
    
    def _build_flow_section(self, flow: List[str]) -> str:
        """
        Construit la section 5 : Match Flow (v3.1 amélioré).
        
        Args:
            flow: Chronologie du match.
        
        Returns:
            Texte de la section flow.
        """
        if not flow:
            return "Match flow reconstruction not available due to limited behavioral data."
        
        lines = []
        lines.append("Reconstructed match chronology:")
        
        # Le flow contient déjà les phases numérotées
        for phase in flow:
            lines.append(f"  {phase}")
        
        return "\n".join(lines)
    
    def _build_key_points_section(
        self, 
        behaviors: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        home_team: str,
        away_team: str,
        historical_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construit la section 6 : Points clés (v3.2 avec contexte historique).
        """
        points = []
        
        # Point 1: Pattern le plus significatif ou comportement dominant
        triple_patterns = [p for p in patterns if len(p.get("sources", [])) == 3]
        
        if triple_patterns:
            main_pattern = triple_patterns[0]
            label = main_pattern.get("label", "pattern detected")
            points.append(f"Primary narrative: {label} (high significance)")
        elif patterns:
            main_pattern = patterns[0]
            label = main_pattern.get("label", "pattern detected")
            points.append(f"Primary narrative: {label}")
        else:
            active_behaviors = [b for b in behaviors if b.get("status") == "ACTIVE"]
            if active_behaviors:
                sorted_behaviors = sorted(
                    active_behaviors, 
                    key=lambda x: x.get("intensity", 0) or 0,
                    reverse=True
                )
                top_behavior = sorted_behaviors[0]
                code = top_behavior.get("code", "")
                description = self.BEHAVIOR_DESCRIPTIONS.get(code, "pattern")
                points.append(f"Primary observation: {description}")
            else:
                points.append("No dominant behavioral pattern detected")
        
        # Point 2: Money Time indicator
        last_15_behaviors = [
            b for b in behaviors 
            if b.get("time_slice") == "last_15_min" and b.get("status") == "ACTIVE"
        ]
        if last_15_behaviors:
            codes = [b.get("code", "") for b in last_15_behaviors]
            points.append(f"Final phase indicators: {', '.join(codes)}")
        else:
            points.append("No significant final phase patterns detected")
        
        # Point 3: Cohérence narrative ou contexte historique
        if historical_context and historical_context.get("total_episodes", 0) > 2:
            # Contexte historique disponible (7.0)
            vs_style = historical_context.get("vs_style")
            if vs_style and vs_style.get("episodes_count", 0) > 0:
                points.append(
                    f"Historical data available: {vs_style['episodes_count']} "
                    f"similar matches analyzed"
                )
            else:
                points.append(
                    f"Historical data available: {historical_context['total_episodes']} "
                    f"matches in memory"
                )
        elif len(patterns) > 1:
            points.append("Multiple narrative patterns suggest complex dynamics")
        elif len(patterns) == 1:
            points.append("Clear narrative pattern identified")
        else:
            ambiguous = [b for b in behaviors if b.get("status") == "AMBIGUOUS"]
            if ambiguous:
                points.append("Mixed signals require careful interpretation")
            else:
                active_count = len([b for b in behaviors if b.get("status") == "ACTIVE"])
                if active_count >= 2:
                    points.append("Consistent behavioral indicators detected")
                else:
                    points.append("Limited behavioral signals detected")
        
        return "\n".join([f"- {p}" for p in points])
    
    def _build_synthesis_section(
        self, 
        behaviors: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        home_team: str,
        away_team: str
    ) -> str:
        """
        Construit la section 7 : Synthèse neutre.
        """
        active_count = len([b for b in behaviors if b.get("status") == "ACTIVE"])
        ambiguous_count = len([b for b in behaviors if b.get("status") == "AMBIGUOUS"])
        pattern_count = len(patterns)
        triple_count = len([p for p in patterns if len(p.get("sources", [])) == 3])
        
        lines = []
        
        if active_count == 0 and ambiguous_count == 0 and pattern_count == 0:
            lines.append(
                f"The match between {home_team} and {away_team} shows no significant "
                "behavioral patterns at this time. Both teams appear to be operating "
                "within normal parameters."
            )
        elif triple_count > 0:
            # v3.1: Mentionner les patterns triples avec emphase
            triple_labels = [
                p.get("label", "") for p in patterns 
                if len(p.get("sources", [])) == 3
            ][:2]
            if len(triple_labels) == 1:
                lines.append(
                    f"The analysis identifies a significant composite pattern: {triple_labels[0]}. "
                    "This pattern combines multiple behavioral dimensions."
                )
            else:
                lines.append(
                    f"The analysis reveals complex dynamics: {' and '.join(triple_labels)}. "
                    "These patterns indicate interconnected behavioral factors."
                )
        elif pattern_count > 0:
            # Mentionner les patterns doubles
            pattern_labels = [p.get("label", "") for p in patterns[:2]]
            if len(pattern_labels) == 1:
                lines.append(
                    f"The analysis identifies a clear narrative pattern: {pattern_labels[0]}."
                )
            else:
                lines.append(
                    f"The analysis reveals multiple dynamics: {' and '.join(pattern_labels)}."
                )
        elif ambiguous_count > 0:
            lines.append(
                "The analysis reveals conflicting signals that prevent definitive "
                "conclusions. The behavioral state remains unclear and may evolve."
            )
        else:
            # Résumer par catégorie
            categories_present = set(b.get("category") for b in behaviors if b.get("status") == "ACTIVE")
            
            if "psychology" in categories_present:
                lines.append("Psychological factors appear influential in current dynamics.")
            if "intensity" in categories_present:
                lines.append("Physical intensity levels show notable patterns.")
            if "stability" in categories_present:
                lines.append("Structural organization displays observable trends.")
        
        lines.append(
            "This analysis describes observed dynamics without implying any outcome."
        )
        
        return " ".join(lines)
    
    def _intensity_to_text(self, intensity: Optional[float]) -> str:
        """
        Convertit une valeur d'intensité en texte descriptif.
        """
        if intensity is None:
            return "undefined"
        
        if intensity < 0.5:
            return "low"
        elif intensity < 0.7:
            return "moderate"
        elif intensity < 0.9:
            return "high"
        else:
            return "very high"
