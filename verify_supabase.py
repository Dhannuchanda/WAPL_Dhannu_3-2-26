import os
from dotenv import load_dotenv
from storage import Storage
import time

# Load environment variables
load_dotenv()

print("Checking Supabase Configuration...")
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
bucket = os.environ.get('SUPABASE_BUCKET')

print(f"URL: {url}")
print(f"Key: {'*' * 10 if key else 'None'}")
print(f"Bucket: {bucket}")

if not url or not key:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

print("\nTesting Storage Connection...")
try:
    # Initialize client (Storage class does this lazily)
    client = Storage._get_client()
    if not client:
        print("❌ Failed to initialize Supabase client (Check URL/Key)")
        exit(1)
        
    print("✅ Client initialized")
    
    # Try to list buckets (if possible) or just do an upload test
    print("Attempting to upload test file...")
    
    # Create a dummy file object mock
    class MockFile:
        def __init__(self, content, filename):
            self.content = content
            self.filename = filename
            self.content_type = 'text/plain'
            self._pos = 0
            
        def read(self):
            return self.content
            
        def seek(self, pos):
            self._pos = pos
            
        def save(self, path):
            print(f"Simulating local save to {path}")

    mock_file = MockFile(b"Hello Supabase!", "test_connection.txt")
    
    # Upload
    url = Storage.save_file(mock_file, subfolder="test")
    
    if url and "supabase.co" in url:
        print(f"✅ Upload successful!")
        print(f"URL: {url}")
        
        # Clean up
        print("Cleaning up...")
        Storage.delete_file(url)
        print("✅ Cleanup successful")
        print("\n🎉 Supabase Storage is CONNECTED and WORKING!")
    else:
        print(f"⚠️ Upload returned: {url}")
        print("❌ It seems to be falling back to local storage. Check credentials.")

except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
