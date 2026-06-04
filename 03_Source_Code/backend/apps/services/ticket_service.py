import os
from pathlib import Path
from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from ..config import settings
from ..digital_signature.key_manager import KeyManager
from ..digital_signature.signer import Signer
from ..digital_signature.verifier import Verifier
from ..models.ticket_model import Ticket
from ..models.user_model import User
from ..repositories.service_repository import ServiceRepository
from ..repositories.ticket_repository import TicketRepository
from ..security.crypto_service import CryptoService


class TicketService:
    def __init__(self, db: Session):
        self.db = db

        # 1. Inisialisasi modul keamanan di dalam Service
        # Ambil key dari settings/env
        self.crypto = CryptoService()

        # Muat private key untuk signing (Asumsi path ada di settings)
        private_key = KeyManager.load_private_key()
        self.signer = Signer()
        self._private_key = private_key
        self._public_key = KeyManager.load_public_key()

        # 2. Masukkan ke dalam Repository
        self.repo = TicketRepository(self.db, crypto=self.crypto, signer=self.signer)
        self.service_repo = ServiceRepository(self.db)

    def create_ticket(
        self,
        user_id: UUID,
        service_type_id: UUID,
        purpose: str,
        notes: str | None = None,
        file_path: str | None = None,
    ) -> Ticket:
        if not self.service_repo.get_by_id(service_type_id):
            raise HTTPException(status_code=404, detail="Jenis layanan tidak ditemukan.")
        purpose_encrypted = self.crypto.encrypt(purpose)
        notes_encrypted = self.crypto.encrypt(notes) if notes else None
        data_to_sign = f"{user_id}:{service_type_id}:{purpose}"
        digital_signature = self.signer.sign(self._private_key, data_to_sign)
        ticket = self.repo.create_ticket(
            user_id=user_id,
            service_type_id=service_type_id,
            purpose_encrypted=purpose_encrypted,
            notes_encrypted=notes_encrypted,
            file_path=file_path,
            digital_signature=digital_signature,
        )
        ticket.purpose = purpose
        ticket.notes = notes
        return ticket

    async def submit(self, current_user: User, service_type_id: UUID, purpose: str, file: UploadFile | None, notes: str | None = None):
        file_path = await self._store_upload(file) if file else None
        return self.create_ticket(
            user_id=current_user.id,
            service_type_id=service_type_id,
            purpose=purpose,
            notes=notes,
            file_path=file_path,
        )

    def get_my_tickets(self, user_or_id: User | UUID) -> list[Ticket]:
        user_id = user_or_id.id if hasattr(user_or_id, "id") else user_or_id
        return self.repo.get_by_mahasiswa(user_id)

    def get_all_tickets(self, current_user_or_role=None, status_filter: str | None = None) -> list[Ticket]:
        return self.repo.get_all(status_filter)

    def get_ticket_detail(self, current_user: User, ticket_id: UUID) -> Ticket:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Tiket tidak ditemukan.")
        if current_user.role == "mahasiswa" and ticket.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Akses tiket ditolak.")
        return ticket

    async def claim_next(self, current_user: User) -> Ticket:
        ticket = self.repo.claim_next(current_user.id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Tidak ada tiket yang bisa diklaim.")
        return ticket

    def claim_specific(self, ticket_id: UUID, staff_id: UUID) -> Ticket:
        ticket = self.repo.get_raw_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Tiket tidak ditemukan.")
        if ticket.claimed_by and ticket.claimed_by != staff_id:
            raise HTTPException(status_code=409, detail="Tiket sudah diklaim staf lain.")
        return self.repo.claim_specific(ticket, staff_id)

    async def claim_specific_for_user(self, current_user: User, ticket_id: UUID) -> Ticket:
        return self.claim_specific(ticket_id, current_user.id)

    def approve_ticket(self, ticket_id: UUID, staff_id: UUID, notes: str | None = None) -> Ticket:
        ticket = self._require_claimed_by_staff(ticket_id, staff_id)
        return self.repo.update_status(ticket, "approved", notes)

    async def approve(self, current_user: User, ticket_id: UUID, notes: str | None = None) -> Ticket:
        return self.approve_ticket(ticket_id, current_user.id, notes)

    def reject_ticket(self, ticket_id: UUID, staff_id: UUID, notes: str) -> Ticket:
        ticket = self._require_claimed_by_staff(ticket_id, staff_id)
        return self.repo.update_status(ticket, "rejected", notes)

    async def reject(self, current_user: User, ticket_id: UUID, notes: str) -> Ticket:
        return self.reject_ticket(ticket_id, current_user.id, notes)

    def complete_ticket(self, ticket_id: UUID, staff_id: UUID, file_path: str | None = None, notes: str | None = None) -> Ticket:
        ticket = self._require_claimed_by_staff(ticket_id, staff_id)
        if file_path:
            ticket.file_path = file_path
        return self.repo.update_status(ticket, "completed", notes)

    async def complete(self, current_user: User, ticket_id: UUID, file: UploadFile | None = None, notes: str | None = None) -> Ticket:
        file_path = await self._store_upload(file) if file else None
        return self.complete_ticket(ticket_id, current_user.id, file_path, notes)

    def verify_ticket_integrity(self, ticket_id: UUID) -> dict:
        ticket = self.repo.get_raw_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Tiket tidak ditemukan.")
        purpose = self.crypto.decrypt(ticket.purpose_encrypted)
        data_to_verify = f"{ticket.user_id}:{ticket.service_type_id}:{purpose}"
        valid = Verifier.verify(self._public_key, data_to_verify, ticket.digital_signature or "")
        return {
            "valid": valid,
            "message": "Integritas tiket valid." if valid else "Integritas tiket tidak valid.",
        }

    def _require_claimed_by_staff(self, ticket_id: UUID, staff_id: UUID) -> Ticket:
        ticket = self.repo.get_raw_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Tiket tidak ditemukan.")
        if ticket.claimed_by != staff_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tiket harus diklaim oleh staf ini.")
        return ticket

    async def _store_upload(self, file: UploadFile) -> str:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".jpg", ".jpeg", ".png", ".docx"}:
            raise HTTPException(status_code=400, detail="Format file tidak diizinkan.")
        target_name = f"{UUID(bytes=os.urandom(16))}{suffix}"
        target = upload_dir / target_name
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Ukuran file maksimal 5MB.")
        target.write_bytes(content)
        return target_name
