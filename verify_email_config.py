#!/usr/bin/env python
"""
Email Configuration Verification Script
Verifies that Gmail settings are correctly configured before deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_email_config():
    """Verify email configuration"""
    
    print("\n" + "="*60)
    print("📧 EMAIL CONFIGURATION VERIFICATION")
    print("="*60 + "\n")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("   Create .env from .env.example:")
        print("   $ cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check Gmail email
    gmail_email = os.getenv('GMAIL_EMAIL', '').strip()
    if not gmail_email:
        print("❌ ERROR: GMAIL_EMAIL not set in .env")
        return False
    
    if gmail_email != 'techinfo506168@gmail.com':
        print(f"⚠️  WARNING: GMAIL_EMAIL is '{gmail_email}'")
        print("   Expected: 'techinfo506168@gmail.com'")
    else:
        print(f"✅ GMAIL_EMAIL: {gmail_email}")
    
    # Check Gmail password
    gmail_password = os.getenv('GMAIL_PASSWORD', '').strip()
    if not gmail_password:
        print("❌ ERROR: GMAIL_PASSWORD not set in .env")
        print("   ⚠️  OTP emails will NOT be sent!")
        print("\n   To fix:")
        print("   1. Enable 2FA on Gmail: https://myaccount.google.com/security")
        print("   2. Generate App Password: https://myaccount.google.com/apppasswords")
        print("   3. Copy the 16-character password")
        print("   4. Add GMAIL_PASSWORD=xxxx xxxx xxxx xxxx to .env")
        return False
    
    # Check password format (should be ~16 chars, possibly with spaces)
    password_clean = gmail_password.replace(' ', '')
    if len(password_clean) < 10:
        print(f"⚠️  WARNING: GMAIL_PASSWORD seems too short ({len(password_clean)} chars)")
        print("   Gmail app passwords should be 16 characters")
        return False
    
    print(f"✅ GMAIL_PASSWORD: {'*' * (len(password_clean) - 4)}{password_clean[-4:]}")
    
    # Check Mail sender name
    mail_sender = os.getenv('MAIL_SENDER_NAME', 'WAPL System')
    print(f"✅ MAIL_SENDER_NAME: {mail_sender}")
    
    print("\n" + "="*60)
    print("CONFIGURATION STATUS: ✅ READY")
    print("="*60 + "\n")
    
    return True

def test_email_import():
    """Test that email functions can be imported"""
    print("\n" + "="*60)
    print("🧪 TESTING EMAIL FUNCTIONS")
    print("="*60 + "\n")
    
    try:
        from utils import send_email_gmail, send_otp_email, send_registration_confirmation_email
        print("✅ Email functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ ERROR importing email functions: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n" + "="*60)
    print("📦 CHECKING DEPENDENCIES")
    print("="*60 + "\n")
    
    dependencies = {
        'flask': 'Flask',
        'flask_session': 'Flask-Session',
        'dotenv': 'python-dotenv',
        'qrcode': 'qrcode',
        'reportlab': 'ReportLab',
        'PIL': 'Pillow'
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Missing dependencies. Install with:")
        print("   $ pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all verifications"""
    print("\n🚀 WAPL EMAIL DEPLOYMENT VERIFICATION\n")
    
    checks = [
        ("Dependencies", test_dependencies),
        ("Email Configuration", verify_email_config),
        ("Email Functions", test_email_import),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY TO DEPLOY")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Test OTP at: http://localhost:5000/register")
        print("3. Check email at: techinfo506168@gmail.com forwarding")
    else:
        print("❌ SOME CHECKS FAILED - SEE ABOVE FOR DETAILS")
        print("\nRead GMAIL_SETUP_GUIDE.md for help")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
