import secrets
import string
import qrcode
from io import BytesIO
import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from PIL import Image as PILImage, ImageDraw, ImageFont
import base64
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail Configuration
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'techinfo506168@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '')
MAIL_SENDER_NAME = os.getenv('MAIL_SENDER_NAME', 'WAPL System')

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_wapl_id():
    """Generate unique WAPL ID in format WAPL2026XXXXXX"""
    import sqlite3
    from database import DB_NAME
    
    conn = None
    try:
        # Connect directly
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the latest WAPL ID
        cursor.execute("SELECT wapl_id FROM students ORDER BY id DESC LIMIT 1")
        last_student = cursor.fetchone()
        
        if last_student and last_student['wapl_id']:
            # Extract number from last WAPL ID (e.g., WAPL2026000001 -> 1)
            last_number = int(last_student['wapl_id'][-6:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        # Format: WAPL + YEAR + 6-digit number
        year = datetime.now().year
        wapl_id = f"WAPL{year}{new_number:06d}"
        
        return wapl_id
        
    except Exception as e:
        print(f"Error generating WAPL ID: {e}")
        # Fallback to random number if database query fails
        year = datetime.now().year
        random_num = random.randint(1, 999999)
        return f"WAPL{year}{random_num:06d}"
    finally:
        if conn:
            conn.close()


def generate_certificate_id():
    """Generate certificate unique ID: CERT + timestamp + 6-char random string"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f'CERT{timestamp}{random_str}'

def generate_qr_code(data, output_path):
    """Generate QR code and save to file"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path

def generate_certificate_pdf(student_name, wapl_id, domain_name, issue_date, expiry_date, qr_code_path, output_path, hr_name=None, certificate_text=None):
    """Generate certificate by overlaying text on base image"""
    try:
        # Use base certificate image with logo
        base_image_path = 'uploads/certificates/certificate_wapl_id.jpg'
        
        if not os.path.exists(base_image_path):
            # Fallback to ReportLab if template missing
            return generate_certificate_pdf_reportlab(student_name, wapl_id, domain_name, issue_date, expiry_date, qr_code_path, output_path, hr_name, certificate_text)
        
        # Open base image
        img = PILImage.open(base_image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        w, h = img.size
        cx = w // 2  # Center X
        
        # Define colors
        GOLD = "#8a6a2f"
        BLUE = "#1f2b44"
        BLACK = "black"
        
        # Load fonts - adjust paths if needed
        try:
            name_font = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 90)
            title_font = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 54)
            body_font = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 44)
            small_font = ImageFont.truetype("fonts/PlayfairDisplay-Regular.ttf", 36)
        except:
            # Fallback to default if fonts not found
            name_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Title text
        draw.text((cx, 395), "This certificate is proudly presented to", GOLD, title_font, anchor="mm")
        
        # Student name (prominent)
        draw.text((cx, 480), student_name.upper(), BLUE, name_font, anchor="mm")
        
        # Body text with wrapping
        if certificate_text:
            body_text = certificate_text
        else:
            body_text = f"This certificate recognizes the candidate's hands-on experience in {domain_name} and successful assessment by WAPL."
        
        # Simple text wrapping
        wrapped_lines = []
        words = body_text.split()
        current_line = ""
        max_width = w - 400
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=body_font)
            if bbox[2] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
        
        if current_line:
            wrapped_lines.append(current_line)
        
        # Draw wrapped body text
        body_y = 580
        for line in wrapped_lines:
            draw.text((cx, body_y), line, GOLD, body_font, anchor="ma")
            body_y += 58  # Line spacing
        
        # Bottom section coordinates
        left_x = 180
        base_y = h - 300
        
        # Issue and expiry dates
        draw.text((left_x, base_y), f"Valid From: {issue_date}", BLACK, small_font)
        draw.text((left_x, base_y + 50), f"Valid Until: {expiry_date}", BLACK, small_font)
        draw.text((left_x, base_y + 100), f"WAPL ID: {wapl_id}", BLACK, small_font)
        
        # HR name (if provided)
        if hr_name:
            draw.text((left_x, base_y + 150), f"Issued by: {hr_name}", BLACK, small_font)
        
        # QR Code
        if os.path.exists(qr_code_path):
            qr_img = PILImage.open(qr_code_path)
            qr_img = qr_img.resize((220, 220))
            img.paste(qr_img, (w - 400, base_y - 80))
        
        # Convert to PDF and save
        rgb_img = img.convert('RGB')
        rgb_img.save(output_path, 'PDF')
        return output_path
    
    except Exception as e:
        print(f"Error generating certificate: {str(e)}")
        # Fallback to ReportLab
        return generate_certificate_pdf_reportlab(student_name, wapl_id, domain_name, issue_date, expiry_date, qr_code_path, output_path, hr_name, certificate_text)


def generate_certificate_pdf_reportlab(student_name, wapl_id, domain_name, issue_date, expiry_date, qr_code_path, output_path, hr_name=None, certificate_text=None):
    """Fallback: Generate professional PDF certificate using ReportLab"""
    # Create custom canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Draw decorative border
    border_color = colors.HexColor('#1a237e')
    c.setStrokeColor(border_color)
    c.setLineWidth(3)
    c.rect(0.5*cm, 0.5*cm, width - 1*cm, height - 1*cm)
    
    # Draw inner decorative line
    c.setLineWidth(1)
    c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)
    
    # Add corner decorative elements
    accent_color = colors.HexColor('#283593')
    c.setFillColor(accent_color)
    corner_size = 15
    c.circle(1.5*cm, height - 1.5*cm, corner_size, fill=1)
    c.circle(width - 1.5*cm, height - 1.5*cm, corner_size, fill=1)
    c.circle(1.5*cm, 1.5*cm, corner_size, fill=1)
    c.circle(width - 1.5*cm, 1.5*cm, corner_size, fill=1)
    
    # Title
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.drawCentredString(width/2, height - 3*cm, "CERTIFICATE OF REGISTRATION")
    
    # Subtitle line
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor('#424242'))
    c.drawCentredString(width/2, height - 3.7*cm, "WAPL - Student Portfolio and Placement Management System")
    
    # Main text
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor('#424242'))
    c.drawCentredString(width/2, height - 5.5*cm, "This is to certify that")
    
    # Student name (prominent)
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.drawCentredString(width/2, height - 6.8*cm, student_name)
    
    # Details section
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor('#424242'))
    c.drawCentredString(width/2, height - 7.7*cm, "has successfully registered with WAPL")
    
    # Details table-like layout
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor('#283593'))
    c.drawString(2*cm, height - 8.8*cm, "WAPL ID:")
    c.drawString(2*cm, height - 9.5*cm, "Domain:")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.drawString(4.5*cm, height - 8.8*cm, wapl_id)
    c.drawString(4.5*cm, height - 9.5*cm, domain_name)
    
    # HR Name
    if hr_name:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor('#283593'))
        c.drawString(2*cm, height - 10.2*cm, "Issued by:")
        
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor('#1a237e'))
        c.drawString(4.5*cm, height - 10.2*cm, hr_name)
    
    # Validity dates
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor('#283593'))
    c.drawString(2*cm, height - 11*cm, "Issue Date:")
    c.drawString(2*cm, height - 11.7*cm, "Expiry Date:")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.drawString(4.5*cm, height - 11*cm, str(issue_date))
    c.drawString(4.5*cm, height - 11.7*cm, str(expiry_date))
    
    # Certificate text/matter
    if certificate_text:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor('#424242'))
        # Wrap text
        from reportlab.lib.utils import simpleSplit
        lines = simpleSplit(certificate_text, "Helvetica", 10, width - 4*cm)
        text_y = height - 13*cm
        for line in lines[:4]:  # Max 4 lines
            c.drawString(1.5*cm, text_y, line)
            text_y -= 0.5*cm
    
    # QR Code section
    if os.path.exists(qr_code_path):
        qr_x = width/2 - 1.2*cm
        qr_y = height - 15.5*cm
        c.drawImage(qr_code_path, qr_x, qr_y, width=2.4*cm, height=2.4*cm)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(width/2, qr_y - 0.5*cm, "Scan QR Code to Verify")
    
    # Certificate ID footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#999999'))
    c.drawCentredString(width/2, 1.2*cm, f"Certificate ID: {wapl_id}")
    
    # Save the canvas
    c.save()
    return output_path

def send_email_simulation(to_email, subject, body):
    """Simulate email sending (console log for now)"""
    print(f"\n{'='*60}")
    print(f"EMAIL SIMULATION")
    print(f"{'='*60}")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"{'='*60}\n")


def send_email_gmail(to_email, subject, body, html_body=None, attachment_path=None):
    """Send email using Gmail SMTP"""
    try:
        # Verify credentials are set
        if not GMAIL_EMAIL or not GMAIL_PASSWORD:
            print("⚠️ WARNING: Gmail credentials not configured!")
            print("Please set GMAIL_EMAIL and GMAIL_PASSWORD in .env file")
            # Fallback to simulation
            send_email_simulation(to_email, subject, body)
            return False
        
        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = f"{MAIL_SENDER_NAME} <{GMAIL_EMAIL}>"
        message['To'] = to_email
        message['Subject'] = subject
        
        # Attach plain text body
        message.attach(MIMEText(body, 'plain'))
        
        # Attach HTML body if provided
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        
        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_path)}')
                message.attach(part)
        
        # Send email via Gmail SMTP
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        smtp_server.send_message(message)
        smtp_server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"❌ Gmail authentication failed!")
        print("Please check your GMAIL_EMAIL and GMAIL_PASSWORD in .env file")
        print("Note: Use Gmail App Password, not your regular password")
        print("Generate at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print(f"Falling back to simulation...")
        send_email_simulation(to_email, subject, body)
        return False


def send_otp_email(to_email, otp_code, full_name="User"):
    """Send OTP email with professional HTML template"""
    subject = "WAPL Registration - OTP Verification"
    
    # Plain text body
    text_body = f"""
Hello {full_name},

Your OTP for WAPL Registration is: {otp_code}

This OTP is valid for 10 minutes.

If you did not request this OTP, please ignore this email.

Best regards,
WAPL System
"""
    
    # HTML body with styling
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #1f2b44;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 20px;
            background-color: white;
        }}
        .otp-box {{
            background-color: #f0f0f0;
            border: 2px solid #1f2b44;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .otp-code {{
            font-size: 36px;
            font-weight: bold;
            color: #1f2b44;
            letter-spacing: 5px;
            font-family: 'Courier New', monospace;
        }}
        .validity {{
            color: #e74c3c;
            font-weight: bold;
            margin-top: 10px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 10px;
            border-radius: 4px;
            margin: 15px 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>WAPL Registration</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{full_name}</strong>,</p>
            
            <p>Thank you for registering with WAPL (Student Portfolio and Placement Management System)!</p>
            
            <p>Your OTP (One-Time Password) for email verification is:</p>
            
            <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="validity">⏱️ Valid for 10 minutes</div>
            </div>
            
            <div class="warning">
                <strong>🔒 Security Notice:</strong> Never share this OTP with anyone. WAPL team will never ask for your OTP.
            </div>
            
            <p>If you did not request this OTP, you can safely ignore this email.</p>
            
            <p>Need help? Contact our support team.</p>
            
            <p>Best regards,<br><strong>WAPL System</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>&copy; 2026 WAPL - Student Portfolio and Placement Management System</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email_gmail(to_email, subject, text_body, html_body)


def send_registration_confirmation_email(to_email, full_name, wapl_id):
    """Send registration confirmation email"""
    subject = "WAPL Registration Successful"
    
    text_body = f"""
Hello {full_name},

Congratulations! Your registration with WAPL is complete.

Your WAPL ID: {wapl_id}

Your account is currently pending admin approval. You will receive an email once your account is activated.

Best regards,
WAPL System
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #27ae60;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 20px;
            background-color: white;
        }}
        .wapl-id-box {{
            background-color: #ecf0f1;
            border: 2px solid #27ae60;
            padding: 15px;
            text-align: center;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .wapl-id {{
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
            font-family: 'Courier New', monospace;
        }}
        .info-box {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Registration Successful</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{full_name}</strong>,</p>
            
            <p>Congratulations! Your registration with WAPL is complete. We're excited to have you on board!</p>
            
            <p>Your unique WAPL ID is:</p>
            <div class="wapl-id-box">
                <div class="wapl-id">{wapl_id}</div>
            </div>
            
            <div class="info-box">
                <strong>ℹ️ Next Step:</strong> Your account is currently pending admin approval. You will receive an email notification once your account is activated and ready to use.
            </div>
            
            <p>Thank you for joining WAPL - Student Portfolio and Placement Management System!</p>
            
            <p>Best regards,<br><strong>WAPL System</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>&copy; 2026 WAPL</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email_gmail(to_email, subject, text_body, html_body)


def send_account_activation_email(to_email, full_name, wapl_id):
    """Send account activation email when admin approves student"""
    subject = "WAPL Account Activated - Ready to Use"
    
    text_body = f"""
Hello {full_name},

Great news! Your WAPL account has been activated by the admin.

Your WAPL ID: {wapl_id}

Your account is now active and ready to use. You can now:
- Access your student dashboard
- View your portfolio
- Participate in recruitment activities
- Download your certificates

You can log in using your registered email and password.

Best regards,
WAPL System
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #27ae60;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 20px;
            background-color: white;
        }}
        .success-message {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }}
        .wapl-id-box {{
            background-color: #ecf0f1;
            border: 2px solid #27ae60;
            padding: 15px;
            text-align: center;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .wapl-id {{
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
            font-family: 'Courier New', monospace;
        }}
        .features {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
        }}
        .features ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .features li {{
            margin: 8px 0;
        }}
        .cta-button {{
            display: inline-block;
            background-color: #27ae60;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Account Activated</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{full_name}</strong>,</p>
            
            <div class="success-message">
                🎉 Your WAPL account has been activated!
            </div>
            
            <p>Congratulations! The admin has reviewed and approved your registration. Your account is now active and ready to use.</p>
            
            <p>Your WAPL ID:</p>
            <div class="wapl-id-box">
                <div class="wapl-id">{wapl_id}</div>
            </div>
            
            <div class="features">
                <strong>✨ What you can now do:</strong>
                <ul>
                    <li>Access your personalized student dashboard</li>
                    <li>Build and manage your portfolio</li>
                    <li>Participate in recruitment activities</li>
                    <li>Download your certificates</li>
                    <li>Update your profile and skills</li>
                </ul>
            </div>
            
            <p><strong>How to get started:</strong></p>
            <p>Log in to your account using your registered email and password. You'll be directed to your personalized dashboard.</p>
            
            <p>If you have any questions or need assistance, please contact our support team.</p>
            
            <p>Best regards,<br><strong>WAPL System</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>&copy; 2026 WAPL - Student Portfolio and Placement Management System</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email_gmail(to_email, subject, text_body, html_body)

def sanitize_input(text):
    """Sanitize input to prevent XSS"""
    if not text:
        return ""
    import html
    return html.escape(str(text))

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

from storage import Storage

def save_uploaded_file(file, upload_folder, user_id, file_type):
    """Save uploaded file using Storage abstraction - returns path or URL"""
    if file and file.filename:
        # Extract subfolder from e.g. 'uploads/resumes' -> 'resumes'
        normalized_folder = upload_folder.replace('\\', '/')
        
        if 'uploads/' in normalized_folder:
            parts = normalized_folder.split('uploads/')
            subfolder = parts[1] if len(parts) > 1 else ''
        else:
            subfolder = normalized_folder
            
        return Storage.save_file(file, subfolder=subfolder)
    return None
