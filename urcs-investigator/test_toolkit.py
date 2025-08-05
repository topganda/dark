#!/usr/bin/env python3
"""
Simple test script for URCS Investigator Toolkit
Tests the basic structure and functionality without external dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from src.core.config import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from src.utils.logger import setup_logging
        print("✅ Logger utilities imported successfully")
        
        from src.utils.validator import validate_authorization
        print("✅ Authorization validator imported successfully")
        
        from src.utils.ioc_extractor import IOCExtractor
        print("✅ IOC extractor imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration management."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Test basic config structure
        assert "investigation" in config
        assert "detection" in config
        assert "monitoring" in config
        
        print("✅ Configuration loaded successfully")
        print(f"   Investigation scope: {config['investigation']['scope']}")
        print(f"   Detection thresholds: {config['detection']['thresholds']}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/analysis", 
        "src/detection",
        "src/forensics",
        "src/reporting",
        "src/utils",
        "config",
        "logs",
        "reports",
        "yara_rules",
        "scripts"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        else:
            print(f"✅ {directory}/ exists")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    return True

def test_files():
    """Test that all required files exist."""
    print("\n📄 Testing required files...")
    
    required_files = [
        "main.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/config.py",
        "src/core/investigator.py",
        "yara_rules/urcs_detection.yar"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def test_yara_rules():
    """Test YARA rules file."""
    print("\n🎯 Testing YARA rules...")
    
    try:
        with open("yara_rules/urcs_detection.yar", "r") as f:
            content = f.read()
            
        # Check for basic YARA rule structure
        assert "rule urcs_detection" in content
        assert "meta:" in content
        assert "strings:" in content
        assert "condition:" in content
        
        print("✅ YARA rules file is valid")
        return True
    except Exception as e:
        print(f"❌ YARA rules test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 URCS Investigator Toolkit - Structure Test")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_files),
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("YARA Rules", test_yara_rules)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Toolkit structure is correct.")
        print("\n📖 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run setup: python setup.py")
        print("3. Start investigating: python main.py investigate --target localhost")
    else:
        print("❌ Some tests failed. Please check the toolkit structure.")
        sys.exit(1)

if __name__ == "__main__":
    main()