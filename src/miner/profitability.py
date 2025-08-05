"""
Profitability Calculator
Calculates mining profitability, tracks earnings, and provides financial insights.
"""

import time
import requests
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ProfitabilityData:
    """Profitability data structure"""
    hashrate: float
    coin_price: float
    daily_earnings: float
    monthly_earnings: float
    yearly_earnings: float
    electricity_cost: float
    net_profit: float
    roi_percentage: float

class ProfitabilityCalculator:
    """
    Calculates mining profitability and tracks earnings.
    Integrates with cryptocurrency price APIs and mining pool APIs.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.profitability_config = config.get('profitability', {})
        self.electricity_cost = self.profitability_config.get('electricity_cost', 0.12)  # USD per kWh
        self.power_consumption = self.profitability_config.get('power_consumption', 200)  # Watts
        self.currency = self.profitability_config.get('currency', 'USD')
        
        # Historical data
        self.earnings_history = []
        self.hashrate_history = []
        self.price_history = {}
        
        # Cache for API calls
        self.price_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        self.logger.info("Profitability Calculator initialized")
    
    def calculate_earnings(self, hashrate: float, mining_time: float) -> float:
        """Calculate earnings based on hashrate and mining time"""
        try:
            # Get current coin price
            coin_price = self.get_coin_price()
            
            # Calculate earnings (simplified calculation)
            # In a real implementation, you'd use pool-specific APIs
            daily_hashrate = hashrate * 86400  # hashrate * seconds per day
            daily_coins = daily_hashrate / (2**32)  # Simplified difficulty calculation
            
            # Calculate earnings in USD
            daily_earnings = daily_coins * coin_price
            
            # Calculate earnings for the given time period
            earnings = daily_earnings * (mining_time / 86400)
            
            # Store in history
            self.earnings_history.append({
                'timestamp': time.time(),
                'hashrate': hashrate,
                'earnings': earnings,
                'mining_time': mining_time
            })
            
            return earnings
            
        except Exception as e:
            self.logger.error(f"Error calculating earnings: {e}")
            return 0.0
    
    def get_current_profitability(self) -> ProfitabilityData:
        """Get current profitability data"""
        try:
            # Get current hashrate (would come from mining engine)
            current_hashrate = 1000  # Placeholder - should come from mining engine
            
            # Get coin price
            coin_price = self.get_coin_price()
            
            # Calculate daily earnings
            daily_hashrate = current_hashrate * 86400
            daily_coins = daily_hashrate / (2**32)
            daily_earnings = daily_coins * coin_price
            
            # Calculate monthly and yearly earnings
            monthly_earnings = daily_earnings * 30
            yearly_earnings = daily_earnings * 365
            
            # Calculate electricity costs
            daily_power_kwh = (self.power_consumption * 24) / 1000
            daily_electricity_cost = daily_power_kwh * self.electricity_cost
            monthly_electricity_cost = daily_electricity_cost * 30
            yearly_electricity_cost = daily_electricity_cost * 365
            
            # Calculate net profit
            daily_net_profit = daily_earnings - daily_electricity_cost
            monthly_net_profit = monthly_earnings - monthly_electricity_cost
            yearly_net_profit = yearly_earnings - yearly_electricity_cost
            
            # Calculate ROI (assuming hardware cost of $1000)
            hardware_cost = 1000
            roi_percentage = (yearly_net_profit / hardware_cost) * 100 if hardware_cost > 0 else 0
            
            return ProfitabilityData(
                hashrate=current_hashrate,
                coin_price=coin_price,
                daily_earnings=daily_earnings,
                monthly_earnings=monthly_earnings,
                yearly_earnings=yearly_earnings,
                electricity_cost=daily_electricity_cost,
                net_profit=daily_net_profit,
                roi_percentage=roi_percentage
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating profitability: {e}")
            return ProfitabilityData(0, 0, 0, 0, 0, 0, 0, 0)
    
    def get_coin_price(self, coin: str = 'XMR') -> float:
        """Get current cryptocurrency price"""
        try:
            # Check cache first
            cache_key = f"{coin}_{int(time.time() // self.cache_duration)}"
            if cache_key in self.price_cache:
                return self.price_cache[cache_key]
            
            # Fetch from API
            price = self._fetch_coin_price(coin)
            
            # Cache the result
            self.price_cache[cache_key] = price
            
            return price
            
        except Exception as e:
            self.logger.error(f"Error getting coin price: {e}")
            return 0.0
    
    def _fetch_coin_price(self, coin: str) -> float:
        """Fetch coin price from API"""
        try:
            # Use CoinGecko API (free and reliable)
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': self._get_coin_id(coin),
                'vs_currencies': self.currency.lower()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            coin_id = self._get_coin_id(coin)
            
            if coin_id in data and self.currency.lower() in data[coin_id]:
                price = data[coin_id][self.currency.lower()]
                self.logger.debug(f"Fetched {coin} price: {price} {self.currency}")
                return price
            else:
                self.logger.warning(f"Could not find price for {coin}")
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error fetching coin price: {e}")
            return 0.0
    
    def _get_coin_id(self, coin: str) -> str:
        """Get CoinGecko coin ID"""
        coin_mapping = {
            'XMR': 'monero',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'RVN': 'ravencoin',
            'ERG': 'ergo',
            'CFX': 'conflux-token'
        }
        return coin_mapping.get(coin.upper(), 'monero')
    
    def get_earnings_summary(self, period: str = '24h') -> Dict[str, Any]:
        """Get earnings summary for a specific period"""
        try:
            now = time.time()
            
            if period == '24h':
                start_time = now - 86400
            elif period == '7d':
                start_time = now - 604800
            elif period == '30d':
                start_time = now - 2592000
            else:
                start_time = 0
            
            # Filter earnings history
            period_earnings = [
                entry for entry in self.earnings_history
                if entry['timestamp'] >= start_time
            ]
            
            if not period_earnings:
                return {
                    'period': period,
                    'total_earnings': 0.0,
                    'average_hashrate': 0.0,
                    'total_mining_time': 0.0,
                    'earnings_per_hour': 0.0
                }
            
            # Calculate summary
            total_earnings = sum(entry['earnings'] for entry in period_earnings)
            total_mining_time = sum(entry['mining_time'] for entry in period_earnings)
            average_hashrate = sum(entry['hashrate'] for entry in period_earnings) / len(period_earnings)
            earnings_per_hour = total_earnings / (total_mining_time / 3600) if total_mining_time > 0 else 0
            
            return {
                'period': period,
                'total_earnings': total_earnings,
                'average_hashrate': average_hashrate,
                'total_mining_time': total_mining_time,
                'earnings_per_hour': earnings_per_hour,
                'data_points': len(period_earnings)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating earnings summary: {e}")
            return {}
    
    def get_profitability_forecast(self, days: int = 30) -> Dict[str, Any]:
        """Get profitability forecast for the next N days"""
        try:
            current_profitability = self.get_current_profitability()
            
            # Calculate forecast based on current profitability
            daily_earnings = current_profitability.daily_earnings
            daily_costs = current_profitability.electricity_cost
            
            forecast = {
                'daily_earnings': daily_earnings,
                'daily_costs': daily_costs,
                'daily_net': daily_earnings - daily_costs,
                'total_earnings': daily_earnings * days,
                'total_costs': daily_costs * days,
                'total_net': (daily_earnings - daily_costs) * days,
                'roi_percentage': current_profitability.roi_percentage,
                'break_even_days': self._calculate_break_even_days(daily_earnings - daily_costs)
            }
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error calculating profitability forecast: {e}")
            return {}
    
    def _calculate_break_even_days(self, daily_profit: float) -> int:
        """Calculate days to break even on hardware investment"""
        try:
            hardware_cost = 1000  # Assumed hardware cost
            if daily_profit <= 0:
                return -1  # Never break even
            
            break_even_days = hardware_cost / daily_profit
            return int(break_even_days)
            
        except Exception as e:
            self.logger.error(f"Error calculating break-even days: {e}")
            return -1
    
    def get_mining_efficiency(self) -> Dict[str, Any]:
        """Calculate mining efficiency metrics"""
        try:
            current_profitability = self.get_current_profitability()
            
            # Calculate efficiency metrics
            power_efficiency = current_profitability.hashrate / self.power_consumption  # H/s per Watt
            cost_efficiency = current_profitability.daily_earnings / current_profitability.electricity_cost
            
            return {
                'power_efficiency': power_efficiency,
                'cost_efficiency': cost_efficiency,
                'hashrate_per_watt': power_efficiency,
                'earnings_per_kwh': cost_efficiency,
                'power_consumption': self.power_consumption,
                'electricity_cost': self.electricity_cost
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating mining efficiency: {e}")
            return {}
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update profitability calculator configuration"""
        self.config.update(new_config)
        self.profitability_config = new_config.get('profitability', {})
        self.electricity_cost = self.profitability_config.get('electricity_cost', self.electricity_cost)
        self.power_consumption = self.profitability_config.get('power_consumption', self.power_consumption)
        self.currency = self.profitability_config.get('currency', self.currency)
        
        self.logger.info("Profitability Calculator configuration updated")
    
    def get_historical_data(self, days: int = 7) -> Dict[str, Any]:
        """Get historical mining data"""
        try:
            now = time.time()
            start_time = now - (days * 86400)
            
            # Filter historical data
            historical_earnings = [
                entry for entry in self.earnings_history
                if entry['timestamp'] >= start_time
            ]
            
            # Group by day
            daily_data = {}
            for entry in historical_earnings:
                date = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d')
                if date not in daily_data:
                    daily_data[date] = {
                        'earnings': 0.0,
                        'hashrate': 0.0,
                        'mining_time': 0.0,
                        'count': 0
                    }
                
                daily_data[date]['earnings'] += entry['earnings']
                daily_data[date]['hashrate'] += entry['hashrate']
                daily_data[date]['mining_time'] += entry['mining_time']
                daily_data[date]['count'] += 1
            
            # Calculate averages
            for date in daily_data:
                count = daily_data[date]['count']
                if count > 0:
                    daily_data[date]['hashrate'] /= count
            
            return {
                'daily_data': daily_data,
                'total_earnings': sum(entry['earnings'] for entry in historical_earnings),
                'average_hashrate': sum(entry['hashrate'] for entry in historical_earnings) / len(historical_earnings) if historical_earnings else 0,
                'total_mining_time': sum(entry['mining_time'] for entry in historical_earnings)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return {}
    
    def clear_cache(self):
        """Clear price cache"""
        self.price_cache.clear()
        self.logger.info("Price cache cleared")
    
    def export_data(self, format: str = 'json') -> str:
        """Export profitability data"""
        try:
            data = {
                'earnings_history': self.earnings_history,
                'hashrate_history': self.hashrate_history,
                'price_history': self.price_history,
                'configuration': {
                    'electricity_cost': self.electricity_cost,
                    'power_consumption': self.power_consumption,
                    'currency': self.currency
                }
            }
            
            if format.lower() == 'json':
                import json
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return ""