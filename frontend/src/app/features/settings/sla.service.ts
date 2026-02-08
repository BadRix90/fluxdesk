import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import {
  type BusinessCalendar,
  type SLA,
} from '../../core/models/sla.model';
import { type PaginatedResponse } from '../../core/models/ticket.model';

@Injectable({ providedIn: 'root' })
export class SlaService {
  private http = inject(HttpClient);

  calendar = signal<BusinessCalendar | null>(null);
  slaRules = signal<SLA[]>([]);

  loadCalendar(): Observable<BusinessCalendar> {
    return this.http.get<BusinessCalendar>(
      '/api/business-calendar/'
    ).pipe(
      tap(cal => this.calendar.set(cal))
    );
  }

  updateCalendar(data: Partial<BusinessCalendar>): Observable<BusinessCalendar> {
    return this.http.patch<BusinessCalendar>(
      '/api/business-calendar/', data
    ).pipe(
      tap(cal => this.calendar.set(cal))
    );
  }

  loadSlaRules(): Observable<SLA[]> {
    return this.http.get<PaginatedResponse<SLA>>(
      '/api/sla/'
    ).pipe(
      map(res => res.results),
      tap(rules => this.slaRules.set(rules))
    );
  }

  createSla(data: Partial<SLA>): Observable<SLA> {
    return this.http.post<SLA>('/api/sla/', data).pipe(
      tap(sla => this.slaRules.update(
        rules => [...rules, sla]
      ))
    );
  }

  updateSla(id: number, data: Partial<SLA>): Observable<SLA> {
    return this.http.patch<SLA>(
      `/api/sla/${id}/`, data
    ).pipe(
      tap(updated => this.slaRules.update(
        rules => rules.map(r => r.id === id ? updated : r)
      ))
    );
  }

  deleteSla(id: number): Observable<void> {
    return this.http.delete<void>(`/api/sla/${id}/`).pipe(
      tap(() => this.slaRules.update(
        rules => rules.filter(r => r.id !== id)
      ))
    );
  }
}
