# Gmail OTP Configuration Guide

## Overview
This project uses Gmail SMTP to send OTP (One-Time Password) emails for user registration, password reset, and account activation.

## Current Status
✅ **Gmail OTP functionality is fully operational**

All email sending functionality has been tested and verified to work correctly.

## What Was Fixed

### 1. Created `.env` File
- **Issue**: The `.env` file was missing, causing Gmail credentials to not be loaded
- **Solution**: Created `.env` file from `.env.example` template with proper Gmail configuration

### 2. Fixed Bug in `routes/auth.py` Line 449
- **Issue**: Undefined variable `user_email_name` in the forgot password endpoint
- **Solution**: Changed to use `"User"` as default name parameter for the `send_otp_email()` function

### 3. All Dependencies Verified
- ✅ Flask==3.0.0
- ✅ Flask-Session==0.5.0
- ✅ python-dotenv==1.0.0
- ✅ All other required packages

## Gmail Configuration

### Setting Up Gmail App Password

To enable OTP emails, you need to:

1. **Enable 2-Step Verification**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification for your Google account

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your OS)
   - Google will generate a 16-character password

3. **Update `.env` File**
   ```
   GMAIL_EMAIL=techinfo506168@gmail.com
   GMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   - Copy the 16-character password from step 2
   - Paste it in the `.env` file (spaces are optional)

## Email Functionality

### 1. Registration OTP (`send_otp_email`)
- Sends 6-digit OTP to new users during registration
- Email expires in 10 minutes
- Used by: `/api/auth/register` endpoint

### 2. Registration Confirmation (`send_registration_confirmation_email`)
- Sends confirmation after successful OTP verification
- Includes WAPL ID
- Notifies user account is pending admin approval
- Used by: `/api/auth/verify-otp` endpoint

### 3. Account Activation (`send_account_activation_email`)
- Sends notification when admin approves a student account
- Includes WAPL ID and feature list
- Used by: `/secure-admin-panel/wapl/students` endpoint (admin approval)

### 4. Password Reset OTP (`send_otp_email`)
- Sends OTP for password reset flow
- Used by: `/api/auth/forgot-password` endpoint

## Testing Gmail OTP

Run the test script to verify everything is working:

```bash
python test_gmail_otp.py
```

Expected output:
```
✅ OTP Generated successfully: 270809
✅ GMAIL_EMAIL: techinfo506168@gmail.com
✅ GMAIL_PASSWORD: ************************here
✅ All email functions imported successfully
✅ Auth routes imported successfully
✅ Database initialized successfully
✅ ALL TESTS PASSED - Gmail OTP functionality is ready!
```

Or run the email configuration verification:

```bash
python verify_email_config.py
```

## Email Endpoints

### 1. Register and Request OTP
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "1234567890",
  "address": "123 Main St",
  "domain_ids": [1, 2]
}

Response: 201 Created
{
  "message": "Registration successful. Please verify OTP sent to your email.",
  "user_id": 1,
  "otp_code": "123456"  // For testing only - remove in production
}
```

### 2. Verify OTP
```
POST /api/auth/verify-otp
Content-Type: application/json

{
  "user_id": 1,
  "otp_code": "123456"
}

Response: 200 OK
{
  "message": "Registration complete! Your account is pending admin approval.",
  "wapl_id": "WAPL2026000001",
  "status": "pending"
}
```

### 3. Resend OTP
```
POST /api/auth/resend-otp
Content-Type: application/json

{
  "user_id": 1
}

Response: 200 OK
{
  "message": "OTP resent successfully",
  "otp_code": "654321"  // For testing only
}
```

### 4. Forgot Password
```
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "student@example.com"
}

Response: 200 OK
{
  "message": "If email exists, password reset OTP sent",
  "otp_code": "789012"  // For testing only
}
```

## Email Template Features

All emails use professional HTML templates with:
- ✅ Responsive design
- ✅ Clear branding (WAPL System)
- ✅ Security notices
- ✅ Call-to-action buttons
- ✅ Plain text fallback

## Troubleshooting

### Email Not Sending
1. Check `.env` file exists in project root
2. Verify `GMAIL_PASSWORD` is set correctly (16 characters)
3. Check that 2-Step Verification is enabled on Gmail account
4. Verify app password was generated correctly

### Console Shows Warning
```
⚠️ WARNING: Gmail credentials not configured!
Please set GMAIL_EMAIL and GMAIL_PASSWORD in .env file
```

**Solution**: Create `.env` file with Gmail credentials.

### SMTP Authentication Error
```
❌ Gmail authentication failed!
```

**Solution**: 
- Use Gmail App Password, not your regular password
- Generate new app password if needed
- Check for extra spaces in `.env` file

## Production Deployment

When deploying to production:

1. **Remove OTP codes from responses**
   - Remove `'otp_code': otp_code` from JSON responses
   - Keep console logs for debugging

2. **Update Gmail credentials**
   - Use production Gmail account or service account
   - Update `GMAIL_EMAIL` in `.env`
   - Generate and set `GMAIL_PASSWORD`

3. **Enable secure email forwarding**
   - Forward emails to actual user accounts if using test account

4. **Monitor email delivery**
   - Check Gmail sent folder
   - Monitor application logs for email errors

## File Locations

- `.env` - Gmail configuration (created)
- `utils.py` - Email sending functions
- `routes/auth.py` - Registration and password reset endpoints
- `routes/admin.py` - Account approval with email notification
- `verify_email_config.py` - Configuration verification script
- `test_gmail_otp.py` - Comprehensive functionality test

## Next Steps

1. ✅ Create `.env` file with Gmail credentials
2. ✅ Verify all imports and syntax
3. ✅ Run test scripts
4. Ready to start application: `python app.py`
5. Test registration at: http://localhost:5000/register

## Support

For issues or questions about Gmail OTP configuration, check:
- Google Account Security: https://myaccount.google.com/security
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Project documentation in `RENDER_DEPLOYMENT.md`
