from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    nama: str
    nim_nip: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
