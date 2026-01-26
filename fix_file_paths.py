from database import db

# Get all students with file paths
students = db.execute_query('SELECT id, profile_pic, resume FROM students WHERE profile_pic IS NOT NULL OR resume IS NOT NULL', fetch_all=True)

print(f"Found {len(students)} students with files")

for student in students:
    student_id = student['id']
    profile_pic = student['profile_pic']
    resume = student['resume']
    
    # Extract just filename from profile_pic if it has a folder path
    if profile_pic and '/' in profile_pic:
        new_pic = profile_pic.split('/')[-1]
        db.execute_query('UPDATE students SET profile_pic = ? WHERE id = ?', (new_pic,))
        print(f"✅ Student {student_id}: profile_pic '{profile_pic}' → '{new_pic}'")
    
    # Extract just filename from resume if it has a folder path
    if resume and '/' in resume:
        new_resume = resume.split('/')[-1]
        db.execute_query('UPDATE students SET resume = ? WHERE id = ?', (new_resume,))
        print(f"✅ Student {student_id}: resume '{resume}' → '{new_resume}'")

print("\n✓ Database fixed - all file paths now store only filenames")
