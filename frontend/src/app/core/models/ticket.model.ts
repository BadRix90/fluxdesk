import { User } from './user.model';

export type TicketStatus = 'NEW' | 'OPEN' | 'WAITING' | 'RESOLVED' | 'CLOSED';
export type TicketPriority = 1 | 2 | 3 | 4;

export interface Ticket {
  id: number;
  ticket_number: number;
  display_number?: string;
  subject: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  customer: User;
  assignee: User | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  closed_at: string | null;
  comments: Comment[];
  attachments: Attachment[];
  comment_count?: number;
  sla?: { id: number; name: string } | null;
  escalation_at?: string | null;
  first_response_at?: string | null;
  first_response_deadline?: string | null;
  next_response_deadline?: string | null;
  resolution_deadline?: string | null;
  last_agent_response_at?: string | null;
  last_customer_response_at?: string | null;
}

export interface Comment {
  id: number;
  ticket: number;
  author: User;
  text: string;
  is_internal: boolean;
  created_at: string;
  edited_at: string | null;
}

export interface Attachment {
  id: number;
  ticket: number;
  file: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  uploaded_by: User;
  created_at: string;
}

export interface TicketCreatePayload {
  customer_email: string;
  subject: string;
  description: string;
  priority: TicketPriority;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const PRIORITY_LABELS: Record<TicketPriority, string> = {
  1: 'Low',
  2: 'Normal',
  3: 'High',
  4: 'Critical',
};

export const STATUS_LABELS: Record<TicketStatus, string> = {
  NEW: 'Neu',
  OPEN: 'Offen',
  WAITING: 'Wartend',
  RESOLVED: 'Gelöst',
  CLOSED: 'Geschlossen',
};
