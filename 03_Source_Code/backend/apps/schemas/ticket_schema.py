from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from .user_schema import UserResponse
from .service_schema import ServiceTypeResponse


class TicketSubmitRequest(BaseModel):
    service_type_id: UUID
    purpose: str = Field(..., min_length=1, max_length=2000)
    notes: str | None = Field(None, max_length=2000)


class TicketRejectRequest(BaseModel):
    catatan_tu: str | None = Field(None, min_length=10, max_length=2000)
    notes: str | None = Field(None, min_length=10, max_length=2000)


class TicketApproveRequest(BaseModel):
    catatan_tu: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)


class TicketResponse(BaseModel):
    id: UUID
    status: str
    purpose: str
    notes: str | None = None
    file_syarat_path: str | None
    catatan_tu: str | None
    file_hasil_path: str | None
    file_path: str | None = None
    digital_signature: str | None = None
    created_at: datetime
    updated_at: datetime
    mahasiswa: UserResponse
    service_type: ServiceTypeResponse
    assigned_staff: UserResponse | None = None

    model_config = {"from_attributes": True}
