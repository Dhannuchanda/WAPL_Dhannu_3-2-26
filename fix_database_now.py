import sqlite3
import os

db_path = 'wapl_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current state
print("Current database contents:")
cursor.execute("SELECT id, profile_pic, resume FROM students WHERE profile_pic IS NOT NULL LIMIT 5")
students = cursor.fetchall()
for student in students:
    print(f"Student {student[0]}: profile_pic={student[1]}, resume={student[2]}")

# Fix profile_pic - extract just the filename
print("\n\nFixing profile_pic...")
cursor.execute("SELECT id, profile_pic FROM students WHERE profile_pic IS NOT NULL")
pic_records = cursor.fetchall()

for student_id, pic_path in pic_records:
    if pic_path and ('/' in pic_path or '\\' in pic_path):
        # Extract just the filename
        filename = os.path.basename(pic_path)
        print(f"Student {student_id}: {pic_path} -> {filename}")
        cursor.execute("UPDATE students SET profile_pic = ? WHERE id = ?", (filename, student_id))

# Fix resume - extract just the filename
print("\nFixing resume...")
cursor.execute("SELECT id, resume FROM students WHERE resume IS NOT NULL")
resume_records = cursor.fetchall()

for student_id, resume_path in resume_records:
    if resume_path and ('/' in resume_path or '\\' in resume_path):
        # Extract just the filename
        filename = os.path.basename(resume_path)
        print(f"Student {student_id}: {resume_path} -> {filename}")
        cursor.execute("UPDATE students SET resume = ? WHERE id = ?", (filename, student_id))

conn.commit()

# Verify
print("\n\n✅ Verification after fixes:")
cursor.execute("SELECT id, profile_pic, resume FROM students WHERE profile_pic IS NOT NULL LIMIT 5")
students = cursor.fetchall()
for student in students:
    print(f"Student {student[0]}: profile_pic={student[1]}, resume={student[2]}")

conn.close()
print("\n✅ Database fixed successfully!")
