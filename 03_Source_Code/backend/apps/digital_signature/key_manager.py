import os
from cryptography.hazmat.primitives import serialization

class KeyManager:
    @staticmethod
    def load_private_key():
        """
        Mencoba memuat private key dari Environment Variable (untuk Vercel),
        jika tidak ada, maka memuat dari file lokal (untuk development).
        """
        # 1. Coba ambil dari Environment Variable (Produksi/Vercel)
        # Di Vercel, simpan isi file .pem ke variable bernama PRIVATE_KEY_CONTENT
        env_key = os.getenv("PRIVATE_KEY_CONTENT")
        
        if env_key:
            # Perbaikan format newline jika tersimpan sebagai string tunggal
            formatted_key = env_key.replace("\\n", "\n")
            return serialization.load_pem_private_key(
                formatted_key.encode(),
                password=None # Sesuaikan jika kunci Anda pakai password
            )

        # 2. Fallback: Muat dari file lokal (Development)
        # Pastikan path ini sesuai dengan letak file .pem di laptopmu
        file_path = "certs/private_key.pem" 
        if os.path.exists(file_path):
            with open(file_path, "rb") as key_file:
                return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        
        raise RuntimeError("Private key tidak ditemukan di Env maupun File!")

    @staticmethod
    def load_public_key():
        """
        Sama dengan private key, mencoba dari Env lalu ke file lokal.
        """
        env_key = os.getenv("PUBLIC_KEY_CONTENT")
        
        if env_key:
            formatted_key = env_key.replace("\\n", "\n")
            return serialization.load_pem_public_key(formatted_key.encode())

        file_path = "certs/public_key.pem"
        if os.path.exists(file_path):
            with open(file_path, "rb") as key_file:
                return serialization.load_pem_public_key(key_file.read())
                
        raise RuntimeError("Public key tidak ditemukan di Env maupun File!")