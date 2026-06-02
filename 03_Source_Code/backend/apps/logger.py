import logging
import sys

_FMT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=_FMT)

# Untuk event autentikasi dan akses (login gagal, akses ditolak)
security_logger = logging.getLogger("iash.security")

# Untuk aksi admin terhadap tiket (klaim, setujui, tolak, selesai)
audit_logger = logging.getLogger("iash.audit")
