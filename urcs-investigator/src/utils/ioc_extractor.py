"""
IOC (Indicators of Compromise) Extractor for URCS Investigator Toolkit.
"""

import json
import csv
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional


class IOCExtractor:
    """Extracts and manages indicators of compromise from investigation results."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # IOC categories
        self.ioc_categories = {
            "file": ["hash", "filename", "path"],
            "network": ["ip", "domain", "url", "port"],
            "registry": ["key", "value"],
            "process": ["pid", "name", "command_line"],
            "service": ["name", "display_name", "binary_path"],
            "scheduled_task": ["name", "command", "trigger"]
        }
    
    def extract_iocs(self, modules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract IOCs from investigation modules.
        
        Args:
            modules: Dictionary containing analysis module results
            
        Returns:
            List of IOC dictionaries
        """
        iocs = []
        
        try:
            # Extract from static analysis
            if "static" in modules:
                iocs.extend(self._extract_static_iocs(modules["static"]))
            
            # Extract from behavioral analysis
            if "behavioral" in modules:
                iocs.extend(self._extract_behavioral_iocs(modules["behavioral"]))
            
            # Extract from memory analysis
            if "memory" in modules:
                iocs.extend(self._extract_memory_iocs(modules["memory"]))
            
            # Extract from network analysis
            if "network" in modules:
                iocs.extend(self._extract_network_iocs(modules["network"]))
            
            # Deduplicate IOCs
            iocs = self._deduplicate_iocs(iocs)
            
            # Add metadata
            for ioc in iocs:
                ioc["extracted_at"] = datetime.now().isoformat()
                ioc["confidence"] = ioc.get("confidence", "medium")
            
            self.logger.info(f"Extracted {len(iocs)} IOCs from investigation results")
            
        except Exception as e:
            self.logger.error(f"Failed to extract IOCs: {e}")
        
        return iocs
    
    def export_iocs(self, iocs: List[Dict[str, Any]], format: str = "json", 
                   output_path: Optional[str] = None) -> str:
        """
        Export IOCs to various formats.
        
        Args:
            iocs: List of IOC dictionaries
            format: Export format (json, csv, stix)
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/iocs_{timestamp}.{format}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            if format == "json":
                return self._export_json(iocs, output_path)
            elif format == "csv":
                return self._export_csv(iocs, output_path)
            elif format == "stix":
                return self._export_stix(iocs, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Failed to export IOCs: {e}")
            return ""
    
    def _extract_static_iocs(self, static_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract IOCs from static analysis results."""
        iocs = []
        
        try:
            # File-based IOCs
            if "file_path" in static_results:
                file_path = static_results["file_path"]
                
                # File hash
                if "hash" in static_results:
                    iocs.append({
                        "type": "file_hash",
                        "value": static_results["hash"],
                        "category": "file",
                        "confidence": "high",
                        "source": "static_analysis",
                        "metadata": {"file_path": file_path}
                    })
                
                # File path
                iocs.append({
                    "type": "file_path",
                    "value": file_path,
                    "category": "file",
                    "confidence": "medium",
                    "source": "static_analysis"
                })
                
                # YARA matches
                for match in static_results.get("yara_matches", []):
                    iocs.append({
                        "type": "yara_match",
                        "value": match.get("rule", "unknown"),
                        "category": "file",
                        "confidence": "high",
                        "source": "static_analysis",
                        "metadata": {"match": match}
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to extract static IOCs: {e}")
        
        return iocs
    
    def _extract_behavioral_iocs(self, behavioral_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract IOCs from behavioral analysis results."""
        iocs = []
        
        try:
            # Registry IOCs
            for finding in behavioral_results.get("registry_findings", []):
                if "key" in finding:
                    iocs.append({
                        "type": "registry_key",
                        "value": finding["key"],
                        "category": "registry",
                        "confidence": "medium",
                        "source": "behavioral_analysis",
                        "metadata": finding
                    })
                
                if "value" in finding:
                    iocs.append({
                        "type": "registry_value",
                        "value": finding["value"],
                        "category": "registry",
                        "confidence": "medium",
                        "source": "behavioral_analysis",
                        "metadata": finding
                    })
            
            # Service IOCs
            for finding in behavioral_results.get("service_findings", []):
                if "name" in finding:
                    iocs.append({
                        "type": "service_name",
                        "value": finding["name"],
                        "category": "service",
                        "confidence": "medium",
                        "source": "behavioral_analysis",
                        "metadata": finding
                    })
                
                if "binary_path" in finding:
                    iocs.append({
                        "type": "service_binary",
                        "value": finding["binary_path"],
                        "category": "service",
                        "confidence": "high",
                        "source": "behavioral_analysis",
                        "metadata": finding
                    })
            
            # Scheduled task IOCs
            for finding in behavioral_results.get("task_findings", []):
                if "name" in finding:
                    iocs.append({
                        "type": "scheduled_task",
                        "value": finding["name"],
                        "category": "scheduled_task",
                        "confidence": "medium",
                        "source": "behavioral_analysis",
                        "metadata": finding
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to extract behavioral IOCs: {e}")
        
        return iocs
    
    def _extract_memory_iocs(self, memory_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract IOCs from memory analysis results."""
        iocs = []
        
        try:
            # Process injection IOCs
            for finding in memory_results.get("injection_findings", []):
                if "process_name" in finding:
                    iocs.append({
                        "type": "injected_process",
                        "value": finding["process_name"],
                        "category": "process",
                        "confidence": "high",
                        "source": "memory_analysis",
                        "metadata": finding
                    })
                
                if "injected_address" in finding:
                    iocs.append({
                        "type": "injection_address",
                        "value": finding["injected_address"],
                        "category": "process",
                        "confidence": "medium",
                        "source": "memory_analysis",
                        "metadata": finding
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to extract memory IOCs: {e}")
        
        return iocs
    
    def _extract_network_iocs(self, network_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract IOCs from network analysis results."""
        iocs = []
        
        try:
            # Connection IOCs
            for connection in network_results.get("connections", []):
                if "remote_ip" in connection:
                    iocs.append({
                        "type": "ip_address",
                        "value": connection["remote_ip"],
                        "category": "network",
                        "confidence": "medium",
                        "source": "network_analysis",
                        "metadata": connection
                    })
                
                if "remote_port" in connection:
                    iocs.append({
                        "type": "port",
                        "value": str(connection["remote_port"]),
                        "category": "network",
                        "confidence": "low",
                        "source": "network_analysis",
                        "metadata": connection
                    })
            
            # DNS query IOCs
            for query in network_results.get("dns_queries", []):
                if "domain" in query:
                    iocs.append({
                        "type": "domain",
                        "value": query["domain"],
                        "category": "network",
                        "confidence": "medium",
                        "source": "network_analysis",
                        "metadata": query
                    })
            
            # Suspicious traffic IOCs
            for traffic in network_results.get("suspicious_traffic", []):
                if "protocol" in traffic:
                    iocs.append({
                        "type": "protocol",
                        "value": traffic["protocol"],
                        "category": "network",
                        "confidence": "medium",
                        "source": "network_analysis",
                        "metadata": traffic
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to extract network IOCs: {e}")
        
        return iocs
    
    def _deduplicate_iocs(self, iocs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate IOCs based on type and value."""
        seen = set()
        unique_iocs = []
        
        for ioc in iocs:
            key = (ioc.get("type"), ioc.get("value"))
            if key not in seen:
                seen.add(key)
                unique_iocs.append(ioc)
        
        return unique_iocs
    
    def _export_json(self, iocs: List[Dict[str, Any]], output_path: str) -> str:
        """Export IOCs to JSON format."""
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_iocs": len(iocs),
                "categories": list(set(ioc.get("category", "unknown") for ioc in iocs))
            },
            "iocs": iocs
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(iocs)} IOCs to JSON: {output_path}")
        return output_path
    
    def _export_csv(self, iocs: List[Dict[str, Any]], output_path: str) -> str:
        """Export IOCs to CSV format."""
        if not iocs:
            return ""
        
        # Get all possible fields
        fields = set()
        for ioc in iocs:
            fields.update(ioc.keys())
        
        fields = sorted(list(fields))
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(iocs)
        
        self.logger.info(f"Exported {len(iocs)} IOCs to CSV: {output_path}")
        return output_path
    
    def _export_stix(self, iocs: List[Dict[str, Any]], output_path: str) -> str:
        """Export IOCs to STIX format."""
        # This is a simplified STIX export
        # In a real implementation, you would use a proper STIX library
        
        stix_data = {
            "type": "bundle",
            "id": f"bundle--{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "objects": []
        }
        
        for ioc in iocs:
            stix_object = {
                "type": "indicator",
                "id": f"indicator--{hash(ioc.get('value', '')) % 1000000}",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "pattern": self._create_stix_pattern(ioc),
                "pattern_type": "stix",
                "pattern_version": "2.1",
                "valid_from": datetime.now().isoformat(),
                "labels": [ioc.get("category", "unknown"), ioc.get("confidence", "medium")]
            }
            stix_data["objects"].append(stix_object)
        
        with open(output_path, 'w') as f:
            json.dump(stix_data, f, indent=2)
        
        self.logger.info(f"Exported {len(iocs)} IOCs to STIX: {output_path}")
        return output_path
    
    def _create_stix_pattern(self, ioc: Dict[str, Any]) -> str:
        """Create STIX pattern for an IOC."""
        ioc_type = ioc.get("type", "")
        value = ioc.get("value", "")
        
        if ioc_type == "ip_address":
            return f"[ipv4-addr:value = '{value}']"
        elif ioc_type == "domain":
            return f"[domain-name:value = '{value}']"
        elif ioc_type == "file_hash":
            return f"[file:hashes.'SHA-256' = '{value}']"
        elif ioc_type == "url":
            return f"[url:value = '{value}']"
        else:
            return f"[artifact:payload_bin = '{value}']"