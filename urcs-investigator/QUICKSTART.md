# Quick Start Guide - URCS Investigator Toolkit

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for Windows-specific analysis)
- Administrative privileges (recommended)
- Stable internet connection

### Step 1: Installation

```bash
# Clone or download the project
git clone <repository-url>
cd urcs-investigator

# Run the setup script
python setup.py
```

### Step 2: Basic Investigation

```bash
# Run a comprehensive investigation on localhost
python main.py investigate --target localhost

# Run basic investigation only
python main.py investigate --target localhost --scope basic

# Run full investigation with custom output
python main.py investigate --target localhost --scope full --output custom_reports/
```

### Step 3: Specific Analysis

```bash
# Static analysis of a suspicious file
python main.py static --file suspicious.exe --entropy --signature --yara

# Behavioral analysis of the system
python main.py behavioral --system --registry --services --tasks

# Memory forensics on a specific process
python main.py memory --pid 1234 --injection

# Network analysis
python main.py network --interface eth0 --live
```

### Step 4: Generate Reports

```bash
# Generate HTML report
python main.py report --output investigation_report.html --format html

# Export IOCs in JSON format
python main.py export-iocs --format json --output iocs.json
```

## 🔍 Investigation Workflow

### Phase 1: Initial Detection
1. **Run basic investigation**: `python main.py investigate --target <system> --scope basic`
2. **Review findings**: Check the generated report for suspicious indicators
3. **Identify scope**: Determine if full investigation is needed

### Phase 2: Deep Analysis
1. **Static analysis**: Analyze suspicious files for entropy, signatures, and YARA matches
2. **Behavioral analysis**: Check registry, services, and scheduled tasks
3. **Memory forensics**: Detect process injection and analyze memory regions
4. **Network analysis**: Monitor network traffic and connections

### Phase 3: Documentation
1. **Generate comprehensive report**: `python main.py report --output final_report.html`
2. **Export IOCs**: `python main.py export-iocs --format json`
3. **Archive evidence**: Store all investigation artifacts securely

## 📊 Key Features

### Detection Capabilities
- **Registry Analysis**: Suspicious Run keys, service creation, persistence mechanisms
- **File System Analysis**: Suspicious files in system directories, random filenames
- **Process Analysis**: Process injection detection, memory hollowing
- **Network Analysis**: DNS queries, Stratum protocol connections, suspicious traffic

### Analysis Modules
- **Static Analysis**: File entropy, digital signatures, YARA scanning, PE analysis
- **Behavioral Analysis**: Registry monitoring, service enumeration, task analysis
- **Memory Forensics**: Process injection detection, memory region analysis
- **Network Analysis**: Traffic capture, protocol analysis, IOC extraction

### Reporting Features
- **Multiple Formats**: HTML, PDF, JSON, CSV
- **IOC Extraction**: Automatic extraction and export of indicators
- **Timeline Analysis**: Chronological event sequence
- **MITRE ATT&CK Mapping**: Technique correlation

## 🛠️ Configuration

### Main Configuration File
Location: `config/investigation_config.json`

Key settings:
```json
{
  "investigation": {
    "scope": "comprehensive",
    "modules": ["static", "behavioral", "memory", "network"],
    "output_format": "html"
  },
  "detection": {
    "thresholds": {
      "entropy": 7.5,
      "cpu_drop": 70
    }
  }
}
```

### YARA Rules
Location: `yara_rules/`

Add custom detection rules:
```yara
rule custom_detection {
    meta:
        description = "Custom detection rule"
        author = "Your Name"
    
    strings:
        $suspicious_string = "suspicious_pattern"
    
    condition:
        $suspicious_string
}
```

## 📋 Common Commands

### Investigation Commands
```bash
# Comprehensive investigation
python main.py investigate --target localhost

# Basic investigation
python main.py investigate --target localhost --scope basic

# Custom investigation
python main.py investigate --config custom_config.json
```

### Analysis Commands
```bash
# Static file analysis
python main.py static --file file.exe --entropy --signature --yara

# Behavioral analysis
python main.py behavioral --system --registry --services --tasks

# Memory forensics
python main.py memory --pid 1234 --injection

# Network analysis
python main.py network --interface eth0 --live
```

### Reporting Commands
```bash
# Generate report
python main.py report --output report.html --format html

# Export IOCs
python main.py export-iocs --format json --output iocs.json

# Setup environment
python main.py setup --sysmon --etw --powershell
```

## 🔧 Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Run with administrative privileges
# Windows: Right-click Command Prompt -> Run as Administrator
# Linux/Mac: Use sudo
```

**Missing Dependencies**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or run setup again
python setup.py
```

**Configuration Issues**
```bash
# Check configuration file
cat config/investigation_config.json

# Recreate default configuration
python -c "from src.core.config import ConfigManager; ConfigManager().create_default_config()"
```

### Log Files
- **Main log**: `logs/investigation.log`
- **Error log**: `logs/error.log`
- **Investigation results**: `reports/<investigation_id>/investigation_results.json`

## 🚨 Security Notes

### Authorization
- Always obtain proper authorization before investigations
- Only analyze systems you own or have permission to examine
- Follow your organization's security policies

### Evidence Handling
- Preserve all investigation artifacts
- Store results securely and confidentially
- Document all actions taken during investigation

### Legal Compliance
- Ensure compliance with applicable laws and regulations
- Follow responsible disclosure practices
- Maintain professional integrity and objectivity

## 📚 Additional Resources

### Documentation
- [Full Documentation](docs/)
- [Configuration Guide](docs/config.md)
- [Investigation Manual](docs/manual.md)
- [Troubleshooting](docs/troubleshooting.md)

### References
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [YARA Documentation](https://yara.readthedocs.io/)
- [Volatility Documentation](https://volatility3.readthedocs.io/)

### Support
- Check logs for detailed error messages
- Review configuration settings
- Consult documentation and guides
- Report issues on GitHub

---

**Remember**: This toolkit is designed for legitimate security research and incident response. Always obtain proper authorization before conducting investigations.