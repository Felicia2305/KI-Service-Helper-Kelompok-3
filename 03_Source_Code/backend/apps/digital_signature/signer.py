import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Signer:
    @staticmethod
    def sign(private_key, message: str) -> str:
        """
        Menandatangani pesan dan mengembalikan string Base64.
        """
        signature_bytes = private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature_bytes).decode('utf-8')