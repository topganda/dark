"""
Logging utility for URCS Investigator Toolkit.
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
    log_file: str = "investigation.log",
    max_size: str = "10MB",
    backup_count: int = 5,
    console_output: bool = True
) -> None:
    """
    Setup comprehensive logging for the investigation toolkit.
    
    Args:
        level: Logging level
        log_dir: Directory for log files
        log_file: Main log file name
        max_size: Maximum log file size
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    """
    # Create log directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    log_path = os.path.join(log_dir, log_file)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=_parse_size(max_size),
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_log_path = os.path.join(log_dir, "error.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=_parse_size(max_size),
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info("Logging system initialized")
    logging.info(f"Log file: {log_path}")
    logging.info(f"Error log: {error_log_path}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


def log_investigation_event(logger: logging.Logger, event_type: str, details: dict) -> None:
    """Log investigation events in a structured format."""
    logger.info(f"INVESTIGATION_EVENT: {event_type} - {details}")


def log_finding(logger: logging.Logger, finding_type: str, severity: str, description: str, evidence: dict) -> None:
    """Log investigation findings in a structured format."""
    logger.warning(f"FINDING: {finding_type} ({severity}) - {description} - {evidence}")


def log_ioc(logger: logging.Logger, ioc_type: str, value: str, confidence: str, source: str) -> None:
    """Log indicators of compromise in a structured format."""
    logger.info(f"IOC: {ioc_type} - {value} (confidence: {confidence}, source: {source})")


def _parse_size(size_str: str) -> int:
    """Parse size string (e.g., '10MB') to bytes."""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)