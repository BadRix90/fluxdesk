import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  private auth = inject(AuthService);

  orgName = '';
  supportEmail = '';
  username = '';
  email = '';
  password = '';
  firstName = '';
  lastName = '';
  error = signal('');
  loading = signal(false);
  success = signal(false);

  onSubmit(): void {
    this.loading.set(true);
    this.error.set('');

    this.auth.register({
      org_name: this.orgName,
      support_email: this.supportEmail,
      username: this.username,
      email: this.email,
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
    return 'Registrierung fehlgeschlagen.';
  }
}
