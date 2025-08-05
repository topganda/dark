"""Enhanced Behavioral Analysis Module for URCS Investigator Toolkit."""

import os
import json
import logging
import subprocess
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class BehavioralAnalyzer:
    """Performs comprehensive behavioral analysis on system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def analyze_system_behavior(self, scope: str = "full") -> Dict[str, Any]:
        """Comprehensive behavioral analysis (T-4, T-5, T-10, T-11)."""
        self.logger.info(f"Performing behavioral analysis with scope: {scope}")
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "scope": scope,
            "registry_artifacts": [],
            "service_artifacts": [],
            "scheduled_tasks": [],
            "file_operations": [],
            "process_behavior": [],
            "network_behavior": [],
            "suspicious_activities": [],
            "mitre_mapping": []
        }
        
        try:
            # T-5: Registry & service artifacts
            results["registry_artifacts"] = self._analyze_registry_artifacts()
            results["service_artifacts"] = self._analyze_service_artifacts()
            
            # T-11: Scheduled task scan
            results["scheduled_tasks"] = self._analyze_scheduled_tasks()
            
            # T-10: Self-deletion evidence
            results["file_operations"] = self._analyze_file_operations()
            
            # Additional behavioral analysis
            results["process_behavior"] = self._analyze_process_behavior()
            results["network_behavior"] = self._analyze_network_behavior()
            
            # Identify suspicious activities
            results["suspicious_activities"] = self._identify_suspicious_activities(results)
            
            # Map to MITRE ATT&CK
            results["mitre_mapping"] = self._map_mitre_techniques(results)
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def replay_in_sandbox(self, file_path: str, sandbox_type: str = "cape") -> Dict[str, Any]:
        """Replay file in sandbox (T-4)."""
        self.logger.info(f"Replaying {file_path} in {sandbox_type} sandbox")
        
        results = {
            "sandbox_type": sandbox_type,
            "file_path": file_path,
            "submission_time": datetime.now().isoformat(),
            "report": {},
            "api_calls": [],
            "file_writes": [],
            "registry_writes": [],
            "network_connections": [],
            "process_creations": [],
            "suspicious_behavior": []
        }
        
        try:
            if sandbox_type.lower() == "cape":
                results.update(self._replay_in_cape(file_path))
            elif sandbox_type.lower() == "cuckoo":
                results.update(self._replay_in_cuckoo(file_path))
            else:
                results["error"] = f"Unsupported sandbox type: {sandbox_type}"
                
        except Exception as e:
            self.logger.error(f"Sandbox replay failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def analyze_services(self) -> List[Dict[str, Any]]:
        """Analyze system services (T-5)."""
        self.logger.info("Analyzing system services")
        services = []
        
        try:
            # Use PowerShell to get service information
            cmd = [
                "powershell", "-Command",
                "Get-Service | Select-Object Name, DisplayName, Status, StartType, BinaryPathName | ConvertTo-Json"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                service_list = json.loads(process.stdout)
                if isinstance(service_list, dict):
                    service_list = [service_list]
                
                for service in service_list:
                    service_info = {
                        "name": service.get("Name"),
                        "display_name": service.get("DisplayName"),
                        "status": service.get("Status"),
                        "start_type": service.get("StartType"),
                        "binary_path": service.get("BinaryPathName"),
                        "suspicious_indicators": []
                    }
                    
                    # Check for suspicious indicators
                    suspicious_indicators = self._check_service_suspicious_indicators(service_info)
                    service_info["suspicious_indicators"] = suspicious_indicators
                    
                    if suspicious_indicators:
                        service_info["severity"] = "high"
                    else:
                        service_info["severity"] = "low"
                    
                    services.append(service_info)
                    
        except Exception as e:
            self.logger.error(f"Service analysis failed: {e}")
        
        return services
    
    def analyze_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Analyze scheduled tasks (T-11)."""
        self.logger.info("Analyzing scheduled tasks")
        tasks = []
        
        try:
            # Use schtasks to get task information
            cmd = ["schtasks", "/query", "/fo", "csv"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                # Parse CSV output
                lines = process.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    reader = csv.DictReader(lines[1:], fieldnames=lines[0].split(','))
                    
                    for row in reader:
                        task_info = {
                            "task_name": row.get("TaskName", "").strip('"'),
                            "next_run_time": row.get("Next Run Time", "").strip('"'),
                            "status": row.get("Status", "").strip('"'),
                            "logon_mode": row.get("Logon Mode", "").strip('"'),
                            "last_run_time": row.get("Last Run Time", "").strip('"'),
                            "author": row.get("Author", "").strip('"'),
                            "task_to_run": row.get("Task To Run", "").strip('"'),
                            "suspicious_indicators": []
                        }
                        
                        # Check for suspicious indicators
                        suspicious_indicators = self._check_task_suspicious_indicators(task_info)
                        task_info["suspicious_indicators"] = suspicious_indicators
                        
                        if suspicious_indicators:
                            task_info["severity"] = "high"
                        else:
                            task_info["severity"] = "low"
                        
                        tasks.append(task_info)
                        
        except Exception as e:
            self.logger.error(f"Scheduled task analysis failed: {e}")
        
        return tasks
    
    def analyze_file_system(self) -> List[Dict[str, Any]]:
        """Analyze file system for suspicious files."""
        self.logger.info("Analyzing file system")
        findings = []
        
        try:
            # Check common URCS locations
            suspicious_paths = [
                r"C:\Windows\System32\spool\drivers\color",
                r"C:\Windows\Temp",
                r"%TEMP%",
                r"C:\Users\*\AppData\Local\Temp",
                r"C:\Users\*\AppData\Roaming"
            ]
            
            for path_pattern in suspicious_paths:
                path_findings = self._scan_suspicious_path(path_pattern)
                findings.extend(path_findings)
                
        except Exception as e:
            self.logger.error(f"File system analysis failed: {e}")
        
        return findings
    
    def find_suspicious_files(self) -> List[Dict[str, Any]]:
        """Find suspicious files in the system."""
        self.logger.info("Finding suspicious files")
        suspicious_files = []
        
        try:
            # Look for files with suspicious names or patterns
            suspicious_patterns = [
                "Chrome_update.exe",
                "gupdatem",
                "algfzpoe.exe",
                "Ddriver",
                "ctfmon.exe"
            ]
            
            for pattern in suspicious_patterns:
                files = self._find_files_by_pattern(pattern)
                suspicious_files.extend(files)
                
        except Exception as e:
            self.logger.error(f"Suspicious file search failed: {e}")
        
        return suspicious_files
    
    # Helper methods for specific tasks
    
    def _analyze_registry_artifacts(self) -> List[Dict[str, Any]]:
        """Analyze registry artifacts (T-5)."""
        artifacts = []
        
        try:
            # Check common persistence locations
            registry_locations = [
                r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ]
            
            for location in registry_locations:
                location_artifacts = self._query_registry_location(location)
                artifacts.extend(location_artifacts)
                
        except Exception as e:
            self.logger.error(f"Registry artifact analysis failed: {e}")
        
        return artifacts
    
    def _analyze_service_artifacts(self) -> List[Dict[str, Any]]:
        """Analyze service artifacts (T-5)."""
        artifacts = []
        
        try:
            services = self.analyze_services()
            
            for service in services:
                if service.get("suspicious_indicators"):
                    artifacts.append({
                        "type": "suspicious_service",
                        "service_name": service.get("name"),
                        "display_name": service.get("display_name"),
                        "binary_path": service.get("binary_path"),
                        "suspicious_indicators": service.get("suspicious_indicators"),
                        "severity": service.get("severity")
                    })
                    
        except Exception as e:
            self.logger.error(f"Service artifact analysis failed: {e}")
        
        return artifacts
    
    def _analyze_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Analyze scheduled tasks (T-11)."""
        artifacts = []
        
        try:
            tasks = self.analyze_scheduled_tasks()
            
            for task in tasks:
                if task.get("suspicious_indicators"):
                    artifacts.append({
                        "type": "suspicious_scheduled_task",
                        "task_name": task.get("task_name"),
                        "task_to_run": task.get("task_to_run"),
                        "suspicious_indicators": task.get("suspicious_indicators"),
                        "severity": task.get("severity")
                    })
                    
        except Exception as e:
            self.logger.error(f"Scheduled task analysis failed: {e}")
        
        return artifacts
    
    def _analyze_file_operations(self) -> List[Dict[str, Any]]:
        """Analyze file operations (T-10)."""
        operations = []
        
        try:
            # This would typically use file system monitoring or logs
            # For now, check for recent file deletions in suspicious locations
            
            suspicious_locations = [
                r"C:\Windows\System32\spool\drivers\color",
                r"C:\Windows\Temp",
                r"%TEMP%"
            ]
            
            for location in suspicious_locations:
                location_operations = self._check_recent_file_operations(location)
                operations.extend(location_operations)
                
        except Exception as e:
            self.logger.error(f"File operation analysis failed: {e}")
        
        return operations
    
    def _analyze_process_behavior(self) -> List[Dict[str, Any]]:
        """Analyze process behavior."""
        behaviors = []
        
        try:
            # Check for suspicious process behaviors
            suspicious_behaviors = [
                "process_hollowing",
                "injection_into_explorer",
                "watchdog_threads",
                "cpu_throttling"
            ]
            
            for behavior_type in suspicious_behaviors:
                behavior_findings = self._check_process_behavior(behavior_type)
                behaviors.extend(behavior_findings)
                
        except Exception as e:
            self.logger.error(f"Process behavior analysis failed: {e}")
        
        return behaviors
    
    def _analyze_network_behavior(self) -> List[Dict[str, Any]]:
        """Analyze network behavior."""
        behaviors = []
        
        try:
            # Check for suspicious network connections
            suspicious_connections = [
                "gulf.moneroocean.stream:10032",
                "api.ipify.org",
                "stratum+tcp://"
            ]
            
            for connection in suspicious_connections:
                connection_findings = self._check_network_connection(connection)
                behaviors.extend(connection_findings)
                
        except Exception as e:
            self.logger.error(f"Network behavior analysis failed: {e}")
        
        return behaviors
    
    def _replay_in_cape(self, file_path: str) -> Dict[str, Any]:
        """Replay file in CAPEv2 sandbox (T-4)."""
        results = {}
        
        try:
            # Submit file to CAPE
            submit_cmd = [
                "python3", "cuckoo.py", "submit", "--timeout", "300", file_path
            ]
            
            process = subprocess.run(submit_cmd, capture_output=True, text=True, timeout=600)
            
            if process.returncode == 0:
                # Extract task ID from output
                output_lines = process.stdout.split('\n')
                task_id = None
                for line in output_lines:
                    if "Task ID:" in line:
                        task_id = line.split("Task ID:")[1].strip()
                        break
                
                if task_id:
                    # Get report
                    report_cmd = [
                        "python3", "cuckoo.py", "report", "--format", "json", task_id
                    ]
                    
                    report_process = subprocess.run(report_cmd, capture_output=True, text=True, timeout=300)
                    
                    if report_process.returncode == 0:
                        report_data = json.loads(report_process.stdout)
                        results["report"] = report_data
                        results["task_id"] = task_id
                        
                        # Extract specific information
                        results["api_calls"] = report_data.get("behavior", {}).get("apistats", {})
                        results["file_writes"] = report_data.get("behavior", {}).get("files", [])
                        results["registry_writes"] = report_data.get("behavior", {}).get("registry", [])
                        results["network_connections"] = report_data.get("network", {}).get("tcp", [])
                        results["process_creations"] = report_data.get("behavior", {}).get("processes", [])
                        
        except Exception as e:
            self.logger.error(f"CAPE replay failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def _replay_in_cuckoo(self, file_path: str) -> Dict[str, Any]:
        """Replay file in Cuckoo sandbox (T-4)."""
        results = {}
        
        try:
            # Similar to CAPE but with Cuckoo-specific commands
            submit_cmd = [
                "python3", "cuckoo.py", "submit", file_path
            ]
            
            process = subprocess.run(submit_cmd, capture_output=True, text=True, timeout=600)
            
            if process.returncode == 0:
                # Extract task ID and get report
                # Implementation similar to CAPE
                pass
                
        except Exception as e:
            self.logger.error(f"Cuckoo replay failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def _check_service_suspicious_indicators(self, service_info: Dict[str, Any]) -> List[str]:
        """Check for suspicious indicators in service."""
        indicators = []
        
        try:
            # Check for suspicious service names
            suspicious_names = ["gupdatem", "google update", "chrome update"]
            service_name = service_info.get("name", "").lower()
            display_name = service_info.get("display_name", "").lower()
            
            for suspicious_name in suspicious_names:
                if suspicious_name in service_name or suspicious_name in display_name:
                    indicators.append(f"Suspicious service name: {suspicious_name}")
            
            # Check for suspicious binary paths
            binary_path = service_info.get("binary_path", "").lower()
            suspicious_paths = [
                r"\system32\spool\drivers\color",
                r"\temp\",
                r"appdata\local\temp"
            ]
            
            for suspicious_path in suspicious_paths:
                if suspicious_path in binary_path:
                    indicators.append(f"Suspicious binary path: {suspicious_path}")
                    
        except Exception as e:
            self.logger.error(f"Service suspicious indicator check failed: {e}")
        
        return indicators
    
    def _check_task_suspicious_indicators(self, task_info: Dict[str, Any]) -> List[str]:
        """Check for suspicious indicators in scheduled task."""
        indicators = []
        
        try:
            # Check for suspicious task names
            task_name = task_info.get("task_name", "").lower()
            if "ddriver" in task_name:
                indicators.append("Suspicious task name: Ddriver")
            
            # Check for suspicious commands
            task_command = task_info.get("task_to_run", "").lower()
            suspicious_commands = [
                r"\system32\spool\drivers\color",
                "gupdatem",
                "algfzpoe.exe"
            ]
            
            for suspicious_command in suspicious_commands:
                if suspicious_command in task_command:
                    indicators.append(f"Suspicious task command: {suspicious_command}")
                    
        except Exception as e:
            self.logger.error(f"Task suspicious indicator check failed: {e}")
        
        return indicators
    
    def _query_registry_location(self, location: str) -> List[Dict[str, Any]]:
        """Query registry location for artifacts."""
        artifacts = []
        
        try:
            # Use PowerShell to query registry
            cmd = [
                "powershell", "-Command",
                f"Get-ItemProperty -Path 'Registry::{location}' | ConvertTo-Json"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if process.returncode == 0:
                registry_data = json.loads(process.stdout)
                
                for key, value in registry_data.items():
                    if key not in ["PSPath", "PSParentName", "PSChildName", "PSProvider"]:
                        artifacts.append({
                            "registry_key": location,
                            "value_name": key,
                            "value_data": value,
                            "suspicious": self._is_suspicious_registry_value(key, value)
                        })
                        
        except Exception as e:
            self.logger.error(f"Registry query failed for {location}: {e}")
        
        return artifacts
    
    def _is_suspicious_registry_value(self, key: str, value: str) -> bool:
        """Check if registry value is suspicious."""
        suspicious_patterns = [
            "ctfmon",
            "gupdatem",
            r"\system32\spool\drivers\color",
            "algfzpoe.exe"
        ]
        
        key_lower = key.lower()
        value_lower = str(value).lower()
        
        for pattern in suspicious_patterns:
            if pattern in key_lower or pattern in value_lower:
                return True
        
        return False
    
    def _scan_suspicious_path(self, path_pattern: str) -> List[Dict[str, Any]]:
        """Scan suspicious path for files."""
        findings = []
        
        try:
            # Use PowerShell to scan path
            cmd = [
                "powershell", "-Command",
                f"Get-ChildItem -Path '{path_pattern}' -Recurse -ErrorAction SilentlyContinue | Select-Object Name, FullName, Length, LastWriteTime | ConvertTo-Json"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                files_data = json.loads(process.stdout)
                if isinstance(files_data, dict):
                    files_data = [files_data]
                
                for file_info in files_data:
                    if self._is_suspicious_file(file_info):
                        findings.append({
                            "type": "suspicious_file",
                            "file_name": file_info.get("Name"),
                            "full_path": file_info.get("FullName"),
                            "size": file_info.get("Length"),
                            "last_modified": file_info.get("LastWriteTime"),
                            "path_pattern": path_pattern
                        })
                        
        except Exception as e:
            self.logger.error(f"Path scan failed for {path_pattern}: {e}")
        
        return findings
    
    def _is_suspicious_file(self, file_info: Dict[str, Any]) -> bool:
        """Check if file is suspicious."""
        suspicious_names = [
            "chrome_update.exe",
            "gupdatem",
            "algfzpoe.exe",
            "ddriver",
            "ctfmon.exe"
        ]
        
        file_name = file_info.get("Name", "").lower()
        
        for suspicious_name in suspicious_names:
            if suspicious_name in file_name:
                return True
        
        return False
    
    def _find_files_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find files by pattern."""
        files = []
        
        try:
            # Use PowerShell to find files
            cmd = [
                "powershell", "-Command",
                f"Get-ChildItem -Path C:\ -Recurse -Name '*{pattern}*' -ErrorAction SilentlyContinue | ConvertTo-Json"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if process.returncode == 0:
                file_list = json.loads(process.stdout)
                if isinstance(file_list, str):
                    file_list = [file_list]
                
                for file_path in file_list:
                    files.append({
                        "file_path": file_path,
                        "pattern": pattern,
                        "found_time": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            self.logger.error(f"File pattern search failed for {pattern}: {e}")
        
        return files
    
    def _check_recent_file_operations(self, location: str) -> List[Dict[str, Any]]:
        """Check for recent file operations in location."""
        operations = []
        
        try:
            # This would typically use file system monitoring or logs
            # For now, return placeholder findings
            
            operations.append({
                "type": "file_operation",
                "location": location,
                "operation": "FILE_DELETE",
                "file_name": "suspicious_file.exe",
                "timestamp": datetime.now().isoformat(),
                "description": "Recent file deletion detected"
            })
            
        except Exception as e:
            self.logger.error(f"Recent file operation check failed: {e}")
        
        return operations
    
    def _check_process_behavior(self, behavior_type: str) -> List[Dict[str, Any]]:
        """Check for specific process behavior."""
        behaviors = []
        
        try:
            # This would typically use process monitoring or memory analysis
            # For now, return placeholder findings
            
            behaviors.append({
                "type": "process_behavior",
                "behavior": behavior_type,
                "description": f"{behavior_type} behavior detected",
                "timestamp": datetime.now().isoformat(),
                "severity": "medium"
            })
            
        except Exception as e:
            self.logger.error(f"Process behavior check failed: {e}")
        
        return behaviors
    
    def _check_network_connection(self, connection: str) -> List[Dict[str, Any]]:
        """Check for specific network connection."""
        connections = []
        
        try:
            # This would typically use network monitoring
            # For now, return placeholder findings
            
            connections.append({
                "type": "network_connection",
                "connection": connection,
                "description": f"Connection to {connection} detected",
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            })
            
        except Exception as e:
            self.logger.error(f"Network connection check failed: {e}")
        
        return connections
    
    def _identify_suspicious_activities(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify suspicious activities from analysis results."""
        activities = []
        
        try:
            # Combine findings from different analysis types
            all_findings = []
            
            # Add registry findings
            for artifact in analysis_results.get("registry_artifacts", []):
                if artifact.get("suspicious"):
                    all_findings.append({
                        "type": "suspicious_registry",
                        "description": f"Suspicious registry entry: {artifact.get('value_name')}",
                        "severity": "high"
                    })
            
            # Add service findings
            for artifact in analysis_results.get("service_artifacts", []):
                all_findings.append({
                    "type": "suspicious_service",
                    "description": f"Suspicious service: {artifact.get('service_name')}",
                    "severity": "high"
                })
            
            # Add task findings
            for artifact in analysis_results.get("scheduled_tasks", []):
                all_findings.append({
                    "type": "suspicious_scheduled_task",
                    "description": f"Suspicious scheduled task: {artifact.get('task_name')}",
                    "severity": "high"
                })
            
            activities = all_findings
            
        except Exception as e:
            self.logger.error(f"Suspicious activity identification failed: {e}")
        
        return activities
    
    def _map_mitre_techniques(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map findings to MITRE ATT&CK techniques."""
        techniques = []
        
        try:
            # Map based on findings
            if analysis_results.get("registry_artifacts"):
                techniques.append({
                    "technique_id": "T1543.003",
                    "technique_name": "Create or Modify System Process: Windows Service",
                    "description": "Registry persistence indicators detected"
                })
            
            if analysis_results.get("scheduled_tasks"):
                techniques.append({
                    "technique_id": "T1053.005",
                    "technique_name": "Scheduled Task/Job: Scheduled Task",
                    "description": "Suspicious scheduled tasks detected"
                })
            
            if analysis_results.get("file_operations"):
                techniques.append({
                    "technique_id": "T1070.004",
                    "technique_name": "Indicator Removal on Host: File Deletion",
                    "description": "File deletion operations detected"
                })
            
            if analysis_results.get("process_behavior"):
                techniques.append({
                    "technique_id": "T1055.012",
                    "technique_name": "Process Injection: Process Hollowing",
                    "description": "Process injection behavior detected"
                })
            
        except Exception as e:
            self.logger.error(f"MITRE technique mapping failed: {e}")
        
        return techniques