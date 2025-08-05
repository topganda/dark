"""
Intelligent Intensity Management Engine
Provides legitimate, user-consented resource management for defensive analysis.
This module demonstrates proper resource management patterns that can be used
to detect unauthorized resource-consuming software behaviors.
"""

import psutil
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False

@dataclass
class SystemState:
    """System state information for intensity calculation."""
    idle_time_minutes: float
    battery_percent: float
    on_ac_power: bool
    cpu_temperature: float
    gpu_temperature: Optional[float]
    task_manager_foreground: bool
    user_active: bool
    foreground_window: Optional[str]
    timestamp: datetime

@dataclass
class IntensityDecision:
    """Intensity decision with metadata."""
    intensity_percent: int
    reason: str
    system_state: SystemState
    timestamp: datetime

class IntensityEngine:
    """
    Intelligent intensity management engine for legitimate resource management.
    
    This engine demonstrates proper resource management patterns that can be used
    to detect unauthorized resource-consuming software behaviors by comparing
    against legitimate patterns.
    """
    
    def __init__(self, poll_seconds: int = 2, callback: Optional[Callable] = None):
        """
        Initialize the intensity engine.
        
        Args:
            poll_seconds: Polling interval in seconds
            callback: Optional callback function for intensity changes
        """
        self.poll_seconds = poll_seconds
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.thread = None
        
        # Initialize WMI if available
        self.wmi = None
        if WMI_AVAILABLE:
            try:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize WMI: {e}")
        
        # Performance tracking
        self.intensity_history = []
        self.max_history_size = 1000
        
        # Intensity decision matrix (legitimate patterns)
        self.intensity_matrix = {
            "opportunistic": {
                "conditions": {
                    "idle_minutes": 10,
                    "battery_percent": 90,
                    "on_ac": True,
                    "max_temp": 75
                },
                "intensity": 90,
                "reason": "Opportunistic - High idle, plugged in, cool"
            },
            "balanced": {
                "conditions": {
                    "idle_minutes": 5,
                    "battery_percent": 50,
                    "on_ac": True,
                    "max_temp": 80
                },
                "intensity": 70,
                "reason": "Balanced - Moderate idle, plugged in"
            },
            "battery_care": {
                "conditions": {
                    "idle_minutes": 5,
                    "battery_percent": 70,
                    "on_ac": False,
                    "max_temp": 75
                },
                "intensity": 40,
                "reason": "Battery care - Moderate idle, on battery"
            },
            "stealth": {
                "conditions": {
                    "user_active": True
                },
                "intensity": 30,
                "reason": "Stealth - User active"
            },
            "ultra_stealth": {
                "conditions": {
                    "task_manager_foreground": True
                },
                "intensity": 5,
                "reason": "Ultra-stealth - Task Manager detected"
            },
            "pause": {
                "conditions": {
                    "battery_low": 30,
                    "temp_high": 85
                },
                "intensity": 0,
                "reason": "Pause - Battery low or temperature high"
            }
        }
    
    def get_system_state(self) -> SystemState:
        """Get current system state for intensity calculation."""
        try:
            # Get idle time
            idle_time = psutil.cpu_times().idle
            idle_minutes = idle_time / psutil.cpu_count() / 60
            
            # Get battery information
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else 100
            on_ac = battery.power_plugged if battery else True
            
            # Get temperatures
            cpu_temp = self._get_cpu_temperature()
            gpu_temp = self._get_gpu_temperature()
            
            # Check for Task Manager
            task_manager_foreground = self._is_task_manager_foreground()
            
            # Check user activity
            user_active = not self._is_system_idle(idle_minutes)
            
            # Get foreground window (if possible)
            foreground_window = self._get_foreground_window()
            
            return SystemState(
                idle_time_minutes=idle_minutes,
                battery_percent=battery_percent,
                on_ac_power=on_ac,
                cpu_temperature=cpu_temp,
                gpu_temperature=gpu_temp,
                task_manager_foreground=task_manager_foreground,
                user_active=user_active,
                foreground_window=foreground_window,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system state: {e}")
            # Return safe default state
            return SystemState(
                idle_time_minutes=0,
                battery_percent=100,
                on_ac_power=True,
                cpu_temperature=65,
                gpu_temperature=None,
                task_manager_foreground=False,
                user_active=True,
                foreground_window=None,
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
            self.logger.warning(f"Failed to get CPU temperature: {e}")
            return 65.0  # Safe default
    
    def _get_gpu_temperature(self) -> Optional[float]:
        """Get GPU temperature if available."""
        try:
            # Try NVIDIA GPU
            if self.wmi:
                gpu_info = self.wmi.Win32_VideoController()[0]
                if hasattr(gpu_info, 'Temperature'):
                    return float(gpu_info.Temperature)
            
            # Try AMD GPU (would need pyamdgpuinfo)
            # For now, return None
            return None
            
        except Exception as e:
            self.logger.debug(f"GPU temperature not available: {e}")
            return None
    
    def _is_task_manager_foreground(self) -> bool:
        """Check if Task Manager is in foreground."""
        try:
            taskmgr_processes = [
                p for p in psutil.process_iter(['name', 'pid'])
                if p.info['name'] and p.info['name'].lower() == 'taskmgr.exe'
            ]
            return len(taskmgr_processes) > 0
        except Exception as e:
            self.logger.debug(f"Failed to check Task Manager: {e}")
            return False
    
    def _is_system_idle(self, idle_minutes: float) -> bool:
        """Check if system is idle."""
        return idle_minutes >= 5
    
    def _get_foreground_window(self) -> Optional[str]:
        """Get foreground window title (if possible)."""
        try:
            # This would require platform-specific implementation
            # For now, return None
            return None
        except Exception:
            return None
    
    def compute_intensity(self, system_state: SystemState) -> IntensityDecision:
        """
        Compute intensity level based on system state.
        
        Args:
            system_state: Current system state
            
        Returns:
            IntensityDecision with calculated intensity and reason
        """
        # Check pause conditions first
        if (system_state.battery_percent < 30 or 
            system_state.cpu_temperature >= 85 or
            (system_state.gpu_temperature and system_state.gpu_temperature >= 85)):
            return IntensityDecision(
                intensity_percent=0,
                reason="Pause - Battery low or temperature high",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Check ultra-stealth (Task Manager)
        if system_state.task_manager_foreground:
            return IntensityDecision(
                intensity_percent=5,
                reason="Ultra-stealth - Task Manager detected",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Check user activity
        if system_state.user_active:
            return IntensityDecision(
                intensity_percent=30,
                reason="Stealth - User active",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Check opportunistic conditions
        if (system_state.idle_time_minutes >= 10 and 
            system_state.on_ac_power and 
            system_state.battery_percent >= 90 and 
            system_state.cpu_temperature < 75):
            return IntensityDecision(
                intensity_percent=90,
                reason="Opportunistic - High idle, plugged in, cool",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Check balanced conditions
        if (system_state.idle_time_minutes >= 5 and 
            system_state.on_ac_power and 
            system_state.battery_percent >= 50 and 
            system_state.cpu_temperature < 80):
            return IntensityDecision(
                intensity_percent=70,
                reason="Balanced - Moderate idle, plugged in",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Check battery care conditions
        if (system_state.idle_time_minutes >= 5 and 
            not system_state.on_ac_power and 
            system_state.battery_percent >= 70 and 
            system_state.cpu_temperature < 75):
            return IntensityDecision(
                intensity_percent=40,
                reason="Battery care - Moderate idle, on battery",
                system_state=system_state,
                timestamp=datetime.now()
            )
        
        # Default fallback
        return IntensityDecision(
            intensity_percent=25,
            reason="Default - Conservative fallback",
            system_state=system_state,
            timestamp=datetime.now()
        )
    
    def start_monitoring(self):
        """Start the intensity monitoring loop."""
        if self.running:
            self.logger.warning("Intensity engine already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("Intensity engine started")
    
    def stop_monitoring(self):
        """Stop the intensity monitoring loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Intensity engine stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Get system state
                system_state = self.get_system_state()
                
                # Compute intensity
                decision = self.compute_intensity(system_state)
                
                # Store in history
                self.intensity_history.append(decision)
                if len(self.intensity_history) > self.max_history_size:
                    self.intensity_history.pop(0)
                
                # Log decision
                self.logger.info(
                    f"Intensity: {decision.intensity_percent}% - {decision.reason} "
                    f"(Idle: {system_state.idle_time_minutes:.1f}m, "
                    f"Battery: {system_state.battery_percent}%, "
                    f"AC: {system_state.on_ac_power}, "
                    f"Temp: {system_state.cpu_temperature:.1f}°C)"
                )
                
                # Call callback if provided
                if self.callback:
                    try:
                        self.callback(decision)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
                # Wait for next poll
                time.sleep(self.poll_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.poll_seconds)
    
    def get_current_intensity(self) -> Optional[IntensityDecision]:
        """Get the most recent intensity decision."""
        if self.intensity_history:
            return self.intensity_history[-1]
        return None
    
    def get_intensity_history(self, minutes: int = 60) -> list:
        """Get intensity history for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            decision for decision in self.intensity_history
            if decision.timestamp >= cutoff_time
        ]
    
    def get_intensity_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get intensity statistics for the last N minutes."""
        history = self.get_intensity_history(minutes)
        if not history:
            return {}
        
        intensities = [d.intensity_percent for d in history]
        reasons = [d.reason for d in history]
        
        return {
            "average_intensity": sum(intensities) / len(intensities),
            "max_intensity": max(intensities),
            "min_intensity": min(intensities),
            "total_decisions": len(history),
            "most_common_reason": max(set(reasons), key=reasons.count),
            "time_period_minutes": minutes
        }
    
    def detect_suspicious_patterns(self) -> list:
        """
        Detect suspicious intensity patterns that might indicate unauthorized activity.
        
        Returns:
            List of suspicious patterns detected
        """
        suspicious_patterns = []
        history = self.get_intensity_history(30)  # Last 30 minutes
        
        if len(history) < 10:
            return suspicious_patterns
        
        # Check for constant high intensity
        high_intensity_count = sum(1 for d in history if d.intensity_percent >= 80)
        if high_intensity_count > len(history) * 0.8:
            suspicious_patterns.append({
                "type": "constant_high_intensity",
                "description": f"High intensity ({high_intensity_count}/{len(history)} decisions)",
                "severity": "medium"
            })
        
        # Check for rapid intensity changes
        rapid_changes = 0
        for i in range(1, len(history)):
            change = abs(history[i].intensity_percent - history[i-1].intensity_percent)
            if change > 50:
                rapid_changes += 1
        
        if rapid_changes > len(history) * 0.3:
            suspicious_patterns.append({
                "type": "rapid_intensity_changes",
                "description": f"Rapid intensity changes ({rapid_changes} changes)",
                "severity": "high"
            })
        
        # Check for ignoring system state
        ignored_pauses = 0
        for decision in history:
            state = decision.system_state
            if (state.battery_percent < 30 or state.cpu_temperature >= 85) and decision.intensity_percent > 0:
                ignored_pauses += 1
        
        if ignored_pauses > 0:
            suspicious_patterns.append({
                "type": "ignored_system_state",
                "description": f"Ignored system state {ignored_pauses} times",
                "severity": "high"
            })
        
        return suspicious_patterns


def demo_intensity_engine():
    """Demo function to show how the intensity engine works."""
    print("🔍 URCS Intensity Engine Demo")
    print("=" * 50)
    
    def intensity_callback(decision):
        print(f"📊 Intensity: {decision.intensity_percent}% - {decision.reason}")
    
    # Create and start intensity engine
    engine = IntensityEngine(poll_seconds=3, callback=intensity_callback)
    
    print("🚀 Starting intensity monitoring...")
    print("💡 This demonstrates legitimate resource management patterns")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        engine.start_monitoring()
        
        # Run for 30 seconds
        time.sleep(30)
        
        # Show statistics
        stats = engine.get_intensity_stats(1)  # Last minute
        print(f"\n📈 Statistics:")
        print(f"   Average intensity: {stats.get('average_intensity', 0):.1f}%")
        print(f"   Max intensity: {stats.get('max_intensity', 0)}%")
        print(f"   Min intensity: {stats.get('min_intensity', 0)}%")
        print(f"   Total decisions: {stats.get('total_decisions', 0)}")
        
        # Check for suspicious patterns
        suspicious = engine.detect_suspicious_patterns()
        if suspicious:
            print(f"\n⚠️ Suspicious patterns detected:")
            for pattern in suspicious:
                print(f"   - {pattern['type']}: {pattern['description']}")
        else:
            print(f"\n✅ No suspicious patterns detected")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping intensity engine...")
    finally:
        engine.stop_monitoring()
        print("✅ Intensity engine stopped")


if __name__ == "__main__":
    demo_intensity_engine()