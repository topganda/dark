#!/usr/bin/env python3
"""
Advanced Crypto Mining Suite - Main Application
A comprehensive, legal cryptocurrency mining solution with intelligent resource management.
"""

import argparse
import sys
import os
import signal
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.miner import AdvancedMiner
from src.dashboard import Dashboard
from src.service import MiningService
from src.utils.logger import setup_logging
from src.utils.config import ConfigManager

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutting down Advanced Crypto Mining Suite...")
    if hasattr(signal_handler, 'miner'):
        signal_handler.miner.stop()
    sys.exit(0)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced Crypto Mining Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run          # Start mining in foreground
  python main.py start        # Start mining as service
  python main.py stop         # Stop mining service
  python main.py dashboard    # Open web dashboard
  python main.py setup        # Run setup wizard
  python main.py status       # Show current status
        """
    )
    
    parser.add_argument('command', choices=[
        'run', 'start', 'stop', 'restart', 'status', 
        'dashboard', 'setup', 'config', 'logs'
    ], help='Command to execute')
    
    parser.add_argument('--config', '-c', 
                       help='Path to configuration file')
    parser.add_argument('--daemon', '-d', action='store_true',
                       help='Run in daemon mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--port', '-p', type=int, default=8080,
                       help='Dashboard port (default: 8080)')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    config = config_manager.load_config()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.command == 'run':
            run_miner(config, args)
        elif args.command == 'start':
            start_service(config, args)
        elif args.command == 'stop':
            stop_service()
        elif args.command == 'restart':
            restart_service(config, args)
        elif args.command == 'status':
            show_status()
        elif args.command == 'dashboard':
            start_dashboard(config, args)
        elif args.command == 'setup':
            run_setup()
        elif args.command == 'config':
            show_config(config)
        elif args.command == 'logs':
            show_logs()
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

def run_miner(config, args):
    """Run the miner in foreground mode"""
    print("🚀 Starting Advanced Crypto Mining Suite...")
    print("📊 Intelligent Resource Management: ENABLED")
    print("🛡️  Legal Mining Only: CONFIRMED")
    print("=" * 50)
    
    miner = AdvancedMiner(config)
    signal_handler.miner = miner
    
    try:
        miner.start()
        print("✅ Mining started successfully!")
        print("🌐 Dashboard available at: http://localhost:8080")
        print("📱 Press Ctrl+C to stop")
        
        # Keep running
        miner.wait()
        
    except Exception as e:
        print(f"❌ Failed to start miner: {e}")
        sys.exit(1)

def start_service(config, args):
    """Start the mining service"""
    service = MiningService(config)
    
    if args.daemon:
        print("🔄 Starting mining service in daemon mode...")
        service.start_daemon()
    else:
        print("🔄 Starting mining service...")
        service.start()
    
    print("✅ Mining service started successfully!")

def stop_service():
    """Stop the mining service"""
    service = MiningService()
    print("🛑 Stopping mining service...")
    service.stop()
    print("✅ Mining service stopped!")

def restart_service(config, args):
    """Restart the mining service"""
    print("🔄 Restarting mining service...")
    stop_service()
    start_service(config, args)

def show_status():
    """Show current mining status"""
    service = MiningService()
    status = service.get_status()
    
    print("📊 Mining Status:")
    print("=" * 30)
    print(f"Service: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
    print(f"Uptime: {status.get('uptime', 'N/A')}")
    print(f"Hashrate: {status.get('hashrate', 'N/A')}")
    print(f"CPU Usage: {status.get('cpu_usage', 'N/A')}%")
    print(f"GPU Usage: {status.get('gpu_usage', 'N/A')}%")
    print(f"Temperature: {status.get('temperature', 'N/A')}°C")
    print(f"Earnings: {status.get('earnings', 'N/A')}")

def start_dashboard(config, args):
    """Start the web dashboard"""
    print(f"🌐 Starting dashboard on port {args.port}...")
    dashboard = Dashboard(config, port=args.port)
    dashboard.start()

def run_setup():
    """Run the setup wizard"""
    from src.setup import SetupWizard
    print("🔧 Running Advanced Crypto Mining Suite Setup Wizard...")
    wizard = SetupWizard()
    wizard.run()

def show_config(config):
    """Show current configuration"""
    print("⚙️  Current Configuration:")
    print("=" * 30)
    print(f"Mining Algorithm: {config.get('mining', {}).get('algorithm', 'N/A')}")
    print(f"CPU Threads: {config.get('mining', {}).get('cpu_threads', 'N/A')}")
    print(f"GPU Enabled: {config.get('mining', {}).get('gpu_enabled', 'N/A')}")
    print(f"Pool URL: {config.get('mining', {}).get('pool_url', 'N/A')}")
    print(f"Wallet: {config.get('mining', {}).get('wallet', 'N/A')[:20]}...")

def show_logs():
    """Show recent logs"""
    log_file = "logs/miner.log"
    if os.path.exists(log_file):
        print("📋 Recent Logs:")
        print("=" * 30)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-20:]:  # Show last 20 lines
                print(line.strip())
    else:
        print("📋 No logs found")

if __name__ == "__main__":
    main()