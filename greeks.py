"""
greeks.py - Calculate and summarize option Greeks for portfolio and positions.
"""

from typing import List, Dict, Any
import numpy as np

# Dummy Black-Scholes Greeks calculation for demonstration
# In production, use real market data and a robust options library

def calculate_greeks(option: Dict[str, Any]) -> Dict[str, float]:
    """Calculate option Greeks for a single position (dummy implementation)."""
    # Required fields: spot, strike, expiry, volatility, rate, option_type
    # For now, use random values for demonstration
    np.random.seed(hash(option.get("tradingsymbol", "")) % 2**32)
    return {
        "delta": np.random.uniform(-1, 1),
        "gamma": np.random.uniform(0, 0.2),
        "theta": np.random.uniform(-0.1, 0),
        "vega": np.random.uniform(0, 1),
    }

def summarize_portfolio_greeks(positions: List[Dict[str, Any]]) -> Dict[str, float]:
    """Summarize Greeks across all positions in the portfolio."""
    totals = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
    for pos in positions:
        greeks = calculate_greeks(pos)
        for k in totals:
            totals[k] += greeks[k]
    return totals

def per_position_greeks(positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return Greeks for each position."""
    result = []
    for pos in positions:
        greeks = calculate_greeks(pos)
        pos_greeks = pos.copy()
        pos_greeks.update(greeks)
        result.append(pos_greeks)
    return result

if __name__ == "__main__":
    # Example usage
    dummy_positions = [
        {"tradingsymbol": "RELIANCE", "quantity": 75},
        {"tradingsymbol": "TCS", "quantity": -50},
    ]
    print("Portfolio Greeks:", summarize_portfolio_greeks(dummy_positions))
    print("Per-position Greeks:", per_position_greeks(dummy_positions)) 