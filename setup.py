#!/usr/bin/env python3
"""
Setup script for Restaurant Billing System
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    return run_command("pip install -r requirements.txt", "Installing requirements")

def create_directories():
    """Create necessary directories"""
    directories = ['database', 'static/images', 'static/css', 'static/js', 'templates', 'utils']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def download_bootstrap():
    """Download Bootstrap files if not present"""
    bootstrap_css = 'static/css/bootstrap.min.css'
    bootstrap_js = 'static/js/bootstrap.bundle.min.js'
    bootstrap_icons = 'static/css/bootstrap-icons.css'
    
    if os.path.exists(bootstrap_css) and os.path.exists(bootstrap_js) and os.path.exists(bootstrap_icons):
        print("✅ Bootstrap files already present")
        return True
    
    print("📦 Downloading Bootstrap files...")
    return run_command("python download_bootstrap.py", "Downloading Bootstrap files")

def main():
    """Main setup process"""
    print("🍽️  Restaurant Billing System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Download Bootstrap files
    print("\n📦 Setting up offline components...")
    download_bootstrap()
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then open your browser and go to:")
    print("   http://localhost:5000")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
