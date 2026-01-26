# WAPL - Student Portfolio and Placement Management System

A comprehensive web application for managing student portfolios, HR assignments, and certificate generation.

## Features

### Student Features
- User registration with OTP verification
- Profile management (personal details, education, skills, projects)
- Profile picture and resume upload
- Certificate generation with QR code
- View assigned HR details

### HR Features
- View assigned students only
- Search/filter students by domain and skills
- View student profiles (read-only)
- Download student resumes
- View active certificates

### Admin Features
- Domain management (add, edit, delete, activate/deactivate)
- HR account management
- Student management
- Student-HR assignment (bulk and individual)
- Certificate management (view all certificates including expired)

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Email**: Gmail SMTP (for OTP delivery)
- **Libraries**: 
  - python-qrcode (QR code generation)
  - ReportLab (PDF generation)
  - python-dotenv (environment variables)
  - bcrypt (password hashing)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Gmail for OTP emails** ⚠️ IMPORTANT
   - Follow [GMAIL_SETUP_GUIDE.md](GMAIL_SETUP_GUIDE.md) for complete instructions
   - Quick setup:
     1. Enable 2-Factor Authentication on `techinfo506168@gmail.com`
     2. Generate a Gmail App Password
     3. Create `.env` file with your Gmail credentials
     ```env
     GMAIL_EMAIL=techinfo506168@gmail.com
     GMAIL_PASSWORD=your_16_char_app_password
     ```

5. **Set up other environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` file

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Main site: http://localhost:5000
   - Admin panel: http://localhost:5000/secure-admin-panel-wapl/login

## Email Configuration

This application sends OTP verification emails via Gmail:

- **Email Account**: techinfo506168@gmail.com
- **Purpose**: User registration OTP, password reset OTP, confirmations
- **Setup Guide**: See [GMAIL_SETUP_GUIDE.md](GMAIL_SETUP_GUIDE.md)

### What Emails Are Sent?

1. **Registration OTP** - When user registers
2. **Registration Confirmation** - After OTP verification
3. **Password Reset OTP** - When user requests password reset

All emails use professional HTML templates with branding.

## Default Admin Credentials

- **Email**: admin@wapl.com
- **Password**: admin123


## Project Structure

```
new/
├── app.py                 # Main Flask application
├── database.py           # Database initialization and helpers
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── student.py       # Student routes
│   ├── hr.py            # HR routes
│   ├── admin.py         # Admin routes
│   └── public.py        # Public routes
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Landing page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── student/         # Student templates
│   ├── hr/              # HR templates
│   └── admin/           # Admin templates
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       └── utils.js     # Utility JavaScript
└── uploads/             # Uploaded files (created automatically)
    ├── profile_pics/
    |── pics/
    ├── resumes/
    ├── certificates/
    └── qr_codes/
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Student registration
- `POST /api/auth/login` - Login (Student/HR)
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/verify-otp` - Verify OTP
- `POST /api/auth/resend-otp` - Resend OTP
- `POST /api/auth/logout` - Logout
- `POST /api/auth/forgot-password` - Password reset

### Student
- `GET /api/student/profile` - Get profile
- `PUT /api/student/profile` - Update profile
- `POST /api/student/upload-photo` - Upload profile picture
- `POST /api/student/upload-resume` - Upload resume
- `GET /api/student/certificate` - Get certificate
- `GET /api/student/certificate/download` - Download certificate PDF
- `GET /api/domains/active` - Get active domains

### HR
- `GET /api/hr/students` - Get assigned students
- `GET /api/hr/student/<id>` - Get student details
- `GET /api/hr/students/filter` - Filter students

### Admin
- `POST /api/admin/hr/create` - Create HR
- `GET /api/admin/hrs` - Get all HRs
- `PUT /api/admin/hr/<id>` - Update HR
- `DELETE /api/admin/hr/<id>` - Delete HR
- `GET /api/admin/students` - Get all students
- `PUT /api/admin/student/<id>` - Update student
- `DELETE /api/admin/student/<id>` - Delete student
- `POST /api/admin/assign-students` - Assign students to HR
- `PUT /api/admin/reassign-student` - Reassign student
- `DELETE /api/admin/unassign-student/<id>` - Unassign student
- `GET /api/admin/unassigned-students` - Get unassigned students
- `GET /api/admin/hr/<id>/students` - Get HR's students
- `GET /api/admin/domains` - Get all domains
- `POST /api/admin/domain` - Create domain
- `PUT /api/admin/domain/<id>` - Update domain
- `DELETE /api/admin/domain/<id>` - Delete domain
- `PATCH /api/admin/domain/<id>/toggle` - Toggle domain status
- `GET /api/admin/certificates` - Get all certificates

### Public
- `GET /verify-certificate/<cert_id>` - Verify certificate
- `GET /api/verify-certificate/<cert_id>` - Verify certificate (API)

## Security Features

- Password hashing with bcrypt
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)
- Session-based authentication
- Role-based access control (RBAC)
- File upload validation (type and size)
- Admin panel hidden URL
- Session timeout (30 minutes)

## File Upload Limits

- Profile Picture: Max 5MB (JPG, JPEG, PNG)
- Resume: Max 10MB (PDF, DOC, DOCX)

## Certificate Generation

Certificates are automatically generated upon successful student registration with:
- Unique certificate ID (CERT + timestamp + random string)
- QR code for verification
- PDF format with student details
- 1-year validity from issue date

## WAPL ID Format

WAPL IDs are auto-generated in the format: `WAPL + YEAR + 6-digit sequential number`
Example: `WAPL2026000001`

## Development Notes

- Email sending is simulated (console log) - implement actual email service for production
- Database is SQLite - consider PostgreSQL for production
- Session storage is filesystem - consider Redis for production
- Admin panel URL is intentionally hidden from frontend navigation

