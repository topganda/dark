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
import time # Added for monitor command

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.investigator import URCSInvestigator
from src.core.config import ConfigManager
from src.utils.logger import setup_logging
from src.utils.validator import validate_authorization
from src.utils.tool_manager import ToolManager
from src.utils.system_monitor import SystemMonitor


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
  python main.py setup --install-tools
  python main.py monitor --start
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
    setup_parser.add_argument('--install-tools', action='store_true', help='Install all external tools')
    setup_parser.add_argument('--configure-tools', action='store_true', help='Configure installed tools')
    setup_parser.add_argument('--sysmon', action='store_true', help='Install Sysmon')
    setup_parser.add_argument('--etw', action='store_true', help='Configure ETW tracing')
    setup_parser.add_argument('--powershell', action='store_true', help='Enable PowerShell logging')
    setup_parser.add_argument('--all', action='store_true', help='Setup everything')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time system monitoring')
    monitor_parser.add_argument('--start', action='store_true', help='Start monitoring')
    monitor_parser.add_argument('--stop', action='store_true', help='Stop monitoring')
    monitor_parser.add_argument('--status', action='store_true', help='Show monitoring status')
    monitor_parser.add_argument('--config', help='Monitoring configuration file')

    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Web dashboard for monitoring')
    dashboard_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    dashboard_parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config-file', help='Configuration file path')

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else (logging.INFO if args.verbose else logging.WARNING)
    setup_logging(level=log_level)

    # Validate authorization
    if not validate_authorization():
        print("❌ Authorization required. Please create .investigation_authorized file or set INVESTIGATION_AUTHORIZED=1")
        sys.exit(1)

    # Load configuration
    config_manager = ConfigManager(args.config_file)
    config = config_manager.load_config()

    # Execute command
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
    elif args.command == 'monitor':
        run_monitor(args, config)
    elif args.command == 'dashboard':
        run_dashboard(args, config)
    else:
        parser.print_help()


def run_investigation(args, config):
    """Run comprehensive investigation"""
    print(f"🔍 Starting investigation of {args.target}...")
    
    investigator = URCSInvestigator(config)
    results = investigator.investigate(
        target=args.target,
        scope=args.scope,
        output_dir=args.output or "reports"
    )
    
    print("✅ Investigation completed!")
    print(f"📊 Findings: {len(results.get('findings', []))}")
    print(f"🎯 IOCs: {len(results.get('iocs', []))}")
    print(f"📄 Report: {results.get('report_path', 'N/A')}")


def run_static_analysis(args, config):
    """Run static analysis"""
    print(f"📄 Performing static analysis on {args.file}...")
    
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
    
    results = {}
    
    # Initialize tool manager and system monitor
    tool_manager = ToolManager(config)
    system_monitor = SystemMonitor(config)
    
    # Install tools if requested
    if args.install_tools or args.all:
        print("📦 Installing external tools...")
        tool_results = tool_manager.install_all_tools()
        results.update({f"tool_{k}": v for k, v in tool_results.items()})
    
    # Configure tools if requested
    if args.configure_tools or args.all:
        print("⚙️ Configuring tools...")
        for tool_name in tool_manager.tool_configs.keys():
            if tool_manager.is_tool_installed(tool_name):
                success = tool_manager.configure_tool(tool_name)
                results[f"config_{tool_name}"] = success
    
    # Setup system monitoring
    if args.sysmon or args.all:
        print("🔍 Setting up Sysmon...")
        results["sysmon"] = tool_manager.configure_tool("sysmon")
    
    if args.etw or args.all:
        print("📊 Setting up ETW tracing...")
        results["etw"] = system_monitor.enable_etw_tracing()
    
    if args.powershell or args.all:
        print("💻 Setting up PowerShell logging...")
        results["powershell"] = system_monitor.enable_powershell_logging()
    
    print("✅ Environment setup completed!")
    for component, status in results.items():
        print(f"  {component}: {'✅' if status else '❌'}")


def run_monitor(args, config):
    """Run real-time monitoring"""
    system_monitor = SystemMonitor(config)
    
    if args.start:
        print("🔍 Starting real-time monitoring...")
        success = system_monitor.start_monitoring()
        if success:
            print("✅ Monitoring started successfully!")
            print("Press Ctrl+C to stop monitoring...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping monitoring...")
                system_monitor.stop_monitoring()
                print("✅ Monitoring stopped.")
        else:
            print("❌ Failed to start monitoring.")
    
    elif args.stop:
        print("🛑 Stopping monitoring...")
        system_monitor.stop_monitoring()
        print("✅ Monitoring stopped.")
    
    elif args.status:
        status = system_monitor.get_monitoring_status()
        print("📊 Monitoring Status:")
        print(f"  Active: {'✅' if status['monitoring'] else '❌'}")
        print(f"  Active monitors: {', '.join(status['active_monitors']) if status['active_monitors'] else 'None'}")
        print(f"  Callbacks: {status['callback_count']}")


def run_dashboard(args, config):
    """Run web dashboard."""
    try:
        from src.web.dashboard import URCSDashboard
        
        dashboard = URCSDashboard(config)
        print(f"🌐 Starting URCS Dashboard on http://{args.host}:{args.port}")
        print("📊 Dashboard features:")
        print("  - Real-time system monitoring")
        print("  - Live metrics and alerts")
        print("  - Interactive investigation controls")
        print("  - Performance charts")
        print("\n🔗 Open your browser and navigate to the URL above")
        print("🛑 Press Ctrl+C to stop the dashboard")
        
        dashboard.run(host=args.host, port=args.port, debug=args.debug)
        
    except ImportError as e:
        print(f"❌ Failed to import dashboard: {e}")
        print("💡 Install Flask and Flask-SocketIO: pip install flask flask-socketio")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")


if __name__ == "__main__":
    main()