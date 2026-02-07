import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register.component').then(m => m.RegisterComponent),
  },
  {
    path: 'verify/:token',
    loadComponent: () =>
      import('./features/auth/verify-email.component').then(m => m.VerifyEmailComponent),
  },
  {
    path: 'invite/:token',
    loadComponent: () =>
      import('./features/auth/accept-invite.component').then(m => m.AcceptInviteComponent),
  },
  {
    path: 'tickets',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./features/tickets/components/ticket-list/ticket-list.component')
            .then(m => m.TicketListComponent),
      },
      {
        path: 'my-queue',
        loadComponent: () =>
          import('./features/tickets/components/ticket-list/ticket-list.component')
            .then(m => m.TicketListComponent),
        data: { filter: 'my-queue' },
      },
      {
        path: 'unassigned',
        loadComponent: () =>
          import('./features/tickets/components/ticket-list/ticket-list.component')
            .then(m => m.TicketListComponent),
        data: { filter: 'unassigned' },
      },
      {
        path: 'escalated',
        loadComponent: () =>
          import('./features/tickets/components/ticket-list/ticket-list.component')
            .then(m => m.TicketListComponent),
        data: { filter: 'escalated' },
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./features/tickets/components/ticket-detail/ticket-detail.component')
            .then(m => m.TicketDetailComponent),
      },
    ],
  },
  {
    path: 'settings',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/settings/settings.component').then(m => m.SettingsComponent),
  },
  { path: '', redirectTo: 'tickets', pathMatch: 'full' },
  { path: '**', redirectTo: 'tickets' },
];
