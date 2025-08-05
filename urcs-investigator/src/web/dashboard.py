"""Web Dashboard for URCS Investigator Toolkit
Provides a real-time web interface for monitoring and investigation.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import psutil

from ..utils.system_monitor import SystemMonitor
from ..utils.platform_utils import PlatformUtils
from ..core.config import ConfigManager

class URCSDashboard:
    """Web dashboard for URCS monitoring and investigation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.system_monitor = SystemMonitor(config)
        self.platform_utils = PlatformUtils()
        
        # Flask app setup
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'urcs-investigator-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dashboard state
        self.monitoring_active = False
        self.alerts = []
        self.metrics = {}
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/status')
        def get_status():
            """Get dashboard status."""
            return jsonify({
                "monitoring_active": self.monitoring_active,
                "system_info": self.platform_utils.get_system_info(),
                "alerts_count": len(self.alerts),
                "last_update": datetime.now().isoformat()
            })
        
        @self.app.route('/api/metrics')
        def get_metrics():
            """Get current metrics."""
            return jsonify(self._get_current_metrics())
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts."""
            return jsonify({
                "alerts": self.alerts[-50:],  # Last 50 alerts
                "total": len(self.alerts)
            })
        
        @self.app.route('/api/processes')
        def get_processes():
            """Get running processes."""
            processes = self.platform_utils.get_process_list()
            return jsonify({
                "processes": processes,
                "count": len(processes)
            })
        
        @self.app.route('/api/network')
        def get_network():
            """Get network connections."""
            connections = self.platform_utils.get_network_connections()
            return jsonify({
                "connections": connections,
                "count": len(connections)
            })
        
        @self.app.route('/api/services')
        def get_services():
            """Get system services."""
            services = self.platform_utils.get_services()
            return jsonify({
                "services": services,
                "count": len(services)
            })
        
        @self.app.route('/api/start_monitoring', methods=['POST'])
        def start_monitoring():
            """Start real-time monitoring."""
            try:
                if not self.monitoring_active:
                    self.monitoring_active = self.system_monitor.start_monitoring()
                    if self.monitoring_active:
                        # Start metrics collection thread
                        threading.Thread(target=self._collect_metrics, daemon=True).start()
                        return jsonify({"success": True, "message": "Monitoring started"})
                    else:
                        return jsonify({"success": False, "message": "Failed to start monitoring"})
                else:
                    return jsonify({"success": False, "message": "Monitoring already active"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/stop_monitoring', methods=['POST'])
        def stop_monitoring():
            """Stop real-time monitoring."""
            try:
                if self.monitoring_active:
                    self.system_monitor.stop_monitoring()
                    self.monitoring_active = False
                    return jsonify({"success": True, "message": "Monitoring stopped"})
                else:
                    return jsonify({"success": False, "message": "Monitoring not active"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/investigate', methods=['POST'])
        def run_investigation():
            """Run investigation."""
            try:
                data = request.get_json()
                target = data.get('target', 'localhost')
                scope = data.get('scope', 'basic')
                
                # Run investigation in background
                threading.Thread(
                    target=self._run_investigation_background,
                    args=(target, scope),
                    daemon=True
                ).start()
                
                return jsonify({
                    "success": True,
                    "message": f"Investigation started for {target}",
                    "investigation_id": f"inv_{int(time.time())}"
                })
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
    
    def _setup_socketio(self):
        """Setup SocketIO events."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.logger.info("Client connected to dashboard")
            emit('status', {
                "monitoring_active": self.monitoring_active,
                "alerts_count": len(self.alerts)
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.logger.info("Client disconnected from dashboard")
        
        @self.socketio.on('request_metrics')
        def handle_metrics_request():
            """Handle metrics request."""
            emit('metrics_update', self._get_current_metrics())
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "processes": len(psutil.pids()),
                "alerts_count": len(self.alerts)
            }
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    def _collect_metrics(self):
        """Collect metrics in background thread."""
        while self.monitoring_active:
            try:
                metrics = self._get_current_metrics()
                self.metrics = metrics
                
                # Emit metrics to connected clients
                self.socketio.emit('metrics_update', metrics)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                time.sleep(10)
    
    def _run_investigation_background(self, target: str, scope: str):
        """Run investigation in background thread."""
        try:
            from ..core.investigator import URCSInvestigator
            
            investigator = URCSInvestigator(self.config)
            results = investigator.investigate(target=target, scope=scope)
            
            # Emit investigation results
            self.socketio.emit('investigation_complete', {
                "target": target,
                "scope": scope,
                "findings_count": len(results.get('findings', [])),
                "iocs_count": len(results.get('iocs', [])),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Investigation failed: {e}")
            self.socketio.emit('investigation_error', {
                "target": target,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def add_alert(self, alert_data: Dict[str, Any]):
        """Add new alert."""
        alert_data["timestamp"] = datetime.now().isoformat()
        alert_data["id"] = f"alert_{int(time.time())}"
        
        self.alerts.append(alert_data)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Emit alert to connected clients
        self.socketio.emit('new_alert', alert_data)
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the dashboard."""
        self.logger.info(f"Starting URCS Dashboard on {host}:{port}")
        
        # Create templates directory if it doesn't exist
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Create dashboard template
        self._create_dashboard_template()
        
        # Start the Flask app
        self.socketio.run(self.app, host=host, port=port, debug=debug)
    
    def _create_dashboard_template(self):
        """Create the dashboard HTML template."""
        template_path = Path(__file__).parent / "templates" / "dashboard.html"
        
        if not template_path.exists():
            template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URCS Investigator Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn.danger {
            background: #e74c3c;
        }
        .btn.danger:hover {
            background: #c0392b;
        }
        .alerts-container {
            max-height: 400px;
            overflow-y: auto;
        }
        .alert {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .alert.high {
            background: #f8d7da;
            border-color: #f5c6cb;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 URCS Investigator Dashboard</h1>
            <p>Real-time monitoring and investigation for unauthorized resource-consuming software</p>
        </div>
        
        <div class="status-bar">
            <div>
                <span id="status-indicator">●</span>
                <span id="status-text">Monitoring: Inactive</span>
            </div>
            <div>
                <button class="btn" id="startBtn" onclick="startMonitoring()">Start Monitoring</button>
                <button class="btn danger" id="stopBtn" onclick="stopMonitoring()" disabled>Stop Monitoring</button>
                <button class="btn" onclick="runInvestigation()">Run Investigation</button>
            </div>
        </div>
        
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value" id="cpuPercent">0%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" id="memoryPercent">0%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" id="diskPercent">0%</div>
                <div class="metric-label">Disk Usage</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" id="processCount">0</div>
                <div class="metric-label">Processes</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" id="alertsCount">0</div>
                <div class="metric-label">Alerts</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" id="networkSent">0 MB</div>
                <div class="metric-label">Network Sent</div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>System Performance</h3>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>Recent Alerts</h3>
            <div class="alerts-container" id="alertsContainer">
                <p>No alerts yet...</p>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let performanceChart;
        let chartData = {
            labels: [],
            cpu: [],
            memory: [],
            disk: []
        };
        
        // Initialize chart
        const ctx = document.getElementById('performanceChart').getContext('2d');
        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Memory %',
                    data: [],
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Disk %',
                    data: [],
                    borderColor: '#f093fb',
                    backgroundColor: 'rgba(240, 147, 251, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Socket.IO event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
        });
        
        socket.on('status', function(data) {
            updateStatus(data);
        });
        
        socket.on('metrics_update', function(data) {
            updateMetrics(data);
        });
        
        socket.on('new_alert', function(alert) {
            addAlert(alert);
        });
        
        socket.on('investigation_complete', function(result) {
            addAlert({
                type: 'investigation_complete',
                severity: 'info',
                description: `Investigation completed for ${result.target}. Found ${result.findings_count} findings and ${result.iocs_count} IOCs.`
            });
        });
        
        function updateStatus(data) {
            const indicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            
            if (data.monitoring_active) {
                indicator.style.color = '#27ae60';
                statusText.textContent = 'Monitoring: Active';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                indicator.style.color = '#e74c3c';
                statusText.textContent = 'Monitoring: Inactive';
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }
        
        function updateMetrics(data) {
            // Update metric cards
            document.getElementById('cpuPercent').textContent = data.cpu.percent.toFixed(1) + '%';
            document.getElementById('memoryPercent').textContent = data.memory.percent.toFixed(1) + '%';
            document.getElementById('diskPercent').textContent = data.disk.percent.toFixed(1) + '%';
            document.getElementById('processCount').textContent = data.processes;
            document.getElementById('alertsCount').textContent = data.alerts_count;
            document.getElementById('networkSent').textContent = (data.network.bytes_sent / 1024 / 1024).toFixed(1) + ' MB';
            
            // Update chart
            const time = new Date().toLocaleTimeString();
            chartData.labels.push(time);
            chartData.cpu.push(data.cpu.percent);
            chartData.memory.push(data.memory.percent);
            chartData.disk.push(data.disk.percent);
            
            // Keep only last 20 data points
            if (chartData.labels.length > 20) {
                chartData.labels.shift();
                chartData.cpu.shift();
                chartData.memory.shift();
                chartData.disk.shift();
            }
            
            performanceChart.data.labels = chartData.labels;
            performanceChart.data.datasets[0].data = chartData.cpu;
            performanceChart.data.datasets[1].data = chartData.memory;
            performanceChart.data.datasets[2].data = chartData.disk;
            performanceChart.update();
        }
        
        function addAlert(alert) {
            const container = document.getElementById('alertsContainer');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${alert.severity}`;
            alertDiv.innerHTML = `
                <strong>${alert.type}</strong><br>
                ${alert.description}<br>
                <small>${new Date(alert.timestamp).toLocaleString()}</small>
            `;
            
            container.insertBefore(alertDiv, container.firstChild);
            
            // Keep only last 50 alerts
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }
        
        function startMonitoring() {
            fetch('/api/start_monitoring', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Monitoring started');
                } else {
                    alert('Failed to start monitoring: ' + data.message);
                }
            });
        }
        
        function stopMonitoring() {
            fetch('/api/stop_monitoring', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Monitoring stopped');
                } else {
                    alert('Failed to stop monitoring: ' + data.message);
                }
            });
        }
        
        function runInvestigation() {
            const target = prompt('Enter target (default: localhost):', 'localhost');
            if (target) {
                fetch('/api/investigate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        target: target,
                        scope: 'basic'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Investigation started');
                    } else {
                        alert('Failed to start investigation: ' + data.message);
                    }
                });
            }
        }
        
        // Load initial status
        fetch('/api/status')
            .then(response => response.json())
            .then(data => updateStatus(data));
    </script>
</body>
</html>"""
            
            with open(template_path, 'w') as f:
                f.write(template_content)