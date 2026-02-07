import { Component, input } from '@angular/core';

import {
  type TicketStatus,
  STATUS_LABELS,
} from '../../../core/models/ticket.model';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  template: `
    <span class="badge" [attr.data-status]="status()">
      {{ label() }}
    </span>
  `,
  styles: [`
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.025em;
    }
    [data-status="NEW"]      { background: #DBEAFE; color: #1D4ED8; }
    [data-status="OPEN"]     { background: #FFF3E0; color: #E65100; }
    [data-status="WAITING"]  { background: #F5F5F5; color: #616161; }
    [data-status="RESOLVED"] { background: #E8F5E9; color: #2E7D32; }
    [data-status="CLOSED"]   { background: #EEEEEE; color: #424242; }
  `],
})
export class StatusBadgeComponent {
  status = input.required<TicketStatus>();

  label() {
    return STATUS_LABELS[this.status()];
  }
}
