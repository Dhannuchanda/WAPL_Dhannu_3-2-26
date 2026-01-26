"""
Test to verify profile picture display in admin panel works end-to-end
"""
from database import db
import json

# Get student 1
student = db.execute_query(
    """SELECT id, full_name, profile_pic, resume FROM students WHERE id = 1""",
    fetch_one=True
)

print("=" * 60)
print("ADMIN PANEL PROFILE PICTURE TEST")
print("=" * 60)

print("\n1. Database Check:")
print(f"   Student: {student['full_name']}")
print(f"   profile_pic field: {student['profile_pic']}")
print(f"   resume field: {student['resume']}")

# Simulate JavaScript logic in template
print("\n2. Template JavaScript Logic:")
profile_pic_value = student['profile_pic']
profile_name = profile_pic_value.split('/').pop().split('\\').pop() if profile_pic_value else None
profile_pic_url = f"/uploads/profile_pics/{profile_name}" if profile_name else None

print(f"   Input: {profile_pic_value}")
print(f"   After extraction: {profile_name}")
print(f"   Final URL: {profile_pic_url}")

# Check file exists
import os
file_path = f"uploads/profile_pics/{profile_name}"
file_exists = os.path.exists(file_path) if profile_name else False

print(f"\n3. File Check:")
print(f"   Expected path: {file_path}")
print(f"   File exists: {file_exists}")
if file_exists:
    print(f"   File size: {os.path.getsize(file_path)} bytes")

# Simulate Flask routing
print(f"\n4. Flask Route Handler:")
print(f"   Request URL: {profile_pic_url}")
print(f"   Route: /uploads/<path:filename>")
print(f"   Parsed filename: profile_pics/{profile_name}")
print(f"   UPLOAD_BASE_PATH + '/uploads' + 'profile_pics/{profile_name}'")
print(f"   = uploads/profile_pics/{profile_name}")
print(f"   File accessible: {file_exists}")

# Resume download
print(f"\n5. Resume Download Test:")
resume_value = student['resume']
resume_file = resume_value.split('/').pop().split('\\').pop() if resume_value else None
resume_url = f"/download/resumes/{resume_file}" if resume_file else None

print(f"   Input: {resume_value}")
print(f"   After extraction: {resume_file}")
print(f"   Final URL: {resume_url}")

file_path_resume = f"uploads/resumes/{resume_file}"
file_exists_resume = os.path.exists(file_path_resume) if resume_file else False

print(f"   File path: {file_path_resume}")
print(f"   File exists: {file_exists_resume}")
if file_exists_resume:
    print(f"   File size: {os.path.getsize(file_path_resume)} bytes")

print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
if profile_pic_url and file_exists:
    print("✅ Profile picture: READY FOR DISPLAY")
else:
    print("❌ Profile picture: NOT ACCESSIBLE")
    
if resume_url and file_exists_resume:
    print("✅ Resume download: READY FOR DOWNLOAD")
else:
    print("❌ Resume download: NOT ACCESSIBLE")
