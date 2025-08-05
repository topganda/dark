"""
Hardware Warranty Checker System
Provides legitimate, AV-safe hardware warranty monitoring for defensive analysis.
This module demonstrates how to detect mining-related warranty issues and avoid them.
"""

import os
import sys
import time
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import psutil

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
class SMARTInfo:
    """SMART drive information."""
    drive_path: str
    power_on_hours: Optional[int]
    temperature_current: Optional[float]
    temperature_max: Optional[float]
    life_percentage: Optional[float]
    total_bytes_written: Optional[int]
    total_bytes_read: Optional[int]
    health_status: str
    timestamp: datetime

@dataclass
class GPUWarrantyInfo:
    """GPU warranty information."""
    gpu_model: str
    vendor: str
    serial_number: Optional[str]
    mining_flag: Optional[bool]
    lhr_status: Optional[bool]
    warranty_status: str
    warranty_expiry: Optional[datetime]
    timestamp: datetime

@dataclass
class WarrantyAlert:
    """Warranty alert information."""
    alert_type: str
    severity: str
    component: str
    description: str
    recommendation: str
    timestamp: datetime

class WarrantyChecker:
    """
    Hardware warranty checker for detecting mining-related warranty issues.
    
    This system demonstrates how to monitor hardware health and avoid
    warranty violations through legitimate resource management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Warranty thresholds
        self.warranty_thresholds = {
            "ssd_temp_warning": 75.0,      # °C
            "ssd_temp_critical": 80.0,     # °C
            "ssd_life_warning": 80.0,      # %
            "ssd_life_critical": 90.0,     # %
            "power_hours_warning": 8000,   # hours
            "power_hours_critical": 8760,  # hours (1 year)
            "gpu_temp_warning": 80.0,      # °C
            "gpu_temp_critical": 85.0,     # °C
        }
        
        # Vendor warranty policies
        self.vendor_policies = {
            "nvidia": {
                "mining_voids_warranty": True,
                "lhr_models": ["rtx 3060", "rtx 3070", "rtx 3080", "rtx 3090"],
                "warranty_portal": "https://www.nvidia.com/warranty-check"
            },
            "amd": {
                "mining_voids_warranty": False,
                "lhr_models": [],
                "warranty_portal": "https://support.amd.com"
            },
            "evga": {
                "mining_voids_warranty": True,
                "lhr_models": ["rtx 3060", "rtx 3070", "rtx 3080", "rtx 3090"],
                "warranty_portal": "https://www.evga.com/support"
            },
            "msi": {
                "mining_voids_warranty": True,
                "lhr_models": ["rtx 3060", "rtx 3070", "rtx 3080", "rtx 3090"],
                "warranty_portal": "https://www.msi.com/support"
            }
        }
        
        # Alert history
        self.alert_history = []
        self.max_alert_history = 100
        
        # Initialize monitoring
        self._initialize_monitoring()
        
        self.logger.info("Warranty Checker initialized")
    
    def _initialize_monitoring(self):
        """Initialize monitoring components."""
        try:
            if WMI_AVAILABLE:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized for warranty monitoring")
        except Exception as e:
            self.logger.error(f"Monitoring initialization failed: {e}")
    
    def check_smart_attributes(self, drive_path: str = None) -> SMARTInfo:
        """Check SMART attributes for a drive."""
        try:
            if not drive_path:
                # Get first available drive
                drives = self._get_available_drives()
                if drives:
                    drive_path = drives[0]
                else:
                    return self._create_default_smart_info("No drives found")
            
            smart_info = SMARTInfo(
                drive_path=drive_path,
                power_on_hours=None,
                temperature_current=None,
                temperature_max=None,
                life_percentage=None,
                total_bytes_written=None,
                total_bytes_read=None,
                health_status="Unknown",
                timestamp=datetime.now()
            )
            
            # Try to get SMART data using smartctl (Linux)
            if os.name == 'posix':
                smart_info = self._get_smartctl_info(drive_path)
            # Try to get SMART data using WMI (Windows)
            elif WMI_AVAILABLE:
                smart_info = self._get_wmi_smart_info(drive_path)
            
            # Fallback to basic drive info
            if smart_info.health_status == "Unknown":
                smart_info = self._get_basic_drive_info(drive_path)
            
            return smart_info
            
        except Exception as e:
            self.logger.error(f"SMART check failed for {drive_path}: {e}")
            return self._create_default_smart_info(drive_path)
    
    def _get_available_drives(self) -> List[str]:
        """Get list of available drives."""
        try:
            drives = []
            
            # Get disk partitions
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if partition.device not in drives:
                    drives.append(partition.device)
            
            return drives
            
        except Exception as e:
            self.logger.error(f"Failed to get available drives: {e}")
            return []
    
    def _get_smartctl_info(self, drive_path: str) -> SMARTInfo:
        """Get SMART information using smartctl (Linux)."""
        try:
            # Run smartctl command
            result = subprocess.run(
                ['smartctl', '-a', drive_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return self._create_default_smart_info(drive_path)
            
            output = result.stdout
            
            # Parse SMART attributes
            smart_info = SMARTInfo(
                drive_path=drive_path,
                power_on_hours=None,
                temperature_current=None,
                temperature_max=None,
                life_percentage=None,
                total_bytes_written=None,
                total_bytes_read=None,
                health_status="Good",
                timestamp=datetime.now()
            )
            
            # Parse power-on hours (Attribute 9)
            power_on_match = self._extract_smart_attribute(output, "9", "Power_On_Hours")
            if power_on_match:
                smart_info.power_on_hours = int(power_on_match)
            
            # Parse temperature (Attribute 194)
            temp_match = self._extract_smart_attribute(output, "194", "Temperature_Celsius")
            if temp_match:
                smart_info.temperature_current = float(temp_match)
            
            # Parse temperature (Attribute 190)
            temp_max_match = self._extract_smart_attribute(output, "190", "Airflow_Temperature_Cel")
            if temp_max_match:
                smart_info.temperature_max = float(temp_max_match)
            
            # Parse life percentage (Attribute 231)
            life_match = self._extract_smart_attribute(output, "231", "SSD_Life_Left")
            if life_match:
                smart_info.life_percentage = float(life_match)
            
            # Parse total bytes written (Attribute 241)
            written_match = self._extract_smart_attribute(output, "241", "Total_LBAs_Written")
            if written_match:
                smart_info.total_bytes_written = int(written_match) * 512  # Convert to bytes
            
            # Parse total bytes read (Attribute 242)
            read_match = self._extract_smart_attribute(output, "242", "Total_LBAs_Read")
            if read_match:
                smart_info.total_bytes_read = int(read_match) * 512  # Convert to bytes
            
            return smart_info
            
        except Exception as e:
            self.logger.error(f"smartctl parsing failed: {e}")
            return self._create_default_smart_info(drive_path)
    
    def _extract_smart_attribute(self, output: str, attribute_id: str, attribute_name: str) -> Optional[str]:
        """Extract SMART attribute value from smartctl output."""
        try:
            lines = output.split('\n')
            for line in lines:
                if attribute_id in line and attribute_name in line:
                    parts = line.split()
                    if len(parts) >= 10:
                        return parts[9]  # Raw value
            return None
        except Exception:
            return None
    
    def _get_wmi_smart_info(self, drive_path: str) -> SMARTInfo:
        """Get SMART information using WMI (Windows)."""
        try:
            smart_info = SMARTInfo(
                drive_path=drive_path,
                power_on_hours=None,
                temperature_current=None,
                temperature_max=None,
                life_percentage=None,
                total_bytes_written=None,
                total_bytes_read=None,
                health_status="Unknown",
                timestamp=datetime.now()
            )
            
            # Get disk information from WMI
            for disk in self.wmi.Win32_DiskDrive():
                if disk.DeviceID in drive_path or drive_path in disk.DeviceID:
                    # Get basic disk info
                    smart_info.health_status = "Good" if disk.Status == "OK" else "Warning"
                    break
            
            # Get disk usage statistics
            try:
                disk_usage = psutil.disk_usage(drive_path)
                # Estimate total bytes written based on usage
                smart_info.total_bytes_written = disk_usage.used
            except Exception:
                pass
            
            return smart_info
            
        except Exception as e:
            self.logger.error(f"WMI SMART info failed: {e}")
            return self._create_default_smart_info(drive_path)
    
    def _get_basic_drive_info(self, drive_path: str) -> SMARTInfo:
        """Get basic drive information as fallback."""
        try:
            disk_usage = psutil.disk_usage(drive_path)
            
            return SMARTInfo(
                drive_path=drive_path,
                power_on_hours=None,
                temperature_current=None,
                temperature_max=None,
                life_percentage=None,
                total_bytes_written=disk_usage.used,
                total_bytes_read=None,
                health_status="Unknown",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Basic drive info failed: {e}")
            return self._create_default_smart_info(drive_path)
    
    def _create_default_smart_info(self, drive_path: str) -> SMARTInfo:
        """Create default SMART info when detection fails."""
        return SMARTInfo(
            drive_path=drive_path,
            power_on_hours=None,
            temperature_current=None,
            temperature_max=None,
            life_percentage=None,
            total_bytes_written=None,
            total_bytes_read=None,
            health_status="Unknown",
            timestamp=datetime.now()
        )
    
    def check_gpu_warranty(self) -> GPUWarrantyInfo:
        """Check GPU warranty information."""
        try:
            gpu_info = GPUWarrantyInfo(
                gpu_model="Unknown",
                vendor="Unknown",
                serial_number=None,
                mining_flag=None,
                lhr_status=None,
                warranty_status="Unknown",
                warranty_expiry=None,
                timestamp=datetime.now()
            )
            
            # Try to get GPU information
            if WMI_AVAILABLE:
                gpu_info = self._get_wmi_gpu_info()
            
            # Determine vendor and check policies
            vendor = self._determine_gpu_vendor(gpu_info.gpu_model)
            gpu_info.vendor = vendor
            
            # Check if GPU has mining restrictions
            if vendor in self.vendor_policies:
                policy = self.vendor_policies[vendor]
                gpu_info.lhr_status = self._is_lhr_gpu(gpu_info.gpu_model, policy)
                gpu_info.mining_flag = policy["mining_voids_warranty"]
            
            # Set warranty status
            gpu_info.warranty_status = self._determine_warranty_status(gpu_info)
            
            return gpu_info
            
        except Exception as e:
            self.logger.error(f"GPU warranty check failed: {e}")
            return GPUWarrantyInfo(
                gpu_model="Unknown",
                vendor="Unknown",
                serial_number=None,
                mining_flag=None,
                lhr_status=None,
                warranty_status="Unknown",
                warranty_expiry=None,
                timestamp=datetime.now()
            )
    
    def _get_wmi_gpu_info(self) -> GPUWarrantyInfo:
        """Get GPU information using WMI."""
        try:
            gpu_info = GPUWarrantyInfo(
                gpu_model="Unknown",
                vendor="Unknown",
                serial_number=None,
                mining_flag=None,
                lhr_status=None,
                warranty_status="Unknown",
                warranty_expiry=None,
                timestamp=datetime.now()
            )
            
            for gpu in self.wmi.Win32_VideoController():
                gpu_info.gpu_model = gpu.Name
                gpu_info.serial_number = getattr(gpu, 'PNPDeviceID', None)
                break
            
            return gpu_info
            
        except Exception as e:
            self.logger.error(f"WMI GPU info failed: {e}")
            return GPUWarrantyInfo(
                gpu_model="Unknown",
                vendor="Unknown",
                serial_number=None,
                mining_flag=None,
                lhr_status=None,
                warranty_status="Unknown",
                warranty_expiry=None,
                timestamp=datetime.now()
            )
    
    def _determine_gpu_vendor(self, gpu_model: str) -> str:
        """Determine GPU vendor from model name."""
        gpu_lower = gpu_model.lower()
        
        if "nvidia" in gpu_lower or "rtx" in gpu_lower or "gtx" in gpu_lower:
            return "nvidia"
        elif "amd" in gpu_lower or "radeon" in gpu_lower or "rx" in gpu_lower:
            return "amd"
        elif "evga" in gpu_lower:
            return "evga"
        elif "msi" in gpu_lower:
            return "msi"
        else:
            return "Unknown"
    
    def _is_lhr_gpu(self, gpu_model: str, policy: Dict[str, Any]) -> bool:
        """Check if GPU is LHR (Lite Hash Rate) model."""
        gpu_lower = gpu_model.lower()
        
        for lhr_model in policy.get("lhr_models", []):
            if lhr_model.lower() in gpu_lower:
                return True
        
        return False
    
    def _determine_warranty_status(self, gpu_info: GPUWarrantyInfo) -> str:
        """Determine warranty status based on GPU information."""
        if gpu_info.vendor == "Unknown":
            return "Unknown"
        
        if gpu_info.vendor in self.vendor_policies:
            policy = self.vendor_policies[gpu_info.vendor]
            if policy["mining_voids_warranty"]:
                return "Mining may void warranty"
            else:
                return "Mining allowed"
        
        return "Unknown"
    
    def check_warranty_compliance(self) -> List[WarrantyAlert]:
        """Check overall warranty compliance and generate alerts."""
        alerts = []
        
        try:
            # Check SSD health
            smart_info = self.check_smart_attributes()
            alerts.extend(self._check_ssd_warranty(smart_info))
            
            # Check GPU warranty
            gpu_info = self.check_gpu_warranty()
            alerts.extend(self._check_gpu_warranty(gpu_info))
            
            # Store alerts
            self.alert_history.extend(alerts)
            if len(self.alert_history) > self.max_alert_history:
                self.alert_history = self.alert_history[-self.max_alert_history:]
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Warranty compliance check failed: {e}")
            return []
    
    def _check_ssd_warranty(self, smart_info: SMARTInfo) -> List[WarrantyAlert]:
        """Check SSD warranty compliance."""
        alerts = []
        
        try:
            # Check temperature
            if smart_info.temperature_current:
                if smart_info.temperature_current > self.warranty_thresholds["ssd_temp_critical"]:
                    alerts.append(WarrantyAlert(
                        alert_type="SSD_TEMPERATURE_CRITICAL",
                        severity="critical",
                        component="SSD",
                        description=f"SSD temperature {smart_info.temperature_current:.1f}°C exceeds critical threshold",
                        recommendation="Reduce workload and improve cooling immediately",
                        timestamp=datetime.now()
                    ))
                elif smart_info.temperature_current > self.warranty_thresholds["ssd_temp_warning"]:
                    alerts.append(WarrantyAlert(
                        alert_type="SSD_TEMPERATURE_WARNING",
                        severity="warning",
                        component="SSD",
                        description=f"SSD temperature {smart_info.temperature_current:.1f}°C is high",
                        recommendation="Monitor temperature and consider reducing workload",
                        timestamp=datetime.now()
                    ))
            
            # Check life percentage
            if smart_info.life_percentage:
                if smart_info.life_percentage < (100 - self.warranty_thresholds["ssd_life_critical"]):
                    alerts.append(WarrantyAlert(
                        alert_type="SSD_LIFE_CRITICAL",
                        severity="critical",
                        component="SSD",
                        description=f"SSD life remaining {smart_info.life_percentage:.1f}% is critical",
                        recommendation="Backup data and replace SSD soon",
                        timestamp=datetime.now()
                    ))
                elif smart_info.life_percentage < (100 - self.warranty_thresholds["ssd_life_warning"]):
                    alerts.append(WarrantyAlert(
                        alert_type="SSD_LIFE_WARNING",
                        severity="warning",
                        component="SSD",
                        description=f"SSD life remaining {smart_info.life_percentage:.1f}% is low",
                        recommendation="Monitor SSD health and plan replacement",
                        timestamp=datetime.now()
                    ))
            
            # Check power-on hours
            if smart_info.power_on_hours:
                if smart_info.power_on_hours > self.warranty_thresholds["power_hours_critical"]:
                    alerts.append(WarrantyAlert(
                        alert_type="POWER_HOURS_CRITICAL",
                        severity="critical",
                        component="SSD",
                        description=f"Power-on hours {smart_info.power_on_hours} exceeds critical threshold",
                        recommendation="Consider replacing SSD due to age",
                        timestamp=datetime.now()
                    ))
                elif smart_info.power_on_hours > self.warranty_thresholds["power_hours_warning"]:
                    alerts.append(WarrantyAlert(
                        alert_type="POWER_HOURS_WARNING",
                        severity="warning",
                        component="SSD",
                        description=f"Power-on hours {smart_info.power_on_hours} is high",
                        recommendation="Monitor SSD health and plan replacement",
                        timestamp=datetime.now()
                    ))
            
        except Exception as e:
            self.logger.error(f"SSD warranty check failed: {e}")
        
        return alerts
    
    def _check_gpu_warranty(self, gpu_info: GPUWarrantyInfo) -> List[WarrantyAlert]:
        """Check GPU warranty compliance."""
        alerts = []
        
        try:
            # Check if mining voids warranty
            if gpu_info.mining_flag:
                alerts.append(WarrantyAlert(
                    alert_type="GPU_MINING_WARRANTY",
                    severity="warning",
                    component="GPU",
                    description=f"GPU {gpu_info.gpu_model} warranty may be voided by mining",
                    recommendation="Check vendor warranty policy before mining",
                    timestamp=datetime.now()
                ))
            
            # Check LHR status
            if gpu_info.lhr_status:
                alerts.append(WarrantyAlert(
                    alert_type="GPU_LHR_DETECTED",
                    severity="info",
                    component="GPU",
                    description=f"GPU {gpu_info.gpu_model} has LHR (Lite Hash Rate) restrictions",
                    recommendation="Mining performance will be limited by LHR",
                    timestamp=datetime.now()
                ))
            
            # Check vendor-specific policies
            if gpu_info.vendor in self.vendor_policies:
                policy = self.vendor_policies[gpu_info.vendor]
                alerts.append(WarrantyAlert(
                    alert_type="GPU_VENDOR_POLICY",
                    severity="info",
                    component="GPU",
                    description=f"Vendor {gpu_info.vendor} policy: Mining {'voids' if policy['mining_voids_warranty'] else 'does not void'} warranty",
                    recommendation=f"Check warranty portal: {policy['warranty_portal']}",
                    timestamp=datetime.now()
                ))
            
        except Exception as e:
            self.logger.error(f"GPU warranty check failed: {e}")
        
        return alerts
    
    def get_warranty_recommendations(self) -> List[str]:
        """Get warranty compliance recommendations."""
        recommendations = []
        
        try:
            # Check current alerts
            alerts = self.check_warranty_compliance()
            
            # Generate recommendations based on alerts
            for alert in alerts:
                if alert.severity == "critical":
                    recommendations.append(f"🚨 CRITICAL: {alert.recommendation}")
                elif alert.severity == "warning":
                    recommendations.append(f"⚠️ WARNING: {alert.recommendation}")
                else:
                    recommendations.append(f"ℹ️ INFO: {alert.recommendation}")
            
            # Add general recommendations
            recommendations.append("💡 General warranty tips:")
            recommendations.append("   - Monitor hardware temperatures regularly")
            recommendations.append("   - Use proper cooling and ventilation")
            recommendations.append("   - Check vendor warranty policies before mining")
            recommendations.append("   - Keep hardware within recommended operating conditions")
            recommendations.append("   - Document hardware usage for warranty claims")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Warranty recommendations failed: {e}")
            return ["Error generating warranty recommendations"]
    
    def get_alert_history(self, hours: int = 24) -> List[WarrantyAlert]:
        """Get warranty alert history for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
    
    def export_warranty_report(self, output_path: str = None) -> str:
        """Export comprehensive warranty report."""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"warranty_report_{timestamp}.json"
            
            # Gather all warranty information
            smart_info = self.check_smart_attributes()
            gpu_info = self.check_gpu_warranty()
            alerts = self.check_warranty_compliance()
            recommendations = self.get_warranty_recommendations()
            
            # Create report
            report = {
                "timestamp": datetime.now().isoformat(),
                "smart_info": asdict(smart_info),
                "gpu_info": asdict(gpu_info),
                "alerts": [asdict(alert) for alert in alerts],
                "recommendations": recommendations,
                "vendor_policies": self.vendor_policies,
                "thresholds": self.warranty_thresholds
            }
            
            # Write report
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Warranty report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Warranty report export failed: {e}")
            return ""


def demo_warranty_checker():
    """Demo function to show how the warranty checker works."""
    print("🔍 Hardware Warranty Checker Demo")
    print("=" * 50)
    
    # Create sample config
    config = {
        "warranty_checker": {
            "enabled": True,
            "check_interval": 300,  # 5 minutes
            "alert_thresholds": {
                "ssd_temp_warning": 75.0,
                "ssd_temp_critical": 80.0,
                "gpu_temp_warning": 80.0,
                "gpu_temp_critical": 85.0
            }
        }
    }
    
    try:
        # Create warranty checker
        checker = WarrantyChecker(config)
        
        print("✅ Warranty Checker initialized")
        
        # Check SMART attributes
        print("\n🔍 Checking SMART attributes...")
        smart_info = checker.check_smart_attributes()
        print(f"✅ SMART check completed:")
        print(f"   - Drive: {smart_info.drive_path}")
        print(f"   - Health: {smart_info.health_status}")
        print(f"   - Temperature: {smart_info.temperature_current or 'N/A'}°C")
        print(f"   - Power-on hours: {smart_info.power_on_hours or 'N/A'}")
        print(f"   - Life percentage: {smart_info.life_percentage or 'N/A'}%")
        
        # Check GPU warranty
        print("\n🔍 Checking GPU warranty...")
        gpu_info = checker.check_gpu_warranty()
        print(f"✅ GPU warranty check completed:")
        print(f"   - Model: {gpu_info.gpu_model}")
        print(f"   - Vendor: {gpu_info.vendor}")
        print(f"   - LHR Status: {gpu_info.lhr_status or 'Unknown'}")
        print(f"   - Mining voids warranty: {gpu_info.mining_flag or 'Unknown'}")
        print(f"   - Warranty status: {gpu_info.warranty_status}")
        
        # Check warranty compliance
        print("\n🔍 Checking warranty compliance...")
        alerts = checker.check_warranty_compliance()
        print(f"✅ Warranty compliance check completed:")
        print(f"   - Alerts found: {len(alerts)}")
        
        for alert in alerts:
            print(f"   - {alert.severity.upper()}: {alert.description}")
        
        # Get recommendations
        print("\n💡 Getting warranty recommendations...")
        recommendations = checker.get_warranty_recommendations()
        print("✅ Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        
        # Export report
        print("\n📄 Exporting warranty report...")
        report_path = checker.export_warranty_report()
        print(f"✅ Warranty report exported to: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Warranty checker demo failed: {e}")
        return False


if __name__ == "__main__":
    demo_warranty_checker()