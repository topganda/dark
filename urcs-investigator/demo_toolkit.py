#!/usr/bin/env python3
"""
URCS Investigator Toolkit - Comprehensive Demonstration
Shows all features and capabilities of the toolkit.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_banner():
    """Print toolkit banner."""
    print("=" * 80)
    print("🔍 URCS INVESTIGATOR TOOLKIT - COMPREHENSIVE DEMONSTRATION")
    print("=" * 80)
    print("🎯 Purpose: Defensive analysis and detection of unauthorized resource-consuming software")
    print("🛡️  Legal: This toolkit is for defensive analysis and threat intelligence only")
    print("📋 Features: Real-time monitoring, behavioral analysis, memory forensics, network analysis")
    print("=" * 80)

def demo_basic_functionality():
    """Demonstrate basic toolkit functionality."""
    print("\n🚀 DEMO 1: Basic Functionality")
    print("-" * 40)
    
    try:
        from src.core.config import ConfigManager
        from src.utils.platform_utils import PlatformUtils
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✅ Configuration loaded successfully")
        
        # Get system information
        platform_utils = PlatformUtils()
        system_info = platform_utils.get_system_info()
        print(f"✅ System detected: {system_info['platform']} ({system_info['architecture']})")
        
        # Get running processes
        processes = platform_utils.get_process_list()
        print(f"✅ Found {len(processes)} running processes")
        
        # Get network connections
        connections = platform_utils.get_network_connections()
        print(f"✅ Found {len(connections)} network connections")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality demo failed: {e}")
        return False

def demo_investigation():
    """Demonstrate investigation capabilities."""
    print("\n🔍 DEMO 2: Investigation Capabilities")
    print("-" * 40)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("✅ Investigator initialized")
        
        # Run basic investigation
        print("🔍 Running basic investigation...")
        results = investigator.investigate(target="localhost", scope="basic")
        
        print(f"✅ Investigation completed:")
        print(f"   - Findings: {len(results.get('findings', []))}")
        print(f"   - IOCs: {len(results.get('iocs', []))}")
        print(f"   - Behaviors detected: {len(results.get('behaviors_detected', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Investigation demo failed: {e}")
        return False

def demo_static_analysis():
    """Demonstrate static analysis."""
    print("\n📄 DEMO 3: Static Analysis")
    print("-" * 40)
    
    try:
        # Create a test file for analysis
        test_file = "demo_test_file.bin"
        with open(test_file, 'wb') as f:
            # Create some test data with mixed entropy
            f.write(b'\x00' * 1000)  # Low entropy
            f.write(b'\xFF' * 1000)  # High entropy
            f.write(b'URCS_TEST_PATTERN' * 10)  # Test pattern
        
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print(f"🔍 Analyzing test file: {test_file}")
        results = investigator.static_analysis(
            file_path=test_file,
            entropy=True,
            signature=True,
            yara=True
        )
        
        print(f"✅ Static analysis completed:")
        print(f"   - File size: {os.path.getsize(test_file)} bytes")
        print(f"   - YARA matches: {len(results.get('yara_matches', []))}")
        
        # Clean up
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Static analysis demo failed: {e}")
        return False

def demo_behavioral_analysis():
    """Demonstrate behavioral analysis."""
    print("\n🔍 DEMO 4: Behavioral Analysis")
    print("-" * 40)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("🔍 Running behavioral analysis...")
        results = investigator.behavioral_analysis(
            system=True,
            registry=True,
            services=True,
            tasks=True
        )
        
        print(f"✅ Behavioral analysis completed:")
        print(f"   - Registry findings: {len(results.get('registry_findings', []))}")
        print(f"   - Service findings: {len(results.get('service_findings', []))}")
        print(f"   - Task findings: {len(results.get('task_findings', []))}")
        print(f"   - File system findings: {len(results.get('file_system_findings', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Behavioral analysis demo failed: {e}")
        return False

def demo_network_analysis():
    """Demonstrate network analysis."""
    print("\n🌐 DEMO 5: Network Analysis")
    print("-" * 40)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("🌐 Running network analysis...")
        results = investigator.network_analysis(
            interface="lo",  # Loopback interface
            capture_live=False
        )
        
        print(f"✅ Network analysis completed:")
        print(f"   - Connections analyzed: {len(results.get('connections', []))}")
        print(f"   - Suspicious traffic: {len(results.get('suspicious_traffic', []))}")
        print(f"   - Network IOCs: {len(results.get('network_iocs', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Network analysis demo failed: {e}")
        return False

def demo_memory_forensics():
    """Demonstrate memory forensics."""
    print("\n🧠 DEMO 6: Memory Forensics")
    print("-" * 40)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("🧠 Running memory forensics...")
        results = investigator.memory_forensics()
        
        print(f"✅ Memory forensics completed:")
        print(f"   - Injection findings: {len(results.get('injection_findings', []))}")
        print(f"   - Memory regions analyzed: {len(results.get('memory_regions', []))}")
        print(f"   - DLL findings: {len(results.get('dll_findings', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory forensics demo failed: {e}")
        return False

def demo_system_monitoring():
    """Demonstrate system monitoring."""
    print("\n📊 DEMO 7: System Monitoring")
    print("-" * 40)
    
    try:
        from src.utils.system_monitor import SystemMonitor
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        system_monitor = SystemMonitor(config)
        
        print("📊 Testing system monitoring capabilities...")
        
        # Get monitoring status
        status = system_monitor.get_monitoring_status()
        print(f"✅ Monitoring status: {'Active' if status['monitoring'] else 'Inactive'}")
        
        # Test configuration generation
        powershell_result = system_monitor.enable_powershell_logging()
        etw_result = system_monitor.enable_etw_tracing()
        
        print(f"✅ Configuration tests:")
        print(f"   - PowerShell logging: {'✅' if powershell_result else '❌'}")
        print(f"   - ETW tracing: {'✅' if etw_result else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ System monitoring demo failed: {e}")
        return False

def demo_tool_manager():
    """Demonstrate tool management."""
    print("\n🔧 DEMO 8: Tool Management")
    print("-" * 40)
    
    try:
        from src.utils.tool_manager import ToolManager
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        tool_manager = ToolManager(config)
        
        print("🔧 Testing tool management...")
        
        # Get tool status
        status = tool_manager.get_installation_status()
        print(f"✅ Tool status retrieved: {len(status)} tools configured")
        
        # Check specific tools
        tools_to_check = ["tcpdump", "binwalk"]
        for tool in tools_to_check:
            path = tool_manager.get_tool_path(tool)
            if path:
                print(f"   - {tool}: ✅ Found at {path}")
            else:
                print(f"   - {tool}: ⚠️ Not found (may need installation)")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool management demo failed: {e}")
        return False

def demo_reporting():
    """Demonstrate reporting capabilities."""
    print("\n📄 DEMO 9: Reporting Capabilities")
    print("-" * 40)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        # Run a quick investigation for reporting
        print("🔍 Running investigation for report generation...")
        results = investigator.investigate(target="localhost", scope="basic")
        
        # Generate report
        print("📄 Generating investigation report...")
        report_path = investigator.generate_report(output_dir="reports", format="html")
        
        print(f"✅ Report generated: {report_path}")
        
        # Export IOCs
        print("📊 Exporting IOCs...")
        ioc_path = investigator.export_iocs(output_dir="reports", format="json")
        
        print(f"✅ IOCs exported: {ioc_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Reporting demo failed: {e}")
        return False

def demo_platform_utils():
    """Demonstrate platform utilities."""
    print("\n🖥️ DEMO 10: Platform Utilities")
    print("-" * 40)
    
    try:
        from src.utils.platform_utils import PlatformUtils
        
        platform_utils = PlatformUtils()
        
        print("🖥️ Testing platform utilities...")
        
        # Get system info
        system_info = platform_utils.get_system_info()
        print(f"✅ System information:")
        print(f"   - Platform: {system_info['platform']}")
        print(f"   - Architecture: {system_info['architecture']}")
        print(f"   - Hostname: {system_info['hostname']}")
        
        # Get processes
        processes = platform_utils.get_process_list()
        print(f"✅ Process analysis: {len(processes)} processes found")
        
        # Get services
        services = platform_utils.get_services()
        print(f"✅ Service analysis: {len(services)} services found")
        
        # Get network connections
        connections = platform_utils.get_network_connections()
        print(f"✅ Network analysis: {len(connections)} connections found")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform utilities demo failed: {e}")
        return False

def main():
    """Main demonstration function."""
    print_banner()
    
    demos = [
        ("Basic Functionality", demo_basic_functionality),
        ("Investigation Capabilities", demo_investigation),
        ("Static Analysis", demo_static_analysis),
        ("Behavioral Analysis", demo_behavioral_analysis),
        ("Network Analysis", demo_network_analysis),
        ("Memory Forensics", demo_memory_forensics),
        ("System Monitoring", demo_system_monitoring),
        ("Tool Management", demo_tool_manager),
        ("Reporting Capabilities", demo_reporting),
        ("Platform Utilities", demo_platform_utils)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results[demo_name] = success
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Demo '{demo_name}' failed with exception: {e}")
            results[demo_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for demo_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{demo_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} demonstrations passed")
    
    if passed == total:
        print("\n🎉 ALL DEMONSTRATIONS PASSED!")
        print("🚀 The URCS Investigator Toolkit is fully functional!")
        print("\n📖 Next steps:")
        print("1. Run: python3 main.py dashboard --port 5000")
        print("2. Open browser to http://localhost:5000")
        print("3. Start real-time monitoring")
        print("4. Run investigations through the web interface")
        print("\n💡 Additional commands:")
        print("   - python3 main.py investigate --target localhost --scope full")
        print("   - python3 main.py monitor --start")
        print("   - python3 main.py setup --all")
        return True
    else:
        print(f"\n⚠️ {total - passed} demonstrations failed.")
        print("Please check the errors above and ensure all dependencies are installed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)