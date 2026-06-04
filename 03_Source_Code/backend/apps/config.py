from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FERNET_KEY: str = Field(default="", validation_alias=AliasChoices("FERNET_KEY", "ENCRYPTION_KEY"))

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@iash.ipb.ac.id"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    UPLOAD_DIR: str = "uploads"
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"
    FORCE_HTTPS: bool = False
    TRUSTED_HOSTS: str = "localhost,127.0.0.1"
    MAX_REQUEST_SIZE: int = 6 * 1024 * 1024
    AUTO_CREATE_TABLES: bool = False

    PRIVATE_KEY_PATH: str = "keys/private_key.pem"
    PUBLIC_KEY_PATH: str = "keys/public_key.pem"
    PRIVATE_KEY_CONTENT: str | None = None
    PUBLIC_KEY_CONTENT: str | None = None

    @field_validator("DATABASE_URL", "SECRET_KEY")
    @classmethod
    def required_secret_values(cls, value: str, info):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} wajib diisi dari environment variable.")
        return value

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_minimum_length(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY minimal 32 karakter random.")
        return value

    @model_validator(mode="after")
    def validate_fernet_key(self):
        if not self.FERNET_KEY:
            raise ValueError("FERNET_KEY wajib diisi dari environment variable untuk enkripsi data at rest.")
        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
