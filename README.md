<div align="center">

![Flux Logo](docs/assets/full_margin.png)

# FluxDesk

**Open-source ticketing system. Fast, private, European.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Angular](https://img.shields.io/badge/Angular-21-red.svg)](https://angular.dev/)

</div>

---

## What is FluxDesk?

FluxDesk is a lightweight, self-hostable ticketing system built for teams that care about speed and data privacy. It runs on a modern stack (Django + Angular) and keeps everything — including AI features — local and GDPR-compliant.

### Key Features

- **Multi-tenant organizations** — each org has its own users, tickets, and settings
- **Role-based access** — Admin, Agent, and Customer roles with scoped permissions
- **Email verification & agent invitations** — secure onboarding with token-based flows
- **Ticket management** — create, assign, escalate, resolve, comment
- **Queue views** — my queue, unassigned, escalated
- **JWT authentication** — stateless auth with token refresh
- **Local-first AI** (planned) — Ollama + pgvector, no data leaves your server

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13+, Django 6.0, Django REST Framework, SimpleJWT |
| **Frontend** | Angular 21, TypeScript, Signals, TailwindCSS 4 |
| **Database** | PostgreSQL 17 |
| **Cache / Broker** | Redis 7 |
| **Task Queue** | Celery |
| **Real-time** | Django Channels (WebSockets) |
| **AI** (planned) | Ollama, pgvector, sentence-transformers |
| **Deployment** | Docker Compose |

---

## Quick Start

```bash
git clone https://github.com/BadRix90/fluxdesk.git
cd fluxdesk

# Copy environment file and adjust as needed
cp .env.example .env

# Start all services
docker compose up -d
```

The app will be available at:
- **Frontend:** http://localhost:4200
- **Backend API:** http://localhost:8000/api/

### Services

| Container | Purpose |
|---|---|
| `flux-backend` | Django API (Gunicorn) |
| `flux-frontend` | Angular dev server |
| `flux-db` | PostgreSQL 17 |
| `flux-redis` | Redis 7 |
| `flux-celery` | Celery worker |
| `flux-celery-beat` | Celery scheduler |

---

## Project Structure

```
fluxdesk/
  backend/
    apps/
      core/          # Organization, Invitation, auth endpoints
      tickets/       # Ticket, Comment models + API
      users/         # Custom User model with roles
    config/          # Django settings, URLs, Celery, ASGI
  frontend/
    src/app/
      core/          # Guards, interceptors, services, models
      features/      # Auth, tickets, settings components
      shared/        # Sidebar, status badge
  docker-compose.yml
  .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/token/` | Login (JWT) |
| POST | `/api/auth/token/refresh/` | Refresh token |
| POST | `/api/register/` | Register new org + admin |
| POST | `/api/verify-email/` | Verify email address |
| POST | `/api/accept-invitation/` | Accept agent invitation |
| GET/PATCH | `/api/organization/` | Org settings |
| GET/POST/DELETE | `/api/invitations/` | Manage invitations |
| GET/POST | `/api/tickets/` | List / create tickets |
| GET/PATCH/DELETE | `/api/tickets/:id/` | Ticket detail |
| POST | `/api/tickets/:id/assign_to_me/` | Assign ticket |
| POST | `/api/tickets/:id/resolve/` | Resolve ticket |
| POST | `/api/tickets/:id/close/` | Close ticket |
| POST | `/api/tickets/:id/comment/` | Add comment |
| GET | `/api/tickets/my_queue/` | Agent's assigned tickets |
| GET | `/api/tickets/unassigned/` | Unassigned tickets |
| GET | `/api/tickets/escalated/` | Escalated tickets |

---

## Development

### Backend (local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (local)

```bash
cd frontend
npm install
npm start
```

The Angular dev server proxies `/api` requests to `localhost:8000`.

---

## Documentation

- [FLUX.md](docs/FLUX.md) — Architecture and concept
- [FLUX-DEV-RULES.md](docs/FLUX-DEV-RULES.md) — Coding standards
- [FLUX-DESIGN-SYSTEM.md](docs/FLUX-DESIGN-SYSTEM.md) — Design system

---

## License

FluxDesk is licensed under the [GNU Affero General Public License v3.0](LICENSE).

You can freely use, modify, and distribute it. If you run a modified version as a service, you must make the source code available to your users.

---

<div align="center">

**Built by [Kay Dietrich](https://github.com/BadRix90)**

[fluxdesk.eu](https://fluxdesk.eu)

</div>
