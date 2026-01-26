import json
from database import db

# Get student 1
student = db.execute_query("""
    SELECT 
        s.id,
        s.user_id,
        s.wapl_id,
        s.full_name,
        s.phone,
        s.profile_pic,
        s.resume,
        s.domain_id,
        s.registration_date,
        s.certificate_issued_date,
        s.certificate_expiry_date,
        s.assigned_hr_id,
        s.address,
        s.education_details,
        s.skills,
        s.projects,
        s.account_status,
        u.email,
        h.full_name as assigned_hr_name,
        h.company_name as hr_company,
        h.id as assigned_hr_id,
        GROUP_CONCAT(d.domain_name, ', ') as domain_names
    FROM students s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN hrs h ON s.assigned_hr_id = h.id
    LEFT JOIN student_domains sd ON s.id = sd.student_id
    LEFT JOIN domains d ON sd.domain_id = d.id
    WHERE s.id = 1
    GROUP BY s.id
""", fetch_one=True)

if student:
    print("Student 1 API Response:")
    print(json.dumps(dict(student), indent=2, default=str))
    print(f"\nprofile_pic value: {student['profile_pic']}")
    print(f"Type: {type(student['profile_pic'])}")
    
    # Test the JavaScript logic
    profile_pic_value = student['profile_pic']
    profile_name = profile_pic_value.split('/').pop() if profile_pic_value else None
    constructed_url = f"/uploads/profile_pics/{profile_name}" if profile_name else None
    
    print(f"\nJavaScript simulation:")
    print(f"  student.profile_pic: {profile_pic_value}")
    print(f"  .split('/')': {profile_pic_value.split('/')}")
    print(f"  .pop(): {profile_name}")
    print(f"  Final URL: {constructed_url}")
else:
    print("Student not found")
