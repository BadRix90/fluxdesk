# Flux

**Support ohne Reibung. Made in Europe.**

🌍 **fluxdesk.eu**

---

## Vision

Ein Ticketsystem für Teams, die Probleme lösen wollen – nicht Tools konfigurieren.

**Kern-Prinzip:** Wenn es mehr als 3 Klicks braucht, ist es falsch designed.

**Positionierung:** Das Anti-Bloat Ticketsystem. Schneller als Zammad. Günstiger als Zendesk. Privacy-First durch Local AI.

---

## Warum Flux existieren muss

### Der Markt 2026: Unzufriedenheit überall

**Zammad (Open Source):**
- ❌ Ressourcen-Monster (8GB RAM durch Elasticsearch)
- ❌ Starr (kein Löschen/Editieren von Tickets)
- ❌ Reporting-Limits (6.000 Zeilen max)
- ❌ Komplexe Updates (Elasticsearch-Versionskonflikte)

**Zendesk (SaaS Marktführer):**
- ❌ Teuer ($19-$99/Agent, versteckte Kosten)
- ❌ Feature-Bloat (90% Features werden nicht genutzt)
- ❌ Träge UI (Legacy-Code aus 2010)
- ❌ US-Cloud (DSGVO-Bedenken)

**Jira Service Desk (Enterprise):**
- ❌ Extrem langsam (5s+ Ladezeiten)
- ❌ Entwickler-zentriert (zu komplex für Support)
- ❌ Teuer (Enterprise-Pricing)

**Freshdesk:**
- ❌ Feature-Removal (CSV-Export plötzlich kostenpflichtig)
- ❌ Vertrauensverlust (ständige Preis-/Plan-Änderungen)
- ❌ Bug-Dichte (instabile UI)

### Die Marktlücke

**Missing Middle:** Teams, die aus Shared Inbox (Gmail, Outlook) herausgewachsen sind, aber die Komplexität von Enterprise-Tools scheuen.

**Flux füllt diese Lücke:**
- ✅ Modern & Schnell (wie Zendesk sein sollte)
- ✅ Open Source & Hostbar (wie Zammad, aber besser)
- ✅ Privacy-First (Local AI statt US-Cloud)
- ✅ Simpel (Convention over Configuration)

---

## Core-Prinzipien

### 1. Geschwindigkeit über Features
- Ticket öffnen: **1 Klick**
- Antworten: **0 Klicks** (direkt inline)
- Status ändern: **1 Klick** (Dropdown, kein Modal)
- **Performance-Ziel:** < 200ms Ticket-Öffnungszeit

### 2. Klare Ownership
- Ticket ist **entweder** zugewiesen **oder** nicht
- Ein Name, ein Verantwortlicher
- **Kein** "Primary Agent with Secondary Backup and Observing Groups"-Wahnsinn

### 3. Status = Was passiert als Nächstes
```
NEW         → System muss zuweisen
OPEN        → Agent muss antworten
WAITING     → Kunde muss antworten
RESOLVED    → Kunde bestätigt oder Auto-Close nach 7 Tagen
CLOSED      → Fertig
```

**Nicht:** 15 Custom-Status wie "Pending Approval Level 2"

### 4. Auto-Eskalation = Simpel
- **24h keine Antwort** → Priorität +1
- **48h keine Antwort** → Manager-Notification
- **72h keine Antwort** → Kritisch + Reassign
- **Fertig. Keine komplexen Trigger-Bedingungen.**

### 5. Convention over Configuration
- 80% Use Cases funktionieren out-of-the-box
- Smart Defaults statt endlose Config
- Anpassungen nur wo wirklich nötig

### 6. Privacy-First
- **Local AI** (Ollama) statt US-Cloud (OpenAI)
- **EU-Hosting** (Hetzner) als Standard
- **Datensouveränität** als Feature, nicht Afterthought

---

## Tech-Stack

### Backend: Django + DRF

```
Python 3.12+
Django 5.x
Django REST Framework
PostgreSQL (mit pg_trgm für Full-Text Search)
Redis (Caching + Celery + Channels Backend)
Celery (Background Jobs)
Django Channels (WebSockets für Real-Time)
```

**Warum Django trotz Go/Rust-Performance-Argumenten:**

**Technische Realität:**
- **Zammad's Problem ist NICHT Rails** – es ist Elasticsearch (2-8GB RAM)
- Django + PostgreSQL FTS = kein externer Search-Service nötig
- Modern deployed Django (Gunicorn + Redis) ist verdammt schnell
- **RAM-Budget Flux:** ~350MB (Django 200MB + Postgres 100MB + Redis 50MB)
- **RAM-Budget Zammad:** ~8GB (Rails 500MB + Elasticsearch 2-8GB)

**Pragmatische Gründe:**
- Kay's Expertise (Factora läuft auf Django)
- Batteries Included (Admin, ORM, Auth out-of-the-box)
- Schnellere Time-to-Market (4-6 Wochen MVP vs. 6-12 Monate Go/Rust lernen)
- Battle-tested Stack (Instagram, Spotify nutzen Django)

**Hybrid-Strategie (später):**
- **Phase 1:** Django Monolith (MVP in 4-6 Wochen)
- **Phase 2:** Performance-kritische Services in Go auslagern
  - Search-Service (Go + Meilisearch)
  - WebSocket-Server (Go)
  - AI-Proxy (Go + Ollama)

**Performance-Optimierungen:**
- Kein Elasticsearch (PostgreSQL pg_trgm + pg_search)
- Aggressive Redis-Caching (Query-Results, Sessions)
- Database Indexing (GIN-Indizes für FTS)
- Connection Pooling (PgBouncer)
- Async Views (Django async support)

### Frontend: Angular 20+

```
Angular 20+ (Standalone Components)
TypeScript (Strict Mode)
Signals (Reactive State)
RxJS (Async Operations)
TailwindCSS (Styling)
```

**Warum Angular:**
- Kay's Haupt-Framework (Factora-Stack)
- Type-Safety (weniger Bugs)
- Enterprise-Ready (klare Struktur)
- Performance (Ahead-of-Time Compilation)

**UI-Philosophie:**
- **Inbox-First** (Gmail/Outlook-Feeling)
- **Keyboard-Driven** (j/k Navigation)
- **Minimal Clicks** (Inline Actions)
- **Real-Time** (WebSocket-Updates)

### Datenbank & Suche

**PostgreSQL:**
- Primary Database
- Full-Text Search (pg_trgm, pg_search)
- Vektoren (pgvector für AI/RAG)

**SQLite (Optional für kleine Instanzen):**
- Teams < 20 Agents
- Single-File Database
- Zero Admin Overhead

**Keine Elasticsearch:**
- PostgreSQL FTS reicht für 99% Use Cases
- Spart 2-8GB RAM
- Keine komplexen Updates

### Infrastruktur

```
Docker + Docker Compose (Development)
PostgreSQL (Database)
Redis (Cache + Message Broker)
Nginx (Reverse Proxy)
Hetzner Cloud (Hosting)
```

**Deployment:**
- Docker-basiert (Single Stack)
- One-Command Install: `docker-compose up -d`
- Update: `docker-compose pull && docker-compose up -d`
- Rollback: `docker-compose down && docker-compose up -d <old-version>`

---

## Killer-Feature: Local AI

### Das Problem mit Cloud-AI

**Zendesk/Freshdesk AI:**
- Daten gehen an OpenAI (US-Server)
- DSGVO-Bedenken (Schrems II)
- Pro-Token-Kosten ($0.01-$0.10 pro Request)
- Zusatzkosten: $50/Agent/Monat

**Flux AI: Local-First, Privacy-First**

### Technologie: Ollama + pgvector

**Stack:**
- **Ollama:** Lokale LLM-Runtime (Llama-3, Mistral, Mixtral)
- **pgvector:** Vektordatenbank in PostgreSQL
- **RAG:** Retrieval-Augmented Generation

**Workflow:**
1. **Kunde fragt:** "Login funktioniert nicht, Fehler 503"
2. **Flux durchsucht lokal:**
   - Alte Tickets mit ähnlichen Problemen
   - Wissensdatenbank-Artikel
   - Interne Dokumentation
3. **Lokales LLM generiert Antwortentwurf:**
   - Basierend auf gefundenen Lösungen
   - Im Kontext des Unternehmens
4. **Agent sieht Vorschlag:**
   - Korrigiert kurz
   - Sendet ab

### Vorteile

✅ **100% DSGVO-konform**  
→ Keine Daten verlassen das Unternehmen

✅ **Keine Pro-Token-Kosten**  
→ Nur einmalige Hardware-Investition (GPU optional)

✅ **Offline-fähig**  
→ Kein Internet nötig für AI-Features

✅ **Branchen-spezifisch trainierbar**  
→ Gesundheitswesen, Finanzen, Behörden

✅ **Keine Vendor-Lock-in**  
→ Modelle sind Open Source (Llama, Mistral)

### Copilot vs. Autopilot

**Flux setzt auf Draft-Mode:**
- AI antwortet **NIE** direkt an Kunden
- AI füllt Antwortfeld vor
- **Mensch prüft → Mensch sendet**
- Verhindert KI-Halluzinationen

**Human in the Loop = Qualität + Vertrauen**

### Competitive Advantage

| Feature | Zendesk AI | Flux AI |
|---|---|---|
| Hosting | US-Cloud | Lokal (EU) |
| Datenschutz | Schrems II Risiko | 100% DSGVO |
| Kosten | $50/Agent/Monat | Einmalig (Hardware) |
| Latenz | 500ms-2s (API) | <100ms (lokal) |
| Offline | Nein | Ja |
| Vendor-Lock | OpenAI | Open Source Models |

**Flux AI = Verkaufsargument #1 für deutsche SMEs**

---

## Core Features (v1.0)

### Ticket-Management

- ✅ **Inbox-Style UI** (Split-View: Liste + Detail)
- ✅ **Keyboard Shortcuts** (j/k Navigation, Enter öffnen, Esc schließen, r Antworten)
- ✅ **Inline Actions** (Status/Priority per Dropdown)
- ✅ **Drag & Drop** (File-Uploads)
- ✅ **Rich-Text** (Markdown-Kommentare)
- ✅ **Interne Notizen** (nur für Agents sichtbar)
- ✅ **@Mentions** (Kollegen taggen)
- ✅ **Soft-Delete** (Tickets löschen ohne DB-Verlust)

### Automatisierung

- ✅ **Auto-Assignment** (Agent mit wenigsten offenen Tickets)
- ✅ **Auto-Eskalation** (24h/48h/72h Rules)
- ✅ **Auto-Close** (7 Tage nach RESOLVED)
- ✅ **Email-Integration** (Tickets via Email erstellen)
- ✅ **Smart Notifications** (nur was wichtig ist)

### Suche & Filter

- ✅ **Google-Style Volltext** (PostgreSQL FTS)
- ✅ **Quick-Filters** (Meine Queue, Nicht zugewiesen, Eskaliert)
- ✅ **Advanced Search** (`status:open priority:high customer:@acme.com`)
- ✅ **Saved Searches** (Favoriten speichern)

### Analytics

- ✅ **Agent Dashboard** (Meine Tickets, Performance)
- ✅ **Team Dashboard** (Gesamtübersicht)
- ✅ **Key Metrics:**
  - Durchschnittliche Antwortzeit
  - Tickets pro Agent
  - Offene Tickets gesamt
  - Resolution Rate
  - Kundenzufriedenheit (Thumbs Up/Down)
- ✅ **Unlimited Export** (kein 6.000-Zeilen-Limit)
- ✅ **SQL-Access** (Schreibgeschützt für Power-User)

### Multi-Channel

- ✅ **Email** (Tickets erstellen + beantworten via Email)
- ✅ **Web Widget** (Embedded Support-Form)
- ✅ **API** (REST + Webhooks)
- 🔜 **Slack/Discord** (v2.0)

### AI-Integration (KILLER-FEATURE)

- ✅ **Ollama Integration** (Lokale LLMs)
- ✅ **pgvector RAG** (Semantische Suche in Tickets/Docs)
- ✅ **Draft-Mode** (AI schlägt vor, Mensch sendet)
- ✅ **Knowledge Base Search** (AI findet relevante Artikel)
- ✅ **Auto-Tag** (AI kategorisiert Tickets automatisch)

---

## Was Flux NICHT ist

### Anti-Features (bewusst weggelassen)

❌ **Keine Business Rules Engine**
- Keine verschachtelten If/Then/Else-Bedingungen
- Keine "Trigger Builder" UIs
- Einfache, klare Automatisierungen in Code

❌ **Keine Custom Fields Orgie**
- Standard-Felder decken 95% ab
- Max. 5 Custom Fields pro Ticket-Typ
- Wenn du mehr brauchst, nutzt du das Tool falsch

❌ **Kein Ticket-Merge/Split**
- Macht eh keiner richtig
- Führt zu Chaos in der Historie
- Bei Bedarf: Neues Ticket + Referenz

❌ **Kein überkompliziertes SLA-Management**
- Simple Deadlines: 24h/48h/72h
- Automatische Eskalation
- Keine "SLA Compliance Matrix by Weekday per Department"

❌ **Keine Integration zu jedem Tool der Welt**
- API für wichtige Use Cases
- Webhooks für Custom-Integrationen
- Kein Plugin-Marketplace-Chaos

❌ **Kein Time-Tracking auf die Minute**
- Grobe Zeiterfassung (Optional)
- Fokus auf Problemlösung, nicht Zeiterfassung

---

## Konkurrenz-Vergleich

### Performance & Ressourcen

| Kriterium | Zammad | Zendesk | Jira Service Desk | **Flux** |
|---|---|---|---|---|
| RAM-Bedarf | 4-8 GB | N/A (Cloud) | N/A (Cloud) | **< 500 MB** |
| Ticket öffnen | ~1s | ~500ms | ~5s | **< 200ms** |
| Search Engine | Elasticsearch | Proprietär | Lucene | **PostgreSQL FTS** |
| Setup-Zeit | Stunden | Minuten (SaaS) | Tage | **5 Minuten** |

### Kosten

| Kriterium | Zammad | Zendesk | Freshdesk | **Flux** |
|---|---|---|---|---|
| Self-Hosted | Kostenlos | Nicht möglich | Nicht möglich | **Kostenlos (AGPLv3)** |
| Pro Agent/Monat | N/A | $19-$99 | $15-$79 | **€0 (Resource-based)** |
| AI-Kosten | Cloud-Integration | $50/Agent | $30/Agent | **Einmalig (Hardware)** |
| Hidden Costs | Teures Hosting | Viele Add-ons | Feature-Removal | **Keine** |

### Features

| Kriterium | Zammad | Zendesk | Jira SD | **Flux** |
|---|---|---|---|---|
| Ticket löschen | ❌ Blockiert | ✅ Möglich | ✅ Möglich | **✅ Soft-Delete** |
| Report-Export | ❌ 6k Limit | ✅ Unlimited | ✅ Unlimited | **✅ Unlimited + SQL** |
| Keyboard Shortcuts | ⚠️ Begrenzt | ✅ Ja | ❌ Nein | **✅ Gmail-like** |
| Edit History | ❌ Nein | ⚠️ Limitiert | ✅ Ja | **✅ 10min Window** |

### AI & Datenschutz

| Kriterium | Zammad | Zendesk | Freshdesk | **Flux** |
|---|---|---|---|---|
| KI-Integration | ⚠️ Begrenzt | ✅ OpenAI (US) | ✅ Cloud-AI | **✅ Ollama (Lokal)** |
| Datenspeicherung | ✅ EU (Self) | ⚠️ US/EU | ⚠️ US/EU | **✅ 100% Lokal** |
| DSGVO-konform | ✅ Ja | ⚠️ Schrems II | ⚠️ Schrems II | **✅ By Design** |

### UX

| Kriterium | Zammad | Zendesk | Jira SD | **Flux** |
|---|---|---|---|---|
| UI-Philosophie | Feature-reich | Bloated | Developer-zentriert | **Minimalistisch** |
| Mobile | ✅ Funktioniert | ✅ Native App | ⚠️ Schlecht | **✅ PWA** |
| Lernkurve | Wochen | Tage | Wochen | **Minuten** |
| Dark Mode | ✅ Ja | ✅ Ja | ❌ Nein | **✅ Auto** |

---

## Architektur-Übersicht

### Database Schema (Core)

```sql
-- Tickets
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'NEW',
    priority INTEGER DEFAULT 2,
    customer_id INTEGER REFERENCES users(id),
    assignee_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP NULL,
    closed_at TIMESTAMP NULL,
    deleted_at TIMESTAMP NULL,  -- Soft-Delete
    
    -- Full-Text Search
    search_vector tsvector,
    
    -- AI/RAG
    embedding vector(1536)  -- pgvector für semantische Suche
);

-- Indizes für Performance
CREATE INDEX idx_tickets_status ON tickets(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_assignee ON tickets(assignee_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_search ON tickets USING GIN(search_vector);
CREATE INDEX idx_tickets_embedding ON tickets USING ivfflat(embedding vector_cosine_ops);

-- Comments
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id),
    author_id INTEGER REFERENCES users(id),
    text TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    edited_at TIMESTAMP NULL,
    
    search_vector tsvector
);

-- Attachments
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id),
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Escalations (Audit Log)
CREATE TABLE escalations (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id),
    from_priority INTEGER NOT NULL,
    to_priority INTEGER NOT NULL,
    reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Drafts (Cache für KI-Vorschläge)
CREATE TABLE ai_drafts (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id),
    draft_text TEXT NOT NULL,
    confidence FLOAT,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```
# Tickets
GET    /api/tickets/                    # Liste aller Tickets
POST   /api/tickets/                    # Neues Ticket
GET    /api/tickets/{id}/               # Ticket-Details
PATCH  /api/tickets/{id}/               # Ticket updaten
DELETE /api/tickets/{id}/               # Soft-Delete

# Queues
GET    /api/tickets/my_queue/           # Meine zugewiesenen Tickets
GET    /api/tickets/escalated/          # Eskalierte Tickets
GET    /api/tickets/unassigned/         # Nicht zugewiesene Tickets

# Actions
POST   /api/tickets/{id}/comment/       # Kommentar hinzufügen
POST   /api/tickets/{id}/assign_to_me/  # Ticket mir zuweisen
POST   /api/tickets/{id}/resolve/       # Ticket als gelöst markieren
POST   /api/tickets/{id}/close/         # Ticket schließen
POST   /api/tickets/{id}/restore/       # Soft-Delete rückgängig

# AI
POST   /api/tickets/{id}/ai_draft/      # KI-Antwortentwurf generieren
GET    /api/tickets/{id}/similar/       # Ähnliche Tickets finden (RAG)

# Search
GET    /api/search/?q=login+problem     # Volltext-Suche
GET    /api/search/advanced/            # Advanced Search mit Filtern

# Analytics
GET    /api/analytics/dashboard/        # Dashboard-Daten
GET    /api/analytics/export/           # Unlimited CSV Export
POST   /api/analytics/sql/              # Custom SQL Query (Read-Only)
```

### Background Jobs (Celery)

```python
# Jede Stunde
@celery.task
def check_escalations():
    """Tickets > 24h ohne Antwort → Priorität erhöhen"""
    escalated = 0
    for ticket in Ticket.objects.escalated():
        if ticket.auto_escalate():
            escalated += 1
            send_escalation_email(ticket)
    return f"Escalated {escalated} tickets"

# Täglich
@celery.task
def auto_close_resolved():
    """RESOLVED Tickets > 7 Tage → CLOSED"""
    cutoff = timezone.now() - timedelta(days=7)
    tickets = Ticket.objects.filter(
        status='RESOLVED',
        resolved_at__lt=cutoff
    )
    count = tickets.update(
        status='CLOSED',
        closed_at=timezone.now()
    )
    return f"Auto-closed {count} tickets"

# Bei Ticket-Erstellung
@celery.task
def send_notifications(ticket_id):
    """Email/Slack Benachrichtigungen"""
    ticket = Ticket.objects.get(id=ticket_id)
    
    # Email an Assignee
    if ticket.assignee:
        send_email(
            to=ticket.assignee.email,
            subject=f"Neues Ticket: {ticket.subject}",
            template='new_ticket.html',
            context={'ticket': ticket}
        )
    
    # Optional: Slack/Discord Webhook
    if settings.SLACK_WEBHOOK:
        post_to_slack(ticket)

# Täglich (Nacht)
@celery.task
def update_search_vectors():
    """Full-Text Search Indizes aktualisieren"""
    Ticket.objects.update_search_vectors()
    Comment.objects.update_search_vectors()

# Bei AI-Request
@celery.task
def generate_ai_draft(ticket_id):
    """Asynchrone AI-Draft-Generierung"""
    ticket = Ticket.objects.get(id=ticket_id)
    
    # RAG: Ähnliche Tickets finden
    similar = ticket.find_similar(limit=5)
    
    # Ollama API Call
    draft = ollama_generate_response(
        ticket=ticket,
        similar_tickets=similar
    )
    
    # Draft speichern
    AIDraft.objects.create(
        ticket=ticket,
        draft_text=draft['text'],
        confidence=draft['confidence'],
        model_used='llama-3-8b'
    )
```

### WebSocket Events (Django Channels)

```python
# Real-Time Updates via WebSockets

# Ticket created
ws://fluxdesk.eu/ws/tickets/
→ { "type": "ticket.created", "ticket_id": 123, "subject": "..." }

# Ticket updated
→ { "type": "ticket.updated", "ticket_id": 123, "status": "RESOLVED" }

# New comment
→ { "type": "comment.added", "ticket_id": 123, "author": "Max" }

# Agent assigned
→ { "type": "ticket.assigned", "ticket_id": 123, "assignee": "Anna" }

# AI draft ready
→ { "type": "ai.draft_ready", "ticket_id": 123 }
```

---

## UI/UX Konzept

### Design-Prinzipien

**1. Inbox-First**
- Split-View Layout (Liste links, Detail rechts)
- Wie Gmail/Outlook
- Keine vollständigen Page-Reloads
- Progressive Web App (PWA)

**2. Keyboard-Driven**
```
j/k       → Nächstes/Vorheriges Ticket
Enter     → Ticket öffnen
Esc       → Ticket schließen
r         → Reply (Antworten)
e         → Escalate (Eskalieren)
a         → Assign to me
c         → Close
Ctrl+K    → Command Palette
1-4       → Priorität setzen
```

**3. Minimal Clicks**
- Status: Dropdown in Header (1 Klick)
- Priority: Dropdown in Header (1 Klick)
- Assign: Button "Mir zuweisen" (1 Klick)
- Comment: Inline-Form immer sichtbar (0 Klicks zum Start)

**4. Real-Time Updates**
- WebSocket-Verbindung (Django Channels)
- Live-Counter für neue Tickets
- Toast-Notifications bei Updates
- Optimistic UI (sofortige Reaktion)

**5. Mobile-First**
- Responsive Design (TailwindCSS)
- Touch-optimiert
- Swipe-Gesten:
  - Swipe Right → Resolve
  - Swipe Left → Archive
  - Pull-to-Refresh

### Color Scheme

```scss
// Primary Colors
$primary:   #0EA5E9;  // Electric Blue (Speed, Tech)
$success:   #10B981;  // Neon Green (EU, Eco, Resolved)
$warning:   #F59E0B;  // Orange (Escalated)
$danger:    #EF4444;  // Red (Critical)

// Neutrals
$dark:      #0F172A;  // Cyberpunk Dark
$gray:      #64748B;  // Text Secondary
$light:     #F1F5F9;  // Background

// Status Colors
$status-new:        #3B82F6;  // Blue
$status-open:       #F59E0B;  // Orange
$status-progress:   #8B5CF6;  // Purple
$status-waiting:    #64748B;  // Gray
$status-resolved:   #10B981;  // Green
$status-closed:     #475569;  // Dark Gray
```

### Typography

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
font-size: 16px;
line-height: 1.5;
font-weight: 400; /* Normal */
font-weight: 500; /* Medium */
font-weight: 600; /* Semibold für Headlines */
```

### Component Examples

```typescript
// Command Palette (Ctrl+K)
interface Command {
  id: string;
  label: string;
  icon: string;
  action: () => void;
  shortcut?: string;
}

const commands: Command[] = [
  { id: 'resolve', label: 'Ticket lösen', icon: 'check', action: resolveTicket, shortcut: 'e' },
  { id: 'assign', label: 'Mir zuweisen', icon: 'user', action: assignToMe, shortcut: 'a' },
  { id: 'close', label: 'Schließen', icon: 'x', action: closeTicket, shortcut: 'c' },
  { id: 'ai-draft', label: 'KI-Vorschlag', icon: 'sparkles', action: generateAIDraft }
];
```

---

## Roadmap

### Phase 1: MVP (4-6 Wochen) – "Flux Core"

**Backend:**
- [x] Django Models (Ticket, Comment, Attachment)
- [x] REST API (DRF ViewSets)
- [x] PostgreSQL FTS (Full-Text Search)
- [x] Auto-Assignment
- [x] Auto-Eskalation (Celery Tasks)
- [x] Email-Integration (Inbound/Outbound)

**Frontend:**
- [x] Angular Inbox-View (Split-Layout)
- [x] Ticket-List Component
- [x] Ticket-Detail Component
- [x] Keyboard Shortcuts (j/k/r/e/a)
- [x] Real-Time Updates (WebSockets)

**Deployment:**
- [x] Docker Compose Setup
- [x] Nginx Config
- [x] One-Command Install

**Deliverable:** Funktionierende Ticket-System-Basis

---

### Phase 2: Polish & AI (2-3 Wochen) – "Flux Intelligence"

**AI-Integration:**
- [ ] Ollama REST API Integration
- [ ] pgvector Setup
- [ ] RAG Implementation (Ähnliche Tickets finden)
- [ ] AI-Draft-Generierung
- [ ] Auto-Tagging (Kategorisierung)

**UX:**
- [ ] Command Palette (Ctrl+K)
- [ ] Advanced Search UI
- [ ] Saved Searches
- [ ] Dark Mode
- [ ] Mobile Optimierung (PWA)

**Analytics:**
- [ ] Agent Dashboard
- [ ] Team Dashboard
- [ ] Export (CSV/Excel)
- [ ] SQL-Access UI

**Deliverable:** Production-Ready System mit Local AI

---

### Phase 3: Growth Features (Later) – "Flux Enterprise"

**Multi-Channel:**
- [ ] Slack Integration
- [ ] Discord Integration
- [ ] WhatsApp Business API
- [ ] Telegram Bot

**Enterprise:**
- [ ] Multi-Tenancy (SaaS-Modus)
- [ ] SSO (SAML/OAuth)
- [ ] Advanced Permissions (RBAC)
- [ ] Audit Logs
- [ ] Custom Branding
- [ ] Whitelabel-Option

**Performance:**
- [ ] Go-basierter Search-Service (Meilisearch)
- [ ] Go WebSocket-Server (Centrifugo)
- [ ] CDN Integration (Cloudflare)

**Deliverable:** Enterprise-Grade SaaS Platform

---

### Migration Strategy: Der "Shadow Mode"

**Problem:** Niemand wechselt gerne sein Ticketsystem ("Rip and Replace" ist riskant)

**Flux-Lösung: Shadow Integration**

**Workflow:**
1. **Flux verbindet sich via API** mit Zendesk/Jira/Freshdesk
2. **Importiert Tickets in Echtzeit** (Read-Only Mirror)
3. **Agenten nutzen Flux als Frontend**
4. **Aktionen werden zurückgespielt** an das alte System
5. **Wenn Team zufrieden** → Vollständige Migration mit einem Klick

**Vorteil:**
- ✅ **Zero Risk:** Altes System bleibt parallel aktiv
- ✅ **Test-Drive:** Team kann Geschwindigkeit + UX testen
- ✅ **Schrittweise Migration:** Erst einzelne Teams, dann alle
- ✅ **Kein Datenverlust:** Historie bleibt erhalten

**Technische Umsetzung:**
```python
# flux/integrations/zendesk.py
class ZendeskShadowSync:
    def sync_tickets(self):
        """Sync Zendesk → Flux (Read-Only)"""
        zendesk_tickets = self.zendesk_api.get_tickets()
        for zt in zendesk_tickets:
            Ticket.objects.update_or_create(
                external_id=zt.id,
                defaults={
                    'subject': zt.subject,
                    'description': zt.description,
                    # ...
                }
            )
    
    def push_update(self, ticket):
        """Flux Action → Zendesk"""
        self.zendesk_api.update_ticket(
            ticket.external_id,
            status=ticket.status
        )
```

---

## Business Model

### Target Market

**Primary:** Deutsche SMEs (10-100 Mitarbeiter)

**Branchen:**
- IT-Dienstleister
- SaaS-Unternehmen
- E-Commerce
- Gesundheitswesen (DSGVO-kritisch)
- Behörden/Öffentlicher Sektor

**Use Cases:**
- IT-Support (Internal Helpdesk)
- Customer Service
- Bug-Tracking
- Field Service

### Pricing (SaaS)

**Resource-Based Pricing** (nicht per Agent!)

```
Starter:      €29/Monat
- 500 Tickets/Monat
- 5 GB Storage
- Email-Support
- Community-Forum

Professional: €79/Monat
- Unlimited Tickets
- 50 GB Storage
- Priority Email-Support
- Slack Integration

Enterprise:   €199/Monat
- Unlimited Everything
- Dedicated Support
- Custom Branding
- SSO/SAML
- SLA-Garantie (99.9%)
```

**Warum Resource-Based?**
- Bestraft nicht Teamgröße
- Fördert Kollaboration (jeder kann helfen)
- Transparenter (keine "Agent-Lizenzen")
- Konkurrent Zendesk: $99/Agent → Team mit 10 Agents = $990
- Flux: $79 flat → Team mit 50 Agents = $79

### Self-Hosted (Open Source)

**Lizenz:** AGPLv3

**Kostenlos:**
- Komplette Kernsoftware
- Updates
- Community-Support

**Monetarisierung via Add-ons:**
- **Enterprise Plugins:** €499 einmalig
  - SSO (SAML/OAuth)
  - Advanced Audit Logs
  - Multi-Brand Support
  - Whitelabel
- **Managed Hosting:** €49-€149/Monat
  - Automatische Backups
  - Monitoring
  - Updates
- **Support-Verträge:** €99/Monat
  - 8h Response-Time
  - Telefon-Support

### Revenue Streams

1. **SaaS Subscriptions** (Hauptumsatz, ~70%)
2. **Self-Hosted Lizenzen** (Enterprise Plugins, ~20%)
3. **Managed Hosting** (~5%)
4. **Custom Development** (€120/Stunde, ~5%)

### Break-Even Kalkulation

**Kosten pro Monat:**
```
Server (Hetzner CX51):     €30
Domain/Email:              €10
Monitoring (Uptime Robot): €5
Marketing (Google Ads):    €200
Total:                     €245
```

**Break-Even:**
- 4 Professional-Kunden (4 × €79 = €316)
- Oder 9 Starter-Kunden (9 × €29 = €261)

**Realistic Target (6 Monate nach Launch):**
- 20 Starter (€580)
- 10 Professional (€790)
- 2 Enterprise (€398)
- **Total: €1.768 MRR**

---

## Entwicklungs-Guidelines

### Code-Qualität

**Backend (Python/Django):**
```python
# Type Hints überall
def create_ticket(subject: str, customer: User) -> Ticket:
    ...

# Docstrings für alle Public Methods
"""
Create a new ticket and auto-assign to available agent.

Args:
    subject: Ticket subject line
    customer: User who created the ticket

Returns:
    Ticket: Newly created ticket instance
"""

# Unit Tests (>80% Coverage)
pytest tests/

# Django Best Practices
- Use Django ORM (kein Raw SQL außer Performance-Critical)
- DRY Prinzip
- Fat Models, Thin Views
- Signals für Side Effects
```

**Frontend (TypeScript/Angular):**
```typescript
// TypeScript Strict Mode
"strict": true,
"noImplicitAny": true,
"strictNullChecks": true

// Standalone Components
@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule, TicketItemComponent]
})

// Signals für State
ticketService.tickets = signal<Ticket[]>([]);

// RxJS für Async
loadTickets(): Observable<Ticket[]> {
  return this.http.get<Ticket[]>('/api/tickets/');
}

// TailwindCSS (keine Custom CSS außer Ausnahmen)
<div class="flex items-center gap-4 p-4 hover:bg-gray-50">
```

### Performance-Ziele

```
Page Load:           < 1s (First Contentful Paint)
Ticket öffnen:       < 200ms (API + Render)
Search Results:      < 500ms
API Response:        < 100ms (95th percentile)
WebSocket Latency:   < 50ms

Database Queries:    < 10ms (mit Indizes)
Cache Hit Rate:      > 90% (Redis)
```

### Security

**OWASP Top 10:**
- ✅ CSRF Protection (Django Middleware)
- ✅ XSS Prevention (Template Auto-Escaping)
- ✅ SQL Injection Prevention (ORM)
- ✅ Rate Limiting (Django-Ratelimit)
- ✅ HTTPS-only (Nginx Config)
- ✅ Secure Headers (CSP, HSTS, X-Frame-Options)

**DSGVO:**
- ✅ Data Minimization (nur nötige Daten speichern)
- ✅ Right to Erasure (Soft-Delete + Hard-Delete nach 30 Tagen)
- ✅ Data Portability (Export aller User-Daten)
- ✅ Encryption at Rest (PostgreSQL Encryption)
- ✅ Encryption in Transit (TLS 1.3)

**Authentication:**
- ✅ Password Hashing (Django Argon2)
- ✅ 2FA Support (django-otp)
- ✅ Session Security (Secure Cookies)
- ✅ API Token (JWT für API-Zugriff)

---

## Installation & Deployment

### Docker Compose (Development)

```bash
# Clone Repo
git clone https://github.com/kaydietrich/flux.git
cd flux

# Start Stack
docker-compose up -d

# Create Superuser
docker-compose exec web python manage.py createsuperuser

# Läuft auf http://localhost:8000
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: flux
      POSTGRES_USER: flux
      POSTGRES_PASSWORD: flux
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    
  web:
    build: .
    command: gunicorn flux.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      DATABASE_URL: postgres://flux:flux@db:5432/flux
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    
  celery:
    build: .
    command: celery -A flux worker -l info
    depends_on:
      - db
      - redis
      
  celery-beat:
    build: .
    command: celery -A flux beat -l info
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Production (Hetzner)

**Server-Anforderungen:**
```
Hetzner CX21:
- 2 vCPU
- 4 GB RAM
- 40 GB SSD
- €5.83/Monat

→ Reicht für 50-100 Agents

Hetzner CX41 (für AI):
- 4 vCPU
- 16 GB RAM
- 160 GB SSD
- €15.50/Monat

→ Mit Ollama (Llama-3-8B)
```

**Deployment via Ansible:**
```bash
# Setup Server
ansible-playbook -i production deploy.yml

# Updates
ansible-playbook -i production update.yml

# Rollback
ansible-playbook -i production rollback.yml
```

---

## Why Flux will succeed

### 1. Problem-Solution Fit ✅

**Problem:** Ticketsysteme sind zu komplex, zu teuer, zu langsam  
**Solution:** Flux ist radikal simpel, günstig, schnell  
**Evidence:** Jeder hasst Zammad's RAM-Hunger, Zendesk's Preise, Jira's Langsamkeit

### 2. Timing ✅

**2026 Market Conditions:**
- Cloud-Backlash (Privacy-Bedenken)
- AI-Hype (aber Cloud-AI ist teuer + unsicher)
- SMEs digitalisieren (brauchen Tools)
- DSGVO-Enforcement (US-Tools riskant)

**Flux = Right Product, Right Time**

### 3. Developer Experience ✅

- Kay's Expertise (Django + Angular)
- Modern Stack (Spaß beim Entwickeln)
- Clean Code (Wartbar, Erweiterbar)
- Open Source (Community-Driven)

### 4. Market Gap ✅

**Expensive:** Zendesk, Freshdesk (zu teuer für SMEs)  
**Complex:** Zammad, Jira (zu komplex)  
**Flux:** Sweet Spot (simpel + erschwinglich + schnell)

### 5. Unique Differentiator ✅

**Local AI (Ollama):**
- Kein Konkurrent hat das
- DSGVO-konform by design
- Keine laufenden Kosten
- **Verkaufsargument #1**

### 6. Realistic Execution ✅

- Kay hat Zeit nach Factora-Launch
- Stack ist bekannt (Django + Angular)
- MVP in 4-6 Wochen möglich
- Break-Even bei 4 Kunden (realistisch)

---

## Success Metrics

### Development Metrics

- [ ] Backend API vollständig (100% Endpoints)
- [ ] Frontend UI vollständig (Inbox + Detail + Analytics)
- [ ] Unit Tests > 80% Coverage
- [ ] E2E Tests für Critical Paths (Ticket Create, Resolve, Close)
- [ ] Performance Goals erreicht (< 200ms Ticket-Öffnung)
- [ ] Docker Deployment funktioniert (One-Command Install)

### Business Metrics

**MVP Launch:**
- [ ] 10 Beta-Tester (Freunde/Familie/Communities)
- [ ] 5 GitHub Stars/Woche
- [ ] 1 Blog Post (Launch Announcement)

**Public Launch (+4 Wochen):**
- [ ] 50 Signups (Self-Hosted)
- [ ] 10 Paying Customers (€290 MRR)
- [ ] 100 GitHub Stars
- [ ] 1 Tech-Blog Erwähnung (t3n, heise)

**Growth (+12 Wochen):**
- [ ] 100 Paying Customers (€2.900 MRR)
- [ ] Break-Even (Server-Kosten gedeckt)
- [ ] 500 GitHub Stars
- [ ] Top 10 bei "Open Source Helpdesk" Google-Suche

**Scale (+6 Monate):**
- [ ] 500 Paying Customers (€14.500 MRR)
- [ ] Kay's Haupteinkommen (€5k+/Monat)
- [ ] 2.000 GitHub Stars
- [ ] Erste Enterprise-Kunde (Custom Contract)

---

## Next Steps

### Sofort (diese Woche)

- [x] Name finalisieren: **Flux**
- [x] Domain sichern: **fluxdesk.eu**
- [ ] Logo-Konzept erstellen
- [ ] GitHub Repo aufsetzen (github.com/kaydietrich/flux)
- [ ] Basis README.md schreiben

### Nach Factora-Launch (Q2 2026)

**Woche 1-2: Backend**
- [ ] Django Project Setup
- [ ] Models (Ticket, Comment, User, Attachment)
- [ ] REST API (DRF)
- [ ] PostgreSQL FTS
- [ ] Celery Tasks (Auto-Eskalation)

**Woche 3-4: Frontend**
- [ ] Angular Project Setup
- [ ] Inbox-View (Split-Layout)
- [ ] Ticket-List Component
- [ ] Ticket-Detail Component
- [ ] Keyboard Shortcuts

**Woche 5: Integration**
- [ ] Email-Integration (Inbound)
- [ ] WebSocket Setup (Django Channels)
- [ ] Real-Time Updates

**Woche 6: AI**
- [ ] Ollama Integration
- [ ] pgvector Setup
- [ ] AI-Draft-Generierung

**Woche 7-8: Polish**
- [ ] UI/UX Refinement
- [ ] Analytics Dashboard
- [ ] Testing (Unit + E2E)
- [ ] Docker Deployment

**Woche 9: Beta Launch**
- [ ] Beta-Tester onboarden
- [ ] Feedback sammeln
- [ ] Bugs fixen

**Woche 10-12: Public Launch**
- [ ] Landing Page (fluxdesk.eu)
- [ ] Docs (docs.fluxdesk.eu)
- [ ] Blog Post (Launch Announcement)
- [ ] Reddit/HackerNews Post
- [ ] ProductHunt Launch

---

## Fazit

**Flux = Das Ticketsystem, das du aufmachst und einfach benutzt.**

Keine Schulung.  
Keine Konfiguration.  
Keine Frustration.  
Keine US-Cloud.

Einfach Support machen – wie es sein sollte.

---

*"Support fließt, Probleme lösen sich. Flux."*  
– Flux Manifesto

---

**Version:** 1.0  
**Erstellt:** 18. Januar 2026  
**Author:** Kay Dietrich  
**Status:** Konzept (Pre-Development)  
**Domain:** fluxdesk.eu (reserviert)  
**Stack:** Django + Angular + Ollama  
**Launch:** Q2 2026 (nach Factora)

---

## Anhang: Technische Deep-Dives

### PostgreSQL Full-Text Search (FTS)

**Warum kein Elasticsearch?**
- Elasticsearch braucht 2-8GB RAM
- PostgreSQL FTS braucht < 50MB
- FTS ist "good enough" für 99% Use Cases

**Setup:**
```sql
-- Extension aktivieren
CREATE EXTENSION pg_trgm;
CREATE EXTENSION unaccent;

-- Search Vector Column
ALTER TABLE tickets ADD COLUMN search_vector tsvector;

-- Trigger für Auto-Update
CREATE TRIGGER tickets_search_update
BEFORE INSERT OR UPDATE ON tickets
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(
  search_vector, 'pg_catalog.german',
  subject, description
);

-- GIN Index für Performance
CREATE INDEX tickets_search_idx ON tickets
USING GIN(search_vector);

-- Suche (Deutsch)
SELECT * FROM tickets
WHERE search_vector @@ to_tsquery('german', 'login & problem');

-- Fuzzy Search (Tippfehler)
SELECT * FROM tickets
WHERE subject % 'lgoin problm';  -- Findet "login problem"
```

### pgvector für AI/RAG

**Setup:**
```sql
-- Extension
CREATE EXTENSION vector;

-- Embedding Column
ALTER TABLE tickets ADD COLUMN embedding vector(1536);

-- Index (IVFFlat)
CREATE INDEX tickets_embedding_idx ON tickets
USING ivfflat(embedding vector_cosine_ops)
WITH (lists = 100);

-- Ähnliche Tickets finden
SELECT subject, description,
  1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM tickets
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

**Python Integration:**
```python
from sentence_transformers import SentenceTransformer

# Model laden (lokal!)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Embedding generieren
text = f"{ticket.subject} {ticket.description}"
embedding = model.encode(text)

# Speichern
ticket.embedding = embedding.tolist()
ticket.save()

# Ähnliche finden
similar = Ticket.objects.raw('''
    SELECT *, 
      1 - (embedding <=> %s::vector) AS similarity
    FROM tickets
    WHERE id != %s
    ORDER BY embedding <=> %s::vector
    LIMIT 5
''', [embedding.tolist(), ticket.id, embedding.tolist()])
```

### Ollama Integration

**API Call:**
```python
import requests

def ollama_generate_draft(ticket, similar_tickets):
    # Context aufbauen
    context = f"""
    Aktuelle Anfrage:
    {ticket.subject}
    {ticket.description}
    
    Ähnliche gelöste Tickets:
    """
    
    for st in similar_tickets:
        context += f"\n- {st.subject}: {st.resolution_text}"
    
    # Ollama API
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama3',
        'prompt': f"""
        {context}
        
        Erstelle eine professionelle Antwort auf Deutsch für den Kunden.
        Sei höflich, klar und lösungsorientiert.
        """,
        'stream': False
    })
    
    return response.json()['response']
```

---

**Flux ist bereit. Jetzt muss nur noch Factora durch die Tür, dann bauen wir das schnellste Ticketsystem Europas. 🚀**
