# Render Deployment Guide

## Prerequisites
1. **GitHub Account** - Repository must be on GitHub
2. **Render Account** - Sign up at https://render.com
3. **Environment Variables** - Copy from your `.env` file

---

## Step 1: Push to GitHub

Make sure your code is committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**Important Files Created:**
- `Procfile` - Defines how to start the app
- `render.yaml` - Render configuration
- `.renderignore` - Files to exclude from deployment
- Updated `requirements.txt` - Added gunicorn

---

## Step 2: Connect GitHub to Render

1. Go to https://render.com
2. Sign in with your GitHub account
3. Click **"New +"** → **"Web Service"**
4. Select your repository: `FINAL_WAPL/GITPULL`
5. Click **"Connect"**

---

## Step 3: Configure the Web Service

### Basic Settings:
- **Name**: `wapl-system` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Select closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Environment Variables:
Add these in the Render dashboard:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11` |
| `SECRET_KEY` | (Copy from your .env) |
| `GMAIL_EMAIL` | (Your Gmail) |
| `GMAIL_PASSWORD` | (Your Gmail App Password) |
| `MAIL_SENDER_NAME` | `WAPL System` |

**To find Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows"
3. Copy the 16-character password

---

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (2-5 minutes)
3. Once deployed, you'll get a URL: `https://wapl-system.onrender.com`

---

## Step 5: Verify Deployment

- Visit your live URL
- Default admin login:
  - Email: `admin@wapl.com`
  - Password: `admin123`

---

## Important Notes

### Database
- SQLite database will be stored in `/tmp/` (ephemeral)
- For production, consider using PostgreSQL with Render's database service
- Files uploaded will be lost on redeployment (use cloud storage for production)

### Session Storage
- Uses `/tmp/flask_session` for session files (ephemeral)
- For better persistence, upgrade to Render's more expensive tiers

### Environment Variables in Production
Make sure to update email credentials and secret keys in Render:
1. Go to your Web Service settings
2. Scroll to "Environment"
3. Add/update variables

### Debugging
- View logs in Render dashboard: **Logs** tab
- Check for any error messages
- Ensure all environment variables are set correctly

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"
- **Solution**: Ensure all imports are in `requirements.txt`

### Issue: "Port bind error"
- **Solution**: Render automatically assigns ports. Keep `app.run()` unchanged.

### Issue: "File not found" errors
- **Solution**: Use `/tmp/` for writable storage (already configured)

### Issue: 502 Bad Gateway
- **Solution**: Check logs, ensure `gunicorn app:app` starts without errors

---

## Upgrading from Starter Tier

For production use, consider:
- **PostgreSQL Database** - Persistent data storage
- **Paid Tier** - More reliable, better performance
- **Static File Hosting** - Use Cloudinary or AWS S3 for uploads

---

## Useful Commands

View live logs:
```bash
render logs <service-id>
```

Manually redeploy:
- Push to GitHub (automatic redeploy)
- Or click "Manual Deploy" in Render dashboard

---

## Support
- Render Docs: https://render.com/docs
- Discord Support: https://discord.gg/render-official
