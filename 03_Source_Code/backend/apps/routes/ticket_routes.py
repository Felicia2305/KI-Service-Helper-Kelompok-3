import os
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user, require_role, require_staff
from ..models.user_model import User
from ..services.ticket_service import TicketService
from ..services.auth_service import AuthService
from ..services.audit_service import AuditService
from ..schemas.ticket_schema import TicketResponse, TicketRejectRequest, TicketApproveRequest
from ..config import settings
from ..limiter import limiter


router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

_MAX_FILE_SIZE = 5 * 1024 * 1024
_ALLOWED_MIME = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

@router.get("/{ticket_id}/verify-integrity")
def verify_ticket(
    ticket_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    result = TicketService(db).verify_ticket_integrity(ticket_id)
    AuditService(db).log_event(current_user.id, "verify_signature", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket_id), "valid": result["valid"]})
    return result


def _safe_path(upload_dir: str, relative_path: str) -> Path:
    base = Path(upload_dir).resolve()
    full = (base / relative_path).resolve()
    if not str(full).startswith(str(base) + os.sep) and str(full) != str(base):
        raise HTTPException(status_code=403, detail="Akses ditolak.")
    return full


@router.post("", response_model=TicketResponse, status_code=201)
@limiter.limit("10/minute")
async def submit_ticket(
    request: Request,
    service_type_id: UUID = Form(...),
    purpose: str = Form(..., max_length=2000),
    notes: str | None = Form(None, max_length=2000),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_upload(file)
    ticket = await TicketService(db).submit(current_user, service_type_id, purpose, file, notes)
    AuditService(db).log_event(current_user.id, "create_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket.id)})
    return ticket


@router.get("/my", response_model=list[TicketResponse])
def my_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TicketService(db).get_my_tickets(current_user)


@router.get("", response_model=list[TicketResponse])
def all_tickets(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return TicketService(db).get_all_tickets(current_user, status)


@router.post("/claim", response_model=TicketResponse)
async def claim_ticket(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    ticket = await TicketService(db).claim_next(current_user)
    AuditService(db).log_event(current_user.id, "claim_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket.id)})
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def ticket_detail(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TicketService(db).get_ticket_detail(current_user, ticket_id)


@router.post("/{ticket_id}/claim", response_model=TicketResponse)
async def claim_specific_ticket(
    ticket_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    ticket = await TicketService(db).claim_specific_for_user(current_user, ticket_id)
    AuditService(db).log_event(current_user.id, "claim_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket_id)})
    return ticket


@router.patch("/{ticket_id}/approve", response_model=TicketResponse)
async def approve_ticket(
    ticket_id: UUID,
    body: TicketApproveRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    ticket = await TicketService(db).approve(current_user, ticket_id, body.notes or body.catatan_tu)
    AuditService(db).log_event(current_user.id, "approve_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket_id)})
    return ticket


@router.patch("/{ticket_id}/reject", response_model=TicketResponse)
async def reject_ticket(
    ticket_id: UUID,
    body: TicketRejectRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    ticket = await TicketService(db).reject(current_user, ticket_id, body.notes or body.catatan_tu)
    AuditService(db).log_event(current_user.id, "reject_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket_id)})
    return ticket


@router.patch("/{ticket_id}/complete", response_model=TicketResponse)
async def complete_ticket(
    ticket_id: UUID,
    request: Request,
    file: UploadFile | None = File(None),
    notes: str | None = Form(None, max_length=2000),
    catatan_tu: str | None = Form(None, max_length=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    _validate_upload(file)
    ticket = await TicketService(db).complete(current_user, ticket_id, file, notes or catatan_tu)
    AuditService(db).log_event(current_user.id, "complete_ticket", "ticket", request.client.host if request.client else None, {"ticket_id": str(ticket_id)})
    return ticket


@router.get("/{ticket_id}/download-syarat")
def download_syarat(
    ticket_id: UUID,
    request: Request,
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    bearer = request.headers.get("Authorization", "")
    resolved = bearer.replace("Bearer ", "").strip() if bearer else token
    if not resolved:
        raise HTTPException(status_code=401, detail="Token diperlukan.")
    current_user = AuthService(db).get_user_from_token(resolved)
    ticket = TicketService(db).get_ticket_detail(current_user, ticket_id)
    if not ticket.file_syarat_path:
        raise HTTPException(status_code=404, detail="Berkas syarat tidak tersedia.")
    full_path = _safe_path(settings.UPLOAD_DIR, ticket.file_syarat_path)
    return FileResponse(str(full_path), filename=os.path.basename(str(full_path)))


@router.get("/{ticket_id}/download")
def download_hasil(
    ticket_id: UUID,
    request: Request,
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    bearer = request.headers.get("Authorization", "")
    resolved = bearer.replace("Bearer ", "").strip() if bearer else token
    if not resolved:
        raise HTTPException(status_code=401, detail="Token diperlukan.")
    current_user = AuthService(db).get_user_from_token(resolved)

    ticket = TicketService(db).get_ticket_detail(current_user, ticket_id)
    if not ticket.file_hasil_path:
        raise HTTPException(status_code=404, detail="Dokumen hasil belum tersedia.")
    full_path = _safe_path(settings.UPLOAD_DIR, ticket.file_hasil_path)
    return FileResponse(str(full_path), filename=os.path.basename(str(full_path)))


def _validate_upload(file: UploadFile | None) -> None:
    if not file:
        return
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Format file tidak diizinkan.")
    if file.size and file.size > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran file maksimal 5MB.")
