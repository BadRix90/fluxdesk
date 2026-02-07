import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  auth = inject(AuthService);

  navItems = [
    { label: 'Alle Tickets', route: '/tickets', icon: 'inbox' },
    { label: 'Meine Queue', route: '/tickets/my-queue', icon: 'user' },
    { label: 'Nicht zugewiesen', route: '/tickets/unassigned', icon: 'alert' },
    { label: 'Eskaliert', route: '/tickets/escalated', icon: 'fire' },
    { label: 'Einstellungen', route: '/settings', icon: 'settings' },
  ];
}
