#!/usr/bin/env python3
"""
Setup script for URCS Investigator Toolkit
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main setup function"""
    print("🔍 URCS Investigator Toolkit - Setup")
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
    directories = [
        "logs",
        "reports", 
        "config",
        "yara_rules",
        "templates",
        "tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    # Create default configuration
    print("\n⚙️ Creating default configuration...")
    try:
        from src.core.config import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.create_default_config()
        print("✅ Default configuration created")
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        sys.exit(1)
    
    # Setup logging
    print("\n📋 Setting up logging...")
    try:
        from src.utils.logger import setup_logging
        setup_logging()
        print("✅ Logging system configured")
    except Exception as e:
        print(f"❌ Failed to setup logging: {e}")
    
    # Create authorization file for development
    print("\n🔐 Creating development authorization...")
    try:
        from src.utils.validator import create_authorization_file
        if create_authorization_file():
            print("✅ Development authorization created")
        else:
            print("⚠️ Could not create authorization file")
    except Exception as e:
        print(f"❌ Failed to create authorization: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Review configuration in config/investigation_config.json")
    print("2. Add custom YARA rules to yara_rules/ directory")
    print("3. Run: python main.py investigate --target localhost")
    print("4. Check logs/ directory for investigation logs")
    print("5. View reports in reports/ directory")
    
    print("\n⚠️ Important:")
    print("- This toolkit is for defensive analysis only")
    print("- Always obtain proper authorization before investigations")
    print("- Follow your organization's security policies")
    print("- Keep investigation results secure and confidential")


if __name__ == "__main__":
    main()