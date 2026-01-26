from database import db

# Check what's in the database - is there a student 2?
all_students = db.execute_query(
    'SELECT id, user_id, full_name, profile_pic, resume FROM students',
    fetch_all=True
)

print("All students:")
for s in all_students:
    print(f"  ID {s['id']}: {s['full_name']} (user_id {s['user_id']})")
    print(f"    profile_pic: {s['profile_pic']}")
    print(f"    resume: {s['resume']}")
    print()

# Check users table too
all_users = db.execute_query(
    'SELECT id, email, role FROM users ORDER BY id',
    fetch_all=True
)

print("\nAll users:")
for u in all_users:
    print(f"  ID {u['id']}: {u['email']} ({u['role']})")
