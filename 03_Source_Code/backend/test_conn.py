import psycopg2

try:
    print("Sedang mencoba menghubungkan ke Sydney...")
    conn = psycopg2.connect(
        host="aws-0-ap-southeast-2.pooler.supabase.com",
        port=6543,
        user="postgres.ciiyerhncjuyzjlwvwig",
        password="4-4*X7BZQdWzBYN", # Password asli kamu
        database="postgres"
    )
    print("✅ KONEKSI SUKSES!")
    conn.close()
except Exception as e:
    print(f"❌ KONEKSI GAGAL: {e}")