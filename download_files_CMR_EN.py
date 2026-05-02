#!/usr/bin/env python3
import os
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# Core settings constants
# ==========================================
CMR_BASE_URL = "https://cmr.earthdata.nasa.gov"
MAX_WORKERS = 5  # Number of concurrent downloads

# ==========================================
# Helper functions
# ==========================================
def setup_auth(cred_file_path):
    """Read username and password from text file and configure NASA authentication file"""
    if not os.path.exists(cred_file_path):
        raise FileNotFoundError(f"Password file not found: {cred_file_path}. Please check the path!")

    with open(cred_file_path, 'r') as f:
        lines = f.read().splitlines()
        if len(lines) < 2:
            raise ValueError("Invalid password file format. First line should be username, second line password.")
        username, password = lines[0].strip(), lines[1].strip()

    netrc_path = os.path.expanduser('~/.netrc')
    with open(netrc_path, 'w') as f:
        f.write(f'machine urs.earthdata.nasa.gov login {username} password {password}\n')
    os.chmod(netrc_path, 0o600)
    print("✅ NASA authentication configured (read from file).")

def query_cmr_granules(short_name, version, page_size=2000, search_after=None, **extra_params):
    """Query CMR API to get file list"""
    url = f"{CMR_BASE_URL}/search/granules.umm_json"
    params = {"short_name": short_name, "version": version, "page_size": page_size, **extra_params}
    headers = {"Accept": "application/json"}
    if search_after:
        headers["CMR-Search-After"] = search_after

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response, response.json().get("items", [])

def download_file(url, output_dir):
    """Single file download logic"""
    local_filename = os.path.join(output_dir, os.path.basename(url))
    if os.path.exists(local_filename):
        return "skipped", os.path.basename(url)
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        return "success", os.path.basename(url)
    except Exception as e:
        return "failed", os.path.basename(url)

# ==========================================
# Core reusable main function
# ==========================================
def batch_download_cmr_data(short_name, version, temporal_range, bounding_box, output_dir):
    """
    General download controller function

    Parameters:
    - short_name: Satellite data short name (e.g., 'OCO2_L2_Lite_FP' or 'OCO3_L2_Lite_FP')
    - version: Data version (e.g., '11.2r' or '10.4r')
    - temporal_range: Time range (e.g., '2025-04-01,2025-04-30')
    - bounding_box: Spatial bounding box (e.g., '-13.58,35.62,45.83,71.22')
    - output_dir: Local/cloud path to save downloads
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n🚀 Starting task: {short_name} v{version}")
    print(f"📅 Time range: {temporal_range} | 🌍 Bounding box: {bounding_box}")
    print(f"💾 Save path: {output_dir}")

    filter_params = {"temporal": temporal_range, "bounding_box": bounding_box}

    # 1. Collect download links
    search_after_value = None
    all_download_urls = []

    print("🔍 Requesting file list from NASA server...")
    while True:
        response, items = query_cmr_granules(short_name, version, search_after=search_after_value, **filter_params)
        for item in items:
            for related_url in item.get("umm", {}).get("RelatedUrls", []):
                if related_url.get("Type") == "GET DATA":
                    all_download_urls.append(related_url.get("URL"))

        search_after_value = response.headers.get("CMR-Search-After")
        if not search_after_value:
            break

    total_files = len(all_download_urls)
    print(f"🎯 Found {total_files} files to download.")
    if total_files == 0:
        return

    # 2. Multi-threaded concurrent download
    downloaded_count, skipped_count, failed_count = 0, 0, 0
    with tqdm(total=total_files, desc="⬇️ Download progress", unit="file") as pbar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(download_file, url, output_dir): url for url in all_download_urls}
            for future in as_completed(future_to_url):
                status, filename = future.result()
                if status == "success": downloaded_count += 1
                elif status == "skipped": skipped_count += 1
                else: failed_count += 1
                pbar.update(1)

    print(f"✅ Task completed: {downloaded_count} succeeded, {skipped_count} skipped, {failed_count} failed\n")

# ==========================================
# Your usage entry (call here)
# ==========================================
if __name__ == "__main__":

    # 1. Configure authentication (point to the password file you just created)
    CRED_FILE = '/earthdata_credentials.txt'
    setup_auth(CRED_FILE)

    # ==========================
    # Task 1: Download OCO-2 data for August
    # ==========================
    batch_download_cmr_data(
        short_name='OCO3_L2_Lite_FP',
        version='11r',
        temporal_range='2025-04-01,2025-04-30',
        bounding_box='-13.58,35.62,45.83,71.22',
        output_dir='/Met_Data/OCO3_Data'
    )

    # ==========================
    # Additional demo: download OCO-3 data
    # ==========================
    """
    batch_download_cmr_data(
        short_name='OCO2_L2_Lite_FP',
        version='11.2r',
        temporal_range='2025-04-01,2025-04-30',
        bounding_box='-13.58,35.62,45.83,71.22',
        output_dir='/Met_Data/OCO2_Data'
    )
    """
