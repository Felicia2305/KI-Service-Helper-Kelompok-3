import os
import uuid
from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from ..config import settings
from ..models.user_model import User
from ..models.ticket_model import Ticket
from ..repositories.ticket_repository import TicketRepository
from ..repositories.service_repository import ServiceRepository
from .notification_service import NotificationService
from ..logger import security_logger, audit_logger
from ..config import settings

# Transisi status yang diizinkan
_VALID_TRANSITIONS: dict[str, list[str]] = {
    "dalam_antrean": ["diproses"],
    "diproses": ["dalam_pembuatan", "ditolak"],
    "dalam_pembuatan": ["selesai"],
    "ditolak": [],
    "selesai": [],
}

# Pemetaan role staff ke level layanan yang bisa mereka tangani
_STAFF_LEVEL_MAP: dict[str, str] = {
    "staff_departemen": "departemen",
    "staff_fakultas": "fakultas",
    "staff_ipb": "ipb",
}


class TicketService:
    def __init__(self, db: Session):
        self._ticket_repo = TicketRepository(db)
        self._service_repo = ServiceRepository(db)
        self._notif = NotificationService()

    async def submit(self, mahasiswa: User, service_type_id: UUID, purpose: str, file: UploadFile | None) -> Ticket:
        service = self._service_repo.get_by_id(service_type_id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jenis layanan tidak ditemukan.")

        file_path = None
        if file and file.filename:
            file_path = await self._save_file(file, "berkas_syarat")

        ticket = self._ticket_repo.create(
            mahasiswa_id=mahasiswa.id,
            service_type_id=service_type_id,
            purpose=purpose,
            file_syarat_path=file_path,
        )
        ticket = self._ticket_repo.get_by_id(ticket.id)
        await self._notif.notify_submitted(ticket)
        return ticket

    async def claim_specific(self, staff: User, ticket_id: UUID) -> Ticket:
        self._require_staff(staff)
        ticket = self._ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiket tidak ditemukan.")
        if ticket.status != "dalam_antrean":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tiket sudah diambil atau tidak lagi dalam antrean.")

        staff_level = _STAFF_LEVEL_MAP.get(staff.role)
        if not staff_level:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role staff tidak dikenali.")
        if ticket.service_type.level != staff_level:
            security_logger.warning(
                "CLAIM_DENIED staff=%s staff_level=%s ticket_id=%s ticket_level=%s",
                staff.email, staff_level, ticket_id, ticket.service_type.level,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tiket ini tidak sesuai dengan level Anda.")

        ticket = self._ticket_repo.claim_specific(ticket, staff.id)
        ticket = self._ticket_repo.get_by_id(ticket.id)
        audit_logger.info("TICKET_CLAIMED ticket_id=%s staff=%s level=%s", ticket.id, staff.email, staff_level)
        await self._notif.notify_claimed(ticket)
        return ticket

    async def claim_next(self, staff: User) -> Ticket:
        self._require_staff(staff)
        staff_level = _STAFF_LEVEL_MAP.get(staff.role)
        if not staff_level:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role staff tidak dikenali.")

        ticket = self._ticket_repo.claim_next(staff.id, staff_level)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ada tiket dalam antrean untuk level Anda saat ini.",
            )
        ticket = self._ticket_repo.get_by_id(ticket.id)
        audit_logger.info("TICKET_CLAIMED_NEXT ticket_id=%s staff=%s level=%s", ticket.id, staff.email, staff_level)
        await self._notif.notify_claimed(ticket)
        return ticket

    async def approve(self, staff: User, ticket_id: UUID, catatan_tu: str | None) -> Ticket:
        ticket = self._get_assigned_ticket(staff, ticket_id)
        self._assert_transition(ticket.status, "dalam_pembuatan")

        ticket = self._ticket_repo.update_status(ticket, "dalam_pembuatan", catatan_tu)
        ticket = self._ticket_repo.get_by_id(ticket.id)
        audit_logger.info("TICKET_APPROVED ticket_id=%s staff=%s", ticket.id, staff.email)
        await self._notif.notify_approved(ticket)
        return ticket

    async def reject(self, staff: User, ticket_id: UUID, catatan_tu: str) -> Ticket:
        ticket = self._get_assigned_ticket(staff, ticket_id)
        self._assert_transition(ticket.status, "ditolak")

        ticket = self._ticket_repo.update_status(ticket, "ditolak", catatan_tu)
        ticket = self._ticket_repo.get_by_id(ticket.id)
        audit_logger.info("TICKET_REJECTED ticket_id=%s staff=%s", ticket.id, staff.email)
        await self._notif.notify_rejected(ticket)
        return ticket

    async def complete(self, staff: User, ticket_id: UUID, file: UploadFile, catatan_tu: str | None) -> Ticket:
        ticket = self._get_assigned_ticket(staff, ticket_id)
        self._assert_transition(ticket.status, "selesai")

        file_path = await self._save_file(file, "berkas_hasil")
        self._ticket_repo.set_file_hasil(ticket, file_path)
        ticket = self._ticket_repo.update_status(ticket, "selesai", catatan_tu)
        ticket = self._ticket_repo.get_by_id(ticket.id)
        audit_logger.info("TICKET_COMPLETED ticket_id=%s staff=%s", ticket.id, staff.email)

        await self._notif.notify_completed(ticket, settings.FRONTEND_URL)
        return ticket

    def get_ticket_detail(self, requester: User, ticket_id: UUID) -> Ticket:
        ticket = self._ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiket tidak ditemukan.")

        if requester.role == "mahasiswa" and ticket.mahasiswa_id != requester.id:
            security_logger.warning(
                "ACCESS_DENIED user=%s ticket_id=%s owner=%s",
                requester.email, ticket_id, ticket.mahasiswa_id,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")
        return ticket

    def get_my_tickets(self, mahasiswa: User) -> list[Ticket]:
        return self._ticket_repo.get_by_mahasiswa(mahasiswa.id)

    def get_all_tickets(self, staff: User, status_filter: str | None) -> list[Ticket]:
        self._require_staff(staff)
        return self._ticket_repo.get_all(status_filter)

    # --- Private helpers ---

    def _get_assigned_ticket(self, staff: User, ticket_id: UUID) -> Ticket:
        self._require_staff(staff)
        ticket = self._ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiket tidak ditemukan.")
        if ticket.assigned_to != staff.id:
            security_logger.warning(
                "ACCESS_DENIED staff=%s ticket_id=%s assigned_to=%s",
                staff.email, ticket_id, ticket.assigned_to,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tiket ini bukan milik Anda.")
        return ticket

    def _assert_transition(self, current: str, target: str) -> None:
        if target not in _VALID_TRANSITIONS.get(current, []):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transisi dari '{current}' ke '{target}' tidak diizinkan.",
            )

    def _require_staff(self, user: User) -> None:
        if user.role == "mahasiswa":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya staff yang dapat melakukan aksi ini.")

    async def _save_file(self, file: UploadFile, subfolder: str) -> str:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in {".pdf"}:
            raise HTTPException(status_code=400, detail="Hanya file PDF yang diizinkan.")
        if file.content_type not in {"application/pdf"}:
            raise HTTPException(status_code=400, detail="Tipe MIME tidak valid. Gunakan file PDF.")
        filename = f"{uuid.uuid4()}{ext}"
        dest_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, filename)
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)
        return os.path.join(subfolder, filename)
