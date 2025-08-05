"""
Mining Engine
Handles the actual cryptocurrency mining operations with support for multiple algorithms.
"""

import time
import threading
import logging
import subprocess
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

class MiningEngine:
    """
    Mining engine that manages cryptocurrency mining operations.
    Supports multiple algorithms and mining software.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Mining configuration
        self.mining_config = config.get('mining', {})
        self.algorithm = self.mining_config.get('algorithm', 'rx/0')  # RandomX for Monero
        self.pool_url = self.mining_config.get('pool_url', '')
        self.wallet = self.mining_config.get('wallet', '')
        self.worker_name = self.mining_config.get('worker_name', 'advanced-miner')
        self.cpu_threads = self.mining_config.get('cpu_threads', 'auto')
        self.gpu_enabled = self.mining_config.get('gpu_enabled', False)
        
        # State management
        self.running = False
        self.mining_process = None
        self.current_hashrate = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        self.start_time = None
        
        # Threading
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        # Mining software paths (would be configured based on platform)
        self.miner_paths = {
            'xmrig': 'miners/xmrig/xmrig.exe',  # Windows
            't-rex': 'miners/t-rex/t-rex.exe',  # NVIDIA GPU
            'teamredminer': 'miners/teamredminer/teamredminer'  # AMD GPU
        }
        
        self.logger.info("Mining Engine initialized")
    
    def start(self):
        """Start the mining operation"""
        if self.running:
            self.logger.warning("Mining engine is already running")
            return
        
        self.logger.info("🚀 Starting Mining Engine...")
        self.running = True
        self.start_time = time.time()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        # Start mining process
        self._start_mining_process()
        
        self.logger.info("✅ Mining Engine started successfully")
    
    def stop(self):
        """Stop the mining operation"""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping Mining Engine...")
        self.running = False
        self.stop_event.set()
        
        # Stop mining process
        self._stop_mining_process()
        
        # Wait for monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("✅ Mining Engine stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current mining statistics"""
        return {
            'running': self.running,
            'hashrate': self.current_hashrate,
            'shares_accepted': self.shares_accepted,
            'shares_rejected': self.shares_rejected,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'algorithm': self.algorithm,
            'pool_url': self.pool_url,
            'worker_name': self.worker_name
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update mining configuration"""
        self.config.update(new_config)
        self.mining_config = new_config.get('mining', {})
        self.algorithm = self.mining_config.get('algorithm', self.algorithm)
        self.pool_url = self.mining_config.get('pool_url', self.pool_url)
        self.wallet = self.mining_config.get('wallet', self.wallet)
        self.worker_name = self.mining_config.get('worker_name', self.worker_name)
        self.cpu_threads = self.mining_config.get('cpu_threads', self.cpu_threads)
        self.gpu_enabled = self.mining_config.get('gpu_enabled', self.gpu_enabled)
        
        self.logger.info("Mining Engine configuration updated")
    
    def emergency_stop(self):
        """Emergency stop - immediately halt mining"""
        self.logger.warning("🚨 Emergency stop - halting mining")
        self._stop_mining_process()
        self.running = False
        self.stop_event.set()
    
    def is_healthy(self) -> bool:
        """Check if mining engine is healthy"""
        if not self.running:
            return False
        
        # Check if mining process is still running
        if self.mining_process and self.mining_process.poll() is not None:
            self.logger.warning("Mining process has terminated unexpectedly")
            return False
        
        return True
    
    def _start_mining_process(self):
        """Start the mining process"""
        try:
            # Determine which miner to use based on algorithm and hardware
            miner_cmd = self._build_miner_command()
            
            if not miner_cmd:
                self.logger.error("No suitable miner found for algorithm: " + self.algorithm)
                return
            
            self.logger.info(f"Starting miner: {' '.join(miner_cmd)}")
            
            # Start the mining process
            self.mining_process = subprocess.Popen(
                miner_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.logger.info(f"Mining process started with PID: {self.mining_process.pid}")
            
        except Exception as e:
            self.logger.error(f"Failed to start mining process: {e}")
            self.running = False
    
    def _stop_mining_process(self):
        """Stop the mining process"""
        if self.mining_process:
            try:
                self.logger.info("Stopping mining process...")
                self.mining_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.mining_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Mining process didn't stop gracefully, forcing...")
                    self.mining_process.kill()
                    self.mining_process.wait()
                
                self.mining_process = None
                self.logger.info("Mining process stopped")
                
            except Exception as e:
                self.logger.error(f"Error stopping mining process: {e}")
    
    def _build_miner_command(self) -> Optional[List[str]]:
        """Build the command to start the mining software"""
        if self.algorithm == 'rx/0':  # RandomX (Monero)
            return self._build_xmrig_command()
        elif self.algorithm == 'kawpow':  # KawPow (Ravencoin)
            return self._build_kawpow_command()
        elif self.algorithm == 'ethash':  # Ethash (Ethereum)
            return self._build_ethash_command()
        else:
            self.logger.error(f"Unsupported algorithm: {self.algorithm}")
            return None
    
    def _build_xmrig_command(self) -> List[str]:
        """Build XMRig command for RandomX mining"""
        xmrig_path = self.miner_paths.get('xmrig')
        
        if not Path(xmrig_path).exists():
            # Fallback to system PATH
            xmrig_path = 'xmrig'
        
        cmd = [
            xmrig_path,
            '--url=' + self.pool_url,
            '--user=' + self.wallet,
            '--pass=' + self.worker_name,
            '--algo=rx/0',
            '--threads=' + str(self.cpu_threads),
            '--background',
            '--print-time=60',
            '--api-port=18067',
            '--api-access-token=advanced-miner-token',
            '--api-worker-id=' + self.worker_name,
            '--donate-level=1'
        ]
        
        return cmd
    
    def _build_kawpow_command(self) -> List[str]:
        """Build KawPow mining command"""
        if self.gpu_enabled:
            # Use T-Rex for NVIDIA or TeamRedMiner for AMD
            if self._has_nvidia_gpu():
                return self._build_trex_kawpow_command()
            else:
                return self._build_teamredminer_kawpow_command()
        else:
            # CPU mining with XMRig
            return self._build_xmrig_kawpow_command()
    
    def _build_ethash_command(self) -> List[str]:
        """Build Ethash mining command"""
        if self.gpu_enabled:
            if self._has_nvidia_gpu():
                return self._build_trex_ethash_command()
            else:
                return self._build_teamredminer_ethash_command()
        else:
            self.logger.warning("Ethash requires GPU mining")
            return None
    
    def _build_trex_kawpow_command(self) -> List[str]:
        """Build T-Rex KawPow command"""
        trex_path = self.miner_paths.get('t-rex')
        
        if not Path(trex_path).exists():
            trex_path = 't-rex'
        
        cmd = [
            trex_path,
            '-a', 'kawpow',
            '-o', self.pool_url,
            '-u', self.wallet,
            '-p', self.worker_name,
            '--api-bind-http', '127.0.0.1:4067',
            '--api-read-only'
        ]
        
        return cmd
    
    def _build_teamredminer_kawpow_command(self) -> List[str]:
        """Build TeamRedMiner KawPow command"""
        teamred_path = self.miner_paths.get('teamredminer')
        
        if not Path(teamred_path).exists():
            teamred_path = 'teamredminer'
        
        cmd = [
            teamred_path,
            '-a', 'kawpow',
            '-o', self.pool_url,
            '-u', self.wallet,
            '-p', self.worker_name,
            '--api_port=4067'
        ]
        
        return cmd
    
    def _build_xmrig_kawpow_command(self) -> List[str]:
        """Build XMRig KawPow command (CPU)"""
        xmrig_path = self.miner_paths.get('xmrig')
        
        if not Path(xmrig_path).exists():
            xmrig_path = 'xmrig'
        
        cmd = [
            xmrig_path,
            '--url=' + self.pool_url,
            '--user=' + self.wallet,
            '--pass=' + self.worker_name,
            '--algo=kawpow',
            '--threads=' + str(self.cpu_threads),
            '--background',
            '--print-time=60',
            '--api-port=18067',
            '--api-access-token=advanced-miner-token',
            '--api-worker-id=' + self.worker_name,
            '--donate-level=1'
        ]
        
        return cmd
    
    def _build_trex_ethash_command(self) -> List[str]:
        """Build T-Rex Ethash command"""
        trex_path = self.miner_paths.get('t-rex')
        
        if not Path(trex_path).exists():
            trex_path = 't-rex'
        
        cmd = [
            trex_path,
            '-a', 'ethash',
            '-o', self.pool_url,
            '-u', self.wallet,
            '-p', self.worker_name,
            '--api-bind-http', '127.0.0.1:4067',
            '--api-read-only'
        ]
        
        return cmd
    
    def _build_teamredminer_ethash_command(self) -> List[str]:
        """Build TeamRedMiner Ethash command"""
        teamred_path = self.miner_paths.get('teamredminer')
        
        if not Path(teamred_path).exists():
            teamred_path = 'teamredminer'
        
        cmd = [
            teamred_path,
            '-a', 'ethash',
            '-o', self.pool_url,
            '-u', self.wallet,
            '-p', self.worker_name,
            '--api_port=4067'
        ]
        
        return cmd
    
    def _has_nvidia_gpu(self) -> bool:
        """Check if system has NVIDIA GPU"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                if 'nvidia' in gpu.name.lower():
                    return True
            return False
        except:
            return False
    
    def _monitoring_loop(self):
        """Monitor mining process and update statistics"""
        while self.running and not self.stop_event.is_set():
            try:
                # Check if process is still running
                if self.mining_process and self.mining_process.poll() is not None:
                    self.logger.warning("Mining process terminated, restarting...")
                    self._start_mining_process()
                
                # Update statistics from miner API
                self._update_mining_stats()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    def _update_mining_stats(self):
        """Update mining statistics from miner API"""
        try:
            # Try to get stats from XMRig API
            if self.algorithm == 'rx/0':
                self._update_xmrig_stats()
            else:
                # For other miners, we'd implement their specific APIs
                pass
                
        except Exception as e:
            self.logger.error(f"Error updating mining stats: {e}")
    
    def _update_xmrig_stats(self):
        """Update statistics from XMRig API"""
        try:
            import requests
            
            # XMRig API endpoint
            api_url = "http://127.0.0.1:18067/api/v1/summary"
            headers = {'Authorization': 'Bearer advanced-miner-token'}
            
            response = requests.get(api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                self.current_hashrate = data.get('hashrate', {}).get('total', [0])[0]
                self.shares_accepted = data.get('results', {}).get('shares_good', 0)
                self.shares_rejected = data.get('results', {}).get('shares_total', 0) - self.shares_accepted
                
        except Exception as e:
            self.logger.debug(f"Could not update XMRig stats: {e}")
    
    def get_mining_software_info(self) -> Dict[str, Any]:
        """Get information about available mining software"""
        info = {
            'xmrig': {
                'path': self.miner_paths.get('xmrig'),
                'exists': Path(self.miner_paths.get('xmrig', '')).exists(),
                'algorithms': ['rx/0', 'kawpow', 'randomx']
            },
            't-rex': {
                'path': self.miner_paths.get('t-rex'),
                'exists': Path(self.miner_paths.get('t-rex', '')).exists(),
                'algorithms': ['kawpow', 'ethash', 'octopus']
            },
            'teamredminer': {
                'path': self.miner_paths.get('teamredminer'),
                'exists': Path(self.miner_paths.get('teamredminer', '')).exists(),
                'algorithms': ['kawpow', 'ethash', 'autolykos']
            }
        }
        
        return info