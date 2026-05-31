"""
Seed script — jalankan sekali untuk isi data awal:
  python seed.py

Yang di-seed:
  - 2 demo user (mahasiswa + staff)
  - 4 jenis layanan sesuai ApplyTicket.tsx
"""

import json
from app.database import engine, SessionLocal
from app.database import Base
from app.models import User, ServiceType, Ticket  # noqa: F401 — daftarkan semua model
from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USERS = [
    {
        "email": "mahasiswa_demo@apps.ipb.ac.id",
        "password": "mahasiswa123",
        "nama": "Mahasiswa Demo",
        "nim_nip": "G640001",
        "role": "mahasiswa",
    },
    {
        "email": "staff_demo@apps.ipb.ac.id",
        "password": "admin123",
        "nama": "Staf TU Demo",
        "nim_nip": "196701011994031001",
        "role": "staff_departemen",
    },
]

SERVICES = [
    {
        "nama": "Surat Keterangan Mahasiswa Aktif",
        "deskripsi": "Surat resmi yang menyatakan status mahasiswa aktif semester ini.",
        "level": "departemen",
        "berkas_dibutuhkan": json.dumps(["Scan KRS semester berjalan", "Fotokopi KTM aktif"]),
    },
    {
        "nama": "Legalisir Ijazah / Transkrip",
        "deskripsi": "Pengajuan pengesahan fotokopi dokumen akademik.",
        "level": "fakultas",
        "berkas_dibutuhkan": json.dumps([
            "Fotokopi Ijazah / Transkrip (min. resolusi 300dpi)",
            "Fotokopi KTM aktif",
            "Surat permohonan legalisir",
        ]),
    },
    {
        "nama": "Permohonan Cuti Akademik",
        "deskripsi": "Pengajuan cuti sementara dari kegiatan perkuliahan.",
        "level": "departemen",
        "berkas_dibutuhkan": json.dumps([
            "Surat permohonan cuti bermaterai",
            "Fotokopi KTM aktif",
            "Bukti pembayaran UKT semester terakhir",
        ]),
    },
    {
        "nama": "Permohonan Undur Diri",
        "deskripsi": "Prosedur resmi untuk berhenti menjadi mahasiswa IPB.",
        "level": "ipb",
        "berkas_dibutuhkan": json.dumps([
            "Surat permohonan undur diri bermaterai",
            "Fotokopi KTM",
            "Surat persetujuan orang tua/wali",
            "Bukti bebas tanggungan perpustakaan",
        ]),
    },
]


def run():
    print("Membuat tabel...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed_users(db)
        _seed_services(db)
        print("\nSeed selesai.")
    finally:
        db.close()


def _seed_users(db):
    for data in DEMO_USERS:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            print(f"  [SKIP] User {data['email']} sudah ada.")
            continue
        user = User(
            email=data["email"],
            password_hash=_pwd.hash(data["password"]),
            nama=data["nama"],
            nim_nip=data["nim_nip"],
            role=data["role"],
        )
        db.add(user)
        print(f"  [OK]   User {data['email']} ditambahkan.")
    db.commit()


def _seed_services(db):
    for data in SERVICES:
        existing = db.query(ServiceType).filter(ServiceType.nama == data["nama"]).first()
        if existing:
            print(f"  [SKIP] Layanan '{data['nama']}' sudah ada.")
            continue
        service = ServiceType(**data)
        db.add(service)
        print(f"  [OK]   Layanan '{data['nama']}' ditambahkan.")
    db.commit()


if __name__ == "__main__":
    run()
