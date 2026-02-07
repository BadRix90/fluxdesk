import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import {
  type Invitation,
  type Organization,
} from '../../core/models/user.model';
import { type PaginatedResponse } from '../../core/models/ticket.model';

@Injectable({ providedIn: 'root' })
export class OrgService {
  private http = inject(HttpClient);

  organization = signal<Organization | null>(null);
  invitations = signal<Invitation[]>([]);

  loadOrganization(): Observable<Organization> {
    return this.http.get<Organization>('/api/organization/').pipe(
      tap(org => this.organization.set(org))
    );
  }

  updateOrganization(data: Partial<Organization>): Observable<Organization> {
    return this.http.patch<Organization>('/api/organization/', data).pipe(
      tap(org => this.organization.set(org))
    );
  }

  loadInvitations(): Observable<Invitation[]> {
    return this.http.get<PaginatedResponse<Invitation>>(
      '/api/invitations/'
    ).pipe(
      map(res => res.results),
      tap(invs => this.invitations.set(invs))
    );
  }

  sendInvitation(email: string, role: string): Observable<Invitation> {
    return this.http.post<Invitation>(
      '/api/invitations/', { email, role }
    );
  }

  deleteInvitation(id: number): Observable<void> {
    return this.http.delete<void>(`/api/invitations/${id}/`);
  }
}
