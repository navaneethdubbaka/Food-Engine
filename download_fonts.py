#!/usr/bin/env python3
"""
Download Bootstrap Icons font files for offline use
"""

import os
import urllib.request
from pathlib import Path

def download_file(url, filepath):
    """Download a file from URL"""
    try:
        print(f"Downloading {url}...")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Downloaded {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def main():
    """Download Bootstrap Icons font files"""
    print("📦 Downloading Bootstrap Icons font files...")
    
    # Create fonts directory
    os.makedirs('static/css/fonts', exist_ok=True)
    
    # Bootstrap Icons font files
    files_to_download = [
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.woff2',
            'path': 'static/css/fonts/bootstrap-icons.woff2'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.woff',
            'path': 'static/css/fonts/bootstrap-icons.woff'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.ttf',
            'path': 'static/css/fonts/bootstrap-icons.ttf'
        }
    ]
    
    success_count = 0
    for file_info in files_to_download:
        if download_file(file_info['url'], file_info['path']):
            success_count += 1
    
    print(f"\n🎉 Downloaded {success_count}/{len(files_to_download)} font files successfully!")
    
    if success_count == len(files_to_download):
        print("✅ All Bootstrap Icons font files downloaded successfully!")
    else:
        print("⚠️  Some font files failed to download. Icons may not display properly.")

if __name__ == "__main__":
    main()

