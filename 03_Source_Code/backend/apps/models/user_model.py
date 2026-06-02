import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nama = Column(String(255), nullable=False)
    nim_nip = Column(String(50), nullable=False)
    role = Column(
        Enum("mahasiswa", "staff_departemen", "staff_fakultas", "staff_ipb", name="user_role"),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    submitted_tickets = relationship(
        "Ticket", foreign_keys="Ticket.mahasiswa_id", back_populates="mahasiswa"
    )
    assigned_tickets = relationship(
        "Ticket", foreign_keys="Ticket.assigned_to", back_populates="assigned_staff"
    )
