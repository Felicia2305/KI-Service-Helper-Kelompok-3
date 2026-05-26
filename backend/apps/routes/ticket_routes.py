import os
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user, require_staff
from ..models.user_model import User
from ..services.ticket_service import TicketService
from ..services.auth_service import AuthService
from ..schemas.ticket_schema import TicketResponse, TicketRejectRequest, TicketApproveRequest
from ..config import settings

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _safe_path(upload_dir: str, relative_path: str) -> Path:
    base = Path(upload_dir).resolve()
    full = (base / relative_path).resolve()
    if not str(full).startswith(str(base) + os.sep) and str(full) != str(base):
        raise HTTPException(status_code=403, detail="Akses ditolak.")
    return full


@router.post("", response_model=TicketResponse, status_code=201)
async def submit_ticket(
    service_type_id: UUID = Form(...),
    purpose: str = Form(..., max_length=2000),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file and file.size and file.size > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran file maksimal 10MB.")
    return await TicketService(db).submit(current_user, service_type_id, purpose, file)


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


@router.get("/{ticket_id}", response_model=TicketResponse)
def ticket_detail(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TicketService(db).get_ticket_detail(current_user, ticket_id)


@router.post("/claim", response_model=TicketResponse)
async def claim_ticket(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return await TicketService(db).claim_next(current_user)


@router.post("/{ticket_id}/claim", response_model=TicketResponse)
async def claim_specific_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return await TicketService(db).claim_specific(current_user, ticket_id)


@router.patch("/{ticket_id}/approve", response_model=TicketResponse)
async def approve_ticket(
    ticket_id: UUID,
    body: TicketApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return await TicketService(db).approve(current_user, ticket_id, body.catatan_tu)


@router.patch("/{ticket_id}/reject", response_model=TicketResponse)
async def reject_ticket(
    ticket_id: UUID,
    body: TicketRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return await TicketService(db).reject(current_user, ticket_id, body.catatan_tu)


@router.patch("/{ticket_id}/complete", response_model=TicketResponse)
async def complete_ticket(
    ticket_id: UUID,
    file: UploadFile = File(...),
    catatan_tu: str | None = Form(None, max_length=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    if file.size and file.size > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran file maksimal 10MB.")
    return await TicketService(db).complete(current_user, ticket_id, file, catatan_tu)


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
