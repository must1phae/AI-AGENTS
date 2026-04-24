from __future__ import annotations

from google import genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, NICHE, TONE


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

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    caption = _extract_text(response)
    if not caption:
        raise RuntimeError("The LLM returned an empty caption.")
    return caption
