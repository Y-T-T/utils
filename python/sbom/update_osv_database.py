import os
import urllib.request
import urllib.parse
import hashlib
from pathlib import Path

def get_remote_hash(url):
    """
    Sends a HEAD request to fetch the remote file's MD5 hash from the 
    'x-goog-hash' header. Google Cloud Storage returns this as Base64.
    If the 'x-goog-hash' header is not available, it falls back to using the ETag header.
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            x_goog_hash = response.headers.get('x-goog-hash')
            if x_goog_hash:
                # The header format is usually: "crc32c=..., md5=..."
                parts = x_goog_hash.split(',')
                for part in parts:
                    part = part.strip()
                    if part.startswith('md5='):
                        return "md5", part[4:] # Return the Base64 MD5 string
                    
            etag = response.headers.get('ETag')
            if etag:
                return "etag", etag.strip('"') # Remove quotes from ETag if present
    except Exception as e:
        print(f"Error fetching headers for {url}: {e}")
    return None, None

def get_local_md5(file_path, format="hex"):
    """
    Calculates the MD5 hash of a local file and returns it as a Base64 string
    to match the format provided by Google Cloud Storage.
    """
    if not Path(file_path).exists():
        return None
        
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read the file in chunks to avoid memory issues with large files
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            
    if format == "base64":
        import base64
        return base64.b64encode(hash_md5.digest()).decode('utf-8')
    
    return hash_md5.hexdigest()

def download_osv_offline_database():
    """
    Downloads OSV databases directly into the OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY
    maintaining the exact directory structure required by OSV-Scanner.
    """
    # 1. Get the cache directory from environment variables
    cache_dir = os.environ.get("OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY")
    
    if not cache_dir:
        print("""Error: OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY environment variable is not set.
              Please set it to the desired cache directory path and run the script again.
                Example:
                In Windows PowerShell:
                  $env:OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY = \"$HOME\\.osv_offine_db\"
                In Linux/macOS:
                  export OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=\"$HOME/.osv_offine_db\"""")
        return
    else:
        cache_dir = Path(cache_dir) # Convert to Path object
        
    base_url = "https://storage.googleapis.com/osv-vulnerabilities"
    ecosystems_url = f"{base_url}/ecosystems.txt"
    cache_dir = cache_dir / "osv-scanner" # The expected structure is <cache_dir>/osv-scanner/<ecosystem>/all.zip

    print(f"Target Cache Directory: {cache_dir}")
    print("Checking for updates...\n")
    
    try:
        with urllib.request.urlopen(ecosystems_url) as response:
            ecosystems = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error fetching ecosystems.txt: {e}")
        return

    downloaded_count = 0
    skipped_count = 0

    for eco in ecosystems:
        eco = eco.strip()
        if not eco:
            continue
            
        eco_encoded = urllib.parse.quote(eco)
        zip_url = f"{base_url}/{eco_encoded}/all.zip"
        eco_dir = cache_dir / eco
        eco_dir.mkdir(parents=True, exist_ok=True)
            
        dest_file = eco_dir / "all.zip"
        
        hash_type, remote_hash = get_remote_hash(zip_url)

        local_hash = get_local_md5(dest_file, format="base64" if hash_type == "md5" else "hex")

        if remote_hash and local_hash and remote_hash == local_hash:
            print(f"[SKIP] {eco} is up-to-date.")
            skipped_count += 1
            continue
            
        print(f"[DOWNLOADING] {eco} -> {dest_file}")
        
        try:
            # Download the file if hashes don't match or file is missing
            urllib.request.urlretrieve(zip_url, dest_file)
            downloaded_count += 1
            
        except Exception as e:
            print(f"Failed to download database for {eco}: {e}")

    print("-" * 30)
    print(f"Update complete: {downloaded_count} downloaded, {skipped_count} skipped.")

    print("\nOffline database update complete. Ready for OSV-Scanner offline mode.")

if __name__ == "__main__":
    download_osv_offline_database()