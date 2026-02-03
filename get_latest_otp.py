
from database import db, get_db_type
import time

def get_latest_otp():
    try:
        # Get the most recent OTP
        print("Querying latest OTP...")
        
        sql = """
        SELECT o.otp_code, o.expires_at, o.is_used, u.email 
        FROM otp_verifications o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC LIMIT 1
        """
        
        # Adjust for SQLite local if needed, but we are on Postgres now mostly
        # Actually database.py handles the connection based on ENV
        
        otp = db.execute_query(sql, fetch_one=True)
        
        if otp:
            print(f"FOUND_OTP: {otp['otp_code']} (Email: {otp['email']}, Time: {otp['created_at'] if 'created_at' in otp.keys() else 'N/A'}, Expires: {otp['expires_at']})")
        else:
            print("No OTP records found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_otp()
