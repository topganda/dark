"""Platform Utilities for URCS Investigator Toolkit
Provides cross-platform compatibility for different operating systems.
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple

class PlatformUtils:
    """Cross-platform utilities for the URCS Investigator Toolkit."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_linux = self.system == "linux"
        self.is_macos = self.system == "darwin"
        
        # Platform-specific commands
        self.commands = self._get_platform_commands()
    
    def _get_platform_commands(self) -> Dict[str, str]:
        """Get platform-specific command mappings."""
        if self.is_windows:
            return {
                "process_list": "tasklist",
                "network_connections": "netstat",
                "registry_query": "reg query",
                "service_list": "sc query",
                "scheduled_tasks": "schtasks",
                "dns_lookup": "nslookup",
                "file_search": "dir",
                "powershell": "powershell"
            }
        elif self.is_linux:
            return {
                "process_list": "ps",
                "network_connections": "netstat",
                "registry_query": None,  # Not applicable
                "service_list": "systemctl",
                "scheduled_tasks": "crontab",
                "dns_lookup": "nslookup",
                "file_search": "find",
                "powershell": None  # Not available by default
            }
        elif self.is_macos:
            return {
                "process_list": "ps",
                "network_connections": "netstat",
                "registry_query": None,  # Not applicable
                "service_list": "launchctl",
                "scheduled_tasks": "crontab",
                "dns_lookup": "nslookup",
                "file_search": "find",
                "powershell": None  # Not available by default
            }
        else:
            return {}
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes."""
        processes = []
        
        try:
            if self.is_windows:
                # Use tasklist on Windows
                result = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH"], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and ',' in line:
                            parts = line.split(',')
                            if len(parts) >= 5:
                                processes.append({
                                    "name": parts[0].strip('"'),
                                    "pid": parts[1].strip('"'),
                                    "session": parts[2].strip('"'),
                                    "memory": parts[4].strip('"'),
                                    "platform": "windows"
                                })
            
            elif self.is_linux or self.is_macos:
                # Use ps on Unix-like systems
                result = subprocess.run(
                    ["ps", "aux"], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append({
                                "user": parts[0],
                                "pid": parts[1],
                                "cpu": parts[2],
                                "memory": parts[3],
                                "vsz": parts[4],
                                "rss": parts[5],
                                "tty": parts[6],
                                "stat": parts[7],
                                "start": parts[8],
                                "time": parts[9],
                                "command": ' '.join(parts[10:]),
                                "platform": "unix"
                            })
        
        except Exception as e:
            self.logger.error(f"Failed to get process list: {e}")
        
        return processes
    
    def get_network_connections(self) -> List[Dict[str, Any]]:
        """Get network connections."""
        connections = []
        
        try:
            if self.is_windows:
                # Use netstat on Windows
                result = subprocess.run(
                    ["netstat", "-ano"], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'TCP' in line or 'UDP' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                connections.append({
                                    "protocol": parts[0],
                                    "local_address": parts[1],
                                    "foreign_address": parts[2],
                                    "state": parts[3] if len(parts) > 3 else "",
                                    "pid": parts[4] if len(parts) > 4 else "",
                                    "platform": "windows"
                                })
            
            elif self.is_linux or self.is_macos:
                # Use netstat on Unix-like systems
                result = subprocess.run(
                    ["netstat", "-tuln"], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'tcp' in line or 'udp' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                connections.append({
                                    "protocol": parts[0],
                                    "recv_q": parts[1],
                                    "send_q": parts[2],
                                    "local_address": parts[3],
                                    "foreign_address": parts[4] if len(parts) > 4 else "",
                                    "state": parts[5] if len(parts) > 5 else "",
                                    "platform": "unix"
                                })
        
        except Exception as e:
            self.logger.error(f"Failed to get network connections: {e}")
        
        return connections
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get system services."""
        services = []
        
        try:
            if self.is_windows:
                # Use sc query on Windows
                result = subprocess.run(
                    ["sc", "query", "type=", "service", "state=", "all"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    current_service = {}
                    for line in result.stdout.strip().split('\n'):
                        line = line.strip()
                        if line.startswith('SERVICE_NAME:'):
                            if current_service:
                                services.append(current_service)
                            current_service = {"platform": "windows"}
                            current_service["name"] = line.split(':', 1)[1].strip()
                        elif line.startswith('DISPLAY_NAME:'):
                            current_service["display_name"] = line.split(':', 1)[1].strip()
                        elif line.startswith('STATE:'):
                            current_service["state"] = line.split(':', 1)[1].strip()
                        elif line.startswith('BINARY_PATH_NAME:'):
                            current_service["binary_path"] = line.split(':', 1)[1].strip()
                    
                    if current_service:
                        services.append(current_service)
            
            elif self.is_linux:
                # Use systemctl on Linux
                result = subprocess.run(
                    ["systemctl", "list-units", "--type=service", "--all"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if '.service' in line and not line.startswith('UNIT'):
                            parts = line.split()
                            if len(parts) >= 4:
                                services.append({
                                    "name": parts[0],
                                    "load": parts[1],
                                    "active": parts[2],
                                    "sub": parts[3],
                                    "description": ' '.join(parts[4:]) if len(parts) > 4 else "",
                                    "platform": "linux"
                                })
            
            elif self.is_macos:
                # Use launchctl on macOS
                result = subprocess.run(
                    ["launchctl", "list"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and not line.startswith('PID'):
                            parts = line.split()
                            if len(parts) >= 2:
                                services.append({
                                    "pid": parts[0],
                                    "status": parts[1],
                                    "name": ' '.join(parts[2:]) if len(parts) > 2 else "",
                                    "platform": "macos"
                                })
        
        except Exception as e:
            self.logger.error(f"Failed to get services: {e}")
        
        return services
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get scheduled tasks."""
        tasks = []
        
        try:
            if self.is_windows:
                # Use schtasks on Windows
                result = subprocess.run(
                    ["schtasks", "/query", "/fo", "csv", "/nh"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and ',' in line:
                            parts = line.split(',')
                            if len(parts) >= 7:
                                tasks.append({
                                    "task_name": parts[0].strip('"'),
                                    "next_run": parts[1].strip('"'),
                                    "status": parts[2].strip('"'),
                                    "logon_mode": parts[3].strip('"'),
                                    "last_run": parts[4].strip('"'),
                                    "last_result": parts[5].strip('"'),
                                    "creator": parts[6].strip('"'),
                                    "platform": "windows"
                                })
            
            elif self.is_linux or self.is_macos:
                # Use crontab on Unix-like systems
                result = subprocess.run(
                    ["crontab", "-l"], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 6:
                                tasks.append({
                                    "minute": parts[0],
                                    "hour": parts[1],
                                    "day": parts[2],
                                    "month": parts[3],
                                    "weekday": parts[4],
                                    "command": ' '.join(parts[5:]),
                                    "platform": "unix"
                                })
        
        except Exception as e:
            self.logger.error(f"Failed to get scheduled tasks: {e}")
        
        return tasks
    
    def dns_lookup(self, domain: str) -> Optional[str]:
        """Perform DNS lookup."""
        try:
            if self.commands["dns_lookup"]:
                result = subprocess.run(
                    [self.commands["dns_lookup"], domain], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    # Parse the output to extract IP address
                    for line in result.stdout.split('\n'):
                        if 'Address:' in line and domain not in line:
                            return line.split('Address:')[1].strip()
            
            return None
        
        except Exception as e:
            self.logger.error(f"DNS lookup failed for {domain}: {e}")
            return None
    
    def find_files(self, pattern: str, path: str = ".") -> List[str]:
        """Find files matching pattern."""
        files = []
        
        try:
            if self.is_windows:
                # Use dir on Windows
                result = subprocess.run(
                    ["dir", "/s", "/b", f"{path}\\*{pattern}*"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            elif self.is_linux or self.is_macos:
                # Use find on Unix-like systems
                result = subprocess.run(
                    ["find", path, "-name", f"*{pattern}*", "-type", "f"], 
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        except Exception as e:
            self.logger.error(f"File search failed for pattern {pattern}: {e}")
        
        return files
    
    def run_powershell(self, command: str) -> Tuple[bool, str, str]:
        """Run PowerShell command (Windows only)."""
        if not self.is_windows:
            return False, "", "PowerShell not available on this platform"
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", command], 
                capture_output=True, text=True, timeout=60
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        
        except Exception as e:
            return False, "", str(e)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "platform": self.system,
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": sys.version,
            "is_windows": self.is_windows,
            "is_linux": self.is_linux,
            "is_macos": self.is_macos
        }
    
    def is_command_available(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                ["which", command] if not self.is_windows else ["where", command], 
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False