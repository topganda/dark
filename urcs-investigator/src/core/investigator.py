"""
Main Investigator Class for URCS Investigator Toolkit
Orchestrates all analysis modules and provides unified interface for investigations.
"""

import os
import time
import logging
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
        
        # Investigation state
        self.investigation_id = None
        self.start_time = None
        self.results = {}
        
        self.logger.info("URCS Investigator initialized")
    
    def investigate(self, target: str, scope: str = "comprehensive", 
                   output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Run comprehensive investigation."""
        self.investigation_id = f"investigation_{int(time.time())}"
        self.start_time = datetime.now()
        
        output_dir = output_dir or f"reports/{self.investigation_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Starting investigation {self.investigation_id} on {target}")
        self.logger.info(f"Scope: {scope}, Output: {output_dir}")
        
        results = {
            "investigation_id": self.investigation_id,
            "target": target,
            "scope": scope,
            "start_time": self.start_time.isoformat(),
            "output_dir": output_dir,
            "modules": {},
            "iocs": [],
            "findings": [],
            "report_path": None
        }
        
        try:
            # Run analysis modules based on scope
            if scope in ["comprehensive", "full"]:
                results["modules"]["static"] = self._run_static_analysis(target)
                results["modules"]["behavioral"] = self._run_behavioral_analysis(target)
                results["modules"]["memory"] = self._run_memory_analysis(target)
                results["modules"]["network"] = self._run_network_analysis(target)
            elif scope == "basic":
                results["modules"]["behavioral"] = self._run_behavioral_analysis(target)
                results["modules"]["static"] = self._run_static_analysis(target)
            
            # Extract IOCs
            results["iocs"] = self.ioc_extractor.extract_iocs(results["modules"])
            
            # Generate findings
            results["findings"] = self._generate_findings(results["modules"])
            
            # Generate report
            results["report_path"] = self.report_generator.generate_report(
                results, output_dir
            )
            
            # Save investigation results
            self._save_investigation_results(results, output_dir)
            
            self.logger.info(f"Investigation {self.investigation_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Investigation failed: {e}")
            results["error"] = str(e)
        
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = (datetime.now() - self.start_time).total_seconds()
        
        return results
    
    def static_analysis(self, file_path: str, entropy: bool = True, 
                       signature: bool = True, yara: bool = True) -> Dict[str, Any]:
        """Perform static analysis on a file."""
        self.logger.info(f"Performing static analysis on {file_path}")
        
        results = {
            "file_path": file_path,
            "entropy": None,
            "signature_status": None,
            "yara_matches": [],
            "pe_info": {},
            "findings": []
        }
        
        try:
            if entropy:
                results["entropy"] = self.static_analyzer.calculate_entropy(file_path)
            
            if signature:
                results["signature_status"] = self.static_analyzer.verify_signature(file_path)
            
            if yara:
                results["yara_matches"] = self.yara_detector.scan_file(file_path)
            
            # PE analysis
            results["pe_info"] = self.static_analyzer.analyze_pe_file(file_path)
            
            # Generate findings
            results["findings"] = self._analyze_static_findings(results)
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def behavioral_analysis(self, system: bool = True, registry: bool = True,
                          services: bool = True, tasks: bool = True) -> Dict[str, Any]:
        """Perform behavioral analysis."""
        self.logger.info("Performing behavioral analysis")
        
        results = {
            "registry_findings": [],
            "service_findings": [],
            "task_findings": [],
            "file_system_findings": [],
            "process_findings": []
        }
        
        try:
            if registry:
                results["registry_findings"] = self.registry_analyzer.analyze_registry()
            
            if services:
                results["service_findings"] = self.behavioral_analyzer.analyze_services()
            
            if tasks:
                results["task_findings"] = self.behavioral_analyzer.analyze_scheduled_tasks()
            
            if system:
                results["file_system_findings"] = self.behavioral_analyzer.analyze_file_system()
                results["process_findings"] = self.process_analyzer.analyze_processes()
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def memory_forensics(self, pid: Optional[int] = None, dump_file: Optional[str] = None,
                        injection: bool = True) -> Dict[str, Any]:
        """Perform memory forensics."""
        self.logger.info("Performing memory forensics")
        
        results = {
            "injection_findings": [],
            "memory_regions": [],
            "process_info": {},
            "dll_analysis": [],
            "handle_analysis": []
        }
        
        try:
            if injection:
                results["injection_findings"] = self.memory_analyzer.detect_injection(pid, dump_file)
            
            if pid:
                results["process_info"] = self.process_analyzer.get_process_info(pid)
                results["memory_regions"] = self.memory_analyzer.analyze_memory_regions(pid)
                results["dll_analysis"] = self.memory_analyzer.analyze_dlls(pid)
                results["handle_analysis"] = self.memory_analyzer.analyze_handles(pid)
            
        except Exception as e:
            self.logger.error(f"Memory forensics failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def network_analysis(self, interface: Optional[str] = None, 
                        capture_file: Optional[str] = None,
                        live: bool = False) -> Dict[str, Any]:
        """Perform network analysis."""
        self.logger.info("Performing network analysis")
        
        results = {
            "connections": [],
            "suspicious_traffic": [],
            "dns_queries": [],
            "protocol_analysis": {},
            "iocs": []
        }
        
        try:
            if live and interface:
                results.update(self.network_analyzer.capture_live_traffic(interface))
            elif capture_file:
                results.update(self.network_analyzer.analyze_capture_file(capture_file))
            else:
                results.update(self.network_analyzer.analyze_current_connections())
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def generate_report(self, output_path: str, format: str = "html", 
                       template: Optional[str] = None) -> str:
        """Generate investigation report."""
        self.logger.info(f"Generating report: {output_path}")
        
        if not self.results:
            self.logger.warning("No investigation results available for report generation")
            return ""
        
        return self.report_generator.generate_report(
            self.results, output_path, format, template
        )
    
    def export_iocs(self, format: str = "json", output_path: Optional[str] = None) -> str:
        """Export indicators of compromise."""
        self.logger.info(f"Exporting IOCs in {format} format")
        
        if not self.results:
            self.logger.warning("No investigation results available for IOC export")
            return ""
        
        return self.ioc_extractor.export_iocs(
            self.results.get("iocs", []), format, output_path
        )
    
    def setup_environment(self, sysmon: bool = True, etw: bool = True, 
                         powershell: bool = True) -> Dict[str, bool]:
        """Setup investigation environment."""
        self.logger.info("Setting up investigation environment")
        
        results = {
            "sysmon": False,
            "etw_tracing": False,
            "powershell_logging": False,
            "directories": False
        }
        
        try:
            # Create necessary directories
            directories = ["logs", "reports", "config", "yara_rules", "templates"]
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            results["directories"] = True
            
            # Setup monitoring components
            if sysmon:
                results["sysmon"] = self._setup_sysmon()
            
            if etw:
                results["etw_tracing"] = self._setup_etw_tracing()
            
            if powershell:
                results["powershell_logging"] = self._setup_powershell_logging()
            
        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
        
        return results
    
    def _run_static_analysis(self, target: str) -> Dict[str, Any]:
        """Run static analysis module."""
        if os.path.isfile(target):
            return self.static_analysis(target)
        else:
            # For system targets, analyze suspicious files
            return self.behavioral_analyzer.find_suspicious_files()
    
    def _run_behavioral_analysis(self, target: str) -> Dict[str, Any]:
        """Run behavioral analysis module."""
        return self.behavioral_analysis(system=True, registry=True, services=True, tasks=True)
    
    def _run_memory_analysis(self, target: str) -> Dict[str, Any]:
        """Run memory analysis module."""
        return self.memory_forensics(injection=True)
    
    def _run_network_analysis(self, target: str) -> Dict[str, Any]:
        """Run network analysis module."""
        return self.network_analysis(live=False)
    
    def _generate_findings(self, modules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate findings from analysis modules."""
        findings = []
        
        for module_name, module_results in modules.items():
            if "findings" in module_results:
                for finding in module_results["findings"]:
                    finding["module"] = module_name
                    findings.append(finding)
        
        return findings
    
    def _save_investigation_results(self, results: Dict[str, Any], output_dir: str):
        """Save investigation results to file."""
        import json
        
        results_file = os.path.join(output_dir, "investigation_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Investigation results saved to {results_file}")
    
    def _analyze_static_findings(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze static analysis results for findings."""
        findings = []
        
        # Check entropy
        if results.get("entropy", 0) > self.config.get("detection.thresholds.entropy", 7.5):
            findings.append({
                "type": "high_entropy",
                "severity": "medium",
                "description": f"File has high entropy: {results['entropy']}",
                "evidence": results["entropy"]
            })
        
        # Check signature
        if results.get("signature_status") == "invalid":
            findings.append({
                "type": "invalid_signature",
                "severity": "high",
                "description": "File has invalid digital signature",
                "evidence": results["signature_status"]
            })
        
        # Check YARA matches
        for match in results.get("yara_matches", []):
            findings.append({
                "type": "yara_match",
                "severity": "high",
                "description": f"YARA rule matched: {match['rule']}",
                "evidence": match
            })
        
        return findings
    
    def _setup_sysmon(self) -> bool:
        """Setup Sysmon monitoring."""
        try:
            # This would typically involve installing and configuring Sysmon
            # For now, we'll just check if it's available
            self.logger.info("Sysmon setup would be implemented here")
            return True
        except Exception as e:
            self.logger.error(f"Sysmon setup failed: {e}")
            return False
    
    def _setup_etw_tracing(self) -> bool:
        """Setup ETW tracing."""
        try:
            # This would typically involve configuring ETW providers
            self.logger.info("ETW tracing setup would be implemented here")
            return True
        except Exception as e:
            self.logger.error(f"ETW tracing setup failed: {e}")
            return False
    
    def _setup_powershell_logging(self) -> bool:
        """Setup PowerShell logging."""
        try:
            # This would typically involve configuring PowerShell logging
            self.logger.info("PowerShell logging setup would be implemented here")
            return True
        except Exception as e:
            self.logger.error(f"PowerShell logging setup failed: {e}")
            return False