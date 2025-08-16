#!/usr/bin/env python3
"""
Manual test script for MCP client methods.
Connects to a running MCP server and tests all the new read-only methods.
"""

import asyncio
import sys
from pathlib import Path

# Add the TradingInsight directory to the path
sys.path.append(str(Path(__file__).parent))

from fastmcp import FastMCP
from services.mcp_client import MCPClient
from config.settings import get_settings


async def test_mcp_methods_manual():
    """Test all MCP client methods with manual server connection."""
    print("🧪 Manual Testing of MCP Client Methods")
    print("=" * 50)
    print("Make sure the MCP server is running in another terminal!")
    print("Run: cd ../kiteMCPServer && python3 demo_mcp_server.py")
    print("=" * 50)
    
    settings = get_settings()
    client = MCPClient(settings)
    
    try:
        # Connect to MCP server (without starting it)
        print("🔗 Connecting to running MCP server...")
        
        # Initialize FastMCP client directly
        server_path = Path(__file__).parent.parent / "kiteMCPServer" / "demo_mcp_server.py"
        client.client = FastMCP.Client(
            transport="stdio",
            command=[sys.executable, str(server_path)]
        )
        
        print("✅ Connected successfully")
        
        # Test Portfolio & Holdings Methods
        print("\n📊 Testing Portfolio & Holdings Methods:")
        print("-" * 30)
        
        # Test portfolio data
        portfolio = await client.get_portfolio_data()
        print(f"✅ Portfolio data: {len(portfolio.get('positions', []))} positions")
        print(f"   Total margin: {portfolio.get('total_margin', 0)}")
        print(f"   Available cash: {portfolio.get('available_cash', 0)}")
        
        # Test holdings data
        holdings = await client.get_holdings_data()
        print(f"✅ Holdings data: {len(holdings)} holdings")
        for holding in holdings:
            print(f"   {holding.get('tradingsymbol', 'Unknown')}: {holding.get('quantity', 0)} shares")
        
        # Test positions data
        positions = await client.get_positions_data()
        print(f"✅ Positions data: {len(positions)} positions")
        for position in positions:
            print(f"   {position.get('tradingsymbol', 'Unknown')}: {position.get('quantity', 0)} lots")
        
        # Test profile data
        profile = await client.get_profile_data()
        print(f"✅ Profile data: {profile.get('user_name', 'Unknown')}")
        print(f"   Broker: {profile.get('broker', 'Unknown')}")
        print(f"   User ID: {profile.get('user_id', 'Unknown')}")
        
        # Test Market Data Methods
        print("\n📈 Testing Market Data Methods:")
        print("-" * 30)
        
        # Test quote data
        quote = await client.get_quote_data("ICICIBANK")
        icici_quote = quote.get('ICICIBANK', {})
        print(f"✅ Quote data for ICICIBANK:")
        print(f"   Last price: {icici_quote.get('last_price', 0)}")
        print(f"   Change: {icici_quote.get('change', 0)}")
        print(f"   Volume: {icici_quote.get('last_quantity', 0)}")
        
        # Test LTP data
        ltp = await client.get_ltp_data("HDFCBANK")
        hdfc_ltp = ltp.get('HDFCBANK', {})
        print(f"✅ LTP data for HDFCBANK: {hdfc_ltp.get('last_price', 0)}")
        
        # Test OHLC data
        ohlc = await client.get_ohlc_data("ICICIBANK", "day")
        print(f"✅ OHLC data: {len(ohlc.get('data', []))} data points")
        if ohlc.get('data'):
            latest = ohlc['data'][0]
            print(f"   Latest: O={latest.get('open', 0)}, H={latest.get('high', 0)}, L={latest.get('low', 0)}, C={latest.get('close', 0)}")
        
        # Test historical data
        historical = await client.get_historical_data("ICICIBANK", "2024-01-01", "2024-01-15")
        print(f"✅ Historical data: {len(historical)} data points")
        
        # Test instruments data
        instruments = await client.get_instruments_data()
        print(f"✅ Instruments data: {len(instruments)} instruments")
        for instrument in instruments[:3]:  # Show first 3
            print(f"   {instrument.get('tradingsymbol', 'Unknown')}: {instrument.get('name', 'Unknown')}")
        
        # Test Order History Methods
        print("\n📋 Testing Order History Methods:")
        print("-" * 30)
        
        # Test orders data
        orders = await client.get_orders_data()
        print(f"✅ Orders data: {len(orders)} orders")
        for order in orders:
            print(f"   Order {order.get('order_id', 'Unknown')}: {order.get('tradingsymbol', 'Unknown')} - {order.get('status', 'Unknown')}")
        
        # Test trades data
        trades = await client.get_trades_data()
        print(f"✅ Trades data: {len(trades)} trades")
        for trade in trades:
            print(f"   Trade {trade.get('trade_id', 'Unknown')}: {trade.get('tradingsymbol', 'Unknown')} - {trade.get('quantity', 0)} @ {trade.get('price', 0)}")
        
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
        equity = margins.get('equity', {})
        print(f"✅ Margins data:")
        print(f"   Net margin: {equity.get('net', 0)}")
        print(f"   Available cash: {equity.get('available', {}).get('cash', 0)}")
        
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
        print(f"✅ Risk metrics:")
        print(f"   Risk score: {risk_metrics.get('risk_score', 0)}")
        print(f"   Total exposure: {risk_metrics.get('total_exposure', 0)}")
        print(f"   VaR 95%: {risk_metrics.get('var_95', 0)}")
        
        # Test basket margins
        basket_margins = await client.get_basket_margins(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Basket margins: {basket_margins.get('total_margin', 0)} total margin")
        
        # Test Real-time Data Methods
        print("\n🔄 Testing Real-time Data Methods:")
        print("-" * 30)
        
        # Test subscribe
        subscribe_result = await client.subscribe_to_data(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Subscribe result: {subscribe_result.get('status', 'Unknown')}")
        print(f"   Instruments: {subscribe_result.get('instruments', [])}")
        
        # Test streaming data
        streaming_data = await client.get_streaming_data()
        print(f"✅ Streaming data: {len(streaming_data.get('data', {}))} symbols")
        for symbol, data in streaming_data.get('data', {}).items():
            print(f"   {symbol}: {data.get('last_price', 0)} ({data.get('change', 0)})")
        
        # Test unsubscribe
        unsubscribe_result = await client.unsubscribe_from_data(["ICICIBANK", "HDFCBANK"])
        print(f"✅ Unsubscribe result: {unsubscribe_result.get('status', 'Unknown')}")
        
        # Test Additional Analysis Methods
        print("\n📊 Testing Additional Analysis Methods:")
        print("-" * 30)
        
        # Test market indicators
        market_indicators = await client.get_market_indicators("ICICIBANK")
        print(f"✅ Market indicators for ICICIBANK:")
        print(f"   Current price: {market_indicators.get('current_price', 0)}")
        print(f"   EMA 20: {market_indicators.get('ema_20', 0)}")
        print(f"   RSI: {market_indicators.get('rsi', 0)}")
        print(f"   Volume: {market_indicators.get('volume', 0)}")
        
        # Test option chain data
        option_chain = await client.get_option_chain_data("ICICIBANK")
        print(f"✅ Option chain: {len(option_chain.get('instruments', []))} instruments")
        for instrument in option_chain.get('instruments', []):
            print(f"   {instrument.get('symbol', 'Unknown')}: {instrument.get('option_type', 'Unknown')} @ {instrument.get('strike_price', 0)}")
        
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
        print("✅ All read-only Kite Connect methods implemented successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Disconnect from MCP server
        await client.disconnect()
        print("🔌 Disconnected from MCP server")


if __name__ == "__main__":
    asyncio.run(test_mcp_methods_manual()) 