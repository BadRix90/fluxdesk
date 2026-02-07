import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { TicketService } from '../../services/ticket.service';

@Component({
  selector: 'app-ticket-create',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './ticket-create.component.html',
  styleUrl: './ticket-create.component.scss',
})
export class TicketCreateComponent {
  private router = inject(Router);
  private ticketService = inject(TicketService);

  subject = '';
  description = '';
  priority = 2;
  error = signal('');
  loading = signal(false);

  onSubmit(): void {
    this.loading.set(true);
    this.error.set('');

    this.ticketService.createTicket({
      subject: this.subject,
      description: this.description,
      priority: this.priority as 1 | 2 | 3 | 4,
    }).subscribe({
      next: (ticket) => {
        this.router.navigate(['/tickets', ticket.id]);
      },
      error: (err) => {
        const msg = this.extractError(err.error);
        this.error.set(msg);
        this.loading.set(false);
      },
    });
  }

  cancel(): void {
    this.router.navigate(['/tickets']);
  }

  private extractError(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object') {
      const values = Object.values(detail);
      const first = values[0];
      if (Array.isArray(first)) return first[0];
      if (typeof first === 'string') return first;
    }
    return 'Ticket konnte nicht erstellt werden.';
  }
}
