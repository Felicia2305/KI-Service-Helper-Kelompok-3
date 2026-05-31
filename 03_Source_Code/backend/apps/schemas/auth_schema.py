from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nama: str
    nim_nip: str
    role: str

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
