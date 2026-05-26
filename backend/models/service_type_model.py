import uuid
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class ServiceType(Base):
    __tablename__ = "service_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama = Column(String(255), nullable=False)
    deskripsi = Column(Text, nullable=True)
    level = Column(
        Enum("departemen", "fakultas", "ipb", name="service_level"),
        nullable=False,
    )
    # JSON array disimpan sebagai string, e.g. '["Fotokopi KTM","Scan KRS"]'
    berkas_dibutuhkan = Column(Text, nullable=True)

    tickets = relationship("Ticket", back_populates="service_type")
