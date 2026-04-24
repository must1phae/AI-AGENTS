from __future__ import annotations

from google import genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, NICHE, TONE


def _is_quota_error(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    message = str(error).upper()
    return status_code == 429 or "RESOURCE_EXHAUSTED" in message or "QUOTA" in message


def _fallback_caption() -> str:
    tone_key = TONE.strip().lower()
    variants = {
        "viral": (
            f"3 declics sur {NICHE} qui peuvent transformer ta semaine en 10 minutes par jour. "
            "Le plus puissant est souvent celui que personne ne teste. Tu veux que je te donne le plan complet ? "
            "Dis MOI en commentaire. #IA #Tech"
        ),
        "educatif": (
            f"Voici une methode simple pour progresser sur {NICHE} sans te disperser. "
            "Choisis 1 outil, applique-le 7 jours, puis mesure le resultat. "
            "Si tu veux la checklist, ecris CHECKLIST. #IA #Apprentissage"
        ),
        "storytelling": (
            f"Il y a 30 jours, je me sentais bloque sur {NICHE}. "
            "J ai change une seule habitude et tout est devenu plus clair. "
            "Tu veux que je raconte l histoire complete ? #IA #Story"
        ),
    }
    return variants.get(tone_key, variants["viral"])


def _extract_text(response: object) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", [])
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        chunks = getattr(content, "parts", [])
        for chunk in chunks:
            chunk_text = getattr(chunk, "text", None)
            if chunk_text:
                parts.append(str(chunk_text))
    return "".join(parts).strip()


def generate_caption() -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required to generate a caption.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""Tu es un créateur de contenu viral sur Instagram.
Génère une caption Instagram engageante sur le thème : {NICHE}.
Ton : {TONE}.

Règles :
- Hook puissant en 1ère ligne (curiosité ou chiffre)
- 3 à 5 phrases max
- Appel à l'action à la fin
- 1 à 2 hashtags pertinents uniquement
- Ajoute des emojis intelligemment

Réponds UNIQUEMENT avec la caption, rien d'autre."""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    except Exception as error:
        if _is_quota_error(error):
            return _fallback_caption()
        raise

    caption = _extract_text(response)
    if not caption:
        return _fallback_caption()
    return caption
