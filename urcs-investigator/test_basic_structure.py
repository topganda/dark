#!/usr/bin/env python3
"""
Basic Structure Test for URCS Investigator Toolkit
Tests the basic structure without requiring external dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test basic imports that don't require external dependencies."""
    print("🧪 Testing basic imports...")
    
    try:
        from src.core.config import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from src.utils.logger import setup_logging
        print("✅ Logger utilities imported successfully")
        
        from src.utils.validator import validate_authorization
        print("✅ Authorization validator imported successfully")
        
        from src.utils.ioc_extractor import IOCExtractor
        print("✅ IOC extractor imported successfully")
        
        from src.utils.tool_manager import ToolManager
        print("✅ ToolManager imported successfully")
        
        from src.utils.system_monitor import SystemMonitor
        print("✅ SystemMonitor imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Check required sections
        required_sections = ["investigation", "analysis", "detection", "monitoring", "tools"]
        for section in required_sections:
            if section in config:
                print(f"✅ Configuration section '{section}' found")
            else:
                print(f"❌ Configuration section '{section}' missing")
                return False
        
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and required files."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "config/investigation_config.json",
        "yara_rules/urcs_detection.yar",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/config.py",
        "src/core/investigator.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/validator.py",
        "src/utils/ioc_extractor.py",
        "src/utils/tool_manager.py",
        "src/utils/system_monitor.py",
        "src/analysis/__init__.py",
        "src/analysis/static_analyzer.py",
        "src/analysis/behavioral_analyzer.py",
        "src/analysis/memory_analyzer.py",
        "src/analysis/network_analyzer.py",
        "src/detection/__init__.py",
        "src/detection/yara_detector.py",
        "src/forensics/__init__.py",
        "src/forensics/registry_analyzer.py",
        "src/forensics/process_analyzer.py",
        "src/reporting/__init__.py",
        "src/reporting/report_generator.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {len(missing_files)}")
        return False
    
    return True

def test_directories():
    """Test required directories."""
    print("\n📂 Testing directories...")
    
    required_dirs = [
        "logs",
        "reports", 
        "config",
        "yara_rules",
        "tools",
        "src",
        "src/core",
        "src/analysis",
        "src/detection",
        "src/forensics",
        "src/reporting",
        "src/utils"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️ Missing directories: {len(missing_dirs)}")
        return False
    
    return True

def test_yara_rules():
    """Test YARA rules file."""
    print("\n🎯 Testing YARA rules...")
    
    try:
        yara_file = "yara_rules/urcs_detection.yar"
        if os.path.exists(yara_file):
            with open(yara_file, 'r') as f:
                content = f.read()
            
            # Check for required rule components
            if "rule urcs_detection" in content:
                print("✅ URCS detection rule found")
            else:
                print("❌ URCS detection rule missing")
                return False
            
            if "gulf.moneroocean.stream" in content:
                print("✅ Mining pool indicators found")
            else:
                print("❌ Mining pool indicators missing")
                return False
            
            print("✅ YARA rules file is valid")
            return True
        else:
            print("❌ YARA rules file not found")
            return False
            
    except Exception as e:
        print(f"❌ YARA rules test failed: {e}")
        return False

def test_cli_structure():
    """Test CLI command structure without running commands."""
    print("\n💻 Testing CLI structure...")
    
    try:
        # Check if main.py exists and has the right structure
        with open("main.py", 'r') as f:
            content = f.read()
        
        # Check for required commands
        required_commands = ["investigate", "static", "behavioral", "memory", "network", "report", "setup", "monitor"]
        for cmd in required_commands:
            if f"'{cmd}'" in content or f'"{cmd}"' in content:
                print(f"✅ Command '{cmd}' found in main.py")
            else:
                print(f"❌ Command '{cmd}' missing from main.py")
                return False
        
        print("✅ CLI structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ CLI structure test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 URCS Investigator Toolkit - Basic Structure Test")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_configuration),
        ("File Structure", test_file_structure),
        ("Directories", test_directories),
        ("YARA Rules", test_yara_rules),
        ("CLI Structure", test_cli_structure)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 BASIC STRUCTURE TESTS PASSED!")
        print("\n📖 The toolkit structure is complete and ready.")
        print("\n⚠️ Note: Some features require external dependencies:")
        print("   - YARA Python module (yara-python)")
        print("   - External tools (CAPEv2, Sysmon, Zeek, etc.)")
        print("\n📋 To install dependencies:")
        print("   1. Run: python3 setup.py")
        print("   2. Run: python3 main.py setup --install-tools")
        print("   3. Run: python3 main.py investigate --target localhost")
        return True
    else:
        print("⚠️ Some basic structure tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)