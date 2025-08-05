"""Enhanced Network Analysis Module for URCS Investigator Toolkit."""

import os
import json
import logging
import subprocess
import socket
import struct
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class NetworkAnalyzer:
    """Performs comprehensive network traffic analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.suspicious_domains = config.get("detection.network.suspicious_domains", [])
        self.suspicious_ports = config.get("detection.network.suspicious_ports", [])
        self.mining_pools = config.get("detection.network.mining_pools", [])
    
    def analyze_network_traffic(self, scope: str = "full") -> Dict[str, Any]:
        """Comprehensive network analysis (T-9)."""
        self.logger.info(f"Performing network analysis with scope: {scope}")
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "scope": scope,
            "current_connections": [],
            "dns_queries": [],
            "suspicious_connections": [],
            "mining_pool_connections": [],
            "stratum_protocol_detected": False,
            "network_iocs": [],
            "mitre_mapping": []
        }
        
        try:
            # T-9: Network IOC extraction
            results["current_connections"] = self._analyze_current_connections()
            results["dns_queries"] = self._analyze_dns_queries()
            results["suspicious_connections"] = self._find_suspicious_connections()
            results["mining_pool_connections"] = self._find_mining_pool_connections()
            results["stratum_protocol_detected"] = self._detect_stratum_protocol()
            
            # Extract network IOCs
            results["network_iocs"] = self._extract_network_iocs(results)
            
            # Map to MITRE ATT&CK
            results["mitre_mapping"] = self._map_mitre_techniques(results)
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def capture_live_traffic(self, interface: str, duration: int = 60) -> Dict[str, Any]:
        """Capture live network traffic."""
        self.logger.info(f"Capturing live traffic on interface {interface} for {duration} seconds")
        
        results = {
            "interface": interface,
            "duration": duration,
            "capture_start": datetime.now().isoformat(),
            "packets_captured": 0,
            "connections": [],
            "suspicious_traffic": [],
            "dns_queries": [],
            "capture_file": None
        }
        
        try:
            # Use tcpdump or similar tool for packet capture
            capture_file = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
            
            cmd = [
                "tcpdump", "-i", interface, "-w", capture_file, 
                "-c", "1000",  # Capture 1000 packets
                "host", "gulf.moneroocean.stream", "or", "host", "api.ipify.org"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if process.returncode == 0:
                results["capture_file"] = capture_file
                results["packets_captured"] = 1000
                
                # Analyze the captured traffic
                analysis_results = self._analyze_capture_file(capture_file)
                results.update(analysis_results)
                
        except Exception as e:
            self.logger.error(f"Live traffic capture failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def analyze_capture_file(self, pcap_file: str) -> Dict[str, Any]:
        """Analyze network capture file (T-9)."""
        self.logger.info(f"Analyzing capture file: {pcap_file}")
        
        results = {
            "pcap_file": pcap_file,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_packets": 0,
            "connections": [],
            "dns_queries": [],
            "suspicious_traffic": [],
            "stratum_detected": False,
            "network_iocs": []
        }
        
        try:
            # Use Zeek for analysis
            zeek_results = self._analyze_with_zeek(pcap_file)
            results.update(zeek_results)
            
            # Additional analysis
            results["connections"] = self._extract_connections_from_pcap(pcap_file)
            results["dns_queries"] = self._extract_dns_from_pcap(pcap_file)
            results["suspicious_traffic"] = self._find_suspicious_in_pcap(pcap_file)
            results["stratum_detected"] = self._detect_stratum_in_pcap(pcap_file)
            
            # Extract IOCs
            results["network_iocs"] = self._extract_iocs_from_pcap(pcap_file)
            
        except Exception as e:
            self.logger.error(f"Capture file analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def analyze_current_connections(self) -> List[Dict[str, Any]]:
        """Analyze current network connections."""
        self.logger.info("Analyzing current network connections")
        connections = []
        
        try:
            # Use netstat to get current connections
            cmd = ["netstat", "-an"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                
                for line in lines[4:]:  # Skip header lines
                    if line.strip():
                        connection_info = self._parse_netstat_line(line)
                        if connection_info:
                            connections.append(connection_info)
                            
        except Exception as e:
            self.logger.error(f"Current connection analysis failed: {e}")
        
        return connections
    
    def detect_stratum_protocol(self) -> Dict[str, Any]:
        """Detect Stratum protocol usage (T-9)."""
        self.logger.info("Detecting Stratum protocol usage")
        
        results = {
            "stratum_detected": False,
            "connections": [],
            "ports": [],
            "patterns": [],
            "severity": "low"
        }
        
        try:
            # Check for Stratum protocol indicators
            stratum_indicators = [
                "stratum+tcp://",
                "gulf.moneroocean.stream:10032",
                "moneroocean.stream",
                "stratum"
            ]
            
            # Check current connections
            current_connections = self.analyze_current_connections()
            
            for connection in current_connections:
                remote_addr = connection.get("remote_address", "")
                remote_port = connection.get("remote_port", "")
                
                # Check for mining pool connections
                for indicator in stratum_indicators:
                    if indicator in remote_addr or str(remote_port) in indicator:
                        results["stratum_detected"] = True
                        results["connections"].append(connection)
                        results["severity"] = "high"
                        
                        if remote_port not in results["ports"]:
                            results["ports"].append(remote_port)
                        
                        if indicator not in results["patterns"]:
                            results["patterns"].append(indicator)
                            
        except Exception as e:
            self.logger.error(f"Stratum protocol detection failed: {e}")
        
        return results
    
    def extract_network_iocs(self) -> List[Dict[str, Any]]:
        """Extract network IOCs (T-9)."""
        self.logger.info("Extracting network IOCs")
        iocs = []
        
        try:
            # Get current connections
            connections = self.analyze_current_connections()
            
            # Extract IOCs from connections
            for connection in connections:
                remote_addr = connection.get("remote_address", "")
                remote_port = connection.get("remote_port", "")
                
                # Check for suspicious indicators
                if self._is_suspicious_connection(remote_addr, remote_port):
                    ioc = {
                        "type": "network_connection",
                        "ip_address": remote_addr,
                        "port": remote_port,
                        "protocol": connection.get("protocol", "tcp"),
                        "description": f"Suspicious connection to {remote_addr}:{remote_port}",
                        "severity": "high",
                        "mitre_technique": "T1071.001"
                    }
                    iocs.append(ioc)
            
            # Check for DNS queries
            dns_queries = self._analyze_dns_queries()
            for query in dns_queries:
                if self._is_suspicious_domain(query.get("domain", "")):
                    ioc = {
                        "type": "dns_query",
                        "domain": query.get("domain"),
                        "query_type": query.get("query_type"),
                        "description": f"Suspicious DNS query to {query.get('domain')}",
                        "severity": "medium",
                        "mitre_technique": "T1071.004"
                    }
                    iocs.append(ioc)
                    
        except Exception as e:
            self.logger.error(f"Network IOC extraction failed: {e}")
        
        return iocs
    
    # Helper methods for specific tasks
    
    def _analyze_current_connections(self) -> List[Dict[str, Any]]:
        """Analyze current network connections."""
        connections = []
        
        try:
            # Use netstat to get current connections
            cmd = ["netstat", "-an"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                
                for line in lines[4:]:  # Skip header lines
                    if line.strip():
                        connection_info = self._parse_netstat_line(line)
                        if connection_info:
                            connections.append(connection_info)
                            
        except Exception as e:
            self.logger.error(f"Current connection analysis failed: {e}")
        
        return connections
    
    def _analyze_dns_queries(self) -> List[Dict[str, Any]]:
        """Analyze DNS queries."""
        queries = []
        
        try:
            # Check for DNS queries to suspicious domains
            suspicious_domains = [
                "api.ipify.org",
                "gulf.moneroocean.stream",
                "moneroocean.stream"
            ]
            
            for domain in suspicious_domains:
                # Use nslookup to check domain resolution
                cmd = ["nslookup", domain]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0:
                    queries.append({
                        "domain": domain,
                        "query_type": "A",
                        "resolved": True,
                        "response": process.stdout,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    queries.append({
                        "domain": domain,
                        "query_type": "A",
                        "resolved": False,
                        "error": process.stderr,
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            self.logger.error(f"DNS query analysis failed: {e}")
        
        return queries
    
    def _find_suspicious_connections(self) -> List[Dict[str, Any]]:
        """Find suspicious network connections."""
        suspicious = []
        
        try:
            connections = self.analyze_current_connections()
            
            for connection in connections:
                remote_addr = connection.get("remote_address", "")
                remote_port = connection.get("remote_port", "")
                
                if self._is_suspicious_connection(remote_addr, remote_port):
                    suspicious.append({
                        "type": "suspicious_connection",
                        "local_address": connection.get("local_address"),
                        "local_port": connection.get("local_port"),
                        "remote_address": remote_addr,
                        "remote_port": remote_port,
                        "protocol": connection.get("protocol"),
                        "state": connection.get("state"),
                        "description": f"Suspicious connection to {remote_addr}:{remote_port}",
                        "severity": "high"
                    })
                    
        except Exception as e:
            self.logger.error(f"Suspicious connection detection failed: {e}")
        
        return suspicious
    
    def _find_mining_pool_connections(self) -> List[Dict[str, Any]]:
        """Find connections to mining pools."""
        pool_connections = []
        
        try:
            connections = self.analyze_current_connections()
            
            for connection in connections:
                remote_addr = connection.get("remote_address", "")
                remote_port = connection.get("remote_port", "")
                
                if self._is_mining_pool_connection(remote_addr, remote_port):
                    pool_connections.append({
                        "type": "mining_pool_connection",
                        "pool_address": remote_addr,
                        "pool_port": remote_port,
                        "protocol": connection.get("protocol"),
                        "description": f"Connection to mining pool {remote_addr}:{remote_port}",
                        "severity": "high",
                        "mitre_technique": "T1071.001"
                    })
                    
        except Exception as e:
            self.logger.error(f"Mining pool connection detection failed: {e}")
        
        return pool_connections
    
    def _detect_stratum_protocol(self) -> bool:
        """Detect Stratum protocol usage."""
        try:
            # Check for Stratum protocol indicators
            stratum_indicators = [
                "stratum+tcp://",
                "gulf.moneroocean.stream:10032",
                "moneroocean.stream"
            ]
            
            connections = self.analyze_current_connections()
            
            for connection in connections:
                remote_addr = connection.get("remote_address", "")
                remote_port = connection.get("remote_port", "")
                
                for indicator in stratum_indicators:
                    if indicator in remote_addr or str(remote_port) in indicator:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Stratum protocol detection failed: {e}")
            return False
    
    def _extract_network_iocs(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract network IOCs from analysis results."""
        iocs = []
        
        try:
            # Extract from suspicious connections
            for connection in analysis_results.get("suspicious_connections", []):
                ioc = {
                    "type": "network_connection",
                    "ip_address": connection.get("remote_address"),
                    "port": connection.get("remote_port"),
                    "protocol": connection.get("protocol"),
                    "description": connection.get("description"),
                    "severity": connection.get("severity"),
                    "mitre_technique": "T1071.001"
                }
                iocs.append(ioc)
            
            # Extract from mining pool connections
            for connection in analysis_results.get("mining_pool_connections", []):
                ioc = {
                    "type": "mining_pool_connection",
                    "ip_address": connection.get("pool_address"),
                    "port": connection.get("pool_port"),
                    "protocol": connection.get("protocol"),
                    "description": connection.get("description"),
                    "severity": connection.get("severity"),
                    "mitre_technique": "T1071.001"
                }
                iocs.append(ioc)
            
            # Extract from DNS queries
            for query in analysis_results.get("dns_queries", []):
                if self._is_suspicious_domain(query.get("domain", "")):
                    ioc = {
                        "type": "dns_query",
                        "domain": query.get("domain"),
                        "query_type": query.get("query_type"),
                        "description": f"Suspicious DNS query to {query.get('domain')}",
                        "severity": "medium",
                        "mitre_technique": "T1071.004"
                    }
                    iocs.append(ioc)
                    
        except Exception as e:
            self.logger.error(f"Network IOC extraction failed: {e}")
        
        return iocs
    
    def _map_mitre_techniques(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map findings to MITRE ATT&CK techniques."""
        techniques = []
        
        try:
            # Map based on findings
            if analysis_results.get("suspicious_connections"):
                techniques.append({
                    "technique_id": "T1071.001",
                    "technique_name": "Application Layer Protocol: Web Protocols",
                    "description": "Suspicious network connections detected"
                })
            
            if analysis_results.get("mining_pool_connections"):
                techniques.append({
                    "technique_id": "T1071.001",
                    "technique_name": "Application Layer Protocol: Web Protocols",
                    "description": "Mining pool connections detected"
                })
            
            if analysis_results.get("dns_queries"):
                techniques.append({
                    "technique_id": "T1071.004",
                    "technique_name": "Application Layer Protocol: DNS",
                    "description": "Suspicious DNS queries detected"
                })
            
            if analysis_results.get("stratum_protocol_detected"):
                techniques.append({
                    "technique_id": "T1071.001",
                    "technique_name": "Application Layer Protocol: Web Protocols",
                    "description": "Stratum protocol usage detected"
                })
            
        except Exception as e:
            self.logger.error(f"MITRE technique mapping failed: {e}")
        
        return techniques
    
    def _analyze_with_zeek(self, pcap_file: str) -> Dict[str, Any]:
        """Analyze PCAP file with Zeek (T-9)."""
        results = {
            "zeek_analysis": {},
            "conn_log": [],
            "dns_log": [],
            "http_log": []
        }
        
        try:
            # Use Zeek to analyze the PCAP file
            zeek_cmd = ["zeek", "-r", pcap_file, "local"]
            process = subprocess.run(zeek_cmd, capture_output=True, text=True, timeout=300)
            
            if process.returncode == 0:
                # Parse Zeek logs
                results["conn_log"] = self._parse_zeek_conn_log("conn.log")
                results["dns_log"] = self._parse_zeek_dns_log("dns.log")
                results["http_log"] = self._parse_zeek_http_log("http.log")
                
        except Exception as e:
            self.logger.error(f"Zeek analysis failed: {e}")
        
        return results
    
    def _parse_zeek_conn_log(self, log_file: str) -> List[Dict[str, Any]]:
        """Parse Zeek connection log."""
        connections = []
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.startswith('#'):
                            parts = line.strip().split('\t')
                            if len(parts) >= 8:
                                connection = {
                                    "timestamp": parts[0],
                                    "uid": parts[1],
                                    "id_orig_h": parts[2],
                                    "id_orig_p": parts[3],
                                    "id_resp_h": parts[4],
                                    "id_resp_p": parts[5],
                                    "proto": parts[6],
                                    "service": parts[7] if len(parts) > 7 else ""
                                }
                                connections.append(connection)
                                
        except Exception as e:
            self.logger.error(f"Zeek connection log parsing failed: {e}")
        
        return connections
    
    def _parse_zeek_dns_log(self, log_file: str) -> List[Dict[str, Any]]:
        """Parse Zeek DNS log."""
        queries = []
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.startswith('#'):
                            parts = line.strip().split('\t')
                            if len(parts) >= 5:
                                query = {
                                    "timestamp": parts[0],
                                    "uid": parts[1],
                                    "id_orig_h": parts[2],
                                    "id_resp_h": parts[3],
                                    "query": parts[4],
                                    "qtype": parts[5] if len(parts) > 5 else ""
                                }
                                queries.append(query)
                                
        except Exception as e:
            self.logger.error(f"Zeek DNS log parsing failed: {e}")
        
        return queries
    
    def _parse_zeek_http_log(self, log_file: str) -> List[Dict[str, Any]]:
        """Parse Zeek HTTP log."""
        requests = []
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.startswith('#'):
                            parts = line.strip().split('\t')
                            if len(parts) >= 7:
                                request = {
                                    "timestamp": parts[0],
                                    "uid": parts[1],
                                    "id_orig_h": parts[2],
                                    "id_resp_h": parts[3],
                                    "method": parts[5],
                                    "host": parts[6],
                                    "uri": parts[7] if len(parts) > 7 else ""
                                }
                                requests.append(request)
                                
        except Exception as e:
            self.logger.error(f"Zeek HTTP log parsing failed: {e}")
        
        return requests
    
    def _extract_connections_from_pcap(self, pcap_file: str) -> List[Dict[str, Any]]:
        """Extract connections from PCAP file."""
        connections = []
        
        try:
            # Use tcpdump to extract connection information
            cmd = ["tcpdump", "-r", pcap_file, "-n"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                
                for line in lines:
                    connection_info = self._parse_tcpdump_line(line)
                    if connection_info:
                        connections.append(connection_info)
                        
        except Exception as e:
            self.logger.error(f"PCAP connection extraction failed: {e}")
        
        return connections
    
    def _extract_dns_from_pcap(self, pcap_file: str) -> List[Dict[str, Any]]:
        """Extract DNS queries from PCAP file."""
        queries = []
        
        try:
            # Use tcpdump to extract DNS queries
            cmd = ["tcpdump", "-r", pcap_file, "-n", "port", "53"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                
                for line in lines:
                    dns_info = self._parse_dns_line(line)
                    if dns_info:
                        queries.append(dns_info)
                        
        except Exception as e:
            self.logger.error(f"PCAP DNS extraction failed: {e}")
        
        return queries
    
    def _find_suspicious_in_pcap(self, pcap_file: str) -> List[Dict[str, Any]]:
        """Find suspicious traffic in PCAP file."""
        suspicious = []
        
        try:
            # Check for suspicious patterns in PCAP
            suspicious_patterns = [
                "gulf.moneroocean.stream",
                "api.ipify.org",
                "stratum+tcp://"
            ]
            
            for pattern in suspicious_patterns:
                cmd = ["tcpdump", "-r", pcap_file, "-A", "|", "grep", pattern]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if process.returncode == 0 and process.stdout.strip():
                    suspicious.append({
                        "type": "suspicious_pattern",
                        "pattern": pattern,
                        "matches": len(process.stdout.strip().split('\n')),
                        "description": f"Found {pattern} in traffic"
                    })
                    
        except Exception as e:
            self.logger.error(f"Suspicious traffic detection failed: {e}")
        
        return suspicious
    
    def _detect_stratum_in_pcap(self, pcap_file: str) -> bool:
        """Detect Stratum protocol in PCAP file."""
        try:
            # Check for Stratum protocol indicators
            stratum_indicators = [
                "stratum+tcp://",
                "gulf.moneroocean.stream:10032"
            ]
            
            for indicator in stratum_indicators:
                cmd = ["tcpdump", "-r", pcap_file, "-A", "|", "grep", indicator]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if process.returncode == 0 and process.stdout.strip():
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Stratum detection in PCAP failed: {e}")
            return False
    
    def _extract_iocs_from_pcap(self, pcap_file: str) -> List[Dict[str, Any]]:
        """Extract IOCs from PCAP file."""
        iocs = []
        
        try:
            # Extract IP addresses and ports
            cmd = ["tcpdump", "-r", pcap_file, "-n"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                
                for line in lines:
                    ioc = self._extract_ioc_from_line(line)
                    if ioc:
                        iocs.append(ioc)
                        
        except Exception as e:
            self.logger.error(f"IOC extraction from PCAP failed: {e}")
        
        return iocs
    
    def _parse_netstat_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse netstat output line."""
        try:
            parts = line.split()
            if len(parts) >= 4:
                protocol = parts[0]
                local_address = parts[3]
                remote_address = parts[4] if len(parts) > 4 else ""
                state = parts[5] if len(parts) > 5 else ""
                
                # Parse addresses
                local_parts = local_address.split(':')
                remote_parts = remote_address.split(':')
                
                return {
                    "protocol": protocol,
                    "local_address": local_parts[0] if len(local_parts) > 0 else "",
                    "local_port": local_parts[1] if len(local_parts) > 1 else "",
                    "remote_address": remote_parts[0] if len(remote_parts) > 0 else "",
                    "remote_port": remote_parts[1] if len(remote_parts) > 1 else "",
                    "state": state
                }
        except Exception as e:
            self.logger.error(f"Netstat line parsing failed: {e}")
        
        return None
    
    def _is_suspicious_connection(self, remote_addr: str, remote_port: str) -> bool:
        """Check if connection is suspicious."""
        try:
            # Check for suspicious domains
            for domain in self.suspicious_domains:
                if domain in remote_addr:
                    return True
            
            # Check for suspicious ports
            for port in self.suspicious_ports:
                if str(port) == str(remote_port):
                    return True
            
            # Check for mining pools
            for pool in self.mining_pools:
                if pool in remote_addr:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Suspicious connection check failed: {e}")
            return False
    
    def _is_mining_pool_connection(self, remote_addr: str, remote_port: str) -> bool:
        """Check if connection is to a mining pool."""
        try:
            mining_pools = [
                "gulf.moneroocean.stream",
                "moneroocean.stream",
                "xmr.pool.gntl.co.uk",
                "pool.supportxmr.com"
            ]
            
            for pool in mining_pools:
                if pool in remote_addr:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Mining pool connection check failed: {e}")
            return False
    
    def _is_suspicious_domain(self, domain: str) -> bool:
        """Check if domain is suspicious."""
        try:
            suspicious_domains = [
                "api.ipify.org",
                "gulf.moneroocean.stream",
                "moneroocean.stream"
            ]
            
            for suspicious in suspicious_domains:
                if suspicious in domain:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Suspicious domain check failed: {e}")
            return False
    
    def _parse_tcpdump_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse tcpdump output line."""
        try:
            # Basic parsing of tcpdump output
            if "IP" in line and ">" in line:
                parts = line.split()
                if len(parts) >= 5:
                    return {
                        "timestamp": parts[0],
                        "source": parts[2],
                        "destination": parts[4].rstrip(':'),
                        "protocol": "IP"
                    }
        except Exception as e:
            self.logger.error(f"Tcpdump line parsing failed: {e}")
        
        return None
    
    def _parse_dns_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse DNS query line."""
        try:
            if "A?" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "A?" and i + 1 < len(parts):
                        domain = parts[i + 1].rstrip('.')
                        return {
                            "domain": domain,
                            "query_type": "A",
                            "timestamp": parts[0] if parts else ""
                        }
        except Exception as e:
            self.logger.error(f"DNS line parsing failed: {e}")
        
        return None
    
    def _extract_ioc_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract IOC from tcpdump line."""
        try:
            # Extract IP addresses
            import re
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ips = re.findall(ip_pattern, line)
            
            for ip in ips:
                if self._is_suspicious_ip(ip):
                    return {
                        "type": "ip_address",
                        "value": ip,
                        "description": f"Suspicious IP address: {ip}",
                        "severity": "medium"
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"IOC extraction failed: {e}")
            return None
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address is suspicious."""
        try:
            # This would typically check against threat intelligence feeds
            # For now, return False as placeholder
            return False
        except Exception as e:
            self.logger.error(f"Suspicious IP check failed: {e}")
            return False
    
    def _analyze_capture_file(self, capture_file: str) -> Dict[str, Any]:
        """Analyze capture file."""
        results = {}
        
        try:
            # Basic analysis of capture file
            results["file_size"] = os.path.getsize(capture_file)
            results["analysis_timestamp"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Capture file analysis failed: {e}")
        
        return results