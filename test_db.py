import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="warehouse_db",
        user="postgres",
        password="2311ss"
    )

    print("✅ Connected Successfully!")

    conn.close()

except Exception as e:
    print("❌ Error:", e)