"""
Mining Service
Manages the mining process as a system service with auto-restart capabilities.
"""

import time
import threading
import logging
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from ..miner import AdvancedMiner
from ..utils.config import ConfigManager

class MiningService:
    """
    Service manager for the Advanced Crypto Mining Suite.
    Handles starting, stopping, and monitoring the mining process.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.load_config()
        
        # Service state
        self.running = False
        self.miner = None
        self.service_thread = None
        self.stop_event = threading.Event()
        
        # Service management
        self.restart_count = 0
        self.max_restart_attempts = self.config.get('advanced', {}).get('max_restart_attempts', 3)
        self.restart_delay = self.config.get('advanced', {}).get('restart_delay', 30)
        self.auto_restart = self.config.get('advanced', {}).get('auto_restart', True)
        
        # Status tracking
        self.start_time = None
        self.last_restart_time = None
        self.status_file = Path("logs/service_status.json")
        
        self.logger.info("Mining Service initialized")
    
    def start(self) -> bool:
        """Start the mining service"""
        if self.running:
            self.logger.warning("Mining service is already running")
            return True
        
        self.logger.info("🚀 Starting Mining Service...")
        self.running = True
        self.start_time = time.time()
        self.stop_event.clear()
        
        # Start service thread
        self.service_thread = threading.Thread(
            target=self._service_loop,
            daemon=True
        )
        self.service_thread.start()
        
        # Update status
        self._update_status()
        
        self.logger.info("✅ Mining Service started successfully")
        return True
    
    def start_daemon(self) -> bool:
        """Start the mining service in daemon mode"""
        self.logger.info("🔄 Starting Mining Service in daemon mode...")
        
        # Fork process (Unix-like systems)
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                self.logger.info(f"Mining service daemon started with PID: {pid}")
                return True
            else:
                # Child process
                os.setsid()  # Create new session
                return self.start()
        except OSError:
            # Fallback for non-Unix systems
            self.logger.warning("Daemon mode not supported on this platform, starting normally")
            return self.start()
    
    def stop(self) -> bool:
        """Stop the mining service"""
        if not self.running:
            self.logger.warning("Mining service is not running")
            return True
        
        self.logger.info("🛑 Stopping Mining Service...")
        self.running = False
        self.stop_event.set()
        
        # Stop miner
        if self.miner:
            self.miner.stop()
            self.miner = None
        
        # Wait for service thread
        if self.service_thread:
            self.service_thread.join(timeout=10)
        
        # Update status
        self._update_status()
        
        self.logger.info("✅ Mining Service stopped")
        return True
    
    def restart(self) -> bool:
        """Restart the mining service"""
        self.logger.info("🔄 Restarting Mining Service...")
        
        if self.stop():
            time.sleep(2)  # Brief pause
            return self.start()
        else:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
            else:
                status = {}
            
            # Add current runtime information
            if self.start_time:
                status['uptime'] = time.time() - self.start_time
                status['uptime_formatted'] = self._format_uptime(status['uptime'])
            
            status['running'] = self.running
            status['restart_count'] = self.restart_count
            status['auto_restart'] = self.auto_restart
            
            # Add miner status if available
            if self.miner:
                status['miner_status'] = self.miner.get_stats()
                status['miner_health'] = self.miner.get_health_status()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return {
                'running': self.running,
                'error': str(e)
            }
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        if not self.running:
            return False
        
        if self.miner:
            return self.miner.is_healthy()
        
        return True
    
    def _service_loop(self):
        """Main service loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Start miner if not running
                if not self.miner or not self.miner.is_healthy():
                    self._start_miner()
                
                # Monitor miner health
                if self.miner and self.miner.is_healthy():
                    # Reset restart count on successful operation
                    self.restart_count = 0
                    
                    # Update status periodically
                    self._update_status()
                    
                    # Sleep for monitoring interval
                    time.sleep(30)
                else:
                    # Miner is not healthy, handle restart
                    self._handle_miner_failure()
                    
            except Exception as e:
                self.logger.error(f"Error in service loop: {e}")
                self._handle_miner_failure()
    
    def _start_miner(self) -> bool:
        """Start the mining process"""
        try:
            if self.miner:
                self.miner.stop()
            
            self.logger.info("Starting Advanced Crypto Miner...")
            self.miner = AdvancedMiner(self.config)
            self.miner.start()
            
            self.logger.info("✅ Advanced Crypto Miner started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start miner: {e}")
            return False
    
    def _handle_miner_failure(self):
        """Handle miner failure and restart if needed"""
        self.logger.warning("Miner failure detected")
        
        if not self.auto_restart:
            self.logger.error("Auto-restart disabled, stopping service")
            self.running = False
            return
        
        if self.restart_count >= self.max_restart_attempts:
            self.logger.error(f"Maximum restart attempts ({self.max_restart_attempts}) reached")
            self.running = False
            return
        
        self.restart_count += 1
        self.last_restart_time = time.time()
        
        self.logger.info(f"Restarting miner (attempt {self.restart_count}/{self.max_restart_attempts})")
        
        # Stop current miner
        if self.miner:
            self.miner.stop()
            self.miner = None
        
        # Wait before restart
        time.sleep(self.restart_delay)
        
        # Try to restart
        if not self._start_miner():
            self.logger.error("Failed to restart miner")
    
    def _update_status(self):
        """Update service status file"""
        try:
            status = {
                'running': self.running,
                'start_time': self.start_time,
                'restart_count': self.restart_count,
                'last_restart_time': self.last_restart_time,
                'auto_restart': self.auto_restart,
                'max_restart_attempts': self.max_restart_attempts,
                'restart_delay': self.restart_delay,
                'last_update': time.time()
            }
            
            # Ensure logs directory exists
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get detailed service information"""
        status = self.get_status()
        
        return {
            'service': {
                'running': self.running,
                'uptime': status.get('uptime', 0),
                'uptime_formatted': status.get('uptime_formatted', 'N/A'),
                'restart_count': self.restart_count,
                'auto_restart': self.auto_restart,
                'max_restart_attempts': self.max_restart_attempts,
                'restart_delay': self.restart_delay
            },
            'miner': status.get('miner_status', {}),
            'health': status.get('miner_health', {}),
            'configuration': {
                'algorithm': self.config.get('mining', {}).get('algorithm', 'N/A'),
                'pool_url': self.config.get('mining', {}).get('pool_url', 'N/A'),
                'worker_name': self.config.get('mining', {}).get('worker_name', 'N/A')
            }
        }
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all operations"""
        self.logger.warning("🚨 Emergency stop triggered!")
        
        if self.miner:
            self.miner.emergency_stop()
        
        self.running = False
        self.stop_event.set()
        
        self._update_status()
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update service configuration"""
        try:
            self.config.update(new_config)
            self.config_manager.update_config(new_config)
            
            # Update service parameters
            self.max_restart_attempts = new_config.get('advanced', {}).get('max_restart_attempts', self.max_restart_attempts)
            self.restart_delay = new_config.get('advanced', {}).get('restart_delay', self.restart_delay)
            self.auto_restart = new_config.get('advanced', {}).get('auto_restart', self.auto_restart)
            
            # Update miner configuration if running
            if self.miner:
                self.miner.update_config(new_config)
            
            self.logger.info("Service configuration updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating service configuration: {e}")
            return False
    
    def get_logs(self, lines: int = 100) -> str:
        """Get recent service logs"""
        try:
            log_file = Path("logs/miner.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines_list = f.readlines()
                    return ''.join(lines_list[-lines:])
            else:
                return "No log file found"
        except Exception as e:
            return f"Error reading logs: {e}"
    
    def cleanup(self):
        """Clean up service resources"""
        self.logger.info("Cleaning up service resources...")
        
        if self.miner:
            self.miner.stop()
            self.miner = None
        
        self.running = False
        self.stop_event.set()
        
        # Remove status file
        if self.status_file.exists():
            try:
                self.status_file.unlink()
            except Exception as e:
                self.logger.error(f"Error removing status file: {e}")
        
        self.logger.info("Service cleanup completed")