# AI Instagram Agent

Bot Python pour générer une caption avec Gemini, l'optimiser, puis publier un post image via l'Instagram Graph API ou une Page Facebook.

## Prérequis

- Compte Instagram Business ou Creator lié à une Page Facebook
- App Meta for Developers avec le produit Instagram Graph API
- `IG_USER_ID` et `IG_ACCESS_TOKEN`
- `GEMINI_API_KEY`
- Une image hébergée publiquement via S3, Cloudinary, etc.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Renseigne ensuite les variables dans `.env`.

## Lancement manuel

```bash
python main.py --image-url https://example.com/image.jpg
```

Sans argument, le script utilise `DEFAULT_IMAGE_URL`.

Si Gemini retourne une erreur de quota (429), l'agent bascule automatiquement sur une caption locale de secours pour ne pas bloquer le flux.

## Planification

### Option simple: cron

```bash
0 9 * * * /usr/bin/python3 /path/to/ai-instagram-agent/main.py >> /tmp/ig_agent.log 2>&1
```

### Option Celery + Redis

```bash
celery -A scheduler.tasks worker --loglevel=info
celery -A scheduler.tasks beat --loglevel=info
```

## Variables importantes

- `IG_USER_ID`: l'identifiant Instagram Business lié à la Page Facebook
- `IG_ACCESS_TOKEN`: token long-terme valide pour Graph API
- `GEMINI_API_KEY`: clé API Gemini
- `DEFAULT_IMAGE_URL`: image publique à publier
- `POST_HOUR`: heure cible pour la publication
- `PUBLISH_TARGET`: `instagram` ou `facebook`
- `FACEBOOK_PAGE_ID`: requis si `PUBLISH_TARGET=facebook`
