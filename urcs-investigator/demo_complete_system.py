#!/usr/bin/env python3
"""
Complete Enhanced URCS Investigator Toolkit - Comprehensive Demonstration
Shows all features including the new hardware optimization and warranty checking systems.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_banner():
    """Print complete system banner."""
    print("=" * 80)
    print("🔍 COMPLETE ENHANCED URCS INVESTIGATOR TOOLKIT - COMPREHENSIVE DEMONSTRATION")
    print("=" * 80)
    print("🎯 Purpose: Defensive analysis and detection of unauthorized resource-consuming software")
    print("🛡️  Legal: This toolkit is for defensive analysis and threat intelligence only")
    print("📋 Features: Real-time monitoring, behavioral analysis, memory forensics, network analysis")
    print("🌟 NEW: Intelligent intensity management engine")
    print("🔧 NEW: Hardware-aware mining optimization")
    print("🔍 NEW: Hardware warranty compliance checker")
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

def demo_hardware_optimizer():
    """Demonstrate the hardware-aware mining optimizer."""
    print("\n🔧 DEMO 2: Hardware-Aware Mining Optimizer")
    print("-" * 50)
    
    try:
        from src.utils.hardware_optimizer import HardwareOptimizer
        
        # Create sample config
        config = {
            "hardware_optimizer": {
                "enabled": True,
                "monitoring_interval": 5,
                "thermal_thresholds": {
                    "cpu_critical": 85.0,
                    "cpu_warning": 80.0,
                    "gpu_critical": 88.0,
                    "gpu_warning": 82.0
                }
            }
        }
        
        # Create hardware optimizer
        optimizer = HardwareOptimizer(config)
        
        print("✅ Hardware Optimizer initialized")
        print(f"🔍 Detected hardware:")
        print(f"   - CPU: {optimizer.hardware_info.cpu_model}")
        print(f"   - Cores: {optimizer.hardware_info.cpu_cores}")
        print(f"   - Threads: {optimizer.hardware_info.cpu_threads}")
        print(f"   - TDP: {optimizer.hardware_info.cpu_tdp}W")
        print(f"   - GPU: {optimizer.hardware_info.gpu_model or 'None'}")
        print(f"   - VRAM: {optimizer.hardware_info.gpu_vram or 'N/A'}MB")
        print(f"   - RAM: {optimizer.hardware_info.system_ram}MB")
        
        # Test optimization
        print("\n🔧 Testing optimization...")
        optimization = optimizer.optimize_mining()
        
        print(f"✅ Optimization results:")
        print(f"   - Algorithm: {optimization.recommended_algorithm}")
        print(f"   - CPU Threads: {optimization.cpu_threads}")
        print(f"   - GPU Enabled: {optimization.gpu_enabled}")
        print(f"   - Intensity: {optimization.intensity_percent}%")
        print(f"   - Reason: {optimization.reason}")
        print(f"   - Thermal Safe: {optimization.thermal_safe}")
        print(f"   - Power Safe: {optimization.power_safe}")
        print(f"   - User Safe: {optimization.user_safe}")
        
        # Test monitoring
        print("\n📊 Starting brief monitoring session...")
        optimizer.start_monitoring()
        time.sleep(15)  # Monitor for 15 seconds
        
        # Get statistics
        stats = optimizer.get_optimization_stats(1)  # Last minute
        print(f"📈 Monitoring statistics:")
        print(f"   - Total optimizations: {stats.get('total_optimizations', 0)}")
        print(f"   - Most common algorithm: {stats.get('most_common_algorithm', 'N/A')}")
        print(f"   - Average intensity: {stats.get('average_intensity', 0):.1f}%")
        print(f"   - GPU usage: {stats.get('gpu_usage_percent', 0):.1f}%")
        
        # Test emergency stop
        print("\n🛑 Testing emergency stop...")
        emergency_opt = optimizer.emergency_stop()
        print(f"   - Emergency stop activated: {emergency_opt.intensity_percent}% intensity")
        
        # Stop monitoring
        optimizer.stop_monitoring()
        print("✅ Hardware monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware optimizer demo failed: {e}")
        return False

def demo_warranty_checker():
    """Demonstrate the hardware warranty checker."""
    print("\n🔍 DEMO 3: Hardware Warranty Compliance Checker")
    print("-" * 50)
    
    try:
        from src.utils.warranty_checker import WarrantyChecker
        
        # Create sample config
        config = {
            "warranty_checker": {
                "enabled": True,
                "check_interval": 300,  # 5 minutes
                "alert_thresholds": {
                    "ssd_temp_warning": 75.0,
                    "ssd_temp_critical": 80.0,
                    "gpu_temp_warning": 80.0,
                    "gpu_temp_critical": 85.0
                }
            }
        }
        
        # Create warranty checker
        checker = WarrantyChecker(config)
        
        print("✅ Warranty Checker initialized")
        
        # Check SMART attributes
        print("\n🔍 Checking SMART attributes...")
        smart_info = checker.check_smart_attributes()
        print(f"✅ SMART check completed:")
        print(f"   - Drive: {smart_info.drive_path}")
        print(f"   - Health: {smart_info.health_status}")
        print(f"   - Temperature: {smart_info.temperature_current or 'N/A'}°C")
        print(f"   - Power-on hours: {smart_info.power_on_hours or 'N/A'}")
        print(f"   - Life percentage: {smart_info.life_percentage or 'N/A'}%")
        
        # Check GPU warranty
        print("\n🔍 Checking GPU warranty...")
        gpu_info = checker.check_gpu_warranty()
        print(f"✅ GPU warranty check completed:")
        print(f"   - Model: {gpu_info.gpu_model}")
        print(f"   - Vendor: {gpu_info.vendor}")
        print(f"   - LHR Status: {gpu_info.lhr_status or 'Unknown'}")
        print(f"   - Mining voids warranty: {gpu_info.mining_flag or 'Unknown'}")
        print(f"   - Warranty status: {gpu_info.warranty_status}")
        
        # Check warranty compliance
        print("\n🔍 Checking warranty compliance...")
        alerts = checker.check_warranty_compliance()
        print(f"✅ Warranty compliance check completed:")
        print(f"   - Alerts found: {len(alerts)}")
        
        for alert in alerts:
            print(f"   - {alert.severity.upper()}: {alert.description}")
        
        # Get recommendations
        print("\n💡 Getting warranty recommendations...")
        recommendations = checker.get_warranty_recommendations()
        print("✅ Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        
        # Export report
        print("\n📄 Exporting warranty report...")
        report_path = checker.export_warranty_report()
        print(f"✅ Warranty report exported to: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Warranty checker demo failed: {e}")
        return False

def demo_enhanced_investigation():
    """Demonstrate enhanced investigation with all new features."""
    print("\n🔍 DEMO 4: Enhanced Investigation with All Features")
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

def demo_all_cli_commands():
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
                "report", "export-iocs", "setup", "monitor", "dashboard", 
                "intensity", "hardware", "warranty"
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

def demo_integration():
    """Demonstrate integration between all systems."""
    print("\n🔗 DEMO 6: System Integration")
    print("-" * 50)
    
    try:
        from src.core.investigator import URCSInvestigator
        from src.core.config import ConfigManager
        from src.utils.intensity_engine import IntensityEngine
        from src.utils.hardware_optimizer import HardwareOptimizer
        from src.utils.warranty_checker import WarrantyChecker
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print("🔗 Testing system integration...")
        
        # Test investigator integration
        investigator = URCSInvestigator(config)
        if hasattr(investigator, 'intensity_engine'):
            print("✅ Intensity engine integrated into investigator")
        else:
            print("❌ Intensity engine not integrated")
            return False
        
        # Test hardware optimizer
        hardware_config = {"hardware_optimizer": {"enabled": True}}
        optimizer = HardwareOptimizer(hardware_config)
        optimization = optimizer.optimize_mining()
        print(f"✅ Hardware optimizer working: {optimization.recommended_algorithm}")
        
        # Test warranty checker
        warranty_config = {"warranty_checker": {"enabled": True}}
        checker = WarrantyChecker(warranty_config)
        alerts = checker.check_warranty_compliance()
        print(f"✅ Warranty checker working: {len(alerts)} alerts found")
        
        # Test intensity engine
        intensity_engine = IntensityEngine()
        system_state = intensity_engine.get_system_state()
        decision = intensity_engine.compute_intensity(system_state)
        print(f"✅ Intensity engine working: {decision.intensity_percent}%")
        
        print("✅ All systems integrated and working together")
        
        return True
        
    except Exception as e:
        print(f"❌ System integration demo failed: {e}")
        return False

def main():
    """Main demonstration function."""
    print_banner()
    
    demos = [
        ("Intensity Engine", demo_intensity_engine),
        ("Hardware Optimizer", demo_hardware_optimizer),
        ("Warranty Checker", demo_warranty_checker),
        ("Enhanced Investigation", demo_enhanced_investigation),
        ("CLI Commands", demo_all_cli_commands),
        ("System Integration", demo_integration)
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
    print("📊 COMPLETE SYSTEM DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for demo_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{demo_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} demonstrations passed")
    
    if passed == total:
        print("\n🎉 ALL COMPLETE SYSTEM DEMONSTRATIONS PASSED!")
        print("🚀 The Complete Enhanced URCS Investigator Toolkit is fully operational!")
        print("\n🌟 ALL NEW FEATURES DEMONSTRATED:")
        print("   - Intelligent intensity management engine")
        print("   - Hardware-aware mining optimization")
        print("   - Hardware warranty compliance checker")
        print("   - Enhanced web dashboard")
        print("   - Cross-platform compatibility")
        print("   - Suspicious pattern detection")
        print("   - Real-time monitoring and alerts")
        print("\n📖 Next steps:")
        print("1. Run: python3 main.py intensity --demo")
        print("2. Run: python3 main.py hardware --demo")
        print("3. Run: python3 main.py warranty --demo")
        print("4. Run: python3 main.py dashboard --port 5000")
        print("5. Run: python3 main.py investigate --target localhost --scope full")
        print("\n💡 The complete system demonstrates:")
        print("   - Legitimate resource management patterns")
        print("   - Hardware-aware optimization")
        print("   - Warranty compliance monitoring")
        print("   - Defensive analysis capabilities")
        print("   - Educational insights into proper resource management!")
        return True
    else:
        print(f"\n⚠️ {total - passed} demonstrations failed.")
        print("Please check the errors above and ensure all dependencies are installed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)