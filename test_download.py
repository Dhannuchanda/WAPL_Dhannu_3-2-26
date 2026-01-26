import requests
import os

# Test the download endpoint
filename = 'resumes/1_20260125231810_DHANUSH CHANDA.pdf'
url = f'http://localhost:5000/download/{filename}'

print(f'Testing: {url}')

# Check if file exists locally first
local_file = f'uploads/resumes/1_20260125231810_DHANUSH CHANDA.pdf'
if os.path.exists(local_file):
    print(f'Local file exists: {local_file}')
    print(f'File size: {os.path.getsize(local_file)} bytes')

try:
    response = requests.head(url, timeout=5, allow_redirects=True)
    print(f'Status: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')
    print(f'Content-Disposition: {response.headers.get("Content-Disposition")}')
except Exception as e:
    print(f'Error: {e}')
