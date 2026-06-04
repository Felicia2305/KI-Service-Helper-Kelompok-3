from uuid import UUID
from sqlalchemy.orm import Session
from ..models.audit_log_model import AuditLog
from ..logger import audit_logger


class AuditService:
    def __init__(self, db: Session):
        self._db = db

    def log_event(
        self,
        user_id: UUID | str | None,
        action: str,
        resource: str | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        parsed_user_id = UUID(str(user_id)) if user_id else None
        entry = AuditLog(
            user_id=parsed_user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            details=details or {},
        )
        self._db.add(entry)
        self._db.commit()
        self._db.refresh(entry)
        audit_logger.info("AUDIT action=%s resource=%s user_id=%s ip=%s", action, resource, user_id, ip_address)
        return entry
