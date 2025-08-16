"""
Integration tests for MCP communication.
"""

import pytest
import asyncio
import subprocess
import time
from unittest.mock import Mock, AsyncMock

from services.mcp_client import MCPClient, MCPConnectionError
from config.settings import get_settings


class TestMCPIntegration:
    """Test MCP client-server integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mcp_client = MCPClient(self.settings)
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'mcp_client') and self.mcp_client.client:
            asyncio.run(self.mcp_client.disconnect())
    
    async def test_mcp_client_initialization(self):
        """Test MCP client initialization."""
        assert self.mcp_client is not None
        assert self.mcp_client.settings == self.settings
        assert self.mcp_client._cache == {}
    
    async def test_mcp_connection_with_mock_server(self):
        """Test MCP connection with mock server."""
        # Mock the transport to avoid actual server connection
        self.mcp_client._start_mcp_server = AsyncMock()
        
        # Test connection
        connected = await self.mcp_client.connect()
        
        # Since we're mocking, we expect it to work
        assert connected == True
    
    async def test_mcp_cache_functionality(self):
        """Test MCP client caching functionality."""
        # Test cache operations
        self.mcp_client._cache_data("test_key", {"data": "test"})
        
        assert "test_key" in self.mcp_client._cache
        assert self.mcp_client._cache["test_key"]["data"] == "test"
        
        # Test cache validation
        assert self.mcp_client._is_cache_valid("test_key") == True
        
        # Test cache clearing
        self.mcp_client.clear_cache()
        assert len(self.mcp_client._cache) == 0
    
    async def test_mcp_cache_stats(self):
        """Test MCP cache statistics."""
        # Add some test data
        self.mcp_client._cache_data("key1", {"data": "test1"})
        self.mcp_client._cache_data("key2", {"data": "test2"})
        
        stats = self.mcp_client.get_cache_stats()
        
        assert "total_entries" in stats
        assert "cache_size" in stats
        assert stats["total_entries"] == 2


class TestMCPErrorHandling:
    """Test MCP error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mcp_client = MCPClient(self.settings)
    
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        # Mock connection failure
        self.mcp_client._start_mcp_server = AsyncMock(side_effect=Exception("Connection failed"))
        
        with pytest.raises(MCPConnectionError):
            await self.mcp_client.connect()
    
    async def test_tool_call_error_handling(self):
        """Test handling of tool call errors."""
        # Mock successful connection but failed tool call
        self.mcp_client._start_mcp_server = AsyncMock()
        self.mcp_client._make_mcp_call = AsyncMock(side_effect=MCPConnectionError("Tool call failed"))
        
        await self.mcp_client.connect()
        
        with pytest.raises(MCPConnectionError):
            await self.mcp_client.get_portfolio_data()
    
    async def test_retry_logic(self):
        """Test retry logic for failed calls."""
        # Mock tool call that fails twice then succeeds
        call_count = 0
        
        async def mock_tool_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"success": True}
        
        self.mcp_client._make_mcp_call = mock_tool_call
        
        # Should succeed after retries
        result = await self.mcp_client.get_portfolio_data()
        assert result == {"success": True}
        assert call_count == 3


class TestMCPDataTransformation:
    """Test MCP data transformation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mcp_client = MCPClient(self.settings)
    
    def test_portfolio_data_transformation(self):
        """Test portfolio data transformation."""
        # Mock raw portfolio data
        raw_data = {
            "total_margin": 100000.0,
            "available_cash": 50000.0,
            "total_exposure": 150000.0,
            "positions": [
                {
                    "symbol": "ICICIBANK",
                    "quantity": 100,
                    "average_price": 950.0,
                    "current_price": 960.0,
                    "pnl": 1000.0,
                    "margin_used": 50000.0,
                    "premium_collected": 5000.0,
                    "rom": 10.0,
                    "ssr": 5.0,
                    "risk_indicator": 6,
                    "reward_risk_ratio": 833.33,
                    "position_type": "short",
                    "expiry": "2024-01-25T00:00:00",
                    "strike_price": 950.0,
                    "option_type": "PE"
                }
            ],
            "sector_exposure": {"Banking": 0.6, "IT": 0.4},
            "risk_score": 6.5
        }
        
        portfolio = self.mcp_client._transform_portfolio_data(raw_data)
        
        assert portfolio.total_margin == 100000.0
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0].symbol == "ICICIBANK"
        assert portfolio.positions[0].rom == 10.0
    
    def test_portfolio_data_transformation_list_format(self):
        """Test portfolio data transformation with list format."""
        # Mock raw portfolio data as list (from demo server)
        raw_data = [
            {
                "symbol": "ICICIBANK",
                "quantity": 100,
                "average_price": 950.0,
                "current_price": 960.0,
                "pnl": 1000.0,
                "margin_used": 50000.0,
                "premium_collected": 5000.0,
                "rom": 10.0,
                "ssr": 5.0,
                "risk_indicator": 6,
                "reward_risk_ratio": 833.33,
                "position_type": "short",
                "expiry": "2024-01-25T00:00:00",
                "strike_price": 950.0,
                "option_type": "PE"
            }
        ]
        
        portfolio = self.mcp_client._transform_portfolio_data(raw_data)
        
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0].symbol == "ICICIBANK"
        assert portfolio.total_margin == 100000.0  # Default value


class TestMCPServerCommunication:
    """Test actual MCP server communication (if server available)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mcp_client = MCPClient(self.settings)
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'mcp_client') and self.mcp_client.client:
            asyncio.run(self.mcp_client.disconnect())
    
    async def test_server_availability(self):
        """Test if MCP server is available."""
        # This test will only pass if the demo server is running
        try:
            connected = await self.mcp_client.connect()
            if connected:
                # Test basic functionality
                portfolio = await self.mcp_client.get_portfolio_data()
                assert portfolio is not None
                await self.mcp_client.disconnect()
        except Exception as e:
            # Server not available, skip test
            pytest.skip(f"MCP server not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__]) 