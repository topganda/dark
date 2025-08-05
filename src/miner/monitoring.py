"""
System Monitoring
Monitors system resources, user activity, and provides data for resource management decisions.
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
import platform

class SystemMonitor:
    """
    System monitoring component that tracks:
    - CPU and GPU usage
    - Temperature monitoring
    - Battery status
    - User activity
    - System load
    - Memory and disk usage
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_activity_check = time.time()
        self.system_info = self._get_system_info()
        
        self.logger.info("System Monitor initialized")
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_gpu_usage(self) -> float:
        """Get current GPU usage percentage"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                # Return average GPU usage
                total_usage = sum(gpu.load * 100 for gpu in gpus)
                return total_usage / len(gpus)
            return 0.0
        except Exception as e:
            self.logger.debug(f"Could not get GPU usage: {e}")
            return 0.0
    
    def get_temperature(self) -> float:
        """Get current CPU temperature in Celsius"""
        try:
            if platform.system() == "Windows":
                return self._get_windows_temperature()
            elif platform.system() == "Linux":
                return self._get_linux_temperature()
            elif platform.system() == "Darwin":  # macOS
                return self._get_macos_temperature()
            else:
                return 0.0
        except Exception as e:
            self.logger.debug(f"Could not get temperature: {e}")
            return 0.0
    
    def get_power_consumption(self) -> float:
        """Get estimated power consumption in watts"""
        try:
            # This is a simplified estimation
            cpu_usage = self.get_cpu_usage()
            gpu_usage = self.get_gpu_usage()
            
            # Rough estimation based on usage
            cpu_power = cpu_usage * 0.5  # Assuming 50W max CPU
            gpu_power = gpu_usage * 0.8  # Assuming 80W max GPU
            
            return cpu_power + gpu_power
        except Exception as e:
            self.logger.error(f"Error calculating power consumption: {e}")
            return 0.0
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Get detailed battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'plugged': battery.power_plugged,
                    'percent': battery.percent,
                    'time_left': battery.secsleft,
                    'power_consumption': battery.power_plugged,
                    'charging': battery.power_plugged and battery.percent < 100
                }
            else:
                return {
                    'plugged': True,
                    'percent': 100,
                    'time_left': None,
                    'power_consumption': True,
                    'charging': False
                }
        except Exception as e:
            self.logger.error(f"Error getting battery info: {e}")
            return {
                'plugged': True,
                'percent': 100,
                'time_left': None,
                'power_consumption': True,
                'charging': False
            }
    
    def get_idle_time(self) -> float:
        """Get system idle time in seconds"""
        try:
            if platform.system() == "Windows":
                return self._get_windows_idle_time()
            elif platform.system() == "Linux":
                return self._get_linux_idle_time()
            elif platform.system() == "Darwin":
                return self._get_macos_idle_time()
            else:
                return time.time() - self.last_activity_check
        except Exception as e:
            self.logger.error(f"Error getting idle time: {e}")
            return 0.0
    
    def get_system_load(self) -> float:
        """Get system load average"""
        try:
            if platform.system() == "Linux":
                return psutil.getloadavg()[0]  # 1-minute load average
            else:
                # For Windows/macOS, use CPU usage as load indicator
                return self.get_cpu_usage()
        except Exception as e:
            self.logger.error(f"Error getting system load: {e}")
            return 0.0
    
    def is_task_manager_open(self) -> bool:
        """Check if Task Manager (or equivalent) is currently open"""
        try:
            task_manager_names = ['taskmgr', 'activity monitor', 'system monitor']
            
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name']:
                    proc_name = proc.info['name'].lower()
                    if any(name in proc_name for name in task_manager_names):
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking for task manager: {e}")
            return False
    
    def is_system_healthy(self) -> bool:
        """Check if system is healthy for mining"""
        try:
            # Check CPU temperature
            temp = self.get_temperature()
            if temp > 85:  # Celsius
                self.logger.warning(f"High CPU temperature: {temp}°C")
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning(f"High memory usage: {memory.percent}%")
                return False
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                self.logger.warning(f"Low disk space: {disk.percent}%")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': self.get_cpu_usage(),
                'gpu_usage': self.get_gpu_usage(),
                'temperature': self.get_temperature(),
                'power_consumption': self.get_power_consumption(),
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'disk_total': disk.total,
                'battery_info': self.get_battery_info(),
                'idle_time': self.get_idle_time(),
                'system_load': self.get_system_load(),
                'task_manager_open': self.is_task_manager_open(),
                'system_healthy': self.is_system_healthy()
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def _get_windows_temperature(self) -> float:
        """Get CPU temperature on Windows"""
        try:
            # This would require additional libraries like wmi or OpenHardwareMonitor
            # For now, return a placeholder
            return 45.0  # Placeholder temperature
        except Exception as e:
            self.logger.debug(f"Could not get Windows temperature: {e}")
            return 0.0
    
    def _get_linux_temperature(self) -> float:
        """Get CPU temperature on Linux"""
        try:
            # Try to read from thermal zone
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except Exception as e:
            self.logger.debug(f"Could not get Linux temperature: {e}")
            return 0.0
    
    def _get_macos_temperature(self) -> float:
        """Get CPU temperature on macOS"""
        try:
            # This would require additional libraries or system calls
            # For now, return a placeholder
            return 45.0  # Placeholder temperature
        except Exception as e:
            self.logger.debug(f"Could not get macOS temperature: {e}")
            return 0.0
    
    def _get_windows_idle_time(self) -> float:
        """Get idle time on Windows"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get last input time
            last_input = wintypes.DWORD()
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input))
            
            # Get current tick count
            current_tick = ctypes.windll.kernel32.GetTickCount()
            
            # Calculate idle time in seconds
            idle_time = (current_tick - last_input.value) / 1000.0
            return idle_time
        except Exception as e:
            self.logger.debug(f"Could not get Windows idle time: {e}")
            return time.time() - self.last_activity_check
    
    def _get_linux_idle_time(self) -> float:
        """Get idle time on Linux"""
        try:
            # Try to read from /proc/uptime
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.read().split()[0])
            
            # This is a simplified approach - in a real implementation,
            # you'd need to track user activity more precisely
            return time.time() - self.last_activity_check
        except Exception as e:
            self.logger.debug(f"Could not get Linux idle time: {e}")
            return time.time() - self.last_activity_check
    
    def _get_macos_idle_time(self) -> float:
        """Get idle time on macOS"""
        try:
            # This would require additional system calls
            # For now, return a simplified calculation
            return time.time() - self.last_activity_check
        except Exception as e:
            self.logger.debug(f"Could not get macOS idle time: {e}")
            return time.time() - self.last_activity_check
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_check = time.time()
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'connections': len(psutil.net_connections())
            }
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return {}
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Get process statistics"""
        try:
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
            
            # Get top processes by CPU usage
            top_cpu = sorted(processes, key=lambda x: x.info['cpu_percent'], reverse=True)[:5]
            
            # Get top processes by memory usage
            top_memory = sorted(processes, key=lambda x: x.info['memory_percent'], reverse=True)[:5]
            
            return {
                'total_processes': len(processes),
                'top_cpu_processes': [
                    {
                        'name': p.info['name'],
                        'pid': p.info['pid'],
                        'cpu_percent': p.info['cpu_percent']
                    } for p in top_cpu
                ],
                'top_memory_processes': [
                    {
                        'name': p.info['name'],
                        'pid': p.info['pid'],
                        'memory_percent': p.info['memory_percent']
                    } for p in top_memory
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting process stats: {e}")
            return {}