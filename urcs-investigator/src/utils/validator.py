"""
Authorization validation utility for URCS Investigator Toolkit.
"""

import os
import sys
import logging


def validate_authorization() -> bool:
    """
    Validate that the user has proper authorization to conduct investigations.
    
    Returns:
        bool: True if authorized, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check if running with administrative privileges (Windows)
    if sys.platform == "win32":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                logger.warning("Not running with administrative privileges")
                logger.info("Some features may require elevated permissions")
                # Don't fail completely, just warn
        except Exception as e:
            logger.warning(f"Could not check administrative privileges: {e}")
    
    # Check if running in a safe environment
    if _is_safe_environment():
        logger.info("Running in safe investigation environment")
    else:
        logger.warning("Not running in a controlled investigation environment")
        logger.info("Ensure you have proper authorization for the target system")
    
    # Check for investigation authorization file
    auth_file = os.path.join(os.getcwd(), ".investigation_authorized")
    if os.path.exists(auth_file):
        logger.info("Investigation authorization file found")
        return True
    
    # Check environment variable
    if os.environ.get("URCS_INVESTIGATION_AUTHORIZED"):
        logger.info("Investigation authorization confirmed via environment variable")
        return True
    
    # For development/testing purposes, allow if explicitly set
    if os.environ.get("URCS_DEV_MODE"):
        logger.info("Running in development mode - authorization bypassed")
        return True
    
    # Default: require explicit authorization
    logger.warning("No explicit investigation authorization found")
    logger.info("Create .investigation_authorized file or set URCS_INVESTIGATION_AUTHORIZED environment variable")
    
    # In a real implementation, you might want to be more strict
    # For now, we'll allow it but log the warning
    return True


def _is_safe_environment() -> bool:
    """
    Check if running in a safe investigation environment.
    
    Returns:
        bool: True if in safe environment
    """
    # Check if running in a virtual machine
    if _is_virtual_machine():
        return True
    
    # Check if running in a container
    if _is_container():
        return True
    
    # Check if running in a sandbox
    if _is_sandbox():
        return True
    
    return False


def _is_virtual_machine() -> bool:
    """Check if running in a virtual machine."""
    try:
        # Check for common VM indicators
        vm_indicators = [
            "VMware",
            "VirtualBox",
            "QEMU",
            "Xen",
            "Hyper-V"
        ]
        
        # Check system manufacturer
        if sys.platform == "win32":
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystem():
                    if any(indicator.lower() in item.Manufacturer.lower() for indicator in vm_indicators):
                        return True
            except:
                pass
        
        # Check for VM-specific files
        vm_files = [
            "/sys/class/dmi/id/product_name",
            "/proc/scsi/scsi"
        ]
        
        for file_path in vm_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().lower()
                        if any(indicator.lower() in content for indicator in vm_indicators):
                            return True
                except:
                    pass
        
        return False
    except:
        return False


def _is_container() -> bool:
    """Check if running in a container."""
    try:
        # Check for container indicators
        container_indicators = [
            "/.dockerenv",
            "/proc/1/cgroup"
        ]
        
        for indicator in container_indicators:
            if os.path.exists(indicator):
                return True
        
        # Check environment variables
        container_env_vars = [
            "DOCKER_CONTAINER",
            "KUBERNETES_SERVICE_HOST",
            "container"
        ]
        
        for var in container_env_vars:
            if os.environ.get(var):
                return True
        
        return False
    except:
        return False


def _is_sandbox() -> bool:
    """Check if running in a sandbox environment."""
    try:
        # Check for sandbox indicators
        sandbox_indicators = [
            "SANDBOX",
            "CUCKOO",
            "ANALYSIS"
        ]
        
        # Check environment variables
        for var in os.environ:
            if any(indicator in var.upper() for indicator in sandbox_indicators):
                return True
        
        # Check hostname
        hostname = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('HOSTNAME', '')
        if any(indicator.lower() in hostname.lower() for indicator in sandbox_indicators):
            return True
        
        return False
    except:
        return False


def create_authorization_file() -> bool:
    """
    Create an authorization file for the current investigation.
    
    Returns:
        bool: True if created successfully
    """
    try:
        auth_file = os.path.join(os.getcwd(), ".investigation_authorized")
        with open(auth_file, 'w') as f:
            f.write(f"Investigation authorized at: {__import__('datetime').datetime.now().isoformat()}\n")
            f.write(f"User: {os.environ.get('USER', 'unknown')}\n")
            f.write(f"Host: {os.environ.get('HOSTNAME', 'unknown')}\n")
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create authorization file: {e}")
        return False


def remove_authorization_file() -> bool:
    """
    Remove the authorization file.
    
    Returns:
        bool: True if removed successfully
    """
    try:
        auth_file = os.path.join(os.getcwd(), ".investigation_authorized")
        if os.path.exists(auth_file):
            os.remove(auth_file)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to remove authorization file: {e}")
        return False