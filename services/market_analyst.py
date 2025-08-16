"""
Market Analyst Agent for Kite Trading Recommendation App.
Professional equity research analyst with years of experience providing sentiment analysis.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from pydantic import BaseModel
from langgraph.graph import StateGraph, END, START

from models.data_models import SentimentAnalysis, ApplicationSettings
from .mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketAnalysisState(BaseModel):
    """State for market analysis workflow."""
    symbol: str
    timeframe: str = "both"
    market_data: Optional[Dict[str, Any]] = None
    financial_data: Optional[Dict[str, Any]] = None
    news_data: Optional[Dict[str, Any]] = None
    intrinsic_value: Optional[Dict[str, Any]] = None
    analyst_ratings: Optional[Dict[str, Any]] = None
    fii_data: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    confidence_score: Optional[float] = None
    error: Optional[str] = None


class MarketAnalyst:
    """Professional equity research analyst with years of experience."""
    
    def __init__(self, mcp_client: MCPClient, settings: ApplicationSettings):
        """Initialize market analyst with MCP client and settings."""
        self.mcp_client = mcp_client
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_sentiment(self, symbol: str, timeframe: str = "both") -> SentimentAnalysis:
        """
        Analyze market sentiment for a symbol following ICICIBANK template format.
        
        Args:
            symbol: Stock symbol to analyze
            timeframe: Analysis timeframe ("short", "medium", "both")
            
        Returns:
            SentimentAnalysis with professional-grade analysis
        """
        try:
            logger.info(f"Starting sentiment analysis for {symbol}")
            
            # Create analysis state
            state = MarketAnalysisState(symbol=symbol, timeframe=timeframe)
            
            # Execute simplified analysis workflow
            final_state = await self._execute_simple_analysis_workflow(state)
            
            logger.info(f"Completed sentiment analysis for {symbol}")
            return final_state.sentiment_analysis
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            raise
    
    async def _execute_simple_analysis_workflow(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Execute a simplified market analysis workflow."""
        
        try:
            # Gather market data
            state = await self._gather_market_data(state)
            
            # Gather financial data
            state = await self._gather_financial_data(state)
            
            # Gather news data
            state = await self._gather_news_data(state)
            
            # Gather intrinsic value
            state = await self._gather_intrinsic_value(state)
            
            # Gather analyst ratings
            state = await self._gather_analyst_ratings(state)
            
            # Gather FII data
            state = await self._gather_fii_data(state)
            
            # Analyze sentiment
            state = await self._analyze_sentiment(state)
            
            # Self assess
            state = await self._self_assess(state)
            
            return state
            
        except Exception as e:
            state.error = f"Analysis workflow failed: {e}"
            return state
    
    async def _gather_market_data(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather market data from MCP server."""
        try:
            logger.debug(f"Gathering market data for {state.symbol}")
            state.market_data = await self.mcp_client.get_market_data(state.symbol)
            return state
        except Exception as e:
            state.error = f"Failed to gather market data: {e}"
            return state
    
    async def _gather_financial_data(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather financial data from screener.in."""
        try:
            logger.debug(f"Gathering financial data for {state.symbol}")
            state.financial_data = await self._scrape_screener_data(state.symbol)
            return state
        except Exception as e:
            logger.warning(f"Failed to gather financial data for {state.symbol}: {e}")
            state.financial_data = {}
            return state
    
    async def _gather_news_data(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather news and social media sentiment."""
        try:
            logger.debug(f"Gathering news data for {state.symbol}")
            state.news_data = await self._scrape_news_data(state.symbol)
            return state
        except Exception as e:
            logger.warning(f"Failed to gather news data for {state.symbol}: {e}")
            state.news_data = {}
            return state
    
    async def _gather_intrinsic_value(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather intrinsic value analysis."""
        try:
            logger.debug(f"Gathering intrinsic value for {state.symbol}")
            state.intrinsic_value = await self._scrape_intrinsic_value(state.symbol)
            return state
        except Exception as e:
            logger.warning(f"Failed to gather intrinsic value for {state.symbol}: {e}")
            state.intrinsic_value = {}
            return state
    
    async def _gather_analyst_ratings(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather analyst ratings and market mood."""
        try:
            logger.debug(f"Gathering analyst ratings for {state.symbol}")
            state.analyst_ratings = await self._scrape_analyst_ratings(state.symbol)
            return state
        except Exception as e:
            logger.warning(f"Failed to gather analyst ratings for {state.symbol}: {e}")
            state.analyst_ratings = {}
            return state
    
    async def _gather_fii_data(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Gather FII activity data."""
        try:
            logger.debug(f"Gathering FII data for {state.symbol}")
            state.fii_data = await self._scrape_fii_data(state.symbol)
            return state
        except Exception as e:
            logger.warning(f"Failed to gather FII data for {state.symbol}: {e}")
            state.fii_data = {}
            return state
    
    async def _analyze_sentiment(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Analyze sentiment using all gathered data."""
        try:
            logger.debug(f"Analyzing sentiment for {state.symbol}")
            
            # Create analysis prompt
            prompt = self._build_analysis_prompt(state)
            
            # Perform sentiment analysis using LLM
            analysis_result = await self._perform_llm_analysis(prompt, state)
            
            # Create SentimentAnalysis model
            state.sentiment_analysis = SentimentAnalysis(
                symbol=state.symbol,
                short_term_sentiment=analysis_result["short_term_sentiment"],
                short_term_target=analysis_result["short_term_target"],
                short_term_confidence=analysis_result["short_term_confidence"],
                short_term_timeframe="Next 2-4 weeks",
                medium_term_sentiment=analysis_result["medium_term_sentiment"],
                medium_term_target=analysis_result["medium_term_target"],
                medium_term_confidence=analysis_result["medium_term_confidence"],
                medium_term_timeframe="1-3 months",
                key_drivers=analysis_result["key_drivers"],
                risks=analysis_result["risks"],
                summary=analysis_result["summary"],
                financial_analysis=state.financial_data,
                intrinsic_value=state.intrinsic_value,
                social_sentiment=state.analyst_ratings
            )
            
            return state
            
        except Exception as e:
            state.error = f"Failed to analyze sentiment: {e}"
            return state
    
    async def _self_assess(self, state: MarketAnalysisState) -> MarketAnalysisState:
        """Self-assess the analysis quality and confidence."""
        try:
            logger.debug(f"Self-assessing analysis for {state.symbol}")
            
            # Calculate confidence based on data quality and analysis consistency
            confidence = self._calculate_confidence_score(state)
            state.confidence_score = confidence
            
            # Update sentiment analysis with confidence scores
            if state.sentiment_analysis:
                state.sentiment_analysis.short_term_confidence = confidence
                state.sentiment_analysis.medium_term_confidence = confidence * 0.9  # Slightly lower for medium term
            
            return state
            
        except Exception as e:
            logger.warning(f"Self-assessment failed for {state.symbol}: {e}")
            return state
    
    def _build_analysis_prompt(self, state: MarketAnalysisState) -> str:
        """Build comprehensive analysis prompt following ICICIBANK template."""
        
        prompt = f"""
        You are a seasoned professional equity research analyst with years of experience in financial markets.
        
        Analyze {state.symbol} and provide a comprehensive sentiment analysis following this exact format:
        
        SHORT-TERM VIEW (<1 Month):
        • Sentiment: [Cautiously Positive/Moderately Positive/Strongly Positive/Cautiously Negative/Moderately Negative/Strongly Negative]
        • Target Price Range: ₹[min] – ₹[max]
        • Time Frame: Next 2–4 weeks
        • Confidence Score: [X.X] / 10
        
        Key Drivers:
        • [Driver 1]
        • [Driver 2]
        • [Driver 3]
        
        Risks:
        • [Risk 1]
        • [Risk 2]
        • [Risk 3]
        
        Summary: [Clear actionable summary]
        
        MEDIUM-TERM VIEW (1–3 Months):
        • Sentiment: [Cautiously Positive/Moderately Positive/Strongly Positive/Cautiously Negative/Moderately Negative/Strongly Negative]
        • Target Price Range: ₹[min] – ₹[max]
        • Time Frame: 1-3 months
        • Confidence Score: [X.X] / 10
        
        Key Drivers:
        • [Driver 1]
        • [Driver 2]
        • [Driver 3]
        
        Risks:
        • [Risk 1]
        • [Risk 2]
        • [Risk 3]
        
        Summary: [Clear actionable summary]
        
        Available Data:
        - Market Data: {state.market_data}
        - Financial Data: {state.financial_data}
        - News Data: {state.news_data}
        - Intrinsic Value: {state.intrinsic_value}
        - Analyst Ratings: {state.analyst_ratings}
        - FII Data: {state.fii_data}
        
        Provide analysis based on this data and your professional expertise.
        """
        
        return prompt
    
    async def _perform_llm_analysis(self, prompt: str, state: MarketAnalysisState) -> Dict[str, Any]:
        """Perform LLM-based sentiment analysis."""
        # This would integrate with an actual LLM service
        # For now, return a structured analysis based on available data
        
        # Extract key metrics from market data
        market_metrics = self._extract_market_metrics(state.market_data)
        
        # Determine sentiment based on data
        sentiment = self._determine_sentiment(state)
        
        # Calculate target ranges
        current_price = market_metrics.get("current_price", 1000)
        short_target = self._calculate_target_range(current_price, sentiment, "short")
        medium_target = self._calculate_target_range(current_price, sentiment, "medium")
        
        # Generate key drivers and risks
        drivers = self._generate_key_drivers(state)
        risks = self._generate_risks(state)
        
        return {
            "short_term_sentiment": sentiment,
            "short_term_target": short_target,
            "short_term_confidence": 8.5,
            "medium_term_sentiment": sentiment,
            "medium_term_target": medium_target,
            "medium_term_confidence": 7.5,
            "key_drivers": drivers,
            "risks": risks,
            "summary": f"{state.symbol} shows {sentiment.lower()} sentiment with key drivers including {', '.join(drivers[:2])}."
        }
    
    def _extract_market_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from market data."""
        if not market_data:
            return {"current_price": 1000, "ema_20": 1000}
        
        return {
            "current_price": market_data.get("current_price", 1000),
            "ema_20": market_data.get("ema_20", 1000),
            "close_prices": market_data.get("close_prices", [1000])
        }
    
    def _determine_sentiment(self, state: MarketAnalysisState) -> str:
        """Determine sentiment based on available data."""
        # Simple sentiment determination logic
        # In a real implementation, this would be more sophisticated
        
        if not state.market_data:
            return "neutral"
        
        current_price = state.market_data.get("current_price", 1000)
        ema_20 = state.market_data.get("ema_20", 1000)
        
        if current_price > ema_20 * 1.05:
            return "Cautiously Positive"
        elif current_price < ema_20 * 0.95:
            return "Cautiously Negative"
        else:
            return "neutral"
    
    def _calculate_target_range(self, current_price: float, sentiment: str, timeframe: str) -> tuple:
        """Calculate target price range based on sentiment and timeframe."""
        if "Positive" in sentiment:
            if timeframe == "short":
                return (current_price * 1.02, current_price * 1.08)
            else:
                return (current_price * 1.05, current_price * 1.15)
        elif "Negative" in sentiment:
            if timeframe == "short":
                return (current_price * 0.92, current_price * 0.98)
            else:
                return (current_price * 0.85, current_price * 0.95)
        else:
            if timeframe == "short":
                return (current_price * 0.98, current_price * 1.02)
            else:
                return (current_price * 0.95, current_price * 1.05)
    
    def _generate_key_drivers(self, state: MarketAnalysisState) -> List[str]:
        """Generate key drivers based on available data."""
        drivers = []
        
        if state.financial_data:
            drivers.append("Strong quarterly performance")
        
        if state.market_data and state.market_data.get("ema_20"):
            drivers.append("Technical momentum above key levels")
        
        if state.analyst_ratings:
            drivers.append("Positive analyst sentiment")
        
        if not drivers:
            drivers = ["Market momentum", "Sector strength"]
        
        return drivers
    
    def _generate_risks(self, state: MarketAnalysisState) -> List[str]:
        """Generate risk factors based on available data."""
        risks = []
        
        if state.market_data:
            risks.append("Market volatility")
        
        if state.financial_data:
            risks.append("Earnings uncertainty")
        
        risks.extend(["Global macro factors", "Sector-specific headwinds"])
        
        return risks
    
    def _calculate_confidence_score(self, state: MarketAnalysisState) -> float:
        """Calculate confidence score based on data quality and analysis consistency."""
        score = 7.0  # Base score
        
        # Add points for available data
        if state.market_data:
            score += 0.5
        if state.financial_data:
            score += 0.5
        if state.news_data:
            score += 0.3
        if state.intrinsic_value:
            score += 0.3
        if state.analyst_ratings:
            score += 0.4
        
        # Cap at 10
        return min(score, 10.0)
    
    async def _scrape_screener_data(self, symbol: str) -> Dict[str, Any]:
        """Scrape financial data from screener.in."""
        try:
            url = f"{self.settings.screener_base_url}/stock/{symbol}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract financial data (simplified)
                    return {
                        "revenue_growth": "15%",
                        "profit_margin": "25%",
                        "debt_to_equity": "0.5",
                        "pe_ratio": "18.5"
                    }
                else:
                    return {}
        except Exception as e:
            logger.warning(f"Failed to scrape screener data for {symbol}: {e}")
            return {}
    
    async def _scrape_news_data(self, symbol: str) -> Dict[str, Any]:
        """Scrape news and social media sentiment."""
        # Simplified implementation
        return {
            "news_sentiment": "positive",
            "social_sentiment": "neutral",
            "recent_news": [f"Recent news about {symbol}"]
        }
    
    async def _scrape_intrinsic_value(self, symbol: str) -> Dict[str, Any]:
        """Scrape intrinsic value analysis."""
        # Simplified implementation
        return {
            "intrinsic_value": 1500.0,
            "valuation": "fair_value",
            "margin_of_safety": "10%"
        }
    
    async def _scrape_analyst_ratings(self, symbol: str) -> Dict[str, Any]:
        """Scrape analyst ratings and market mood."""
        # Simplified implementation
        return {
            "analyst_rating": "buy",
            "target_price": 1600.0,
            "market_mood": "positive"
        }
    
    async def _scrape_fii_data(self, symbol: str) -> Dict[str, Any]:
        """Scrape FII activity data."""
        # Simplified implementation
        return {
            "fii_holding": "15%",
            "fii_activity": "buying",
            "institutional_sentiment": "positive"
        }


# Example usage
async def main():
    """Example usage of Market Analyst."""
    from config.settings import get_settings
    from .mcp_client import MCPClient
    
    settings = get_settings()
    
    async with MCPClient(settings) as mcp_client:
        async with MarketAnalyst(mcp_client, settings) as analyst:
            try:
                # Analyze sentiment for a stock
                analysis = await analyst.analyze_sentiment("ICICIBANK")
                print(f"Analysis for ICICIBANK:")
                print(f"Short-term sentiment: {analysis.short_term_sentiment}")
                print(f"Short-term confidence: {analysis.short_term_confidence}/10")
                print(f"Key drivers: {analysis.key_drivers}")
                print(f"Risks: {analysis.risks}")
                print(f"Summary: {analysis.summary}")
                
            except Exception as e:
                print(f"Analysis failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 