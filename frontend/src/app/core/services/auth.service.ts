import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, Observable, of, tap } from 'rxjs';

import {
  type AuthTokens,
  type MessageResponse,
  type UserProfile,
} from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  accessToken = signal<string | null>(
    localStorage.getItem('access_token')
  );
  currentUser = signal<UserProfile | null>(null);

  isAuthenticated = computed(() => !!this.accessToken());

  login(username: string, password: string): Observable<AuthTokens> {
    return this.http.post<AuthTokens>('/api/auth/token/', {
      username,
      password,
    }).pipe(
      tap(tokens => {
        this.storeTokens(tokens);
        this.fetchMe();
      })
    );
  }

  fetchMe(): void {
    this.http.get<UserProfile>('/api/me/').subscribe({
      next: (user) => this.currentUser.set(user),
      error: () => this.currentUser.set(null),
    });
  }

  validateSession(): Observable<UserProfile | null> {
    return this.http.get<UserProfile>('/api/me/').pipe(
      tap(user => this.currentUser.set(user)),
      catchError(() => {
        this.logout();
        return of(null);
      }),
    );
  }

  register(data: {
    org_name: string;
    support_email: string;
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Observable<MessageResponse> {
    return this.http.post<MessageResponse>('/api/register/', data);
  }

  verifyEmail(token: string): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(
      '/api/verify-email/', { token }
    );
  }

  acceptInvitation(data: {
    token: string;
    username: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(
      '/api/accept-invitation/', data
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.accessToken.set(null);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<AuthTokens> {
    const refresh = localStorage.getItem('refresh_token');
    return this.http.post<AuthTokens>('/api/auth/token/refresh/', {
      refresh,
    }).pipe(
      tap(tokens => this.storeTokens(tokens))
    );
  }

  private storeTokens(tokens: { access: string; refresh: string }): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    this.accessToken.set(tokens.access);
  }
}
