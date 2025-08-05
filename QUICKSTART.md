# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- Windows 10/11, Linux, or macOS
- 4GB+ RAM
- Stable internet connection

### Step 1: Installation

```bash
# Clone or download the project
git clone https://github.com/yourusername/advanced-crypto-miner.git
cd advanced-crypto-miner

# Run the setup script
python setup.py
```

### Step 2: Configuration

```bash
# Run the interactive setup wizard
python main.py setup
```

The wizard will guide you through:
- **Mining Configuration**: Algorithm, pool, wallet address
- **Resource Management**: CPU usage, battery settings
- **Profitability**: Electricity costs, power consumption
- **Monitoring**: Dashboard settings, logging
- **Security**: API tokens, access control

### Step 3: Start Mining

```bash
# Start mining in foreground
python main.py run

# Or start as a service
python main.py start

# Access the web dashboard
python main.py dashboard
```

## 📊 Key Features

### 🧠 Intelligent Resource Management
- **Adaptive CPU Usage**: 90% when charging/idle, 60-70% when active
- **Task Manager Detection**: Automatically reduces usage when detected
- **Battery Awareness**: Optimizes for battery life
- **Idle Detection**: Maximizes mining when device is unused

### 📈 Real-time Monitoring
- **Web Dashboard**: Beautiful, responsive interface at `http://localhost:8080`
- **Performance Charts**: Live hashrate and CPU usage graphs
- **Profitability Tracking**: Real-time earnings calculations
- **System Health**: Temperature, memory, and disk monitoring

### 🔧 Professional Features
- **Service Mode**: Runs as Windows service or system daemon
- **Auto-restart**: Automatic recovery from crashes
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Configuration Management**: Easy setup and customization

## 💰 Supported Cryptocurrencies

### CPU Mining
- **Monero (XMR)**: RandomX algorithm
- **Ravencoin (RVN)**: KawPow algorithm
- **Verus Coin (VRSC)**: VerusHash 2.2

### GPU Mining
- **Ethereum (ETH)**: Ethash algorithm
- **Ravencoin (RVN)**: KawPow algorithm
- **Ergo (ERG)**: Autolykos v2

## 🎯 Resource Management Modes

| Mode | CPU Usage | When Activated |
|------|-----------|----------------|
| **Stealth** | 5% | Task Manager detected |
| **Conservative** | 25% | Low battery, high system load |
| **Balanced** | 60% | Normal operation |
| **Aggressive** | 90% | Charging + idle, optimal conditions |

## 📱 Dashboard Features

- **Real-time Statistics**: Hashrate, CPU/GPU usage, temperature
- **Control Panel**: Start/stop/restart mining operations
- **Performance Charts**: Live graphs of mining performance
- **Log Viewer**: Real-time log monitoring
- **Configuration Editor**: Web-based config management

## 🔧 Common Commands

```bash
# Start mining
python main.py run

# Start as service
python main.py start

# Stop service
python main.py stop

# Show status
python main.py status

# Open dashboard
python main.py dashboard

# Run setup wizard
python main.py setup

# View logs
python main.py logs

# Show configuration
python main.py config
```

## ⚙️ Configuration Examples

### Basic Monero Mining
```json
{
  "mining": {
    "algorithm": "rx/0",
    "pool_url": "stratum+tcp://pool.supportxmr.com:3333",
    "wallet": "your_monero_wallet_address",
    "worker_name": "my-miner"
  }
}
```

### Aggressive Mining (High Performance)
```json
{
  "resource_management": {
    "charging_threshold": 80,
    "idle_threshold": 180,
    "battery_threshold": 15
  },
  "advanced": {
    "performance_mode": "aggressive"
  }
}
```

### Conservative Mining (Battery Saving)
```json
{
  "resource_management": {
    "charging_threshold": 95,
    "idle_threshold": 600,
    "battery_threshold": 40
  },
  "advanced": {
    "performance_mode": "conservative"
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

**Mining won't start**
- Check wallet address is correct
- Verify pool URL is accessible
- Ensure you have internet connection

**High CPU usage**
- Adjust resource management settings
- Check for other resource-intensive applications
- Monitor system temperature

**Dashboard not accessible**
- Check if port 8080 is available
- Verify firewall settings
- Try different port in configuration

**Low hashrate**
- Optimize CPU thread count
- Check system temperature
- Verify mining pool connection

### Getting Help

1. **Check Logs**: `python main.py logs`
2. **View Status**: `python main.py status`
3. **Restart Service**: `python main.py restart`
4. **Reset Configuration**: Delete `config/miner_config.json` and run setup wizard

## 🔒 Security Notes

- **Legal Use Only**: Use only on devices you own or have permission to use
- **Secure Configuration**: Change default API tokens
- **Network Security**: Use firewall rules to restrict access
- **Regular Updates**: Keep the software updated

## 📈 Performance Tips

1. **Optimize CPU Threads**: Use `auto` or `max` for best performance
2. **Monitor Temperature**: Keep CPU below 85°C
3. **Battery Management**: Use conservative mode on laptops
4. **Network Stability**: Use reliable internet connection
5. **System Resources**: Close unnecessary applications

## 🎉 Success!

You're now running the Advanced Crypto Mining Suite with intelligent resource management!

- **Dashboard**: http://localhost:8080
- **Logs**: `logs/miner.log`
- **Configuration**: `config/miner_config.json`

Happy Mining! 🚀💰