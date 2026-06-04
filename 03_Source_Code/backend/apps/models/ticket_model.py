import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service_type_id = Column(UUID(as_uuid=True), ForeignKey("service_types.id"), nullable=False)
    
    status = Column(
        Enum(
            "pending",
            "claimed",
            "approved",
            "rejected",
            "completed",
            name="ticket_status",
        ),
        default="pending",
        nullable=False,
    )

    # KEAMANAN: Kolom ini akan menyimpan data hasil enkripsi (AES/Fernet)
    purpose_encrypted = Column(Text, nullable=False)
    notes_encrypted = Column(Text, nullable=True)
    
    # KEAMANAN: Kolom ini menyimpan Digital Signature (RSA/ECDSA) 
    # Menjamin Integrity & Non-repudiation
    digital_signature = Column(Text, nullable=True)

    file_path = Column(String(500), nullable=True)
    claimed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
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
    mahasiswa = relationship("User", foreign_keys=[user_id], back_populates="submitted_tickets")
    assigned_staff = relationship("User", foreign_keys=[claimed_by], back_populates="assigned_tickets")
    service_type = relationship("ServiceType", back_populates="tickets")

    @property
    def mahasiswa_id(self):
        return self.user_id

    @property
    def assigned_to(self):
        return self.claimed_by

    @property
    def purpose(self):
        return getattr(self, "_purpose_plain", self.purpose_encrypted)

    @purpose.setter
    def purpose(self, value):
        self._purpose_plain = value

    @property
    def notes(self):
        return getattr(self, "_notes_plain", self.notes_encrypted)

    @notes.setter
    def notes(self, value):
        self._notes_plain = value

    @property
    def catatan_tu(self):
        return self.notes

    @catatan_tu.setter
    def catatan_tu(self, value):
        self.notes = value

    @property
    def file_syarat_path(self):
        return self.file_path

    @property
    def file_hasil_path(self):
        return self.file_path

    @property
    def signature(self):
        return self.digital_signature
