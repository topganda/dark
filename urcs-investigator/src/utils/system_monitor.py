"""System Monitor for URCS Investigator Toolkit
Provides real-time monitoring of system activities for URCS detection.
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
import psutil
try:
    import winreg
    import win32api
    import win32con
    import win32security
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import socket


class SystemMonitor:
    """Real-time system monitoring for URCS detection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitors = {}
        self.callbacks = {}
        
        # Monitoring configurations
        self.monitor_configs = {
            "process": {
                "enabled": True,
                "interval": 5,  # seconds
                "suspicious_processes": [
                    "Chrome_update.exe",
                    "gupdatem.exe",
                    "algfzpoe.exe",
                    "Ddriver.exe",
                    "ctfmon.exe"
                ]
            },
            "registry": {
                "enabled": True,
                "interval": 10,  # seconds
                "suspicious_keys": [
                    r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\ctfmon",
                    r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\gupdatem",
                    r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\ctfmon"
                ]
            },
            "network": {
                "enabled": True,
                "interval": 3,  # seconds
                "suspicious_domains": [
                    "gulf.moneroocean.stream",
                    "api.ipify.org",
                    "moneroocean.stream"
                ],
                "suspicious_ports": [10032, 3333, 14444]
            },
            "file_system": {
                "enabled": True,
                "interval": 15,  # seconds
                "suspicious_paths": [
                    r"C:\Windows\System32\spool\drivers\color",
                    r"C:\Windows\Temp",
                    r"%TEMP%"
                ]
            },
            "performance": {
                "enabled": True,
                "interval": 2,  # seconds
                "cpu_threshold": 70,
                "memory_threshold": 80
            }
        }
    
    def start_monitoring(self) -> bool:
        """Start all monitoring threads."""
        if self.monitoring:
            self.logger.warning("Monitoring already started")
            return True
        
        self.logger.info("Starting system monitoring")
        self.monitoring = True
        
        try:
            # Start individual monitors
            for monitor_name, config in self.monitor_configs.items():
                if config.get("enabled", False):
                    self._start_monitor(monitor_name, config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop all monitoring threads."""
        self.logger.info("Stopping system monitoring")
        self.monitoring = False
        
        # Stop all monitor threads
        for monitor_name, thread in self.monitors.items():
            if thread and thread.is_alive():
                thread.join(timeout=5)
        
        self.monitors.clear()
    
    def _start_monitor(self, monitor_name: str, config: Dict[str, Any]):
        """Start a specific monitor thread."""
        if monitor_name == "process":
            thread = threading.Thread(target=self._monitor_processes, args=(config,), daemon=True)
        elif monitor_name == "registry":
            thread = threading.Thread(target=self._monitor_registry, args=(config,), daemon=True)
        elif monitor_name == "network":
            thread = threading.Thread(target=self._monitor_network, args=(config,), daemon=True)
        elif monitor_name == "file_system":
            thread = threading.Thread(target=self._monitor_file_system, args=(config,), daemon=True)
        elif monitor_name == "performance":
            thread = threading.Thread(target=self._monitor_performance, args=(config,), daemon=True)
        else:
            self.logger.error(f"Unknown monitor: {monitor_name}")
            return
        
        thread.start()
        self.monitors[monitor_name] = thread
        self.logger.info(f"Started {monitor_name} monitor")
    
    def _monitor_processes(self, config: Dict[str, Any]):
        """Monitor for suspicious processes."""
        interval = config.get("interval", 5)
        suspicious_processes = config.get("suspicious_processes", [])
        
        while self.monitoring:
            try:
                # Get all running processes
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info.get('name', '').lower()
                        cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
                        exe_path = proc_info.get('exe', '').lower()
                        
                        # Check for suspicious processes
                        for suspicious in suspicious_processes:
                            if (suspicious.lower() in proc_name or 
                                suspicious.lower() in cmdline or
                                suspicious.lower() in exe_path):
                                
                                self._trigger_alert("process", {
                                    "type": "suspicious_process",
                                    "process_name": proc_name,
                                    "pid": proc_info.get('pid'),
                                    "cmdline": cmdline,
                                    "exe_path": exe_path,
                                    "suspicious_pattern": suspicious,
                                    "timestamp": datetime.now().isoformat()
                                })
                        
                        # Check for process injection indicators
                        if self._check_process_injection(proc_info):
                            self._trigger_alert("process", {
                                "type": "process_injection",
                                "process_name": proc_name,
                                "pid": proc_info.get('pid'),
                                "indicators": "Possible process injection detected",
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Process monitoring error: {e}")
                time.sleep(interval)
    
    def _monitor_registry(self, config: Dict[str, Any]):
        """Monitor for suspicious registry changes."""
        interval = config.get("interval", 10)
        suspicious_keys = config.get("suspicious_keys", [])
        
        # Store initial values
        registry_state = {}
        
        while self.monitoring:
            try:
                for key_path in suspicious_keys:
                    try:
                        current_value = self._get_registry_value(key_path)
                        
                        if key_path not in registry_state:
                            registry_state[key_path] = current_value
                        elif registry_state[key_path] != current_value:
                            # Registry value changed
                            self._trigger_alert("registry", {
                                "type": "registry_change",
                                "key_path": key_path,
                                "old_value": registry_state[key_path],
                                "new_value": current_value,
                                "timestamp": datetime.now().isoformat()
                            })
                            registry_state[key_path] = current_value
                        
                        # Check for suspicious values
                        if current_value and self._is_suspicious_registry_value(current_value):
                            self._trigger_alert("registry", {
                                "type": "suspicious_registry",
                                "key_path": key_path,
                                "value": current_value,
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    except Exception as e:
                        self.logger.debug(f"Registry monitoring error for {key_path}: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Registry monitoring error: {e}")
                time.sleep(interval)
    
    def _monitor_network(self, config: Dict[str, Any]):
        """Monitor for suspicious network connections."""
        interval = config.get("interval", 3)
        suspicious_domains = config.get("suspicious_domains", [])
        suspicious_ports = config.get("suspicious_ports", [])
        
        while self.monitoring:
            try:
                # Get network connections
                connections = psutil.net_connections()
                
                for conn in connections:
                    try:
                        if conn.status == 'ESTABLISHED':
                            # Check for suspicious domains
                            if conn.raddr:
                                remote_ip = conn.raddr.ip
                                remote_port = conn.raddr.port
                                
                                # Check suspicious ports
                                if remote_port in suspicious_ports:
                                    self._trigger_alert("network", {
                                        "type": "suspicious_port",
                                        "remote_ip": remote_ip,
                                        "remote_port": remote_port,
                                        "local_port": conn.laddr.port if conn.laddr else None,
                                        "timestamp": datetime.now().isoformat()
                                    })
                                
                                # Check for suspicious domains (DNS resolution)
                                for domain in suspicious_domains:
                                    if self._is_domain_resolved(domain, remote_ip):
                                        self._trigger_alert("network", {
                                            "type": "suspicious_domain",
                                            "domain": domain,
                                            "remote_ip": remote_ip,
                                            "remote_port": remote_port,
                                            "timestamp": datetime.now().isoformat()
                                        })
                    
                    except Exception as e:
                        continue
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Network monitoring error: {e}")
                time.sleep(interval)
    
    def _monitor_file_system(self, config: Dict[str, Any]):
        """Monitor for suspicious file system changes."""
        interval = config.get("interval", 15)
        suspicious_paths = config.get("suspicious_paths", [])
        
        while self.monitoring:
            try:
                for path_pattern in suspicious_paths:
                    # Expand environment variables
                    expanded_path = os.path.expandvars(path_pattern)
                    
                    if os.path.exists(expanded_path):
                        # Check for suspicious files
                        for root, dirs, files in os.walk(expanded_path):
                            for file in files:
                                if self._is_suspicious_file(file):
                                    file_path = os.path.join(root, file)
                                    self._trigger_alert("file_system", {
                                        "type": "suspicious_file",
                                        "file_path": file_path,
                                        "file_name": file,
                                        "timestamp": datetime.now().isoformat()
                                    })
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"File system monitoring error: {e}")
                time.sleep(interval)
    
    def _monitor_performance(self, config: Dict[str, Any]):
        """Monitor system performance for anomalies."""
        interval = config.get("interval", 2)
        cpu_threshold = config.get("cpu_threshold", 70)
        memory_threshold = config.get("memory_threshold", 80)
        
        # Track performance history
        cpu_history = []
        memory_history = []
        
        while self.monitoring:
            try:
                # Get current performance metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                cpu_history.append(cpu_percent)
                memory_history.append(memory_percent)
                
                # Keep only last 10 measurements
                if len(cpu_history) > 10:
                    cpu_history.pop(0)
                if len(memory_history) > 10:
                    memory_history.pop(0)
                
                # Check for anomalies
                if len(cpu_history) >= 5:
                    # Check for sudden CPU drops (Task Manager detection)
                    if cpu_history[-1] < 10 and max(cpu_history[-5:-1]) > cpu_threshold:
                        self._trigger_alert("performance", {
                            "type": "cpu_throttling",
                            "current_cpu": cpu_percent,
                            "previous_cpu": max(cpu_history[-5:-1]),
                            "description": "Possible Task Manager detection",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Check for high CPU usage
                    if cpu_percent > cpu_threshold:
                        self._trigger_alert("performance", {
                            "type": "high_cpu_usage",
                            "cpu_percent": cpu_percent,
                            "threshold": cpu_threshold,
                            "timestamp": datetime.now().isoformat()
                        })
                
                # Check memory usage
                if memory_percent > memory_threshold:
                    self._trigger_alert("performance", {
                        "type": "high_memory_usage",
                        "memory_percent": memory_percent,
                        "threshold": memory_threshold,
                        "timestamp": datetime.now().isoformat()
                    })
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(interval)
    
    def _check_process_injection(self, proc_info: Dict[str, Any]) -> bool:
        """Check for process injection indicators."""
        try:
            # Check for suspicious DLLs
            proc = psutil.Process(proc_info.get('pid'))
            dlls = proc.memory_maps()
            
            suspicious_dlls = [
                "kernel32.dll",
                "ntdll.dll",
                "user32.dll"
            ]
            
            # Check for unusual DLL loading patterns
            dll_count = len(dlls)
            if dll_count > 100:  # Suspicious number of DLLs
                return True
            
            # Check for suspicious memory regions
            memory_info = proc.memory_info()
            if memory_info.rss > 500 * 1024 * 1024:  # > 500MB
                return True
            
            return False
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _get_registry_value(self, key_path: str) -> Optional[str]:
        """Get registry value."""
        if not WINDOWS_AVAILABLE:
            self.logger.warning("Windows registry access not available on this platform")
            return None
            
        try:
            # Parse registry path
            if key_path.startswith("HKCU\\"):
                hive = winreg.HKEY_CURRENT_USER
                subkey = key_path[6:]
            elif key_path.startswith("HKLM\\"):
                hive = winreg.HKEY_LOCAL_MACHINE
                subkey = key_path[6:]
            else:
                return None
            
            # Open registry key
            key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            
            return value
            
        except Exception:
            return None
    
    def _is_suspicious_registry_value(self, value: str) -> bool:
        """Check if registry value is suspicious."""
        suspicious_patterns = [
            "chrome_update.exe",
            "gupdatem",
            "algfzpoe.exe",
            "ddriver",
            "ctfmon",
            "system32\\spool\\drivers\\color"
        ]
        
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in suspicious_patterns)
    
    def _is_domain_resolved(self, domain: str, ip: str) -> bool:
        """Check if domain resolves to IP."""
        try:
            # Simple DNS resolution check
            resolved_ip = socket.gethostbyname(domain)
            return resolved_ip == ip
        except Exception:
            return False
    
    def _is_suspicious_file(self, filename: str) -> bool:
        """Check if file is suspicious."""
        suspicious_patterns = [
            "chrome_update.exe",
            "gupdatem",
            "algfzpoe.exe",
            "ddriver",
            "ctfmon"
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in suspicious_patterns)
    
    def _trigger_alert(self, monitor_type: str, alert_data: Dict[str, Any]):
        """Trigger an alert."""
        alert_data["monitor_type"] = monitor_type
        alert_data["severity"] = "high"
        
        # Log alert
        self.logger.warning(f"URCS Alert: {alert_data}")
        
        # Call registered callbacks
        if monitor_type in self.callbacks:
            for callback in self.callbacks[monitor_type]:
                try:
                    callback(alert_data)
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")
    
    def register_callback(self, monitor_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for alerts."""
        if monitor_type not in self.callbacks:
            self.callbacks[monitor_type] = []
        
        self.callbacks[monitor_type].append(callback)
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status."""
        return {
            "monitoring": self.monitoring,
            "active_monitors": list(self.monitors.keys()),
            "monitor_configs": self.monitor_configs,
            "callback_count": {k: len(v) for k, v in self.callbacks.items()}
        }
    
    def enable_powershell_logging(self) -> bool:
        """Enable PowerShell ScriptBlock logging."""
        try:
            # PowerShell ScriptBlock logging configuration
            scriptblock_config = """# PowerShell ScriptBlock Logging Configuration
# Run as Administrator

# Enable ScriptBlock Logging
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging" -Name "EnableScriptBlockLogging" -Value 1

# Enable Module Logging
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging" -Name "EnableModuleLogging" -Value 1

# Enable Transcription
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription" -Name "EnableTranscripting" -Value 1
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription" -Name "OutputDirectory" -Value "C:\\PowerShell_Logs"

Write-Host "PowerShell logging enabled successfully"
"""
            
            # Save configuration script
            script_path = Path("tools") / "powershell_logging_config.ps1"
            script_path.parent.mkdir(exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(scriptblock_config)
            
            self.logger.info(f"PowerShell logging configuration saved to {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable PowerShell logging: {e}")
            return False
    
    def enable_etw_tracing(self) -> bool:
        """Enable ETW tracing for URCS detection."""
        try:
            # ETW tracing configuration
            etw_config = """# ETW Tracing Configuration for URCS Detection
# Run as Administrator

# Create ETW session for URCS monitoring
logman create trace "URCS_Tracing" -ow -o "C:\\ETW_Logs\\urcs_trace.etl" -f bincirc -max 2048 -mode Circular

# Add providers
logman add counter "URCS_Tracing" -si 5 -v mmddhhmm -f csv -o "C:\\ETW_Logs\\urcs_perf.csv" "\\Processor(_Total)\\% Processor Time"
logman add counter "URCS_Tracing" -si 5 -v mmddhhmm -f csv -o "C:\\ETW_Logs\\urcs_perf.csv" "\\Memory\\Available MBytes"

# Add Windows Kernel Process provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-Process

# Add Windows Kernel Registry provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-Registry

# Add Windows Kernel File provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-File

# Start tracing
logman start "URCS_Tracing"

Write-Host "ETW tracing enabled successfully"
"""
            
            # Save configuration script
            script_path = Path("tools") / "etw_tracing_config.ps1"
            script_path.parent.mkdir(exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(etw_config)
            
            self.logger.info(f"ETW tracing configuration saved to {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable ETW tracing: {e}")
            return False