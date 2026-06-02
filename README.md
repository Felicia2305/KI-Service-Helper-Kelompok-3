---
title: KI Service Helper
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# IPB Academic Service Helper
Backend API untuk layanan mahasiswa.

# KI-Academic-Service-Helper

Sistem manajemen layanan mahasiswa berbasis **FastAPI + PostgreSQL** dengan fitur autentikasi, antrian tiket, dan digital signature untuk keamanan data.

---

## 📁 Struktur Folder Repository

Struktur proyek mengikuti standar PBL sebagai berikut:
01_Proposal_&_Analisis/
├── Proposal_Teknis.pdf
└── Threat_Modeling.pdf

02_Design_Documents/
├── ERD_Modified.png
├── Architecture_Diagram.pdf
└── Testing_Plan.pdf

03_Source_Code/
├── backend/
│ ├── apps/
│ ├── main.py
│ ├── requirements.txt
│ └── .env.example
│
├── database/
│ └── schema.sql / migration files
│
└── digital_signature/
└── crypto utilities (encrypt/decrypt, signing)

04_Reports_&_Paper/
├── Monitoring_P7/
├── Final_Technical_Report/
└── Scientific_Paper/


---

## 🚀 Deskripsi Sistem

Sistem ini digunakan untuk:
- Pengajuan layanan mahasiswa
- Manajemen antrian tiket oleh staff
- Approval dan penyelesaian layanan
- Validasi keamanan menggunakan **digital signature**
- Upload dan verifikasi dokumen PDF

---

## ⚙️ Tech Stack

- FastAPI (Backend API)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Docker (Database container)
- Python JWT Authentication
- Cryptography (Digital Signature)

---

## API Endpoint
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

---

## 🔐 Fitur Keamanan
Role-based access control (Mahasiswa / Staff)
Digital signature untuk integritas tiket
Audit logging aktivitas penting

---

## 👥 Pembagian Tugas (sesuai PBL)
Benadeo → Analisis & proposal
Marcell → Design & architecture
Felicia → Backend + Database + Digital Signature
Tim (Bareng) → Report & Paper

---


## 🐘 Setup Database (Docker)

```bash id="dbpbl1"
docker run --name postgres-iash \
-e POSTGRES_USER=iash_user \
-e POSTGRES_PASSWORD=iash_pass \
-e POSTGRES_DB=iash_db \
-p 5432:5432 \
-d postgres:15

# Cara menjalankan backend

cd 03_Source_Code/backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

uvicorn main:app --reload
