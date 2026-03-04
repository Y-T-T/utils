import os
import urllib.request
import urllib.parse

def get_remote_etag(url):
    """
    Sends an HTTP HEAD request to fetch the ETag (hash) of the remote file 
    without downloading the actual file content.
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            return response.headers.get('ETag')
    except Exception as e:
        print(f"Error fetching headers for {url}: {e}")
        return None

def download_osv_offline_database():
    """
    Downloads OSV databases directly into the OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY
    maintaining the exact directory structure required by OSV-Scanner.
    """
    # 1. Get the cache directory from environment variables
    cache_dir = os.environ.get("OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY")
    
    if not cache_dir:
        print("Warning: OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY environment variable is not set.")
        print("Defaulting to './osv_offline_db'.")
        print("Please ensure you export this same path before running osv-scanner.")
        cache_dir = "./osv_offline_db"
        
    base_url = "https://storage.googleapis.com/osv-vulnerabilities"
    ecosystems_url = f"{base_url}/ecosystems.txt"
    
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
        eco_dir = os.path.join(cache_dir, eco)
        
        if not os.path.exists(eco_dir):
            os.makedirs(eco_dir)
            
        dest_file = os.path.join(eco_dir, "all.zip")
        etag_file = os.path.join(eco_dir, "all.zip.etag")
        
        # Get the remote hash (ETag) via HEAD request
        remote_etag = get_remote_etag(zip_url)
        
        # Check the local hash (ETag) if the zip file exists
        local_etag = None
        if os.path.exists(dest_file) and os.path.exists(etag_file):
            with open(etag_file, 'r') as f:
                local_etag = f.read().strip()

        # Compare hashes
        if remote_etag and local_etag == remote_etag:
            print(f"[SKIP] {eco} is up-to-date.")
            skipped_count += 1
            continue
            
        print(f"[DOWNLOADING] {eco} -> {dest_file}")
        
        try:
            # Download the file if hashes don't match or file is missing
            urllib.request.urlretrieve(zip_url, dest_file)
            
            # Save the new hash to the local etag file
            if remote_etag:
                with open(etag_file, 'w') as f:
                    f.write(remote_etag)
            downloaded_count += 1
            
        except Exception as e:
            print(f"Failed to download database for {eco}: {e}")

    print("-" * 30)
    print(f"Update complete: {downloaded_count} downloaded, {skipped_count} skipped.")

    print("\nOffline database update complete. Ready for OSV-Scanner offline mode.")

if __name__ == "__main__":
    download_osv_offline_database()