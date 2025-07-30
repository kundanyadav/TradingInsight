"""
risk.py - Margin utilization alerts, stress testing, and VaR calculation for the MCPClient app.
"""

from typing import List, Dict, Any
import numpy as np

# Dummy margin utilization alert

def margin_utilization_alert(portfolio: Dict[str, Any], threshold: float = 0.7) -> Dict[str, Any]:
    """Alert if margin utilization exceeds threshold (default 70%)."""
    used = portfolio.get("margin_used", 0)
    total = portfolio.get("margin_total", 1)
    utilization = used / total if total else 0
    alert = utilization > threshold
    return {
        "utilization": utilization,
        "threshold": threshold,
        "alert": alert,
        "message": f"Margin utilization is {'HIGH' if alert else 'OK'}: {utilization:.2%}"
    }

# Dummy stress test: simulate a % drop in all positions

def stress_test(portfolio: Dict[str, Any], drop_pct: float = 0.05) -> Dict[str, Any]:
    """Simulate a market drop and show impact on portfolio value and P&L."""
    positions = portfolio.get("net", [])
    simulated = []
    total_pnl = 0
    for pos in positions:
        mv = pos.get("market_value", 0)
        pnl = pos.get("pnl", 0)
        new_mv = mv * (1 - drop_pct)
        new_pnl = pnl - (mv - new_mv)
        simulated.append({**pos, "simulated_market_value": new_mv, "simulated_pnl": new_pnl})
        total_pnl += new_pnl
    return {
        "drop_pct": drop_pct,
        "simulated_positions": simulated,
        "total_simulated_pnl": total_pnl
    }

# Dummy Value at Risk (VaR) calculation

def calculate_var(portfolio: Dict[str, Any], confidence: float = 0.95) -> Dict[str, Any]:
    """Estimate maximum expected loss (VaR) for a given confidence level (dummy)."""
    positions = portfolio.get("net", [])
    # For demo, VaR = 2 * stddev of P&L (not a real VaR method)
    pnls = [pos.get("pnl", 0) for pos in positions]
    if not pnls:
        return {"VaR": 0, "confidence": confidence}
    var = 2 * np.std(pnls)
    return {"VaR": var, "confidence": confidence}

if __name__ == "__main__":
    dummy_portfolio = {
        "margin_used": 70000,
        "margin_total": 100000,
        "net": [
            {"tradingsymbol": "RELIANCE", "market_value": 100000, "pnl": 5000},
            {"tradingsymbol": "TCS", "market_value": 80000, "pnl": -2000},
        ]
    }
    print(margin_utilization_alert(dummy_portfolio))
    print(stress_test(dummy_portfolio, 0.05))
    print(calculate_var(dummy_portfolio, 0.95)) 