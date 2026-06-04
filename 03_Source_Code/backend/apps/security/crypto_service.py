from cryptography.fernet import Fernet
from ..config import settings

class CryptoService:

    def __init__(self, key: str | bytes | None = None):
        resolved = key or settings.FERNET_KEY
        if not resolved:
            raise RuntimeError("FERNET_KEY belum dikonfigurasi.")
        self.cipher = Fernet(resolved.encode() if isinstance(resolved, str) else resolved)

    def encrypt(self, plaintext: str) -> str:
        if plaintext is None:
            return plaintext
        return self.cipher.encrypt(
            plaintext.encode()
        ).decode()

    def decrypt(self, ciphertext: str) -> str:
        if ciphertext is None:
            return ciphertext
        return self.cipher.decrypt(
            ciphertext.encode()
        ).decode()
