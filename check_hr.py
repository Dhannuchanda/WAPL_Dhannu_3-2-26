import sqlite3

conn = sqlite3.connect('wapl.db')
cursor = conn.cursor()
cursor.execute('SELECT u.email, h.full_name, h.company_name FROM users u JOIN hrs h ON u.id = h.user_id WHERE u.role = "hr"')
hrs = cursor.fetchall()
print('HR Accounts:')
for hr in hrs:
    print(f'Email: {hr[0]}, Name: {hr[1]}, Company: {hr[2]}')
conn.close()