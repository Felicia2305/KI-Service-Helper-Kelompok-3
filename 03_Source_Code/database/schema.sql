CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE user_role AS ENUM (
    'mahasiswa', 'staff_departemen', 'staff_fakultas', 'staff_ipb'
);

CREATE TYPE service_level AS ENUM (
    'departemen', 'fakultas', 'ipb'
);

CREATE TYPE ticket_status AS ENUM (
    'pending', 'claimed', 'approved', 'rejected', 'completed'
);

-- 1. Tabel User (Hashing & Salting)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Untuk Bcrypt
    nama TEXT NOT NULL,
    nim_nip TEXT NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabel Jenis Layanan
CREATE TABLE service_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama TEXT NOT NULL,
    deskripsi TEXT,
    level service_level NOT NULL,
    berkas_dibutuhkan TEXT
);

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_type_id UUID NOT NULL REFERENCES service_types(id),
    purpose_encrypted TEXT NOT NULL,
    notes_encrypted TEXT,
    file_path TEXT,
    status ticket_status DEFAULT 'pending',
    digital_signature TEXT,
    claimed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    ip_address VARCHAR(45),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contoh Data Awal untuk Layanan
INSERT INTO service_types (nama, deskripsi, level, berkas_dibutuhkan) VALUES
('Legalisir Ijazah', 'Pengajuan pengesahan dokumen akademik.', 'fakultas', '["Fotokopi Ijazah","Fotokopi KTM"]'),
('Surat Keterangan Aktif Kuliah', 'Surat resmi status mahasiswa aktif.', 'departemen', '["Scan KRS","Fotokopi KTM"]'),
('Cuti Akademik', 'Permohonan cuti sementara dari perkuliahan.', 'departemen', '["Surat permohonan","Fotokopi KTM"]');
