"""
Recommendation Agent for Kite Trading Recommendation App.
Experienced investment fund manager and financial advisor for options trading strategies.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel
from langgraph.graph import StateGraph, END, START

from models.data_models import (
    TradeRecommendation, 
    RecommendationType, 
    Portfolio, 
    SentimentAnalysis,
    ApplicationSettings
)
from .mcp_client import MCPClient
from .market_analyst import MarketAnalyst

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationState(BaseModel):
    """State for recommendation workflow."""
    portfolio: Portfolio
    filters: Dict[str, Any]
    scope_stocks: List[str]
    opportunities: List[Dict[str, Any]] = []
    recommendations: List[TradeRecommendation] = []
    market_analyses: Dict[str, SentimentAnalysis] = {}
    final_recommendations: List[TradeRecommendation] = []
    confidence_scores: Dict[str, float] = {}
    error: Optional[str] = None


class RecommendationAgent:
    """Experienced investment fund manager and financial advisor."""
    
    def __init__(self, mcp_client: MCPClient, market_analyst: MarketAnalyst, settings: ApplicationSettings):
        """Initialize recommendation agent."""
        self.mcp_client = mcp_client
        self.market_analyst = market_analyst
        self.settings = settings
        
    async def find_opportunities(self, portfolio: Portfolio, filters: Dict[str, Any]) -> List[TradeRecommendation]:
        """
        Find trading opportunities based on portfolio and filters.
        
        Args:
            portfolio: Current portfolio data
            filters: User-defined filter constraints
            
        Returns:
            List of actionable trade recommendations
        """
        try:
            logger.info("Starting opportunity analysis...")
            
            # Create recommendation state
            state = RecommendationState(
                portfolio=portfolio,
                filters=filters,
                scope_stocks=self.settings.stock_scope.approved_stocks
            )
            
            # Execute recommendation workflow
            final_state = await self._execute_simple_recommendation_workflow(state)
            
            if hasattr(final_state, 'error') and final_state.error:
                raise Exception(f"Recommendation analysis failed: {final_state.error}")
            
            logger.info(f"Found {len(final_state.final_recommendations)} recommendations")
            return final_state.final_recommendations
            
        except Exception as e:
            logger.error(f"Opportunity analysis failed: {e}")
            raise
    
    async def _execute_simple_recommendation_workflow(self, state: RecommendationState) -> RecommendationState:
        """Execute a simplified recommendation workflow."""
        
        try:
            # Analyze portfolio
            state = await self._analyze_portfolio(state)
            
            # Scan opportunities
            state = await self._scan_opportunities(state)
            
            # Analyze market sentiment
            state = await self._analyze_market_sentiment(state)
            
            # Calculate metrics
            state = await self._calculate_metrics(state)
            
            # Apply filters
            state = await self._apply_filters(state)
            
            # Generate recommendations
            state = await self._generate_recommendations(state)
            
            # Self review
            state = await self._self_review(state)
            
            # Rank recommendations
            state = await self._rank_recommendations(state)
            
            return state
            
        except Exception as e:
            state.error = f"Recommendation workflow failed: {e}"
            return state
    
    async def _analyze_portfolio(self, state: RecommendationState) -> RecommendationState:
        """Analyze current portfolio for optimization opportunities."""
        try:
            logger.debug("Analyzing portfolio for opportunities...")
            
            portfolio = state.portfolio
            
            # Analyze portfolio diversification
            sector_exposure = portfolio.sector_exposure
            total_positions = len(portfolio.positions)
            available_margin = portfolio.available_cash
            
            logger.info(f"Portfolio analysis: {total_positions} positions, ₹{available_margin:,.0f} available margin")
            
            # Identify sectors with low exposure
            low_exposure_sectors = self._identify_low_exposure_sectors(sector_exposure)
            
            # Identify high-risk positions for potential swaps
            high_risk_positions = self._identify_high_risk_positions(portfolio.positions)
            
            # Store analysis results
            state.opportunities.extend([
                {"type": "diversification", "sectors": low_exposure_sectors},
                {"type": "risk_management", "positions": high_risk_positions},
                {"type": "margin_utilization", "available_margin": available_margin}
            ])
            
            return state
            
        except Exception as e:
            state.error = f"Portfolio analysis failed: {e}"
            return state
    
    async def _scan_opportunities(self, state: RecommendationState) -> RecommendationState:
        """Scan for trading opportunities across approved stocks."""
        try:
            logger.debug("Scanning for trading opportunities...")
            
            opportunities = []
            
            for stock in state.scope_stocks:
                try:
                    # Get option chain for the stock
                    option_chain = await self.mcp_client.get_option_chain(stock)
                    
                    # Get current quote
                    quote = await self.mcp_client.get_quote(stock)
                    
                    # Analyze each option in the chain
                    for option in option_chain[:10]:  # Limit to first 10 options
                        opportunity = {
                            "symbol": stock,
                            "option": option,
                            "quote": quote,
                            "analysis_needed": True
                        }
                        opportunities.append(opportunity)
                        
                except Exception as e:
                    logger.warning(f"Failed to scan opportunities for {stock}: {e}")
                    continue
            
            state.opportunities.extend(opportunities)
            logger.info(f"Scanned {len(opportunities)} opportunities across {len(state.scope_stocks)} stocks")
            
            return state
            
        except Exception as e:
            state.error = f"Opportunity scanning failed: {e}"
            return state
    
    async def _analyze_market_sentiment(self, state: RecommendationState) -> RecommendationState:
        """Analyze market sentiment for opportunities."""
        try:
            logger.debug("Analyzing market sentiment for opportunities...")
            
            # Get unique symbols from opportunities
            symbols = list(set([
                opp["symbol"] for opp in state.opportunities 
                if isinstance(opp, dict) and "symbol" in opp
            ]))
            
            # Analyze sentiment for each symbol
            for symbol in symbols:
                try:
                    analysis = await self.market_analyst.analyze_sentiment(symbol)
                    state.market_analyses[symbol] = analysis
                    logger.debug(f"Analyzed sentiment for {symbol}: {analysis.short_term_sentiment}")
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze sentiment for {symbol}: {e}")
                    continue
            
            return state
            
        except Exception as e:
            state.error = f"Market sentiment analysis failed: {e}"
            return state
    
    async def _calculate_metrics(self, state: RecommendationState) -> RecommendationState:
        """Calculate key metrics for each opportunity."""
        try:
            logger.debug("Calculating metrics for opportunities...")
            
            for opportunity in state.opportunities:
                if isinstance(opportunity, dict) and "option" in opportunity:
                    symbol = opportunity["symbol"]
                    option = opportunity["option"]
                    quote = opportunity.get("quote", {})
                    
                    # Calculate ROM (Return on Margin)
                    rom = self._calculate_rom(option, state.portfolio)
                    
                    # Calculate SSR (Strike Safety Ratio)
                    ssr = self._calculate_ssr(option, quote)
                    
                    # Calculate risk indicator
                    risk_indicator = self._calculate_risk_indicator(option, state.market_analyses.get(symbol))
                    
                    # Store calculated metrics
                    opportunity.update({
                        "rom": rom,
                        "ssr": ssr,
                        "risk_indicator": risk_indicator,
                        "metrics_calculated": True
                    })
            
            return state
            
        except Exception as e:
            state.error = f"Metrics calculation failed: {e}"
            return state
    
    async def _apply_filters(self, state: RecommendationState) -> RecommendationState:
        """Apply user-defined filters to opportunities."""
        try:
            logger.debug("Applying filters to opportunities...")
            
            filters = state.filters
            min_ssr = filters.get('min_ssr', 0.02)
            min_premium = filters.get('min_premium', 0.05)
            min_rom = filters.get('min_rom', 0.05)
            max_risk = filters.get('max_risk', 7)
            
            filtered_opportunities = []
            
            for opportunity in state.opportunities:
                if isinstance(opportunity, dict) and "metrics_calculated" in opportunity:
                    rom = opportunity.get("rom", 0)
                    ssr = opportunity.get("ssr", 0)
                    risk_indicator = opportunity.get("risk_indicator", 10)
                    premium = opportunity.get("option", {}).get("premium", 0)
                    
                    # Apply filter criteria
                    if (rom >= min_rom and 
                        ssr >= min_ssr and 
                        premium >= min_premium and 
                        risk_indicator <= max_risk):
                        filtered_opportunities.append(opportunity)
            
            state.opportunities = filtered_opportunities
            logger.info(f"Filtered to {len(filtered_opportunities)} opportunities")
            
            return state
            
        except Exception as e:
            state.error = f"Filter application failed: {e}"
            return state
    
    async def _generate_recommendations(self, state: RecommendationState) -> RecommendationState:
        """Generate trade recommendations from filtered opportunities."""
        try:
            logger.debug("Generating trade recommendations...")
            
            recommendations = []
            
            for opportunity in state.opportunities:
                if isinstance(opportunity, dict) and "symbol" in opportunity:
                    recommendation = await self._create_recommendation(opportunity, state)
                    if recommendation:
                        recommendations.append(recommendation)
            
            state.recommendations = recommendations
            logger.info(f"Generated {len(recommendations)} recommendations")
            
            return state
            
        except Exception as e:
            state.error = f"Recommendation generation failed: {e}"
            return state
    
    async def _self_review(self, state: RecommendationState) -> RecommendationState:
        """Self-review recommendations for quality and consistency."""
        try:
            logger.debug("Self-reviewing recommendations...")
            
            reviewed_recommendations = []
            
            for recommendation in state.recommendations:
                # Review recommendation quality
                quality_score = self._assess_recommendation_quality(recommendation, state)
                
                # Update confidence based on review
                recommendation.confidence = min(recommendation.confidence * quality_score, 10.0)
                
                # Only keep high-quality recommendations
                if recommendation.confidence >= 6.0:
                    reviewed_recommendations.append(recommendation)
                    state.confidence_scores[recommendation.symbol] = recommendation.confidence
            
            state.recommendations = reviewed_recommendations
            logger.info(f"Self-review completed: {len(reviewed_recommendations)} high-quality recommendations")
            
            return state
            
        except Exception as e:
            state.error = f"Self-review failed: {e}"
            return state
    
    async def _rank_recommendations(self, state: RecommendationState) -> RecommendationState:
        """Rank recommendations by confidence and potential return."""
        try:
            logger.debug("Ranking recommendations...")
            
            # Sort by confidence score and expected ROM
            ranked_recommendations = sorted(
                state.recommendations,
                key=lambda r: (r.confidence, r.expected_rom),
                reverse=True
            )
            
            # Limit to top recommendations
            final_recommendations = ranked_recommendations[:5]  # Top 5 recommendations
            
            state.final_recommendations = final_recommendations
            logger.info(f"Ranked and selected {len(final_recommendations)} final recommendations")
            
            return state
            
        except Exception as e:
            state.error = f"Recommendation ranking failed: {e}"
            return state
    
    def _identify_low_exposure_sectors(self, sector_exposure: Dict[str, float]) -> List[str]:
        """Identify sectors with low portfolio exposure."""
        low_exposure_threshold = 0.1  # 10%
        low_exposure_sectors = []
        
        for sector, exposure in sector_exposure.items():
            if exposure < low_exposure_threshold:
                low_exposure_sectors.append(sector)
        
        return low_exposure_sectors
    
    def _identify_high_risk_positions(self, positions: List) -> List:
        """Identify high-risk positions for potential swaps."""
        high_risk_positions = []
        
        for position in positions:
            if position.risk_indicator >= 8:  # High risk threshold
                high_risk_positions.append(position)
        
        return high_risk_positions
    
    def _calculate_rom(self, option: Dict[str, Any], portfolio: Portfolio) -> float:
        """Calculate Return on Margin (ROM)."""
        try:
            premium = option.get("premium", 0)
            margin_required = option.get("margin_required", 1)  # Avoid division by zero
            
            if margin_required > 0:
                rom = (premium / margin_required) * 100
                return min(rom, 100.0)  # Cap at 100%
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _calculate_ssr(self, option: Dict[str, Any], quote: Dict[str, Any]) -> float:
        """Calculate Strike Safety Ratio (SSR)."""
        try:
            spot_price = quote.get("last_price", 1000)
            strike_price = option.get("strike_price", 1000)
            
            if spot_price > 0:
                ssr = ((spot_price - strike_price) / spot_price) * 100
                return max(ssr, 0.0)  # SSR should be positive
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _calculate_risk_indicator(self, option: Dict[str, Any], analysis: Optional[SentimentAnalysis]) -> int:
        """Calculate risk indicator (1-10 scale)."""
        try:
            base_risk = 5  # Base risk score
            
            # Adjust based on sentiment analysis
            if analysis:
                if "Negative" in analysis.short_term_sentiment:
                    base_risk += 2
                elif "Positive" in analysis.short_term_sentiment:
                    base_risk -= 1
            
            # Adjust based on option characteristics
            if option.get("option_type") == "PE":  # Put options
                base_risk += 1
            
            # Ensure risk is within 1-10 range
            return max(1, min(10, base_risk))
            
        except Exception:
            return 5  # Default risk score
    
    async def _create_recommendation(self, opportunity: Dict[str, Any], state: RecommendationState) -> Optional[TradeRecommendation]:
        """Create a trade recommendation from an opportunity."""
        try:
            symbol = opportunity["symbol"]
            option = opportunity["option"]
            analysis = state.market_analyses.get(symbol)
            
            # Determine recommendation type
            recommendation_type = self._determine_recommendation_type(opportunity, state.portfolio)
            
            # Calculate key metrics
            rom = opportunity.get("rom", 0)
            ssr = opportunity.get("ssr", 0)
            risk_indicator = opportunity.get("risk_indicator", 5)
            
            # Build trade driver
            trade_driver = self._build_trade_driver(opportunity, analysis, rom, ssr)
            
            # Build reasoning
            reasoning = self._build_reasoning(opportunity, analysis, state.portfolio)
            
            # Assess portfolio impact
            portfolio_impact = self._assess_portfolio_impact(opportunity, state.portfolio)
            
            # Create recommendation
            recommendation = TradeRecommendation(
                recommendation_type=recommendation_type,
                symbol=symbol,
                option_type=option.get("option_type", "PE"),
                strike_price=option.get("strike_price", 0),
                expiry=option.get("expiry", "AUG"),
                quantity=option.get("lot_size", 1),
                price_range=(option.get("bid_price", 0), option.get("ask_price", 0)),
                confidence=analysis.short_term_confidence if analysis else 7.0,
                trade_driver=trade_driver,
                risk_assessment=f"Risk indicator: {risk_indicator}/10",
                expected_rom=rom,
                expected_ssr=ssr,
                reasoning=reasoning,
                portfolio_impact=portfolio_impact
            )
            
            return recommendation
            
        except Exception as e:
            logger.warning(f"Failed to create recommendation: {e}")
            return None
    
    def _determine_recommendation_type(self, opportunity: Dict[str, Any], portfolio: Portfolio) -> RecommendationType:
        """Determine the type of recommendation."""
        symbol = opportunity["symbol"]
        
        # Check if we should recommend a swap
        for position in portfolio.positions:
            if position.symbol == symbol and position.risk_indicator >= 8:
                return RecommendationType.SWAP_TRADE
        
        # Check if we should recommend a hedge
        if self._should_hedge(opportunity, portfolio):
            return RecommendationType.HEDGE_TRADE
        
        # Default to new trade
        return RecommendationType.NEW_TRADE
    
    def _should_hedge(self, opportunity: Dict[str, Any], portfolio: Portfolio) -> bool:
        """Determine if this should be a hedge recommendation."""
        # Simplified hedge logic
        # In a real implementation, this would be more sophisticated
        return False
    
    def _build_trade_driver(self, opportunity: Dict[str, Any], analysis: Optional[SentimentAnalysis], rom: float, ssr: float) -> str:
        """Build trade driver following template format."""
        symbol = opportunity["symbol"]
        
        driver = f"""
        - {symbol} posted strong financial performance and positive sentiment
        - Currently the portfolio has relatively less exposure to this sector
        - The trade is offering good ROM at {rom:.1f}% and SSR of {ssr:.1f}%
        - Overall positive sentiments for the sector
        """
        
        if analysis:
            driver += f"- Market analyst confidence: {analysis.short_term_confidence}/10"
        
        return driver.strip()
    
    def _build_reasoning(self, opportunity: Dict[str, Any], analysis: Optional[SentimentAnalysis], portfolio: Portfolio) -> str:
        """Build detailed reasoning for the recommendation."""
        symbol = opportunity["symbol"]
        option = opportunity["option"]
        
        reasoning = f"""
        This recommendation is based on comprehensive analysis of {symbol}:
        
        1. Technical Analysis: {option.get('option_type', 'PE')} option with strike price ₹{option.get('strike_price', 0):,.0f}
        2. Market Sentiment: {analysis.short_term_sentiment if analysis else 'Neutral'}
        3. Portfolio Diversification: Reduces concentration risk
        4. Risk-Reward Profile: Favorable ROM and SSR metrics
        5. Market Conditions: Aligned with current market trends
        """
        
        return reasoning.strip()
    
    def _assess_portfolio_impact(self, opportunity: Dict[str, Any], portfolio: Portfolio) -> str:
        """Assess how the recommendation impacts the portfolio."""
        symbol = opportunity["symbol"]
        
        # Check sector exposure
        sector = self._get_stock_sector(symbol)
        current_exposure = portfolio.sector_exposure.get(sector, 0)
        
        impact = f"""
        Portfolio Impact Analysis:
        
        1. Sector Exposure: {sector} exposure will increase from {current_exposure:.1%} to {(current_exposure + 0.05):.1%}
        2. Risk Distribution: Improves overall portfolio risk profile
        3. Margin Utilization: Uses ₹{opportunity.get('option', {}).get('margin_required', 0):,.0f} of available margin
        4. Diversification: Reduces concentration in existing positions
        """
        
        return impact.strip()
    
    def _get_stock_sector(self, symbol: str) -> str:
        """Get the sector for a given stock symbol."""
        # Simplified sector mapping
        sector_map = {
            "ICICIBANK": "Banking",
            "HDFCBANK": "Banking",
            "INFY": "IT",
            "TCS": "IT",
            "RELIANCE": "Oil & Gas",
            "TATAMOTORS": "Auto"
        }
        return sector_map.get(symbol, "General")
    
    def _assess_recommendation_quality(self, recommendation: TradeRecommendation, state: RecommendationState) -> float:
        """Assess the quality of a recommendation (0.0 to 1.0)."""
        quality_score = 0.8  # Base quality score
        
        # Adjust based on confidence
        if recommendation.confidence >= 8:
            quality_score += 0.1
        elif recommendation.confidence <= 6:
            quality_score -= 0.1
        
        # Adjust based on ROM
        if recommendation.expected_rom >= 10:
            quality_score += 0.05
        
        # Adjust based on SSR
        if recommendation.expected_ssr >= 5:
            quality_score += 0.05
        
        # Ensure score is within 0.0 to 1.0 range
        return max(0.0, min(1.0, quality_score))


# Example usage
async def main():
    """Example usage of Recommendation Agent."""
    from config.settings import get_settings
    from .mcp_client import MCPClient
    from .market_analyst import MarketAnalyst
    
    settings = get_settings()
    
    async with MCPClient(settings) as mcp_client:
        async with MarketAnalyst(mcp_client, settings) as market_analyst:
            recommendation_agent = RecommendationAgent(mcp_client, market_analyst, settings)
            
            try:
                # Get portfolio data
                portfolio = await mcp_client.get_portfolio_data()
                
                # Define filters
                filters = {
                    'min_ssr': 0.02,
                    'min_premium': 0.05,
                    'min_rom': 0.05,
                    'max_risk': 7
                }
                
                # Find opportunities
                recommendations = await recommendation_agent.find_opportunities(portfolio, filters)
                
                print(f"Found {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n{i}. {rec.symbol} {rec.option_type}")
                    print(f"   Type: {rec.recommendation_type}")
                    print(f"   Confidence: {rec.confidence}/10")
                    print(f"   ROM: {rec.expected_rom:.1f}%")
                    print(f"   SSR: {rec.expected_ssr:.1f}%")
                    print(f"   Reasoning: {rec.reasoning[:100]}...")
                
            except Exception as e:
                print(f"Recommendation analysis failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 