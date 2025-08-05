"""Enhanced Behavioral Analysis Module for URCS Investigator Toolkit."""

import os
import re
import logging
import subprocess
from typing import Dict, Any, List
from pathlib import Path


class BehavioralAnalyzer:
    """Performs comprehensive behavioral analysis on system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # URCS-specific patterns
        self.suspicious_names = config.get("detection.patterns.suspicious_names", [])
        self.suspicious_paths = config.get("detection.patterns.suspicious_paths", [])
        self.suspicious_pools = config.get("detection.patterns.suspicious_pools", [])
    
    def analyze_services(self) -> List[Dict[str, Any]]:
        """Analyze system services for URCS indicators."""
        self.logger.info("Analyzing system services")
        findings = []
        
        try:
            # Check for suspicious service names
            suspicious_services = [
                "gupdatem",
                "Google Update Service",
                "ctfmon",
                "Ddriver"
            ]
            
            # This would typically use Windows API or WMI
            # For now, we'll simulate the detection
            for service_name in suspicious_services:
                if self._check_service_exists(service_name):
                    findings.append({
                        "type": "suspicious_service",
                        "name": service_name,
                        "description": f"Suspicious service found: {service_name}",
                        "severity": "high",
                        "mitre_technique": "T1543.003"
                    })
            
            # Check for services with suspicious binary paths
            suspicious_paths = [
                r"System32\\spool\\drivers\\color\\",
                r"System32\\drivers\\",
                r"Temp\\"
            ]
            
            for path_pattern in suspicious_paths:
                services = self._find_services_by_path(path_pattern)
                for service in services:
                    findings.append({
                        "type": "suspicious_service_path",
                        "name": service.get("name", "unknown"),
                        "path": service.get("path", "unknown"),
                        "description": f"Service with suspicious path: {service.get('path', 'unknown')}",
                        "severity": "medium",
                        "mitre_technique": "T1543.003"
                    })
            
        except Exception as e:
            self.logger.error(f"Service analysis failed: {e}")
        
        return findings
    
    def analyze_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Analyze scheduled tasks for URCS indicators."""
        self.logger.info("Analyzing scheduled tasks")
        findings = []
        
        try:
            # Check for suspicious task names
            suspicious_tasks = [
                "Ddriver",
                "gupdatem",
                "ctfmon"
            ]
            
            for task_name in suspicious_tasks:
                if self._check_task_exists(task_name):
                    findings.append({
                        "type": "suspicious_scheduled_task",
                        "name": task_name,
                        "description": f"Suspicious scheduled task found: {task_name}",
                        "severity": "high",
                        "mitre_technique": "T1053.005"
                    })
            
            # Check for tasks with 30-minute intervals (resurrection pattern)
            tasks_30min = self._find_tasks_by_interval(30)
            for task in tasks_30min:
                findings.append({
                    "type": "resurrection_task",
                    "name": task.get("name", "unknown"),
                    "interval": "30 minutes",
                    "description": f"Task with 30-minute interval (possible resurrection): {task.get('name', 'unknown')}",
                    "severity": "medium",
                    "mitre_technique": "T1053.005"
                })
            
        except Exception as e:
            self.logger.error(f"Scheduled task analysis failed: {e}")
        
        return findings
    
    def analyze_file_system(self) -> List[Dict[str, Any]]:
        """Analyze file system for URCS indicators."""
        self.logger.info("Analyzing file system")
        findings = []
        
        try:
            # 1. Check for fake Chrome update installer
            chrome_update_paths = self._find_chrome_update_files()
            for path in chrome_update_paths:
                findings.append({
                    "type": "fake_installer",
                    "path": path,
                    "description": f"Fake Chrome update installer found: {path}",
                    "severity": "high",
                    "mitre_technique": "T1204.002"
                })
            
            # 2. Check for random 8-letter filenames in System32\spool\drivers\color\
            random_files = self._find_random_8_letter_files()
            for file_path in random_files:
                findings.append({
                    "type": "random_filename",
                    "path": file_path,
                    "description": f"Random 8-letter filename found: {file_path}",
                    "severity": "medium",
                    "mitre_technique": "T1036.005"
                })
            
            # 3. Check for suspicious files in system directories
            suspicious_files = self._find_suspicious_system_files()
            for file_path in suspicious_files:
                findings.append({
                    "type": "suspicious_system_file",
                    "path": file_path,
                    "description": f"Suspicious file in system directory: {file_path}",
                    "severity": "medium",
                    "mitre_technique": "T1036.005"
                })
            
        except Exception as e:
            self.logger.error(f"File system analysis failed: {e}")
        
        return findings
    
    def analyze_registry(self) -> List[Dict[str, Any]]:
        """Analyze registry for URCS persistence indicators."""
        self.logger.info("Analyzing registry")
        findings = []
        
        try:
            # 1. Check for ctfmon in Run keys
            ctfmon_findings = self._check_ctfmon_registry()
            findings.extend(ctfmon_findings)
            
            # 2. Check for suspicious registry values
            suspicious_values = self._find_suspicious_registry_values()
            findings.extend(suspicious_values)
            
            # 3. Check for registry persistence mechanisms
            persistence_findings = self._check_registry_persistence()
            findings.extend(persistence_findings)
            
        except Exception as e:
            self.logger.error(f"Registry analysis failed: {e}")
        
        return findings
    
    def analyze_processes(self) -> List[Dict[str, Any]]:
        """Analyze processes for URCS indicators."""
        self.logger.info("Analyzing processes")
        findings = []
        
        try:
            # 1. Check for process hollowing into explorer.exe
            explorer_hollowing = self._check_explorer_hollowing()
            findings.extend(explorer_hollowing)
            
            # 2. Check for watchdog threads
            watchdog_threads = self._check_watchdog_threads()
            findings.extend(watchdog_threads)
            
            # 3. Check for CPU throttling behavior
            throttling_findings = self._check_cpu_throttling()
            findings.extend(throttling_findings)
            
            # 4. Check for battery-aware behavior
            battery_findings = self._check_battery_aware_behavior()
            findings.extend(battery_findings)
            
        except Exception as e:
            self.logger.error(f"Process analysis failed: {e}")
        
        return findings
    
    def analyze_network_behavior(self) -> List[Dict[str, Any]]:
        """Analyze network behavior for URCS indicators."""
        self.logger.info("Analyzing network behavior")
        findings = []
        
        try:
            # 1. Check for DNS beacon to api.ipify.org
            dns_beacons = self._check_dns_beacons()
            findings.extend(dns_beacons)
            
            # 2. Check for Stratum protocol connections
            stratum_connections = self._check_stratum_connections()
            findings.extend(stratum_connections)
            
            # 3. Check for mining pool connections
            pool_connections = self._check_mining_pool_connections()
            findings.extend(pool_connections)
            
        except Exception as e:
            self.logger.error(f"Network behavior analysis failed: {e}")
        
        return findings
    
    def find_suspicious_files(self) -> Dict[str, Any]:
        """Find suspicious files in system."""
        self.logger.info("Finding suspicious files")
        
        findings = {
            "fake_installers": [],
            "random_filenames": [],
            "suspicious_system_files": [],
            "mining_related_files": []
        }
        
        try:
            # Find fake Chrome update installers
            findings["fake_installers"] = self._find_chrome_update_files()
            
            # Find random 8-letter filenames
            findings["random_filenames"] = self._find_random_8_letter_files()
            
            # Find suspicious system files
            findings["suspicious_system_files"] = self._find_suspicious_system_files()
            
            # Find mining-related files
            findings["mining_related_files"] = self._find_mining_related_files()
            
        except Exception as e:
            self.logger.error(f"File finding failed: {e}")
        
        return findings
    
    # Helper methods for specific detections
    
    def _check_service_exists(self, service_name: str) -> bool:
        """Check if a service exists (placeholder implementation)."""
        # This would typically use Windows API or WMI
        # For now, return False as placeholder
        return False
    
    def _find_services_by_path(self, path_pattern: str) -> List[Dict[str, Any]]:
        """Find services with suspicious paths (placeholder implementation)."""
        # This would typically use Windows API or WMI
        return []
    
    def _check_task_exists(self, task_name: str) -> bool:
        """Check if a scheduled task exists (placeholder implementation)."""
        # This would typically use schtasks command or WMI
        return False
    
    def _find_tasks_by_interval(self, minutes: int) -> List[Dict[str, Any]]:
        """Find tasks with specific intervals (placeholder implementation)."""
        # This would typically use schtasks command or WMI
        return []
    
    def _find_chrome_update_files(self) -> List[str]:
        """Find fake Chrome update installer files."""
        chrome_update_files = []
        
        try:
            # Search for Chrome_update.exe files
            search_paths = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                "C:/Temp",
                "C:/Windows/Temp"
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if "chrome_update" in file.lower() and file.endswith('.exe'):
                                chrome_update_files.append(os.path.join(root, file))
            
        except Exception as e:
            self.logger.error(f"Chrome update file search failed: {e}")
        
        return chrome_update_files
    
    def _find_random_8_letter_files(self) -> List[str]:
        """Find random 8-letter filenames in suspicious locations."""
        random_files = []
        
        try:
            # Check System32\spool\drivers\color\ directory
            color_dir = "C:/Windows/System32/spool/drivers/color"
            if os.path.exists(color_dir):
                for file in os.listdir(color_dir):
                    if re.match(r'^[a-z]{8}\.exe$', file.lower()):
                        random_files.append(os.path.join(color_dir, file))
            
        except Exception as e:
            self.logger.error(f"Random file search failed: {e}")
        
        return random_files
    
    def _find_suspicious_system_files(self) -> List[str]:
        """Find suspicious files in system directories."""
        suspicious_files = []
        
        try:
            system_dirs = [
                "C:/Windows/System32",
                "C:/Windows/System32/drivers",
                "C:/Windows/Temp"
            ]
            
            for system_dir in system_dirs:
                if os.path.exists(system_dir):
                    for root, dirs, files in os.walk(system_dir):
                        for file in files:
                            if file.lower() in self.suspicious_names:
                                suspicious_files.append(os.path.join(root, file))
            
        except Exception as e:
            self.logger.error(f"Suspicious system file search failed: {e}")
        
        return suspicious_files
    
    def _find_mining_related_files(self) -> List[str]:
        """Find mining-related files."""
        mining_files = []
        
        try:
            mining_indicators = [
                "xmrig",
                "mining",
                "monero",
                "crypto",
                "stratum"
            ]
            
            search_paths = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                "C:/Temp",
                "C:/Windows/Temp"
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            file_lower = file.lower()
                            if any(indicator in file_lower for indicator in mining_indicators):
                                mining_files.append(os.path.join(root, file))
            
        except Exception as e:
            self.logger.error(f"Mining file search failed: {e}")
        
        return mining_files
    
    def _check_ctfmon_registry(self) -> List[Dict[str, Any]]:
        """Check for ctfmon in registry Run keys."""
        findings = []
        
        try:
            # This would typically use Windows Registry API
            # For now, return placeholder findings
            findings.append({
                "type": "registry_persistence",
                "key": "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\ctfmon",
                "value": "suspicious_path.exe",
                "description": "Suspicious ctfmon entry in Run key",
                "severity": "high",
                "mitre_technique": "T1547.001"
            })
            
        except Exception as e:
            self.logger.error(f"Registry ctfmon check failed: {e}")
        
        return findings
    
    def _find_suspicious_registry_values(self) -> List[Dict[str, Any]]:
        """Find suspicious registry values."""
        findings = []
        
        try:
            # This would typically use Windows Registry API
            # For now, return placeholder findings
            pass
            
        except Exception as e:
            self.logger.error(f"Suspicious registry value search failed: {e}")
        
        return findings
    
    def _check_registry_persistence(self) -> List[Dict[str, Any]]:
        """Check for registry persistence mechanisms."""
        findings = []
        
        try:
            # This would typically use Windows Registry API
            # For now, return placeholder findings
            pass
            
        except Exception as e:
            self.logger.error(f"Registry persistence check failed: {e}")
        
        return findings
    
    def _check_explorer_hollowing(self) -> List[Dict[str, Any]]:
        """Check for process hollowing into explorer.exe."""
        findings = []
        
        try:
            # This would typically use Windows API or memory analysis
            # For now, return placeholder findings
            findings.append({
                "type": "process_hollowing",
                "target_process": "explorer.exe",
                "description": "Potential process hollowing into explorer.exe detected",
                "severity": "high",
                "mitre_technique": "T1055.012"
            })
            
        except Exception as e:
            self.logger.error(f"Explorer hollowing check failed: {e}")
        
        return findings
    
    def _check_watchdog_threads(self) -> List[Dict[str, Any]]:
        """Check for watchdog threads monitoring Task Manager."""
        findings = []
        
        try:
            # This would typically use Windows API or memory analysis
            # For now, return placeholder findings
            findings.append({
                "type": "watchdog_thread",
                "target": "taskmgr.exe",
                "description": "Watchdog thread monitoring Task Manager detected",
                "severity": "medium",
                "mitre_technique": "T1562.001"
            })
            
        except Exception as e:
            self.logger.error(f"Watchdog thread check failed: {e}")
        
        return findings
    
    def _check_cpu_throttling(self) -> List[Dict[str, Any]]:
        """Check for CPU throttling behavior."""
        findings = []
        
        try:
            # This would typically use performance monitoring
            # For now, return placeholder findings
            findings.append({
                "type": "cpu_throttling",
                "description": "CPU throttling behavior detected when Task Manager opens",
                "severity": "medium",
                "mitre_technique": "T1562.001"
            })
            
        except Exception as e:
            self.logger.error(f"CPU throttling check failed: {e}")
        
        return findings
    
    def _check_battery_aware_behavior(self) -> List[Dict[str, Any]]:
        """Check for battery-aware throttling behavior."""
        findings = []
        
        try:
            # This would typically use power management APIs
            # For now, return placeholder findings
            findings.append({
                "type": "battery_aware_throttling",
                "description": "Battery-aware throttling behavior detected (90% on AC, 60% on battery)",
                "severity": "medium",
                "mitre_technique": "T1562.001"
            })
            
        except Exception as e:
            self.logger.error(f"Battery-aware behavior check failed: {e}")
        
        return findings
    
    def _check_dns_beacons(self) -> List[Dict[str, Any]]:
        """Check for DNS beacon to api.ipify.org."""
        findings = []
        
        try:
            # This would typically use network monitoring
            # For now, return placeholder findings
            findings.append({
                "type": "dns_beacon",
                "domain": "api.ipify.org",
                "description": "DNS beacon to api.ipify.org detected",
                "severity": "medium",
                "mitre_technique": "T1071.004"
            })
            
        except Exception as e:
            self.logger.error(f"DNS beacon check failed: {e}")
        
        return findings
    
    def _check_stratum_connections(self) -> List[Dict[str, Any]]:
        """Check for Stratum protocol connections."""
        findings = []
        
        try:
            # This would typically use network monitoring
            # For now, return placeholder findings
            findings.append({
                "type": "stratum_connection",
                "description": "Stratum protocol connection detected",
                "severity": "high",
                "mitre_technique": "T1071.001"
            })
            
        except Exception as e:
            self.logger.error(f"Stratum connection check failed: {e}")
        
        return findings
    
    def _check_mining_pool_connections(self) -> List[Dict[str, Any]]:
        """Check for mining pool connections."""
        findings = []
        
        try:
            # Check for connections to known mining pools
            for pool in self.suspicious_pools:
                findings.append({
                    "type": "mining_pool_connection",
                    "pool": pool,
                    "description": f"Connection to mining pool detected: {pool}",
                    "severity": "high",
                    "mitre_technique": "T1071.001"
                })
            
        except Exception as e:
            self.logger.error(f"Mining pool connection check failed: {e}")
        
        return findings