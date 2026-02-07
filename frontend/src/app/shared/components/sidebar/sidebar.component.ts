import { Component, computed, inject, input, output } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
  host: { '[class.mobile-open]': 'mobileOpen()' },
})
export class SidebarComponent {
  auth = inject(AuthService);
  theme = input<'light' | 'dark'>('light');
  mobileOpen = input(false);
  themeToggle = output<void>();
  closeSidebar = output<void>();

  navItems = [
    { label: 'Alle Tickets', route: '/tickets', icon: '\u{1F4E5}' },
    { label: 'Meine Queue', route: '/tickets/my-queue', icon: '\u{1F464}' },
    { label: 'Nicht zugewiesen', route: '/tickets/unassigned', icon: '\u{1F4CB}' },
    { label: 'Eskaliert', route: '/tickets/escalated', icon: '\u{1F525}' },
    { label: 'Einstellungen', route: '/settings', icon: '\u2699\uFE0F' },
  ];

  themeIcon = computed(() => this.theme() === 'light' ? '\u263E' : '\u2600');

  initials = computed(() => {
    const user = this.auth.currentUser();
    if (!user) return '?';
    const first = user.first_name?.[0] ?? '';
    const last = user.last_name?.[0] ?? '';
    return (first + last).toUpperCase() || '?';
  });
}
