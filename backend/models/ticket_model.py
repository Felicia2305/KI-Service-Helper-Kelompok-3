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
    purpose = Column(Text, nullable=False)
    file_syarat_path = Column(String(500), nullable=True)
    # NULL = belum diambil siapapun (masih di pool antrean)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
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

    mahasiswa = relationship("User", foreign_keys=[mahasiswa_id], back_populates="submitted_tickets")
    assigned_staff = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    service_type = relationship("ServiceType", back_populates="tickets")
