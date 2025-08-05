#!/usr/bin/env python3
"""
Complete Toolkit Test Script for URCS Investigator Toolkit
Tests all components and functionality to ensure everything is working.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from src.core.config import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from src.core.investigator import URCSInvestigator
        print("✅ URCSInvestigator imported successfully")
        
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
        
        from src.analysis.static_analyzer import StaticAnalyzer
        print("✅ StaticAnalyzer imported successfully")
        
        from src.analysis.behavioral_analyzer import BehavioralAnalyzer
        print("✅ BehavioralAnalyzer imported successfully")
        
        from src.analysis.memory_analyzer import MemoryAnalyzer
        print("✅ MemoryAnalyzer imported successfully")
        
        from src.analysis.network_analyzer import NetworkAnalyzer
        print("✅ NetworkAnalyzer imported successfully")
        
        from src.detection.yara_detector import YARADetector
        print("✅ YARADetector imported successfully")
        
        from src.forensics.registry_analyzer import RegistryAnalyzer
        print("✅ RegistryAnalyzer imported successfully")
        
        from src.forensics.process_analyzer import ProcessAnalyzer
        print("✅ ProcessAnalyzer imported successfully")
        
        from src.reporting.report_generator import ReportGenerator
        print("✅ ReportGenerator imported successfully")
        
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

def test_tool_manager():
    """Test tool manager functionality."""
    print("\n🔧 Testing tool manager...")
    
    try:
        from src.core.config import ConfigManager
        from src.utils.tool_manager import ToolManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        tool_manager = ToolManager(config)
        
        # Test tool status
        status = tool_manager.get_installation_status()
        print(f"✅ Tool status retrieved: {len(status)} tools configured")
        
        # Test tool path resolution
        for tool_name in ["tcpdump", "binwalk"]:
            path = tool_manager.get_tool_path(tool_name)
            if path:
                print(f"✅ {tool_name} found at: {path}")
            else:
                print(f"⚠️ {tool_name} not found (may need installation)")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool manager test failed: {e}")
        return False

def test_system_monitor():
    """Test system monitor functionality."""
    print("\n🔍 Testing system monitor...")
    
    try:
        from src.core.config import ConfigManager
        from src.utils.system_monitor import SystemMonitor
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        system_monitor = SystemMonitor(config)
        
        # Test monitoring status
        status = system_monitor.get_monitoring_status()
        print(f"✅ Monitoring status retrieved: {status['monitoring']}")
        
        # Test configuration generation
        powershell_result = system_monitor.enable_powershell_logging()
        etw_result = system_monitor.enable_etw_tracing()
        
        print(f"✅ PowerShell logging config: {'✅' if powershell_result else '❌'}")
        print(f"✅ ETW tracing config: {'✅' if etw_result else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ System monitor test failed: {e}")
        return False

def test_investigator():
    """Test investigator functionality."""
    print("\n🔬 Testing investigator...")
    
    try:
        from src.core.config import ConfigManager
        from src.core.investigator import URCSInvestigator
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        investigator = URCSInvestigator(config)
        print("✅ Investigator initialized successfully")
        
        # Test method availability
        methods = [
            "investigate", "static_analysis", "behavioral_analysis", 
            "memory_analysis", "memory_forensics", "network_analysis",
            "generate_report", "export_iocs", "setup_environment"
        ]
        
        for method in methods:
            if hasattr(investigator, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Investigator test failed: {e}")
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

def test_cli_commands():
    """Test CLI command structure."""
    print("\n💻 Testing CLI commands...")
    
    try:
        import subprocess
        
        # Test help command
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI help command works")
            
            # Check for required commands
            required_commands = ["investigate", "static", "behavioral", "memory", "network", "report", "setup", "monitor"]
            for cmd in required_commands:
                if cmd in result.stdout:
                    print(f"✅ Command '{cmd}' found in help")
                else:
                    print(f"❌ Command '{cmd}' missing from help")
                    return False
            
            return True
        else:
            print("❌ CLI help command failed")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 URCS Investigator Toolkit - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Tool Manager", test_tool_manager),
        ("System Monitor", test_system_monitor),
        ("Investigator", test_investigator),
        ("File Structure", test_file_structure),
        ("Directories", test_directories),
        ("YARA Rules", test_yara_rules),
        ("CLI Commands", test_cli_commands)
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
        print("🎉 ALL TESTS PASSED! Toolkit is ready for use.")
        print("\n📖 Next steps:")
        print("1. Run: python main.py setup --all")
        print("2. Run: python main.py investigate --target localhost")
        print("3. Run: python main.py monitor --start")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)