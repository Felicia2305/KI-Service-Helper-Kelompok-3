from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    nama: str = Field(..., min_length=2, max_length=255)
    nim_nip: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., max_length=32)

    @field_validator("email")
    @classmethod
    def email_must_be_ipb(cls, v: str) -> str:
        if not v.endswith("@apps.ipb.ac.id"):
            raise ValueError("Email harus menggunakan domain @apps.ipb.ac.id")
        return v

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        valid_roles = {"mahasiswa", "staff_departemen", "staff_fakultas", "staff_ipb"}
        if v not in valid_roles:
            raise ValueError(f"Role tidak valid. Pilihan: {valid_roles}")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
