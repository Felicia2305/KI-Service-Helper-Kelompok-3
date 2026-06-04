from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.ticket_model import Ticket
from ..models.service_type_model import ServiceType
# Import tambahan untuk integrasi keamanan
from ..security.crypto_service import CryptoService
from ..digital_signature.signer import Signer 

class TicketRepository:
    def __init__(self, db: Session, crypto: CryptoService = None, signer: Signer = None):
        self._db = db
        self._crypto = crypto
        self._signer = signer

    def _decrypt_ticket(self, ticket: Ticket) -> Ticket:
        """Helper untuk mendekripsi data tiket agar bisa dibaca di UI."""
        if ticket and self._crypto:
            if ticket.purpose_encrypted:
                try:
                    ticket.purpose = self._crypto.decrypt(ticket.purpose_encrypted)
                except Exception:
                    ticket.purpose = ticket.purpose_encrypted
            if ticket.notes_encrypted:
                try:
                    ticket.notes = self._crypto.decrypt(ticket.notes_encrypted)
                except Exception:
                    ticket.notes = ticket.notes_encrypted
        return ticket

    def get_raw_ticket(self, ticket_id: UUID) -> Ticket | None:
        return self._db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        ticket = self._db.query(Ticket).filter(Ticket.id == ticket_id).first()
        return self._decrypt_ticket(ticket)

    def get_by_mahasiswa(self, user_id: UUID) -> list[Ticket]:
        tickets = (
            self._db.query(Ticket)
            .filter(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )
        return [self._decrypt_ticket(t) for t in tickets]

    def get_all(self, status_filter: str | None = None) -> list[Ticket]:
        query = self._db.query(Ticket)
        if status_filter:
            query = query.filter(Ticket.status == status_filter)
        tickets = query.order_by(Ticket.created_at.desc()).all()
        return [self._decrypt_ticket(t) for t in tickets]

    def create_ticket(
        self,
        user_id: UUID,
        service_type_id: UUID,
        purpose_encrypted: str,
        notes_encrypted: str | None = None,
        file_path: str | None = None,
        digital_signature: str | None = None,
    ) -> Ticket:
        ticket = Ticket(
            user_id=user_id,
            service_type_id=service_type_id,
            purpose_encrypted=purpose_encrypted,
            notes_encrypted=notes_encrypted,
            digital_signature=digital_signature,
            file_path=file_path,
            status="pending",
        )
        self._db.add(ticket)
        self._db.commit()
        self._db.refresh(ticket)
        return self._decrypt_ticket(ticket)

    def create(self, mahasiswa_id: UUID, service_type_id: UUID, purpose: str, file_syarat_path: str | None = None) -> Ticket:
        encrypted_purpose = self._crypto.encrypt(purpose) if self._crypto else purpose
        signature = None
        return self.create_ticket(
            user_id=mahasiswa_id,
            service_type_id=service_type_id,
            purpose_encrypted=encrypted_purpose,
            file_path=file_syarat_path,
            digital_signature=signature,
        )

    def update_status(self, ticket: Ticket, status: str, catatan_tu: str | None = None) -> Ticket:
        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        
        if catatan_tu is not None:
            # --- LOGIKA KEAMANAN ---
            # Enkripsi catatan staf sebelum disimpan
            if self._crypto:
                ticket.notes_encrypted = self._crypto.encrypt(catatan_tu)
            else:
                ticket.notes_encrypted = catatan_tu
                
        self._db.commit()
        self._db.refresh(ticket)
        return self._decrypt_ticket(ticket)

    def claim_specific(self, ticket: Ticket, staff_id: UUID) -> Ticket:
        ticket.status = "claimed"
        ticket.claimed_by = staff_id
        ticket.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(ticket)
        return self._decrypt_ticket(ticket)

    def claim_next(self, staff_id: UUID, staff_level: str | None = None) -> Ticket | None:
        ticket = (
            self._db.query(Ticket)
            .join(ServiceType, Ticket.service_type_id == ServiceType.id)
            .filter(
                Ticket.status == "pending",
                Ticket.claimed_by == None,
            )
            .order_by(Ticket.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if not ticket:
            return None

        ticket.status = "claimed"
        ticket.claimed_by = staff_id
        ticket.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(ticket)
        return self._decrypt_ticket(ticket)
