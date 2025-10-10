#!/usr/bin/env python3
"""
Download Bootstrap 5 files for offline use
"""

import os
import urllib.request
from pathlib import Path

def download_file(url, filepath):
    """Download a file from URL"""
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Downloaded {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def main():
    """Download Bootstrap 5 files"""
    print("📦 Downloading Bootstrap 5 files for offline use...")
    
    # Create directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Bootstrap 5.3.2 files
    files_to_download = [
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
            'path': 'static/css/bootstrap.min.css'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
            'path': 'static/js/bootstrap.bundle.min.js'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
            'path': 'static/css/bootstrap-icons.css'
        }
    ]
    
    success_count = 0
    for file_info in files_to_download:
        if download_file(file_info['url'], file_info['path']):
            success_count += 1
    
    print(f"\n🎉 Downloaded {success_count}/{len(files_to_download)} files successfully!")
    
    if success_count == len(files_to_download):
        print("✅ All Bootstrap files downloaded successfully!")
        print("🚀 You can now run the application offline!")
    else:
        print("⚠️  Some files failed to download. You may need to download them manually.")

if __name__ == "__main__":
    main()
