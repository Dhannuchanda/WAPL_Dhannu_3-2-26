from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database import db
from utils import generate_otp, send_email_simulation, sanitize_input, generate_wapl_id
import secrets


auth_bp = Blueprint('auth', __name__)


def require_auth(roles=None):
    """Decorator to require authentication and optionally specific roles"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            if roles and session.get('role') not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Student registration with OTP verification - multiple domains support"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', '').strip().lower())
        password = data.get('password', '')
        full_name = sanitize_input(data.get('full_name', '').strip())
        phone = sanitize_input(data.get('phone', '').strip())
        address = sanitize_input(data.get('address', '').strip())
        domain_ids = data.get('domain_ids', [])  # Array of domain IDs
        
        # Validation
        if not all([email, password, full_name, phone]):
            return jsonify({'error': 'Email, password, full name, and phone are required'}), 400
        
        if not domain_ids or len(domain_ids) == 0:
            return jsonify({'error': 'Please select at least one domain'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if email exists
        existing_user = db.execute_query(
            'SELECT id FROM users WHERE email = ?',
            (email,),
            fetch_one=True
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate domains exist and are active
        for domain_id in domain_ids:
            domain = db.execute_query(
                'SELECT id FROM domains WHERE id = ? AND is_active = 1',
                (domain_id,),
                fetch_one=True
            )
            
            if not domain:
                return jsonify({'error': f'Invalid or inactive domain selected'}), 400
        
        # Create user account (unverified until OTP is confirmed)
        password_hash = generate_password_hash(password)
        user_id = db.execute_query(
            'INSERT INTO users (email, password_hash, role, is_verified) VALUES (?, ?, ?, ?)',
            (email, password_hash, 'student', 0)  # is_verified = 0 (needs OTP)
        )
        
        # Store registration data in session for OTP verification
        session['pending_registration'] = {
            'user_id': user_id,
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'address': address,
            'domain_ids': domain_ids
        }
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)
        
        db.execute_query(
            'INSERT INTO otp_verifications (user_id, otp_code, purpose, expires_at) VALUES (?, ?, ?, ?)',
            (user_id, otp_code, 'registration', expires_at)
        )
        
        # Send OTP email (simulation)
        send_email_simulation(
            email,
            'WAPL Registration - OTP Verification',
            f'Your OTP for registration is: {otp_code}\nValid for 10 minutes.'
        )
        
        print(f"Registration initiated for: {email}, User ID: {user_id}")
        return jsonify({
            'message': 'Registration successful. Please verify OTP sent to your email.',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete student registration with PENDING status"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        otp_code = data.get('otp_code', '').strip()
        
        if not all([user_id, otp_code]):
            return jsonify({'error': 'User ID and OTP are required'}), 400
        
        # Verify OTP
        otp_record = db.execute_query(
            '''SELECT * FROM otp_verifications 
               WHERE user_id = ? AND otp_code = ? AND purpose = 'registration' 
               AND is_used = 0 AND expires_at > ?''',
            (user_id, otp_code, datetime.now()),
            fetch_one=True
        )
        
        if not otp_record:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # Mark OTP as used
        db.execute_query(
            'UPDATE otp_verifications SET is_used = 1 WHERE id = ?',
            (otp_record['id'],)
        )
        
        # Mark user as verified
        db.execute_query(
            'UPDATE users SET is_verified = 1 WHERE id = ?',
            (user_id,)
        )
        
        # Get registration data from session
        registration_data = session.get('pending_registration')
        
        if not registration_data or registration_data.get('user_id') != user_id:
            return jsonify({'error': 'Registration data not found. Please register again.'}), 400
        
        # Complete student registration
        try:
            # Generate WAPL ID
            wapl_id = generate_wapl_id()
            
            # Create student record with PENDING status (requires admin approval)
            student_id = db.execute_query(
                '''INSERT INTO students 
                   (user_id, wapl_id, full_name, phone, address, account_status)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    wapl_id,
                    registration_data.get('full_name', ''),
                    registration_data.get('phone', ''),
                    registration_data.get('address', ''),
                    'pending'  # PENDING STATUS - REQUIRES ADMIN APPROVAL
                )
            )
            
            # Assign multiple domains via junction table
            for domain_id in registration_data.get('domain_ids', []):
                db.execute_query(
                    "INSERT INTO student_domains (student_id, domain_id) VALUES (?, ?)",
                    (student_id, domain_id)
                )
            
            # Get user email
            email = registration_data.get('email', '')
            
            # Send confirmation email
            if email:
                send_email_simulation(
                    email,
                    'WAPL Registration Successful',
                    f'''Congratulations! Your registration is complete.

WAPL ID: {wapl_id}

Your account is currently PENDING ADMIN APPROVAL. 
You will be able to login once an administrator approves your account.

You will receive a notification email once your account is activated.

Thank you for registering with WAPL!'''
                )
            
            # Clear session data
            session.pop('pending_registration', None)
            
            print(f"✅ Student registered: {email} (WAPL ID: {wapl_id}) - Status: PENDING")
            
        except Exception as e:
            print(f"Error completing registration: {e}")
            return jsonify({'error': f'Failed to complete registration: {str(e)}'}), 500
        
        return jsonify({
            'message': 'Registration complete! Your account is pending admin approval. You will be notified once approved.',
            'wapl_id': wapl_id,
            'status': 'pending'
        }), 200
        
    except Exception as e:
        print(f"OTP verification error: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for registration"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)
        
        # Invalidate old OTPs
        db.execute_query(
            'UPDATE otp_verifications SET is_used = 1 WHERE user_id = ? AND purpose = ?',
            (user_id, 'registration')
        )
        
        # Create new OTP
        db.execute_query(
            'INSERT INTO otp_verifications (user_id, otp_code, purpose, expires_at) VALUES (?, ?, ?, ?)',
            (user_id, otp_code, 'registration', expires_at)
        )
        
        # Get user email
        user = db.execute_query(
            'SELECT email FROM users WHERE id = ?',
            (user_id,),
            fetch_one=True
        )
        
        if user:
            send_email_simulation(
                user['email'],
                'WAPL Registration - OTP Verification',
                f'Your new OTP for registration is: {otp_code}\nValid for 10 minutes.'
            )
        
        print(f"OTP resent for user_id: {user_id}")
        return jsonify({'message': 'OTP resent successfully'}), 200
        
    except Exception as e:
        print(f"Resend OTP error: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login with student status check"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', '').strip().lower())
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user
        user = db.execute_query(
            'SELECT * FROM users WHERE email = ?',
            (email,),
            fetch_one=True
        )
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user['is_verified']:
            return jsonify({'error': 'Please verify your email first'}), 403
        
        # Enforce student account status
        if user['role'] == 'student':
            student = db.execute_query(
                'SELECT account_status FROM students WHERE user_id = ?',
                (user['id'],),
                fetch_one=True
            )
            if not student:
                return jsonify({'error': 'Student profile not found'}), 404
            
            status = student['account_status']
            if status != 'active':
                return jsonify({'error': f'Account status is {status}. Please contact admin.'}), 403

        # Update last login
        db.execute_query(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user['id'])
        )
        
        # Set session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session.permanent = True
        
        # Redirect based on role
        redirect_urls = {
            'student': '/student/dashboard',
            'hr': '/hr/dashboard',
            'admin': '/secure-admin-panel-wapl/dashboard'
        }
        
        return jsonify({
            'message': 'Login successful',
            'role': user['role'],
            'redirect': redirect_urls.get(user['role'], '/')
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', '').strip().lower())
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get admin user
        user = db.execute_query(
            'SELECT * FROM users WHERE email = ? AND role = ?',
            (email, 'admin'),
            fetch_one=True
        )
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get admin details including super admin status
        admin = db.execute_query(
            'SELECT is_super_admin FROM admins WHERE user_id = ?',
            (user['id'],),
            fetch_one=True
        )
        
        # Update last login
        db.execute_query(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user['id'])
        )
        
        # Set session with super admin flag
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = 'admin'
        session['is_super_admin'] = bool(admin['is_super_admin']) if admin else False
        session.permanent = True
        
        return jsonify({
            'message': 'Admin login successful',
            'is_super_admin': session['is_super_admin'],
            'redirect': '/secure-admin-panel/wapl/dashboard'
        }), 200
        
    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/login')
def login_page():
    return render_template('login.html')


@auth_bp.route('/register')
def register_page():
    return render_template('register.html')


@auth_bp.route('/verify-otp')
def verify_otp_page():
    return render_template('verify_otp.html')


@auth_bp.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password - send OTP"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', '').strip().lower())
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = db.execute_query(
            'SELECT id FROM users WHERE email = ?',
            (email,),
            fetch_one=True
        )
        
        if not user:
            # Don't reveal if email exists
            return jsonify({'message': 'If email exists, password reset link sent'}), 200
        
        # Generate OTP for password reset
        otp_code = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)
        
        db.execute_query(
            'INSERT INTO otp_verifications (user_id, otp_code, purpose, expires_at) VALUES (?, ?, ?, ?)',
            (user['id'], otp_code, 'password_reset', expires_at)
        )
        
        send_email_simulation(
            email,
            'WAPL Password Reset',
            f'Your OTP for password reset is: {otp_code}\nValid for 10 minutes.'
        )
        
        return jsonify({'message': 'If email exists, password reset OTP sent'}), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'error': str(e)}), 500
