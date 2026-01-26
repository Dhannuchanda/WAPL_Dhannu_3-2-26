import json
from database import db

# Get student 1
student = db.execute_query(
    'SELECT resume FROM students WHERE id = 1',
    fetch_one=True
)

print("Testing resume download path construction:")
print(f"Database value: {student['resume']}")

# Simulate the template JavaScript logic
resume_value = student['resume']
resume_file = resume_value.split('/').pop().split('\\').pop()
resume_path = f"/download/resumes/{resume_file}"

print(f"After split: {resume_file}")
print(f"Final URL: {resume_path}")

# Test with old format (if it had the folder path)
print("\nTesting with old format (with folder path):")
old_format = "resumes/1_20260125231810_DHANUSH CHANDA.pdf"
old_file = old_format.split('/').pop().split('\\').pop()
old_path = f"/download/resumes/{old_file}"

print(f"Database value: {old_format}")
print(f"After split: {old_file}")
print(f"Final URL: {old_path}")

# Verify the file exists
import os
file_path = f"uploads/resumes/{resume_file}"
if os.path.exists(file_path):
    print(f"\n✅ File exists: {file_path}")
else:
    print(f"\n❌ File NOT found: {file_path}")
