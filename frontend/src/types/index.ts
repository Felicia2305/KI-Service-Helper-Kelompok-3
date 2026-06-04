export type Role = 'mahasiswa' | 'staff_departemen' | 'staff_fakultas' | 'staff_ipb';

export type User = {
  id: string;
  email: string;
  nama: string;
  nim_nip: string;
  role: Role;
  is_active: boolean;
  created_at: string;
};

export type ServiceType = {
  id: string;
  nama: string;
  deskripsi?: string | null;
  level: string;
  berkas_dibutuhkan: string[];
};

export type TicketStatus = 'pending' | 'claimed' | 'approved' | 'rejected' | 'completed';

export type Ticket = {
  id: string;
  status: TicketStatus;
  purpose: string;
  notes?: string | null;
  catatan_tu?: string | null;
  file_syarat_path?: string | null;
  file_hasil_path?: string | null;
  file_path?: string | null;
  digital_signature?: string | null;
  created_at: string;
  updated_at: string;
  mahasiswa: User;
  service_type: ServiceType;
  assigned_staff?: User | null;
};

export type AuditLog = {
  id: string;
  user_id?: string | null;
  action: string;
  resource?: string | null;
  ip_address?: string | null;
  details?: Record<string, unknown>;
  created_at: string;
};

export type IntegrityResult = {
  valid: boolean;
  message: string;
};
