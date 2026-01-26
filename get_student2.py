from database import db

# Get student 2 data if it exists
student = db.execute_query(
    'SELECT id, full_name, profile_pic, resume FROM students WHERE id = 2',
    fetch_one=True
)

if student:
    print(f"Student 2 found:")
    print(f"  Name: {student['full_name']}")
    print(f"  Profile pic: {student['profile_pic']}")
    print(f"  Resume: {student['resume']}")
else:
    print("Student 2 not found")

# Check all students
print("\nAll students:")
all_students = db.execute_query(
    'SELECT id, full_name, profile_pic, resume FROM students',
    fetch_all=True
)
for s in all_students:
    print(f"  {s['id']}: {s['full_name']}")
    print(f"      pic={s['profile_pic']}")
    print(f"      resume={s['resume']}")
