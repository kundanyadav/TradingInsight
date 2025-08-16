"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any

from models.data_models import (
    Position, Portfolio, SentimentAnalysis, TradeRecommendation,
    FilterConstraints, StockScope, MarketHours, ApplicationSettings,
    PositionType, RiskLevel, RecommendationType
)


class TestPosition:
    """Test Position model."""
    
    def test_position_creation(self):
        """Test creating a valid position."""
        position = Position(
            symbol="ICICIBANK",
            quantity=100,
            average_price=950.0,
            current_price=960.0,
            pnl=1000.0,
            margin_used=50000.0,
            premium_collected=5000.0,
            rom=10.0,
            ssr=5.0,
            risk_indicator=6,
            reward_risk_ratio=1.2,
            position_type=PositionType.SHORT,
            expiry=datetime.now(),
            strike_price=950.0,
            option_type="PE"
        )
        
        assert position.symbol == "ICICIBANK"
        assert position.quantity == 100
        assert position.rom == 10.0
        assert position.ssr == 5.0
        assert position.risk_indicator == 6
    
    def test_position_validation(self):
        """Test position validation rules."""
        with pytest.raises(ValueError):
            Position(
                symbol="ICICIBANK",
                quantity=100,
                average_price=950.0,
                current_price=960.0,
                pnl=1000.0,
                margin_used=50000.0,
                premium_collected=5000.0,
                rom=150.0,  # Invalid: > 100
                ssr=5.0,
                risk_indicator=6,
                reward_risk_ratio=1.2,
                position_type=PositionType.SHORT,
                expiry=datetime.now(),
                strike_price=950.0,
                option_type="PE"
            )
    
    def test_position_risk_indicator_range(self):
        """Test risk indicator validation."""
        with pytest.raises(ValueError):
            Position(
                symbol="ICICIBANK",
                quantity=100,
                average_price=950.0,
                current_price=960.0,
                pnl=1000.0,
                margin_used=50000.0,
                premium_collected=5000.0,
                rom=10.0,
                ssr=5.0,
                risk_indicator=15,  # Invalid: > 10
                reward_risk_ratio=1.2,
                position_type=PositionType.SHORT,
                expiry=datetime.now(),
                strike_price=950.0,
                option_type="PE"
            )


class TestPortfolio:
    """Test Portfolio model."""
    
    def test_portfolio_creation(self):
        """Test creating a valid portfolio."""
        position = Position(
            symbol="ICICIBANK",
            quantity=100,
            average_price=950.0,
            current_price=960.0,
            pnl=1000.0,
            margin_used=50000.0,
            premium_collected=5000.0,
            rom=10.0,
            ssr=5.0,
            risk_indicator=6,
            reward_risk_ratio=1.2,
            position_type=PositionType.SHORT,
            expiry=datetime.now(),
            strike_price=950.0,
            option_type="PE"
        )
        
        portfolio = Portfolio(
            total_margin=100000.0,
            available_cash=50000.0,
            total_exposure=150000.0,
            positions=[position],
            sector_exposure={"Banking": 0.6, "IT": 0.4},
            risk_score=6.5
        )
        
        assert portfolio.total_margin == 100000.0
        assert len(portfolio.positions) == 1
        assert portfolio.risk_score == 6.5
    
    def test_portfolio_validation(self):
        """Test portfolio validation rules."""
        with pytest.raises(ValueError):
            Portfolio(
                total_margin=-1000.0,  # Invalid: negative
                available_cash=50000.0,
                total_exposure=150000.0,
                positions=[],
                sector_exposure={},
                risk_score=6.5
            )


class TestSentimentAnalysis:
    """Test SentimentAnalysis model."""
    
    def test_sentiment_analysis_creation(self):
        """Test creating a valid sentiment analysis."""
        sentiment = SentimentAnalysis(
            symbol="ICICIBANK",
            short_term_sentiment="bullish",
            short_term_target=(950.0, 980.0),
            short_term_confidence=7.5,
            medium_term_sentiment="bullish",
            medium_term_target=(980.0, 1020.0),
            medium_term_confidence=8.0,
            key_drivers=["Strong fundamentals", "Technical breakout"],
            risks=["Market volatility", "Sector rotation"],
            summary="ICICIBANK shows strong momentum",
            financial_analysis={"growth": 15.2},
            intrinsic_value={"valuation": "Fair"},
            social_sentiment={"rating": "Buy"}
        )
        
        assert sentiment.symbol == "ICICIBANK"
        assert sentiment.short_term_sentiment == "bullish"
        assert sentiment.short_term_target == (950.0, 980.0)
    
    def test_sentiment_validation(self):
        """Test sentiment validation rules."""
        with pytest.raises(ValueError):
            SentimentAnalysis(
                symbol="ICICIBANK",
                short_term_sentiment="invalid",  # Invalid sentiment
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


class TestTradeRecommendation:
    """Test TradeRecommendation model."""
    
    def test_trade_recommendation_creation(self):
        """Test creating a valid trade recommendation."""
        recommendation = TradeRecommendation(
            recommendation_type=RecommendationType.NEW_TRADE,
            symbol="ICICIBANK",
            option_type="PE",
            strike_price=950.0,
            expiry="2024-01-25",
            quantity=100,
            price_range=(50.0, 60.0),
            confidence=7.5,
            trade_driver="Technical breakout",
            risk_assessment="Medium risk",
            expected_rom=12.0,
            expected_ssr=8.0,
            reasoning="Strong technical momentum",
            portfolio_impact="Adds banking exposure"
        )
        
        assert recommendation.symbol == "ICICIBANK"
        assert recommendation.confidence == 7.5
        assert recommendation.expected_rom == 12.0
    
    def test_trade_recommendation_validation(self):
        """Test trade recommendation validation rules."""
        with pytest.raises(ValueError):
            TradeRecommendation(
                recommendation_type=RecommendationType.NEW_TRADE,
                symbol="ICICIBANK",
                option_type="PE",
                strike_price=950.0,
                expiry="2024-01-25",
                quantity=100,
                price_range=(50.0, 60.0),
                confidence=15.0,  # Invalid: > 10
                trade_driver="Technical breakout",
                risk_assessment="Medium risk",
                expected_rom=12.0,
                expected_ssr=8.0,
                reasoning="Strong technical momentum",
                portfolio_impact="Adds banking exposure"
            )


class TestFilterConstraints:
    """Test FilterConstraints model."""
    
    def test_filter_constraints_creation(self):
        """Test creating valid filter constraints."""
        filters = FilterConstraints(
            min_ssr=0.05,
            min_premium=0.10,
            min_rom=0.08,
            max_risk=7
        )
        
        assert filters.min_ssr == 0.05
        assert filters.max_risk == 7
    
    def test_filter_constraints_defaults(self):
        """Test filter constraints default values."""
        filters = FilterConstraints()
        
        assert filters.min_ssr == 0.02
        assert filters.min_premium == 0.05
        assert filters.min_rom == 0.05
        assert filters.max_risk == 7


class TestStockScope:
    """Test StockScope model."""
    
    def test_stock_scope_creation(self):
        """Test creating a valid stock scope."""
        scope = StockScope(
            approved_stocks=["ICICIBANK", "HDFCBANK", "RELIANCE"],
            sectors=["Banking", "Oil & Gas"]
        )
        
        assert len(scope.approved_stocks) == 3
        assert "ICICIBANK" in scope.approved_stocks
    
    def test_stock_approval(self):
        """Test stock approval functionality."""
        scope = StockScope(
            approved_stocks=["ICICIBANK", "HDFCBANK"],
            sectors=["Banking"]
        )
        
        assert scope.is_stock_approved("ICICIBANK") == True
        assert scope.is_stock_approved("INVALID") == False


class TestMarketHours:
    """Test MarketHours model."""
    
    def test_market_hours_creation(self):
        """Test creating market hours."""
        hours = MarketHours(
            start_time="09:15",
            end_time="15:30",
            timezone="Asia/Kolkata"
        )
        
        assert hours.start_time == "09:15"
        assert hours.end_time == "15:30"
        assert hours.timezone == "Asia/Kolkata"


class TestApplicationSettings:
    """Test ApplicationSettings model."""
    
    def test_application_settings_creation(self):
        """Test creating application settings."""
        stock_scope = StockScope(
            approved_stocks=["ICICIBANK"],
            sectors=["Banking"]
        )
        
        filter_constraints = FilterConstraints()
        
        market_hours = MarketHours()
        
        settings = ApplicationSettings(
            stock_scope=stock_scope,
            filter_constraints=filter_constraints,
            market_hours=market_hours,
            cache_ttl=300,
            max_retries=3,
            retry_delay=1.0
        )
        
        assert settings.cache_ttl == 300
        assert settings.max_retries == 3
        assert len(settings.stock_scope.approved_stocks) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 