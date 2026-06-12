import logging
import re
from typing import Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)

TEXTILE_KNOWLEDGE = {
    "coton": {
        "definition": "Le coton est une fibre naturelle cellulosique obtenue du cotonnier (Gossypium). C'est une fibre tres utilisee pour les articles d'habillement et de linge de maison.",
        "proprietes": [
            "Absorbant et confortable au porter",
            "Respirant",
            "Facile a teindre",
            "Lavable a temperature moderee a elevee selon l'article",
            "Biodgradable dans des conditions adaptees",
        ],
        "denominations_eu": ["Cotton", "Coton"],
        "code_eu": "CO",
    },
    "polyester": {
        "definition": "Le polyester (PES) est une fibre synthetique, generalement issue du polyethylene terephtalate.",
        "proprietes": [
            "Bonne resistance mecanique",
            "Sechage rapide",
            "Faible froissabilite",
            "Faible absorption d'humidite",
            "Bonne stabilite dimensionnelle",
        ],
        "denominations_eu": ["Polyester"],
        "code_eu": "PES",
    },
    "laine": {
        "definition": "La laine est une fibre proteique naturelle provenant de la toison du mouton ou d'autres animaux autorises selon les denominations applicables.",
        "proprietes": [
            "Thermoregulation naturelle",
            "Bon pouvoir isolant",
            "Elasticite naturelle",
            "Hygroscopicite",
            "Comportement au feu favorable par rapport a beaucoup de fibres synthetiques",
        ],
        "denominations_eu": ["Wool", "Laine"],
        "code_eu": "WO",
    },
    "viscose": {
        "definition": "La viscose est une fibre cellulosique regeneree obtenue par transformation chimique de cellulose.",
        "proprietes": [
            "Toucher souple",
            "Bonne drapabilite",
            "Forte absorption d'humidite",
            "Resistance reduite a l'etat humide",
        ],
        "denominations_eu": ["Viscose"],
        "code_eu": "VI",
    },
    "lin": {
        "definition": "Le lin est une fibre naturelle vegetale extraite des tiges de Linum usitatissimum.",
        "proprietes": [
            "Frais au toucher",
            "Tres bonne resistance",
            "Faible elasticite",
            "Aspect naturellement irregulier",
            "S'ameliore souvent avec les lavages",
        ],
        "denominations_eu": ["Flax", "Lin"],
        "code_eu": "LI",
    },
    "elasthanne": {
        "definition": "L'elasthanne est une fibre synthetique elastomerique, aussi connue sous certains noms commerciaux comme Lycra ou Spandex.",
        "proprietes": [
            "Tres forte extensibilite",
            "Retour elastique eleve",
            "Utilise le plus souvent en melange",
            "Ameliore l'aisance et la tenue du vetement",
        ],
        "denominations_eu": ["Elastane", "Elasthanne"],
        "code_eu": "EL",
    },
}

REGLEMENTATION_EU = """Reglement UE 1007/2011 relatif aux denominations des fibres textiles:
- Article 5 et Annexe I: les denominations de fibres doivent correspondre aux denominations autorisees.
- Article 7: la composition en fibres est indiquee par ordre decroissant de masse.
- Article 9: les produits composes de plusieurs fibres portent le nom et le pourcentage en masse de toutes les fibres constituantes.
- Article 14: l'etiquetage et le marquage doivent etre durables, lisibles, visibles et accessibles.
- Article 16: les informations sont fournies dans la langue officielle de l'Etat membre de mise a disposition, sauf disposition nationale differente.
- Article 20: des tolerances techniques peuvent s'appliquer dans les limites prevues par le reglement."""

REGLEMENTATION_US_FTC = """FTC Textile Fiber Products Identification Act et 16 CFR Part 303:
- La composition doit indiquer les fibres par nom generique et pourcentage en poids.
- Les fibres presentes a moins de 5% peuvent etre designees comme other fiber, sauf si elles ont une signification fonctionnelle.
- Le pays d'origine doit etre indique.
- L'identite du fabricant, distributeur ou vendeur doit etre indiquee, notamment via RN lorsque applicable.
- Les informations doivent etre exactes, lisibles et non trompeuses."""


class LocalLLM:
    """LLM service using Ollama when available, with deterministic textile fallback."""

    _ollama_available: Optional[bool] = None

    @classmethod
    def get_pipeline(cls):
        return None

    _openai_available: Optional[bool] = None

    @classmethod
    def _check_ollama(cls) -> bool:
        if cls._ollama_available is not None:
            return cls._ollama_available
        try:
            import ollama

            ollama.list()
            cls._ollama_available = True
            logger.info("Ollama available; using model %s", settings.LLM_MODEL_ID)
        except Exception as exc:
            cls._ollama_available = False
            logger.warning("Ollama unavailable (%s); fallback mode enabled", exc)
        return cls._ollama_available

    @classmethod
    def _check_openai(cls) -> bool:
        if cls._openai_available is not None:
            return cls._openai_available
        cls._openai_available = bool(settings.OPENAI_API_KEY and settings.USE_OPENAI_LLM)
        return cls._openai_available

    @classmethod
    def _build_system_prompt(cls) -> str:
        return (
            "Tu es TextileBot Pro, expert en reglementation textile internationale. "
            "Tu maitrises le Reglement UE 1007/2011, les regles FTC americaines, "
            "REACH, OEKO-TEX, GOTS et les pratiques de controle qualite textile.\n\n"
            "Regles: si la question concerne le textile, cite les sources disponibles, "
            "separe faits, reserves et recommandations, indique un niveau de confiance. "
            "Si la question ne concerne pas le textile, reponds quand meme normalement "
            "et utilement, comme un assistant generaliste. "
            "Reponds en francais sauf demande contraire."
        )

    @classmethod
    def check_out_of_scope(cls, query: str) -> bool:
        textile_keywords = [
            "textil", "tissu", "fibre", "coton", "polyester", "composition", "etiquet", "etiquette",
            "norme", "reglement", "conform", "laine", "soie", "vetement", "habil", "lin", "chanvre",
            "synthet", "cuir", "lavage", "entretien", "marquage", "securite", "chemise", "pantalon",
            "robe", "manteau", "t-shirt", "veste", "tissage", "fil", "matiere", "viscose", "elasthanne",
            "elastane", "acrylique", "nylon", "polyamide", "modal", "lyocell", "gots", "oeko", "reach",
            "iso", "ftc", "1007", "grammage", "teinture", "certification", "label", "import", "export",
            "douane", "analyse", "made in", "origine",
        ]
        normalized = cls._normalize(query)

        # If the user greets the bot, allow the chat and return a friendly textile-related answer.
        if cls._is_greeting(normalized):
            return False

        return not any(keyword in normalized for keyword in textile_keywords)

    @classmethod
    def _is_greeting(cls, normalized_query: str) -> bool:
        return normalized_query.strip() in {
            "salut", "bonjour", "hello", "hi", "coucou", "hey", "salutation", "bonsoir"
        }

    @classmethod
    def generate_response(
        cls,
        query: str,
        contexts: list[dict],
        system_override: str = None,
    ) -> tuple[str, list[dict]]:
        normalized = cls._normalize(query)

        if cls._is_greeting(normalized):
            return (
                "Bonjour ! Je suis TextileBot, votre assistant spécialisé en conformité textile. "
                "Posez-moi une question sur les fibres, l’étiquetage, les normes ou la réglementation.",
                [],
            )

        if cls._check_openai():
            return cls._generate_with_openai(query, contexts, system_override)
        if cls._check_ollama():
            return cls._generate_with_ollama(query, contexts, system_override)

        if cls.check_out_of_scope(query):
            return (
                "**Hors domaine** - Je suis specialise en conformite, fibres, etiquetage, "
                "normes et documentation textile.\n\n"
                "Je peux par exemple analyser une composition, verifier une etiquette EU/USA, "
                "ou expliquer une exigence reglementaire textile.",
                [],
            )

        return cls._generate_fallback(query, contexts)

    @classmethod
    def _generate_with_openai(
        cls,
        query: str,
        contexts: list[dict],
        system_override: str = None,
    ) -> tuple[str, list[dict]]:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL or None,
            )
            context_text, sources_used = cls._format_contexts(contexts, min_score=0.2, limit=5)
            messages = [
                {"role": "system", "content": system_override or cls._build_system_prompt()},
                {"role": "user", "content": f"{context_text}\nQuestion utilisateur:\n{query}\n\nProduis une reponse professionnelle avec: synthese, justification, sources citees, limites eventuelles et niveau de confiance."},
            ]
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.2,
                top_p=0.9,
            )
            answer = response.choices[0].message.content
            if sources_used and "confiance" not in cls._normalize(answer):
                avg_score = sum(float(s.get("score", 0)) for s in sources_used) / len(sources_used)
                answer += f"\n\n**Confiance:** {cls._confidence_label(avg_score)} ({avg_score:.0%})"
            return answer, sources_used
        except Exception as exc:
            logger.exception("OpenAI generation failed; falling back: %s", exc)
            cls._openai_available = False
            return cls._generate_fallback(query, contexts)

    @classmethod
    def _generate_with_ollama(
        cls,
        query: str,
        contexts: list[dict],
        system_override: str = None,
    ) -> tuple[str, list[dict]]:
        try:
            import ollama

            context_text, sources_used = cls._format_contexts(contexts, min_score=0.2, limit=5)
            prompt = (
                f"{context_text}\n"
                f"Question utilisateur:\n{query}\n\n"
                "Produis une reponse professionnelle avec: synthese, justification, sources citees, "
                "limites eventuelles et niveau de confiance."
            )
            response = ollama.chat(
                model=settings.LLM_MODEL_ID,
                messages=[
                    {"role": "system", "content": system_override or cls._build_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.2, "top_p": 0.9},
            )
            answer = response["message"]["content"]
            if sources_used and "confiance" not in cls._normalize(answer):
                avg_score = sum(float(s.get("score", 0)) for s in sources_used) / len(sources_used)
                answer += f"\n\n**Confiance:** {cls._confidence_label(avg_score)} ({avg_score:.0%})"
            return answer, sources_used
        except Exception as exc:
            logger.exception("Ollama generation failed; falling back: %s", exc)
            cls._ollama_available = False
            return cls._generate_fallback(query, contexts)

    @classmethod
    def _generate_fallback(cls, query: str, contexts: list[dict]) -> tuple[str, list[dict]]:
        query_normalized = cls._normalize(query)
        response_parts: list[str] = []
        sources_used: list[dict] = []

        relevant_contexts = [ctx for ctx in contexts if float(ctx.get("score", 0) or 0) >= 0.18]
        if relevant_contexts:
            response_parts.append("**Synthese issue de vos documents**")
            for ctx in relevant_contexts[:3]:
                excerpt = cls._best_excerpt(query, ctx.get("content") or "")
                if excerpt:
                    response_parts.append(
                        f"- {excerpt}  \n"
                        f"  Source: {ctx.get('filename', 'document')}, chunk {ctx.get('chunk_index', '-')}, "
                        f"score {float(ctx.get('score', 0)):.0%}."
                    )
                    sources_used.append(ctx)

        for fiber_key, fiber_data in TEXTILE_KNOWLEDGE.items():
            names = [fiber_key, *fiber_data.get("denominations_eu", [])]
            if any(cls._normalize(name) in query_normalized for name in names):
                response_parts.append(f"\n**Fiche fibre - {fiber_key.capitalize()}**")
                response_parts.append(fiber_data["definition"])
                response_parts.append("Proprietes principales:")
                response_parts.extend(f"- {prop}" for prop in fiber_data["proprietes"][:4])
                response_parts.append(
                    "Denomination UE (Reglement UE 1007/2011, Annexe I): "
                    + ", ".join(fiber_data["denominations_eu"])
                    + f" ({fiber_data['code_eu']})."
                )
                break

        if any(word in query_normalized for word in ["reglement", "norme", "ue", "europe", "1007", "conform", "etiquet"]):
            response_parts.append("\n**Cadre UE utile**")
            response_parts.append(REGLEMENTATION_EU)
        if any(word in query_normalized for word in ["usa", "americ", "ftc", "rn", "wpl"]):
            response_parts.append("\n**Cadre USA utile**")
            response_parts.append(REGLEMENTATION_US_FTC)

        if response_parts:
            avg_score = sum(float(s.get("score", 0)) for s in sources_used) / len(sources_used) if sources_used else 0.55
            response_parts.append(
                f"\n**Confiance:** {cls._confidence_label(avg_score)} ({avg_score:.0%}).\n"
                "*Mode fallback local: Ollama n'est pas disponible. Pour activer Llama 3.2: "
                "`ollama pull llama3.2:3b`, puis configurez `LLM_MODEL_ID=llama3.2:3b`.*"
            )
            return "\n".join(response_parts), sources_used

        if contexts:
            best = max(contexts, key=lambda item: float(item.get("score", 0) or 0))
            return (
                f"Je n'ai pas assez d'elements pour conclure de facon fiable. "
                f"Extrait le plus proche ({best.get('filename', 'document')}, score {float(best.get('score', 0)):.0%}):\n\n"
                f"{(best.get('content') or '')[:700]}",
                [best],
            )

        return (
            "Aucun document textile indexe n'est disponible pour etayer la reponse. "
            "Importez des reglements, normes, fiches techniques ou procedures qualite pour alimenter le RAG.",
            [],
        )

    @classmethod
    def generate_compliance_analysis(
        cls,
        product_name: str,
        fiber_composition: str,
        intended_market: str,
        label_text: str,
        contexts: list[dict],
    ) -> tuple[str, str, float, list[str]]:
        issues: list[str] = []
        warnings: list[str] = []
        references: list[str] = []

        composition_items = cls._extract_composition_items(fiber_composition)
        label_items = cls._extract_composition_items(label_text or "")
        composition_total = round(sum(item["percent"] for item in composition_items), 2)
        label_total = round(sum(item["percent"] for item in label_items), 2)
        market = cls._normalize(intended_market)

        if not composition_items:
            issues.append("Composition inexploitable: aucun pourcentage de fibre n'a ete detecte.")
        elif abs(composition_total - 100) > 0.5:
            issues.append(f"Somme des pourcentages composition = {composition_total:g}% au lieu de 100%.")
            references.append("Reglement UE 1007/2011, articles 7 et 9")

        if any(item["percent"] <= 0 or item["percent"] > 100 for item in composition_items):
            issues.append("Chaque fibre doit avoir un pourcentage strictement compris entre 0 et 100.")

        if label_text:
            if label_items and abs(label_total - 100) > 0.5:
                issues.append(f"Somme des pourcentages etiquette = {label_total:g}% au lieu de 100%.")
                references.append("Reglement UE 1007/2011, articles 7 et 9")
            elif composition_items and not label_items:
                warnings.append("L'etiquette ne contient pas de pourcentages de fibres clairement detectables.")

            composition_names = {item["fiber"] for item in composition_items}
            label_names = {item["fiber"] for item in label_items}
            if composition_names and label_names:
                missing = composition_names - label_names
                extra = label_names - composition_names
                if missing:
                    issues.append("Fibres manquantes sur l'etiquette: " + ", ".join(sorted(missing)) + ".")
                    references.append("Reglement UE 1007/2011, article 9")
                if extra:
                    warnings.append("Fibres presentes sur l'etiquette mais absentes de la composition declaree: " + ", ".join(sorted(extra)) + ".")
        else:
            warnings.append("Aucun texte d'etiquette fourni: l'analyse porte seulement sur la composition declaree.")

        if any(token in market for token in ["union europeenne", "europe", "ue", "france"]):
            references.extend(["Reglement UE 1007/2011, article 7", "Reglement UE 1007/2011, article 16"])
            percentages = [item["percent"] for item in label_items or composition_items]
            if percentages and percentages != sorted(percentages, reverse=True):
                warnings.append("Les fibres ne semblent pas classees par ordre decroissant de pourcentage.")
            if "france" in market and label_text and not cls._looks_french(label_text):
                warnings.append("Pour la France, l'information consommateur doit etre disponible en francais.")

        if any(token in market for token in ["usa", "etats", "americ", "us "]):
            references.append("FTC Textile Fiber Products Identification Act, 16 CFR Part 303")
            if label_text:
                if "made in" not in cls._normalize(label_text) and "fabrique" not in cls._normalize(label_text):
                    warnings.append("USA: le pays d'origine n'est pas clairement indique sur l'etiquette.")
                if not re.search(r"\bRN\s*\d+|\bWPL\s*\d+", label_text, flags=re.IGNORECASE):
                    warnings.append("USA: l'identite fabricant/distributeur ou le numero RN/WPL n'est pas detecte.")

        if issues:
            status = "non_compliant"
            confidence = 0.92
        elif warnings:
            status = "conditional"
            confidence = 0.78
        else:
            status = "compliant"
            confidence = 0.86

        analysis = cls._build_compliance_text(
            product_name=product_name,
            fiber_composition=fiber_composition,
            intended_market=intended_market,
            label_text=label_text,
            issues=issues,
            warnings=warnings,
            references=references,
            status=status,
            confidence=confidence,
            contexts=contexts,
        )
        return analysis, status, confidence, sorted(set(references))

    @classmethod
    def _build_compliance_text(
        cls,
        product_name,
        fiber_composition,
        intended_market,
        label_text,
        issues,
        warnings,
        references,
        status,
        confidence,
        contexts,
    ) -> str:
        status_label = {
            "compliant": "CONFORME",
            "non_compliant": "NON CONFORME",
            "conditional": "CONFORME AVEC RESERVE",
        }[status]
        lines = [
            f"## Analyse de conformite - {product_name}",
            f"**Statut:** {status_label}",
            f"**Score de confiance:** {confidence:.0%}",
            f"**Marche cible:** {intended_market}",
            "",
            "### Composition analysee",
            f"- Composition declaree: `{fiber_composition}`",
        ]
        if label_text:
            lines.append(f"- Etiquette fournie: `{label_text}`")

        if issues:
            lines.extend(["", "### Non-conformites bloquantes"])
            lines.extend(f"- {issue}" for issue in issues)
        if warnings:
            lines.extend(["", "### Reserves et points de vigilance"])
            lines.extend(f"- {warning}" for warning in warnings)
        if not issues and not warnings:
            lines.extend(["", "### Resultat", "- Aucune anomalie detectee sur les controles automatises."])

        if references:
            lines.extend(["", "### References"])
            lines.extend(f"- {ref}" for ref in sorted(set(references)))

        relevant, _ = cls._format_contexts(contexts, min_score=0.25, limit=2)
        if relevant:
            lines.extend(["", "### Sources documentaires RAG", relevant.replace("DOCUMENTS DE REFERENCE:\n\n", "")])

        lines.extend(["", "---", "*Analyse generee par TextileBot Pro. Validation juridique finale recommandee avant mise sur le marche.*"])
        return "\n".join(lines)

    @classmethod
    def _format_contexts(cls, contexts: list[dict], min_score: float, limit: int) -> tuple[str, list[dict]]:
        selected = [ctx for ctx in contexts if float(ctx.get("score", 0) or 0) >= min_score][:limit]
        parts = []
        for index, ctx in enumerate(selected, start=1):
            parts.append(
                f"[Source {index}: {ctx.get('filename', 'document')}, chunk {ctx.get('chunk_index', '-')}, "
                f"score {float(ctx.get('score', 0)):.0%}]\n{ctx.get('content', '')}"
            )
        if not parts:
            return "", []
        return "DOCUMENTS DE REFERENCE:\n\n" + "\n\n---\n\n".join(parts) + "\n\n", selected

    @classmethod
    def _best_excerpt(cls, query: str, content: str) -> str:
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", content) if len(sentence.strip()) > 30]
        if not sentences:
            return content[:450].strip()
        query_terms = {term for term in re.findall(r"\w+", cls._normalize(query)) if len(term) > 3}
        ranked = sorted(
            sentences,
            key=lambda sentence: len(query_terms.intersection(set(re.findall(r"\w+", cls._normalize(sentence))))),
            reverse=True,
        )
        return ranked[0][:500].strip()

    @staticmethod
    def _confidence_label(score: float) -> str:
        if score >= 0.75:
            return "Elevee"
        if score >= 0.45:
            return "Moyenne"
        return "Faible"

    @staticmethod
    def _normalize(text: str) -> str:
        replacements = str.maketrans({
            "à": "a", "â": "a", "ä": "a", "á": "a",
            "ç": "c",
            "è": "e", "é": "e", "ê": "e", "ë": "e",
            "î": "i", "ï": "i",
            "ô": "o", "ö": "o",
            "ù": "u", "û": "u", "ü": "u",
            "ÿ": "y",
        })
        return (text or "").lower().translate(replacements)

    @classmethod
    def _extract_composition_items(cls, text: str) -> list[dict]:
        if not text:
            return []
        matches = re.finditer(
            r"(?P<pct>\d+(?:[.,]\d+)?)\s*%\s*(?P<fiber>[A-Za-zÀ-ÿ \-]+?)(?=,|;|/|\bet\b|\band\b|\d+(?:[.,]\d+)?\s*%|$)",
            text,
            flags=re.IGNORECASE,
        )
        items = []
        for match in matches:
            fiber = cls._normalize(match.group("fiber")).strip(" .:-")
            fiber = re.sub(r"\s+", " ", fiber)
            if not fiber:
                continue
            try:
                percent = float(match.group("pct").replace(",", "."))
            except ValueError:
                continue
            items.append({"fiber": fiber, "percent": percent})
        return items

    @staticmethod
    def _extract_percentages(text: str) -> list[float]:
        if not text:
            return []
        values = []
        for raw in re.findall(r"(\d+(?:[.,]\d+)?)\s*%", text):
            try:
                values.append(float(raw.replace(",", ".")))
            except ValueError:
                continue
        return values

    @classmethod
    def _extract_fiber_names(cls, text: str) -> list[str]:
        return [item["fiber"] for item in cls._extract_composition_items(text)]

    @classmethod
    def _looks_french(cls, text: str) -> bool:
        normalized = cls._normalize(text)
        return any(word in normalized for word in ["coton", "laine", "lin", "polyester", "viscose", "fabrique", "entretien"])
