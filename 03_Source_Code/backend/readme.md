# Backend KI / IPB Academic Service Helper

Letakkan RSA key di folder `keys/`:

- `keys/private_key.pem`
- `keys/public_key.pem`

File `.pem` tidak boleh dicommit. Folder `keys/` hanya ditrack lewat `.gitkeep`.
Jika key masih berada di root project, pindahkan secara manual ke folder ini sebelum menjalankan backend.

Environment variable wajib tersedia di `.env` atau deployment secrets. Lihat `.env.example`.
