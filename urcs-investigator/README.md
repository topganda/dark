# URCS Investigator Toolkit

A comprehensive defensive analysis and detection toolkit for investigating unauthorized resource-consuming software (URCS) using legitimate, open-source tools.

## 🎯 Purpose

This toolkit is designed for security researchers, incident responders, and investigators to detect, analyze, and document unauthorized resource-consuming software behaviors using legitimate, open-source tools and techniques.

## ⚠️ Legal and Ethical Notice

- **Authorized Use Only**: Only use this toolkit on systems you own or have explicit permission to analyze
- **Defensive Purpose**: This toolkit is designed for defensive analysis and threat intelligence
- **Legal Compliance**: Follow all applicable laws and regulations in your jurisdiction
- **Ethical Standards**: Maintain professional integrity and objectivity

## 🚀 Features

### Core Investigation Capabilities
- **Static File Analysis**: Entropy analysis, digital signature verification, YARA scanning
- **Behavioral Monitoring**: Registry analysis, service enumeration, scheduled task detection
- **Memory Forensics**: Process injection detection, memory region analysis
- **Network Analysis**: Traffic capture, protocol analysis, IOC extraction
- **Artifact Collection**: Comprehensive evidence gathering and documentation

### Detection Methods
- **Registry Monitoring**: Suspicious Run keys, service creation, persistence mechanisms
- **File System Analysis**: Suspicious file detection in system directories
- **Process Analysis**: Injection detection, anomalous process behavior
- **Network Monitoring**: DNS queries, Stratum protocol detection, connection analysis
- **Performance Monitoring**: CPU usage patterns, Task Manager detection

### Reporting and Documentation
- **Automated Reports**: Generate comprehensive investigation reports
- **IOC Extraction**: Extract and document indicators of compromise
- **MITRE ATT&CK Mapping**: Correlate findings with known attack techniques
- **Evidence Management**: Organize and preserve investigation artifacts

## 📁 Project Structure

```
urcs-investigator/
├── src/                    # Core investigation modules
│   ├── analysis/          # Analysis engines
│   ├── detection/         # Detection methods
│   ├── forensics/         # Forensic tools
│   └── reporting/         # Report generation
├── tools/                 # External tools and utilities
├── config/                # Configuration files
├── logs/                  # Investigation logs
├── reports/               # Generated reports
├── yara_rules/           # YARA detection rules
├── scripts/              # Investigation scripts
└── docs/                 # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (for Windows-specific analysis)
- Administrative privileges (for system monitoring)

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd urcs-investigator

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

## 📖 Usage

### Basic Investigation
```bash
# Run a comprehensive investigation
python main.py investigate --target <system>

# Run specific analysis modules
python main.py static --file <suspicious_file>
python main.py behavioral --system
python main.py memory --pid <process_id>
python main.py network --interface <interface>
```

### Advanced Analysis
```bash
# Custom investigation with specific focus
python main.py investigate --config custom_config.json

# Generate detailed report
python main.py report --output detailed_report.html

# Export IOCs
python main.py export-iocs --format json
```

## 🔍 Investigation Workflow

### Phase 1: Initial Detection
1. **Static Analysis**: File entropy, signatures, YARA scanning
2. **Behavioral Setup**: Enable monitoring, logging, tracing
3. **Artifact Collection**: Registry, services, tasks, files

### Phase 2: Deep Analysis
1. **Memory Forensics**: Process injection, memory regions
2. **Network Analysis**: Traffic capture, protocol analysis
3. **Performance Monitoring**: CPU patterns, system behavior

### Phase 3: Documentation
1. **Evidence Organization**: Collect and preserve artifacts
2. **Report Generation**: Create comprehensive reports
3. **IOC Extraction**: Document indicators of compromise

## 📊 Detection Capabilities

### Registry Analysis
- Suspicious Run keys (`ctfmon`, random names)
- Service creation (`gupdatem`, fake services)
- Scheduled task creation (`Ddriver`, periodic tasks)

### File System Analysis
- Suspicious files in system directories
- Random 8-letter filenames
- Files in `System32\spool\drivers\color\`

### Process Analysis
- Process injection into `explorer.exe`
- Memory hollowing detection
- Anomalous process behavior

### Network Analysis
- DNS queries to `api.ipify.org`
- Stratum protocol connections (port 10032)
- Monero pool communications

## 🛡️ Security Features

### Monitoring Capabilities
- **Sysmon Integration**: System activity monitoring
- **ETW Tracing**: Performance and process monitoring
- **PowerShell Logging**: Script execution monitoring
- **Network Capture**: Traffic analysis and monitoring

### Detection Rules
- **YARA Rules**: Pattern-based file detection
- **Behavioral Rules**: Anomaly-based detection
- **Network Rules**: Protocol and connection detection
- **Registry Rules**: Persistence mechanism detection

## 📈 Reporting

### Report Types
- **Executive Summary**: High-level findings and impact
- **Technical Analysis**: Detailed technical findings
- **IOC Report**: Indicators of compromise
- **Timeline Analysis**: Chronological event sequence
- **MITRE ATT&CK Mapping**: Technique correlation

### Export Formats
- **HTML**: Interactive web reports
- **PDF**: Printable documentation
- **JSON**: Machine-readable data
- **CSV**: Spreadsheet-compatible data

## 🔧 Configuration

### Main Configuration
```json
{
  "investigation": {
    "scope": "comprehensive",
    "modules": ["static", "behavioral", "memory", "network"],
    "output_format": "html"
  },
  "detection": {
    "yara_rules": "yara_rules/",
    "thresholds": {
      "entropy": 7.5,
      "cpu_drop": 70
    }
  },
  "monitoring": {
    "sysmon": true,
    "etw_tracing": true,
    "powershell_logging": true
  }
}
```

## 🚨 Incident Response

### Immediate Actions
1. **Isolate**: Disconnect affected systems
2. **Preserve**: Create memory dumps and disk images
3. **Document**: Record all findings and actions
4. **Analyze**: Use toolkit for comprehensive analysis

### Recovery Steps
1. **Remove Persistence**: Clean registry, services, tasks
2. **Restore Files**: Replace compromised files
3. **Update Security**: Implement detection improvements
4. **Monitor**: Continue monitoring for re-infection

## 📚 Documentation

### Guides
- [Quick Start Guide](docs/quickstart.md)
- [Investigation Manual](docs/manual.md)
- [Configuration Guide](docs/config.md)
- [Troubleshooting](docs/troubleshooting.md)

### References
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [YARA Documentation](https://yara.readthedocs.io/)
- [Volatility Documentation](https://volatility3.readthedocs.io/)

## 🤝 Contributing

### Guidelines
- Follow defensive analysis best practices
- Maintain ethical and legal compliance
- Document all changes and improvements
- Test thoroughly before submission

### Development
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

This toolkit is provided for educational and defensive purposes only. Users are responsible for ensuring compliance with applicable laws and regulations. The authors are not liable for any misuse or damage resulting from the use of this toolkit.

## 🆘 Support

### Issues
- Report bugs and issues on GitHub
- Provide detailed reproduction steps
- Include system information and logs

### Questions
- Check documentation and guides
- Search existing issues
- Create new issue for questions

### Security
- Report security vulnerabilities privately
- Follow responsible disclosure practices
- Contact maintainers directly for sensitive issues

---

**Remember**: This toolkit is designed for legitimate security research and incident response. Always obtain proper authorization before conducting investigations.