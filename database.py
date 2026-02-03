import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from werkzeug.security import generate_password_hash
from contextlib import contextmanager
import secrets
import string
import urllib.parse


# Use /tmp directory on Vercel/Render (serverless), current directory locally
if os.environ.get('VERCEL') or os.environ.get('RENDER'):
    DB_NAME = '/tmp/wapl.db'
else:
    DB_NAME = 'wapl.db'

def get_db_type():
    """Return 'postgres' or 'sqlite'"""
    return 'postgres' if os.environ.get('DATABASE_URL') else 'sqlite'

def get_agg_func():
    """Return the correct string aggregation function for the database type"""
    return "STRING_AGG(d.domain_name, ', ')" if get_db_type() == 'postgres' else "GROUP_CONCAT(d.domain_name, ', ')"

def is_postgres():
    """Check if using PostgreSQL"""
    return get_db_type() == 'postgres'

@contextmanager
def get_db_connection():
    """Get database connection (PostgreSQL or SQLite)"""
    conn = None
    db_url = os.environ.get('DATABASE_URL')
    
    try:
        if db_url:
            # PostgreSQL Connection
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            yield conn
        else:
            # SQLite Connection
            # Add 30-second timeout to prevent lock errors
            conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=30000')  # 30 seconds
            yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize database with all tables"""
    db_type = get_db_type()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Define types for PostgreSQL compatibility
        if db_type == 'postgres':
            pk_type = "SERIAL PRIMARY KEY"
            datetime_default = "DEFAULT CURRENT_TIMESTAMP"
            # Boolean in postgres is valid, same as sqlite (0/1 works in sqlite, true/false in pg)
        else:
            pk_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            datetime_default = "DEFAULT CURRENT_TIMESTAMP"

        # Users table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'hr', 'admin')),
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP {datetime_default},
                last_login TIMESTAMP
            )
        ''')
        
        # Domains table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS domains (
                id {pk_type},
                domain_name TEXT NOT NULL UNIQUE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP {datetime_default},
                created_by_admin_id INTEGER
            )
        ''')
        
        # Admins table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS admins (
                id {pk_type},
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                is_super_admin INTEGER DEFAULT 0,
                created_by_admin_id INTEGER,
                created_at TIMESTAMP {datetime_default},
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (created_by_admin_id) REFERENCES admins(id)
            )
        ''')
        
        # Data migration steps (adding columns if missing) would go here
        # For new deployment validation, we skip manual ALTERs for readability 
        # as CREATE IF NOT EXISTS handles clean state.
        
        # HRs table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS hrs (
                id {pk_type},
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                company_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                designation TEXT NOT NULL,
                created_by_admin_id INTEGER,
                created_at TIMESTAMP {datetime_default},
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (created_by_admin_id) REFERENCES admins(id)
            )
        ''')
        
        # Students table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS students (
                id {pk_type},
                user_id INTEGER NOT NULL,
                wapl_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                profile_pic TEXT,
                resume TEXT,
                domain_id INTEGER,
                registration_date TIMESTAMP {datetime_default},
                certificate_issued_date TIMESTAMP,
                certificate_expiry_date TIMESTAMP,
                assigned_hr_id INTEGER,
                address TEXT,
                education_details TEXT,
                skills TEXT,
                projects TEXT,
                account_status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (domain_id) REFERENCES domains(id),
                FOREIGN KEY (assigned_hr_id) REFERENCES hrs(id)
            )
        ''')

        # Student-Domain junction table (MANY-TO-MANY)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS student_domains (
                id {pk_type},
                student_id INTEGER NOT NULL,
                domain_id INTEGER NOT NULL,
                created_at TIMESTAMP {datetime_default},
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
                UNIQUE(student_id, domain_id)
            )
        ''')
        
        # OTP verifications table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS otp_verifications (
                id {pk_type},
                user_id INTEGER NOT NULL,
                otp_code TEXT NOT NULL,
                purpose TEXT NOT NULL CHECK(purpose IN ('registration', 'login', 'password_reset')),
                is_used BOOLEAN DEFAULT FALSE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP {datetime_default},
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Certificates table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS certificates (
                id {pk_type},
                student_id INTEGER NOT NULL,
                certificate_unique_id TEXT UNIQUE NOT NULL,
                issue_date TIMESTAMP NOT NULL,
                expiry_date TIMESTAMP NOT NULL,
                qr_code TEXT NOT NULL,
                pdf_path TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                issued_by_hr_id INTEGER,
                display_name TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (issued_by_hr_id) REFERENCES hrs(id)
            )
        ''')

        # Recruitment status table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS recruitment_status (
                id {pk_type},
                student_id INTEGER NOT NULL,
                hr_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'viewed',
                notes TEXT,
                created_at TIMESTAMP {datetime_default},
                updated_at TIMESTAMP {datetime_default},
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (hr_id) REFERENCES hrs(id)
            )
        ''')

        # Certificate audit table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS certificate_audit (
                id {pk_type},
                certificate_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                reason TEXT,
                changed_by_admin_id INTEGER,
                created_at TIMESTAMP {datetime_default},
                FOREIGN KEY (certificate_id) REFERENCES certificates(id),
                FOREIGN KEY (changed_by_admin_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        
        # Initialize default data if empty (simplified check)
        # In a real migration we'd check properly, here we check users count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if get_db_type() == 'postgres':
            count = cursor.fetchone()['count']
        else:
            count = cursor.fetchone()[0]

        if count == 0:
            print("🆕 Empty database detected, initializing defaults...")
            # Pre-populate domains
            default_domains = ['AI', 'ML', 'DevOps', 'Web Development', 'Data Science']
            for domain in default_domains:
                if get_db_type() == 'postgres':
                    cursor.execute('INSERT INTO domains (domain_name, is_active) VALUES (%s, TRUE) ON CONFLICT DO NOTHING', (domain,))
                else:
                    cursor.execute('INSERT OR IGNORE INTO domains (domain_name, is_active) VALUES (?, 1)', (domain,))
            
            # Create default SUPER admin account
            admin_email = 'admin@wapl.com'
            admin_password_hash = generate_password_hash('admin123')
            
            insert_user_sql = "INSERT INTO users (email, password_hash, role, is_verified) VALUES (?, ?, 'admin', ?)"
            if get_db_type() == 'postgres':
                insert_user_sql = insert_user_sql.replace('?', '%s') + " RETURNING id"
                cursor.execute(insert_user_sql, (admin_email, admin_password_hash, True))
                admin_user_id = cursor.fetchone()['id']
            else:
                cursor.execute(insert_user_sql, (admin_email, admin_password_hash, 1))
                admin_user_id = cursor.lastrowid
            
            insert_admin_sql = "INSERT INTO admins (user_id, full_name, phone, is_super_admin) VALUES (?, 'Super Admin', '1234567890', 1)"
            if get_db_type() == 'postgres':
                insert_admin_sql = insert_admin_sql.replace('?', '%s')
            
            cursor.execute(insert_admin_sql, (admin_user_id,))
            print("✅ Default Super Admin created")
            conn.commit()

        print(f"✅ Database initialized successfully ({db_type.upper()})")

# Database helper class
class db:
    @staticmethod
    def execute_query(query, params=(), fetch_one=False, fetch_all=False):
        """Execute query with proper connection handling and adaptation"""
        db_type = get_db_type()
        
        # Adapt query for PostgreSQL
        if db_type == 'postgres':
            query = query.replace('?', '%s')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
            except Exception as e:
                print(f"❌ Query Error: {e} | Query: {query}")
                raise e
            
            # Determine if this is a write operation
            is_write = query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP'))
            
            if fetch_one:
                result = cursor.fetchone()
                if is_write:
                    conn.commit()
                
                # Normalize result (RealDictCursor returns dict, sqlite3.Row returns dict-like)
                if result is None:
                    return None
                return dict(result)
                
            elif fetch_all:
                results = cursor.fetchall()
                if is_write:
                    conn.commit()
                return [dict(row) for row in results]
                
            else:
                # For INSERT/UPDATE/DELETE operations
                # Handle returning ID differences
                last_id = None
                
                if query.strip().upper().startswith('INSERT'):
                    if db_type == 'postgres':
                        # In Postgres, we need RETURNING id to get last_id if it wasn't there
                        # But since we are modifying execute_query generic wrapper, we can't easily append RETURNING id
                        # unless the query already has it.
                        # LIMITATION: This simple adapter won't auto-return ID for PG unless query has RETURNING id.
                        # We will rely on cursor.fetchone() if RETURNING is present.
                         if 'RETURNING' in query.upper():
                            res = cursor.fetchone()
                            if res:
                                try:
                                    last_id = res['id']
                                except:
                                    pass
                    else:
                        last_id = cursor.lastrowid
                        
                conn.commit()
                return last_id
    
    @staticmethod
    def execute_many(query, params_list):
        """Execute multiple queries"""
        db_type = get_db_type()
        if db_type == 'postgres':
            query = query.replace('?', '%s')
            
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
