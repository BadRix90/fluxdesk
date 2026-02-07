export interface User {
  id: number;
  username: string;
  display_name: string;
  role: 'ADMIN' | 'AGENT' | 'CUSTOMER';
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'AGENT' | 'CUSTOMER';
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  support_email: string;
  website: string;
  logo: string | null;
  signature_html: string;
  is_active: boolean;
  created_at: string;
}

export interface Invitation {
  id: number;
  email: string;
  role: string;
  status: 'PENDING' | 'ACCEPTED' | 'EXPIRED';
  created_at: string;
  expires_at: string;
  accepted_at: string | null;
}

export interface MessageResponse {
  message: string;
}
