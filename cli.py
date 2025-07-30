"""
Command Line Interface for kiteMCP Client.
"""

import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from workflows.portfolio_analyzer import PortfolioAnalyzer
from models.mcp_client import MCPClient
from models.llm_client import LLMClient
from config.settings import settings


class CLIApp:
    """Command Line Interface for the kiteMCP client."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.console = Console()
        self.analyzer = PortfolioAnalyzer()
        self.mcp_client = None
        self.llm_client = None
    
    async def initialize(self):
        """Initialize the application components."""
        try:
            self.mcp_client = await MCPClient().connect()
            self.llm_client = LLMClient()
            await self.analyzer.initialize()
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to initialize: {e}[/red]")
            return False
    
    def print_header(self):
        """Print the application header."""
        header = Panel.fit(
            "[bold blue]📈 kiteMCP - AI Trading Assistant[/bold blue]\n"
            "[dim]Intelligent Portfolio Analysis and Trading Recommendations[/dim]",
            border_style="blue"
        )
        self.console.print(header)
    
    def print_portfolio_summary(self, portfolio_data: Dict):
        """Print portfolio summary."""
        if not portfolio_data or "net" not in portfolio_data:
            self.console.print("[yellow]No portfolio data available[/yellow]")
            return
        
        positions = portfolio_data["net"]
        total_positions = len(positions)
        total_value = sum(pos.get("market_value", 0) for pos in positions)
        total_pnl = sum(pos.get("pnl", 0) for pos in positions)
        roi = (total_pnl / total_value * 100) if total_value > 0 else 0
        
        # Create summary table
        table = Table(title="📊 Portfolio Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Positions", str(total_positions))
        table.add_row("Total Value", f"₹{total_value:,.2f}")
        table.add_row("Total P&L", f"₹{total_pnl:,.2f}")
        table.add_row("ROI", f"{roi:.2f}%")
        
        self.console.print(table)
    
    def print_portfolio_positions(self, portfolio_data: Dict):
        """Print portfolio positions."""
        if not portfolio_data or "net" not in portfolio_data:
            self.console.print("[yellow]No positions found[/yellow]")
            return
        
        positions = portfolio_data["net"]
        
        if not positions:
            self.console.print("[yellow]No positions found[/yellow]")
            return
        
        # Create positions table
        table = Table(title="📋 Current Positions")
        table.add_column("Symbol", style="cyan")
        table.add_column("Quantity", style="blue")
        table.add_column("Market Value", style="green")
        table.add_column("P&L", style="yellow")
        table.add_column("Avg Price", style="magenta")
        
        for position in positions:
            symbol = position.get("tradingsymbol", "")
            quantity = position.get("quantity", 0)
            market_value = position.get("market_value", 0)
            pnl = position.get("pnl", 0)
            avg_price = position.get("average_price", 0)
            
            # Color code P&L
            pnl_color = "green" if pnl >= 0 else "red"
            
            table.add_row(
                symbol,
                str(quantity),
                f"₹{market_value:,.2f}",
                f"[{pnl_color}]₹{pnl:,.2f}[/{pnl_color}]",
                f"₹{avg_price:,.2f}"
            )
        
        self.console.print(table)
    
    def print_risk_analysis(self, risk_analysis: Dict):
        """Print risk analysis."""
        if not risk_analysis:
            self.console.print("[yellow]No risk analysis data available[/yellow]")
            return
        
        risk_percentage = risk_analysis.get("risk_percentage", 0)
        total_value = risk_analysis.get("total_value", 0)
        risk_exposure = risk_analysis.get("risk_exposure", 0)
        max_allowed_risk = risk_analysis.get("max_allowed_risk", 10)
        
        # Determine risk level
        if risk_percentage > max_allowed_risk:
            risk_level = "[red]HIGH[/red]"
        elif risk_percentage > max_allowed_risk * 0.7:
            risk_level = "[yellow]MEDIUM[/yellow]"
        else:
            risk_level = "[green]LOW[/green]"
        
        # Create risk table
        table = Table(title="⚠️ Risk Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Risk Level", risk_level)
        table.add_row("Risk Exposure", f"{risk_percentage:.2f}%")
        table.add_row("Total Portfolio Value", f"₹{total_value:,.2f}")
        table.add_row("Risk Exposure Amount", f"₹{risk_exposure:,.2f}")
        table.add_row("Max Allowed Risk", f"{max_allowed_risk:.2f}%")
        
        self.console.print(table)
    
    def print_recommendations(self, recommendations: str):
        """Print trading recommendations."""
        if not recommendations:
            self.console.print("[yellow]No recommendations available[/yellow]")
            return
        
        panel = Panel(
            recommendations,
            title="💡 Trading Recommendations",
            border_style="blue"
        )
        self.console.print(panel)
    
    def print_action_plan(self, action_plan: Dict):
        """Print action plan."""
        if not action_plan:
            self.console.print("[yellow]No action plan available[/yellow]")
            return
        
        # Immediate actions
        if action_plan.get("immediate_actions"):
            self.console.print("\n[bold red]🚨 Immediate Actions:[/bold red]")
            for action in action_plan["immediate_actions"]:
                self.console.print(f"  • {action.get('action', '')}: {action.get('reason', '')}")
        
        # Short-term actions
        if action_plan.get("short_term_actions"):
            self.console.print("\n[bold yellow]📅 Short-term Actions:[/bold yellow]")
            for action in action_plan["short_term_actions"]:
                self.console.print(f"  • {action}")
        
        # Risk management
        if action_plan.get("risk_management"):
            self.console.print("\n[bold blue]🛡️ Risk Management:[/bold blue]")
            for action in action_plan["risk_management"]:
                self.console.print(f"  • {action.get('action', '')}: {action.get('target_reduction', '')}")
    
    def print_roi_projection(self, roi_projection: Dict):
        """Print ROI projections."""
        if not roi_projection:
            self.console.print("[yellow]No ROI projections available[/yellow]")
            return
        
        current_roi = roi_projection.get("current_roi", 0)
        projected_1m = roi_projection.get("projected_roi_1m", 0)
        projected_3m = roi_projection.get("projected_roi_3m", 0)
        projected_6m = roi_projection.get("projected_roi_6m", 0)
        
        # Create ROI table
        table = Table(title="📈 ROI Projections")
        table.add_column("Timeframe", style="cyan")
        table.add_column("ROI (%)", style="green")
        table.add_column("Change", style="yellow")
        
        table.add_row("Current", f"{current_roi:.2f}%", "-")
        table.add_row("1 Month", f"{projected_1m:.2f}%", f"+{projected_1m - current_roi:.2f}%")
        table.add_row("3 Months", f"{projected_3m:.2f}%", f"+{projected_3m - current_roi:.2f}%")
        table.add_row("6 Months", f"{projected_6m:.2f}%", f"+{projected_6m - current_roi:.2f}%")
        
        self.console.print(table)
    
    async def run_full_analysis(self):
        """Run complete portfolio analysis."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Analyzing portfolio...", total=None)
            
            try:
                result = await self.analyzer.run_analysis()
                progress.update(task, description="Analysis completed!")
                
                if result["success"]:
                    report = result["final_report"]
                    
                    # Print all sections
                    self.print_portfolio_summary(report.get("portfolio_data", {}))
                    self.print_portfolio_positions(report.get("portfolio_data", {}))
                    self.print_risk_analysis(report.get("risk_analysis", {}))
                    self.print_recommendations(report.get("recommendations", ""))
                    self.print_action_plan(report.get("action_plan", {}))
                    self.print_roi_projection(report.get("roi_projection", {}))
                    
                    return report
                else:
                    self.console.print(f"[red]Analysis failed: {result.get('error', 'Unknown error')}[/red]")
                    return None
                    
            except Exception as e:
                self.console.print(f"[red]Analysis failed: {e}[/red]")
                return None
    
    async def run_quick_analysis(self):
        """Run quick portfolio overview."""
        try:
            # Get basic portfolio data
            portfolio = await self.mcp_client.get_portfolio()
            self.print_portfolio_summary(portfolio)
            self.print_portfolio_positions(portfolio)
            
            # Get market sentiment
            sentiment = await self.mcp_client.get_sentiment()
            self.console.print(f"\n[bold]Market Sentiment:[/bold] {sentiment.get('sentiment', 'Unknown')}")
            
        except Exception as e:
            self.console.print(f"[red]Quick analysis failed: {e}[/red]")
    
    async def run_risk_assessment(self):
        """Run focused risk assessment."""
        try:
            # Get portfolio data
            portfolio = await self.mcp_client.get_portfolio()
            
            # Calculate risk metrics
            total_value = 0
            risk_exposure = 0
            
            if "net" in portfolio:
                for position in portfolio["net"]:
                    value = position.get("market_value", 0)
                    total_value += value
                    
                    if position.get("quantity", 0) < 0:  # Short position
                        risk_exposure += value * 2
                    else:
                        risk_exposure += value
            
            risk_percentage = (risk_exposure / total_value * 100) if total_value > 0 else 0
            
            risk_analysis = {
                "total_value": total_value,
                "risk_exposure": risk_exposure,
                "risk_percentage": risk_percentage,
                "max_allowed_risk": settings.max_portfolio_risk * 100
            }
            
            self.print_risk_analysis(risk_analysis)
            
        except Exception as e:
            self.console.print(f"[red]Risk assessment failed: {e}[/red]")
    
    def save_report(self, report: Dict, filename: str = None):
        """Save analysis report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            self.console.print(f"[green]Report saved to: {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Failed to save report: {e}[/red]")
    
    def run(self, args):
        """Run the CLI application based on arguments."""
        # Initialize
        if not asyncio.run(self.initialize()):
            return
        
        self.print_header()
        
        try:
            if args.command == "full":
                # Full analysis
                report = asyncio.run(self.run_full_analysis())
                if report and args.save:
                    self.save_report(report, args.output)
            
            elif args.command == "quick":
                # Quick analysis
                asyncio.run(self.run_quick_analysis())
            
            elif args.command == "risk":
                # Risk assessment
                asyncio.run(self.run_risk_assessment())
            
            elif args.command == "positions":
                # Show positions only
                portfolio = asyncio.run(self.mcp_client.get_portfolio())
                self.print_portfolio_positions(portfolio)
            
            elif args.command == "sentiment":
                # Market sentiment
                sentiment = asyncio.run(self.mcp_client.get_sentiment())
                self.console.print(f"Market Sentiment: {sentiment}")
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            if self.mcp_client:
                asyncio.run(self.mcp_client.close())


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="kiteMCP - AI Trading Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py full                    # Run full portfolio analysis
  python cli.py quick                   # Run quick portfolio overview
  python cli.py risk                    # Run risk assessment only
  python cli.py positions               # Show current positions
  python cli.py sentiment               # Show market sentiment
  python cli.py full --save --output report.json  # Save analysis report
        """
    )
    
    parser.add_argument(
        "command",
        choices=["full", "quick", "risk", "positions", "sentiment"],
        help="Analysis command to run"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save analysis report to file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output filename for saved report"
    )
    
    args = parser.parse_args()
    
    # Create and run CLI app
    app = CLIApp()
    app.run(args)


if __name__ == "__main__":
    main() 