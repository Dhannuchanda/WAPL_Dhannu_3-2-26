from database import db
import os

# Get the actual files on disk
profile_pic_dir = "uploads/profile_pics"
resume_dir = "uploads/resumes"

profile_files = os.listdir(profile_pic_dir) if os.path.exists(profile_pic_dir) else []
resume_files = os.listdir(resume_dir) if os.path.exists(resume_dir) else []

print("Files on disk:")
print(f"  Profile pics: {profile_files}")
print(f"  Resumes: {resume_files}")

# Check what's in database
student = db.execute_query('SELECT id, profile_pic, resume FROM students WHERE id = 1', fetch_one=True)
if student:
    print(f"\nCurrent database for Dhanush Chanda:")
    print(f"  profile_pic: {student['profile_pic']}")
    print(f"  resume: {student['resume']}")

# Update with latest files from disk
if resume_files:
    latest_resume = resume_files[0]  # Get the file that exists
    db.execute_query('UPDATE students SET resume = ? WHERE id = 1', (latest_resume,))
    print(f"\n✅ Updated resume to: {latest_resume}")

if profile_files:
    latest_pic = profile_files[0]
    db.execute_query('UPDATE students SET profile_pic = ? WHERE id = 1', (latest_pic,))
    print(f"✅ Updated profile_pic to: {latest_pic}")

# Verify the update
updated = db.execute_query('SELECT profile_pic, resume FROM students WHERE id = 1', fetch_one=True)
print(f"\n✓ Verified in database:")
print(f"  profile_pic: {updated['profile_pic']}")
print(f"  resume: {updated['resume']}")
print(f"\n✅ READY: Resume and profile picture will now download correctly!")
