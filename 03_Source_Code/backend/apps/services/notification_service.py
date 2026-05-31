import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import settings
from ..models.ticket_model import Ticket

logger = logging.getLogger(__name__)

# Staff level → label role yang tampil di email
_ROLE_LABEL = {
    "staff_departemen": "Staf Departemen",
    "staff_fakultas": "Staf Fakultas",
    "staff_ipb": "Staf IPB",
}

_MAIL_CONFIG = None


def _get_mail_config() -> ConnectionConfig | None:
    if not settings.MAIL_USERNAME:
        return None
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )


class NotificationService:
    async def _send(self, to: str, subject: str, body: str) -> None:
        config = _get_mail_config()
        if config is None:
            logger.info("[EMAIL SKIPPED — SMTP not configured] To: %s | %s", to, subject)
            return
        message = MessageSchema(subject=subject, recipients=[to], body=body, subtype="html")
        fm = FastMail(config)
        try:
            await fm.send_message(message)
        except Exception as e:
            logger.error("Gagal mengirim email ke %s: %s", to, e)

    async def notify_submitted(self, ticket: Ticket) -> None:
        body = f"""
        <p>Halo <b>{ticket.mahasiswa.nama}</b>,</p>
        <p>Tiket Anda untuk layanan <b>{ticket.service_type.nama}</b> telah berhasil dikirim dan sedang dalam antrean.</p>
        <p><b>ID Tiket:</b> {ticket.id}</p>
        <p>Terima kasih,<br>IASH — IPB Academic Service Helper</p>
        """
        await self._send(ticket.mahasiswa.email, "Tiket Berhasil Dikirim", body)

    async def notify_claimed(self, ticket: Ticket) -> None:
        body = f"""
        <p>Halo <b>{ticket.mahasiswa.nama}</b>,</p>
        <p>Tiket Anda (<b>{ticket.service_type.nama}</b>) kini sedang ditinjau oleh staf TU.</p>
        <p>Harap tunggu informasi selanjutnya.</p>
        <p>Terima kasih,<br>IASH — IPB Academic Service Helper</p>
        """
        await self._send(ticket.mahasiswa.email, "Tiket Anda Sedang Diproses", body)

    async def notify_approved(self, ticket: Ticket) -> None:
        body = f"""
        <p>Halo <b>{ticket.mahasiswa.nama}</b>,</p>
        <p>Berkas Anda untuk layanan <b>{ticket.service_type.nama}</b> telah diverifikasi.</p>
        <p>Dokumen Anda sedang dalam tahap pembuatan. Kami akan menginformasikan kembali saat sudah selesai.</p>
        <p>Terima kasih,<br>IASH — IPB Academic Service Helper</p>
        """
        await self._send(ticket.mahasiswa.email, "Berkas Disetujui — Dalam Pembuatan", body)

    async def notify_rejected(self, ticket: Ticket) -> None:
        body = f"""
        <p>Halo <b>{ticket.mahasiswa.nama}</b>,</p>
        <p>Maaf, pengajuan Anda untuk layanan <b>{ticket.service_type.nama}</b> tidak dapat diproses.</p>
        <p><b>Alasan:</b> {ticket.catatan_tu or '-'}</p>
        <p>Silakan perbaiki kekurangan tersebut dan ajukan tiket baru.</p>
        <p>Terima kasih,<br>IASH — IPB Academic Service Helper</p>
        """
        await self._send(ticket.mahasiswa.email, "Pengajuan Tiket Ditolak", body)

    async def notify_completed(self, ticket: Ticket, frontend_url: str) -> None:
        history_url = f"{frontend_url}/history"
        body = f"""
        <p>Halo <b>{ticket.mahasiswa.nama}</b>,</p>
        <p>Dokumen Anda untuk layanan <b>{ticket.service_type.nama}</b> telah selesai!</p>
        {f'<p><b>Catatan:</b> {ticket.catatan_tu}</p>' if ticket.catatan_tu else ''}
        <p>Silakan login ke <a href="{history_url}">IASH</a> untuk mengunduh dokumen Anda.</p>
        <p>Terima kasih,<br>IASH — IPB Academic Service Helper</p>
        """
        await self._send(ticket.mahasiswa.email, "Dokumen Anda Sudah Siap!", body)
