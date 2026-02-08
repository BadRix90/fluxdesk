export interface BusinessCalendar {
  id: number;
  timezone: string;
  business_hours: Record<string, string[][]>;
  holidays: Record<string, string>;
}

export interface SLA {
  id: number;
  name: string;
  position: number;
  is_active: boolean;
  priority_filter: number[];
  first_response_minutes: number | null;
  next_response_minutes: number | null;
  resolution_minutes: number | null;
}

export const DAY_LABELS: Record<string, string> = {
  mon: 'Montag',
  tue: 'Dienstag',
  wed: 'Mittwoch',
  thu: 'Donnerstag',
  fri: 'Freitag',
  sat: 'Samstag',
  sun: 'Sonntag',
};

export const DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

export const TIMEZONE_OPTIONS = [
  'Europe/Berlin',
  'Europe/Vienna',
  'Europe/Zurich',
  'Europe/London',
  'Europe/Paris',
  'Europe/Amsterdam',
  'Europe/Madrid',
  'Europe/Rome',
  'Europe/Warsaw',
  'Europe/Prague',
  'UTC',
];
