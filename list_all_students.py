from database import db

students = db.execute_query(
    'SELECT id, profile_pic, resume FROM students',
    fetch_all=True
)

print("All students in database:")
for s in students:
    print(f"Student {s['id']}: pic={s['profile_pic']}, resume={s['resume']}")
