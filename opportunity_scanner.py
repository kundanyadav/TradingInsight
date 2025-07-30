"""
opportunity_scanner.py - Scan option chains for new trade opportunities based on custom stock list and thresholds.
"""

from typing import List, Dict, Any
from mcp_client import MCPClient
import asyncio

# Default NIFTY 50 stocks (can be replaced with user custom list)
DEFAULT_STOCK_LIST = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HDFC", "KOTAKBANK", "LT", "SBIN", "AXISBANK",
    "ITC", "HCLTECH", "BHARTIARTL", "ASIANPAINT", "BAJFINANCE", "MARUTI", "SUNPHARMA", "ULTRACEMCO", "TITAN",
    "NESTLEIND", "WIPRO", "POWERGRID", "ONGC", "ADANIPORTS", "HINDUNILVR", "JSWSTEEL", "TATAMOTORS", "COALINDIA",
    "GRASIM", "NTPC", "TATASTEEL", "BPCL", "DIVISLAB", "BRITANNIA", "CIPLA", "EICHERMOT", "HEROMOTOCO", "HDFCLIFE",
    "INDUSINDBK", "M&M", "SHREECEM", "BAJAJFINSV", "BAJAJ-AUTO", "DRREDDY", "UPL", "TECHM", "SBILIFE", "APOLLOHOSP"
]

# Default thresholds (can be customized)
DEFAULT_THRESHOLDS = {
    "min_premium": 10.0,         # Minimum premium to consider
    "max_risk": 0.05,            # Max risk as fraction of margin
    "min_liquidity": 1000,       # Minimum open interest
    "min_time_decay": 0.01,      # Minimum theta (time decay)
}

async def scan_opportunities(
    stock_list: List[str] = None,
    thresholds: Dict[str, float] = None,
    feedback_context: str = None  # New argument for LLM prompt context
) -> List[Dict[str, Any]]:
    """Scan option chains for new trade opportunities, using feedback context for LLM if available."""
    stock_list = stock_list or DEFAULT_STOCK_LIST
    thresholds = thresholds or DEFAULT_THRESHOLDS
    client = MCPClient()
    await client.connect()
    opportunities = []
    # Example: Use feedback_context in LLM prompt (pseudo-code)
    # if feedback_context:
    #     prompt = f"""
    #     You are an options trading assistant. Here is recent user feedback on past recommendations:
    #     {feedback_context}
    #     Based on this, generate new option trade recommendations for the following stocks and thresholds:
    #     ...
    #     """
    #     # Pass prompt to LLM for completion
    #     ...
    for symbol in stock_list:
        option_chain = await client.get_option_chain(symbol)
        if not option_chain or "data" not in option_chain:
            continue
        for option in option_chain["data"]:
            premium = option.get("last_price", 0)
            risk = option.get("risk", 0)
            oi = option.get("open_interest", 0)
            theta = option.get("theta", 0)
            # Apply thresholds
            if (
                premium >= thresholds["min_premium"] and
                risk <= thresholds["max_risk"] and
                oi >= thresholds["min_liquidity"] and
                abs(theta) >= thresholds["min_time_decay"]
            ):
                opportunities.append({
                    "symbol": symbol,
                    "strike": option.get("strike_price"),
                    "type": option.get("option_type"),
                    "expiry": option.get("expiry"),
                    "premium": premium,
                    "risk": risk,
                    "open_interest": oi,
                    "theta": theta,
                    "details": option
                })
    await client.close()
    return opportunities

if __name__ == "__main__":
    # Example usage
    custom_stocks = ["RELIANCE", "TCS", "INFY"]
    custom_thresholds = {"min_premium": 15, "max_risk": 0.04, "min_liquidity": 500, "min_time_decay": 0.02}
    results = asyncio.run(scan_opportunities(custom_stocks, custom_thresholds))
    for opp in results:
        print(opp) 