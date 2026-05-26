"""
Seed jenis layanan — aman dijalankan di production.

  python seed_services.py
"""

import json
from app.database import engine, SessionLocal
from app.database import Base
from app.models import User, ServiceType, Ticket  # noqa: F401

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
        for data in SERVICES:
            existing = db.query(ServiceType).filter(ServiceType.nama == data["nama"]).first()
            if existing:
                print(f"  [SKIP] Layanan '{data['nama']}' sudah ada.")
                continue
            db.add(ServiceType(**data))
            print(f"  [OK]   Layanan '{data['nama']}' ditambahkan.")
        db.commit()
        print("\nSeed layanan selesai.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
