#!/usr/bin/env python3
"""
Setup script for Advanced Crypto Mining Suite
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main setup function"""
    print("🚀 Advanced Crypto Mining Suite - Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = ["logs", "config", "miners"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    # Create default configuration
    print("\n⚙️ Creating default configuration...")
    try:
        from src.utils.config import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.create_default_config()
        print("✅ Default configuration created")
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        sys.exit(1)
    
    # Set up logging
    print("\n📋 Setting up logging...")
    try:
        from src.utils.logger import setup_logging
        setup_logging()
        print("✅ Logging system configured")
    except Exception as e:
        print(f"❌ Failed to setup logging: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the setup wizard: python main.py setup")
    print("2. Start mining: python main.py run")
    print("3. Access dashboard: python main.py dashboard")
    print("4. View help: python main.py --help")

if __name__ == "__main__":
    main()