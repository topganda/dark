"""
Configuration Manager for URCS Investigator Toolkit
Handles loading, validation, and management of investigation configuration.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration for the URCS Investigator Toolkit."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/investigation_config.json"
        self.logger = logging.getLogger(__name__)
        self.config = self._load_default_config()
        
        # Load custom config if exists
        if os.path.exists(self.config_path):
            self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "investigation": {
                "scope": "comprehensive",
                "modules": ["static", "behavioral", "memory", "network"],
                "output_format": "html",
                "parallel_analysis": True,
                "timeout": 300
            },
            "detection": {
                "yara_rules": "yara_rules/",
                "thresholds": {
                    "entropy": 7.5,
                    "cpu_drop": 70,
                    "memory_usage": 80,
                    "network_connections": 100
                },
                "patterns": {
                    "suspicious_names": ["ctfmon", "gupdatem", "Ddriver"],
                    "suspicious_paths": [
                        "System32\\spool\\drivers\\color\\",
                        "System32\\drivers\\",
                        "Temp\\"
                    ],
                    "suspicious_pools": [
                        "gulf.moneroocean.stream:10032",
                        "pool.supportxmr.com:3333",
                        "xmr.pool.gpu:3333"
                    ]
                }
            },
            "monitoring": {
                "sysmon": True,
                "etw_tracing": True,
                "powershell_logging": True,
                "network_capture": True,
                "performance_monitoring": True
            },
            "analysis": {
                "static": {
                    "entropy_analysis": True,
                    "signature_verification": True,
                    "yara_scanning": True,
                    "pe_analysis": True
                },
                "behavioral": {
                    "registry_analysis": True,
                    "service_enumeration": True,
                    "task_analysis": True,
                    "file_system_analysis": True
                },
                "memory": {
                    "process_injection_detection": True,
                    "memory_region_analysis": True,
                    "dll_analysis": True,
                    "handle_analysis": True
                },
                "network": {
                    "traffic_capture": True,
                    "protocol_analysis": True,
                    "dns_analysis": True,
                    "connection_analysis": True
                }
            },
            "reporting": {
                "templates": "templates/",
                "output_formats": ["html", "pdf", "json", "csv"],
                "include_screenshots": True,
                "include_timeline": True,
                "include_iocs": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/investigation.log",
                "max_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "security": {
                "hash_verification": True,
                "digital_signature_check": True,
                "sandbox_analysis": True,
                "quarantine_suspicious": False
            }
        }
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                custom_config = json.load(f)
                self._merge_config(custom_config)
                self.logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load custom config: {e}")
    
    def _merge_config(self, custom_config: Dict[str, Any]):
        """Merge custom configuration with default."""
        def merge_dicts(default: Dict, custom: Dict):
            for key, value in custom.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dicts(default[key], value)
                else:
                    default[key] = value
        
        merge_dicts(self.config, custom_config)
    
    def load_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (dot notation supported)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value by key (dot notation supported)."""
        keys = key.split('.')
        config = self.config
        
        try:
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            return True
        except Exception as e:
            self.logger.error(f"Failed to set configuration key {key}: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return any issues."""
        issues = {}
        
        # Check required directories
        required_dirs = [
            self.get("detection.yara_rules"),
            self.get("reporting.templates"),
            "logs",
            "reports"
        ]
        
        for directory in required_dirs:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    issues[f"directory_{directory}"] = f"Cannot create directory: {e}"
        
        # Check thresholds
        thresholds = self.get("detection.thresholds", {})
        for threshold, value in thresholds.items():
            if not isinstance(value, (int, float)) or value < 0:
                issues[f"threshold_{threshold}"] = f"Invalid threshold value: {value}"
        
        return issues
    
    def create_default_config(self) -> bool:
        """Create and save default configuration."""
        return self.save_config(self.config)