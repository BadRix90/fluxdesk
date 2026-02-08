import { Component, computed, inject, input, output } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { LucideAngularModule, Inbox, User, ClipboardList, Flame, Settings, Sun, Moon, LogOut } from 'lucide-angular';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, LucideAngularModule],
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

  readonly icons = { Inbox, User, ClipboardList, Flame, Settings, Sun, Moon, LogOut };

  navItems = [
    { label: 'Alle Tickets', route: '/tickets', icon: Inbox },
    { label: 'Meine Queue', route: '/tickets/my-queue', icon: User },
    { label: 'Nicht zugewiesen', route: '/tickets/unassigned', icon: ClipboardList },
    { label: 'Eskaliert', route: '/tickets/escalated', icon: Flame },
    { label: 'Einstellungen', route: '/settings', icon: Settings },
  ];

  themeIcon = computed(() => this.theme() === 'light' ? Moon : Sun);

  initials = computed(() => {
    const user = this.auth.currentUser();
    if (!user) return '?';
    const first = user.first_name?.[0] ?? '';
    const last = user.last_name?.[0] ?? '';
    return (first + last).toUpperCase() || '?';
  });
}
