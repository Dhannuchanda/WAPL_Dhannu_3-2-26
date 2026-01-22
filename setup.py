"""
Setup script for WAPL application
Run this script to initialize the database and create necessary directories
"""

import os
from database import init_db

def setup():
    print("Setting up WAPL application...")
    
    # Create upload directories
    directories = [
        'uploads/profile_pics',
        'uploads/resumes',
        'uploads/certificates',
        'uploads/qr_codes'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    
    print("\nSetup complete!")
    print("\nDefault admin credentials:")
    print("Email: admin@wapl.com")
    print("Password: admin123")
    print("\nPlease change the admin password after first login!")

if __name__ == '__main__':
    setup()
