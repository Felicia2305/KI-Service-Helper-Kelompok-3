// Backend menggunakan snake_case enum, frontend menggunakan display string

export const STATUS_TO_DISPLAY: Record<string, string> = {
  'dalam_antrean': 'Dalam Antrean',
  'diproses': 'Diproses',
  'dalam_pembuatan': 'Dalam Pembuatan',
  'ditolak': 'Ditolak',
  'selesai': 'Selesai',
};

export const STATUS_TO_BACKEND: Record<string, string> = {
  'Dalam Antrean': 'dalam_antrean',
  'Diproses': 'diproses',
  'Dalam Pembuatan': 'dalam_pembuatan',
  'Ditolak': 'ditolak',
  'Selesai': 'selesai',
};

export function mapTicket(t: any) {
  return {
    id: t.id,
    jenis_tiket: t.service_type?.nama ?? '',
    submission_date: t.created_at,
    status: STATUS_TO_DISPLAY[t.status] ?? t.status,
    catatan_tu: t.catatan_tu ?? '',
    file_balasan_path: t.file_hasil_path ?? '',
    // admin fields
    user_nama: t.mahasiswa?.nama ?? '',
    user_nim_nip: t.mahasiswa?.nim_nip ?? '',
    // detail view
    form_data: JSON.stringify({ purpose: t.purpose }),
    file_syarat_path: t.file_syarat_path ?? '',
    service_level: t.service_type?.level ?? '',
    // raw untuk keperluan lain
    _raw: t,
  };
}

export function mapService(s: any) {
  return {
    id: s.id,
    name: s.nama,
    description: s.deskripsi ?? '',
    berkas: s.berkas_dibutuhkan ?? [],
  };
}
