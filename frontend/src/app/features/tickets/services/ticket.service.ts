import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import {
  type Ticket,
  type Comment,
  type PaginatedResponse,
} from '../../../core/models/ticket.model';

@Injectable({ providedIn: 'root' })
export class TicketService {
  private http = inject(HttpClient);
  private baseUrl = '/api/tickets';

  tickets = signal<Ticket[]>([]);
  selectedTicket = signal<Ticket | null>(null);
  totalCount = signal(0);
  loading = signal(false);

  loadTickets(params?: HttpParams): Observable<PaginatedResponse<Ticket>> {
    this.loading.set(true);
    return this.http.get<PaginatedResponse<Ticket>>(
      `${this.baseUrl}/`, { params }
    ).pipe(
      tap(res => {
        this.tickets.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      })
    );
  }

  loadTicket(id: number): Observable<Ticket> {
    return this.http.get<Ticket>(
      `${this.baseUrl}/${id}/`
    ).pipe(
      tap(ticket => this.selectedTicket.set(ticket))
    );
  }

  createTicket(data: Partial<Ticket>): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/`, data);
  }

  assignToMe(id: number): Observable<Ticket> {
    return this.http.post<Ticket>(
      `${this.baseUrl}/${id}/assign_to_me/`, {}
    );
  }

  resolve(id: number): Observable<Ticket> {
    return this.http.post<Ticket>(
      `${this.baseUrl}/${id}/resolve/`, {}
    );
  }

  close(id: number): Observable<Ticket> {
    return this.http.post<Ticket>(
      `${this.baseUrl}/${id}/close/`, {}
    );
  }

  addComment(id: number, text: string, isInternal = false): Observable<Comment> {
    return this.http.post<Comment>(
      `${this.baseUrl}/${id}/comment/`,
      { text, is_internal: isInternal }
    );
  }

  loadMyQueue(): Observable<PaginatedResponse<Ticket>> {
    this.loading.set(true);
    return this.http.get<PaginatedResponse<Ticket>>(
      `${this.baseUrl}/my_queue/`
    ).pipe(
      tap(res => {
        this.tickets.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      })
    );
  }

  loadUnassigned(): Observable<PaginatedResponse<Ticket>> {
    this.loading.set(true);
    return this.http.get<PaginatedResponse<Ticket>>(
      `${this.baseUrl}/unassigned/`
    ).pipe(
      tap(res => {
        this.tickets.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      })
    );
  }

  loadEscalated(): Observable<PaginatedResponse<Ticket>> {
    this.loading.set(true);
    return this.http.get<PaginatedResponse<Ticket>>(
      `${this.baseUrl}/escalated/`
    ).pipe(
      tap(res => {
        this.tickets.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      })
    );
  }
}
