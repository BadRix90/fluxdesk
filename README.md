<div align="center">

![Flux Logo](docs/assets/full_margin.png)

# Flux

**Support ohne Reibung. Made in Europe.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Status](https://img.shields.io/badge/Status-Pre--Development-orange)](https://github.com/kaydietrich/flux)
[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Angular](https://img.shields.io/badge/Angular-21+-red.svg)](https://angular.dev/)

[Website](https://fluxdesk.eu) • [Documentation](docs/FLUX.md) • [Roadmap](docs/FLUX.md#roadmap) • [Contributing](#contributing)

</div>

---

## 🎯 Vision

Flux ist ein **modernes Open-Source-Ticketsystem**, das sich auf **Geschwindigkeit**, **Einfachheit** und **Datenschutz** fokussiert.

### Das Problem

Bestehende Lösungen leiden unter:
- 🐌 **Performance-Problemen** (Zammad: 8GB RAM, Jira: 5s Ladezeiten)
- 💸 **Hohen Kosten** (Zendesk: $99/Agent/Monat)
- 🌐 **US-Cloud-Abhängigkeit** (DSGVO-Bedenken)
- 🤯 **Feature-Bloat** (90% Features werden nicht genutzt)

### Die Lösung

Flux bietet:
- ⚡ **Extreme Performance** (<500MB RAM, <200ms Ticket-Öffnung)
- 🧠 **Local-First AI** (Ollama + pgvector, 100% DSGVO-konform)
- 🎨 **Inbox-Style UI** (Gmail-Feeling, Keyboard-First)
- 🇪🇺 **Made in Europe** (Hosting in Deutschland)
- 💰 **Fair Pricing** (Resource-based, nicht per Agent)

---

## ✨ Key Features (Planned)

### Core
- 📥 **Inbox-View** - Split-Layout, Real-Time Updates
- ⌨️ **Keyboard-First** - j/k Navigation, Command Palette (Ctrl+K)
- 🔍 **PostgreSQL FTS** - Keine Elasticsearch-Abhängigkeit
- 📧 **Email-Integration** - Tickets via Email erstellen & beantworten
- 🤖 **Auto-Assignment** - Intelligente Zuweisung
- ⏰ **Auto-Escalation** - 24h/48h/72h Rules

### AI-Powered (DSGVO-konform)
- 🧠 **Local LLMs** (Ollama: Llama-3, Mistral, Mixtral)
- 🔎 **RAG** (Retrieval-Augmented Generation via pgvector)
- ✍️ **Draft-Mode** - AI schlägt vor, Mensch sendet
- 🏷️ **Auto-Tagging** - Kategorisierung durch KI

### Analytics & Reporting
- 📊 **Dashboards** (Agent + Team)
- 📈 **Key Metrics** (Response Time, Resolution Rate)
- 💾 **Unlimited Export** (kein 6.000-Zeilen-Limit)
- 🗄️ **SQL-Access** (Read-Only für Power-User)

---

## 🛠️ Tech Stack

### Backend
- **Python 3.14+**
- **Django 6.0** + Django REST Framework
- **PostgreSQL 17** (mit pg_trgm für FTS, pgvector für AI)
- **Redis 7** (Caching + Celery)
- **Celery** (Background Jobs)
- **Django Channels** (WebSockets)

### Frontend
- **Angular 21+** (Standalone Components)
- **TypeScript** (Strict Mode)
- **Signals** (Reactive State)
- **TailwindCSS 4** (Styling)

### AI
- **Ollama** (Local LLM Runtime)
- **pgvector** (Vektor-Datenbank)
- **sentence-transformers** (Embeddings)

### Deployment
- **Docker** + Docker Compose
- **Nginx** (Reverse Proxy)
- **Hetzner Cloud** (Hosting)

---

## 📋 Status

**🚧 Pre-Development Phase**

Das Projekt ist aktuell in der Konzept-Phase. Entwicklung startet **Q2 2026** (nach Factora-Launch).

### Roadmap

- [ ] **Phase 1 (4-6 Wochen):** MVP - Core Ticketsystem
- [ ] **Phase 2 (2-3 Wochen):** AI-Integration + Polish
- [ ] **Phase 3 (Later):** Enterprise Features + Multi-Tenancy

Siehe [docs/FLUX.md](docs/FLUX.md) für detaillierte Roadmap und Architektur.

---

## 🚀 Quick Start

> **Note:** Noch nicht verfügbar. Coming Q2 2026.

```bash
# Clone Repository
git clone https://github.com/kaydietrich/flux.git
cd flux

# Start mit Docker Compose
docker-compose up -d

# Läuft auf http://localhost:8000
```

---

## 📖 Dokumentation

- **[FLUX.md](docs/FLUX.md)** - Komplettes Konzept-Dokument
  - Vision & Marktanalyse
  - Technische Architektur
  - Business Model
  - Konkurrenz-Vergleich
- **[FLUX-DEV-RULES.md](docs/FLUX-DEV-RULES.md)** - Coding Standards & Guidelines
  - Max 14 Zeilen pro Funktion
  - Max 400 Zeilen pro Datei
  - Django 6.0 & Angular 21 Best Practices
- **[FLUX-DESIGN-SYSTEM.md](docs/FLUX-DESIGN-SYSTEM.md)** - Design System
  - Farben (Light/Dark Mode)
  - Typografie (Inter)
  - WCAG AAA konform
- **[Contributing Guidelines](CONTRIBUTING.md)** - Wie du beitragen kannst *(coming soon)*
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community-Regeln *(coming soon)*

---

## 🤝 Contributing

Flux ist Open Source und lebt von der Community. Contributions sind willkommen!

### Wie du helfen kannst

Aktuell (Pre-Development):
- 🌟 **Star das Repo** - Zeig Interesse!
- 💡 **Diskutiere mit** - [GitHub Discussions](https://github.com/kaydietrich/flux/discussions)
- 📝 **Feedback** - Was fehlt? Was ist falsch?

Später (Development):
- 🐛 Bug Reports
- 💻 Code Contributions
- 📚 Dokumentation
- 🌍 Übersetzungen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details. *(coming soon)*

---

## 📊 Why Flux?

| Feature | Zammad | Zendesk | Jira SD | **Flux** |
|---|---|---|---|---|
| **RAM-Bedarf** | 4-8 GB | N/A | N/A | **< 500 MB** |
| **Ticket öffnen** | ~1s | ~500ms | ~5s | **< 200ms** |
| **Pro Agent/Monat** | N/A | $19-$99 | $20+ | **€0*** |
| **AI-Integration** | Cloud | OpenAI (US) | Cloud | **Lokal (EU)** |
| **DSGVO-konform** | ✅ | ⚠️ | ⚠️ | **✅ By Design** |
| **Open Source** | ✅ GPL | ❌ | ❌ | **✅ AGPL** |

\* SaaS: Resource-based Pricing (€29-199/Monat), Self-Hosted: Kostenlos

---

## 📜 License

Flux ist lizenziert unter der **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Das bedeutet:
- ✅ Kostenlos nutzen, ändern, verteilen
- ✅ Kommerziell nutzen (auch als SaaS)
- ⚠️ Änderungen müssen unter AGPL veröffentlicht werden
- ⚠️ Bei SaaS: Source Code muss Nutzern verfügbar sein

Siehe [LICENSE](LICENSE) für Details.

---

## 🙏 Acknowledgments

Flux steht auf den Schultern von Giganten:
- **Django** - Das beste Web-Framework
- **Angular** - Solide Frontend-Architektur
- **PostgreSQL** - Die zuverlässigste Datenbank
- **Ollama** - Local AI made easy
- **Zammad** - Inspiration für "Was kann man besser machen"

---

## 📬 Kontakt

- **Website:** [fluxdesk.eu](https://fluxdesk.eu)
- **GitHub Discussions:** [Discuss](https://github.com/kaydietrich/flux/discussions)
- **Email:** hello@fluxdesk.eu *(coming soon)*
- **Twitter:** [@fluxdesk](https://twitter.com/fluxdesk) *(coming soon)*

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kaydietrich/flux&type=Date)](https://star-history.com/#kaydietrich/flux&Date)

---

<div align="center">

**Made with ❤️ in Germany by [Kay Dietrich](https://github.com/kaydietrich)**

*Support fließt, Probleme lösen sich. Flux.*

[⬆ Back to Top](#flux)

</div>