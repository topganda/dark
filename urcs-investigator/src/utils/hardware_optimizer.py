"""
Hardware-Aware Mining Optimization System
Provides legitimate, AV-safe hardware optimization for defensive analysis.
This module demonstrates advanced resource management patterns and hardware telemetry.
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
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
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

@dataclass
class HardwareInfo:
    """Hardware information for optimization."""
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    cpu_cache: int  # MB
    cpu_tdp: int    # Watts
    gpu_model: Optional[str]
    gpu_vram: Optional[int]  # MB
    gpu_tdp: Optional[int]   # Watts
    system_ram: int  # MB
    platform: str
    architecture: str

@dataclass
class ThermalInfo:
    """Thermal and fan information."""
    cpu_temperature: float
    gpu_temperature: Optional[float]
    cpu_fan_rpm: Optional[int]
    gpu_fan_rpm: Optional[int]
    cpu_fan_percent: Optional[float]
    gpu_fan_percent: Optional[float]
    timestamp: datetime

@dataclass
class PowerInfo:
    """Power and battery information."""
    battery_percent: float
    on_ac_power: bool
    ac_wattage: Optional[int]
    power_source: str  # "AC", "Battery", "USB-PD", "Thunderbolt"
    estimated_runtime: Optional[int]  # minutes
    timestamp: datetime

@dataclass
class UserPresenceInfo:
    """User presence and activity information."""
    idle_time_seconds: int
    screen_locked: bool
    foreground_window: Optional[str]
    user_active: bool
    last_input_time: datetime
    timestamp: datetime

@dataclass
class MiningOptimization:
    """Mining optimization recommendations."""
    recommended_algorithm: str
    cpu_threads: int
    gpu_enabled: bool
    intensity_percent: int
    reason: str
    thermal_safe: bool
    power_safe: bool
    user_safe: bool
    timestamp: datetime

class HardwareOptimizer:
    """
    Hardware-aware mining optimization system for legitimate resource management.
    
    This system demonstrates advanced hardware telemetry and optimization patterns
    that can be used for defensive analysis and educational purposes.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize hardware detection
        self.hardware_info = self._detect_hardware()
        self.algorithm_database = self._load_algorithm_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.optimization_history = []
        self.max_history_size = 1000
        
        # Thermal thresholds
        self.thermal_thresholds = {
            "cpu_critical": 85.0,  # °C
            "cpu_warning": 80.0,   # °C
            "gpu_critical": 88.0,  # °C
            "gpu_warning": 82.0,   # °C
            "fan_critical": 95.0   # %
        }
        
        # Power thresholds
        self.power_thresholds = {
            "battery_critical": 20.0,  # %
            "battery_warning": 30.0,   # %
            "ac_minimum": 45,          # Watts
        }
        
        # User presence thresholds
        self.user_thresholds = {
            "idle_warning": 300,       # 5 minutes
            "idle_critical": 600,      # 10 minutes
            "screen_lock_timeout": 60  # 1 minute
        }
        
        # Initialize monitoring components
        self._initialize_monitoring()
        
        self.logger.info(f"Hardware Optimizer initialized for {self.hardware_info.cpu_model}")
    
    def _detect_hardware(self) -> HardwareInfo:
        """Detect and analyze hardware configuration."""
        try:
            # CPU Information
            cpu_info = self._get_cpu_info()
            
            # GPU Information
            gpu_info = self._get_gpu_info()
            
            # System Information
            system_ram = psutil.virtual_memory().total // (1024 * 1024)  # MB
            
            return HardwareInfo(
                cpu_model=cpu_info.get("model", "Unknown"),
                cpu_cores=cpu_info.get("cores", 1),
                cpu_threads=cpu_info.get("threads", 1),
                cpu_cache=cpu_info.get("cache", 0),
                cpu_tdp=cpu_info.get("tdp", 0),
                gpu_model=gpu_info.get("model"),
                gpu_vram=gpu_info.get("vram"),
                gpu_tdp=gpu_info.get("tdp"),
                system_ram=system_ram,
                platform=platform.system(),
                architecture=platform.architecture()[0]
            )
            
        except Exception as e:
            self.logger.error(f"Hardware detection failed: {e}")
            return HardwareInfo(
                cpu_model="Unknown",
                cpu_cores=1,
                cpu_threads=1,
                cpu_cache=0,
                cpu_tdp=0,
                gpu_model=None,
                gpu_vram=None,
                gpu_tdp=None,
                system_ram=0,
                platform=platform.system(),
                architecture=platform.architecture()[0]
            )
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information."""
        try:
            cpu_info = {
                "model": platform.processor(),
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "cache": 0,
                "tdp": 0
            }
            
            # Try to get more detailed CPU info
            if WMI_AVAILABLE:
                try:
                    w = wmi.WMI()
                    for processor in w.Win32_Processor():
                        cpu_info["model"] = processor.Name
                        cpu_info["cores"] = processor.NumberOfCores
                        cpu_info["threads"] = processor.NumberOfLogicalProcessors
                        cpu_info["cache"] = processor.L2CacheSize or 0
                        break
                except Exception as e:
                    self.logger.debug(f"WMI CPU info failed: {e}")
            
            # Estimate TDP based on CPU model
            cpu_info["tdp"] = self._estimate_cpu_tdp(cpu_info["model"])
            
            return cpu_info
            
        except Exception as e:
            self.logger.error(f"CPU info detection failed: {e}")
            return {"model": "Unknown", "cores": 1, "threads": 1, "cache": 0, "tdp": 0}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get detailed GPU information."""
        try:
            gpu_info = {"model": None, "vram": None, "tdp": None}
            
            if NVML_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    if device_count > 0:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        name = pynvml.nvmlDeviceGetName(handle)
                        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        
                        gpu_info["model"] = name.decode('utf-8')
                        gpu_info["vram"] = memory_info.total // (1024 * 1024)  # MB
                        gpu_info["tdp"] = self._estimate_gpu_tdp(gpu_info["model"])
                        
                except Exception as e:
                    self.logger.debug(f"NVML GPU info failed: {e}")
            
            # Fallback to WMI for GPU info
            if WMI_AVAILABLE and not gpu_info["model"]:
                try:
                    w = wmi.WMI()
                    for gpu in w.Win32_VideoController():
                        gpu_info["model"] = gpu.Name
                        gpu_info["vram"] = gpu.AdapterRAM // (1024 * 1024) if gpu.AdapterRAM else None
                        gpu_info["tdp"] = self._estimate_gpu_tdp(gpu_info["model"])
                        break
                except Exception as e:
                    self.logger.debug(f"WMI GPU info failed: {e}")
            
            return gpu_info
            
        except Exception as e:
            self.logger.error(f"GPU info detection failed: {e}")
            return {"model": None, "vram": None, "tdp": None}
    
    def _estimate_cpu_tdp(self, cpu_model: str) -> int:
        """Estimate CPU TDP based on model."""
        cpu_model_lower = cpu_model.lower()
        
        # AMD Ryzen series
        if "ryzen 9" in cpu_model_lower:
            return 105 if "5950x" in cpu_model_lower or "5900x" in cpu_model_lower else 95
        elif "ryzen 7" in cpu_model_lower:
            return 65 if "5800x" in cpu_model_lower else 65
        elif "ryzen 5" in cpu_model_lower:
            return 65 if "5600x" in cpu_model_lower else 65
        
        # Intel series
        elif "i9" in cpu_model_lower:
            return 125 if "12900k" in cpu_model_lower else 95
        elif "i7" in cpu_model_lower:
            return 125 if "12700k" in cpu_model_lower else 65
        elif "i5" in cpu_model_lower:
            return 125 if "12600k" in cpu_model_lower else 65
        
        # Default estimates
        elif "ryzen" in cpu_model_lower:
            return 65
        elif "intel" in cpu_model_lower:
            return 65
        else:
            return 65  # Conservative default
    
    def _estimate_gpu_tdp(self, gpu_model: str) -> int:
        """Estimate GPU TDP based on model."""
        gpu_model_lower = gpu_model.lower()
        
        # NVIDIA RTX series
        if "rtx 4090" in gpu_model_lower:
            return 450
        elif "rtx 4080" in gpu_model_lower:
            return 320
        elif "rtx 4070" in gpu_model_lower:
            return 200
        elif "rtx 3090" in gpu_model_lower:
            return 350
        elif "rtx 3080" in gpu_model_lower:
            return 320
        elif "rtx 3070" in gpu_model_lower:
            return 220
        elif "rtx 3060" in gpu_model_lower:
            return 170
        
        # AMD RX series
        elif "rx 6900" in gpu_model_lower:
            return 300
        elif "rx 6800" in gpu_model_lower:
            return 250
        elif "rx 6700" in gpu_model_lower:
            return 175
        elif "rx 6600" in gpu_model_lower:
            return 132
        
        # Default estimates
        elif "rtx" in gpu_model_lower:
            return 200
        elif "rx" in gpu_model_lower:
            return 200
        else:
            return 150  # Conservative default
    
    def _load_algorithm_database(self) -> Dict[str, Any]:
        """Load mining algorithm database."""
        # This would typically load from a JSON file or API
        # For demonstration, we'll use a built-in database
        return {
            "algorithms": {
                "RandomX": {
                    "description": "CPU-based algorithm for Monero",
                    "cpu_optimal": ["ryzen 7 5800x", "ryzen 9 5900x", "i7-12700k"],
                    "gpu_optimal": [],
                    "min_ram": 2048,  # MB
                    "threads_per_core": 1,
                    "cache_benefit": True
                },
                "Ethash": {
                    "description": "GPU-based algorithm for Ethereum",
                    "cpu_optimal": [],
                    "gpu_optimal": ["rtx 3060", "rtx 3070", "rtx 3080", "rx 6600", "rx 6700"],
                    "min_vram": 4096,  # MB
                    "threads_per_core": 0,
                    "cache_benefit": False
                },
                "KawPow": {
                    "description": "GPU-based algorithm for Ravencoin",
                    "cpu_optimal": [],
                    "gpu_optimal": ["rtx 3060", "rtx 3070", "rx 6600", "rx 6700"],
                    "min_vram": 4096,  # MB
                    "threads_per_core": 0,
                    "cache_benefit": False
                },
                "VerusHash": {
                    "description": "CPU-based algorithm for Verus Coin",
                    "cpu_optimal": ["ryzen 7 5800x", "i7-12700k"],
                    "gpu_optimal": [],
                    "min_ram": 1024,  # MB
                    "threads_per_core": 1,
                    "cache_benefit": True
                }
            }
        }
    
    def _initialize_monitoring(self):
        """Initialize monitoring components."""
        try:
            # Initialize NVML if available
            if NVML_AVAILABLE:
                pynvml.nvmlInit()
                self.logger.info("NVML initialized for GPU monitoring")
            
            # Initialize WMI if available
            if WMI_AVAILABLE:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized for system monitoring")
            
        except Exception as e:
            self.logger.error(f"Monitoring initialization failed: {e}")
    
    def get_thermal_info(self) -> ThermalInfo:
        """Get current thermal and fan information."""
        try:
            cpu_temp = self._get_cpu_temperature()
            gpu_temp = self._get_gpu_temperature()
            cpu_fan = self._get_cpu_fan_info()
            gpu_fan = self._get_gpu_fan_info()
            
            return ThermalInfo(
                cpu_temperature=cpu_temp,
                gpu_temperature=gpu_temp,
                cpu_fan_rpm=cpu_fan.get("rpm"),
                gpu_fan_rpm=gpu_fan.get("rpm"),
                cpu_fan_percent=cpu_fan.get("percent"),
                gpu_fan_percent=gpu_fan.get("percent"),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Thermal info collection failed: {e}")
            return ThermalInfo(
                cpu_temperature=65.0,
                gpu_temperature=None,
                cpu_fan_rpm=None,
                gpu_fan_rpm=None,
                cpu_fan_percent=None,
                gpu_fan_percent=None,
                timestamp=datetime.now()
            )
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature."""
        try:
            # Try to get temperature from sensors
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return max([v.current for v in temps['cpu_thermal']])
            elif 'coretemp' in temps:
                return max([v.current for v in temps['coretemp']])
            else:
                # Fallback: estimate based on CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                return 40 + (cpu_percent * 0.5)  # Rough estimate
        except Exception as e:
            self.logger.warning(f"CPU temperature detection failed: {e}")
            return 65.0  # Safe default
    
    def _get_gpu_temperature(self) -> Optional[float]:
        """Get GPU temperature."""
        try:
            if NVML_AVAILABLE:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                return float(temp)
            return None
        except Exception as e:
            self.logger.debug(f"GPU temperature detection failed: {e}")
            return None
    
    def _get_cpu_fan_info(self) -> Dict[str, Any]:
        """Get CPU fan information."""
        try:
            # This would require platform-specific implementation
            # For now, return estimated values
            return {"rpm": None, "percent": None}
        except Exception:
            return {"rpm": None, "percent": None}
    
    def _get_gpu_fan_info(self) -> Dict[str, Any]:
        """Get GPU fan information."""
        try:
            if NVML_AVAILABLE:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                return {"rpm": fan_speed, "percent": None}
            return {"rpm": None, "percent": None}
        except Exception as e:
            self.logger.debug(f"GPU fan detection failed: {e}")
            return {"rpm": None, "percent": None}
    
    def get_power_info(self) -> PowerInfo:
        """Get current power and battery information."""
        try:
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else 100
            on_ac = battery.power_plugged if battery else True
            
            # Determine power source
            power_source = "AC"
            ac_wattage = None
            
            if not on_ac:
                power_source = "Battery"
            else:
                # Try to detect USB-PD or Thunderbolt
                ac_wattage = self._detect_ac_wattage()
                if ac_wattage and ac_wattage < 100:
                    power_source = "USB-PD"
                elif ac_wattage and ac_wattage >= 100:
                    power_source = "Thunderbolt"
            
            # Estimate runtime
            estimated_runtime = None
            if battery and not on_ac:
                estimated_runtime = int(battery.secsleft / 60) if battery.secsleft > 0 else None
            
            return PowerInfo(
                battery_percent=battery_percent,
                on_ac_power=on_ac,
                ac_wattage=ac_wattage,
                power_source=power_source,
                estimated_runtime=estimated_runtime,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Power info collection failed: {e}")
            return PowerInfo(
                battery_percent=100,
                on_ac_power=True,
                ac_wattage=None,
                power_source="AC",
                estimated_runtime=None,
                timestamp=datetime.now()
            )
    
    def _detect_ac_wattage(self) -> Optional[int]:
        """Detect AC adapter wattage."""
        try:
            # This would require platform-specific implementation
            # For demonstration, return estimated values
            if WMI_AVAILABLE:
                # Try to get power information from WMI
                for battery in self.wmi.Win32_Battery():
                    if battery.EstimatedChargeRemaining:
                        # Estimate based on charging rate
                        return 65  # Typical laptop charger
            return 65  # Default estimate
        except Exception:
            return None
    
    def get_user_presence_info(self) -> UserPresenceInfo:
        """Get current user presence and activity information."""
        try:
            # Get idle time
            idle_time = self._get_idle_time()
            
            # Check if screen is locked
            screen_locked = self._is_screen_locked()
            
            # Get foreground window
            foreground_window = self._get_foreground_window()
            
            # Determine if user is active
            user_active = idle_time < self.user_thresholds["idle_warning"]
            
            return UserPresenceInfo(
                idle_time_seconds=idle_time,
                screen_locked=screen_locked,
                foreground_window=foreground_window,
                user_active=user_active,
                last_input_time=datetime.now() - timedelta(seconds=idle_time),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"User presence info collection failed: {e}")
            return UserPresenceInfo(
                idle_time_seconds=0,
                screen_locked=False,
                foreground_window=None,
                user_active=True,
                last_input_time=datetime.now(),
                timestamp=datetime.now()
            )
    
    def _get_idle_time(self) -> int:
        """Get system idle time in seconds."""
        try:
            # This would require platform-specific implementation
            # For demonstration, return estimated values
            return 0  # Assume user is active
        except Exception:
            return 0
    
    def _is_screen_locked(self) -> bool:
        """Check if screen is locked."""
        try:
            # This would require platform-specific implementation
            # For demonstration, return False
            return False
        except Exception:
            return False
    
    def _get_foreground_window(self) -> Optional[str]:
        """Get foreground window title."""
        try:
            # This would require platform-specific implementation
            # For demonstration, return None
            return None
        except Exception:
            return None
    
    def optimize_mining(self) -> MiningOptimization:
        """Generate mining optimization recommendations."""
        try:
            # Get current system state
            thermal_info = self.get_thermal_info()
            power_info = self.get_power_info()
            user_info = self.get_user_presence_info()
            
            # Determine optimal algorithm
            algorithm = self._select_optimal_algorithm()
            
            # Calculate safe thread count
            cpu_threads = self._calculate_safe_cpu_threads(thermal_info, power_info, user_info)
            
            # Determine GPU usage
            gpu_enabled = self._should_enable_gpu(thermal_info, power_info, user_info)
            
            # Calculate intensity
            intensity = self._calculate_intensity(thermal_info, power_info, user_info)
            
            # Determine safety status
            thermal_safe = self._is_thermal_safe(thermal_info)
            power_safe = self._is_power_safe(power_info)
            user_safe = self._is_user_safe(user_info)
            
            # Generate reason
            reason = self._generate_optimization_reason(
                algorithm, cpu_threads, gpu_enabled, intensity,
                thermal_info, power_info, user_info
            )
            
            optimization = MiningOptimization(
                recommended_algorithm=algorithm,
                cpu_threads=cpu_threads,
                gpu_enabled=gpu_enabled,
                intensity_percent=intensity,
                reason=reason,
                thermal_safe=thermal_safe,
                power_safe=power_safe,
                user_safe=user_safe,
                timestamp=datetime.now()
            )
            
            # Store in history
            self.optimization_history.append(optimization)
            if len(self.optimization_history) > self.max_history_size:
                self.optimization_history.pop(0)
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Mining optimization failed: {e}")
            return MiningOptimization(
                recommended_algorithm="RandomX",
                cpu_threads=1,
                gpu_enabled=False,
                intensity_percent=25,
                reason="Error in optimization - using safe defaults",
                thermal_safe=True,
                power_safe=True,
                user_safe=True,
                timestamp=datetime.now()
            )
    
    def _select_optimal_algorithm(self) -> str:
        """Select optimal mining algorithm based on hardware."""
        try:
            cpu_model_lower = self.hardware_info.cpu_model.lower()
            gpu_model_lower = self.hardware_info.gpu_model.lower() if self.hardware_info.gpu_model else ""
            
            # Check CPU-optimal algorithms
            for algo_name, algo_info in self.algorithm_database["algorithms"].items():
                if algo_info["cpu_optimal"]:
                    for optimal_cpu in algo_info["cpu_optimal"]:
                        if optimal_cpu.lower() in cpu_model_lower:
                            return algo_name
            
            # Check GPU-optimal algorithms
            if self.hardware_info.gpu_model:
                for algo_name, algo_info in self.algorithm_database["algorithms"].items():
                    if algo_info["gpu_optimal"]:
                        for optimal_gpu in algo_info["gpu_optimal"]:
                            if optimal_gpu.lower() in gpu_model_lower:
                                return algo_name
            
            # Default to RandomX for CPU mining
            return "RandomX"
            
        except Exception as e:
            self.logger.error(f"Algorithm selection failed: {e}")
            return "RandomX"
    
    def _calculate_safe_cpu_threads(self, thermal: ThermalInfo, power: PowerInfo, user: UserPresenceInfo) -> int:
        """Calculate safe CPU thread count."""
        try:
            # Start with maximum threads
            max_threads = self.hardware_info.cpu_threads
            
            # Reduce based on thermal conditions
            if thermal.cpu_temperature > self.thermal_thresholds["cpu_critical"]:
                max_threads = max(1, max_threads // 4)
            elif thermal.cpu_temperature > self.thermal_thresholds["cpu_warning"]:
                max_threads = max(1, max_threads // 2)
            
            # Reduce based on power conditions
            if not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_critical"]:
                max_threads = max(1, max_threads // 4)
            elif not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_warning"]:
                max_threads = max(1, max_threads // 2)
            
            # Reduce based on user activity
            if not user.user_active:
                max_threads = max(1, max_threads // 2)
            elif user.screen_locked:
                max_threads = max(1, max_threads // 4)
            
            return max(1, max_threads)
            
        except Exception as e:
            self.logger.error(f"CPU thread calculation failed: {e}")
            return 1
    
    def _should_enable_gpu(self, thermal: ThermalInfo, power: PowerInfo, user: UserPresenceInfo) -> bool:
        """Determine if GPU mining should be enabled."""
        try:
            # Check if GPU is available
            if not self.hardware_info.gpu_model:
                return False
            
            # Check thermal conditions
            if thermal.gpu_temperature and thermal.gpu_temperature > self.thermal_thresholds["gpu_critical"]:
                return False
            elif thermal.gpu_temperature and thermal.gpu_temperature > self.thermal_thresholds["gpu_warning"]:
                return False
            
            # Check power conditions
            if not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_critical"]:
                return False
            
            # Check user activity
            if user.screen_locked:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"GPU enable check failed: {e}")
            return False
    
    def _calculate_intensity(self, thermal: ThermalInfo, power: PowerInfo, user: UserPresenceInfo) -> int:
        """Calculate mining intensity percentage."""
        try:
            # Start with maximum intensity
            intensity = 100
            
            # Reduce based on thermal conditions
            if thermal.cpu_temperature > self.thermal_thresholds["cpu_critical"]:
                intensity = 25
            elif thermal.cpu_temperature > self.thermal_thresholds["cpu_warning"]:
                intensity = 50
            
            if thermal.gpu_temperature and thermal.gpu_temperature > self.thermal_thresholds["gpu_critical"]:
                intensity = min(intensity, 25)
            elif thermal.gpu_temperature and thermal.gpu_temperature > self.thermal_thresholds["gpu_warning"]:
                intensity = min(intensity, 50)
            
            # Reduce based on power conditions
            if not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_critical"]:
                intensity = 0
            elif not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_warning"]:
                intensity = min(intensity, 30)
            
            # Reduce based on user activity
            if user.screen_locked:
                intensity = 0
            elif not user.user_active:
                intensity = min(intensity, 70)
            
            return max(0, intensity)
            
        except Exception as e:
            self.logger.error(f"Intensity calculation failed: {e}")
            return 25
    
    def _is_thermal_safe(self, thermal: ThermalInfo) -> bool:
        """Check if thermal conditions are safe."""
        return (thermal.cpu_temperature < self.thermal_thresholds["cpu_critical"] and
                (not thermal.gpu_temperature or thermal.gpu_temperature < self.thermal_thresholds["gpu_critical"]))
    
    def _is_power_safe(self, power: PowerInfo) -> bool:
        """Check if power conditions are safe."""
        return (power.on_ac_power or power.battery_percent > self.power_thresholds["battery_critical"])
    
    def _is_user_safe(self, user: UserPresenceInfo) -> bool:
        """Check if user conditions are safe."""
        return not user.screen_locked
    
    def _generate_optimization_reason(self, algorithm: str, threads: int, gpu_enabled: bool, 
                                    intensity: int, thermal: ThermalInfo, power: PowerInfo, 
                                    user: UserPresenceInfo) -> str:
        """Generate human-readable optimization reason."""
        reasons = []
        
        # Algorithm selection reason
        reasons.append(f"Algorithm: {algorithm} (optimal for {self.hardware_info.cpu_model})")
        
        # Thread count reason
        if threads < self.hardware_info.cpu_threads:
            reasons.append(f"CPU threads reduced to {threads} (thermal/power/user constraints)")
        
        # GPU reason
        if not gpu_enabled and self.hardware_info.gpu_model:
            reasons.append("GPU disabled (thermal/power/user constraints)")
        
        # Intensity reason
        if intensity < 100:
            if thermal.cpu_temperature > self.thermal_thresholds["cpu_warning"]:
                reasons.append(f"Intensity reduced to {intensity}% (high CPU temperature: {thermal.cpu_temperature:.1f}°C)")
            elif not power.on_ac_power and power.battery_percent < self.power_thresholds["battery_warning"]:
                reasons.append(f"Intensity reduced to {intensity}% (low battery: {power.battery_percent}%)")
            elif user.screen_locked:
                reasons.append(f"Intensity reduced to {intensity}% (screen locked)")
            elif not user.user_active:
                reasons.append(f"Intensity reduced to {intensity}% (user inactive)")
        
        return "; ".join(reasons) if reasons else "Optimal configuration"
    
    def start_monitoring(self):
        """Start continuous monitoring."""
        if self.monitoring_active:
            self.logger.warning("Hardware monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Hardware monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Hardware monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Generate optimization
                optimization = self.optimize_mining()
                
                # Log optimization
                self.logger.info(
                    f"Optimization: {optimization.recommended_algorithm}, "
                    f"{optimization.cpu_threads} threads, "
                    f"GPU: {'ON' if optimization.gpu_enabled else 'OFF'}, "
                    f"Intensity: {optimization.intensity_percent}% - {optimization.reason}"
                )
                
                # Check for critical conditions
                self._check_critical_conditions(optimization)
                
                # Wait for next cycle
                time.sleep(5)  # 5-second monitoring cycle
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def _check_critical_conditions(self, optimization: MiningOptimization):
        """Check for critical conditions and generate alerts."""
        try:
            thermal_info = self.get_thermal_info()
            power_info = self.get_power_info()
            
            # Thermal alerts
            if thermal_info.cpu_temperature > self.thermal_thresholds["cpu_critical"]:
                self.logger.warning(f"CRITICAL: CPU temperature {thermal_info.cpu_temperature:.1f}°C")
            
            if thermal_info.gpu_temperature and thermal_info.gpu_temperature > self.thermal_thresholds["gpu_critical"]:
                self.logger.warning(f"CRITICAL: GPU temperature {thermal_info.gpu_temperature:.1f}°C")
            
            # Power alerts
            if not power_info.on_ac_power and power_info.battery_percent < self.power_thresholds["battery_critical"]:
                self.logger.warning(f"CRITICAL: Battery level {power_info.battery_percent}%")
            
        except Exception as e:
            self.logger.error(f"Critical condition check failed: {e}")
    
    def get_optimization_history(self, minutes: int = 60) -> List[MiningOptimization]:
        """Get optimization history for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            opt for opt in self.optimization_history
            if opt.timestamp >= cutoff_time
        ]
    
    def get_optimization_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get optimization statistics."""
        history = self.get_optimization_history(minutes)
        if not history:
            return {}
        
        algorithms = [opt.recommended_algorithm for opt in history]
        intensities = [opt.intensity_percent for opt in history]
        gpu_usage = [opt.gpu_enabled for opt in history]
        
        return {
            "total_optimizations": len(history),
            "most_common_algorithm": max(set(algorithms), key=algorithms.count),
            "average_intensity": sum(intensities) / len(intensities),
            "gpu_usage_percent": (sum(gpu_usage) / len(gpu_usage)) * 100,
            "time_period_minutes": minutes
        }
    
    def emergency_stop(self):
        """Emergency stop - zero all mining activity."""
        self.logger.warning("EMERGENCY STOP ACTIVATED - Zeroing all mining activity")
        
        # Generate emergency optimization
        emergency_opt = MiningOptimization(
            recommended_algorithm="STOPPED",
            cpu_threads=0,
            gpu_enabled=False,
            intensity_percent=0,
            reason="Emergency stop activated",
            thermal_safe=True,
            power_safe=True,
            user_safe=True,
            timestamp=datetime.now()
        )
        
        self.optimization_history.append(emergency_opt)
        return emergency_opt


def demo_hardware_optimizer():
    """Demo function to show how the hardware optimizer works."""
    print("🔧 Hardware-Aware Mining Optimizer Demo")
    print("=" * 50)
    
    # Create sample config
    config = {
        "hardware_optimizer": {
            "enabled": True,
            "monitoring_interval": 5,
            "thermal_thresholds": {
                "cpu_critical": 85.0,
                "cpu_warning": 80.0,
                "gpu_critical": 88.0,
                "gpu_warning": 82.0
            }
        }
    }
    
    try:
        # Create hardware optimizer
        optimizer = HardwareOptimizer(config)
        
        print("✅ Hardware Optimizer initialized")
        print(f"🔍 Detected hardware:")
        print(f"   - CPU: {optimizer.hardware_info.cpu_model}")
        print(f"   - Cores: {optimizer.hardware_info.cpu_cores}")
        print(f"   - Threads: {optimizer.hardware_info.cpu_threads}")
        print(f"   - TDP: {optimizer.hardware_info.cpu_tdp}W")
        print(f"   - GPU: {optimizer.hardware_info.gpu_model or 'None'}")
        print(f"   - VRAM: {optimizer.hardware_info.gpu_vram or 'N/A'}MB")
        print(f"   - RAM: {optimizer.hardware_info.system_ram}MB")
        
        # Test optimization
        print("\n🔧 Testing optimization...")
        optimization = optimizer.optimize_mining()
        
        print(f"✅ Optimization results:")
        print(f"   - Algorithm: {optimization.recommended_algorithm}")
        print(f"   - CPU Threads: {optimization.cpu_threads}")
        print(f"   - GPU Enabled: {optimization.gpu_enabled}")
        print(f"   - Intensity: {optimization.intensity_percent}%")
        print(f"   - Reason: {optimization.reason}")
        print(f"   - Thermal Safe: {optimization.thermal_safe}")
        print(f"   - Power Safe: {optimization.power_safe}")
        print(f"   - User Safe: {optimization.user_safe}")
        
        # Test monitoring
        print("\n📊 Starting brief monitoring session...")
        optimizer.start_monitoring()
        time.sleep(15)  # Monitor for 15 seconds
        
        # Get statistics
        stats = optimizer.get_optimization_stats(1)  # Last minute
        print(f"📈 Monitoring statistics:")
        print(f"   - Total optimizations: {stats.get('total_optimizations', 0)}")
        print(f"   - Most common algorithm: {stats.get('most_common_algorithm', 'N/A')}")
        print(f"   - Average intensity: {stats.get('average_intensity', 0):.1f}%")
        print(f"   - GPU usage: {stats.get('gpu_usage_percent', 0):.1f}%")
        
        # Test emergency stop
        print("\n🛑 Testing emergency stop...")
        emergency_opt = optimizer.emergency_stop()
        print(f"   - Emergency stop activated: {emergency_opt.intensity_percent}% intensity")
        
        # Stop monitoring
        optimizer.stop_monitoring()
        print("✅ Hardware monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware optimizer demo failed: {e}")
        return False


if __name__ == "__main__":
    demo_hardware_optimizer()