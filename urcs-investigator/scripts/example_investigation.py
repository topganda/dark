#!/usr/bin/env python3
"""
Example Investigation Script for URCS Investigator Toolkit
Demonstrates how to use the toolkit for a basic investigation.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.investigator import URCSInvestigator
from src.core.config import ConfigManager
from src.utils.logger import setup_logging


def run_example_investigation():
    """Run an example investigation."""
    print("🔍 URCS Investigator Toolkit - Example Investigation")
    print("=" * 60)
    
    # Setup logging
    setup_logging(level=20)  # INFO level
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Initialize investigator
    investigator = URCSInvestigator(config)
    
    print("📋 Starting example investigation...")
    print("Target: localhost")
    print("Scope: basic")
    print("=" * 60)
    
    # Run basic investigation
    results = investigator.investigate(
        target="localhost",
        scope="basic",
        output_dir="reports/example_investigation"
    )
    
    # Display results summary
    print("\n📊 Investigation Results Summary:")
    print("-" * 40)
    print(f"Investigation ID: {results.get('investigation_id', 'N/A')}")
    print(f"Target: {results.get('target', 'N/A')}")
    print(f"Scope: {results.get('scope', 'N/A')}")
    print(f"Duration: {results.get('duration', 'N/A')} seconds")
    print(f"Findings: {len(results.get('findings', []))}")
    print(f"IOCs: {len(results.get('iocs', []))}")
    print(f"Report: {results.get('report_path', 'N/A')}")
    
    # Display findings
    if results.get('findings'):
        print("\n🔍 Findings:")
        print("-" * 20)
        for i, finding in enumerate(results['findings'], 1):
            print(f"{i}. {finding.get('description', 'N/A')} ({finding.get('severity', 'unknown')})")
    
    # Display IOCs
    if results.get('iocs'):
        print("\n📋 IOCs:")
        print("-" * 20)
        for i, ioc in enumerate(results['iocs'], 1):
            print(f"{i}. {ioc.get('type', 'N/A')}: {ioc.get('value', 'N/A')} ({ioc.get('confidence', 'unknown')})")
    
    print("\n✅ Example investigation completed!")
    print(f"📄 Full report available at: {results.get('report_path', 'N/A')}")
    print("📁 Check the reports/ directory for detailed results")


def run_static_analysis_example():
    """Run static analysis on a test file."""
    print("\n📄 Static Analysis Example")
    print("=" * 40)
    
    # Create a test file for analysis
    test_file = "test_file.bin"
    with open(test_file, 'wb') as f:
        # Create some test data
        f.write(b'\x00' * 1000)  # Low entropy data
        f.write(b'\xFF' * 1000)  # High entropy data
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        investigator = URCSInvestigator(config)
        
        print(f"Analyzing test file: {test_file}")
        results = investigator.static_analysis(
            file_path=test_file,
            entropy=True,
            signature=True,
            yara=True
        )
        
        print(f"Entropy: {results.get('entropy', 'N/A')}")
        print(f"Signature: {results.get('signature_status', 'N/A')}")
        print(f"YARA matches: {len(results.get('yara_matches', []))}")
        
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)


def run_behavioral_analysis_example():
    """Run behavioral analysis example."""
    print("\n🔍 Behavioral Analysis Example")
    print("=" * 40)
    
    config_manager = ConfigManager()
    config = config_manager.load_config()
    investigator = URCSInvestigator(config)
    
    results = investigator.behavioral_analysis(
        system=True,
        registry=True,
        services=True,
        tasks=True
    )
    
    print(f"Registry findings: {len(results.get('registry_findings', []))}")
    print(f"Service findings: {len(results.get('service_findings', []))}")
    print(f"Task findings: {len(results.get('task_findings', []))}")
    print(f"File system findings: {len(results.get('file_system_findings', []))}")
    print(f"Process findings: {len(results.get('process_findings', []))}")


def main():
    """Main function."""
    print("🚀 URCS Investigator Toolkit - Example Scripts")
    print("=" * 60)
    
    try:
        # Run example investigation
        run_example_investigation()
        
        # Run static analysis example
        run_static_analysis_example()
        
        # Run behavioral analysis example
        run_behavioral_analysis_example()
        
        print("\n🎉 All examples completed successfully!")
        print("\n📖 Next steps:")
        print("1. Review the generated reports")
        print("2. Check the logs for detailed information")
        print("3. Customize the configuration for your needs")
        print("4. Add your own YARA rules")
        print("5. Run real investigations on authorized systems")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Check the logs for more details")
        sys.exit(1)


if __name__ == "__main__":
    main()