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
      <span class="badge-dot"></span>
      {{ label() }}
    </span>
  `,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 2px 10px 2px 8px;
      border-radius: 999px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .badge-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    [data-status="NEW"]      { background: rgba(99,102,241,0.1); color: #4F46E5; }
    [data-status="NEW"] .badge-dot { background: #6366F1; }
    [data-status="OPEN"]     { background: rgba(245,158,11,0.1); color: #D97706; }
    [data-status="OPEN"] .badge-dot { background: #F59E0B; }
    [data-status="WAITING"]  { background: rgba(100,116,139,0.1); color: #64748B; }
    [data-status="WAITING"] .badge-dot { background: #94A3B8; }
    [data-status="RESOLVED"] { background: rgba(16,185,129,0.1); color: #059669; }
    [data-status="RESOLVED"] .badge-dot { background: #10B981; }
    [data-status="CLOSED"]   { background: rgba(113,113,122,0.1); color: #52525B; }
    [data-status="CLOSED"] .badge-dot { background: #71717A; }
  `],
})
export class StatusBadgeComponent {
  status = input.required<TicketStatus>();

  label() {
    return STATUS_LABELS[this.status()];
  }
}
