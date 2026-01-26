from database import db

# Check what the database has
student = db.execute_query('SELECT id, profile_pic, resume FROM students WHERE id = 1', fetch_one=True)
print("Database contains:")
print(f"  profile_pic: {repr(student['profile_pic'])}")
print(f"  resume: {repr(student['resume'])}")

# Check if the fix script was run
if student['profile_pic'] and '/' in student['profile_pic']:
    print("\n⚠️  Database still has folder paths! Running fix now...")
    # Run the fix
    import os
    if student['profile_pic'] and '/' in student['profile_pic']:
        new_pic = student['profile_pic'].split('/')[-1]
        db.execute_query('UPDATE students SET profile_pic = ? WHERE id = 1', (new_pic,))
        print(f"✅ Fixed profile_pic: {repr(new_pic)}")
    
    if student['resume'] and '/' in student['resume']:
        new_resume = student['resume'].split('/')[-1]
        db.execute_query('UPDATE students SET resume = ? WHERE id = 1', (new_resume,))
        print(f"✅ Fixed resume: {repr(new_resume)}")
else:
    print("\n✓ Database has clean filenames - no fix needed")
