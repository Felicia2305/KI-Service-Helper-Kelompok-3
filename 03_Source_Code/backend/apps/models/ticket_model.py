import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mahasiswa_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service_type_id = Column(UUID(as_uuid=True), ForeignKey("service_types.id"), nullable=False)
    
    status = Column(
        Enum(
            "dalam_antrean",
            "diproses",
            "dalam_pembuatan",
            "ditolak",
            "selesai",
            name="ticket_status",
        ),
        default="dalam_antrean",
        nullable=False,
    )

    # KEAMANAN: Kolom ini akan menyimpan data hasil enkripsi (AES/Fernet)
    purpose = Column(Text, nullable=False) 
    
    # KEAMANAN: Kolom ini menyimpan Digital Signature (RSA/ECDSA) 
    # Menjamin Integrity & Non-repudiation
    signature = Column(Text, nullable=True)

    file_syarat_path = Column(String(500), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # KEAMANAN: Catatan staf juga sebaiknya dienkripsi agar privasi terjaga
    catatan_tu = Column(Text, nullable=True) 
    
    file_hasil_path = Column(String(500), nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    mahasiswa = relationship("User", foreign_keys=[mahasiswa_id], back_populates="submitted_tickets")
    assigned_staff = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    service_type = relationship("ServiceType", back_populates="tickets")