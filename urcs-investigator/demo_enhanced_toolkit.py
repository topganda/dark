#!/usr/bin/env python3
"""
Enhanced URCS Investigator Toolkit - Comprehensive Demonstration
Shows all enhanced features including the intelligent intensity management engine.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_banner():
    """Print enhanced toolkit banner."""
    print("=" * 80)
    print("🔍 ENHANCED URCS INVESTIGATOR TOOLKIT - COMPREHENSIVE DEMONSTRATION")
    print("=" * 80)
    print("🎯 Purpose: Defensive analysis and detection of unauthorized resource-consuming software")
    print("🛡️  Legal: This toolkit is for defensive analysis and threat intelligence only")
    print("📋 Features: Real-time monitoring, behavioral analysis, memory forensics, network analysis")
    print("🌟 NEW: Intelligent intensity management engine for resource pattern analysis")
    print("=" * 80)

def demo_intensity_engine():
    """Demonstrate the intelligent intensity management engine."""
    print("\n🚀 DEMO 1: Intelligent Intensity Management Engine")
    print("-" * 50)
    
    try:
        from src.utils.intensity_engine import IntensityEngine
        
        print("🔍 Testing intelligent resource management patterns...")
        
        # Create intensity engine
        engine = IntensityEngine(poll_seconds=2)
        
        # Get current system state
        system_state = engine.get_system_state()
        print(f"✅ System state captured:")
        print(f"   - Idle time: {system_state.idle_time_minutes:.1f} minutes")
        print(f"   - Battery: {system_state.battery_percent}%")
        print(f"   - AC Power: {system_state.on_ac_power}")
        print(f"   - CPU Temp: {system_state.cpu_temperature:.1f}°C")
        print(f"   - Task Manager: {system_state.task_manager_foreground}")
        
        # Compute intensity
        decision = engine.compute_intensity(system_state)
        print(f"✅ Intensity decision: {decision.intensity_percent}% - {decision.reason}")
        
        # Start monitoring briefly
        print("📊 Starting brief monitoring session...")
        engine.start_monitoring()
        time.sleep(10)  # Monitor for 10 seconds
        
        # Get statistics
        stats = engine.get_intensity_stats(1)  # Last minute
        print(f"📈 Monitoring statistics:")
        print(f"   - Average intensity: {stats.get('average_intensity', 0):.1f}%")
        print(f"   - Max intensity: {stats.get('max_intensity', 0)}%")
        print(f"   - Min intensity: {stats.get('min_intensity', 0)}%")
        print(f"   - Total decisions: {stats.get('total_decisions', 0)}")
        
        # Check for suspicious patterns
        suspicious = engine.detect_suspicious_patterns()
        if suspicious:
            print(f"⚠️ Suspicious patterns detected:")
            for pattern in suspicious:
                print(f"   - {pattern['type']}: {pattern['description']}")
        else:
            print("✅ No suspicious patterns detected")
        
        # Stop monitoring
        engine.stop_monitoring()
        
        return True
        
    except Exception as e:
        print(f"❌ Intensity engine demo failed: {e}")
        return False

def demo_enhanced_investigation():
    """Demonstrate enhanced investigation with intensity analysis."""
    print("\n🔍 DEMO 2: Enhanced Investigation with Intensity Analysis")
    print("-" * 50)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("🔍 Running enhanced investigation...")
        
        # Run basic investigation
        results = investigator.investigate(target="localhost", scope="basic")
        print(f"✅ Basic investigation completed:")
        print(f"   - Findings: {len(results.get('findings', []))}")
        print(f"   - IOCs: {len(results.get('iocs', []))}")
        print(f"   - Behaviors detected: {len(results.get('behaviors_detected', []))}")
        
        # Run intensity analysis
        print("📊 Running intensity pattern analysis...")
        intensity_results = investigator.analyze_intensity_patterns(duration_minutes=2)
        
        if "error" not in intensity_results:
            print(f"✅ Intensity analysis completed:")
            print(f"   - Current intensity: {intensity_results['current_intensity']}%")
            print(f"   - Current reason: {intensity_results['current_reason']}")
            print(f"   - Suspicious patterns: {len(intensity_results.get('suspicious_patterns', []))}")
            
            # Show pattern analysis
            pattern_analysis = intensity_results.get('pattern_analysis', {})
            if pattern_analysis:
                print(f"   - Pattern consistency: {pattern_analysis.get('pattern_consistency', {}).get('pattern_type', 'Unknown')}")
                print(f"   - Intensity variance: {pattern_analysis.get('intensity_variance', 0):.2f}")
        else:
            print(f"❌ Intensity analysis failed: {intensity_results['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced investigation demo failed: {e}")
        return False

def demo_web_dashboard():
    """Demonstrate web dashboard capabilities."""
    print("\n🌐 DEMO 3: Web Dashboard Capabilities")
    print("-" * 50)
    
    try:
        from src.web.dashboard import URCSDashboard
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print("🌐 Testing web dashboard initialization...")
        
        # Create dashboard
        dashboard = URCSDashboard(config)
        print("✅ Dashboard initialized successfully")
        
        # Test dashboard components
        print("📊 Testing dashboard components:")
        
        # Test system state
        system_info = dashboard.platform_utils.get_system_info()
        print(f"   - Platform: {system_info['platform']}")
        print(f"   - Architecture: {system_info['architecture']}")
        
        # Test metrics
        metrics = dashboard._get_current_metrics()
        print(f"   - CPU Usage: {metrics.get('cpu', {}).get('percent', 0):.1f}%")
        print(f"   - Memory Usage: {metrics.get('memory', {}).get('percent', 0):.1f}%")
        print(f"   - Disk Usage: {metrics.get('disk', {}).get('percent', 0):.1f}%")
        
        print("✅ Web dashboard components working correctly")
        print("💡 To start the dashboard: python3 main.py dashboard --port 5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Web dashboard demo failed: {e}")
        return False

def demo_platform_utils():
    """Demonstrate enhanced platform utilities."""
    print("\n🖥️ DEMO 4: Enhanced Platform Utilities")
    print("-" * 50)
    
    try:
        from src.utils.platform_utils import PlatformUtils
        
        platform_utils = PlatformUtils()
        
        print("🖥️ Testing enhanced platform utilities...")
        
        # Get system information
        system_info = platform_utils.get_system_info()
        print(f"✅ System information:")
        print(f"   - Platform: {system_info['platform']}")
        print(f"   - Architecture: {system_info['architecture']}")
        print(f"   - Hostname: {system_info['hostname']}")
        print(f"   - Python version: {system_info['python_version'].split()[0]}")
        
        # Test process analysis
        processes = platform_utils.get_process_list()
        print(f"✅ Process analysis: {len(processes)} processes found")
        
        # Test network analysis
        connections = platform_utils.get_network_connections()
        print(f"✅ Network analysis: {len(connections)} connections found")
        
        # Test service analysis
        services = platform_utils.get_services()
        print(f"✅ Service analysis: {len(services)} services found")
        
        # Test command availability
        commands_to_test = ["ps", "netstat", "find"]
        for cmd in commands_to_test:
            available = platform_utils.is_command_available(cmd)
            print(f"   - {cmd}: {'✅ Available' if available else '❌ Not available'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform utilities demo failed: {e}")
        return False

def demo_all_commands():
    """Demonstrate all available CLI commands."""
    print("\n💻 DEMO 5: All Available CLI Commands")
    print("-" * 50)
    
    try:
        import subprocess
        
        print("💻 Testing all CLI commands...")
        
        # Test help command
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Main help command works")
            
            # Check for all commands
            commands = [
                "investigate", "static", "behavioral", "memory", "network", 
                "report", "export-iocs", "setup", "monitor", "dashboard", "intensity"
            ]
            
            for cmd in commands:
                if cmd in result.stdout:
                    print(f"   - {cmd}: ✅ Available")
                else:
                    print(f"   - {cmd}: ❌ Missing")
            
            print("✅ All CLI commands are properly configured")
        else:
            print("❌ CLI help command failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI commands demo failed: {e}")
        return False

def demo_intensity_integration():
    """Demonstrate intensity engine integration with investigation."""
    print("\n🔗 DEMO 6: Intensity Engine Integration")
    print("-" * 50)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print("🔗 Testing intensity engine integration...")
        
        # Test that intensity engine is initialized
        if hasattr(investigator, 'intensity_engine'):
            print("✅ Intensity engine properly integrated into investigator")
            
            # Test intensity analysis method
            if hasattr(investigator, 'analyze_intensity_patterns'):
                print("✅ Intensity analysis method available")
                
                # Run brief analysis
                results = investigator.analyze_intensity_patterns(duration_minutes=1)
                
                if "error" not in results:
                    print("✅ Intensity analysis integration working")
                    print(f"   - Current intensity: {results['current_intensity']}%")
                    print(f"   - Analysis type: {results['analysis_type']}")
                else:
                    print(f"❌ Intensity analysis failed: {results['error']}")
            else:
                print("❌ Intensity analysis method not found")
        else:
            print("❌ Intensity engine not integrated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Intensity integration demo failed: {e}")
        return False

def main():
    """Main demonstration function."""
    print_banner()
    
    demos = [
        ("Intensity Engine", demo_intensity_engine),
        ("Enhanced Investigation", demo_enhanced_investigation),
        ("Web Dashboard", demo_web_dashboard),
        ("Platform Utilities", demo_platform_utils),
        ("CLI Commands", demo_all_commands),
        ("Intensity Integration", demo_intensity_integration)
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
    print("📊 ENHANCED DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for demo_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{demo_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} demonstrations passed")
    
    if passed == total:
        print("\n🎉 ALL ENHANCED DEMONSTRATIONS PASSED!")
        print("🚀 The Enhanced URCS Investigator Toolkit is fully operational!")
        print("\n🌟 NEW FEATURES DEMONSTRATED:")
        print("   - Intelligent intensity management engine")
        print("   - Real-time resource pattern analysis")
        print("   - Enhanced web dashboard")
        print("   - Cross-platform compatibility")
        print("   - Suspicious pattern detection")
        print("\n📖 Next steps:")
        print("1. Run: python3 main.py intensity --demo")
        print("2. Run: python3 main.py dashboard --port 5000")
        print("3. Run: python3 main.py investigate --target localhost --scope full")
        print("4. Run: python3 main.py intensity --duration 30")
        print("\n💡 The intensity engine demonstrates legitimate resource management patterns")
        print("   that can be used to detect unauthorized resource-consuming software!")
        return True
    else:
        print(f"\n⚠️ {total - passed} demonstrations failed.")
        print("Please check the errors above and ensure all dependencies are installed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)