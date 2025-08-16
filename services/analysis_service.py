"""
Analysis Service for Kite Trading Recommendation App.
Integrates with market analyst agent for sentiment and market analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from models.data_models import SentimentAnalysis, ApplicationSettings
from services.market_analyst import MarketAnalyst
from services.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketAnalysis:
    """Market analysis result."""
    symbol: str
    sentiment: str
    confidence: float
    short_term_target: float
    medium_term_target: float
    risk_level: str
    key_factors: List[str]
    analysis_date: datetime


@dataclass
class SectorAnalysis:
    """Sector analysis result."""
    sector: str
    sentiment: str
    confidence: float
    top_performers: List[str]
    key_drivers: List[str]
    risk_factors: List[str]
    analysis_date: datetime


@dataclass
class CustomAnalysis:
    """Custom analysis result."""
    prompt: str
    analysis: str
    confidence: float
    key_points: List[str]
    recommendations: List[str]
    analysis_date: datetime


class AnalysisService:
    """Service for market and sentiment analysis."""
    
    def __init__(self, market_analyst: MarketAnalyst, mcp_client: MCPClient, settings: ApplicationSettings):
        """Initialize analysis service."""
        self.market_analyst = market_analyst
        self.mcp_client = mcp_client
        self.settings = settings
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 300  # 5 minutes cache
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache or self._cache_timestamp is None:
            return False
        
        cache_age = datetime.now() - self._cache_timestamp
        return cache_age.seconds < self._cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp."""
        self._cache[key] = data
        self._cache_timestamp = datetime.now()
        logger.debug(f"Cached analysis data for key: {key}")
    
    async def get_stock_analysis(self, symbol: str) -> MarketAnalysis:
        """Get comprehensive analysis for a specific stock."""
        cache_key = f"stock_analysis_{symbol}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug(f"Returning cached stock analysis for {symbol}")
            return self._cache[cache_key]
        
        try:
            logger.info(f"Getting stock analysis for {symbol}...")
            
            # Get market data from MCP server
            market_data = await self.mcp_client.get_market_data(symbol)
            
            # Get quote data
            quote_data = await self.mcp_client.get_quote(symbol)
            
            # Prepare analysis prompt
            analysis_prompt = f"""
            Analyze {symbol} stock with the following data:
            - Current Price: {market_data.get('current_price', 0)}
            - Volume: {market_data.get('volume', 0)}
            - Change: {market_data.get('change_percent', 0)}%
            
            Provide:
            1. Sentiment analysis (bullish/bearish/neutral)
            2. Short-term target (1 month)
            3. Medium-term target (3 months)
            4. Risk assessment
            5. Key factors driving the stock
            """
            
            # Get analysis from market analyst
            analysis_result = await self.market_analyst.analyze_stock(symbol, analysis_prompt)
            
            # Extract sentiment and confidence
            sentiment = analysis_result.get("sentiment", "neutral")
            confidence = analysis_result.get("confidence", 0.5)
            
            # Extract targets
            short_term_target = analysis_result.get("short_term_target", market_data.get('current_price', 0))
            medium_term_target = analysis_result.get("medium_term_target", market_data.get('current_price', 0))
            
            # Determine risk level
            risk_level = self._determine_risk_level(confidence, market_data)
            
            # Extract key factors
            key_factors = analysis_result.get("key_factors", [])
            
            # Create market analysis
            market_analysis = MarketAnalysis(
                symbol=symbol,
                sentiment=sentiment,
                confidence=confidence,
                short_term_target=short_term_target,
                medium_term_target=medium_term_target,
                risk_level=risk_level,
                key_factors=key_factors,
                analysis_date=datetime.now()
            )
            
            # Cache the result
            self._cache_data(cache_key, market_analysis)
            
            logger.info(f"Stock analysis completed for {symbol}")
            return market_analysis
            
        except Exception as e:
            logger.error(f"Failed to get stock analysis for {symbol}: {e}")
            raise
    
    async def get_sector_analysis(self, sector: str) -> SectorAnalysis:
        """Get analysis for a specific sector."""
        cache_key = f"sector_analysis_{sector}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug(f"Returning cached sector analysis for {sector}")
            return self._cache[cache_key]
        
        try:
            logger.info(f"Getting sector analysis for {sector}...")
            
            # Prepare sector analysis prompt
            analysis_prompt = f"""
            Analyze the {sector} sector:
            
            Provide:
            1. Overall sector sentiment
            2. Top performing stocks in the sector
            3. Key drivers affecting the sector
            4. Risk factors to watch
            5. Sector outlook
            """
            
            # Get analysis from market analyst
            analysis_result = await self.market_analyst.analyze_sector(sector, analysis_prompt)
            
            # Extract sentiment and confidence
            sentiment = analysis_result.get("sentiment", "neutral")
            confidence = analysis_result.get("confidence", 0.5)
            
            # Extract top performers
            top_performers = analysis_result.get("top_performers", [])
            
            # Extract key drivers and risk factors
            key_drivers = analysis_result.get("key_drivers", [])
            risk_factors = analysis_result.get("risk_factors", [])
            
            # Create sector analysis
            sector_analysis = SectorAnalysis(
                sector=sector,
                sentiment=sentiment,
                confidence=confidence,
                top_performers=top_performers,
                key_drivers=key_drivers,
                risk_factors=risk_factors,
                analysis_date=datetime.now()
            )
            
            # Cache the result
            self._cache_data(cache_key, sector_analysis)
            
            logger.info(f"Sector analysis completed for {sector}")
            return sector_analysis
            
        except Exception as e:
            logger.error(f"Failed to get sector analysis for {sector}: {e}")
            raise
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get overall market overview."""
        cache_key = "market_overview"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug("Returning cached market overview")
            return self._cache[cache_key]
        
        try:
            logger.info("Getting market overview...")
            
            # Prepare market overview prompt
            analysis_prompt = """
            Provide a comprehensive market overview:
            
            1. Overall market sentiment
            2. Key market drivers
            3. Sector performance summary
            4. Risk factors affecting the market
            5. Market outlook for the next 1-3 months
            """
            
            # Get analysis from market analyst
            analysis_result = await self.market_analyst.analyze_market(analysis_prompt)
            
            # Create market overview
            market_overview = {
                "sentiment": analysis_result.get("sentiment", "neutral"),
                "confidence": analysis_result.get("confidence", 0.5),
                "key_drivers": analysis_result.get("key_drivers", []),
                "sector_performance": analysis_result.get("sector_performance", {}),
                "risk_factors": analysis_result.get("risk_factors", []),
                "outlook": analysis_result.get("outlook", ""),
                "analysis_date": datetime.now()
            }
            
            # Cache the result
            self._cache_data(cache_key, market_overview)
            
            logger.info("Market overview completed")
            return market_overview
            
        except Exception as e:
            logger.error(f"Failed to get market overview: {e}")
            raise
    
    async def get_custom_analysis(self, prompt: str) -> CustomAnalysis:
        """Get custom analysis based on user prompt."""
        try:
            logger.info("Getting custom analysis...")
            
            # Get analysis from market analyst
            analysis_result = await self.market_analyst.analyze_custom(prompt)
            
            # Extract analysis components
            analysis = analysis_result.get("analysis", "")
            confidence = analysis_result.get("confidence", 0.5)
            key_points = analysis_result.get("key_points", [])
            recommendations = analysis_result.get("recommendations", [])
            
            # Create custom analysis
            custom_analysis = CustomAnalysis(
                prompt=prompt,
                analysis=analysis,
                confidence=confidence,
                key_points=key_points,
                recommendations=recommendations,
                analysis_date=datetime.now()
            )
            
            logger.info("Custom analysis completed")
            return custom_analysis
            
        except Exception as e:
            logger.error(f"Failed to get custom analysis: {e}")
            raise
    
    def _determine_risk_level(self, confidence: float, market_data: Dict[str, Any]) -> str:
        """Determine risk level based on confidence and market data."""
        volatility = abs(market_data.get('change_percent', 0))
        
        if confidence < 0.3 or volatility > 5:
            return "High Risk"
        elif confidence < 0.6 or volatility > 2:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def get_analysis_summary(self, analysis: MarketAnalysis) -> Dict[str, Any]:
        """Get analysis summary for display."""
        return {
            "symbol": analysis.symbol,
            "sentiment": analysis.sentiment,
            "confidence": analysis.confidence,
            "short_term_target": analysis.short_term_target,
            "medium_term_target": analysis.medium_term_target,
            "risk_level": analysis.risk_level,
            "key_factors": analysis.key_factors,
            "analysis_date": analysis.analysis_date.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def clear_cache(self):
        """Clear all cached analysis data."""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cached_keys": list(self._cache.keys()),
            "cache_ttl": self._cache_ttl
        } 