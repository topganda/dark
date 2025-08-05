"""Tool Manager for URCS Investigator Toolkit
Handles external tool installation, configuration, and integration.
"""

import os
import sys
import json
import logging
import subprocess
import platform
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse


class ToolManager:
    """Manages external tools installation and configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tools_dir = Path("tools")
        self.tools_dir.mkdir(exist_ok=True)
        
        # Tool configurations
        self.tool_configs = {
            "cape": {
                "name": "CAPEv2",
                "url": "https://github.com/kevoreilly/CAPEv2",
                "install_method": "git",
                "required_files": ["cape2.sh", "cuckoo.py"],
                "config_file": "conf/cuckoo.conf",
                "setup_script": "cape2.sh"
            },
            "sysmon": {
                "name": "Sysmon",
                "url": "https://download.sysinternals.com/files/Sysmon.zip",
                "install_method": "download",
                "required_files": ["Sysmon.exe", "SysmonDrv.sys"],
                "config_file": "sysmonconfig-export.xml",
                "setup_script": None
            },
            "zeek": {
                "name": "Zeek",
                "url": "https://download.zeek.org/zeek-4.2.0.tar.gz",
                "install_method": "package",
                "required_files": ["zeek", "zeekctl"],
                "config_file": "etc/zeekctl.cfg",
                "setup_script": None
            },
            "pe_sieve": {
                "name": "PE-Sieve",
                "url": "https://github.com/hasherezade/pe-sieve/releases/latest",
                "install_method": "github_release",
                "required_files": ["pe-sieve64.exe"],
                "config_file": None,
                "setup_script": None
            },
            "volatility3": {
                "name": "Volatility3",
                "url": "https://github.com/volatilityfoundation/volatility3",
                "install_method": "git",
                "required_files": ["vol.py"],
                "config_file": "volatility3.conf",
                "setup_script": None
            },
            "tcpdump": {
                "name": "tcpdump",
                "url": None,
                "install_method": "system",
                "required_files": ["tcpdump"],
                "config_file": None,
                "setup_script": None
            },
            "binwalk": {
                "name": "binwalk",
                "url": None,
                "install_method": "pip",
                "required_files": ["binwalk"],
                "config_file": None,
                "setup_script": None
            }
        }
    
    def install_all_tools(self) -> Dict[str, bool]:
        """Install all required external tools."""
        self.logger.info("Installing all required external tools")
        
        results = {}
        
        for tool_name, tool_config in self.tool_configs.items():
            try:
                self.logger.info(f"Installing {tool_config['name']}...")
                success = self.install_tool(tool_name)
                results[tool_name] = success
                
                if success:
                    self.logger.info(f"✅ {tool_config['name']} installed successfully")
                else:
                    self.logger.error(f"❌ {tool_config['name']} installation failed")
                    
            except Exception as e:
                self.logger.error(f"Error installing {tool_config['name']}: {e}")
                results[tool_name] = False
        
        return results
    
    def install_tool(self, tool_name: str) -> bool:
        """Install a specific tool."""
        if tool_name not in self.tool_configs:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
        
        tool_config = self.tool_configs[tool_name]
        
        # Check if already installed
        if self.is_tool_installed(tool_name):
            self.logger.info(f"{tool_config['name']} already installed")
            return True
        
        # Install based on method
        install_method = tool_config['install_method']
        
        if install_method == "git":
            return self._install_git_tool(tool_name, tool_config)
        elif install_method == "download":
            return self._install_download_tool(tool_name, tool_config)
        elif install_method == "package":
            return self._install_package_tool(tool_name, tool_config)
        elif install_method == "github_release":
            return self._install_github_release_tool(tool_name, tool_config)
        elif install_method == "system":
            return self._install_system_tool(tool_name, tool_config)
        elif install_method == "pip":
            return self._install_pip_tool(tool_name, tool_config)
        else:
            self.logger.error(f"Unknown install method: {install_method}")
            return False
    
    def _install_git_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install tool from Git repository."""
        try:
            tool_path = self.tools_dir / tool_name
            
            if tool_path.exists():
                # Update existing repository
                subprocess.run(["git", "pull"], cwd=tool_path, check=True)
            else:
                # Clone new repository
                subprocess.run(["git", "clone", tool_config["url"], str(tool_path)], check=True)
            
            # Run setup script if available
            if tool_config.get("setup_script"):
                setup_script = tool_path / tool_config["setup_script"]
                if setup_script.exists():
                    subprocess.run([str(setup_script), "base"], cwd=tool_path, check=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Git installation failed for {tool_name}: {e}")
            return False
    
    def _install_download_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install tool by downloading and extracting."""
        try:
            tool_path = self.tools_dir / tool_name
            tool_path.mkdir(exist_ok=True)
            
            # Download file
            response = requests.get(tool_config["url"], stream=True)
            response.raise_for_status()
            
            # Determine file extension
            parsed_url = urlparse(tool_config["url"])
            filename = os.path.basename(parsed_url.path)
            file_path = tool_path / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract if needed
            if filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tool_path)
            elif filename.endswith('.tar.gz'):
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(tool_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Download installation failed for {tool_name}: {e}")
            return False
    
    def _install_package_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install tool using system package manager."""
        try:
            system = platform.system().lower()
            
            if system == "linux":
                if os.path.exists("/etc/debian_version"):
                    # Debian/Ubuntu
                    subprocess.run(["sudo", "apt-get", "update"], check=True)
                    subprocess.run(["sudo", "apt-get", "install", "-y", tool_name], check=True)
                elif os.path.exists("/etc/redhat-release"):
                    # RHEL/CentOS
                    subprocess.run(["sudo", "yum", "install", "-y", tool_name], check=True)
                else:
                    self.logger.error(f"Unsupported Linux distribution for {tool_name}")
                    return False
            elif system == "windows":
                # Use chocolatey or winget
                try:
                    subprocess.run(["choco", "install", tool_name, "-y"], check=True)
                except FileNotFoundError:
                    try:
                        subprocess.run(["winget", "install", tool_name], check=True)
                    except FileNotFoundError:
                        self.logger.error(f"No package manager found for Windows: {tool_name}")
                        return False
            else:
                self.logger.error(f"Unsupported operating system: {system}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Package installation failed for {tool_name}: {e}")
            return False
    
    def _install_github_release_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install tool from GitHub releases."""
        try:
            # Get latest release
            api_url = tool_config["url"].replace("github.com", "api.github.com/repos") + "/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_data = response.json()
            assets = release_data.get("assets", [])
            
            # Find appropriate asset
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            target_asset = None
            for asset in assets:
                asset_name = asset["name"].lower()
                if system in asset_name and arch in asset_name:
                    target_asset = asset
                    break
            
            if not target_asset:
                # Fallback to any asset
                target_asset = assets[0] if assets else None
            
            if not target_asset:
                self.logger.error(f"No suitable release found for {tool_name}")
                return False
            
            # Download and extract
            tool_path = self.tools_dir / tool_name
            tool_path.mkdir(exist_ok=True)
            
            response = requests.get(target_asset["browser_download_url"], stream=True)
            response.raise_for_status()
            
            file_path = tool_path / target_asset["name"]
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract if needed
            if target_asset["name"].endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tool_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"GitHub release installation failed for {tool_name}: {e}")
            return False
    
    def _install_system_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install system tool (usually already available)."""
        try:
            # Check if tool is available
            result = subprocess.run(["which", tool_name], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            
            # Try to install if not available
            return self._install_package_tool(tool_name, tool_config)
            
        except Exception as e:
            self.logger.error(f"System tool installation failed for {tool_name}: {e}")
            return False
    
    def _install_pip_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Install tool using pip."""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", tool_name], check=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Pip installation failed for {tool_name}: {e}")
            return False
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed and available."""
        if tool_name not in self.tool_configs:
            return False
        
        tool_config = self.tool_configs[tool_name]
        required_files = tool_config.get("required_files", [])
        
        # Check if tool is in PATH
        for file_name in required_files:
            result = subprocess.run(["which", file_name], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        
        # Check if tool is in tools directory
        tool_path = self.tools_dir / tool_name
        if tool_path.exists():
            for file_name in required_files:
                if (tool_path / file_name).exists():
                    return True
        
        return False
    
    def get_tool_path(self, tool_name: str) -> Optional[Path]:
        """Get the path to an installed tool."""
        if not self.is_tool_installed(tool_name):
            return None
        
        tool_config = self.tool_configs[tool_name]
        required_files = tool_config.get("required_files", [])
        
        # Check PATH first
        for file_name in required_files:
            result = subprocess.run(["which", file_name], capture_output=True, text=True)
            if result.returncode == 0:
                return Path(result.stdout.strip())
        
        # Check tools directory
        tool_path = self.tools_dir / tool_name
        if tool_path.exists():
            for file_name in required_files:
                file_path = tool_path / file_name
                if file_path.exists():
                    return file_path
        
        return None
    
    def configure_tool(self, tool_name: str) -> bool:
        """Configure an installed tool."""
        if tool_name not in self.tool_configs:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
        
        tool_config = self.tool_configs[tool_name]
        config_file = tool_config.get("config_file")
        
        if not config_file:
            self.logger.info(f"No configuration needed for {tool_name}")
            return True
        
        try:
            if tool_name == "sysmon":
                return self._configure_sysmon()
            elif tool_name == "zeek":
                return self._configure_zeek()
            elif tool_name == "cape":
                return self._configure_cape()
            else:
                self.logger.info(f"Configuration not implemented for {tool_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Configuration failed for {tool_name}: {e}")
            return False
    
    def _configure_sysmon(self) -> bool:
        """Configure Sysmon with URCS detection rules."""
        try:
            # Create Sysmon configuration
            sysmon_config = """<?xml version="1.0" encoding="UTF-8"?>
<Sysmon schemaversion="4.81">
  <HashAlgorithms>SHA256</HashAlgorithms>
  <EventFiltering>
    <!-- URCS Detection Rules -->
    <ProcessCreate onmatch="include">
      <CommandLine condition="contains">Chrome_update.exe</CommandLine>
      <CommandLine condition="contains">gupdatem</CommandLine>
      <CommandLine condition="contains">algfzpoe.exe</CommandLine>
      <CommandLine condition="contains">Ddriver</CommandLine>
      <CommandLine condition="contains">ctfmon</CommandLine>
      <Image condition="contains">System32\\spool\\drivers\\color\\</Image>
    </ProcessCreate>
    
    <FileCreate onmatch="include">
      <TargetFilename condition="contains">System32\\spool\\drivers\\color\\</TargetFilename>
      <TargetFilename condition="end with">.exe</TargetFilename>
    </FileCreate>
    
    <RegistryEvent onmatch="include">
      <TargetObject condition="contains">HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\ctfmon</TargetObject>
      <TargetObject condition="contains">gupdatem</TargetObject>
    </RegistryEvent>
    
    <NetworkConnect onmatch="include">
      <DestinationHostname condition="contains">gulf.moneroocean.stream</DestinationHostname>
      <DestinationHostname condition="contains">api.ipify.org</DestinationHostname>
      <DestinationPort condition="is">10032</DestinationPort>
    </NetworkConnect>
  </EventFiltering>
</Sysmon>"""
            
            # Save configuration
            config_path = self.tools_dir / "sysmon" / "sysmonconfig-urcs.xml"
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(sysmon_config)
            
            # Install Sysmon with configuration
            sysmon_path = self.get_tool_path("sysmon")
            if sysmon_path:
                subprocess.run([str(sysmon_path), "-accepteula", "-i", str(config_path)], check=True)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Sysmon configuration failed: {e}")
            return False
    
    def _configure_zeek(self) -> bool:
        """Configure Zeek with URCS detection scripts."""
        try:
            # Create Zeek script for URCS detection
            zeek_script = """# URCS Detection Script for Zeek
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http

module URCS;

export {
    redef enum Log::ID += { LOG };
    
    type Info: record {
        ts: time &log;
        uid: string &log;
        id_orig_h: addr &log;
        id_orig_p: port &log;
        id_resp_h: addr &log;
        id_resp_p: port &log;
        proto: transport_proto &log;
        indicator: string &log;
        description: string &log;
    };
}

# Mining pool connections
event connection_established(c: connection)
{
    if ( c$resp$hostname == "gulf.moneroocean.stream" || 
         c$resp$hostname == "api.ipify.org" ||
         c$resp$p == 10032/tcp )
    {
        local info: Info = [
            $ts = network_time(),
            $uid = c$uid,
            $id_orig_h = c$id$orig_h,
            $id_orig_p = c$id$orig_p,
            $id_resp_h = c$id$resp_h,
            $id_resp_p = c$id$resp_p,
            $proto = c$id$resp_p,
            $indicator = "mining_pool_connection",
            $description = "Connection to mining pool or beacon"
        ];
        Log::write(LOG, info);
    }
}

# DNS queries to suspicious domains
event DNS::log_dns(rec: DNS::Info)
{
    if ( rec$query in set("gulf.moneroocean.stream", "api.ipify.org", "moneroocean.stream") )
    {
        local info: Info = [
            $ts = network_time(),
            $uid = rec$uid,
            $id_orig_h = rec$id$orig_h,
            $id_orig_p = rec$id$orig_p,
            $id_resp_h = rec$id$resp_h,
            $id_resp_p = rec$id$resp_p,
            $proto = rec$proto,
            $indicator = "suspicious_dns_query",
            $description = "DNS query to suspicious domain"
        ];
        Log::write(LOG, info);
    }
}"""
            
            # Save script
            script_path = self.tools_dir / "zeek" / "urcs_detection.zeek"
            script_path.parent.mkdir(exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(zeek_script)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Zeek configuration failed: {e}")
            return False
    
    def _configure_cape(self) -> bool:
        """Configure CAPEv2 for URCS analysis."""
        try:
            cape_path = self.tools_dir / "cape"
            if not cape_path.exists():
                self.logger.error("CAPE not installed")
                return False
            
            # Create custom CAPE configuration
            cape_config = """[analysis]
# URCS-specific analysis configuration
timeout = 300
memory_dump = yes
network_dump = yes
process_dump = yes

[processing]
# Enable all processing modules
processing_modules = [
    "static",
    "behavioral",
    "network",
    "memory"
]

[signatures]
# URCS detection signatures
urcs_signatures = [
    "mining_pool_connection",
    "process_hollowing",
    "registry_persistence",
    "service_persistence"
]"""
            
            # Save configuration
            config_path = cape_path / "conf" / "urcs.conf"
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(cape_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"CAPE configuration failed: {e}")
            return False
    
    def run_tool(self, tool_name: str, args: List[str]) -> Tuple[bool, str, str]:
        """Run a tool with arguments."""
        tool_path = self.get_tool_path(tool_name)
        if not tool_path:
            return False, "", f"Tool {tool_name} not found"
        
        try:
            result = subprocess.run([str(tool_path)] + args, 
                                  capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Tool {tool_name} timed out"
        except Exception as e:
            return False, "", f"Error running {tool_name}: {e}"
    
    def get_installation_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tools."""
        status = {}
        
        for tool_name, tool_config in self.tool_configs.items():
            installed = self.is_tool_installed(tool_name)
            tool_path = self.get_tool_path(tool_name) if installed else None
            
            status[tool_name] = {
                "name": tool_config["name"],
                "installed": installed,
                "path": str(tool_path) if tool_path else None,
                "install_method": tool_config["install_method"],
                "config_file": tool_config.get("config_file")
            }
        
        return status