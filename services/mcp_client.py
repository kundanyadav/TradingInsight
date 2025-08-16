"""
MCP Client for TradingInsight application.
Handles communication with the Kite MCP server.
"""

import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastmcp import FastMCP

from config.settings import get_settings

logger = logging.getLogger(__name__)


class MCPConnectionError(Exception):
    """Custom exception for MCP connection errors."""
    pass


class MCPClient:
    """MCP Client for communicating with Kite MCP server."""
    
    def __init__(self, settings):
        """Initialize MCP client."""
        self.settings = settings
        self.client = None
        self._cache = {}
        self._server_process = None
        
    async def connect(self) -> bool:
        """Connect to MCP server."""
        try:
            # Initialize FastMCP client
            server_path = Path(__file__).parent.parent / "kiteMCPServer" / "demo_mcp_server.py"
            from fastmcp import Client
            self.client = Client(
                transport=f"stdio://{sys.executable} {server_path}"
            )
            
            logger.info("MCP client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise MCPConnectionError(f"Connection failed: {e}")
    
    async def _start_mcp_server(self):
        """Start the MCP server process."""
        try:
            server_path = Path(__file__).parent.parent / "kiteMCPServer" / "demo_mcp_server.py"
            self._server_process = subprocess.Popen(
                [sys.executable, str(server_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(1)
            
            if self._server_process.poll() is not None:
                raise Exception("Server process failed to start")
                
            logger.info("MCP server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        try:
            if self._server_process:
                self._server_process.terminate()
                self._server_process.wait(timeout=5)
                logger.info("MCP server stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
    
    async def _make_mcp_call(self, tool_name: str, **kwargs) -> Any:
        """Make a call to an MCP tool."""
        if not self.client:
            raise MCPConnectionError("Client not connected")
        
        for attempt in range(self.settings.max_retries):
            try:
                logger.debug(f"Calling MCP tool {tool_name} (attempt {attempt + 1})")
                
                # Call the MCP tool using async context manager as required by FastMCP
                async with self.client as client:
                    arguments = kwargs if kwargs else None
                    result = await client.call_tool(tool_name, arguments=arguments)
                
                # Extract content from CallToolResult
                if hasattr(result, 'content'):
                    data = result.content
                elif hasattr(result, 'result'):
                    data = result.result
                else:
                    data = result
                
                logger.debug(f"MCP tool {tool_name} returned successfully")
                return data
                
            except Exception as e:
                logger.warning(f"MCP tool {tool_name} failed (attempt {attempt + 1}): {e}")
                if attempt == self.settings.max_retries - 1:
                    raise MCPConnectionError(f"Tool {tool_name} failed after {self.settings.max_retries} attempts: {e}")
                await asyncio.sleep(self.settings.retry_delay)
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp."""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
            "ttl": self.settings.cache_ttl
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache:
            return False
        
        cache_entry = self._cache[key]
        age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
        return age < cache_entry["ttl"]
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "cache_size": sum(len(str(v)) for v in self._cache.values())
        }
    
    # Portfolio & Holdings Methods
    async def get_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data."""
        try:
            cache_key = "portfolio_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_portfolio_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get portfolio data: {e}")
            raise MCPConnectionError(f"Portfolio data retrieval failed: {e}")
    
    async def get_holdings_data(self) -> List[Dict[str, Any]]:
        """Get holdings data."""
        try:
            cache_key = "holdings_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_holdings_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get holdings data: {e}")
            raise MCPConnectionError(f"Holdings data retrieval failed: {e}")
    
    async def get_positions_data(self) -> List[Dict[str, Any]]:
        """Get positions data."""
        try:
            cache_key = "positions_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_positions_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get positions data: {e}")
            raise MCPConnectionError(f"Positions data retrieval failed: {e}")
    
    async def get_profile_data(self) -> Dict[str, Any]:
        """Get user profile data."""
        try:
            cache_key = "profile_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_profile_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get profile data: {e}")
            raise MCPConnectionError(f"Profile data retrieval failed: {e}")
    
    # Market Data Methods
    async def get_quote_data(self, symbol: str) -> Dict[str, Any]:
        """Get quote data for a symbol."""
        try:
            cache_key = f"quote_{symbol}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_quote_tool", symbol=symbol)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get quote data for {symbol}: {e}")
            raise MCPConnectionError(f"Quote data retrieval failed: {e}")
    
    async def get_ltp_data(self, symbol: str) -> Dict[str, Any]:
        """Get last traded price for a symbol."""
        try:
            cache_key = f"ltp_{symbol}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_ltp_tool", symbol=symbol)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get LTP data for {symbol}: {e}")
            raise MCPConnectionError(f"LTP data retrieval failed: {e}")
    
    async def get_ohlc_data(self, symbol: str, interval: str = "day") -> Dict[str, Any]:
        """Get OHLC data for a symbol."""
        try:
            cache_key = f"ohlc_{symbol}_{interval}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_ohlc_tool", symbol=symbol, interval=interval)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get OHLC data for {symbol}: {e}")
            raise MCPConnectionError(f"OHLC data retrieval failed: {e}")
    
    async def get_historical_data(self, symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Get historical data for a symbol."""
        try:
            cache_key = f"historical_{symbol}_{from_date}_{to_date}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_historical_data_tool", symbol=symbol, from_date=from_date, to_date=to_date)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            raise MCPConnectionError(f"Historical data retrieval failed: {e}")
    
    async def get_instruments_data(self) -> List[Dict[str, Any]]:
        """Get all available instruments."""
        try:
            cache_key = "instruments_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_instruments_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get instruments data: {e}")
            raise MCPConnectionError(f"Instruments data retrieval failed: {e}")
    
    # Order History Methods (Read-Only)
    async def get_orders_data(self) -> List[Dict[str, Any]]:
        """Get order history."""
        try:
            cache_key = "orders_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_orders_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get orders data: {e}")
            raise MCPConnectionError(f"Orders data retrieval failed: {e}")
    
    async def get_trades_data(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        try:
            cache_key = "trades_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_trades_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get trades data: {e}")
            raise MCPConnectionError(f"Trades data retrieval failed: {e}")
    
    async def get_order_history(self, order_id: str) -> Dict[str, Any]:
        """Get specific order details."""
        try:
            cache_key = f"order_history_{order_id}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_order_history_tool", order_id=order_id)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get order history for {order_id}: {e}")
            raise MCPConnectionError(f"Order history retrieval failed: {e}")
    
    async def get_order_trades(self, order_id: str) -> List[Dict[str, Any]]:
        """Get trades for specific order."""
        try:
            cache_key = f"order_trades_{order_id}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_order_trades_tool", order_id=order_id)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get order trades for {order_id}: {e}")
            raise MCPConnectionError(f"Order trades retrieval failed: {e}")
    
    # Risk & Margin Methods (Read-Only)
    async def get_margins_data(self) -> Dict[str, Any]:
        """Get current margin information."""
        try:
            cache_key = "margins_data"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_margins_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get margins data: {e}")
            raise MCPConnectionError(f"Margins data retrieval failed: {e}")
    
    async def get_order_margins(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get order margin calculation (simulation only)."""
        try:
            data = await self._make_mcp_call("get_order_margins_tool", order_params=order_params)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get order margins: {e}")
            raise MCPConnectionError(f"Order margins calculation failed: {e}")
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """Get portfolio risk metrics."""
        try:
            cache_key = "risk_metrics"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_risk_metrics_tool")
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get risk metrics: {e}")
            raise MCPConnectionError(f"Risk metrics retrieval failed: {e}")
    
    async def get_basket_margins(self, instruments: List[str]) -> Dict[str, Any]:
        """Get basket margin calculation (simulation only)."""
        try:
            data = await self._make_mcp_call("get_basket_margins_tool", instruments=instruments)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get basket margins: {e}")
            raise MCPConnectionError(f"Basket margins calculation failed: {e}")
    
    # Real-time Data Methods (Read-Only)
    async def subscribe_to_data(self, instruments: List[str]) -> Dict[str, Any]:
        """Subscribe to real-time data."""
        try:
            data = await self._make_mcp_call("subscribe_tool", instruments=instruments)
            return data
            
        except Exception as e:
            logger.error(f"Failed to subscribe to data: {e}")
            raise MCPConnectionError(f"Subscription failed: {e}")
    
    async def unsubscribe_from_data(self, instruments: List[str]) -> Dict[str, Any]:
        """Unsubscribe from real-time data."""
        try:
            data = await self._make_mcp_call("unsubscribe_tool", instruments=instruments)
            return data
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from data: {e}")
            raise MCPConnectionError(f"Unsubscription failed: {e}")
    
    async def get_streaming_data(self) -> Dict[str, Any]:
        """Get real-time market data."""
        try:
            data = await self._make_mcp_call("get_streaming_data_tool")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get streaming data: {e}")
            raise MCPConnectionError(f"Streaming data retrieval failed: {e}")
    
    # Additional Analysis Methods
    async def get_market_indicators(self, symbol: str) -> Dict[str, Any]:
        """Get market indicators for analysis."""
        try:
            cache_key = f"market_indicators_{symbol}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_market_indicators_tool", symbol=symbol)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get market indicators for {symbol}: {e}")
            raise MCPConnectionError(f"Market indicators retrieval failed: {e}")
    
    async def get_option_chain_data(self, symbol: str) -> Dict[str, Any]:
        """Get option chain data for analysis."""
        try:
            cache_key = f"option_chain_{symbol}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]["data"]
            
            data = await self._make_mcp_call("get_option_chain_tool", symbol=symbol)
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get option chain data for {symbol}: {e}")
            raise MCPConnectionError(f"Option chain data retrieval failed: {e}")
    
    def _transform_portfolio_data(self, raw_data: Any) -> Dict[str, Any]:
        """Transform raw portfolio data to standardized format."""
        if isinstance(raw_data, list):
            # Handle list format from demo server
            positions = raw_data
            total_margin = sum(pos.get("margin_used", 0) for pos in positions)
            total_premium = sum(pos.get("premium_collected", 0) for pos in positions)
            
            return {
                "total_margin": total_margin,
                "available_cash": 50000.0,  # Default value
                "total_exposure": total_margin + 50000.0,
                "positions": positions,
                "sector_exposure": {"Banking": 0.6, "IT": 0.4},  # Default
                "risk_score": 6.5  # Default
            }
        else:
            # Handle dict format
            return raw_data 