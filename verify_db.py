import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
print(f"Connecting to: {db_url.split('@')[1] if '@' in db_url else 'Invalid URL'}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    print(f"✅ Connected successfully!")
    print(f"Server version: {version}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
