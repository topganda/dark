"""
Transparent System Administration & Resource Management Module
Educational content for understanding system administration and resource management.
This module provides theoretical knowledge and defensive analysis capabilities only.
NO ACTUAL SYSTEM MODIFICATIONS OR UNAUTHORIZED ACCESS OCCURS.
"""

import json
import subprocess
import psutil
import platform
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

@dataclass
class SystemResource:
    """System resource information for educational purposes."""
    resource_type: str
    current_usage: float
    total_capacity: float
    usage_percentage: float
    educational_notes: List[str]

@dataclass
class PowerManagement:
    """Power management information for educational purposes."""
    power_source: str
    battery_level: float
    power_consumption: float
    thermal_status: str
    educational_notes: List[str]

@dataclass
class SystemConfiguration:
    """System configuration information for educational purposes."""
    config_type: str
    current_value: str
    recommended_value: str
    educational_purpose: str
    implementation_notes: List[str]

@dataclass
class MonitoringScript:
    """Sample monitoring script for educational purposes."""
    script_name: str
    description: str
    script_content: str
    platform: str
    educational_purpose: str
    usage_notes: List[str]

@dataclass
class ResourceLimit:
    """Resource limit configuration for educational purposes."""
    resource_type: str
    limit_value: str
    enforcement_method: str
    educational_purpose: str
    implementation_notes: List[str]

class SystemAdministration:
    """
    Educational module for understanding system administration and resource management.
    
    This module provides theoretical knowledge and defensive analysis capabilities.
    NO ACTUAL SYSTEM MODIFICATIONS OR UNAUTHORIZED ACCESS OCCURS.
    """
    
    def __init__(self):
        self.system_resources = {}
        self.power_management = {}
        self.system_configurations = {}
        self.monitoring_scripts = self._load_monitoring_scripts()
        self.resource_limits = self._load_resource_limits()
        
    def _load_monitoring_scripts(self) -> Dict[str, MonitoringScript]:
        """Load sample monitoring scripts for educational purposes."""
        return {
            "cpu_monitor": MonitoringScript(
                script_name="CPU Usage Monitor",
                description="Monitor CPU usage and identify high-usage processes",
                script_content="""
#!/bin/bash
# Educational CPU monitoring script
# FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL SYSTEM MODIFICATIONS

echo "=== CPU Usage Monitor ==="
echo "Timestamp: $(date)"
echo ""

# Get overall CPU usage
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "Overall CPU Usage: ${cpu_usage}%"

# Get top CPU-consuming processes
echo ""
echo "Top CPU-Consuming Processes:"
ps aux --sort=-%cpu | head -10

# Check for suspicious processes
echo ""
echo "Checking for potential mining processes:"
ps aux | grep -i "xmrig\\|miner\\|crypto\\|hash" | grep -v grep || echo "No obvious mining processes found"

echo ""
echo "=== End CPU Monitor ==="
""",
                platform="Linux",
                educational_purpose="Demonstrate CPU monitoring techniques for detecting unauthorized resource usage",
                usage_notes=[
                    "Run with appropriate permissions",
                    "Monitor output for unusual patterns",
                    "Set up automated monitoring",
                    "Configure alerts for high usage"
                ]
            ),
            "memory_monitor": MonitoringScript(
                script_name="Memory Usage Monitor",
                description="Monitor memory usage and identify memory-intensive processes",
                script_content="""
#!/bin/bash
# Educational memory monitoring script
# FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL SYSTEM MODIFICATIONS

echo "=== Memory Usage Monitor ==="
echo "Timestamp: $(date)"
echo ""

# Get memory information
free -h
echo ""

# Get top memory-consuming processes
echo "Top Memory-Consuming Processes:"
ps aux --sort=-%mem | head -10

# Check for processes using large amounts of memory
echo ""
echo "Processes using >100MB of memory:"
ps aux | awk '$6 > 100000 {print $0}' | head -10

echo ""
echo "=== End Memory Monitor ==="
""",
                platform="Linux",
                educational_purpose="Demonstrate memory monitoring techniques for detecting resource abuse",
                usage_notes=[
                    "Monitor for unusual memory patterns",
                    "Set up memory usage alerts",
                    "Track memory usage over time",
                    "Identify memory leaks"
                ]
            ),
            "network_monitor": MonitoringScript(
                script_name="Network Connection Monitor",
                description="Monitor network connections and identify suspicious traffic",
                script_content="""
#!/bin/bash
# Educational network monitoring script
# FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL SYSTEM MODIFICATIONS

echo "=== Network Connection Monitor ==="
echo "Timestamp: $(date)"
echo ""

# Get active network connections
echo "Active Network Connections:"
netstat -tuln | head -20

# Check for connections to known mining pool ports
echo ""
echo "Checking for mining pool connections:"
netstat -tuln | grep -E ":(3333|14444|10032|8080|8888)" || echo "No mining pool port connections found"

# Get process network usage
echo ""
echo "Process Network Usage:"
ss -tuln | head -10

echo ""
echo "=== End Network Monitor ==="
""",
                platform="Linux",
                educational_purpose="Demonstrate network monitoring techniques for detecting mining traffic",
                usage_notes=[
                    "Monitor for connections to mining pools",
                    "Track network usage patterns",
                    "Set up network alerts",
                    "Analyze traffic patterns"
                ]
            ),
            "windows_monitor": MonitoringScript(
                script_name="Windows System Monitor",
                description="Monitor Windows system resources using PowerShell",
                script_content="""
# Educational Windows monitoring script
# FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL SYSTEM MODIFICATIONS

Write-Host "=== Windows System Monitor ===" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Get CPU usage
$cpu = Get-Counter "\\Processor(_Total)\\% Processor Time"
Write-Host "CPU Usage: $($cpu.CounterSamples.CookedValue)%" -ForegroundColor Cyan

# Get memory usage
$memory = Get-Counter "\\Memory\\Available MBytes"
$totalMemory = (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1MB
$usedMemory = $totalMemory - $memory.CounterSamples.CookedValue
$memoryPercent = ($usedMemory / $totalMemory) * 100
Write-Host "Memory Usage: $([math]::Round($memoryPercent, 2))%" -ForegroundColor Cyan

# Get top processes by CPU
Write-Host ""
Write-Host "Top CPU-Consuming Processes:" -ForegroundColor Green
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table Name, CPU, WorkingSet -AutoSize

# Check for suspicious processes
Write-Host ""
Write-Host "Checking for potential mining processes:" -ForegroundColor Green
Get-Process | Where-Object {$_.ProcessName -match "xmrig|miner|crypto|hash"} | Format-Table Name, CPU, WorkingSet -AutoSize

Write-Host ""
Write-Host "=== End Windows Monitor ===" -ForegroundColor Green
""",
                platform="Windows",
                educational_purpose="Demonstrate Windows system monitoring techniques",
                usage_notes=[
                    "Run PowerShell as administrator if needed",
                    "Monitor for unusual process patterns",
                    "Set up scheduled monitoring",
                    "Configure Windows Event Log monitoring"
                ]
            )
        }
    
    def _load_resource_limits(self) -> Dict[str, ResourceLimit]:
        """Load resource limit configurations for educational purposes."""
        return {
            "cpu_limit": ResourceLimit(
                resource_type="CPU Usage Limit",
                limit_value="80%",
                enforcement_method="cgroups (Linux), Job Objects (Windows)",
                educational_purpose="Prevent excessive CPU usage by limiting process resource consumption",
                implementation_notes=[
                    "Use cgroups on Linux to limit CPU usage",
                    "Use Job Objects on Windows for process limits",
                    "Monitor and enforce limits automatically",
                    "Configure alerts when limits are approached"
                ]
            ),
            "memory_limit": ResourceLimit(
                resource_type="Memory Usage Limit",
                limit_value="2GB per process",
                enforcement_method="cgroups (Linux), Memory Limits (Windows)",
                educational_purpose="Prevent memory exhaustion by limiting process memory usage",
                implementation_notes=[
                    "Set memory limits in cgroups",
                    "Use Windows memory limits",
                    "Monitor memory usage patterns",
                    "Configure swap limits if needed"
                ]
            ),
            "network_limit": ResourceLimit(
                resource_type="Network Bandwidth Limit",
                limit_value="10MB/s per process",
                enforcement_method="tc (Linux), QoS (Windows)",
                educational_purpose="Prevent network abuse by limiting bandwidth usage",
                implementation_notes=[
                    "Use tc (traffic control) on Linux",
                    "Configure QoS policies on Windows",
                    "Monitor network usage patterns",
                    "Set up bandwidth alerts"
                ]
            ),
            "disk_limit": ResourceLimit(
                resource_type="Disk I/O Limit",
                limit_value="50MB/s read, 25MB/s write",
                enforcement_method="cgroups (Linux), I/O Limits (Windows)",
                educational_purpose="Prevent disk I/O abuse by limiting read/write speeds",
                implementation_notes=[
                    "Use cgroups blkio controller",
                    "Configure Windows I/O limits",
                    "Monitor disk usage patterns",
                    "Set up I/O alerts"
                ]
            )
        }
    
    def get_system_resources(self) -> Dict[str, SystemResource]:
        """Get current system resource information for educational purposes."""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network information
            network = psutil.net_io_counters()
            network_total = network.bytes_sent + network.bytes_recv
            
            self.system_resources = {
                "cpu": SystemResource(
                    resource_type="CPU",
                    current_usage=cpu_percent,
                    total_capacity=cpu_count * 100,  # Theoretical max
                    usage_percentage=cpu_percent,
                    educational_notes=[
                        "High CPU usage may indicate mining activity",
                        "Monitor for sustained high usage patterns",
                        "Check for unknown processes consuming CPU",
                        "Use process monitoring tools for detailed analysis"
                    ]
                ),
                "memory": SystemResource(
                    resource_type="Memory",
                    current_usage=memory.used / (1024**3),  # GB
                    total_capacity=memory.total / (1024**3),  # GB
                    usage_percentage=memory_percent,
                    educational_notes=[
                        "High memory usage may indicate mining software",
                        "Monitor for memory leaks or excessive usage",
                        "Check for processes using large amounts of memory",
                        "Use memory profiling tools for analysis"
                    ]
                ),
                "disk": SystemResource(
                    resource_type="Disk",
                    current_usage=disk.used / (1024**3),  # GB
                    total_capacity=disk.total / (1024**3),  # GB
                    usage_percentage=disk_percent,
                    educational_notes=[
                        "Monitor disk usage for mining software installation",
                        "Check for unusual file growth patterns",
                        "Monitor disk I/O for mining activity",
                        "Use disk monitoring tools for analysis"
                    ]
                ),
                "network": SystemResource(
                    resource_type="Network",
                    current_usage=network_total / (1024**2),  # MB
                    total_capacity=float('inf'),  # Unlimited
                    usage_percentage=0,  # Not applicable
                    educational_notes=[
                        "Monitor network traffic for mining pool connections",
                        "Check for connections to known mining ports",
                        "Monitor bandwidth usage patterns",
                        "Use network monitoring tools for analysis"
                    ]
                )
            }
            
            return self.system_resources
            
        except Exception as e:
            return {
                "error": SystemResource(
                    resource_type="Error",
                    current_usage=0,
                    total_capacity=0,
                    usage_percentage=0,
                    educational_notes=[f"Error getting system resources: {e}"]
                )
            }
    
    def get_power_management(self) -> Dict[str, PowerManagement]:
        """Get power management information for educational purposes."""
        try:
            # Battery information
            battery = psutil.sensors_battery()
            
            if battery:
                power_source = "Battery" if not battery.power_plugged else "AC"
                battery_level = battery.percent
                power_consumption = 0  # Would need additional tools to measure
                thermal_status = "Normal"  # Would need additional tools to measure
            else:
                power_source = "AC"
                battery_level = 100
                power_consumption = 0
                thermal_status = "Unknown"
            
            self.power_management = {
                "power_status": PowerManagement(
                    power_source=power_source,
                    battery_level=battery_level,
                    power_consumption=power_consumption,
                    thermal_status=thermal_status,
                    educational_notes=[
                        "Monitor power consumption for mining activity",
                        "High power usage may indicate mining software",
                        "Check thermal status for hardware stress",
                        "Use power monitoring tools for detailed analysis"
                    ]
                )
            }
            
            return self.power_management
            
        except Exception as e:
            return {
                "error": PowerManagement(
                    power_source="Unknown",
                    battery_level=0,
                    power_consumption=0,
                    thermal_status="Unknown",
                    educational_notes=[f"Error getting power management info: {e}"]
                )
            }
    
    def get_system_configurations(self) -> Dict[str, SystemConfiguration]:
        """Get system configuration recommendations for educational purposes."""
        self.system_configurations = {
            "process_monitoring": SystemConfiguration(
                config_type="Process Monitoring",
                current_value="Basic monitoring enabled",
                recommended_value="Enhanced monitoring with alerts",
                educational_purpose="Detect unauthorized processes and resource usage",
                implementation_notes=[
                    "Enable detailed process monitoring",
                    "Configure alerts for high resource usage",
                    "Monitor for suspicious process names",
                    "Track process creation and termination"
                ]
            ),
            "network_monitoring": SystemConfiguration(
                config_type="Network Monitoring",
                current_value="Basic network monitoring",
                recommended_value="Comprehensive network monitoring",
                educational_purpose="Detect unauthorized network connections",
                implementation_notes=[
                    "Monitor all network connections",
                    "Block connections to known mining pools",
                    "Configure network usage alerts",
                    "Track bandwidth usage patterns"
                ]
            ),
            "file_monitoring": SystemConfiguration(
                config_type="File System Monitoring",
                current_value="Basic file monitoring",
                recommended_value="Enhanced file system monitoring",
                educational_purpose="Detect unauthorized file modifications",
                implementation_notes=[
                    "Monitor critical system directories",
                    "Track file creation and modification",
                    "Configure file integrity monitoring",
                    "Alert on suspicious file activity"
                ]
            ),
            "registry_monitoring": SystemConfiguration(
                config_type="Registry Monitoring",
                current_value="Basic registry monitoring",
                recommended_value="Comprehensive registry monitoring",
                educational_purpose="Detect unauthorized registry modifications",
                implementation_notes=[
                    "Monitor critical registry keys",
                    "Track registry modifications",
                    "Configure registry change alerts",
                    "Maintain registry baselines"
                ]
            )
        }
        
        return self.system_configurations
    
    def get_monitoring_script(self, script_name: str) -> Optional[MonitoringScript]:
        """Get a specific monitoring script for educational purposes."""
        return self.monitoring_scripts.get(script_name.lower())
    
    def get_resource_limit(self, limit_type: str) -> Optional[ResourceLimit]:
        """Get a specific resource limit configuration for educational purposes."""
        return self.resource_limits.get(limit_type.lower())
    
    def generate_container_limits(self) -> Dict[str, str]:
        """Generate sample container resource limits for educational purposes."""
        return {
            "docker_cpu_limit": """
# Docker CPU limit example
# FOR EDUCATIONAL PURPOSES ONLY

docker run -d \\
  --name educational-container \\
  --cpus=1.0 \\
  --memory=2g \\
  --pids-limit=100 \\
  your-application
""",
            "kubernetes_resource_limits": """
# Kubernetes resource limits example
# FOR EDUCATIONAL PURPOSES ONLY

apiVersion: v1
kind: Pod
metadata:
  name: educational-pod
spec:
  containers:
  - name: app
    image: your-application
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
""",
            "systemd_resource_limits": """
# systemd resource limits example
# FOR EDUCATIONAL PURPOSES ONLY

[Unit]
Description=Educational Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/your-application
CPUQuota=100%
MemoryMax=2G
LimitNOFILE=1000

[Install]
WantedBy=multi-user.target
"""
        }
    
    def generate_monitoring_dashboard(self) -> Dict[str, Any]:
        """Generate sample monitoring dashboard configuration for educational purposes."""
        return {
            "prometheus_config": """
# Prometheus configuration example
# FOR EDUCATIONAL PURPOSES ONLY

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'system-metrics'
    static_configs:
      - targets: ['localhost:9100']
    metrics_path: '/metrics'
    scrape_interval: 5s
""",
            "grafana_dashboard": """
# Grafana dashboard configuration example
# FOR EDUCATIONAL PURPOSES ONLY

{
  "dashboard": {
    "title": "System Resource Monitoring",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
          }
        ]
      }
    ]
  }
}
""",
            "alerting_rules": """
# Alerting rules example
# FOR EDUCATIONAL PURPOSES ONLY

groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"
      
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for 5 minutes"
"""
        }
    
    def generate_educational_report(self, output_path: str = None) -> str:
        """Generate a comprehensive educational report."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"system_administration_report_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "purpose": "Educational report on system administration and resource management",
            "disclaimer": "FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL SYSTEM MODIFICATIONS OCCUR",
            "system_resources": {k: asdict(v) for k, v in self.get_system_resources().items()},
            "power_management": {k: asdict(v) for k, v in self.get_power_management().items()},
            "system_configurations": {k: asdict(v) for k, v in self.get_system_configurations().items()},
            "monitoring_scripts": {k: asdict(v) for k, v in self.monitoring_scripts.items()},
            "resource_limits": {k: asdict(v) for k, v in self.resource_limits.items()},
            "container_limits": self.generate_container_limits(),
            "monitoring_dashboard": self.generate_monitoring_dashboard(),
            "educational_objectives": [
                "Understand system resource monitoring",
                "Learn about power management and thermal monitoring",
                "Implement resource limits and controls",
                "Configure monitoring and alerting systems",
                "Develop system administration best practices",
                "Build defensive monitoring capabilities"
            ],
            "defensive_applications": [
                "Monitor system resources for unauthorized usage",
                "Detect mining software through resource monitoring",
                "Implement resource limits to prevent abuse",
                "Configure alerts for suspicious activity",
                "Develop incident response procedures",
                "Build comprehensive monitoring systems"
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return output_path


def demo_system_administration():
    """Demo function to show the system administration module."""
    print("⚙️ System Administration & Resource Management Demo")
    print("=" * 60)
    print("💡 This demonstrates educational content only")
    print("🚫 NO ACTUAL SYSTEM MODIFICATIONS OCCUR")
    print()
    
    try:
        # Create system administration module
        admin = SystemAdministration()
        
        print("✅ System Administration Module initialized")
        print()
        
        # Demonstrate system resources
        print("📊 System Resources:")
        resources = admin.get_system_resources()
        for name, resource in resources.items():
            if hasattr(resource, 'resource_type'):
                print(f"   - {resource.resource_type}: {resource.usage_percentage:.1f}% usage")
        print()
        
        # Demonstrate power management
        print("🔋 Power Management:")
        power = admin.get_power_management()
        for name, power_info in power.items():
            if hasattr(power_info, 'power_source'):
                print(f"   - Power Source: {power_info.power_source}")
                print(f"   - Battery Level: {power_info.battery_level}%")
        print()
        
        # Demonstrate system configurations
        print("⚙️ System Configurations:")
        configs = admin.get_system_configurations()
        for name, config in configs.items():
            print(f"   - {config.config_type}: {config.current_value}")
        print()
        
        # Demonstrate monitoring scripts
        print("📝 Monitoring Scripts:")
        for name, script in admin.monitoring_scripts.items():
            print(f"   - {script.script_name}: {script.description}")
        print()
        
        # Demonstrate resource limits
        print("🔒 Resource Limits:")
        for name, limit in admin.resource_limits.items():
            print(f"   - {limit.resource_type}: {limit.limit_value}")
        print()
        
        # Generate educational report
        print("📄 Generating system administration report...")
        report_path = admin.generate_educational_report()
        print(f"✅ System administration report generated: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ System administration demo failed: {e}")
        return False


if __name__ == "__main__":
    demo_system_administration()