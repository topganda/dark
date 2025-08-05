#!/usr/bin/env python3
"""
URCS Investigator Toolkit - Main Application
A comprehensive defensive analysis and detection toolkit for investigating unauthorized resource-consuming software.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.investigator import URCSInvestigator
from src.core.config import ConfigManager
from src.utils.logger import setup_logging
from src.utils.validator import validate_authorization


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="URCS Investigator Toolkit - Defensive Analysis and Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py investigate --target localhost
  python main.py static --file suspicious.exe
  python main.py behavioral --system
  python main.py memory --pid 1234
  python main.py network --interface eth0
  python main.py report --output investigation_report.html
        """
    )

    # Main commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Investigate command
    investigate_parser = subparsers.add_parser('investigate', help='Run comprehensive investigation')
    investigate_parser.add_argument('--target', required=True, help='Target system or file')
    investigate_parser.add_argument('--config', help='Configuration file path')
    investigate_parser.add_argument('--scope', choices=['basic', 'comprehensive', 'full'], 
                                   default='comprehensive', help='Investigation scope')
    investigate_parser.add_argument('--output', help='Output directory for results')

    # Static analysis command
    static_parser = subparsers.add_parser('static', help='Perform static file analysis')
    static_parser.add_argument('--file', required=True, help='File to analyze')
    static_parser.add_argument('--entropy', action='store_true', help='Calculate file entropy')
    static_parser.add_argument('--signature', action='store_true', help='Verify digital signatures')
    static_parser.add_argument('--yara', action='store_true', help='Run YARA rules')

    # Behavioral analysis command
    behavioral_parser = subparsers.add_parser('behavioral', help='Perform behavioral analysis')
    behavioral_parser.add_argument('--system', action='store_true', help='Analyze entire system')
    behavioral_parser.add_argument('--registry', action='store_true', help='Registry analysis')
    behavioral_parser.add_argument('--services', action='store_true', help='Service enumeration')
    behavioral_parser.add_argument('--tasks', action='store_true', help='Scheduled task analysis')

    # Memory forensics command
    memory_parser = subparsers.add_parser('memory', help='Perform memory forensics')
    memory_parser.add_argument('--pid', type=int, help='Process ID to analyze')
    memory_parser.add_argument('--dump', help='Memory dump file path')
    memory_parser.add_argument('--injection', action='store_true', help='Detect process injection')

    # Network analysis command
    network_parser = subparsers.add_parser('network', help='Perform network analysis')
    network_parser.add_argument('--interface', help='Network interface to monitor')
    network_parser.add_argument('--capture', help='PCAP file to analyze')
    network_parser.add_argument('--live', action='store_true', help='Live traffic capture')

    # Report generation command
    report_parser = subparsers.add_parser('report', help='Generate investigation report')
    report_parser.add_argument('--output', required=True, help='Output file path')
    report_parser.add_argument('--format', choices=['html', 'pdf', 'json', 'csv'], 
                              default='html', help='Report format')
    report_parser.add_argument('--template', help='Custom report template')

    # IOC export command
    ioc_parser = subparsers.add_parser('export-iocs', help='Export indicators of compromise')
    ioc_parser.add_argument('--format', choices=['json', 'csv', 'stix'], 
                           default='json', help='IOC format')
    ioc_parser.add_argument('--output', help='Output file path')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup investigation environment')
    setup_parser.add_argument('--sysmon', action='store_true', help='Install Sysmon')
    setup_parser.add_argument('--etw', action='store_true', help='Configure ETW tracing')
    setup_parser.add_argument('--powershell', action='store_true', help='Enable PowerShell logging')

    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config-file', help='Configuration file path')

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else (logging.INFO if args.verbose else logging.WARNING)
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    # Validate authorization
    if not validate_authorization():
        logger.error("❌ Authorization validation failed. Ensure you have proper permissions.")
        sys.exit(1)

    # Load configuration
    config_manager = ConfigManager(args.config_file)
    config = config_manager.load_config()

    try:
        if args.command == 'investigate':
            run_investigation(args, config)
        elif args.command == 'static':
            run_static_analysis(args, config)
        elif args.command == 'behavioral':
            run_behavioral_analysis(args, config)
        elif args.command == 'memory':
            run_memory_forensics(args, config)
        elif args.command == 'network':
            run_network_analysis(args, config)
        elif args.command == 'report':
            generate_report(args, config)
        elif args.command == 'export-iocs':
            export_iocs(args, config)
        elif args.command == 'setup':
            run_setup(args, config)
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_investigation(args, config):
    """Run comprehensive investigation"""
    print("🔍 Starting URCS Investigation...")
    print("=" * 50)
    
    investigator = URCSInvestigator(config)
    
    print(f"📋 Target: {args.target}")
    print(f"📊 Scope: {args.scope}")
    print(f"📁 Output: {args.output or 'reports/'}")
    print("=" * 50)
    
    # Run investigation
    results = investigator.investigate(
        target=args.target,
        scope=args.scope,
        output_dir=args.output
    )
    
    print("✅ Investigation completed successfully!")
    print(f"📄 Report generated: {results['report_path']}")
    print(f"🔍 IOCs extracted: {len(results['iocs'])} indicators")


def run_static_analysis(args, config):
    """Run static file analysis"""
    print(f"📄 Performing static analysis on: {args.file}")
    
    investigator = URCSInvestigator(config)
    results = investigator.static_analysis(
        file_path=args.file,
        entropy=args.entropy,
        signature=args.signature,
        yara=args.yara
    )
    
    print("✅ Static analysis completed!")
    print(f"📊 Entropy: {results.get('entropy', 'N/A')}")
    print(f"🔐 Signature: {results.get('signature_status', 'N/A')}")
    print(f"🎯 YARA matches: {len(results.get('yara_matches', []))}")


def run_behavioral_analysis(args, config):
    """Run behavioral analysis"""
    print("🔍 Performing behavioral analysis...")
    
    investigator = URCSInvestigator(config)
    results = investigator.behavioral_analysis(
        system=args.system,
        registry=args.registry,
        services=args.services,
        tasks=args.tasks
    )
    
    print("✅ Behavioral analysis completed!")
    print(f"🔑 Registry findings: {len(results.get('registry_findings', []))}")
    print(f"⚙️ Service findings: {len(results.get('service_findings', []))}")
    print(f"📅 Task findings: {len(results.get('task_findings', []))}")


def run_memory_forensics(args, config):
    """Run memory forensics"""
    print("🧠 Performing memory forensics...")
    
    investigator = URCSInvestigator(config)
    results = investigator.memory_forensics(
        pid=args.pid,
        dump_file=args.dump,
        injection=args.injection
    )
    
    print("✅ Memory forensics completed!")
    print(f"🔍 Injection findings: {len(results.get('injection_findings', []))}")
    print(f"📊 Memory regions analyzed: {len(results.get('memory_regions', []))}")


def run_network_analysis(args, config):
    """Run network analysis"""
    print("🌐 Performing network analysis...")
    
    investigator = URCSInvestigator(config)
    results = investigator.network_analysis(
        interface=args.interface,
        capture_file=args.capture,
        live=args.live
    )
    
    print("✅ Network analysis completed!")
    print(f"📡 Connections analyzed: {len(results.get('connections', []))}")
    print(f"🔍 Suspicious traffic: {len(results.get('suspicious_traffic', []))}")


def generate_report(args, config):
    """Generate investigation report"""
    print(f"📄 Generating report: {args.output}")
    
    investigator = URCSInvestigator(config)
    report_path = investigator.generate_report(
        output_path=args.output,
        format=args.format,
        template=args.template
    )
    
    print(f"✅ Report generated: {report_path}")


def export_iocs(args, config):
    """Export indicators of compromise"""
    print(f"📊 Exporting IOCs in {args.format} format...")
    
    investigator = URCSInvestigator(config)
    ioc_path = investigator.export_iocs(
        format=args.format,
        output_path=args.output
    )
    
    print(f"✅ IOCs exported: {ioc_path}")


def run_setup(args, config):
    """Setup investigation environment"""
    print("🔧 Setting up investigation environment...")
    
    investigator = URCSInvestigator(config)
    setup_results = investigator.setup_environment(
        sysmon=args.sysmon,
        etw=args.etw,
        powershell=args.powershell
    )
    
    print("✅ Environment setup completed!")
    for component, status in setup_results.items():
        print(f"  {component}: {'✅' if status else '❌'}")


if __name__ == "__main__":
    main()