from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_session import Session
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import secrets
import string

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 1800)))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # 15MB max file size

Session(app)

# Import database and routes
from database import init_db, db
from routes import auth_bp, student_bp, hr_bp, admin_bp, public_bp

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(hr_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(public_bp)

# Create upload directories
os.makedirs('uploads/profile_pics', exist_ok=True)
os.makedirs('uploads/resumes', exist_ok=True)
os.makedirs('uploads/certificates', exist_ok=True)
os.makedirs('uploads/qr_codes', exist_ok=True)

# Keep uploads tree ready before any request tries to write to disk

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
