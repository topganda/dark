"""
Configuration Manager
Handles loading, saving, and managing configuration files for the mining suite.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """
    Manages configuration for the Advanced Crypto Mining Suite.
    Handles loading, saving, and validation of configuration files.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Default configuration path
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path("config/miner_config.json")
        
        # Default configuration
        self.default_config = {
            "mining": {
                "algorithm": "rx/0",
                "pool_url": "stratum+tcp://pool.supportxmr.com:3333",
                "wallet": "",
                "worker_name": "advanced-miner",
                "cpu_threads": "auto",
                "gpu_enabled": False,
                "algorithms": ["rx/0", "kawpow", "ethash"],
                "pools": [
                    {
                        "name": "SupportXMR",
                        "url": "stratum+tcp://pool.supportxmr.com:3333",
                        "backup_url": "stratum+tcp://pool.supportxmr.com:7777"
                    },
                    {
                        "name": "MoneroOcean",
                        "url": "stratum+tcp://gulf.moneroocean.stream:10032",
                        "backup_url": "stratum+tcp://gulf.moneroocean.stream:10033"
                    }
                ]
            },
            "resource_management": {
                "charging_threshold": 90,
                "idle_threshold": 300,
                "battery_threshold": 25,
                "task_manager_detection": True,
                "stealth_mode_duration": 30,
                "temperature_threshold": 85,
                "memory_threshold": 90,
                "disk_threshold": 95
            },
            "profitability": {
                "electricity_cost": 0.12,
                "power_consumption": 200,
                "currency": "USD",
                "price_update_interval": 300,
                "profitability_calculation_interval": 60
            },
            "monitoring": {
                "dashboard_port": 8080,
                "api_port": 18067,
                "log_level": "INFO",
                "log_rotation": True,
                "max_log_size": "10MB",
                "backup_count": 5
            },
            "security": {
                "api_access_token": "advanced-miner-token",
                "enable_ssl": False,
                "allowed_ips": ["127.0.0.1", "::1"],
                "max_connections": 10
            },
            "notifications": {
                "enabled": False,
                "email": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipient": ""
                },
                "discord": {
                    "webhook_url": "",
                    "bot_name": "Advanced Miner"
                },
                "telegram": {
                    "bot_token": "",
                    "chat_id": ""
                }
            },
            "advanced": {
                "auto_restart": True,
                "restart_on_failure": True,
                "max_restart_attempts": 3,
                "restart_delay": 30,
                "performance_mode": "balanced",
                "debug_mode": False,
                "data_retention_days": 30
            }
        }
        
        self.logger.info(f"Config Manager initialized with path: {self.config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                self.logger.info(f"Loading configuration from {self.config_path}")
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                config = self._merge_configs(self.default_config, config)
                self.logger.info("Configuration loaded successfully")
                return config
            else:
                self.logger.info("Configuration file not found, creating default")
                return self.create_default_config()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.logger.info("Using default configuration")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration"""
        try:
            config = self.default_config.copy()
            self.save_config(config)
            return config
        except Exception as e:
            self.logger.error(f"Error creating default configuration: {e}")
            return self.default_config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            config = self.load_config()
            updated_config = self._merge_configs(config, updates)
            return self.save_config(updated_config)
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate mining configuration
        mining_config = config.get('mining', {})
        if not mining_config.get('wallet'):
            issues.append("Mining wallet address is required")
        
        if not mining_config.get('pool_url'):
            issues.append("Mining pool URL is required")
        
        # Validate resource management
        resource_config = config.get('resource_management', {})
        if resource_config.get('charging_threshold', 0) > 100:
            issues.append("Charging threshold must be between 0 and 100")
        
        if resource_config.get('battery_threshold', 0) > 100:
            issues.append("Battery threshold must be between 0 and 100")
        
        # Validate profitability
        profitability_config = config.get('profitability', {})
        if profitability_config.get('electricity_cost', 0) < 0:
            issues.append("Electricity cost must be positive")
        
        if profitability_config.get('power_consumption', 0) < 0:
            issues.append("Power consumption must be positive")
        
        # Validate monitoring
        monitoring_config = config.get('monitoring', {})
        port = monitoring_config.get('dashboard_port', 8080)
        if port < 1 or port > 65535:
            issues.append("Dashboard port must be between 1 and 65535")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def get_mining_config(self) -> Dict[str, Any]:
        """Get mining-specific configuration"""
        config = self.load_config()
        return config.get('mining', {})
    
    def get_resource_config(self) -> Dict[str, Any]:
        """Get resource management configuration"""
        config = self.load_config()
        return config.get('resource_management', {})
    
    def get_profitability_config(self) -> Dict[str, Any]:
        """Get profitability configuration"""
        config = self.load_config()
        return config.get('profitability', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        config = self.load_config()
        return config.get('monitoring', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        config = self.load_config()
        return config.get('security', {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration"""
        config = self.load_config()
        return config.get('notifications', {})
    
    def get_advanced_config(self) -> Dict[str, Any]:
        """Get advanced configuration"""
        config = self.load_config()
        return config.get('advanced', {})
    
    def set_mining_config(self, mining_config: Dict[str, Any]) -> bool:
        """Set mining configuration"""
        return self.update_config({'mining': mining_config})
    
    def set_resource_config(self, resource_config: Dict[str, Any]) -> bool:
        """Set resource management configuration"""
        return self.update_config({'resource_management': resource_config})
    
    def set_profitability_config(self, profitability_config: Dict[str, Any]) -> bool:
        """Set profitability configuration"""
        return self.update_config({'profitability': profitability_config})
    
    def set_monitoring_config(self, monitoring_config: Dict[str, Any]) -> bool:
        """Set monitoring configuration"""
        return self.update_config({'monitoring': monitoring_config})
    
    def set_security_config(self, security_config: Dict[str, Any]) -> bool:
        """Set security configuration"""
        return self.update_config({'security': security_config})
    
    def set_notification_config(self, notification_config: Dict[str, Any]) -> bool:
        """Set notification configuration"""
        return self.update_config({'notifications': notification_config})
    
    def set_advanced_config(self, advanced_config: Dict[str, Any]) -> bool:
        """Set advanced configuration"""
        return self.update_config({'advanced': advanced_config})
    
    def backup_config(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the current configuration"""
        try:
            if not backup_path:
                backup_path = f"{self.config_path}.backup"
            
            config = self.load_config()
            with open(backup_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up configuration: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """Restore configuration from backup"""
        try:
            with open(backup_path, 'r') as f:
                config = json.load(f)
            
            # Validate the backup
            validation = self.validate_config(config)
            if not validation['valid']:
                self.logger.error(f"Backup configuration is invalid: {validation['issues']}")
                return False
            
            return self.save_config(config)
            
        except Exception as e:
            self.logger.error(f"Error restoring configuration: {e}")
            return False
    
    def export_config(self, format: str = 'json') -> str:
        """Export configuration in specified format"""
        try:
            config = self.load_config()
            
            if format.lower() == 'json':
                return json.dumps(config, indent=2)
            elif format.lower() == 'env':
                return self._config_to_env(config)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return ""
    
    def import_config(self, config_data: str, format: str = 'json') -> bool:
        """Import configuration from string"""
        try:
            if format.lower() == 'json':
                config = json.loads(config_data)
            elif format.lower() == 'env':
                config = self._env_to_config(config_data)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # Validate the imported configuration
            validation = self.validate_config(config)
            if not validation['valid']:
                self.logger.error(f"Imported configuration is invalid: {validation['issues']}")
                return False
            
            return self.save_config(config)
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def _merge_configs(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _config_to_env(self, config: Dict[str, Any], prefix: str = "MINER_") -> str:
        """Convert configuration to environment variable format"""
        env_lines = []
        
        def flatten_dict(d, parent_key=''):
            for key, value in d.items():
                new_key = f"{parent_key}_{key}" if parent_key else key
                if isinstance(value, dict):
                    flatten_dict(value, new_key)
                else:
                    env_lines.append(f"{prefix}{new_key.upper()}={value}")
        
        flatten_dict(config)
        return "\n".join(env_lines)
    
    def _env_to_config(self, env_data: str) -> Dict[str, Any]:
        """Convert environment variable format to configuration"""
        config = {}
        
        for line in env_data.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                # Remove MINER_ prefix and convert to nested structure
                key = key.replace('MINER_', '').lower()
                
                # Convert value to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                
                # Set nested value
                keys = key.split('_')
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
        
        return config
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about the current configuration"""
        try:
            config = self.load_config()
            validation = self.validate_config(config)
            
            return {
                'config_path': str(self.config_path),
                'config_exists': self.config_path.exists(),
                'config_size': self.config_path.stat().st_size if self.config_path.exists() else 0,
                'valid': validation['valid'],
                'issues': validation['issues'],
                'sections': list(config.keys()),
                'last_modified': self.config_path.stat().st_mtime if self.config_path.exists() else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting config info: {e}")
            return {}