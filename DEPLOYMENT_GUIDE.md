# 🚀 WAPL ID System - Deployment Guide

## ✅ Pre-Deployment Checklist

### 1. Supabase Setup (Already Done)
- [x] PostgreSQL database created
- [x] Database URL configured
- [x] Storage bucket created (if using file uploads)

### 2. Environment Variables Required
Set these in your hosting platform (Render/Vercel/Railway):

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | ✅ Yes |
| `SECRET_KEY` | Flask secret key (auto-generate in production) | ✅ Yes |
| `SUPABASE_URL` | Your Supabase project URL | ✅ Yes |
| `SUPABASE_KEY` | Supabase anon/public key | ✅ Yes |
| `SUPABASE_BUCKET` | Storage bucket name (default: `uploads`) | Optional |
| `GMAIL_USER` | Gmail address for OTP emails | ✅ Yes |
| `GMAIL_APP_PASSWORD` | Gmail App Password (16 chars) | ✅ Yes |
| `APP_DOMAIN` | Your deployed domain (e.g., `https://wapl.onrender.com`) | Optional |

---

## 🌐 Deployment Options

### Option A: Render.com (Recommended)

1. **Create account** at [render.com](https://render.com)

2. **Connect GitHub repo**:
   - New → Web Service
   - Connect your GitHub repository

3. **Configure build**:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Add environment variables** in Render Dashboard:
   ```
   DATABASE_URL = postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres
   SECRET_KEY = (generate random string)
   SUPABASE_URL = https://xxx.supabase.co
   SUPABASE_KEY = your-anon-key
   GMAIL_USER = your-email@gmail.com
   GMAIL_APP_PASSWORD = your-16-char-password
   APP_DOMAIN = https://your-app.onrender.com
   ```

5. **Deploy** and wait for build to complete

---

### Option B: Railway.app

1. **Create account** at [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - New Project → Deploy from GitHub
   - Select repository

3. **Add environment variables** in Variables tab

4. **Deploy** automatically triggers

---

### Option C: Vercel (with limitations)

⚠️ **Note**: Vercel has serverless limitations. For full functionality, use Render or Railway.

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Add environment variables in Vercel dashboard

---

## 🔧 Post-Deployment Steps

### 1. Verify Database Connection
- Visit: `https://your-app.com/secure-admin-panel/wapl/login`
- Login with: `admin@wapl.com` / `admin123`

### 2. Test All Features
- [ ] Admin login works
- [ ] Student registration with OTP
- [ ] Certificate issuance
- [ ] Certificate verification via QR code
- [ ] File uploads (profile pics, resumes)

### 3. Change Default Admin Password
After first login, change the admin password!

---

## 🐛 Troubleshooting

### "500 Internal Server Error"
- Check logs in hosting dashboard
- Verify all environment variables are set
- Ensure DATABASE_URL is correct

### "Database connection failed"
- Check DATABASE_URL format: `postgresql://user:password@host:5432/database`
- Verify Supabase is not paused (free tier pauses after inactivity)

### "OTP emails not sending"
- Verify GMAIL_USER and GMAIL_APP_PASSWORD
- Ensure 2FA is enabled on Gmail
- Use App Password, not regular password

### "File uploads failing"
- Check SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET
- Verify storage bucket exists and has proper policies

---

## 📁 Files Modified for Deployment

- `requirements.txt` - Added PostgreSQL and all dependencies
- `render.yaml` - Render deployment configuration
- `Procfile` - Gunicorn startup command
- `app.py` - Environment-aware directory handling
- `.env.example` - Template for environment variables

---

## 🔐 Security Checklist

- [ ] Change SECRET_KEY to random value
- [ ] Change default admin password
- [ ] Use HTTPS only (enforced by hosting platforms)
- [ ] Keep SUPABASE_KEY secure (use anon key, not service key)
- [ ] Enable Row Level Security in Supabase if needed
