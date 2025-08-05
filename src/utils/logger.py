"""
Logging Utility
Provides comprehensive logging functionality for the Advanced Crypto Mining Suite.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    log_file: str = "miner.log",
    max_size: str = "10MB",
    backup_count: int = 5,
    console_output: bool = True
) -> None:
    """
    Setup comprehensive logging for the mining suite.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        log_file: Main log file name
        max_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        console_output: Whether to output logs to console
    """
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / log_file,
        maxBytes=_parse_size(max_size),
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "error.log",
        maxBytes=_parse_size(max_size),
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # System log file handler
    system_handler = logging.handlers.RotatingFileHandler(
        log_path / "system.log",
        maxBytes=_parse_size(max_size),
        backupCount=backup_count,
        encoding='utf-8'
    )
    system_handler.setLevel(logging.INFO)
    system_handler.setFormatter(simple_formatter)
    root_logger.addHandler(system_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {logging.getLevelName(level)}")
    logger.info(f"Log directory: {log_path.absolute()}")
    logger.info(f"Main log file: {log_file}")
    logger.info(f"Max log size: {max_size}")
    logger.info(f"Backup count: {backup_count}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_mining_stats(logger: logging.Logger, stats: dict) -> None:
    """
    Log mining statistics in a structured format.
    
    Args:
        logger: Logger instance
        stats: Mining statistics dictionary
    """
    logger.info("=== Mining Statistics ===")
    logger.info(f"Hashrate: {stats.get('hashrate', 0):.2f} H/s")
    logger.info(f"CPU Usage: {stats.get('cpu_usage', 0):.1f}%")
    logger.info(f"GPU Usage: {stats.get('gpu_usage', 0):.1f}%")
    logger.info(f"Temperature: {stats.get('temperature', 0):.1f}°C")
    logger.info(f"Shares Accepted: {stats.get('shares_accepted', 0)}")
    logger.info(f"Shares Rejected: {stats.get('shares_rejected', 0)}")
    logger.info(f"Earnings: ${stats.get('earnings', 0):.4f}")
    logger.info("========================")

def log_system_stats(logger: logging.Logger, stats: dict) -> None:
    """
    Log system statistics in a structured format.
    
    Args:
        logger: Logger instance
        stats: System statistics dictionary
    """
    logger.info("=== System Statistics ===")
    logger.info(f"CPU Usage: {stats.get('cpu_usage', 0):.1f}%")
    logger.info(f"Memory Usage: {stats.get('memory_usage', 0):.1f}%")
    logger.info(f"Disk Usage: {stats.get('disk_usage', 0):.1f}%")
    logger.info(f"Temperature: {stats.get('temperature', 0):.1f}°C")
    logger.info(f"Power Consumption: {stats.get('power_consumption', 0):.1f}W")
    logger.info(f"Battery: {stats.get('battery_info', {}).get('percent', 0)}%")
    logger.info(f"Plugged In: {stats.get('battery_info', {}).get('plugged', False)}")
    logger.info("========================")

def log_profitability_stats(logger: logging.Logger, stats: dict) -> None:
    """
    Log profitability statistics in a structured format.
    
    Args:
        logger: Logger instance
        stats: Profitability statistics dictionary
    """
    logger.info("=== Profitability Statistics ===")
    logger.info(f"Daily Earnings: ${stats.get('daily_earnings', 0):.4f}")
    logger.info(f"Monthly Earnings: ${stats.get('monthly_earnings', 0):.4f}")
    logger.info(f"Yearly Earnings: ${stats.get('yearly_earnings', 0):.4f}")
    logger.info(f"Electricity Cost: ${stats.get('electricity_cost', 0):.4f}/day")
    logger.info(f"Net Profit: ${stats.get('net_profit', 0):.4f}/day")
    logger.info(f"ROI: {stats.get('roi_percentage', 0):.2f}%")
    logger.info("================================")

def log_resource_mode(logger: logging.Logger, mode: str, reason: str = "") -> None:
    """
    Log resource mode changes.
    
    Args:
        logger: Logger instance
        mode: New resource mode
        reason: Reason for mode change
    """
    if reason:
        logger.info(f"Resource mode changed to {mode.upper()}: {reason}")
    else:
        logger.info(f"Resource mode changed to {mode.upper()}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log an error with additional context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    if context:
        logger.error(f"Error in {context}: {error}", exc_info=True)
    else:
        logger.error(f"Error occurred: {error}", exc_info=True)

def log_performance_metrics(logger: logging.Logger, metrics: dict) -> None:
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance
        metrics: Performance metrics dictionary
    """
    logger.info("=== Performance Metrics ===")
    logger.info(f"Response Time: {metrics.get('response_time', 0):.3f}s")
    logger.info(f"Throughput: {metrics.get('throughput', 0):.2f} req/s")
    logger.info(f"Memory Usage: {metrics.get('memory_usage', 0):.1f}%")
    logger.info(f"CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
    logger.info(f"Network I/O: {metrics.get('network_io', 0):.2f} MB/s")
    logger.info("==========================")

def log_security_event(logger: logging.Logger, event_type: str, details: str, severity: str = "INFO") -> None:
    """
    Log security-related events.
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        details: Event details
        severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(log_level, f"SECURITY EVENT [{event_type}]: {details}")

def log_network_event(logger: logging.Logger, event_type: str, details: str) -> None:
    """
    Log network-related events.
    
    Args:
        logger: Logger instance
        event_type: Type of network event
        details: Event details
    """
    logger.info(f"NETWORK EVENT [{event_type}]: {details}")

def log_configuration_change(logger: logging.Logger, section: str, key: str, old_value: any, new_value: any) -> None:
    """
    Log configuration changes.
    
    Args:
        logger: Logger instance
        section: Configuration section
        key: Configuration key
        old_value: Previous value
        new_value: New value
    """
    logger.info(f"CONFIG CHANGE [{section}.{key}]: {old_value} -> {new_value}")

def log_startup_info(logger: logging.Logger, version: str, config: dict) -> None:
    """
    Log startup information.
    
    Args:
        logger: Logger instance
        version: Application version
        config: Configuration dictionary
    """
    logger.info("=== Advanced Crypto Mining Suite Startup ===")
    logger.info(f"Version: {version}")
    logger.info(f"Algorithm: {config.get('mining', {}).get('algorithm', 'N/A')}")
    logger.info(f"Pool: {config.get('mining', {}).get('pool_url', 'N/A')}")
    logger.info(f"Worker: {config.get('mining', {}).get('worker_name', 'N/A')}")
    logger.info(f"CPU Threads: {config.get('mining', {}).get('cpu_threads', 'N/A')}")
    logger.info(f"GPU Enabled: {config.get('mining', {}).get('gpu_enabled', False)}")
    logger.info("=============================================")

def log_shutdown_info(logger: logging.Logger, uptime: float, total_earnings: float) -> None:
    """
    Log shutdown information.
    
    Args:
        logger: Logger instance
        uptime: Total uptime in seconds
        total_earnings: Total earnings during session
    """
    logger.info("=== Advanced Crypto Mining Suite Shutdown ===")
    logger.info(f"Total Uptime: {uptime:.1f} seconds ({uptime/3600:.2f} hours)")
    logger.info(f"Total Earnings: ${total_earnings:.4f}")
    logger.info("=============================================")

def _parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., "10MB", "1GB") to bytes.
    
    Args:
        size_str: Size string with unit
    
    Returns:
        Size in bytes
    """
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith('MB'):
        return int(float(size_str[:-2]) * 1024 * 1024)
    elif size_str.endswith('GB'):
        return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
    else:
        return int(size_str)

def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 30) -> None:
    """
    Clean up old log files.
    
    Args:
        log_dir: Log directory path
        days_to_keep: Number of days to keep log files
    """
    import time
    from pathlib import Path
    
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    cutoff_time = time.time() - (days_to_keep * 24 * 3600)
    
    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Deleted old log file: {log_file}")
            except Exception as e:
                print(f"Error deleting log file {log_file}: {e}")

def get_log_file_info(log_dir: str = "logs") -> dict:
    """
    Get information about log files.
    
    Args:
        log_dir: Log directory path
    
    Returns:
        Dictionary with log file information
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return {}
    
    log_info = {}
    total_size = 0
    
    for log_file in log_path.glob("*.log*"):
        try:
            stat = log_file.stat()
            log_info[log_file.name] = {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'size_mb': stat.st_size / (1024 * 1024)
            }
            total_size += stat.st_size
        except Exception as e:
            log_info[log_file.name] = {'error': str(e)}
    
    return {
        'files': log_info,
        'total_size': total_size,
        'total_size_mb': total_size / (1024 * 1024),
        'file_count': len(log_info)
    }