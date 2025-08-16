"""
Recommendation Service for Kite Trading Recommendation App.
Integrates with recommendation agent for trade recommendations and portfolio analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from models.data_models import TradeRecommendation, ApplicationSettings
from services.recommendation_agent import RecommendationAgent
from services.mcp_client import MCPClient
from services.portfolio_service import PortfolioService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TradeOpportunity:
    """Trade opportunity analysis."""
    symbol: str
    trade_type: str  # new, swap, hedge
    option_type: str
    strike_price: float
    premium: float
    margin_required: float
    rom: float
    ssr: float
    risk_indicator: int
    confidence: float
    reasoning: str
    action_points: List[str]


@dataclass
class FilterConstraints:
    """Filter constraints for recommendations."""
    min_ssr: float = 0.0
    min_premium: float = 0.0
    min_rom: float = 0.0
    max_risk_indicator: int = 10
    approved_stocks: List[str] = None
    
    def __post_init__(self):
        if self.approved_stocks is None:
            self.approved_stocks = []


@dataclass
class RecommendationResult:
    """Complete recommendation result."""
    opportunities: List[TradeOpportunity]
    portfolio_impact: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    confidence_score: float
    recommendations_summary: str
    analysis_date: datetime


class RecommendationService:
    """Service for trade recommendations and portfolio analysis."""
    
    def __init__(self, recommendation_agent: RecommendationAgent, mcp_client: MCPClient, 
                 portfolio_service: PortfolioService, settings: ApplicationSettings):
        """Initialize recommendation service."""
        self.recommendation_agent = recommendation_agent
        self.mcp_client = mcp_client
        self.portfolio_service = portfolio_service
        self.settings = settings
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 600  # 10 minutes cache
    
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
        logger.debug(f"Cached recommendation data for key: {key}")
    
    async def get_trade_recommendations(self, filters: FilterConstraints = None) -> RecommendationResult:
        """Get trade recommendations based on filters."""
        cache_key = f"recommendations_{hash(str(filters)) if filters else 'default'}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug("Returning cached trade recommendations")
            return self._cache[cache_key]
        
        try:
            logger.info("Getting trade recommendations...")
            
            # Get portfolio analysis
            portfolio_analysis = await self.portfolio_service.get_portfolio_analysis()
            
            # Get option chain data for approved stocks
            opportunities = []
            approved_stocks = filters.approved_stocks if filters else self.settings.stock_scope.approved_stocks
            
            for symbol in approved_stocks:
                try:
                    # Get option chain data
                    option_chain = await self.mcp_client.get_option_chain(symbol)
                    
                    # Analyze each option for opportunities
                    for option in option_chain:
                        opportunity = await self._analyze_option_opportunity(
                            symbol, option, portfolio_analysis, filters
                        )
                        if opportunity:
                            opportunities.append(opportunity)
                            
                except Exception as e:
                    logger.warning(f"Failed to analyze {symbol}: {e}")
                    continue
            
            # Sort opportunities by confidence and ROM
            opportunities.sort(key=lambda x: (x.confidence, x.rom), reverse=True)
            
            # Limit to top recommendations
            top_opportunities = opportunities[:10]
            
            # Analyze portfolio impact
            portfolio_impact = await self._analyze_portfolio_impact(top_opportunities, portfolio_analysis)
            
            # Assess overall risk
            risk_assessment = self._assess_portfolio_risk(top_opportunities, portfolio_analysis)
            
            # Calculate overall confidence
            confidence_score = sum(opp.confidence for opp in top_opportunities) / len(top_opportunities) if top_opportunities else 0
            
            # Generate recommendations summary
            recommendations_summary = self._generate_recommendations_summary(top_opportunities)
            
            # Create recommendation result
            recommendation_result = RecommendationResult(
                opportunities=top_opportunities,
                portfolio_impact=portfolio_impact,
                risk_assessment=risk_assessment,
                confidence_score=confidence_score,
                recommendations_summary=recommendations_summary,
                analysis_date=datetime.now()
            )
            
            # Cache the result
            self._cache_data(cache_key, recommendation_result)
            
            logger.info(f"Trade recommendations completed: {len(top_opportunities)} opportunities")
            return recommendation_result
            
        except Exception as e:
            logger.error(f"Failed to get trade recommendations: {e}")
            raise
    
    async def _analyze_option_opportunity(self, symbol: str, option: Dict[str, Any], 
                                        portfolio_analysis: Any, filters: FilterConstraints) -> Optional[TradeOpportunity]:
        """Analyze a specific option for trade opportunity."""
        try:
            # Extract option data
            option_type = option.get("option_type", "PE")
            strike_price = option.get("strike_price", 0)
            premium = option.get("premium", 0)
            margin_required = option.get("margin_required", 0)
            
            # Calculate ROM and SSR
            rom = (premium / margin_required) * 100 if margin_required > 0 else 0
            
            # Get current market price for SSR calculation
            market_data = await self.mcp_client.get_market_data(symbol)
            current_price = market_data.get("current_price", 0)
            ssr = ((current_price - strike_price) / current_price) * 100 if current_price > 0 else 0
            
            # Apply filters
            if filters:
                if ssr < filters.min_ssr:
                    return None
                if premium < filters.min_premium:
                    return None
                if rom < filters.min_rom:
                    return None
            
            # Get recommendation from agent
            recommendation_prompt = f"""
            Analyze {symbol} {option_type} option:
            - Strike Price: {strike_price}
            - Premium: {premium}
            - Margin Required: {margin_required}
            - ROM: {rom:.2f}%
            - SSR: {ssr:.2f}%
            
            Provide:
            1. Trade type (new/swap/hedge)
            2. Risk indicator (1-10)
            3. Confidence score (0-1)
            4. Reasoning
            5. Action points
            """
            
            recommendation_result = await self.recommendation_agent.analyze_option(
                symbol, option, recommendation_prompt
            )
            
            # Extract recommendation data
            trade_type = recommendation_result.get("trade_type", "new")
            risk_indicator = recommendation_result.get("risk_indicator", 5)
            confidence = recommendation_result.get("confidence", 0.5)
            reasoning = recommendation_result.get("reasoning", "")
            action_points = recommendation_result.get("action_points", [])
            
            # Apply risk filter
            if filters and risk_indicator > filters.max_risk_indicator:
                return None
            
            # Create trade opportunity
            opportunity = TradeOpportunity(
                symbol=symbol,
                trade_type=trade_type,
                option_type=option_type,
                strike_price=strike_price,
                premium=premium,
                margin_required=margin_required,
                rom=rom,
                ssr=ssr,
                risk_indicator=risk_indicator,
                confidence=confidence,
                reasoning=reasoning,
                action_points=action_points
            )
            
            return opportunity
            
        except Exception as e:
            logger.warning(f"Failed to analyze option opportunity for {symbol}: {e}")
            return None
    
    async def _analyze_portfolio_impact(self, opportunities: List[TradeOpportunity], 
                                      portfolio_analysis: Any) -> Dict[str, Any]:
        """Analyze the impact of recommendations on portfolio."""
        try:
            total_margin_addition = sum(opp.margin_required for opp in opportunities)
            total_premium_addition = sum(opp.premium for opp in opportunities)
            
            # Calculate new portfolio metrics
            new_total_margin = portfolio_analysis.total_margin + total_margin_addition
            new_total_premium = portfolio_analysis.total_premium_collected + total_premium_addition
            
            # Calculate new ROI
            new_roi = (new_total_premium / new_total_margin) * 100 if new_total_margin > 0 else 0
            
            # Calculate margin utilization impact
            current_utilization = portfolio_analysis.margin_utilization
            new_utilization = (new_total_margin / (new_total_margin + portfolio_analysis.available_cash)) * 100
            
            return {
                "total_margin_addition": total_margin_addition,
                "total_premium_addition": total_premium_addition,
                "new_total_margin": new_total_margin,
                "new_total_premium": new_total_premium,
                "new_roi": new_roi,
                "roi_change": new_roi - portfolio_analysis.overall_roi,
                "margin_utilization_change": new_utilization - current_utilization,
                "opportunity_count": len(opportunities)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze portfolio impact: {e}")
            return {}
    
    def _assess_portfolio_risk(self, opportunities: List[TradeOpportunity], 
                              portfolio_analysis: Any) -> Dict[str, Any]:
        """Assess the risk impact of recommendations."""
        try:
            if not opportunities:
                return {"risk_level": "Low", "risk_score": 0, "risk_factors": []}
            
            # Calculate average risk indicator
            avg_risk_indicator = sum(opp.risk_indicator for opp in opportunities) / len(opportunities)
            
            # Determine risk level
            if avg_risk_indicator <= 3:
                risk_level = "Low"
            elif avg_risk_indicator <= 6:
                risk_level = "Medium"
            else:
                risk_level = "High"
            
            # Identify risk factors
            risk_factors = []
            if avg_risk_indicator > 7:
                risk_factors.append("High risk options in recommendations")
            if len(opportunities) > 5:
                risk_factors.append("Large number of recommendations")
            
            return {
                "risk_level": risk_level,
                "risk_score": avg_risk_indicator,
                "risk_factors": risk_factors,
                "recommendation_count": len(opportunities)
            }
            
        except Exception as e:
            logger.error(f"Failed to assess portfolio risk: {e}")
            return {"risk_level": "Unknown", "risk_score": 0, "risk_factors": []}
    
    def _generate_recommendations_summary(self, opportunities: List[TradeOpportunity]) -> str:
        """Generate a summary of recommendations."""
        if not opportunities:
            return "No trade opportunities found based on current filters."
        
        summary_parts = []
        summary_parts.append(f"Found {len(opportunities)} trade opportunities:")
        
        # Group by trade type
        trade_types = {}
        for opp in opportunities:
            if opp.trade_type not in trade_types:
                trade_types[opp.trade_type] = []
            trade_types[opp.trade_type].append(opp)
        
        for trade_type, opps in trade_types.items():
            summary_parts.append(f"- {len(opps)} {trade_type} trades")
        
        # Add top recommendation
        top_opp = opportunities[0]
        summary_parts.append(f"Top recommendation: {top_opp.symbol} {top_opp.option_type} with {top_opp.rom:.1f}% ROM")
        
        return " ".join(summary_parts)
    
    def get_recommendation_summary(self, result: RecommendationResult) -> Dict[str, Any]:
        """Get recommendation summary for display."""
        return {
            "opportunity_count": len(result.opportunities),
            "confidence_score": result.confidence_score,
            "portfolio_impact": result.portfolio_impact,
            "risk_assessment": result.risk_assessment,
            "recommendations_summary": result.recommendations_summary,
            "analysis_date": result.analysis_date.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def clear_cache(self):
        """Clear all cached recommendation data."""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Recommendation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cached_keys": list(self._cache.keys()),
            "cache_ttl": self._cache_ttl
        } 