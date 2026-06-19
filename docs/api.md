```markdown
# API & Route Reference

This document maps all application endpoints, views, authentication rules, and frontend HTMX injection target structures.

---

## Route Overview

Planned but not yet implemented endpoints are explicitly tagged as `Planned (DEV-xx)`.

| HTTP Method | Path | Auth Required? | Purpose / Action | HTMX Swap Target |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | No | Marketing Landing/Splash Page | Full Page |
| `GET` | `/accounts/login/` | No | Renders User Login Interface | Full Page |
| `GET` | `/dashboard/` | **Yes** | User Profile & Character Selection | Full Page |
| `GET` | `/characters/wizard/step-1/` | **Yes** | Step 1: Choose Archetype/Class | `#character-wizard` |
| `POST`| `/game/session/create/` | **Yes** | Spawns fresh simulation instance | Full Page |
| `POST`| `/game/session/message/send/` | **Yes** | Dispatches choice text, triggers turn engine | `#cards`, `#hp-bar` |
| `GET` | `/legacy/vault/` | **Yes** | *Planned (DEV-44)* View unlocked relics | `#legacy-panel` |