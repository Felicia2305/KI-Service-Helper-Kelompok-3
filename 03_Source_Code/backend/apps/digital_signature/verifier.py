import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

class Verifier:
    @staticmethod
    def verify(public_key, message: str, signature_base64: str) -> bool:
        """
        Memverifikasi apakah signature cocok dengan message.
        """
        try:
            signature_bytes = base64.b64decode(signature_base64)
            public_key.verify(
                signature_bytes,
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True # Verifikasi Berhasil
        except InvalidSignature:
            return False # Data telah dimodifikasi!