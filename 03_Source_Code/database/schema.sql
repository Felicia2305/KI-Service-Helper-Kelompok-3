-- 1. Tabel User (Hashing & Salting)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Untuk Bcrypt
    nama TEXT NOT NULL,
    nim_nip TEXT,
    role TEXT CHECK (role IN ('mahasiswa', 'staff')) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabel Jenis Layanan
CREATE TABLE service_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    level TEXT NOT NULL -- Misal: 'TU', 'Dekanat'
);

-- 3. Tabel Tiket (Encryption & Digital Signature)
CREATE TYPE ticket_status AS ENUM (
    'dalam_antrean', 'diproses', 'dalam_pembuatan', 'ditolak', 'selesai'
);

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mahasiswa_id UUID REFERENCES users(id),
    service_type_id UUID REFERENCES service_types(id),
    status ticket_status DEFAULT 'dalam_antrean',
    
    -- DATA SENSITIF TERENKRIPSI (AES)
    purpose TEXT NOT NULL, 
    catatan_tu TEXT, 
    
    -- INTEGRITY & NON-REPUDIATION (RSA Signature)
    signature TEXT, 
    
    file_syarat_path TEXT,
    file_hasil_path TEXT,
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contoh Data Awal untuk Layanan
INSERT INTO service_types (name, level) VALUES 
('Legalisir Ijazah', 'TU'),
('Surat Keterangan Aktif Kuliah', 'TU'),
('Cuti Akademik', 'Dekanat');