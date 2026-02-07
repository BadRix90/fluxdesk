import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { TicketService } from '../../services/ticket.service';
import { StatusBadgeComponent } from '../../../../shared/components/status-badge/status-badge.component';
import { PRIORITY_LABELS, type Ticket, type TicketPriority } from '../../../../core/models/ticket.model';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [DatePipe, FormsModule, StatusBadgeComponent],
  templateUrl: './ticket-detail.component.html',
  styleUrl: './ticket-detail.component.scss',
})
export class TicketDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  ticketService = inject(TicketService);

  commentText = '';
  isInternal = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.ticketService.loadTicket(id).subscribe();
  }

  get ticket(): Ticket | null {
    return this.ticketService.selectedTicket();
  }

  priorityLabel(p: number): string {
    return PRIORITY_LABELS[p as TicketPriority] ?? '';
  }

  assignToMe(): void {
    if (!this.ticket) return;
    this.ticketService.assignToMe(this.ticket.id).subscribe(
      t => this.ticketService.selectedTicket.set(t)
    );
  }

  resolve(): void {
    if (!this.ticket) return;
    this.ticketService.resolve(this.ticket.id).subscribe(
      t => this.ticketService.selectedTicket.set(t)
    );
  }

  close(): void {
    if (!this.ticket) return;
    this.ticketService.close(this.ticket.id).subscribe(
      t => this.ticketService.selectedTicket.set(t)
    );
  }

  addComment(): void {
    if (!this.ticket || !this.commentText.trim()) return;
    this.ticketService.addComment(
      this.ticket.id,
      this.commentText,
      this.isInternal()
    ).subscribe(() => {
      this.commentText = '';
      this.ticketService.loadTicket(this.ticket!.id).subscribe();
    });
  }

  goBack(): void {
    this.router.navigate(['/tickets']);
  }
}
