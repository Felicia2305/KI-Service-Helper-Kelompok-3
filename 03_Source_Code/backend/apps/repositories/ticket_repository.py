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
            if ticket.purpose:
                try:
                    ticket.purpose = self._crypto.decrypt(ticket.purpose)
                except: pass # Jika gagal (data lama tidak terenkripsi), biarkan apa adanya
            if ticket.catatan_tu:
                try:
                    ticket.catatan_tu = self._crypto.decrypt(ticket.catatan_tu)
                except: pass
        return ticket

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        ticket = self._db.query(Ticket).filter(Ticket.id == ticket_id).first()
        return self._decrypt_ticket(ticket)

    def get_by_mahasiswa(self, mahasiswa_id: UUID) -> list[Ticket]:
        tickets = (
            self._db.query(Ticket)
            .filter(Ticket.mahasiswa_id == mahasiswa_id)
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

    def create(self, mahasiswa_id: UUID, service_type_id: UUID, purpose: str, file_syarat_path: str | None) -> Ticket:
        # --- LOGIKA KEAMANAN ---
        # 1. Enkripsi Purpose (Confidentiality)
        encrypted_purpose = purpose
        if self._crypto:
            encrypted_purpose = self._crypto.encrypt(purpose)

        # 2. Buat Digital Signature (Integrity & Non-repudiation)
        signature = None
        if self._signer:
            # Kita tanda tangani gabungan data penting
            data_to_sign = f"{mahasiswa_id}|{service_type_id}|{encrypted_purpose}"
            signature = self._signer.sign(data_to_sign)
        
        ticket = Ticket(
            mahasiswa_id=mahasiswa_id,
            service_type_id=service_type_id,
            purpose=encrypted_purpose, # Simpan hasil enkripsi
            signature=signature,       # Simpan tanda tangan digital
            file_syarat_path=file_syarat_path,
            status="dalam_antrean",
        )
        self._db.add(ticket)
        self._db.commit()
        self._db.refresh(ticket)
        
        # Dekripsi kembali sebelum dikembalikan ke controller agar user melihat teks asli
        return self._decrypt_ticket(ticket)

    def update_status(self, ticket: Ticket, status: str, catatan_tu: str | None = None) -> Ticket:
        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        
        if catatan_tu is not None:
            # --- LOGIKA KEAMANAN ---
            # Enkripsi catatan staf sebelum disimpan
            if self._crypto:
                ticket.catatan_tu = self._crypto.encrypt(catatan_tu)
            else:
                ticket.catatan_tu = catatan_tu
                
        self._db.commit()
        self._db.refresh(ticket)
        return self._decrypt_ticket(ticket)

    # ... (fungsi claim_next, has_active_ticket, dll tetap sama, 
    # jangan lupa panggil self._decrypt_ticket(ticket) sebelum return) ...

    def claim_next(self, staff_id: UUID, staff_level: str) -> Ticket | None:
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
        return self._decrypt_ticket(ticket)