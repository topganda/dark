"""
Setup Wizard
Interactive setup wizard for configuring the Advanced Crypto Mining Suite.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.config import ConfigManager

class SetupWizard:
    """
    Interactive setup wizard for the Advanced Crypto Mining Suite.
    Guides users through the initial configuration process.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        self.logger.info("Setup Wizard initialized")
    
    def run(self):
        """Run the setup wizard"""
        print("🚀 Welcome to Advanced Crypto Mining Suite Setup Wizard!")
        print("=" * 60)
        print("This wizard will help you configure your mining setup.")
        print("Press Enter to use default values (shown in brackets).")
        print()
        
        try:
            # Mining configuration
            self._configure_mining()
            
            # Resource management
            self._configure_resource_management()
            
            # Profitability settings
            self._configure_profitability()
            
            # Monitoring settings
            self._configure_monitoring()
            
            # Security settings
            self._configure_security()
            
            # Advanced settings
            self._configure_advanced()
            
            # Save configuration
            self._save_configuration()
            
            # Show summary
            self._show_summary()
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)
    
    def _configure_mining(self):
        """Configure mining settings"""
        print("📊 Mining Configuration")
        print("-" * 30)
        
        # Algorithm selection
        algorithms = ["rx/0", "kawpow", "ethash"]
        print(f"Available algorithms: {', '.join(algorithms)}")
        
        algorithm = self._get_input(
            "Select mining algorithm",
            self.config.get('mining', {}).get('algorithm', 'rx/0'),
            algorithms
        )
        self.config.setdefault('mining', {})['algorithm'] = algorithm
        
        # Pool configuration
        pool_url = self._get_input(
            "Mining pool URL",
            self.config.get('mining', {}).get('pool_url', 'stratum+tcp://pool.supportxmr.com:3333')
        )
        self.config.setdefault('mining', {})['pool_url'] = pool_url
        
        # Wallet address
        wallet = self._get_input(
            "Wallet address",
            self.config.get('mining', {}).get('wallet', '')
        )
        self.config.setdefault('mining', {})['wallet'] = wallet
        
        # Worker name
        worker_name = self._get_input(
            "Worker name",
            self.config.get('mining', {}).get('worker_name', 'advanced-miner')
        )
        self.config.setdefault('mining', {})['worker_name'] = worker_name
        
        # CPU threads
        cpu_threads = self._get_input(
            "CPU threads (auto/max/number)",
            self.config.get('mining', {}).get('cpu_threads', 'auto')
        )
        self.config.setdefault('mining', {})['cpu_threads'] = cpu_threads
        
        # GPU mining
        gpu_enabled = self._get_yes_no(
            "Enable GPU mining",
            self.config.get('mining', {}).get('gpu_enabled', False)
        )
        self.config.setdefault('mining', {})['gpu_enabled'] = gpu_enabled
        
        print()
    
    def _configure_resource_management(self):
        """Configure resource management settings"""
        print("🧠 Resource Management Configuration")
        print("-" * 40)
        
        # Charging threshold
        charging_threshold = self._get_number(
            "Charging threshold (%)",
            self.config.get('resource_management', {}).get('charging_threshold', 90),
            0, 100
        )
        self.config.setdefault('resource_management', {})['charging_threshold'] = charging_threshold
        
        # Idle threshold
        idle_threshold = self._get_number(
            "Idle threshold (seconds)",
            self.config.get('resource_management', {}).get('idle_threshold', 300),
            60, 3600
        )
        self.config.setdefault('resource_management', {})['idle_threshold'] = idle_threshold
        
        # Battery threshold
        battery_threshold = self._get_number(
            "Battery threshold (%)",
            self.config.get('resource_management', {}).get('battery_threshold', 25),
            0, 100
        )
        self.config.setdefault('resource_management', {})['battery_threshold'] = battery_threshold
        
        # Task manager detection
        task_manager_detection = self._get_yes_no(
            "Enable Task Manager detection",
            self.config.get('resource_management', {}).get('task_manager_detection', True)
        )
        self.config.setdefault('resource_management', {})['task_manager_detection'] = task_manager_detection
        
        # Temperature threshold
        temperature_threshold = self._get_number(
            "Temperature threshold (°C)",
            self.config.get('resource_management', {}).get('temperature_threshold', 85),
            60, 100
        )
        self.config.setdefault('resource_management', {})['temperature_threshold'] = temperature_threshold
        
        print()
    
    def _configure_profitability(self):
        """Configure profitability settings"""
        print("💰 Profitability Configuration")
        print("-" * 35)
        
        # Electricity cost
        electricity_cost = self._get_float(
            "Electricity cost ($/kWh)",
            self.config.get('profitability', {}).get('electricity_cost', 0.12),
            0.01, 1.0
        )
        self.config.setdefault('profitability', {})['electricity_cost'] = electricity_cost
        
        # Power consumption
        power_consumption = self._get_number(
            "Power consumption (Watts)",
            self.config.get('profitability', {}).get('power_consumption', 200),
            50, 1000
        )
        self.config.setdefault('profitability', {})['power_consumption'] = power_consumption
        
        # Currency
        currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        currency = self._get_input(
            "Currency",
            self.config.get('profitability', {}).get('currency', 'USD'),
            currencies
        )
        self.config.setdefault('profitability', {})['currency'] = currency
        
        print()
    
    def _configure_monitoring(self):
        """Configure monitoring settings"""
        print("📊 Monitoring Configuration")
        print("-" * 30)
        
        # Dashboard port
        dashboard_port = self._get_number(
            "Dashboard port",
            self.config.get('monitoring', {}).get('dashboard_port', 8080),
            1024, 65535
        )
        self.config.setdefault('monitoring', {})['dashboard_port'] = dashboard_port
        
        # Log level
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level = self._get_input(
            "Log level",
            self.config.get('monitoring', {}).get('log_level', 'INFO'),
            log_levels
        )
        self.config.setdefault('monitoring', {})['log_level'] = log_level
        
        # Log rotation
        log_rotation = self._get_yes_no(
            "Enable log rotation",
            self.config.get('monitoring', {}).get('log_rotation', True)
        )
        self.config.setdefault('monitoring', {})['log_rotation'] = log_rotation
        
        print()
    
    def _configure_security(self):
        """Configure security settings"""
        print("🔒 Security Configuration")
        print("-" * 25)
        
        # API access token
        api_token = self._get_input(
            "API access token",
            self.config.get('security', {}).get('api_access_token', 'advanced-miner-token')
        )
        self.config.setdefault('security', {})['api_access_token'] = api_token
        
        # Enable SSL
        enable_ssl = self._get_yes_no(
            "Enable SSL for dashboard",
            self.config.get('security', {}).get('enable_ssl', False)
        )
        self.config.setdefault('security', {})['enable_ssl'] = enable_ssl
        
        print()
    
    def _configure_advanced(self):
        """Configure advanced settings"""
        print("⚙️ Advanced Configuration")
        print("-" * 25)
        
        # Auto restart
        auto_restart = self._get_yes_no(
            "Enable auto restart",
            self.config.get('advanced', {}).get('auto_restart', True)
        )
        self.config.setdefault('advanced', {})['auto_restart'] = auto_restart
        
        # Max restart attempts
        max_restart_attempts = self._get_number(
            "Maximum restart attempts",
            self.config.get('advanced', {}).get('max_restart_attempts', 3),
            1, 10
        )
        self.config.setdefault('advanced', {})['max_restart_attempts'] = max_restart_attempts
        
        # Restart delay
        restart_delay = self._get_number(
            "Restart delay (seconds)",
            self.config.get('advanced', {}).get('restart_delay', 30),
            5, 300
        )
        self.config.setdefault('advanced', {})['restart_delay'] = restart_delay
        
        # Performance mode
        performance_modes = ["conservative", "balanced", "aggressive"]
        performance_mode = self._get_input(
            "Performance mode",
            self.config.get('advanced', {}).get('performance_mode', 'balanced'),
            performance_modes
        )
        self.config.setdefault('advanced', {})['performance_mode'] = performance_mode
        
        # Debug mode
        debug_mode = self._get_yes_no(
            "Enable debug mode",
            self.config.get('advanced', {}).get('debug_mode', False)
        )
        self.config.setdefault('advanced', {})['debug_mode'] = debug_mode
        
        print()
    
    def _save_configuration(self):
        """Save the configuration"""
        print("💾 Saving Configuration...")
        
        try:
            # Validate configuration
            validation = self.config_manager.validate_config(self.config)
            if not validation['valid']:
                print("❌ Configuration validation failed:")
                for issue in validation['issues']:
                    print(f"  - {issue}")
                return False
            
            # Save configuration
            if self.config_manager.save_config(self.config):
                print("✅ Configuration saved successfully!")
                return True
            else:
                print("❌ Failed to save configuration")
                return False
                
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def _show_summary(self):
        """Show configuration summary"""
        print("\n📋 Configuration Summary")
        print("=" * 30)
        
        mining_config = self.config.get('mining', {})
        print(f"Algorithm: {mining_config.get('algorithm', 'N/A')}")
        print(f"Pool: {mining_config.get('pool_url', 'N/A')}")
        print(f"Worker: {mining_config.get('worker_name', 'N/A')}")
        print(f"Wallet: {mining_config.get('wallet', 'N/A')[:20]}...")
        print(f"CPU Threads: {mining_config.get('cpu_threads', 'N/A')}")
        print(f"GPU Enabled: {mining_config.get('gpu_enabled', False)}")
        
        resource_config = self.config.get('resource_management', {})
        print(f"Charging Threshold: {resource_config.get('charging_threshold', 0)}%")
        print(f"Idle Threshold: {resource_config.get('idle_threshold', 0)}s")
        print(f"Battery Threshold: {resource_config.get('battery_threshold', 0)}%")
        
        profitability_config = self.config.get('profitability', {})
        print(f"Electricity Cost: ${profitability_config.get('electricity_cost', 0):.2f}/kWh")
        print(f"Power Consumption: {profitability_config.get('power_consumption', 0)}W")
        print(f"Currency: {profitability_config.get('currency', 'N/A')}")
        
        monitoring_config = self.config.get('monitoring', {})
        print(f"Dashboard Port: {monitoring_config.get('dashboard_port', 0)}")
        print(f"Log Level: {monitoring_config.get('log_level', 'N/A')}")
        
        print("\n🎉 Setup completed successfully!")
        print("You can now start mining with: python main.py run")
        print("Or start the service with: python main.py start")
        print("Access the dashboard at: http://localhost:8080")
    
    def _get_input(self, prompt: str, default: str, valid_options: Optional[list] = None) -> str:
        """Get user input with validation"""
        while True:
            if valid_options:
                print(f"{prompt} ({', '.join(valid_options)}) [{default}]: ", end="")
            else:
                print(f"{prompt} [{default}]: ", end="")
            
            user_input = input().strip()
            
            if not user_input:
                return default
            
            if valid_options and user_input not in valid_options:
                print(f"❌ Invalid option. Please choose from: {', '.join(valid_options)}")
                continue
            
            return user_input
    
    def _get_number(self, prompt: str, default: int, min_val: int, max_val: int) -> int:
        """Get numeric input with range validation"""
        while True:
            print(f"{prompt} ({min_val}-{max_val}) [{default}]: ", end="")
            user_input = input().strip()
            
            if not user_input:
                return default
            
            try:
                value = int(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_float(self, prompt: str, default: float, min_val: float, max_val: float) -> float:
        """Get float input with range validation"""
        while True:
            print(f"{prompt} ({min_val}-{max_val}) [{default}]: ", end="")
            user_input = input().strip()
            
            if not user_input:
                return default
            
            try:
                value = float(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_yes_no(self, prompt: str, default: bool) -> bool:
        """Get yes/no input"""
        while True:
            default_str = "Y" if default else "N"
            print(f"{prompt} (y/n) [{default_str}]: ", end="")
            user_input = input().strip().lower()
            
            if not user_input:
                return default
            
            if user_input in ['y', 'yes']:
                return True
            elif user_input in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' or 'n'")