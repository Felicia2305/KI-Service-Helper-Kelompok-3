import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from ..config import settings

class KeyManager:
    @staticmethod
    def load_private_key(path: str | None = None):
        """
        Mencoba memuat private key dari Environment Variable (untuk Vercel),
        jika tidak ada, maka memuat dari file lokal (untuk development).
        """
        # 1. Coba ambil dari Environment Variable (Produksi/Vercel)
        # Di Vercel, simpan isi file .pem ke variable bernama PRIVATE_KEY_CONTENT
        env_key = settings.PRIVATE_KEY_CONTENT or os.getenv("PRIVATE_KEY_CONTENT")
        
        if env_key:
            # Perbaikan format newline jika tersimpan sebagai string tunggal
            formatted_key = env_key.replace("\\n", "\n")
            return serialization.load_pem_private_key(
                formatted_key.encode(),
                password=None # Sesuaikan jika kunci Anda pakai password
            )

        file_path = Path(path or settings.PRIVATE_KEY_PATH)
        if file_path.exists():
            with file_path.open("rb") as key_file:
                return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        
        raise FileNotFoundError(f"Private key tidak ditemukan. Letakkan file di: {file_path}")

    @staticmethod
    def load_public_key(path: str | None = None):
        """
        Sama dengan private key, mencoba dari Env lalu ke file lokal.
        """
        env_key = settings.PUBLIC_KEY_CONTENT or os.getenv("PUBLIC_KEY_CONTENT")
        
        if env_key:
            formatted_key = env_key.replace("\\n", "\n")
            return serialization.load_pem_public_key(formatted_key.encode())

        file_path = Path(path or settings.PUBLIC_KEY_PATH)
        if file_path.exists():
            with file_path.open("rb") as key_file:
                return serialization.load_pem_public_key(key_file.read())
                
        raise FileNotFoundError(f"Public key tidak ditemukan. Letakkan file di: {file_path}")

    @staticmethod
    def generate_keypair(private_path: str, public_path: str) -> None:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        private_file = Path(private_path)
        public_file = Path(public_path)
        private_file.parent.mkdir(parents=True, exist_ok=True)
        public_file.parent.mkdir(parents=True, exist_ok=True)

        private_file.write_bytes(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        public_file.write_bytes(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
