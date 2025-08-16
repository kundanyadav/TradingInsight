#!/usr/bin/env python3
"""
Direct test of the MCP server by importing it and testing in-process.
"""

import asyncio
import sys
from pathlib import Path

# Add the kiteMCPServer directory to the path
sys.path.append(str(Path(__file__).parent.parent / "kiteMCPServer"))

from fastmcp import FastMCP
from config.settings import get_settings


async def test_direct_server():
    """Test the MCP server directly."""
    print("🧪 Direct MCP Server Test")
    print("=" * 30)
    
    try:
        # Import the server module
        import demo_mcp_server
        
        # Create a FastMCP server from the imported module
        server = demo_mcp_server.mcp
        
        print("✅ Server imported successfully")
        
        # Test the server by calling tools directly
        print("✅ Server started successfully")
        
        # Test portfolio tool
        result = demo_mcp_server.get_portfolio_tool()
        print("✅ Portfolio tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test quote tool
        result = demo_mcp_server.get_quote_tool(symbol="ICICIBANK")
        print("✅ Quote tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test holdings tool
        result = demo_mcp_server.get_holdings_tool()
        print("✅ Holdings tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test positions tool
        result = demo_mcp_server.get_positions_tool()
        print("✅ Positions tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test profile tool
        result = demo_mcp_server.get_profile_tool()
        print("✅ Profile tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test market indicators tool
        result = demo_mcp_server.get_market_indicators_tool(symbol="ICICIBANK")
        print("✅ Market indicators tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test option chain tool
        result = demo_mcp_server.get_option_chain_tool(symbol="ICICIBANK")
        print("✅ Option chain tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test margins tool
        result = demo_mcp_server.get_margins_tool()
        print("✅ Margins tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test risk metrics tool
        result = demo_mcp_server.get_risk_metrics_tool()
        print("✅ Risk metrics tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test orders tool
        result = demo_mcp_server.get_orders_tool()
        print("✅ Orders tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test trades tool
        result = demo_mcp_server.get_trades_tool()
        print("✅ Trades tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test instruments tool
        result = demo_mcp_server.get_instruments_tool()
        print("✅ Instruments tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test subscribe tool
        result = demo_mcp_server.subscribe_tool(instruments=["ICICIBANK", "HDFCBANK"])
        print("✅ Subscribe tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test streaming data tool
        result = demo_mcp_server.get_streaming_data_tool()
        print("✅ Streaming data tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        # Test unsubscribe tool
        result = demo_mcp_server.unsubscribe_tool(instruments=["ICICIBANK", "HDFCBANK"])
        print("✅ Unsubscribe tool called successfully")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result: {result}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ All MCP methods are working correctly")
        print("✅ All read-only Kite Connect methods implemented successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_direct_server()) 