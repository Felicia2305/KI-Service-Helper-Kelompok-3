"""
Seed akun demo — HANYA untuk development/staging, JANGAN dijalankan di production.

  python seed_demo.py
"""

from app.database import engine, SessionLocal
from app.database import Base
from app.models import User, ServiceType, Ticket  # noqa: F401
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


def run():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for data in DEMO_USERS:
            existing = db.query(User).filter(User.email == data["email"]).first()
            if existing:
                print(f"  [SKIP] User {data['email']} sudah ada.")
                continue
            db.add(User(
                email=data["email"],
                password_hash=_pwd.hash(data["password"]),
                nama=data["nama"],
                nim_nip=data["nim_nip"],
                role=data["role"],
            ))
            print(f"  [OK]   User {data['email']} ditambahkan.")
        db.commit()
        print("\nSeed demo users selesai.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
