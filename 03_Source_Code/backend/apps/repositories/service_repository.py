from uuid import UUID
from sqlalchemy.orm import Session
from ..models.service_type_model import ServiceType


class ServiceRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_all(self) -> list[ServiceType]:
        return self._db.query(ServiceType).all()

    def get_by_id(self, service_id: UUID) -> ServiceType | None:
        return self._db.query(ServiceType).filter(ServiceType.id == service_id).first()
