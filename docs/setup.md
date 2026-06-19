# Local Setup & Installation Guide

This guide covers everything required to get the AI Dungeon Master project running locally on your machine.

---

## Prerequisites
Before you begin, ensure you have the following installed:
* **Python 3.12+** (if running manually without Docker)
* **Docker & Docker Desktop** (recommended)
* **Ollama** (optional, required only for local offline AI development)

---

## Run Paths

You can run the application using one of the two paths below.

### Path A: Docker (Recommended)
This path automatically configures the database, web server, and frontend assets.
1. Ensure Docker Desktop is running.
2. Initialize environment variables (see [Environment Variables](#environment-variables)).
3. Run the following command at the repository root:

```bash
   docker compose up
```
   
Access the application at: http://localhost:8000

Path B: Manual Installation
Use this path if you prefer running components natively outside of Docker containers.

**Virtual Environment:**
```bash
python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

Database: Ensure local PostgreSQL is running, create a database named game_db.
**Tailwind CSS:** Build the frontend styles:
```bash
python manage.py tailwind build
```

**Migrations & Server:**
```bash
python manage.py migrate
   python manage.py runserver
```

## Environment Variables
Copy the template file `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```

| Variable | Group | Description | Example Value | Required? |
| :--- | :--- | :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Django Core | Cryptographic key for Django security. | *Auto-generated string* | **Yes** |
| `DJANGO_SETTINGS_MODULE` | Django Core | Defines environment configuration. | `ai_dungeon_master.config.settings.development` | **Yes** |
| `ALLOWED_HOSTS` | Django Core | Host/domain names that this site can serve. | `localhost,127.0.0.1,0.0.0.0` | **Yes** |
| `DB_NAME` | Postgres | Name of the PostgreSQL database. | `game_db` | **Yes** |
| `DB_USER` | Postgres | Database administrative user. | `postgres` | **Yes** |
| `DB_PASSWORD` | Postgres | Password for the database user. | `postgres` | **Yes** |
| `DB_HOST` | Postgres | Hostname of the database server. | `postgres_db` (Docker) or `localhost` | **Yes** |
| `DB_PORT` | Postgres | Connection port for database. | `5432` (or `5433` if port conflict) | **Yes** |
| `AI_PROVIDER` | Gemini / AI | Chooses the active LLM brain. | `gemini` / `mock` / `ollama` | **Yes** |
| `GEMINI_API_KEY` | Gemini / AI | API token from Google AI Studio. | `AIzaSy...` | Optional |
| `GEMINI_MODEL` | Gemini / AI | The exact model deployment name. | `gemini-2.5-flash-lite` | Optional |
| `PGADMIN_DEFAULT_EMAIL` | pgAdmin | Admin login email for database GUI. | `admin@admin.com` | Optional |
| `PGADMIN_DEFAULT_PASSWORD`| pgAdmin | Admin login password for database GUI. | `root` | Optional |

## AI_PROVIDER Switching Modes
The game supports three AI modes via the AI_PROVIDER flag in your .env:

mock: Does not call any external APIs. Returns pre-baked, structural text instantly. Use this for core engine development, frontend styling, or offline workspace without tokens.

gemini: Connects to Google's cloud models. High quality, requires a valid GEMINI_API_KEY.

ollama: Connects to a locally running instance of Ollama for completely offline local neural narration.

Ollama Setup Step: You must pull the targeted model inside your terminal before playing: ollama pull <model_name>.

(Note: Hardware-specific model size guidelines can be found in the future PR reference table under BE-21).

## Canonical Command Reference
Always run these commands from the repository root. If using Docker, prefix them with docker compose exec web.

Apply Migrations: python manage.py migrate

Seed Initial Data: python manage.py seed_data

⚠️ Gotcha Note: If the database contains semi-applied states or you want to cleanly reseed, seed_data might early-exit or fail. To fix this, wipe the database volume entirely via docker compose down -v and run docker compose up again to cleanly execute seeding on an empty volume.

Create Superuser: python manage.py createsuperuser

Build Tailwind CSS: python manage.py tailwind build

Run Tests: pytest

## Troubleshooting
1. Port 5432 Conflict
Issue: Container game_postgres Error dependency postgres_db failed to start.

Fix: A local PostgreSQL instance is already taking up port 5432. Open docker-compose.yml, change the port mapping line to "5433:5432", and change DB_PORT=5433 in your .env.

2. WSL Read-Only File System (Windows)
Issue: Error response from daemon: write ... read-only file system.

Fix: The underlying WSL subsystem crashed. Quit Docker Desktop via the system tray, restart your Windows machine,