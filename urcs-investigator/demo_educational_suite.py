#!/usr/bin/env python3
"""
Comprehensive Educational Suite Demo
Demonstrates all educational modules for mining and cryptocurrency analysis.
This script provides theoretical knowledge and defensive analysis capabilities only.
NO ACTUAL MINING, ATTACKS, OR MALICIOUS ACTIVITIES OCCUR.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main demo function."""
    print("🎓 URCS Investigator - Educational Suite Demo")
    print("=" * 60)
    print("💡 This demonstrates comprehensive educational content only")
    print("🚫 NO ACTUAL MINING, ATTACKS, OR MALICIOUS ACTIVITIES OCCUR")
    print("🔒 All activities are for defensive analysis and learning purposes")
    print()
    
    # Test configuration
    config = {
        "logging": {"level": "INFO"},
        "output": {"directory": "educational_reports"}
    }
    
    # Create output directory
    os.makedirs("educational_reports", exist_ok=True)
    
    # Track demo results
    demo_results = {
        "timestamp": datetime.now().isoformat(),
        "modules_tested": [],
        "success_count": 0,
        "total_count": 0,
        "reports_generated": []
    }
    
    print("🚀 Starting Educational Suite Demo...")
    print()
    
    # Test 1: Mining Education Module
    print("📚 Test 1: Mining & Cryptocurrency Education")
    print("-" * 40)
    try:
        from education.mining_education import demo_mining_education
        
        success = demo_mining_education()
        demo_results["total_count"] += 1
        
        if success:
            print("✅ Mining Education Module: PASSED")
            demo_results["success_count"] += 1
            demo_results["modules_tested"].append("mining_education")
        else:
            print("❌ Mining Education Module: FAILED")
            
    except Exception as e:
        print(f"❌ Mining Education Module: ERROR - {e}")
    
    print()
    
    # Test 2: Cybersecurity Awareness Module
    print("🛡️ Test 2: Cybersecurity Awareness & Defense")
    print("-" * 40)
    try:
        from education.cybersecurity_awareness import demo_cybersecurity_awareness
        
        success = demo_cybersecurity_awareness()
        demo_results["total_count"] += 1
        
        if success:
            print("✅ Cybersecurity Awareness Module: PASSED")
            demo_results["success_count"] += 1
            demo_results["modules_tested"].append("cybersecurity_awareness")
        else:
            print("❌ Cybersecurity Awareness Module: FAILED")
            
    except Exception as e:
        print(f"❌ Cybersecurity Awareness Module: ERROR - {e}")
    
    print()
    
    # Test 3: System Administration Module
    print("⚙️ Test 3: System Administration & Resource Management")
    print("-" * 40)
    try:
        from education.system_administration import demo_system_administration
        
        success = demo_system_administration()
        demo_results["total_count"] += 1
        
        if success:
            print("✅ System Administration Module: PASSED")
            demo_results["success_count"] += 1
            demo_results["modules_tested"].append("system_administration")
        else:
            print("❌ System Administration Module: FAILED")
            
    except Exception as e:
        print(f"❌ System Administration Module: ERROR - {e}")
    
    print()
    
    # Test 4: Privacy Protection Module
    print("🔒 Test 4: Privacy & Data Protection")
    print("-" * 40)
    try:
        from education.privacy_protection import demo_privacy_protection
        
        success = demo_privacy_protection()
        demo_results["total_count"] += 1
        
        if success:
            print("✅ Privacy Protection Module: PASSED")
            demo_results["success_count"] += 1
            demo_results["modules_tested"].append("privacy_protection")
        else:
            print("❌ Privacy Protection Module: FAILED")
            
    except Exception as e:
        print(f"❌ Privacy Protection Module: ERROR - {e}")
    
    print()
    
    # Test 5: Comprehensive Educational Suite
    print("🎓 Test 5: Comprehensive Educational Suite")
    print("-" * 40)
    try:
        from education.educational_suite import EducationalSuite
        
        suite = EducationalSuite()
        success = suite.run_comprehensive_demo()
        demo_results["total_count"] += 1
        
        if success:
            print("✅ Comprehensive Educational Suite: PASSED")
            demo_results["success_count"] += 1
            demo_results["modules_tested"].append("comprehensive_suite")
        else:
            print("❌ Comprehensive Educational Suite: FAILED")
            
    except Exception as e:
        print(f"❌ Comprehensive Educational Suite: ERROR - {e}")
    
    print()
    
    # Test 6: Learning Path Generation
    print("🛤️ Test 6: Learning Path Generation")
    print("-" * 40)
    try:
        from education.educational_suite import EducationalSuite
        
        suite = EducationalSuite()
        
        # Test beginner path
        beginner_plan = suite.generate_learning_plan("beginner")
        if "error" not in beginner_plan:
            print("✅ Beginner Learning Path: PASSED")
            demo_results["success_count"] += 1
        else:
            print(f"❌ Beginner Learning Path: FAILED - {beginner_plan['error']}")
        
        # Test intermediate path
        intermediate_plan = suite.generate_learning_plan("intermediate")
        if "error" not in intermediate_plan:
            print("✅ Intermediate Learning Path: PASSED")
            demo_results["success_count"] += 1
        else:
            print(f"❌ Intermediate Learning Path: FAILED - {intermediate_plan['error']}")
        
        # Test advanced path
        advanced_plan = suite.generate_learning_plan("advanced")
        if "error" not in advanced_plan:
            print("✅ Advanced Learning Path: PASSED")
            demo_results["success_count"] += 1
        else:
            print(f"❌ Advanced Learning Path: FAILED - {advanced_plan['error']}")
        
        demo_results["total_count"] += 3
        
    except Exception as e:
        print(f"❌ Learning Path Generation: ERROR - {e}")
        demo_results["total_count"] += 3
    
    print()
    
    # Test 7: Report Generation
    print("📄 Test 7: Report Generation")
    print("-" * 40)
    try:
        from education.educational_suite import EducationalSuite
        
        suite = EducationalSuite()
        report_path = suite.generate_comprehensive_report()
        
        if report_path and os.path.exists(report_path):
            print(f"✅ Comprehensive Report: PASSED - {report_path}")
            demo_results["success_count"] += 1
            demo_results["reports_generated"].append(report_path)
        else:
            print("❌ Comprehensive Report: FAILED")
        
        demo_results["total_count"] += 1
        
    except Exception as e:
        print(f"❌ Report Generation: ERROR - {e}")
        demo_results["total_count"] += 1
    
    print()
    
    # Generate demo summary report
    print("📊 Demo Summary")
    print("=" * 60)
    
    success_rate = (demo_results["success_count"] / demo_results["total_count"]) * 100 if demo_results["total_count"] > 0 else 0
    
    print(f"✅ Tests Passed: {demo_results['success_count']}/{demo_results['total_count']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"📚 Modules Tested: {len(demo_results['modules_tested'])}")
    print(f"📄 Reports Generated: {len(demo_results['reports_generated'])}")
    
    print()
    print("📋 Modules Tested:")
    for module in demo_results["modules_tested"]:
        print(f"   - {module}")
    
    print()
    print("📄 Reports Generated:")
    for report in demo_results["reports_generated"]:
        print(f"   - {report}")
    
    print()
    
    # Save demo results
    results_file = "educational_reports/demo_results.json"
    with open(results_file, 'w') as f:
        json.dump(demo_results, f, indent=2)
    
    print(f"📊 Demo results saved to: {results_file}")
    
    # Final assessment
    print()
    if success_rate >= 80:
        print("🎉 EDUCATIONAL SUITE DEMO: EXCELLENT SUCCESS!")
        print("✅ All major educational modules are working correctly")
        print("📚 Ready for comprehensive learning and defensive analysis")
    elif success_rate >= 60:
        print("👍 EDUCATIONAL SUITE DEMO: GOOD SUCCESS!")
        print("✅ Most educational modules are working correctly")
        print("⚠️ Some modules may need attention")
    else:
        print("⚠️ EDUCATIONAL SUITE DEMO: NEEDS ATTENTION!")
        print("❌ Several modules encountered issues")
        print("🔧 Please check dependencies and configurations")
    
    print()
    print("🎯 Educational Suite Capabilities:")
    print("   📚 Mining & Cryptocurrency Education")
    print("   🛡️ Cybersecurity Awareness & Defense")
    print("   ⚙️ System Administration & Resource Management")
    print("   🔒 Privacy & Data Protection")
    print("   🛤️ Learning Paths (Beginner, Intermediate, Advanced)")
    print("   📄 Comprehensive Reporting")
    
    print()
    print("💡 Usage Examples:")
    print("   python main.py education --demo")
    print("   python main.py education --module mining")
    print("   python main.py education --path beginner")
    print("   python main.py education --report")
    
    print()
    print("🔒 IMPORTANT REMINDER:")
    print("   This educational suite is for DEFENSIVE ANALYSIS ONLY")
    print("   NO ACTUAL MINING, ATTACKS, OR MALICIOUS ACTIVITIES OCCUR")
    print("   All content is designed for learning and threat detection")
    
    return success_rate >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)