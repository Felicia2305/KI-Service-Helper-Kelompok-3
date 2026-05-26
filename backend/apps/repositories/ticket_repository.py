from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.ticket_model import Ticket
from ..models.service_type_model import ServiceType


class TicketRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self._db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_by_mahasiswa(self, mahasiswa_id: UUID) -> list[Ticket]:
        return (
            self._db.query(Ticket)
            .filter(Ticket.mahasiswa_id == mahasiswa_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    def get_all(self, status_filter: str | None = None) -> list[Ticket]:
        query = self._db.query(Ticket)
        if status_filter:
            query = query.filter(Ticket.status == status_filter)
        return query.order_by(Ticket.created_at.desc()).all()

    def create(self, mahasiswa_id: UUID, service_type_id: UUID, purpose: str, file_syarat_path: str | None) -> Ticket:
        ticket = Ticket(
            mahasiswa_id=mahasiswa_id,
            service_type_id=service_type_id,
            purpose=purpose,
            file_syarat_path=file_syarat_path,
            status="dalam_antrean",
        )
        self._db.add(ticket)
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def has_active_ticket(self, staff_id: UUID) -> bool:
        """Cek apakah staff sudah memegang tiket aktif (diproses/dalam_pembuatan)."""
        return (
            self._db.query(Ticket)
            .filter(
                Ticket.assigned_to == staff_id,
                Ticket.status.in_(["diproses", "dalam_pembuatan"]),
            )
            .first()
            is not None
        )

    def claim_specific(self, ticket: Ticket, staff_id: UUID) -> Ticket:
        """Klaim tiket spesifik berdasarkan ID (dipakai dari halaman detail)."""
        ticket.status = "diproses"
        ticket.assigned_to = staff_id
        ticket.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def claim_next(self, staff_id: UUID, staff_level: str) -> Ticket | None:
        """
        Ambil tiket FIFO dari pool level staff.
        Gunakan SELECT FOR UPDATE SKIP LOCKED untuk mencegah race condition
        ketika dua staff mengklik "Ambil Tiket" bersamaan.
        """
        ticket = (
            self._db.query(Ticket)
            .join(ServiceType, Ticket.service_type_id == ServiceType.id)
            .filter(
                Ticket.status == "dalam_antrean",
                Ticket.assigned_to == None,
                ServiceType.level == staff_level,
            )
            .order_by(Ticket.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if not ticket:
            return None

        ticket.status = "diproses"
        ticket.assigned_to = staff_id
        ticket.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def update_status(self, ticket: Ticket, status: str, catatan_tu: str | None = None) -> Ticket:
        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        if catatan_tu is not None:
            ticket.catatan_tu = catatan_tu
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def set_file_hasil(self, ticket: Ticket, file_path: str) -> Ticket:
        ticket.file_hasil_path = file_path
        ticket.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def count_in_queue_by_level(self, staff_level: str) -> int:
        return (
            self._db.query(Ticket)
            .join(ServiceType, Ticket.service_type_id == ServiceType.id)
            .filter(
                Ticket.status == "dalam_antrean",
                Ticket.assigned_to == None,
                ServiceType.level == staff_level,
            )
            .count()
        )
