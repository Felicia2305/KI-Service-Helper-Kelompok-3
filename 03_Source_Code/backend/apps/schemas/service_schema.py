import json
from uuid import UUID
from pydantic import BaseModel, field_validator


class ServiceTypeResponse(BaseModel):
    id: UUID
    nama: str
    deskripsi: str | None
    level: str
    berkas_dibutuhkan: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator("berkas_dibutuhkan", mode="before")
    @classmethod
    def parse_berkas(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v
