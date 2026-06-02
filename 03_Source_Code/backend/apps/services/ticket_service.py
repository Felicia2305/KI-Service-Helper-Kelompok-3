from sqlalchemy.orm import Session 
from ..repositories.ticket_repository import TicketRepository
from ..security.crypto_service import CryptoService
from .digital_signature.signer import Signer
from ..digital_signature.key_manager import KeyManager
from ..config import settings

class TicketService:
    def __init__(self, db: Session):
        self.db = db
        
        # 1. Inisialisasi modul keamanan di dalam Service
        # Ambil key dari settings/env
        self.crypto = CryptoService(settings.ENCRYPTION_KEY.encode())
        
        # Muat private key untuk signing (Asumsi path ada di settings)
        private_key = KeyManager.load_private_key(settings.PRIVATE_KEY_PATH)
        self.signer = Signer(private_key) 

        # 2. Masukkan ke dalam Repository
        self.repo = TicketRepository(self.db, crypto=self.crypto, signer=self.signer)

    async def submit(self, current_user, service_type_id, purpose, file):
        # ... logika simpan file ...
        # Panggil repo.create yang sudah kita modifikasi (otomatis encrypt & sign)
        return self.repo.create(
            mahasiswa_id=current_user.id,
            service_type_id=service_type_id,
            purpose=purpose,
            file_syarat_path=file_path
        )
    
    # Fungsi lainnya (approve, reject, get_detail) juga akan otomatis 
    # menggunakan self.repo yang sudah dibekali crypto & signer.