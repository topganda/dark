"""
Forensic Awareness & Detection Vector Monitoring System
Comprehensive monitoring of all possible detection vectors for unauthorized resource consumption.
This system helps identify and avoid forensic artifacts that could reveal mining activity.
"""

import os
import sys
import time
import json
import logging
import subprocess
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import platform

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

@dataclass
class ForensicArtifact:
    """Forensic artifact information."""
    category: str
    vector: str
    description: str
    severity: str  # "critical", "high", "medium", "low", "info"
    detection_method: str
    tools: List[str]
    mitigation: str
    timestamp: datetime

@dataclass
class DetectionVector:
    """Detection vector information."""
    category: str
    vector_name: str
    description: str
    detection_methods: List[str]
    forensic_tools: List[str]
    legal_implications: List[str]
    mitigation_strategies: List[str]
    risk_level: str

@dataclass
class ForensicAlert:
    """Forensic alert information."""
    alert_type: str
    severity: str
    category: str
    description: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class ForensicAwareness:
    """
    Comprehensive forensic awareness system for detecting all possible detection vectors.
    
    This system monitors and alerts on all forensic artifacts that could reveal
    unauthorized resource-consuming software activity.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Detection vectors database
        self.detection_vectors = self._load_detection_vectors()
        
        # Forensic artifacts history
        self.artifacts_history = []
        self.alerts_history = []
        self.max_history_size = 1000
        
        # Risk thresholds
        self.risk_thresholds = {
            "hardware_wear": 80.0,      # %
            "power_spike": 300.0,       # Watts
            "temp_critical": 75.0,      # °C
            "network_volume": 1000000,  # bytes
            "process_count": 100,       # processes
            "registry_entries": 50,     # entries
        }
        
        # Initialize monitoring
        self._initialize_monitoring()
        
        self.logger.info("Forensic Awareness System initialized")
    
    def _load_detection_vectors(self) -> Dict[str, DetectionVector]:
        """Load comprehensive detection vectors database."""
        return {
            "hardware_firmware": {
                "gpu_bios_mining_flag": DetectionVector(
                    category="Hardware & Firmware",
                    vector_name="GPU BIOS Mining Flag",
                    description="Vendor RMA portal reads 'mining workload' bit in GPU BIOS",
                    detection_methods=["Vendor RMA portal", "BIOS dump analysis", "Firmware inspection"],
                    forensic_tools=["GPU-Z", "AIDA64", "Vendor diagnostic tools"],
                    legal_implications=["Warranty void", "RMA rejection", "Legal liability"],
                    mitigation_strategies=["Use non-mining GPUs", "Avoid warranty claims", "Use legitimate workloads"],
                    risk_level="critical"
                ),
                "ssd_smart_counters": DetectionVector(
                    category="Hardware & Firmware",
                    vector_name="SSD SMART Counters",
                    description="Power-on hours > 8760, temperature > 75°C, wear leveling > 90%",
                    detection_methods=["SMART attribute monitoring", "Vendor diagnostic tools"],
                    forensic_tools=["smartctl", "CrystalDiskInfo", "HDDScan"],
                    legal_implications=["Warranty void", "RMA rejection"],
                    mitigation_strategies=["Use enterprise SSDs", "Monitor wear levels", "Proper cooling"],
                    risk_level="high"
                ),
                "cpu_microcode_patterns": DetectionVector(
                    category="Hardware & Firmware",
                    vector_name="CPU Microcode Patterns",
                    description="Intel PT / AMD IBS logs reveal sustained RandomX patterns",
                    detection_methods=["Performance counter analysis", "Microcode inspection"],
                    forensic_tools=["Intel PT", "AMD IBS", "Performance monitoring"],
                    legal_implications=["Hardware warranty issues"],
                    mitigation_strategies=["Use diverse workloads", "Avoid sustained patterns"],
                    risk_level="medium"
                ),
                "fan_rpm_cycles": DetectionVector(
                    category="Hardware & Firmware",
                    vector_name="Fan RPM Cycles",
                    description="BIOS logs > 1M revolutions in 3 months → mining signature",
                    detection_methods=["BIOS fan logs", "Thermal monitoring"],
                    forensic_tools=["BIOS inspection", "Fan monitoring tools"],
                    legal_implications=["Hardware warranty issues"],
                    mitigation_strategies=["Proper cooling", "Fan curve optimization"],
                    risk_level="medium"
                )
            },
            "operating_system": {
                "windows_registry": DetectionVector(
                    category="Operating System",
                    vector_name="Windows Registry Artifacts",
                    description="HKCU\\...\\Run\\ctfmon, HKLM\\...\\Services\\gupdatem",
                    detection_methods=["Registry analysis", "Autoruns monitoring"],
                    forensic_tools=["RegRipper", "Autoruns64", "Registry Explorer"],
                    legal_implications=["Forensic evidence", "Legal discovery"],
                    mitigation_strategies=["Use legitimate services", "Avoid suspicious names"],
                    risk_level="high"
                ),
                "scheduled_tasks": DetectionVector(
                    category="Operating System",
                    vector_name="Scheduled Tasks",
                    description="Scheduled task persistence mechanisms",
                    detection_methods=["Task scheduler analysis", "CSV export"],
                    forensic_tools=["schtasks", "Autoruns64", "Task Scheduler"],
                    legal_implications=["Forensic evidence", "Persistence detection"],
                    mitigation_strategies=["Use legitimate task names", "Avoid suspicious scheduling"],
                    risk_level="high"
                ),
                "event_logs": DetectionVector(
                    category="Operating System",
                    vector_name="Windows Event Logs",
                    description="Event ID 7045 (service install), ID 4104 (PowerShell script)",
                    detection_methods=["Event log analysis", "SIEM correlation"],
                    forensic_tools=["wevtutil", "Event Viewer", "Log Parser"],
                    legal_implications=["Audit trail", "Forensic evidence"],
                    mitigation_strategies=["Use legitimate installation methods", "Avoid PowerShell scripts"],
                    risk_level="high"
                ),
                "prefetch_amcache": DetectionVector(
                    category="Operating System",
                    vector_name="Prefetch / AmCache",
                    description="Executable hash + first-run timestamp (30-day retention)",
                    detection_methods=["Prefetch analysis", "AmCache inspection"],
                    forensic_tools=["Prefetch Explorer", "AmCache Parser"],
                    legal_implications=["Execution history", "Forensic timeline"],
                    mitigation_strategies=["Use legitimate executables", "Avoid suspicious names"],
                    risk_level="medium"
                ),
                "crash_dumps": DetectionVector(
                    category="Operating System",
                    vector_name="Crash Dumps",
                    description="C:\\Windows\\Minidump\\*.dmp contains full process list & stack",
                    detection_methods=["Crash dump analysis", "WER inspection"],
                    forensic_tools=["WinDbg", "Volatility", "Crash dump analyzer"],
                    legal_implications=["Process evidence", "Forensic analysis"],
                    mitigation_strategies=["Prevent crashes", "Use stable software"],
                    risk_level="medium"
                )
            },
            "network_telemetry": {
                "isp_dpi": DetectionVector(
                    category="Network Telemetry",
                    vector_name="ISP Deep Packet Inspection",
                    description="Stratum protocol (ports 3333, 4444, 10032) logged for 6-24 months",
                    detection_methods=["ISP DPI logs", "Traffic analysis"],
                    forensic_tools=["Wireshark", "Zeek", "Network monitoring"],
                    legal_implications=["ISP subpoena", "Legal discovery"],
                    mitigation_strategies=["Use VPN", "Encrypt traffic", "Use different ports"],
                    risk_level="critical"
                ),
                "dns_queries": DetectionVector(
                    category="Network Telemetry",
                    vector_name="DNS Queries",
                    description="api.ipify.org, gulf.moneroocean.stream → unencrypted logs",
                    detection_methods=["DNS log analysis", "ISP monitoring"],
                    forensic_tools=["nslookup", "dig", "DNS monitoring"],
                    legal_implications=["ISP subpoena", "DNS logging"],
                    mitigation_strategies=["Use DoH/DoT", "Use different domains", "VPN"],
                    risk_level="high"
                ),
                "pool_api_logs": DetectionVector(
                    category="Network Telemetry",
                    vector_name="Pool API Logs",
                    description="Wallet + IP + user-agent → subpoena to pool",
                    detection_methods=["Pool log analysis", "API monitoring"],
                    forensic_tools=["Pool API", "Network analysis"],
                    legal_implications=["Pool subpoena", "Identity revelation"],
                    mitigation_strategies=["Use different wallets", "Rotate IPs", "Use legitimate user-agents"],
                    risk_level="critical"
                ),
                "cloud_provider": DetectionVector(
                    category="Network Telemetry",
                    vector_name="Cloud Provider Logs",
                    description="AWS / Azure flow logs if VM is mining",
                    detection_methods=["Cloud flow logs", "Provider monitoring"],
                    forensic_tools=["Cloud monitoring", "Flow log analysis"],
                    legal_implications=["Provider subpoena", "Account termination"],
                    mitigation_strategies=["Use legitimate workloads", "Comply with ToS"],
                    risk_level="high"
                )
            },
            "power_utility": {
                "smart_meter": DetectionVector(
                    category="Power & Utility",
                    vector_name="Smart Meter Data",
                    description="15-min kWh spikes → subpoena to utility",
                    detection_methods=["Utility monitoring", "Power analysis"],
                    forensic_tools=["Smart meter data", "Power monitoring"],
                    legal_implications=["Utility subpoena", "Legal investigation"],
                    mitigation_strategies=["Use efficient hardware", "Spread load", "Legitimate workloads"],
                    risk_level="critical"
                ),
                "thermal_camera": DetectionVector(
                    category="Power & Utility",
                    vector_name="Thermal Camera Detection",
                    description="Heat signature from GPU/CPU during mining visible to drones",
                    detection_methods=["Thermal imaging", "IR detection"],
                    forensic_tools=["Thermal cameras", "IR sensors"],
                    legal_implications=["Physical evidence", "Neighbor reports"],
                    mitigation_strategies=["Proper cooling", "Insulation", "Legitimate workloads"],
                    risk_level="medium"
                ),
                "fire_department": DetectionVector(
                    category="Power & Utility",
                    vector_name="Fire Department Alerts",
                    description="Overheated rigs may trigger fire alarms → inspection",
                    detection_methods=["Fire alarm monitoring", "Thermal detection"],
                    forensic_tools=["Fire alarms", "Thermal sensors"],
                    legal_implications=["Emergency response", "Evidence seizure"],
                    mitigation_strategies=["Proper cooling", "Fire safety", "Legitimate workloads"],
                    risk_level="high"
                )
            },
            "blockchain_exchange": {
                "pool_payout_logs": DetectionVector(
                    category="Blockchain & Exchange",
                    vector_name="Pool Payout Logs",
                    description="Wallet → exchange KYC → identity revealed",
                    detection_methods=["Blockchain analysis", "Exchange KYC"],
                    forensic_tools=["Chainalysis", "Blockchain explorers"],
                    legal_implications=["Identity revelation", "Tax implications"],
                    mitigation_strategies=["Use privacy coins", "Mix transactions", "Legitimate mining"],
                    risk_level="critical"
                ),
                "monero_view_key": DetectionVector(
                    category="Blockchain & Exchange",
                    vector_name="Monero View Key",
                    description="If shared → all transactions de-anonymized",
                    detection_methods=["View key analysis", "Transaction correlation"],
                    forensic_tools=["Monero tools", "Blockchain analysis"],
                    legal_implications=["Privacy breach", "Transaction history"],
                    mitigation_strategies=["Never share view keys", "Use legitimate wallets"],
                    risk_level="critical"
                ),
                "exchange_1099": DetectionVector(
                    category="Blockchain & Exchange",
                    vector_name="Exchange 1099 Forms",
                    description="Earnings > $600 triggers IRS Form 1099-MISC",
                    detection_methods=["Tax monitoring", "Exchange reporting"],
                    forensic_tools=["Tax records", "Exchange reports"],
                    legal_implications=["Tax audit", "Legal compliance"],
                    mitigation_strategies=["Proper tax reporting", "Legitimate mining"],
                    risk_level="high"
                )
            },
            "social_human": {
                "exif_gps": DetectionVector(
                    category="Social & Human",
                    vector_name="EXIF GPS Data",
                    description="Photos of rigs posted on Discord / Twitter → GPS location",
                    detection_methods=["EXIF analysis", "Social media monitoring"],
                    forensic_tools=["exiftool", "Social media analysis"],
                    legal_implications=["Location revelation", "Physical evidence"],
                    mitigation_strategies=["Remove EXIF data", "Don't post photos", "Use legitimate setups"],
                    risk_level="medium"
                ),
                "discord_logs": DetectionVector(
                    category="Social & Human",
                    vector_name="Discord Server Logs",
                    description="Server message history (permanent) → IP + username",
                    detection_methods=["Discord log analysis", "Server monitoring"],
                    forensic_tools=["Discord API", "Server logs"],
                    legal_implications=["Identity revelation", "Communication history"],
                    mitigation_strategies=["Use legitimate channels", "Avoid suspicious discussions"],
                    risk_level="high"
                ),
                "reddit_posts": DetectionVector(
                    category="Social & Human",
                    vector_name="Reddit Posts",
                    description="Hardware flex posts → metadata + IP",
                    detection_methods=["Reddit analysis", "Post metadata"],
                    forensic_tools=["Reddit API", "Post analysis"],
                    legal_implications=["Identity revelation", "Public evidence"],
                    mitigation_strategies=["Don't post setups", "Use legitimate discussions"],
                    risk_level="medium"
                ),
                "invoice_warranty": DetectionVector(
                    category="Social & Human",
                    vector_name="Invoice / Warranty Claims",
                    description="Serial number → mining flag on vendor portal",
                    detection_methods=["Vendor portal analysis", "Warranty tracking"],
                    forensic_tools=["Vendor portals", "Warranty systems"],
                    legal_implications=["Warranty void", "Legal liability"],
                    mitigation_strategies=["Use legitimate hardware", "Avoid warranty claims"],
                    risk_level="high"
                )
            }
        }
    
    def _initialize_monitoring(self):
        """Initialize forensic monitoring components."""
        try:
            if WMI_AVAILABLE:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized for forensic monitoring")
        except Exception as e:
            self.logger.error(f"Forensic monitoring initialization failed: {e}")
    
    def check_hardware_artifacts(self) -> List[ForensicArtifact]:
        """Check for hardware-related forensic artifacts."""
        artifacts = []
        
        try:
            # Check SSD SMART attributes
            smart_artifacts = self._check_smart_artifacts()
            artifacts.extend(smart_artifacts)
            
            # Check GPU BIOS flags
            gpu_artifacts = self._check_gpu_artifacts()
            artifacts.extend(gpu_artifacts)
            
            # Check CPU patterns
            cpu_artifacts = self._check_cpu_artifacts()
            artifacts.extend(cpu_artifacts)
            
            # Check fan cycles
            fan_artifacts = self._check_fan_artifacts()
            artifacts.extend(fan_artifacts)
            
        except Exception as e:
            self.logger.error(f"Hardware artifacts check failed: {e}")
        
        return artifacts
    
    def _check_smart_artifacts(self) -> List[ForensicArtifact]:
        """Check SSD SMART attributes for mining indicators."""
        artifacts = []
        
        try:
            # Get disk information
            disks = psutil.disk_partitions()
            
            for disk in disks:
                try:
                    # Check if smartctl is available
                    result = subprocess.run(['smartctl', '-a', disk.device], 
                                          capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        output = result.stdout
                        
                        # Check power-on hours
                        if "Power_On_Hours" in output:
                            # Extract power-on hours
                            for line in output.split('\n'):
                                if "Power_On_Hours" in line:
                                    try:
                                        hours = int(line.split()[-1])
                                        if hours > 8760:  # 1 year
                                            artifacts.append(ForensicArtifact(
                                                category="Hardware & Firmware",
                                                vector="SSD Power-On Hours",
                                                description=f"SSD {disk.device} has {hours} power-on hours (>8760)",
                                                severity="high",
                                                detection_method="SMART attribute monitoring",
                                                tools=["smartctl", "CrystalDiskInfo"],
                                                mitigation="Use enterprise SSDs, monitor wear levels",
                                                timestamp=datetime.now()
                                            ))
                                    except (ValueError, IndexError):
                                        pass
                        
                        # Check temperature
                        if "Temperature_Celsius" in output:
                            for line in output.split('\n'):
                                if "Temperature_Celsius" in line:
                                    try:
                                        temp = int(line.split()[-1])
                                        if temp > 75:  # 75°C
                                            artifacts.append(ForensicArtifact(
                                                category="Hardware & Firmware",
                                                vector="SSD Temperature",
                                                description=f"SSD {disk.device} temperature {temp}°C (>75°C)",
                                                severity="high",
                                                detection_method="SMART temperature monitoring",
                                                tools=["smartctl", "CrystalDiskInfo"],
                                                mitigation="Improve cooling, monitor temperatures",
                                                timestamp=datetime.now()
                                            ))
                                    except (ValueError, IndexError):
                                        pass
                        
                except Exception as e:
                    self.logger.debug(f"SMART check failed for {disk.device}: {e}")
                    
        except Exception as e:
            self.logger.error(f"SMART artifacts check failed: {e}")
        
        return artifacts
    
    def _check_gpu_artifacts(self) -> List[ForensicArtifact]:
        """Check GPU BIOS for mining flags."""
        artifacts = []
        
        try:
            if WMI_AVAILABLE:
                for gpu in self.wmi.Win32_VideoController():
                    # Check for suspicious GPU names or properties
                    gpu_name = gpu.Name.lower()
                    
                    # Check for mining-related indicators
                    mining_indicators = ["mining", "lhr", "hash", "crypto"]
                    for indicator in mining_indicators:
                        if indicator in gpu_name:
                            artifacts.append(ForensicArtifact(
                                category="Hardware & Firmware",
                                vector="GPU Mining Indicators",
                                description=f"GPU {gpu.Name} contains mining-related indicators",
                                severity="medium",
                                detection_method="GPU name analysis",
                                tools=["GPU-Z", "AIDA64"],
                                mitigation="Use legitimate GPU names, avoid mining indicators",
                                timestamp=datetime.now()
                            ))
                            break
                            
        except Exception as e:
            self.logger.error(f"GPU artifacts check failed: {e}")
        
        return artifacts
    
    def _check_cpu_artifacts(self) -> List[ForensicArtifact]:
        """Check CPU for mining-related patterns."""
        artifacts = []
        
        try:
            # Check CPU usage patterns
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Check for sustained high CPU usage
            if cpu_percent > 80:
                artifacts.append(ForensicArtifact(
                    category="Hardware & Firmware",
                    vector="CPU Usage Pattern",
                    description=f"High CPU usage detected: {cpu_percent}%",
                    severity="medium",
                    detection_method="CPU usage monitoring",
                    tools=["Task Manager", "Performance Monitor"],
                    mitigation="Use legitimate workloads, monitor CPU usage",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
            self.logger.error(f"CPU artifacts check failed: {e}")
        
        return artifacts
    
    def _check_fan_artifacts(self) -> List[ForensicArtifact]:
        """Check fan cycles for mining indicators."""
        artifacts = []
        
        try:
            # This would require platform-specific implementation
            # For now, return empty list
            pass
            
        except Exception as e:
            self.logger.error(f"Fan artifacts check failed: {e}")
        
        return artifacts
    
    def check_os_artifacts(self) -> List[ForensicArtifact]:
        """Check for operating system forensic artifacts."""
        artifacts = []
        
        try:
            # Check registry artifacts
            registry_artifacts = self._check_registry_artifacts()
            artifacts.extend(registry_artifacts)
            
            # Check scheduled tasks
            task_artifacts = self._check_scheduled_tasks()
            artifacts.extend(task_artifacts)
            
            # Check event logs
            event_artifacts = self._check_event_logs()
            artifacts.extend(event_artifacts)
            
            # Check prefetch/amcache
            prefetch_artifacts = self._check_prefetch_artifacts()
            artifacts.extend(prefetch_artifacts)
            
        except Exception as e:
            self.logger.error(f"OS artifacts check failed: {e}")
        
        return artifacts
    
    def _check_registry_artifacts(self) -> List[ForensicArtifact]:
        """Check Windows registry for mining artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious registry entries
            suspicious_keys = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SYSTEM\CurrentControlSet\Services"
            ]
            
            suspicious_names = ["ctfmon", "gupdatem", "miner", "xmrig", "crypto"]
            
            # This would require registry access
            # For demonstration, create a generic artifact
            artifacts.append(ForensicArtifact(
                category="Operating System",
                vector="Registry Persistence",
                description="Registry persistence mechanisms should be monitored",
                severity="high",
                detection_method="Registry analysis",
                tools=["RegRipper", "Autoruns64"],
                mitigation="Use legitimate services, avoid suspicious names",
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Registry artifacts check failed: {e}")
        
        return artifacts
    
    def _check_scheduled_tasks(self) -> List[ForensicArtifact]:
        """Check scheduled tasks for mining artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious scheduled tasks
            suspicious_tasks = ["Ddriver", "miner", "xmrig", "crypto"]
            
            # This would require task scheduler access
            # For demonstration, create a generic artifact
            artifacts.append(ForensicArtifact(
                category="Operating System",
                vector="Scheduled Tasks",
                description="Scheduled task persistence should be monitored",
                severity="high",
                detection_method="Task scheduler analysis",
                tools=["schtasks", "Autoruns64"],
                mitigation="Use legitimate task names, avoid suspicious scheduling",
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Scheduled tasks check failed: {e}")
        
        return artifacts
    
    def _check_event_logs(self) -> List[ForensicArtifact]:
        """Check Windows event logs for mining artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious event IDs
            suspicious_events = [7045, 4104]  # Service install, PowerShell script
            
            artifacts.append(ForensicArtifact(
                category="Operating System",
                vector="Event Logs",
                description="Windows event logs should be monitored for suspicious activity",
                severity="high",
                detection_method="Event log analysis",
                tools=["wevtutil", "Event Viewer"],
                mitigation="Use legitimate installation methods, avoid PowerShell scripts",
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Event logs check failed: {e}")
        
        return artifacts
    
    def _check_prefetch_artifacts(self) -> List[ForensicArtifact]:
        """Check prefetch/amcache for mining artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious executables in prefetch
            suspicious_executables = ["xmrig.exe", "miner.exe", "crypto.exe"]
            
            artifacts.append(ForensicArtifact(
                category="Operating System",
                vector="Prefetch / AmCache",
                description="Prefetch and AmCache should be monitored for suspicious executables",
                severity="medium",
                detection_method="Prefetch analysis",
                tools=["Prefetch Explorer", "AmCache Parser"],
                mitigation="Use legitimate executables, avoid suspicious names",
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Prefetch artifacts check failed: {e}")
        
        return artifacts
    
    def check_network_artifacts(self) -> List[ForensicArtifact]:
        """Check for network-related forensic artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious network connections
            connections = psutil.net_connections()
            
            suspicious_ports = [3333, 4444, 10032]  # Stratum ports
            suspicious_domains = ["api.ipify.org", "gulf.moneroocean.stream", "nicehash.com"]
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    # Check for suspicious ports
                    if conn.raddr and conn.raddr.port in suspicious_ports:
                        artifacts.append(ForensicArtifact(
                            category="Network Telemetry",
                            vector="Suspicious Network Ports",
                            description=f"Connection to suspicious port {conn.raddr.port}",
                            severity="critical",
                            detection_method="Network connection analysis",
                            tools=["netstat", "Wireshark", "Zeek"],
                            mitigation="Use VPN, encrypt traffic, use different ports",
                            timestamp=datetime.now()
                        ))
            
            # Check for suspicious DNS queries
            artifacts.append(ForensicArtifact(
                category="Network Telemetry",
                vector="DNS Queries",
                description="DNS queries to mining-related domains should be monitored",
                severity="high",
                detection_method="DNS log analysis",
                tools=["nslookup", "dig", "DNS monitoring"],
                mitigation="Use DoH/DoT, use different domains, VPN",
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Network artifacts check failed: {e}")
        
        return artifacts
    
    def check_power_artifacts(self) -> List[ForensicArtifact]:
        """Check for power-related forensic artifacts."""
        artifacts = []
        
        try:
            # Check battery and power status
            battery = psutil.sensors_battery()
            
            if battery:
                # Check for high power consumption
                if not battery.power_plugged and battery.percent < 50:
                    artifacts.append(ForensicArtifact(
                        category="Power & Utility",
                        vector="High Power Consumption",
                        description=f"High power consumption detected: battery at {battery.percent}%",
                        severity="medium",
                        detection_method="Power monitoring",
                        tools=["Power monitoring", "Smart meter data"],
                        mitigation="Use efficient hardware, spread load, legitimate workloads",
                        timestamp=datetime.now()
                    ))
            
            # Check for thermal issues
            try:
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current > 75:  # 75°C
                            artifacts.append(ForensicArtifact(
                                category="Power & Utility",
                                vector="High Temperature",
                                description=f"High temperature detected: {entry.current}°C",
                                severity="high",
                                detection_method="Thermal monitoring",
                                tools=["Thermal monitoring", "Thermal cameras"],
                                mitigation="Improve cooling, monitor temperatures",
                                timestamp=datetime.now()
                            ))
            except Exception:
                pass
                
        except Exception as e:
            self.logger.error(f"Power artifacts check failed: {e}")
        
        return artifacts
    
    def check_social_artifacts(self) -> List[ForensicArtifact]:
        """Check for social media and human factor artifacts."""
        artifacts = []
        
        try:
            # Check for suspicious files that might contain social media evidence
            suspicious_patterns = ["discord", "reddit", "twitter", "telegram", "mining", "rig"]
            
            # Check user profile for suspicious files
            user_profile = os.path.expanduser("~")
            
            for root, dirs, files in os.walk(user_profile):
                for file in files:
                    file_lower = file.lower()
                    for pattern in suspicious_patterns:
                        if pattern in file_lower:
                            artifacts.append(ForensicArtifact(
                                category="Social & Human",
                                vector="Suspicious Files",
                                description=f"Suspicious file found: {file}",
                                severity="medium",
                                detection_method="File system analysis",
                                tools=["File analysis", "EXIF analysis"],
                                mitigation="Remove suspicious files, don't post evidence",
                                timestamp=datetime.now()
                            ))
                            break
                            
        except Exception as e:
            self.logger.error(f"Social artifacts check failed: {e}")
        
        return artifacts
    
    def run_comprehensive_forensic_scan(self) -> Dict[str, Any]:
        """Run comprehensive forensic scan for all detection vectors."""
        try:
            self.logger.info("Starting comprehensive forensic scan...")
            
            # Check all artifact categories
            hardware_artifacts = self.check_hardware_artifacts()
            os_artifacts = self.check_os_artifacts()
            network_artifacts = self.check_network_artifacts()
            power_artifacts = self.check_power_artifacts()
            social_artifacts = self.check_social_artifacts()
            
            # Combine all artifacts
            all_artifacts = (hardware_artifacts + os_artifacts + 
                           network_artifacts + power_artifacts + social_artifacts)
            
            # Store in history
            self.artifacts_history.extend(all_artifacts)
            if len(self.artifacts_history) > self.max_history_size:
                self.artifacts_history = self.artifacts_history[-self.max_history_size:]
            
            # Generate alerts
            alerts = self._generate_forensic_alerts(all_artifacts)
            
            # Calculate risk scores
            risk_scores = self._calculate_risk_scores(all_artifacts)
            
            # Generate recommendations
            recommendations = self._generate_forensic_recommendations(all_artifacts)
             
             return {
                 "timestamp": datetime.now().isoformat(),
                 "artifacts_found": len(all_artifacts),
                 "alerts_generated": len(alerts),
                 "risk_level": self._determine_overall_risk(risk_scores),
                 "artifacts": [asdict(artifact) for artifact in all_artifacts],
                 "alerts": [asdict(alert) for alert in alerts],
                 "risk_scores": risk_scores,
                 "recommendations": recommendations,
                 "detection_vectors": {k: {sk: asdict(sv) for sk, sv in sv.items()} for k, sv in self.detection_vectors.items()}
             }
            
        except Exception as e:
            self.logger.error(f"Comprehensive forensic scan failed: {e}")
            return {"error": str(e)}
    
    def _generate_forensic_alerts(self, artifacts: List[ForensicArtifact]) -> List[ForensicAlert]:
        """Generate forensic alerts based on artifacts."""
        alerts = []
        
        try:
            # Group artifacts by severity
            critical_artifacts = [a for a in artifacts if a.severity == "critical"]
            high_artifacts = [a for a in artifacts if a.severity == "high"]
            medium_artifacts = [a for a in artifacts if a.severity == "medium"]
            
            # Generate critical alerts
            if critical_artifacts:
                alerts.append(ForensicAlert(
                    alert_type="CRITICAL_FORENSIC_ARTIFACTS",
                    severity="critical",
                    category="Forensic Detection",
                    description=f"Found {len(critical_artifacts)} critical forensic artifacts",
                    evidence={"artifacts": [asdict(a) for a in critical_artifacts]},
                    recommendations=[
                        "Immediate action required",
                        "Review all critical artifacts",
                        "Implement mitigation strategies",
                        "Consider legal implications"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Generate high severity alerts
            if high_artifacts:
                alerts.append(ForensicAlert(
                    alert_type="HIGH_FORENSIC_ARTIFACTS",
                    severity="high",
                    category="Forensic Detection",
                    description=f"Found {len(high_artifacts)} high-severity forensic artifacts",
                    evidence={"artifacts": [asdict(a) for a in high_artifacts]},
                    recommendations=[
                        "Review high-severity artifacts",
                        "Implement mitigation strategies",
                        "Monitor for additional artifacts"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Store alerts in history
            self.alerts_history.extend(alerts)
            if len(self.alerts_history) > self.max_history_size:
                self.alerts_history = self.alerts_history[-self.max_history_size:]
                
        except Exception as e:
            self.logger.error(f"Forensic alert generation failed: {e}")
        
        return alerts
    
    def _calculate_risk_scores(self, artifacts: List[ForensicArtifact]) -> Dict[str, float]:
        """Calculate risk scores for different categories."""
        risk_scores = {
            "hardware": 0.0,
            "operating_system": 0.0,
            "network": 0.0,
            "power": 0.0,
            "social": 0.0,
            "overall": 0.0
        }
        
        try:
            # Calculate category-specific risk scores
            for artifact in artifacts:
                category = artifact.category.lower().replace(" & ", "_").replace(" ", "_")
                
                # Assign risk weights based on severity
                if artifact.severity == "critical":
                    weight = 1.0
                elif artifact.severity == "high":
                    weight = 0.7
                elif artifact.severity == "medium":
                    weight = 0.4
                elif artifact.severity == "low":
                    weight = 0.2
                else:
                    weight = 0.1
                
                # Add to category score
                if category in risk_scores:
                    risk_scores[category] += weight
            
            # Normalize scores to 0-100 range
            for category in risk_scores:
                risk_scores[category] = min(100.0, risk_scores[category] * 10)
            
            # Calculate overall risk
            category_scores = [v for k, v in risk_scores.items() if k != "overall"]
            risk_scores["overall"] = sum(category_scores) / len(category_scores)
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {e}")
        
        return risk_scores
    
    def _determine_overall_risk(self, risk_scores: Dict[str, float]) -> str:
        """Determine overall risk level."""
        overall_score = risk_scores.get("overall", 0.0)
        
        if overall_score >= 80:
            return "CRITICAL"
        elif overall_score >= 60:
            return "HIGH"
        elif overall_score >= 40:
            return "MEDIUM"
        elif overall_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_forensic_recommendations(self, artifacts: List[ForensicArtifact]) -> List[str]:
        """Generate forensic recommendations based on artifacts."""
        recommendations = []
        
        try:
            # Add general recommendations
            recommendations.append("🔍 Forensic Awareness Recommendations:")
            
            # Hardware recommendations
            hardware_artifacts = [a for a in artifacts if "Hardware" in a.category]
            if hardware_artifacts:
                recommendations.append("   - Monitor hardware wear levels and temperatures")
                recommendations.append("   - Use enterprise-grade hardware for intensive workloads")
                recommendations.append("   - Implement proper cooling and thermal management")
            
            # OS recommendations
            os_artifacts = [a for a in artifacts if "Operating System" in a.category]
            if os_artifacts:
                recommendations.append("   - Use legitimate installation methods")
                recommendations.append("   - Avoid suspicious service names and registry entries")
                recommendations.append("   - Monitor event logs for suspicious activity")
            
            # Network recommendations
            network_artifacts = [a for a in artifacts if "Network" in a.category]
            if network_artifacts:
                recommendations.append("   - Use VPN for network traffic")
                recommendations.append("   - Implement traffic encryption")
                recommendations.append("   - Monitor DNS queries and network connections")
            
            # Power recommendations
            power_artifacts = [a for a in artifacts if "Power" in a.category]
            if power_artifacts:
                recommendations.append("   - Monitor power consumption patterns")
                recommendations.append("   - Implement efficient hardware usage")
                recommendations.append("   - Use legitimate workloads to avoid power spikes")
            
            # Social recommendations
            social_artifacts = [a for a in artifacts if "Social" in a.category]
            if social_artifacts:
                recommendations.append("   - Remove EXIF data from photos")
                recommendations.append("   - Avoid posting hardware setups online")
                recommendations.append("   - Use legitimate communication channels")
            
            # Legal recommendations
            recommendations.append("   - Ensure compliance with local laws and regulations")
            recommendations.append("   - Use legitimate software and hardware")
            recommendations.append("   - Maintain proper documentation for all activities")
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            recommendations.append("Error generating recommendations")
        
        return recommendations
    
    def get_forensic_report(self, output_path: str = None) -> str:
        """Generate comprehensive forensic report."""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"forensic_report_{timestamp}.json"
            
            # Run comprehensive scan
            scan_results = self.run_comprehensive_forensic_scan()
            
            # Write report
            with open(output_path, 'w') as f:
                json.dump(scan_results, f, indent=2, default=str)
            
            self.logger.info(f"Forensic report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Forensic report generation failed: {e}")
            return ""


def demo_forensic_awareness():
    """Demo function to show how the forensic awareness system works."""
    print("🔍 Forensic Awareness & Detection Vector Monitoring Demo")
    print("=" * 60)
    
    # Create sample config
    config = {
        "forensic_awareness": {
            "enabled": True,
            "scan_interval": 300,  # 5 minutes
            "risk_thresholds": {
                "hardware_wear": 80.0,
                "power_spike": 300.0,
                "temp_critical": 75.0
            }
        }
    }
    
    try:
        # Create forensic awareness system
        forensic = ForensicAwareness(config)
        
        print("✅ Forensic Awareness System initialized")
        print(f"🔍 Detection vectors loaded: {len(forensic.detection_vectors)} categories")
        
        # Run comprehensive forensic scan
        print("\n🔍 Running comprehensive forensic scan...")
        scan_results = forensic.run_comprehensive_forensic_scan()
        
        if "error" in scan_results:
            print(f"❌ Forensic scan failed: {scan_results['error']}")
            return False
        
        print(f"✅ Forensic scan completed:")
        print(f"   - Artifacts found: {scan_results['artifacts_found']}")
        print(f"   - Alerts generated: {scan_results['alerts_generated']}")
        print(f"   - Risk level: {scan_results['risk_level']}")
        
        # Show risk scores
        risk_scores = scan_results.get('risk_scores', {})
        print(f"\n📊 Risk Scores:")
        for category, score in risk_scores.items():
            print(f"   - {category.replace('_', ' ').title()}: {score:.1f}%")
        
        # Show recommendations
        recommendations = scan_results.get('recommendations', [])
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        
        # Generate report
        print("\n📄 Generating forensic report...")
        report_path = forensic.get_forensic_report()
        print(f"✅ Forensic report generated: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Forensic awareness demo failed: {e}")
        return False


if __name__ == "__main__":
    demo_forensic_awareness()