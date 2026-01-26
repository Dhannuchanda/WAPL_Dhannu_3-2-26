from database import db

# Check all tables
tables = db.execute_query(
    "SELECT name FROM sqlite_master WHERE type='table'",
    fetch_all=True
)

print("Tables in database:")
for table in tables:
    print(f"  - {table['name']}")

# Check students table structure
print("\nStudents table structure:")
columns = db.execute_query(
    "PRAGMA table_info(students)",
    fetch_all=True
)
for col in columns:
    print(f"  {col['name']}: {col['type']}")

# Check actual student data
print("\nStudent 2 data:")
student = db.execute_query(
    "SELECT id, profile_pic, resume FROM students WHERE id = 2",
    fetch_one=True
)
if student:
    print(f"  ID: {student['id']}")
    print(f"  profile_pic: {student['profile_pic']}")
    print(f"  resume: {student['resume']}")
