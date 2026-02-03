import os
import time
from werkzeug.utils import secure_filename
from supabase import create_client, Client

class Storage:
    _supabase: Client = None
    _bucket_name = None
    
    @classmethod
    def _get_client(cls):
        """Initialize Supabase client if configured"""
        if cls._supabase is None:
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_KEY')
            if url and key:
                try:
                    cls._supabase = create_client(url, key)
                    cls._bucket_name = os.environ.get('SUPABASE_BUCKET', 'uploads')
                    print("✅ Supabase Storage initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Supabase: {e}")
        return cls._supabase

    @classmethod
    def save_file(cls, file_obj, subfolder=''):
        """
        Save a file to storage (Local or Supabase).
        Returns the relative path or URL to the file.
        """
        if not file_obj:
            return None
            
        filename = secure_filename(file_obj.filename)
        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        unique_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        
        # Check if Supabase is configured
        client = cls._get_client()
        
        if client:
            # === SUPABASE UPLOAD ===
            try:
                # Read file content
                file_content = file_obj.read()
                file_obj.seek(0) # Reset pointer
                
                path = f"{subfolder}/{unique_filename}" if subfolder else unique_filename
                
                # Upload to Supabase
                res = client.storage.from_(cls._bucket_name).upload(
                    path=path,
                    file=file_content,
                    file_options={"content-type": file_obj.content_type}
                )
                
                # Return public URL
                public_url = client.storage.from_(cls._bucket_name).get_public_url(path)
                return public_url
                
            except Exception as e:
                print(f"❌ Supabase upload failed: {e}. Falling back to local.")
                # Fallback to local storage below
        
        # === LOCAL UPLOAD (Fallback or Default) ===
        upload_base_path = './uploads'
        if os.environ.get('VERCEL') or os.environ.get('RENDER'):
             # Use /tmp for ephemeral storage on cloud if Supabase fails
            upload_base_path = '/tmp/uploads'
            
        target_dir = os.path.join(upload_base_path, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        
        save_path = os.path.join(target_dir, unique_filename)
        file_obj.save(save_path)
        
        # Return local path identifier (to be served by Flask route)
        return f"{subfolder}/{unique_filename}" if subfolder else unique_filename

    @classmethod
    def delete_file(cls, path_or_url):
        """Delete file from storage"""
        if not path_or_url:
            return
            
        client = cls._get_client()
        
        if client and "supabase.co" in path_or_url:
            try:
                # Extract path from URL
                # URL format: .../storage/v1/object/public/bucket/folder/file.ext
                # We need: folder/file.ext
                parsed_path = path_or_url.split(f"/public/{cls._bucket_name}/")[-1]
                client.storage.from_(cls._bucket_name).remove([parsed_path])
                print(f"🗑️ Deleted from Supabase: {parsed_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete from Supabase: {e}")
        else:
            # Local delete
            try:
                # path_or_url is likely "profile_pics/image.jpg"
                upload_base_path = './uploads'
                if os.environ.get('VERCEL') or os.environ.get('RENDER'):
                    upload_base_path = '/tmp/uploads'
                
                full_path = os.path.join(upload_base_path, path_or_url)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"🗑️ Deleted local file: {full_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete local file: {e}")

    @classmethod
    def upload_local_file(cls, local_path, subfolder=''):
        """Upload a file from local filesystem to storage"""
        if not os.path.exists(local_path):
            return None
            
        filename = os.path.basename(local_path)
        timestamp = int(time.time())
        unique_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        
        client = cls._get_client()
        
        if client:
            try:
                # Read file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                
                path = f"{subfolder}/{unique_filename}" if subfolder else unique_filename
                
                # Determine content type
                import mimetypes
                content_type = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
                
                # Upload to Supabase
                res = client.storage.from_(cls._bucket_name).upload(
                    path=path,
                    file=file_content,
                    file_options={"content-type": content_type}
                )
                
                # Return public URL
                public_url = client.storage.from_(cls._bucket_name).get_public_url(path)
                return public_url
                
            except Exception as e:
                print(f"❌ Supabase upload failed: {e}. Falling back to local.")
        
        # If local or fallback, just return the relative path (we assume it's already in the right place 
        # OR we might need to copy it if it was in temp? 
        # But for now, if we are local, the file is usually generated in the target dir directly.
        # But wait, issue_certificate generates it in 'uploads/certificates'.
        # Storage.upload_local_file suggests moving it?
        # No, for local usage, we just return the path relative to root.
        
        # Check if path starts with ./uploads or uploads
        normalized_path = local_path.replace('\\', '/')
        if 'uploads/' in normalized_path:
             path_parts = normalized_path.split('uploads/')
             return 'uploads/' + path_parts[1]
        return normalized_path
