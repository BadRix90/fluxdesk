import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-accept-invite',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './accept-invite.component.html',
  styleUrl: './accept-invite.component.scss',
})
export class AcceptInviteComponent {
  private route = inject(ActivatedRoute);
  private auth = inject(AuthService);
  private router = inject(Router);

  username = '';
  firstName = '';
  lastName = '';
  password = '';
  error = signal('');
  loading = signal(false);
  success = signal(false);

  onSubmit(): void {
    this.loading.set(true);
    this.error.set('');

    const token = this.route.snapshot.paramMap.get('token') ?? '';
    this.auth.acceptInvitation({
      token,
      username: this.username,
      password: this.password,
      first_name: this.firstName,
      last_name: this.lastName,
    }).subscribe({
      next: () => {
        this.success.set(true);
        this.loading.set(false);
      },
      error: (err) => {
        const detail = err.error;
        const msg = this.extractError(detail);
        this.error.set(msg);
        this.loading.set(false);
      },
    });
  }

  private extractError(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object') {
      const values = Object.values(detail);
      const first = values[0];
      if (Array.isArray(first)) return first[0];
      if (typeof first === 'string') return first;
    }
    return 'Einladung konnte nicht angenommen werden.';
  }
}
