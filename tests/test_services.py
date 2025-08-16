"""
Unit tests for services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from typing import List, Dict, Any

from services.portfolio_service import PortfolioService
from services.analysis_service import AnalysisService
from services.recommendation_service import RecommendationService
from config.settings import get_settings
from models.data_models import Position, Portfolio, SentimentAnalysis, TradeRecommendation


class TestPortfolioService:
    """Test PortfolioService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_mcp_client = Mock()
        self.portfolio_service = PortfolioService(self.mock_mcp_client, self.settings)
    
    def test_portfolio_service_initialization(self):
        """Test portfolio service initialization."""
        assert self.portfolio_service is not None
        assert self.portfolio_service.settings == self.settings
    
    def test_calculate_rom(self):
        """Test ROM calculation."""
        rom = self.portfolio_service._calculate_rom(5000.0, 50000.0)
        assert rom == 10.0  # 5000/50000 * 100
    
    def test_calculate_ssr(self):
        """Test SSR calculation."""
        ssr = self.portfolio_service._calculate_ssr(1000.0, 950.0)
        assert ssr == 5.0  # (1000-950)/1000 * 100
    
    def test_classify_risk_group(self):
        """Test risk group classification."""
        assert self.portfolio_service._classify_risk_group(3) == "Low Risk"
        assert self.portfolio_service._classify_risk_group(6) == "Medium Risk"
        assert self.portfolio_service._classify_risk_group(9) == "High Risk"
    
    def test_calculate_reward_risk_ratio(self):
        """Test reward-risk ratio calculation."""
        ratio = self.portfolio_service._calculate_reward_risk_ratio(5000.0, 6)
        assert ratio == 833.33  # 5000/6
    
    async def test_get_portfolio_analysis(self):
        """Test portfolio analysis retrieval."""
        # Mock portfolio data
        mock_portfolio = Portfolio(
            total_margin=100000.0,
            available_cash=50000.0,
            total_exposure=150000.0,
            positions=[],
            sector_exposure={"Banking": 0.6, "IT": 0.4},
            risk_score=6.5
        )
        
        self.mock_mcp_client.get_portfolio_data = AsyncMock(return_value=mock_portfolio)
        
        analysis = await self.portfolio_service.get_portfolio_analysis()
        
        assert analysis is not None
        assert analysis.total_positions == 0
        assert analysis.total_margin == 100000.0


class TestAnalysisService:
    """Test AnalysisService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_market_analyst = Mock()
        self.mock_mcp_client = Mock()
        self.analysis_service = AnalysisService(self.mock_market_analyst, self.mock_mcp_client, self.settings)
    
    def test_analysis_service_initialization(self):
        """Test analysis service initialization."""
        assert self.analysis_service is not None
        assert self.analysis_service.settings == self.settings
    
    async def test_get_stock_analysis(self):
        """Test stock analysis retrieval."""
        # Mock sentiment analysis
        mock_sentiment = SentimentAnalysis(
            symbol="ICICIBANK",
            short_term_sentiment="bullish",
            short_term_target=(950.0, 980.0),
            short_term_confidence=7.5,
            medium_term_sentiment="bullish",
            medium_term_target=(980.0, 1020.0),
            medium_term_confidence=8.0,
            key_drivers=["Strong fundamentals"],
            risks=["Market volatility"],
            summary="ICICIBANK shows strong momentum",
            financial_analysis={"growth": 15.2},
            intrinsic_value={"valuation": "Fair"},
            social_sentiment={"rating": "Buy"}
        )
        
        self.mock_market_analyst.analyze_stock = AsyncMock(return_value=mock_sentiment)
        
        analysis = await self.analysis_service.get_stock_analysis("ICICIBANK")
        
        assert analysis is not None
        assert analysis.symbol == "ICICIBANK"
        assert analysis.short_term_sentiment == "bullish"
    
    async def test_get_sector_analysis(self):
        """Test sector analysis retrieval."""
        # Mock sector analysis
        mock_sector_analysis = {
            "sector": "Banking",
            "sentiment": "bullish",
            "confidence": 7.5,
            "top_performers": ["ICICIBANK", "HDFCBANK"],
            "key_drivers": ["RBI policy", "Economic growth"],
            "risk_factors": ["Interest rate risk", "NPA concerns"],
            "analysis_date": datetime.now()
        }
        
        self.mock_market_analyst.analyze_sector = AsyncMock(return_value=mock_sector_analysis)
        
        analysis = await self.analysis_service.get_sector_analysis("Banking")
        
        assert analysis is not None
        assert analysis.sector == "Banking"
        assert analysis.sentiment == "bullish"
    
    async def test_get_custom_analysis(self):
        """Test custom analysis retrieval."""
        # Mock custom analysis
        mock_custom_analysis = {
            "analysis": "Custom analysis result",
            "confidence": 8.0,
            "key_points": ["Point 1", "Point 2"],
            "recommendations": ["Recommendation 1"]
        }
        
        self.mock_market_analyst.analyze_custom = AsyncMock(return_value=mock_custom_analysis)
        
        analysis = await self.analysis_service.get_custom_analysis("Analyze ICICIBANK")
        
        assert analysis is not None
        assert analysis.confidence == 8.0


class TestRecommendationService:
    """Test RecommendationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_recommendation_agent = Mock()
        self.mock_mcp_client = Mock()
        self.mock_portfolio_service = Mock()
        self.recommendation_service = RecommendationService(
            self.mock_recommendation_agent,
            self.mock_mcp_client,
            self.mock_portfolio_service,
            self.settings
        )
    
    def test_recommendation_service_initialization(self):
        """Test recommendation service initialization."""
        assert self.recommendation_service is not None
        assert self.recommendation_service.settings == self.settings
    
    async def test_get_trade_recommendations(self):
        """Test trade recommendations retrieval."""
        # Mock trade opportunities
        mock_opportunities = [
            {
                "symbol": "ICICIBANK",
                "option_type": "PE",
                "strike_price": 950.0,
                "premium": 5000.0,
                "margin_required": 50000.0,
                "rom": 10.0,
                "ssr": 5.0,
                "risk_indicator": 6,
                "confidence": 7.5,
                "trade_type": "new",
                "reasoning": "Strong technical momentum",
                "action_points": ["Buy at market", "Set stop loss"]
            }
        ]
        
        self.mock_recommendation_agent.get_trade_recommendations = AsyncMock(return_value=mock_opportunities)
        
        # Mock filter constraints
        from models.data_models import FilterConstraints
        filters = FilterConstraints(min_ssr=0.02, min_premium=0.05, min_rom=0.05, max_risk=7)
        
        result = await self.recommendation_service.get_trade_recommendations(filters)
        
        assert result is not None
        assert len(result.opportunities) == 1
        assert result.opportunities[0].symbol == "ICICIBANK"


class TestServiceIntegration:
    """Test service integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
    
    def test_service_dependencies(self):
        """Test that services can be initialized with dependencies."""
        mock_mcp_client = Mock()
        mock_market_analyst = Mock()
        mock_recommendation_agent = Mock()
        mock_portfolio_service = Mock()
        
        # Test all services can be created
        portfolio_service = PortfolioService(mock_mcp_client, self.settings)
        analysis_service = AnalysisService(mock_market_analyst, mock_mcp_client, self.settings)
        recommendation_service = RecommendationService(
            mock_recommendation_agent, mock_mcp_client, mock_portfolio_service, self.settings
        )
        
        assert portfolio_service is not None
        assert analysis_service is not None
        assert recommendation_service is not None


if __name__ == "__main__":
    pytest.main([__file__]) 