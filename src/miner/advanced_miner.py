"""
Advanced Crypto Miner with Intelligent Resource Management
Implements all the advanced features including adaptive CPU usage, task manager detection,
battery awareness, and intelligent resource allocation.
"""

import time
import threading
import psutil
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .resource_manager import ResourceManager
from .mining_engine import MiningEngine
from .monitoring import SystemMonitor
from .profitability import ProfitabilityCalculator

@dataclass
class MiningStats:
    """Mining statistics data class"""
    hashrate: float
    cpu_usage: float
    gpu_usage: float
    temperature: float
    power_consumption: float
    earnings: float
    uptime: float
    shares_accepted: int
    shares_rejected: int

class AdvancedMiner:
    """
    Advanced cryptocurrency miner with intelligent resource management.
    
    Features:
    - Adaptive CPU usage based on system state
    - Task Manager detection and response
    - Battery-aware mining
    - Idle detection and optimization
    - Real-time profitability calculation
    - Comprehensive monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.resource_manager = ResourceManager(config)
        self.mining_engine = MiningEngine(config)
        self.system_monitor = SystemMonitor()
        self.profitability_calc = ProfitabilityCalculator(config)
        
        # State management
        self.running = False
        self.stats = MiningStats(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.start_time = None
        
        # Threading
        self.mining_thread = None
        self.monitoring_thread = None
        self.resource_thread = None
        
        # Event flags
        self.stop_event = threading.Event()
        
        self.logger.info("Advanced Crypto Miner initialized")
    
    def start(self):
        """Start the mining operation"""
        if self.running:
            self.logger.warning("Miner is already running")
            return
        
        self.logger.info("🚀 Starting Advanced Crypto Miner...")
        self.running = True
        self.start_time = time.time()
        
        # Start resource management
        self.resource_manager.start()
        
        # Start monitoring
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True
        )
        self.monitoring_thread.start()
        
        # Start resource optimization
        self.resource_thread = threading.Thread(
            target=self._resource_optimization_loop,
            daemon=True
        )
        self.resource_thread.start()
        
        # Start mining engine
        self.mining_engine.start()
        
        self.logger.info("✅ Advanced Crypto Miner started successfully")
    
    def stop(self):
        """Stop the mining operation"""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping Advanced Crypto Miner...")
        self.running = False
        self.stop_event.set()
        
        # Stop components
        self.mining_engine.stop()
        self.resource_manager.stop()
        
        # Wait for threads to finish
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        if self.resource_thread:
            self.resource_thread.join(timeout=5)
        
        self.logger.info("✅ Advanced Crypto Miner stopped")
    
    def wait(self):
        """Wait for the miner to finish"""
        try:
            while self.running and not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        return {
            'running': self.running,
            'hashrate': self.stats.hashrate,
            'cpu_usage': self.stats.cpu_usage,
            'gpu_usage': self.stats.gpu_usage,
            'temperature': self.stats.temperature,
            'power_consumption': self.stats.power_consumption,
            'earnings': self.stats.earnings,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'shares_accepted': self.stats.shares_accepted,
            'shares_rejected': self.stats.shares_rejected,
            'resource_mode': self.resource_manager.get_current_mode(),
            'profitability': self.profitability_calc.get_current_profitability()
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Update system stats
                self.stats.cpu_usage = self.system_monitor.get_cpu_usage()
                self.stats.gpu_usage = self.system_monitor.get_gpu_usage()
                self.stats.temperature = self.system_monitor.get_temperature()
                self.stats.power_consumption = self.system_monitor.get_power_consumption()
                
                # Update mining stats
                mining_stats = self.mining_engine.get_stats()
                self.stats.hashrate = mining_stats.get('hashrate', 0)
                self.stats.shares_accepted = mining_stats.get('shares_accepted', 0)
                self.stats.shares_rejected = mining_stats.get('shares_rejected', 0)
                
                # Calculate earnings
                self.stats.earnings = self.profitability_calc.calculate_earnings(
                    self.stats.hashrate, 
                    time.time() - self.start_time
                )
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _resource_optimization_loop(self):
        """Resource optimization loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Check for task manager
                if self.system_monitor.is_task_manager_open():
                    self.logger.info("📊 Task Manager detected - reducing resource usage")
                    self.resource_manager.set_stealth_mode()
                
                # Check battery status
                battery_info = self.system_monitor.get_battery_info()
                if battery_info['plugged']:
                    if battery_info['percent'] > 90:
                        self.logger.info("🔌 High battery + charging - maximizing mining")
                        self.resource_manager.set_aggressive_mode()
                    else:
                        self.logger.info("🔌 Charging - moderate mining")
                        self.resource_manager.set_balanced_mode()
                else:
                    if battery_info['percent'] < 20:
                        self.logger.info("🔋 Low battery - minimal mining")
                        self.resource_manager.set_conservative_mode()
                    else:
                        self.logger.info("🔋 Battery power - balanced mining")
                        self.resource_manager.set_balanced_mode()
                
                # Check idle time
                idle_time = self.system_monitor.get_idle_time()
                if idle_time > 300:  # 5 minutes
                    self.logger.info("😴 Device idle - maximizing mining")
                    self.resource_manager.set_aggressive_mode()
                
                # Check system load
                system_load = self.system_monitor.get_system_load()
                if system_load > 80:
                    self.logger.info("⚡ High system load - reducing mining")
                    self.resource_manager.set_conservative_mode()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in resource optimization loop: {e}")
                time.sleep(30)
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update miner configuration"""
        self.config.update(new_config)
        self.resource_manager.update_config(new_config)
        self.mining_engine.update_config(new_config)
        self.profitability_calc.update_config(new_config)
        self.logger.info("Configuration updated")
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all operations"""
        self.logger.warning("🚨 Emergency stop triggered!")
        self.running = False
        self.stop_event.set()
        self.mining_engine.emergency_stop()
        self.resource_manager.emergency_stop()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'miner_healthy': self.running and not self.stop_event.is_set(),
            'resource_manager_healthy': self.resource_manager.is_healthy(),
            'mining_engine_healthy': self.mining_engine.is_healthy(),
            'system_healthy': self.system_monitor.is_system_healthy(),
            'temperature_safe': self.stats.temperature < 85,
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }