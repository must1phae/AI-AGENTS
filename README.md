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

Sans `--image-url`, l'agent peut generer automatiquement une image IA selon le sujet (`NICHE`) et le ton (`TONE`).
Pour desactiver ce comportement sur un run:

```bash
python main.py --no-auto-image
```

Test rapide de la cle Gemini uniquement:

```bash
python main.py --test-gemini
```

Si le test echoue avec `429 RESOURCE_EXHAUSTED` ou `404 NOT_FOUND`, utilise un modele compatible dans `.env`, par exemple:

```bash
GEMINI_MODEL=gemini-flash-lite-latest
```

Sans argument, le script utilise `DEFAULT_IMAGE_URL`.

Si Gemini retourne une erreur de quota (429), l'agent bascule automatiquement sur une caption locale de secours pour ne pas bloquer le flux.

## Dashboard multi-agent

Tu peux piloter plusieurs agents depuis une interface web locale (creation, activation/desactivation, dry-run, publication):

```bash
streamlit run dashboard/app.py
```

Dans la dashboard:

- Cree un ou plusieurs agents (nom, niche, ton, image URL)
- Active `Generer image IA si URL vide` pour creer l'image automatiquement a partir du sujet
- Active ou desactive chaque agent individuellement
- Definis une heure de planification par agent (`Scheduler actif` + `Heure planifiee`)
- Lance `Dry run` pour tester sans publication
- Lance `Publier` pour poster sur la cible configuree dans `.env`

Les agents sont sauvegardes automatiquement dans `dashboard/agents.json`.

Tu peux aussi lancer un check scheduler manuel:

```bash
python main.py --run-scheduled
```

## Planification

### Option Windows (Task Scheduler)

```powershell
powershell -ExecutionPolicy Bypass -File .\scheduler\register_windows_task.ps1 -StartTime 09:00
```

Pour le scheduler par agent (verifie chaque minute les heures configurees dans la dashboard):

```powershell
powershell -ExecutionPolicy Bypass -File .\scheduler\register_windows_task.ps1 -PerAgentScheduler
```

Verifier la tache:

```powershell
schtasks /Query /TN "AI-AGENTS-DailyPost" /V /FO LIST
```

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
- `AUTO_GENERATE_IMAGE`: `true` ou `false` pour autoriser la generation d'image IA automatique
- `IMAGE_PROVIDER`: provider de generation (`pollinations` par defaut)
- `IMAGE_SIZE`: taille image sous la forme `1200x1200`
- `POST_HOUR`: heure cible pour la publication
- `PUBLISH_TARGET`: `instagram` ou `facebook`
- `FACEBOOK_PAGE_ID`: requis si `PUBLISH_TARGET=facebook`
