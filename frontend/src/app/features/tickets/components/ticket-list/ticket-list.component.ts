import { Component, inject, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { LucideAngularModule, Flame, Clock, Inbox } from 'lucide-angular';

import { TicketService } from '../../services/ticket.service';
import { StatusBadgeComponent } from '../../../../shared/components/status-badge/status-badge.component';
import { PRIORITY_LABELS, type TicketPriority } from '../../../../core/models/ticket.model';

@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [DatePipe, RouterLink, StatusBadgeComponent, LucideAngularModule],
  templateUrl: './ticket-list.component.html',
  styleUrl: './ticket-list.component.scss',
})
export class TicketListComponent implements OnInit {
  private route = inject(ActivatedRoute);
  ticketService = inject(TicketService);

  readonly icons = { Flame, Clock, Inbox };

  ngOnInit(): void {
    const filter = this.route.snapshot.data['filter'] ?? 'all';
    this.loadByFilter(filter);
  }

  loadByFilter(filter: string): void {
    switch (filter) {
      case 'my-queue':
        this.ticketService.loadMyQueue().subscribe();
        break;
      case 'unassigned':
        this.ticketService.loadUnassigned().subscribe();
        break;
      case 'escalated':
        this.ticketService.loadEscalated().subscribe();
        break;
      default:
        this.ticketService.loadTickets().subscribe();
    }
  }

  priorityLabel(p: number): string {
    return PRIORITY_LABELS[p as TicketPriority] ?? '';
  }

  escalationState(escalationAt: string | null | undefined): 'breached' | 'warning' | 'none' {
    if (!escalationAt) return 'none';
    const diff = new Date(escalationAt).getTime() - Date.now();
    if (diff < 0) return 'breached';
    if (diff < 3600000) return 'warning';
    return 'none';
  }
}
