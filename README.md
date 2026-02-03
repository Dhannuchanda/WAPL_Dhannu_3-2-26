# 🎓 WAPL ID Management System

A comprehensive web application for managing student IDs, certificates, and HR recruitment workflows.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 👨‍🎓 Student Portal
- Self-registration with OTP email verification
- Profile management (photo, resume, skills)
- View and download certificates
- Track application status

### 👨‍💼 HR Portal  
- View assigned students
- Track recruitment progress
- Download student resumes & certificates
- Manage student evaluations

### 🔐 Admin Panel
- Complete student management (CRUD)
- HR management and student assignment
- Domain/department management
- Certificate generation with QR codes
- Dashboard with analytics

### 🏆 Certificate System
- Auto-generated PDF certificates
- QR code verification
- Public verification page
- Certificate regeneration

## 🛠️ Tech Stack

- **Backend**: Flask 3.0, Python 3.11
- **Database**: PostgreSQL (Supabase)
- **Storage**: Supabase Storage
- **Email**: Gmail SMTP (OTP)
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode + Pillow

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account (free tier works)
- Gmail account with App Password

### Installation

```bash
# Clone the repository
git clone https://github.com/Dhannuchanda/WAPL_Dhannu_3-2-26.git
cd WAPL_Dhannu_3-2-26

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
python app.py
```

### Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

## 📁 Project Structure

```
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── database.py         # Database connection & models
├── storage.py          # File storage (Supabase/Local)
├── utils.py            # Utility functions
├── wsgi.py             # WSGI entry point
├── routes/
│   ├── admin.py        # Admin API routes
│   ├── auth.py         # Authentication routes
│   ├── hr.py           # HR portal routes
│   ├── public.py       # Public routes
│   └── student.py      # Student portal routes
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images
└── uploads/            # User uploads (local dev)
```

## 🌐 Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect repo on [railway.app](https://railway.app)
3. Add environment variables
4. Deploy!

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@wapl.com | admin123 |

⚠️ **Change these immediately in production!**

## 📸 Screenshots

### Admin Dashboard
- Student management with bulk actions
- Certificate issuance workflow
- Real-time statistics

### Student Portal
- Clean, responsive design
- Mobile-friendly interface
- Easy certificate access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Dhannu Chanda**

---

⭐ Star this repo if you find it helpful!

