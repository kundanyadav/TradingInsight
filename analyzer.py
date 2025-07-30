"""
Main Analyzer - Orchestrates all portfolio analysis logic.
"""

import asyncio
from typing import Dict, Any
from mcp_client import MCPClient
from llm_client import LLMClient
from config import get_config
import streamlit as st
from logging_utils import analyze_feedback_patterns


class Analyzer:
    """Main analyzer that orchestrates portfolio analysis."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.config = get_config()
        self.mcp_client = None
        self.llm_client = None
    
    async def initialize(self):
        """Initialize MCP and LLM clients."""
        try:
            self.mcp_client = await MCPClient().connect()
            self.llm_client = LLMClient()
            return True
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    async def get_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data from MCP server."""
        try:
            portfolio = await self.mcp_client.get_portfolio()
            return portfolio
        except Exception as e:
            print(f"❌ Failed to get portfolio: {e}")
            return {}
    
    async def get_market_data(self, symbol: str = "NIFTY") -> Dict[str, Any]:
        """Get market data for a symbol."""
        try:
            indicators = await self.mcp_client.get_market_indicators(symbol)
            sentiment = await self.mcp_client.get_sentiment(symbol)
            quote = await self.mcp_client.get_quote(symbol)
            
            return {
                "indicators": indicators,
                "sentiment": sentiment,
                "quote": quote
            }
        except Exception as e:
            print(f"❌ Failed to get market data: {e}")
            return {}
    
    async def analyze_risk(self, portfolio: Dict) -> Dict[str, Any]:
        """Analyze portfolio risk."""
        try:
            total_value = 0
            risk_exposure = 0
            
            if "net" in portfolio:
                for position in portfolio["net"]:
                    value = position.get("market_value", 0)
                    total_value += value
                    
                    # Simple risk calculation
                    if position.get("quantity", 0) < 0:  # Short position
                        risk_exposure += value * 2  # Higher risk for shorts
                    else:
                        risk_exposure += value
            
            risk_percentage = (risk_exposure / total_value * 100) if total_value > 0 else 0
            
            return {
                "total_value": total_value,
                "risk_exposure": risk_exposure,
                "risk_percentage": risk_percentage,
                "max_allowed_risk": self.config["max_portfolio_risk"] * 100
            }
        except Exception as e:
            print(f"❌ Failed to analyze risk: {e}")
            return {}
    
    async def generate_recommendations(self, portfolio: Dict, market_data: Dict, risk_analysis: Dict) -> str:
        """Generate trading recommendations using LLM."""
        try:
            # Build analysis prompt
            prompt = f"""
Analyze this portfolio and provide trading recommendations:

PORTFOLIO DATA:
{portfolio}

MARKET DATA:
{market_data}

RISK ANALYSIS:
{risk_analysis}

Provide specific recommendations for:
1. Positions to close or adjust
2. New positions to consider
3. Risk management strategies
4. Entry/exit points

Format your response clearly with actionable advice.
"""
            
            recommendations = await self.llm_client.generate_response(prompt)
            return recommendations
            
        except Exception as e:
            print(f"❌ Failed to generate recommendations: {e}")
            return "Unable to generate recommendations due to an error."
    
    async def create_action_plan(self, portfolio: Dict, risk_analysis: Dict, recommendations: str) -> Dict[str, Any]:
        """Create action plan based on analysis."""
        try:
            action_plan = {
                "immediate_actions": [],
                "short_term_actions": [],
                "risk_management": []
            }
            
            # Add risk management actions if needed
            if risk_analysis.get("risk_percentage", 0) > risk_analysis.get("max_allowed_risk", 10):
                action_plan["risk_management"].append({
                    "action": "reduce_risk_exposure",
                    "target_reduction": risk_analysis["risk_percentage"] - risk_analysis["max_allowed_risk"],
                    "priority": "high"
                })
            
            # Add position-specific actions
            if "net" in portfolio:
                for position in portfolio["net"]:
                    pnl = position.get("pnl", 0)
                    if pnl < 0:  # Loss-making position
                        action_plan["immediate_actions"].append({
                            "action": "close_position",
                            "symbol": position.get("tradingsymbol", ""),
                            "reason": "Loss-making position",
                            "priority": "high"
                        })
            
            return action_plan
            
        except Exception as e:
            print(f"❌ Failed to create action plan: {e}")
            return {}
    
    async def analyze_portfolio(self) -> Dict[str, Any]:
        """Run complete portfolio analysis."""
        try:
            # Initialize
            if not await self.initialize():
                return {"success": False, "error": "Failed to initialize"}
            
            print("📊 Gathering portfolio data...")
            portfolio = await self.get_portfolio_data()
            
            print("📈 Gathering market data...")
            market_data = await self.get_market_data()
            
            print("⚠️ Analyzing risk...")
            risk_analysis = await self.analyze_risk(portfolio)
            
            print("🤖 Generating recommendations...")
            recommendations = await self.generate_recommendations(portfolio, market_data, risk_analysis)
            
            print("📋 Creating action plan...")
            action_plan = await self.create_action_plan(portfolio, risk_analysis, recommendations)
            
            return {
                "success": True,
                "portfolio": portfolio,
                "market_data": market_data,
                "risk_analysis": risk_analysis,
                "recommendations": recommendations,
                "action_plan": action_plan
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if self.mcp_client:
                await self.mcp_client.close()
    
    async def quick_analysis(self) -> Dict[str, Any]:
        """Run quick portfolio overview."""
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to initialize"}
            
            portfolio = await self.get_portfolio_data()
            market_data = await self.get_market_data()
            
            return {
                "success": True,
                "portfolio": portfolio,
                "market_data": market_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if self.mcp_client:
                await self.mcp_client.close()
    
    async def risk_assessment(self) -> Dict[str, Any]:
        """Run focused risk assessment."""
        try:
            if not await self.initialize():
                return {"success": False, "error": "Failed to initialize"}
            
            portfolio = await self.get_portfolio_data()
            risk_analysis = await self.analyze_risk(portfolio)
            
            return {
                "success": True,
                "portfolio": portfolio,
                "risk_analysis": risk_analysis
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if self.mcp_client:
                await self.mcp_client.close()

    async def analyze_news_sentiment_for_stocks(self, scan_list) -> dict:
        """Analyze news sentiment for each stock in scan_list using the LLM."""
        sentiment_summary = {}
        from news import aggregate_news_and_macro
        news_india = aggregate_news_and_macro('India')
        news_usa = aggregate_news_and_macro('USA')
        all_headlines = []
        for country_news in [news_india, news_usa]:
            for article in country_news.get('news', []):
                if article.get('title'):
                    all_headlines.append(article['title'])
        # User-submitted news
        import streamlit as st
        user_links = st.session_state.get('user_news_links', [])
        # For each stock, gather relevant headlines
        for symbol in scan_list:
            stock_headlines = [h for h in all_headlines if symbol in h.upper()]
            # Optionally, fetch more news for the symbol
            # Compose prompt for LLM
            prompt = f"""
You are a financial news sentiment analyst.
Analyze the following news headlines and user-submitted links for the stock {symbol}:

NEWS HEADLINES:
{stock_headlines}

USER LINKS:
{user_links}

Classify the overall sentiment for {symbol} as Bullish, Bearish, or Neutral. List the key drivers (news, events, macro factors) and provide a 1-2 sentence summary of the sentiment and its likely impact on the stock.
"""
            sentiment = await self.llm_client.generate_response(prompt)
            sentiment_summary[symbol] = sentiment
        return sentiment_summary

    SECTOR_MAP = {
        # Banking
        "HDFCBANK": "Banking", "ICICIBANK": "Banking", "KOTAKBANK": "Banking", "SBIN": "Banking", "AXISBANK": "Banking", "INDUSINDBK": "Banking", "BANKBARODA": "Banking", "PNB": "Banking",
        # PSU
        "SBIN": "PSU", "ONGC": "PSU", "COALINDIA": "PSU", "NTPC": "PSU", "BPCL": "PSU", "POWERGRID": "PSU", "GAIL": "PSU",
        # Auto
        "MARUTI": "Auto", "TATAMOTORS": "Auto", "EICHERMOT": "Auto", "HEROMOTOCO": "Auto", "M&M": "Auto", "BAJAJ-AUTO": "Auto",
        # NBFC
        "BAJFINANCE": "NBFC", "BAJAJFINSV": "NBFC", "HDFCLIFE": "NBFC", "SBILIFE": "NBFC",
        # IT
        "TCS": "IT", "INFY": "IT", "HCLTECH": "IT", "WIPRO": "IT", "TECHM": "IT",
        # Add more as needed
    }

    async def analyze_sector_sentiment(self, scan_list) -> dict:
        """Analyze news sentiment for each sector using the LLM."""
        from news import aggregate_news_and_macro
        news_india = aggregate_news_and_macro('India')
        news_usa = aggregate_news_and_macro('USA')
        all_headlines = []
        for country_news in [news_india, news_usa]:
            for article in country_news.get('news', []):
                if article.get('title'):
                    all_headlines.append(article['title'])
        # User-submitted news
        import streamlit as st
        user_links = st.session_state.get('user_news_links', [])
        # Aggregate stocks by sector
        sector_stocks = {}
        for symbol in scan_list:
            sector = self.SECTOR_MAP.get(symbol, "Other")
            sector_stocks.setdefault(sector, []).append(symbol)
        sentiment_summary = {}
        for sector, stocks in sector_stocks.items():
            sector_headlines = [h for h in all_headlines if any(s in h.upper() for s in stocks)]
            prompt = f"""
You are a financial news sentiment analyst.
Analyze the following news headlines and user-submitted links for the {sector} sector (stocks: {', '.join(stocks)}):

NEWS HEADLINES:
{sector_headlines}

USER LINKS:
{user_links}

Classify the overall sentiment for the {sector} sector as Bullish, Bearish, or Neutral. List the key drivers (news, events, macro factors) and provide a 1-2 sentence summary of the sentiment and its likely impact on the sector.
"""
            sentiment = await self.llm_client.generate_response(prompt)
            sentiment_summary[sector] = sentiment
        return sentiment_summary

    async def get_full_context(self, scan_list=None, feedback_context=None) -> Dict[str, Any]:
        """Gather all context for LLM recommendations."""
        context = {}
        # Portfolio
        portfolio = await self.get_portfolio_data()
        context['portfolio'] = portfolio
        # Portfolio Greeks
        from greeks import summarize_portfolio_greeks, per_position_greeks
        if 'net' in portfolio:
            context['portfolio_greeks'] = summarize_portfolio_greeks(portfolio['net'])
            context['per_position_greeks'] = per_position_greeks(portfolio['net'])
        # Margin
        context['margin_used'] = portfolio.get('margin_used')
        context['margin_total'] = portfolio.get('margin_total')
        # News sentiment (India & USA)
        from news import aggregate_news_and_macro
        context['news_india'] = aggregate_news_and_macro('India')
        context['news_usa'] = aggregate_news_and_macro('USA')
        # User-submitted news
        import streamlit as st
        context['user_news_links'] = st.session_state.get('user_news_links', [])
        # Technical indicators & option chains for scan list
        context['technical_indicators'] = {}
        context['option_chains'] = {}
        scan_list = scan_list or []
        for symbol in scan_list:
            context['technical_indicators'][symbol] = await self.mcp_client.get_market_indicators(symbol)
            context['option_chains'][symbol] = await self.mcp_client.get_option_chain(symbol)
        # News sentiment for each stock
        context['news_sentiment'] = await self.analyze_news_sentiment_for_stocks(scan_list)
        # Sector-wise sentiment
        context['sector_sentiment'] = await self.analyze_sector_sentiment(scan_list)
        # Recent feedback
        context['recent_feedback'] = feedback_context
        # Performance of underlying stocks (quotes)
        context['quotes'] = {symbol: await self.mcp_client.get_quote(symbol) for symbol in scan_list}
        return context

    async def generate_full_context_recommendations(self, scan_list, feedback_context) -> str:
        """Generate recommendations using full context."""
        # Analyze feedback patterns and summarize
        feedback_patterns = analyze_feedback_patterns(50)
        def summarize_patterns(patterns):
            lines = []
            # Symbol preferences
            if patterns['symbol_stats']:
                top_accept = sorted(patterns['symbol_stats'].items(), key=lambda x: -x[1]['accepted'])[:3]
                top_reject = sorted(patterns['symbol_stats'].items(), key=lambda x: -x[1]['rejected'])[:3]
                if top_accept:
                    lines.append("User often accepts recommendations for: " + ", ".join(f"{s} ({c['accepted']})" for s, c in top_accept if c['accepted'] > 0))
                if top_reject:
                    lines.append("User often rejects: " + ", ".join(f"{s} ({c['rejected']})" for s, c in top_reject if c['rejected'] > 0))
            # Option type
            if patterns['option_type_stats']:
                top_accept = sorted(patterns['option_type_stats'].items(), key=lambda x: -x[1]['accepted'])[:2]
                top_reject = sorted(patterns['option_type_stats'].items(), key=lambda x: -x[1]['rejected'])[:2]
                if top_accept:
                    lines.append("Preferred option types: " + ", ".join(f"{t} ({c['accepted']})" for t, c in top_accept if c['accepted'] > 0))
                if top_reject:
                    lines.append("Rejected option types: " + ", ".join(f"{t} ({c['rejected']})" for t, c in top_reject if c['rejected'] > 0))
            # Risk
            if patterns['avg_risk']['accepted'] is not None:
                lines.append(f"Average risk for accepted: {patterns['avg_risk']['accepted']:.2f}")
            if patterns['avg_risk']['rejected'] is not None:
                lines.append(f"Average risk for rejected: {patterns['avg_risk']['rejected']:.2f}")
            # Rationale keywords
            if patterns['rationale_keywords']:
                top_accept = sorted(patterns['rationale_keywords'].items(), key=lambda x: -x[1]['accepted'])[:3]
                top_reject = sorted(patterns['rationale_keywords'].items(), key=lambda x: -x[1]['rejected'])[:3]
                if top_accept:
                    lines.append("Common accepted rationale: " + ", ".join(f"{w} ({c['accepted']})" for w, c in top_accept if c['accepted'] > 0))
                if top_reject:
                    lines.append("Common rejected rationale: " + ", ".join(f"{w} ({c['rejected']})" for w, c in top_reject if c['rejected'] > 0))
            if not lines:
                return "No strong user preferences detected yet."
            return "\n".join(lines)
        user_pref_summary = summarize_patterns(feedback_patterns)
        context = await self.get_full_context(scan_list, feedback_context)
        prompt = f"""
You are an expert options trading assistant.

USER PREFERENCES (from recent feedback):
{user_pref_summary}

Here is the latest news and sentiment (India):
{context['news_india']}

Here is the latest news and sentiment (USA):
{context['news_usa']}

User-submitted news links:
{context['user_news_links']}

News sentiment for each stock in the scan list:
{context['news_sentiment']}

Sector-wise sentiment:
{context['sector_sentiment']}

Current portfolio positions:
{context['portfolio']}

Portfolio-level Greeks:
{context['portfolio_greeks']}

Per-position Greeks:
{context['per_position_greeks']}

Margin used: {context['margin_used']} / {context['margin_total']}

Technical indicators for tracked stocks:
{context['technical_indicators']}

Option chains for tracked stocks:
{context['option_chains']}

Quotes for underlying stocks:
{context['quotes']}

Recent user feedback on recommendations:
{context['recent_feedback']}

Based on all of the above, generate new option trade recommendations. For each recommendation, provide:
"""
        recommendations = await self.llm_client.generate_response(prompt)
        return recommendations


# Convenience functions
async def analyze_portfolio() -> Dict[str, Any]:
    """Run complete portfolio analysis."""
    analyzer = Analyzer()
    return await analyzer.analyze_portfolio()


async def quick_analysis() -> Dict[str, Any]:
    """Run quick portfolio overview."""
    analyzer = Analyzer()
    return await analyzer.quick_analysis()


async def risk_assessment() -> Dict[str, Any]:
    """Run focused risk assessment."""
    analyzer = Analyzer()
    return await analyzer.risk_assessment()


if __name__ == "__main__":
    # Test the analyzer
    result = asyncio.run(analyze_portfolio())
    print(result) 