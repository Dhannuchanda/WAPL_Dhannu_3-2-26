from database import db
import json

# Check the raw data
student = db.execute_query('SELECT * FROM students WHERE id = 1', fetch_one=True)
if student:
    print("Raw student data from DB:")
    print(json.dumps(dict(student), indent=2, default=str))
else:
    print("Student 1 not found")


