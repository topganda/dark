"""
Web Dashboard
Provides a web-based interface for monitoring and controlling the Advanced Crypto Mining Suite.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from flask import Flask, render_template, jsonify, request, redirect, url_for
    from flask_socketio import SocketIO, emit
except ImportError:
    print("Flask and Flask-SocketIO are required for the dashboard.")
    print("Install with: pip install flask flask-socketio")
    Flask = None
    SocketIO = None

class Dashboard:
    """
    Web dashboard for monitoring and controlling the mining suite.
    Provides real-time statistics, configuration management, and system monitoring.
    """
    
    def __init__(self, config: Dict[str, Any], port: int = 8080):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.port = port
        
        # Initialize Flask app
        if Flask is None:
            raise ImportError("Flask is required for the dashboard")
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'advanced-miner-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dashboard state
        self.running = False
        self.update_thread = None
        self.stop_event = threading.Event()
        
        # Register routes
        self._register_routes()
        
        self.logger.info("Dashboard initialized")
    
    def start(self):
        """Start the dashboard server"""
        if self.running:
            self.logger.warning("Dashboard is already running")
            return
        
        self.logger.info(f"🌐 Starting dashboard on port {self.port}...")
        self.running = True
        self.stop_event.clear()
        
        # Start update thread
        self.update_thread = threading.Thread(
            target=self._update_loop,
            daemon=True
        )
        self.update_thread.start()
        
        # Start Flask server
        try:
            self.socketio.run(
                self.app,
                host='0.0.0.0',
                port=self.port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            self.running = False
    
    def stop(self):
        """Stop the dashboard server"""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping dashboard...")
        self.running = False
        self.stop_event.set()
        
        if self.update_thread:
            self.update_thread.join(timeout=5)
        
        self.logger.info("✅ Dashboard stopped")
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return self._render_dashboard()
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get current mining statistics"""
            return jsonify(self._get_current_stats())
        
        @self.app.route('/api/config')
        def get_config():
            """Get current configuration"""
            return jsonify(self.config)
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update configuration"""
            try:
                new_config = request.json
                # Update configuration logic here
                return jsonify({'success': True, 'message': 'Configuration updated'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        
        @self.app.route('/api/control/start', methods=['POST'])
        def start_mining():
            """Start mining"""
            try:
                # Start mining logic here
                return jsonify({'success': True, 'message': 'Mining started'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        
        @self.app.route('/api/control/stop', methods=['POST'])
        def stop_mining():
            """Stop mining"""
            try:
                # Stop mining logic here
                return jsonify({'success': True, 'message': 'Mining stopped'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        
        @self.app.route('/api/logs')
        def get_logs():
            """Get recent logs"""
            try:
                lines = request.args.get('lines', 100, type=int)
                log_file = Path("logs/miner.log")
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        lines_list = f.readlines()
                        return jsonify({'logs': ''.join(lines_list[-lines:])})
                else:
                    return jsonify({'logs': 'No log file found'})
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.logger.info("Client connected to dashboard")
            emit('status', {'message': 'Connected to Advanced Crypto Mining Suite'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.logger.info("Client disconnected from dashboard")
        
        @self.socketio.on('request_stats')
        def handle_stats_request():
            """Handle stats request from client"""
            stats = self._get_current_stats()
            emit('stats_update', stats)
    
    def _render_dashboard(self) -> str:
        """Render the main dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Crypto Mining Suite - Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .header p {
            text-align: center;
            color: #7f8c8d;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .control-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .control-panel h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2980b9;
        }
        
        .btn-success {
            background: #27ae60;
            color: white;
        }
        
        .btn-success:hover {
            background: #229954;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .btn-warning {
            background: #f39c12;
            color: white;
        }
        
        .btn-warning:hover {
            background: #e67e22;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .chart-container h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .logs-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logs-container h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .logs {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #27ae60;
        }
        
        .status-offline {
            background: #e74c3c;
        }
        
        .status-warning {
            background: #f39c12;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced Crypto Mining Suite</h1>
            <p>Intelligent Resource Management & Real-time Monitoring</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Mining Status</h3>
                <div class="stat-value" id="mining-status">
                    <span class="status-indicator status-offline"></span>Offline
                </div>
                <div class="stat-label">Current mining status</div>
            </div>
            
            <div class="stat-card">
                <h3>Hashrate</h3>
                <div class="stat-value" id="hashrate">0 H/s</div>
                <div class="stat-label">Current mining speed</div>
            </div>
            
            <div class="stat-card">
                <h3>CPU Usage</h3>
                <div class="stat-value" id="cpu-usage">0%</div>
                <div class="stat-label">Current CPU utilization</div>
            </div>
            
            <div class="stat-card">
                <h3>GPU Usage</h3>
                <div class="stat-value" id="gpu-usage">0%</div>
                <div class="stat-label">Current GPU utilization</div>
            </div>
            
            <div class="stat-card">
                <h3>Temperature</h3>
                <div class="stat-value" id="temperature">0°C</div>
                <div class="stat-label">System temperature</div>
            </div>
            
            <div class="stat-card">
                <h3>Earnings</h3>
                <div class="stat-value" id="earnings">$0.0000</div>
                <div class="stat-label">Total earnings</div>
            </div>
        </div>
        
        <div class="control-panel">
            <h3>Control Panel</h3>
            <div class="button-group">
                <button class="btn btn-success" onclick="startMining()">Start Mining</button>
                <button class="btn btn-danger" onclick="stopMining()">Stop Mining</button>
                <button class="btn btn-warning" onclick="restartMining()">Restart</button>
                <button class="btn btn-primary" onclick="refreshStats()">Refresh Stats</button>
                <button class="btn btn-primary" onclick="showLogs()">Show Logs</button>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Performance Chart</h3>
            <canvas id="performanceChart" width="400" height="200"></canvas>
        </div>
        
        <div class="logs-container">
            <h3>Recent Logs</h3>
            <div class="logs" id="logs">Loading logs...</div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // Chart configuration
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Hashrate (H/s)',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4
                }, {
                    label: 'CPU Usage (%)',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            updateStatus('online');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from dashboard');
            updateStatus('offline');
        });
        
        socket.on('stats_update', function(data) {
            updateStats(data);
        });
        
        // Update functions
        function updateStats(data) {
            document.getElementById('hashrate').textContent = formatHashrate(data.hashrate);
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('gpu-usage').textContent = data.gpu_usage.toFixed(1) + '%';
            document.getElementById('temperature').textContent = data.temperature.toFixed(1) + '°C';
            document.getElementById('earnings').textContent = '$' + data.earnings.toFixed(4);
            
            // Update chart
            const now = new Date().toLocaleTimeString();
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(data.hashrate);
            performanceChart.data.datasets[1].data.push(data.cpu_usage);
            
            // Keep only last 20 data points
            if (performanceChart.data.labels.length > 20) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
                performanceChart.data.datasets[1].data.shift();
            }
            
            performanceChart.update('none');
        }
        
        function updateStatus(status) {
            const statusElement = document.getElementById('mining-status');
            const indicator = statusElement.querySelector('.status-indicator');
            
            indicator.className = 'status-indicator status-' + status;
            
            if (status === 'online') {
                statusElement.innerHTML = '<span class="status-indicator status-online"></span>Online';
            } else if (status === 'offline') {
                statusElement.innerHTML = '<span class="status-indicator status-offline"></span>Offline';
            } else {
                statusElement.innerHTML = '<span class="status-indicator status-warning"></span>Warning';
            }
        }
        
        function formatHashrate(hashrate) {
            if (hashrate >= 1e9) {
                return (hashrate / 1e9).toFixed(2) + ' GH/s';
            } else if (hashrate >= 1e6) {
                return (hashrate / 1e6).toFixed(2) + ' MH/s';
            } else if (hashrate >= 1e3) {
                return (hashrate / 1e3).toFixed(2) + ' KH/s';
            } else {
                return hashrate.toFixed(2) + ' H/s';
            }
        }
        
        // Control functions
        function startMining() {
            fetch('/api/control/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Mining started');
                        updateStatus('online');
                    } else {
                        console.error('Failed to start mining:', data.error);
                    }
                });
        }
        
        function stopMining() {
            fetch('/api/control/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Mining stopped');
                        updateStatus('offline');
                    } else {
                        console.error('Failed to stop mining:', data.error);
                    }
                });
        }
        
        function restartMining() {
            stopMining();
            setTimeout(startMining, 2000);
        }
        
        function refreshStats() {
            socket.emit('request_stats');
        }
        
        function showLogs() {
            fetch('/api/logs?lines=50')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('logs').textContent = data.logs;
                });
        }
        
        // Auto-refresh
        setInterval(refreshStats, 5000);
        setInterval(showLogs, 10000);
        
        // Initial load
        refreshStats();
        showLogs();
    </script>
</body>
</html>
        """
    
    def _get_current_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        # This would integrate with the actual miner
        # For now, return mock data
        return {
            'running': True,
            'hashrate': 1500.5,
            'cpu_usage': 65.2,
            'gpu_usage': 45.8,
            'temperature': 72.5,
            'power_consumption': 180.3,
            'earnings': 0.0025,
            'uptime': 3600,
            'shares_accepted': 15,
            'shares_rejected': 2,
            'resource_mode': 'balanced',
            'profitability': {
                'daily_earnings': 0.06,
                'monthly_earnings': 1.8,
                'yearly_earnings': 21.9,
                'electricity_cost': 0.52,
                'net_profit': 0.04,
                'roi_percentage': 15.2
            }
        }
    
    def _update_loop(self):
        """Update loop for real-time data"""
        while self.running and not self.stop_event.is_set():
            try:
                # Get current stats
                stats = self._get_current_stats()
                
                # Emit to connected clients
                self.socketio.emit('stats_update', stats)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(10)
    
    def get_dashboard_info(self) -> Dict[str, Any]:
        """Get dashboard information"""
        return {
            'running': self.running,
            'port': self.port,
            'url': f'http://localhost:{self.port}',
            'connected_clients': len(self.socketio.server.manager.rooms.get('/', {}))
        }