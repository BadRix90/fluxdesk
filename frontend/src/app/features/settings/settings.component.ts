import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { OrgService } from './org.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [FormsModule, DatePipe],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent implements OnInit {
  orgService = inject(OrgService);

  inviteEmail = '';
  inviteRole = 'AGENT';
  saveSuccess = signal(false);
  inviteSuccess = signal('');
  noOrg = signal(false);

  ngOnInit(): void {
    this.orgService.loadOrganization().subscribe({
      next: () => this.orgService.loadInvitations().subscribe(),
      error: () => this.noOrg.set(true),
    });
  }

  saveOrg(): void {
    const org = this.orgService.organization();
    if (!org) return;
    this.orgService.updateOrganization({
      name: org.name,
      support_email: org.support_email,
      website: org.website,
      signature_html: org.signature_html,
    }).subscribe(() => {
      this.saveSuccess.set(true);
      setTimeout(() => this.saveSuccess.set(false), 3000);
    });
  }

  sendInvite(): void {
    if (!this.inviteEmail.trim()) return;
    this.orgService.sendInvitation(
      this.inviteEmail, this.inviteRole
    ).subscribe(() => {
      this.inviteSuccess.set(this.inviteEmail);
      this.inviteEmail = '';
      this.orgService.loadInvitations().subscribe();
      setTimeout(() => this.inviteSuccess.set(''), 3000);
    });
  }

  deleteInvite(id: number): void {
    this.orgService.deleteInvitation(id).subscribe(() => {
      this.orgService.loadInvitations().subscribe();
    });
  }
}
