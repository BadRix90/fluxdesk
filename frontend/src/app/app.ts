import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterOutlet, NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

import { AuthService } from './core/services/auth.service';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  host: { '[attr.data-theme]': 'theme()' },
})
export class App implements OnInit {
  auth = inject(AuthService);
  private router = inject(Router);

  theme = signal<'light' | 'dark'>(this.loadTheme());
  sidebarOpen = signal(false);
  menuIcon = '\u2630';

  ngOnInit(): void {
    if (this.auth.isAuthenticated()) {
      this.auth.fetchMe();
    }
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd),
    ).subscribe(() => this.sidebarOpen.set(false));
  }

  toggleTheme(): void {
    const next = this.theme() === 'light' ? 'dark' : 'light';
    this.theme.set(next);
    localStorage.setItem('flux-theme', next);
  }

  toggleSidebar(): void {
    this.sidebarOpen.update(v => !v);
  }

  private loadTheme(): 'light' | 'dark' {
    const saved = localStorage.getItem('flux-theme');
    if (saved === 'light' || saved === 'dark') {
      return saved;
    }
    const prefersDark = window.matchMedia(
      '(prefers-color-scheme: dark)',
    ).matches;
    return prefersDark ? 'dark' : 'light';
  }
}
