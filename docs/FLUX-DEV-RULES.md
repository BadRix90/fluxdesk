# Flux Development Rules - Kay Dietrich

## Code-Qualitätsstandards

### Funktionslänge & Dateistruktur
- **Max 14 Zeilen pro Funktion** (ohne Docstring/Comments)
- **Max 400 Zeilen pro Datei**
- Bei Überschreitung: Datei splitten oder Funktion refactoren

### Naming Conventions
- **Eindeutige Namen**: Keine generischen Namen wie `handle()`, `process()`, `data`
- **Beschreibend**: `assign_ticket_to_agent()` statt `assign()`
- **Konsistent**: Django/Angular Best Practices folgen

### Dokumentation
- **Offizielle Docs als Referenz:**
  - Django 6.0: https://docs.djangoproject.com/en/6.0/
  - Angular (latest): https://angular.dev/overview
- **Code-Kommentare**: Nur "Warum", nicht "Was" (Code soll selbsterklärend sein)
- **Docstrings**: Für alle Public Functions/Classes

### Code-Qualität
- **DRY Prinzip**: Keine Code-Duplikation
- **Type Hints**: Python überall, TypeScript strict mode
- **Error Handling**: Explizit, keine stillen Failures
- **Testing**: Unit Tests für Business Logic

### Response-Effizienz
- **Fokus auf das Wesentliche**: Keine unnötigen Erklärungen
- **Code First**: Code zeigen, dann kurz erklären
- **Inkrementell**: Nicht alles auf einmal, sondern Schritt für Schritt
- **Gegenprüfung**: Immer gegen offizielle Docs validieren

---

## Django-Spezifisch

### Models
```python
# Max 14 Zeilen pro Method
class Ticket(models.Model):
    def assign_to_available_agent(self) -> Optional[User]:
        """Assign ticket to agent with fewest open tickets."""
        agent = User.objects.filter(
            is_staff=True,
            assigned_tickets__status='OPEN'
        ).annotate(
            ticket_count=Count('assigned_tickets')
        ).order_by('ticket_count').first()
        
        if agent:
            self.assignee = agent
            self.status = 'OPEN'
            self.save()
        return agent
```

### Views (DRF)
- ViewSets für CRUD
- Action Methods max 14 Zeilen
- Business Logic in Models/Services auslagern

### Services
```python
# services/ticket_service.py
class TicketService:
    @staticmethod
    def escalate_ticket(ticket: Ticket) -> bool:
        """Escalate ticket priority if conditions met."""
        if ticket.age_hours > 24 and ticket.status == 'OPEN':
            ticket.priority = min(ticket.priority + 1, 4)
            ticket.save()
            return True
        return False
```

---

## Angular-Spezifisch

### Components
- Standalone Components (Angular 20+)
- Logic in Services, nicht in Components
- Template max 100 Zeilen, sonst splitten

### Services
```typescript
// services/ticket.service.ts
@Injectable({ providedIn: 'root' })
export class TicketService {
  private http = inject(HttpClient);
  tickets = signal<Ticket[]>([]);
  
  loadTickets(): Observable<Ticket[]> {
    return this.http.get<Ticket[]>('/api/tickets/').pipe(
      tap(tickets => this.tickets.set(tickets))
    );
  }
  
  assignToMe(id: number): Observable<Ticket> {
    return this.http.post<Ticket>(`/api/tickets/${id}/assign_to_me/`, {});
  }
}
```

### Components (max 14 Zeilen Methoden)
```typescript
@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule],
  template: `...`
})
export class TicketListComponent {
  ticketService = inject(TicketService);
  
  ngOnInit() {
    this.loadTickets();
  }
  
  loadTickets() {
    this.ticketService.loadTickets().subscribe();
  }
  
  selectTicket(ticket: Ticket) {
    this.ticketService.selectedTicket.set(ticket);
  }
}
```

---

## File Organization

### Django
```
backend/
├── apps/
│   ├── tickets/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py        # < 400 Zeilen
│   │   │   └── comment.py       # < 400 Zeilen
│   │   ├── services/
│   │   │   ├── ticket_service.py
│   │   │   └── escalation_service.py
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   └── viewsets.py
│   │   └── tests/
```

### Angular
```
frontend/src/app/
├── features/
│   ├── tickets/
│   │   ├── components/
│   │   │   ├── ticket-list/
│   │   │   │   ├── ticket-list.component.ts    # < 400 Zeilen
│   │   │   │   ├── ticket-list.component.html  # < 100 Zeilen
│   │   │   │   └── ticket-list.component.scss
│   │   │   └── ticket-detail/
│   │   ├── services/
│   │   │   └── ticket.service.ts
│   │   └── models/
│   │       └── ticket.model.ts
```

---

## Response-Format (für Claude)

### ❌ Nicht so (zu verbose):
```
Ich werde jetzt eine Funktion erstellen, die Tickets eskaliert. 
Diese Funktion prüft zuerst ob das Ticket älter als 24 Stunden ist.
Dann erhöht sie die Priorität. Am Ende speichert sie das Ticket.
Hier ist der Code...
[Code]
Wie du siehst, macht die Funktion XYZ...
```

### ✅ Sondern so (effizient):
```python
# tickets/services/escalation_service.py
class EscalationService:
    @staticmethod
    def escalate_if_needed(ticket: Ticket) -> bool:
        if ticket.age_hours > 24 and ticket.status == 'OPEN':
            ticket.priority = min(ticket.priority + 1, 4)
            ticket.save()
            return True
        return False
```
**Eskaliert Ticket wenn > 24h offen. Max Priority = 4.**

---

## Checkliste vor Response

- [ ] Funktionen < 14 Zeilen?
- [ ] Dateien < 400 Zeilen?
- [ ] Namen eindeutig & beschreibend?
- [ ] Django/Angular Docs gecheckt?
- [ ] Type Hints/Strict Mode?
- [ ] DRY Prinzip eingehalten?
- [ ] Response auf das Nötigste reduziert?

---

## Quick Reference

**Django Docs:** https://docs.djangoproject.com/en/6.0/
**Angular Docs:** https://angular.dev/overview

**Projekt:** Flux (Ticketsystem)
**Stack:** Django 5.x + Angular 20 + PostgreSQL + Redis
**Coding Standard:** Clean Code, pragmatisch, production-ready

---

**Bei Verletzung der Rules → Sofort korrigieren!**
