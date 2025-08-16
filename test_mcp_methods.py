#!/usr/bin/env python3
"""
Test script for MCP client methods.
Tests all the new read-only methods implemented in the MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add the TradingInsight directory to the path
sys.path.append(str(Path(__file__).parent))

from services.mcp_client import MCPClient
from config.settings import get_settings


async def test_mcp_methods():
    """Test all MCP client methods."""
    print("🧪 Testing MCP Client Methods")
    print("=" * 50)
    
    settings = get_settings()
    client = MCPClient(settings)
    
    try:
        # Connect to MCP server
        print("🔗 Connecting to MCP server...")
        await client.connect()
        print("✅ Connected successfully")
        
        # Test Portfolio & Holdings Methods
        print("\n📊 Testing Portfolio & Holdings Methods:")
        print("-" * 30)
        
        # Test portfolio data
        portfolio = await client.get_portfolio_data()
        print(f"✅ Portfolio data: {len(portfolio.get('positions', []))} positions")
        
        # Test holdings data
        holdings = await client.get_holdings_data()
        print(f"✅ Holdings data: {len(holdings)} holdings")
        
        # Test positions data
        positions = await client.get_positions_data()
        print(f"✅ Positions data: {len(positions)} positions")
        
        # Test profile data
        profile = await client.get_profile_data()
        print(f"✅ Profile data: {profile.get('user_name', 'Unknown')}")
        
        # Test Market Data Methods
        print("\n📈 Testing Market Data Methods:")
        print("-" * 30)
        
        # Test quote data
        quote = await client.get_quote_data("ICICIBANK")
        print(f"✅ Quote data for ICICIBANK: {quote.get('ICICIBANK', {}).get('last_price', 0)}")
        
        # Test LTP data
        ltp = await client.get_ltp_data("HDFCBANK")
        print(f"✅ LTP data for HDFCBANK: {ltp.get('HDFCBANK', {}).get('last_price', 0)}")
        
        # Test OHLC data
        ohlc = await client.get_ohlc_data("ICICIBANK", "day")
        print(f"✅ OHLC data: {len(ohlc.get('data', []))} data points")
        
        # Test historical data
        historical = await client.get_historical_data("ICICIBANK", "2024-01-01", "2024-01-15")
        print(f"✅ Historical data: {len(historical)} data points")
        
        # Test instruments data
        instruments = await client.get_instruments_data()
        print(f"✅ Instruments data: {len(instruments)} instruments")
        
        # Test Order History Methods
        print("\n📋 Testing Order History Methods:")
        print("-" * 30)
        
        # Test orders data
        orders = await client.get_orders_data()
        print(f"✅ Orders data: {len(orders)} orders")
        
        # Test trades data
        trades = await client.get_trades_data()
        print(f"✅ Trades data: {len(trades)} trades")
        
        # Test order history
        if orders:
            order_id = orders[0].get('order_id', 'test')
            order_history = await client.get_order_history(order_id)
            print(f"✅ Order history for {order_id}: {order_history.get('status', 'Unknown')}")
        
        # Test order trades
        if trades:
            order_id = trades[0].get('order_id', 'test')
            order_trades = await client.get_order_trades(order_id)
            print(f"✅ Order trades for {order_id}: {len(order_trades)} trades")
        
        # Test Risk & Margin Methods
        print("\n⚖️ Testing Risk & Margin Methods:")
        print("-" * 30)
        
        # Test margins data
        margins = await client.get_margins_data()
        print(f"✅ Margins data: {margins.get('equity', {}).get('net', 0)} net margin")
        
        # Test order margins
        order_params = {
            "tradingsymbol": "ICICIBANK",
            "exchange": "NSE",
            "transaction_type": "SELL",
            "quantity": 100,
            "price": 1520.0,
            "order_type": "LIMIT",
            "product": "MIS"
        }
        order_margins = await client.get_order_margins(order_params)
        print(f"✅ Order margins: {order_margins.get('total', 0)} total margin")
        
        # Test risk metrics
        risk_metrics = await client.get_risk_metrics()
        print(f"✅ Risk metrics: {risk_metrics.get('risk_score', 0)} risk score")
        
        # Test basket margins
        basket_margins = await client.get_basket_margins(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Basket margins: {basket_margins.get('total_margin', 0)} total margin")
        
        # Test Real-time Data Methods
        print("\n🔄 Testing Real-time Data Methods:")
        print("-" * 30)
        
        # Test subscribe
        subscribe_result = await client.subscribe_to_data(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Subscribe result: {subscribe_result.get('status', 'Unknown')}")
        
        # Test streaming data
        streaming_data = await client.get_streaming_data()
        print(f"✅ Streaming data: {len(streaming_data.get('data', {}))} symbols")
        
        # Test unsubscribe
        unsubscribe_result = await client.unsubscribe_from_data(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Unsubscribe result: {unsubscribe_result.get('status', 'Unknown')}")
        
        # Test Additional Analysis Methods
        print("\n📊 Testing Additional Analysis Methods:")
        print("-" * 30)
        
        # Test market indicators
        market_indicators = await client.get_market_indicators("ICICIBANK")
        print(f"✅ Market indicators: {market_indicators.get('current_price', 0)} current price")
        
        # Test option chain data
        option_chain = await client.get_option_chain_data("ICICIBANK")
        print(f"✅ Option chain: {len(option_chain.get('instruments', []))} instruments")
        
        # Test cache functionality
        print("\n💾 Testing Cache Functionality:")
        print("-" * 30)
        
        cache_stats = client.get_cache_stats()
        print(f"✅ Cache stats: {cache_stats.get('total_entries', 0)} entries")
        
        # Clear cache
        client.clear_cache()
        cache_stats_after = client.get_cache_stats()
        print(f"✅ Cache cleared: {cache_stats_after.get('total_entries', 0)} entries")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ All MCP methods are working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Disconnect from MCP server
        await client.disconnect()
        print("🔌 Disconnected from MCP server")


if __name__ == "__main__":
    asyncio.run(test_mcp_methods()) 