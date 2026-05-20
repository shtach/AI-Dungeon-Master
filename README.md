# AI Dungeon Master

A text-based RPG powered by Django and Gemini AI. Play D&D 5e with an AI Dungeon Master in your browser.

## Stack

![Django](https://img.shields.io/badge/Django-5-092E20?style=for-the-badge&logo=django)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css)
![HTMX](https://img.shields.io/badge/HTMX-Enabled-3366CC?style=for-the-badge)
![Alpine.js](https://img.shields.io/badge/Alpine.js-Lightweight-8BC0D0?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)

## Quick Start — Docker (recommended)

The fastest way to run the project locally. Only [Docker Desktop](https://www.docker.com/products/docker-desktop/) required — no Python, PostgreSQL, or Node.js installation needed.

### 1. Clone the repository

```bash
git clone git@github.com:shtach/AI-Dungeon-Master.git
cd AI-Dungeon-Master
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required fields:

> `DB_HOST` does not need to be changed — Docker Compose sets it automatically.

### 3. Start the project

```bash
docker compose up
```

Docker will automatically:

- build the Python image
- start PostgreSQL and wait until it is ready
- run `migrate`
- start Django at [http://localhost:8000](http://localhost:8000)
- start the Tailwind CSS watcher

First build takes ~2 minutes. Subsequent starts are near-instant.

### 4. (Optional) Create a superuser

In a separate terminal while containers are running:

```bash
docker compose exec web python manage.py createsuperuser
```

Then open [http://localhost:8000/admin](http://localhost:8000/admin).

### Useful commands

```bash
# Run in background
docker compose up -d

# View logs
docker compose logs -f web

# Stop containers
docker compose down

# Stop and wipe the database (full reset)
docker compose down -v

# Open Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test --verbosity=2

# Create migrations after model changes
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Rebuild image after changing requirements
docker compose build
```

---

## Manual Setup — Requirements

| Dependency     | Arch Linux                  | Windows                                                               |
| -------------- | --------------------------- | --------------------------------------------------------------------- |
| Python 3.12+   | `sudo pacman -S python`     | [python.org](https://www.python.org/downloads/) — check "Add to PATH" |
| Git            | `sudo pacman -S git`        | [git-scm.com](https://git-scm.com/download/win)                       |
| PostgreSQL 15+ | `sudo pacman -S postgresql` | [postgresql.org](https://www.postgresql.org/download/windows/)        |

---

## Setup — Arch Linux

### 1. Install and initialize PostgreSQL

```bash
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl enable --now postgresql
```

Create the database user and database:

```bash
sudo -u postgres psql -c "CREATE USER pgadmin WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE game_db OWNER pgadmin;"
```

### 2. Clone the repository

```bash
https://github.com/shtach/AI-Dungeon-Master.git
cd AI-Dungeon-Master
```

### 3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

If you use **fish shell**:

```fish
source .venv/bin/activate.fish
```

### 4. Install Python dependencies

```bash
pip install -r requirements/development.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the values:

```env
DJANGO_SECRET_KEY=your-50-character-random-key
DJANGO_SETTINGS_MODULE=ai_dungeon_master.config.settings.development

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

DB_NAME=game_db
DB_USER=pgadmin
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Install Tailwind CSS

```bash
python manage.py tailwind install
python manage.py tailwind build
```

> Downloads the Tailwind CSS standalone binary. No Node.js or npm required.

### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```

### 9. Start the development server

```bash
python manage.py tailwind dev
```

This starts both Django and the Tailwind CSS watcher simultaneously.
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

Alternatively, run them separately in two terminals:

```bash
# Terminal 1 — Tailwind watcher
python manage.py tailwind start

# Terminal 2 — Django
python manage.py runserver
```

---

## Setup — Windows

### 1. Install PostgreSQL

1. Download from [postgresql.org](https://www.postgresql.org/download/windows/) and run the installer
2. Remember the password you set for the `postgres` user
3. Open **pgAdmin** or the **SQL Shell (psql)** and run:

```sql
CREATE USER pgadmin WITH PASSWORD 'your_password';
CREATE DATABASE game_db OWNER pgadmin;
```

### 2. Clone the repository

Open **Git Bash** or **PowerShell**:

```powershell
https://github.com/shtach/AI-Dungeon-Master.git
cd AI-Dungeon-Master
```

### 3. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Python dependencies

```powershell
pip install -r requirements/development.txt
```

### 5. Configure environment variables

```powershell
copy .env.example .env
```

Open `.env` in a text editor and fill in the values:

```env
DJANGO_SECRET_KEY=your-50-character-random-key
DJANGO_SETTINGS_MODULE=ai_dungeon_master.config.settings.development

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

DB_NAME=game_db
DB_USER=pgadmin
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

To generate a secret key in PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 6. Install Tailwind CSS

```powershell
python manage.py tailwind install
python manage.py tailwind build
```

### 7. Run database migrations

```powershell
python manage.py migrate
```

### 8. (Optional) Create a superuser

```powershell
python manage.py createsuperuser
```

### 9. Start the development server

Open two PowerShell windows:

```powershell
# Window 1 — Tailwind watcher
python manage.py tailwind start

# Window 2 — Django
python manage.py runserver
```

Or use the combined command:

```powershell
python manage.py tailwind dev
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Using SQLite instead of PostgreSQL (quick start)

If you want to skip the PostgreSQL setup and run locally without a database server, open
[ai_dungeon_master/config/settings/development.py](ai_dungeon_master/config/settings/development.py)
and uncomment the SQLite block:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "BASE_DIR" or "local_db" or "db.sqlite3",
    }
}
```

Then run `python manage.py migrate` — no database server needed.

---

## AI Provider setup

Our project is designed to support a wide range of AI agents, including models like Google Gemini.

### Get a free API key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Left panel → **Get API Key** → **Create API key**
4. Copy the key

The free tier is sufficient for local development — no credit card required.

### Configure locally

Add to your `.env` file:

```env
GEMINI_API_KEY=your-key-here
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash-lite
```

### Switch to mock provider (no API key needed)

Set in `.env`:

```env
AI_PROVIDER=mock
```

Useful for running tests or working offline.

---

## Project structure

```
AI-Dungeon-Master/
├── ai_dungeon_master/
│   ├── apps/
│   │   ├── accounts/       # Auth — login, register, profile
│   │   ├── characters/     # D&D character system
│   │   ├── game/           # Core game engine
│   │   ├── ai/             # LLM client
│   │   ├── world/          # World settings & scenarios
│   │   └── core/           # Shared utilities
│   └── config/
│       └── settings/
│           ├── base.py         # Common settings
│           ├── development.py  # Local dev (DEBUG=True, PostgreSQL)
│           └── production.py   # Production (DEBUG=False, SSL)
├── theme/                  # Tailwind CSS app
├── templates/              # Django HTML templates
├── static/                 # Static files (JS, images)
├── requirements/
│   ├── common.txt          # Shared dependencies
│   ├── development.txt     # Dev extras (debug toolbar, pytest)
│   └── production.txt      # Prod extras (gunicorn, whitenoise)
└── docs/strategy/          # Architecture & design docs
```

---

## Common commands

```bash
# Run all tests
pytest

# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Rebuild Tailwind CSS manually
python manage.py tailwind build
```

---

## Troubleshooting

**`No module named 'django'`**
Virtual environment is not activated.
Run `source .venv/bin/activate` (bash/zsh), `source .venv/bin/activate.fish` (fish), or `.venv\Scripts\activate` (Windows).

**`connection to server at "localhost" port 5432 failed`**
PostgreSQL is not running. Start it with `sudo systemctl start postgresql` (Linux) or via the Services panel (Windows).

**`database "..." does not exist`**
The `.env` file is missing or has wrong `DB_NAME`. Make sure `.env` exists and `DB_NAME` matches the database you created.

**`tailwind: command not found`**
Run `python manage.py tailwind install` first to download the Tailwind CSS standalone binary.

---

## Git workflow

### Branch structure

```
main       ← production (merged from develop via PR only)
  │
develop    ← main development branch (all PRs target here)
  │
  ├── feature/DEV-A/character-models
  ├── feature/DEV-B/gemini-client
  ├── feature/DEV-C/game-screen
  └── fix/DEV-A/dice-negative-rolls
```

### Branch naming

```bash
feature/DEV-{X}/{short-description}   # new feature
fix/DEV-{X}/{short-description}       # bug fix
hotfix/{short-description}            # critical fix directly to main

# X is number of issue
```

### Commit convention

```
<type>(<module>): <description>

Types:
  feat      new feature
  fix       bug fix
  docs      documentation only
  style     formatting, no logic change
  refactor  code restructure, no behaviour change
  test      adding or updating tests
  chore     dependencies, CI, config

Examples:
  feat(game): add SendMessageView with Gemini integration
  feat(characters): implement 4-step character creation wizard
  fix(dice): handle negative modifiers in breakdown string
  docs: update README with Docker quick start
  chore: add flake8 config to .flake8
```

### Daily workflow

```bash
# 1. Start your day — update develop
git checkout develop
git pull origin develop

# 2. Create a branch from fresh develop
git checkout -b feature/DEV-C/sidebar-component

# 3. Work — commit in small logical units
git status                              # what changed?
git diff                                # exact changes?

git add templates/game/_sidebar.html
git commit -m "feat(frontend): add character sidebar with HP bars"

git add templates/game/_hp_bar.html
git commit -m "feat(frontend): extract HP bar to separate partial"

# 4. Push your branch
git push -u origin feature/DEV-C/sidebar-component

# 5. Open a Pull Request on GitHub → target: develop

# 6. If develop changed while you were working — rebase, don't merge
git fetch origin
git rebase origin/develop
# Resolve conflicts if any, then:
git rebase --continue
git push --force-with-lease   # force only for your own branch
```

### Useful commands

```bash
# Readable history graph
git log --oneline --graph --all

# All commits on your branch vs develop
git log develop..HEAD --oneline

# Search commit messages
git log --all --grep="dice"

# Who changed this line?
git blame templates/game/session.html

# Compare branches
git diff develop..feature/DEV-A/dice-service

# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Stash and restore work in progress
git stash
git stash pop

# Clean up history before opening a PR
git rebase -i develop
```
