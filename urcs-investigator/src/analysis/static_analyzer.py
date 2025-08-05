"""Enhanced Static Analysis Module for URCS Investigator Toolkit."""

import os
import hashlib
import logging
import subprocess
import json
import yara
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class StaticAnalyzer:
    """Performs comprehensive static analysis on files."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.yara_rules = self._load_yara_rules()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive static analysis of a file."""
        self.logger.info(f"Performing static analysis on: {file_path}")
        
        results = {
            "file_path": file_path,
            "file_info": {},
            "entropy_analysis": {},
            "signature_analysis": {},
            "dropper_analysis": {},
            "yara_matches": [],
            "suspicious_indicators": [],
            "mitre_mapping": []
        }
        
        try:
            # T-0: File acquisition and basic info
            results["file_info"] = self._get_file_info(file_path)
            
            # T-1: Static entropy & signer check
            results["entropy_analysis"] = self._analyze_entropy(file_path)
            results["signature_analysis"] = self._analyze_signature(file_path)
            
            # T-2: Dropper extraction
            results["dropper_analysis"] = self._extract_dropper(file_path)
            
            # T-3: YARA rule scanning
            results["yara_matches"] = self._scan_with_yara(file_path)
            
            # Additional analysis
            results["suspicious_indicators"] = self._find_suspicious_indicators(file_path)
            results["mitre_mapping"] = self._map_mitre_techniques(results)
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def calculate_entropy(self, file_path: str) -> float:
        """Calculate file entropy (T-1)."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if not data:
                return 0.0
            
            # Calculate Shannon entropy
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
            
            entropy = 0.0
            data_len = len(data)
            
            for count in byte_counts:
                if count > 0:
                    probability = count / data_len
                    entropy -= probability * (probability.bit_length() - 1)
            
            return entropy
            
        except Exception as e:
            self.logger.error(f"Entropy calculation failed: {e}")
            return 0.0
    
    def verify_signature(self, file_path: str) -> Dict[str, Any]:
        """Verify digital signature (T-1)."""
        result = {
            "signed": False,
            "valid": False,
            "signer": None,
            "timestamp": None,
            "error": None
        }
        
        try:
            # Use PowerShell to check signature
            cmd = [
                "powershell", "-Command",
                f"Get-AuthenticodeSignature '{file_path}' | ConvertTo-Json"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if process.returncode == 0:
                signature_info = json.loads(process.stdout)
                result["signed"] = signature_info.get("Status") != "NotSigned"
                result["valid"] = signature_info.get("Status") == "Valid"
                result["signer"] = signature_info.get("SignerCertificate", {}).get("Subject")
                result["timestamp"] = signature_info.get("TimeStamperCertificate", {}).get("Subject")
            else:
                result["error"] = process.stderr
                
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Signature verification failed: {e}")
        
        return result
    
    def extract_embedded_files(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract embedded files using 7-Zip or binwalk (T-2)."""
        extracted_files = []
        
        try:
            # Try 7-Zip first
            extracted_files.extend(self._extract_with_7zip(file_path))
            
            # Try binwalk as fallback
            if not extracted_files:
                extracted_files.extend(self._extract_with_binwalk(file_path))
                
        except Exception as e:
            self.logger.error(f"File extraction failed: {e}")
        
        return extracted_files
    
    def generate_yara_rule(self, file_path: str, pool_string: str = None, wallet_prefix: str = None) -> str:
        """Generate YARA rule for the file (T-3)."""
        yara_rule = f"""
rule urcs_detection_{hashlib.md5(file_path.encode()).hexdigest()[:8]} {{
    meta:
        description = "URCS detection rule for {os.path.basename(file_path)}"
        author = "URCS Investigator Toolkit"
        date = "2024"
        reference = "MITRE ATT&CK T1055.012, T1543.003"
        severity = "high"
    
    strings:
        // Pool and wallet indicators
        $pool_string = "{pool_string or 'gulf.moneroocean.stream:10032'}"
        $wallet_prefix = "{wallet_prefix or '49d3f'}" nocase
        $stratum_protocol = "stratum+tcp://"
        
        // Process and service names
        $mutex_pattern = /gupdatem_[0-9]{{4}}/
        $service_name = "Google Update Service"
        
        // Registry paths
        $registry_path = "HKCU\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\ctfmon"
        
        // File paths
        $system_path = "\\\\System32\\\\spool\\\\drivers\\\\color\\\\"
        
        // Mining-related strings
        $xmrig_string = "xmrig" nocase
        $mining_string = "mining" nocase
        $crypto_string = "cryptocurrency" nocase
        
        // Evasion techniques
        $task_manager = "taskmgr.exe" nocase
        $process_hollow = "process hollow" nocase
        $injection = "injection" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (all of ($pool_string, $wallet_prefix) or 
         $mutex_pattern or 
         $registry_path or
         $system_path or
         all of ($xmrig_string, $mining_string) or
         all of ($task_manager, $injection))
}}
"""
        return yara_rule
    
    def scan_with_custom_yara(self, file_path: str, yara_rule: str) -> List[Dict[str, Any]]:
        """Scan file with custom YARA rule."""
        matches = []
        
        try:
            # Compile and scan with the custom rule
            rule = yara.compile(source=yara_rule)
            rule_matches = rule.match(file_path)
            
            for match in rule_matches:
                matches.append({
                    "rule_name": match.rule,
                    "strings": [{"name": s.name, "offset": s.offset, "matched_data": s.matched_data.hex()} for s in match.strings],
                    "meta": match.meta
                })
                
        except Exception as e:
            self.logger.error(f"Custom YARA scan failed: {e}")
        
        return matches
    
    # Helper methods for specific tasks
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        try:
            stat = os.stat(file_path)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            return {
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "sha256": file_hash,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": Path(file_path).suffix.lower()
            }
        except Exception as e:
            self.logger.error(f"File info retrieval failed: {e}")
            return {}
    
    def _analyze_entropy(self, file_path: str) -> Dict[str, Any]:
        """Analyze file entropy (T-1)."""
        try:
            entropy = self.calculate_entropy(file_path)
            
            return {
                "overall_entropy": entropy,
                "entropy_threshold": 7.5,
                "is_suspicious": entropy > 7.5,
                "interpretation": "High entropy indicates packed/encrypted content" if entropy > 7.5 else "Normal entropy level"
            }
        except Exception as e:
            self.logger.error(f"Entropy analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_signature(self, file_path: str) -> Dict[str, Any]:
        """Analyze digital signature (T-1)."""
        try:
            signature_info = self.verify_signature(file_path)
            
            return {
                "signature_info": signature_info,
                "is_suspicious": not signature_info.get("valid", False),
                "interpretation": "Invalid or missing signature may indicate tampering"
            }
        except Exception as e:
            self.logger.error(f"Signature analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_dropper(self, file_path: str) -> Dict[str, Any]:
        """Extract dropper content (T-2)."""
        try:
            extracted_files = self.extract_embedded_files(file_path)
            
            return {
                "extracted_files": extracted_files,
                "has_embedded_pe": any(f.get("type") == "PE" for f in extracted_files),
                "embedded_pe_files": [f for f in extracted_files if f.get("type") == "PE"],
                "interpretation": "Embedded PE files may indicate dropper behavior"
            }
        except Exception as e:
            self.logger.error(f"Dropper extraction failed: {e}")
            return {"error": str(e)}
    
    def _scan_with_yara(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan file with YARA rules (T-3)."""
        matches = []
        
        try:
            # Scan with loaded rules
            for rule_name, rule in self.yara_rules.items():
                try:
                    rule_matches = rule.match(file_path)
                    for match in rule_matches:
                        matches.append({
                            "rule_name": rule_name,
                            "match_name": match.rule,
                            "strings": [{"name": s.name, "offset": s.offset} for s in match.strings],
                            "meta": match.meta
                        })
                except Exception as e:
                    self.logger.warning(f"YARA rule {rule_name} failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"YARA scanning failed: {e}")
        
        return matches
    
    def _find_suspicious_indicators(self, file_path: str) -> List[Dict[str, Any]]:
        """Find suspicious indicators in the file."""
        indicators = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check for suspicious strings
            suspicious_patterns = [
                (b"gulf.moneroocean.stream", "Mining pool URL"),
                (b"49d3f", "Monero wallet prefix"),
                (b"xmrig", "XMRig miner"),
                (b"stratum+tcp://", "Stratum protocol"),
                (b"gupdatem", "Suspicious service name"),
                (b"ctfmon", "Registry persistence"),
                (b"taskmgr.exe", "Task Manager monitoring"),
                (b"explorer.exe", "Process hollowing target"),
                (b"\\System32\\spool\\drivers\\color\\", "Suspicious file path")
            ]
            
            for pattern, description in suspicious_patterns:
                if pattern in content:
                    offset = content.find(pattern)
                    indicators.append({
                        "type": "suspicious_string",
                        "pattern": pattern.decode('utf-8', errors='ignore'),
                        "description": description,
                        "offset": offset,
                        "severity": "high"
                    })
                    
        except Exception as e:
            self.logger.error(f"Suspicious indicator detection failed: {e}")
        
        return indicators
    
    def _map_mitre_techniques(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map findings to MITRE ATT&CK techniques."""
        techniques = []
        
        # Map based on findings
        if analysis_results.get("dropper_analysis", {}).get("has_embedded_pe"):
            techniques.append({
                "technique_id": "T1055.012",
                "technique_name": "Process Injection: Process Hollowing",
                "description": "Embedded PE files indicate potential process hollowing"
            })
        
        if any("registry" in str(match) for match in analysis_results.get("yara_matches", [])):
            techniques.append({
                "technique_id": "T1543.003",
                "technique_name": "Create or Modify System Process: Windows Service",
                "description": "Registry persistence indicators detected"
            })
        
        if any("taskmgr" in str(match) for match in analysis_results.get("yara_matches", [])):
            techniques.append({
                "technique_id": "T1562.001",
                "technique_name": "Impair Defenses: Disable or Modify Tools",
                "description": "Task Manager monitoring detected"
            })
        
        return techniques
    
    def _extract_with_7zip(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract files using 7-Zip."""
        extracted_files = []
        
        try:
            # Use 7-Zip to list contents
            cmd = ["7z", "l", file_path]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                # Parse 7-Zip output to find embedded files
                lines = process.stdout.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('---'):
                        parts = line.split()
                        if len(parts) >= 4:
                            filename = parts[-1]
                            if filename.endswith('.exe') or filename.endswith('.dll'):
                                extracted_files.append({
                                    "filename": filename,
                                    "type": "PE",
                                    "extraction_method": "7-Zip",
                                    "description": "Embedded PE file"
                                })
                                
        except Exception as e:
            self.logger.error(f"7-Zip extraction failed: {e}")
        
        return extracted_files
    
    def _extract_with_binwalk(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract files using binwalk."""
        extracted_files = []
        
        try:
            # Use binwalk to analyze file
            cmd = ["binwalk", file_path]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                # Parse binwalk output
                lines = process.stdout.split('\n')
                for line in lines:
                    if 'PE32' in line or 'PE64' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            offset = parts[0]
                            extracted_files.append({
                                "filename": f"extracted_{offset}.exe",
                                "type": "PE",
                                "extraction_method": "binwalk",
                                "offset": offset,
                                "description": "Embedded PE file detected by binwalk"
                            })
                            
        except Exception as e:
            self.logger.error(f"Binwalk extraction failed: {e}")
        
        return extracted_files
    
    def _load_yara_rules(self) -> Dict[str, Any]:
        """Load YARA rules from the rules directory."""
        rules = {}
        rules_dir = Path("yara_rules")
        
        try:
            if rules_dir.exists():
                for rule_file in rules_dir.glob("*.yar"):
                    try:
                        rules[rule_file.stem] = yara.compile(str(rule_file))
                    except Exception as e:
                        self.logger.warning(f"Failed to load YARA rule {rule_file}: {e}")
        except Exception as e:
            self.logger.error(f"YARA rules loading failed: {e}")
        
        return rules