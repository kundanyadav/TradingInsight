"""
Simple Main Entry Point for kiteMCP Client.
"""

import sys
import asyncio
from analyzer import analyze_portfolio, quick_analysis, risk_assessment


def main():
    """Main entry point for the application."""
    if len(sys.argv) > 1:
        # CLI mode
        command = sys.argv[1]
        
        if command == "full":
            print("🔍 Running full portfolio analysis...")
            result = asyncio.run(analyze_portfolio())
            print_result(result)
            
        elif command == "quick":
            print("⚡ Running quick analysis...")
            result = asyncio.run(quick_analysis())
            print_result(result)
            
        elif command == "risk":
            print("⚠️ Running risk assessment...")
            result = asyncio.run(risk_assessment())
            print_result(result)
            
        elif command == "web":
            print("🌐 Starting web interface...")
            import streamlit.web.cli as stcli
            sys.argv = ["streamlit", "run", "app.py"]
            sys.exit(stcli.main())
            
        else:
            print_usage()
    else:
        print_usage()


def print_result(result):
    """Print analysis results in a formatted way."""
    if result.get("success"):
        print("\n" + "="*50)
        print("📊 ANALYSIS RESULTS")
        print("="*50)
        
        if "portfolio" in result:
            portfolio = result["portfolio"]
            if portfolio and "net" in portfolio:
                positions = portfolio["net"]
                print(f"📋 Total Positions: {len(positions)}")
                
                total_value = sum(pos.get("market_value", 0) for pos in positions)
                total_pnl = sum(pos.get("pnl", 0) for pos in positions)
                print(f"💰 Total Value: ₹{total_value:,.2f}")
                print(f"📈 Total P&L: ₹{total_pnl:,.2f}")
                
                if total_value > 0:
                    roi = (total_pnl / total_value * 100)
                    print(f"🎯 ROI: {roi:.2f}%")
        
        if "risk_analysis" in result:
            risk = result["risk_analysis"]
            print(f"⚠️ Risk Level: {risk.get('risk_percentage', 0):.2f}%")
        
        if "recommendations" in result:
            print("\n💡 RECOMMENDATIONS:")
            print("-" * 30)
            print(result["recommendations"])
        
        if "action_plan" in result:
            plan = result["action_plan"]
            if plan.get("immediate_actions"):
                print("\n🚨 IMMEDIATE ACTIONS:")
                for action in plan["immediate_actions"]:
                    print(f"  • {action.get('action', '')}: {action.get('reason', '')}")
        
        print("\n" + "="*50)
        
    else:
        print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")


def print_usage():
    """Print usage instructions."""
    print("""
📈 kiteMCP - AI Trading Assistant

Usage:
  python main.py full      # Full portfolio analysis
  python main.py quick     # Quick portfolio overview  
  python main.py risk      # Risk assessment only
  python main.py web       # Start web interface

Examples:
  python main.py full      # Complete analysis with recommendations
  python main.py quick     # Fast overview of positions
  python main.py risk      # Focus on risk assessment
  python main.py web       # Launch Streamlit web UI
""")


if __name__ == "__main__":
    main() 