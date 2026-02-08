import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { OrgService } from './org.service';
import { SlaService } from './sla.service';
import {
  DAY_KEYS, DAY_LABELS, TIMEZONE_OPTIONS,
} from '../../core/models/sla.model';
import { PRIORITY_LABELS } from '../../core/models/ticket.model';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [FormsModule, DatePipe],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent implements OnInit {
  orgService = inject(OrgService);
  slaService = inject(SlaService);

  inviteEmail = '';
  inviteRole = 'AGENT';
  saveSuccess = signal(false);
  inviteSuccess = signal('');
  calendarSuccess = signal(false);
  slaSuccess = signal('');
  noOrg = signal(false);

  dayKeys = DAY_KEYS;
  dayLabels = DAY_LABELS;
  timezones = TIMEZONE_OPTIONS;
  priorityLabels = PRIORITY_LABELS;

  newHolidayDate = '';
  newHolidayName = '';

  newSlaName = '';
  newSlaPosition = 0;
  newSlaFirstResponse: number | null = null;
  newSlaNextResponse: number | null = null;
  newSlaResolution: number | null = null;
  newSlaPriorities = signal<number[]>([]);
  editingSlaId = signal<number | null>(null);

  ngOnInit(): void {
    this.orgService.loadOrganization().subscribe({
      next: () => {
        this.orgService.loadInvitations().subscribe();
        this.slaService.loadCalendar().subscribe();
        this.slaService.loadSlaRules().subscribe();
      },
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

  /* ── Business Calendar ─────────────────────── */

  getDayStart(day: string): string {
    const cal = this.slaService.calendar();
    const windows = cal?.business_hours?.[day];
    return windows?.[0]?.[0] ?? '';
  }

  getDayEnd(day: string): string {
    const cal = this.slaService.calendar();
    const windows = cal?.business_hours?.[day];
    return windows?.[0]?.[1] ?? '';
  }

  setDayHours(day: string, start: string, end: string): void {
    const cal = this.slaService.calendar();
    if (!cal) return;
    const hours = { ...cal.business_hours };
    hours[day] = start && end ? [[start, end]] : [];
    this.slaService.calendar.set({ ...cal, business_hours: hours });
  }

  setTimezone(tz: string): void {
    const cal = this.slaService.calendar();
    if (!cal) return;
    this.slaService.calendar.set({ ...cal, timezone: tz });
  }

  addHoliday(): void {
    if (!this.newHolidayDate || !this.newHolidayName) return;
    const cal = this.slaService.calendar();
    if (!cal) return;
    const holidays = { ...cal.holidays };
    holidays[this.newHolidayDate] = this.newHolidayName;
    this.slaService.calendar.set({ ...cal, holidays });
    this.newHolidayDate = '';
    this.newHolidayName = '';
  }

  removeHoliday(date: string): void {
    const cal = this.slaService.calendar();
    if (!cal) return;
    const holidays = { ...cal.holidays };
    delete holidays[date];
    this.slaService.calendar.set({ ...cal, holidays });
  }

  holidayEntries(): [string, string][] {
    const cal = this.slaService.calendar();
    if (!cal?.holidays) return [];
    return Object.entries(cal.holidays).sort();
  }

  saveCalendar(): void {
    const cal = this.slaService.calendar();
    if (!cal) return;
    this.slaService.updateCalendar({
      timezone: cal.timezone,
      business_hours: cal.business_hours,
      holidays: cal.holidays,
    }).subscribe(() => {
      this.calendarSuccess.set(true);
      setTimeout(() => this.calendarSuccess.set(false), 3000);
    });
  }

  /* ── SLA Rules ─────────────────────────────── */

  toggleNewSlaPriority(priority: number): void {
    this.newSlaPriorities.update(current => {
      return current.includes(priority)
        ? current.filter(p => p !== priority)
        : [...current, priority];
    });
  }

  createSla(): void {
    if (!this.newSlaName.trim()) return;
    this.slaService.createSla({
      name: this.newSlaName,
      position: this.newSlaPosition,
      is_active: true,
      priority_filter: this.newSlaPriorities(),
      first_response_minutes: this.newSlaFirstResponse,
      next_response_minutes: this.newSlaNextResponse,
      resolution_minutes: this.newSlaResolution,
    }).subscribe(() => {
      this.slaSuccess.set(this.newSlaName);
      this.resetSlaForm();
      setTimeout(() => this.slaSuccess.set(''), 3000);
    });
  }

  deleteSla(id: number): void {
    this.slaService.deleteSla(id).subscribe();
  }

  toggleSlaActive(id: number, isActive: boolean): void {
    this.slaService.updateSla(id, {
      is_active: !isActive,
    }).subscribe();
  }

  formatMinutes(minutes: number | null): string {
    if (minutes === null) return '–';
    if (minutes < 60) return `${minutes}m`;
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }

  priorityChips(filter: number[]): string {
    return filter
      .map(p => this.priorityLabels[p as 1|2|3|4] ?? `P${p}`)
      .join(', ');
  }

  private resetSlaForm(): void {
    this.newSlaName = '';
    this.newSlaPosition = 0;
    this.newSlaFirstResponse = null;
    this.newSlaNextResponse = null;
    this.newSlaResolution = null;
    this.newSlaPriorities.set([]);
  }
}
