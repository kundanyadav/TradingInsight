"""
Pytest configuration and fixtures for TradingInsight tests.
"""

import pytest
import asyncio
from unittest.mock import Mock
from typing import Dict, Any

from config.settings import get_settings
from models.data_models import Position, Portfolio, SentimentAnalysis, TradeRecommendation


@pytest.fixture
def settings():
    """Provide application settings for tests."""
    return get_settings()


@pytest.fixture
def mock_mcp_client():
    """Provide a mock MCP client for tests."""
    client = Mock()
    client.get_portfolio_data = Mock(return_value=Portfolio(
        total_margin=100000.0,
        available_cash=50000.0,
        total_exposure=150000.0,
        positions=[],
        sector_exposure={"Banking": 0.6, "IT": 0.4},
        risk_score=6.5
    ))
    client.get_market_data = Mock(return_value={
        "symbol": "ICICIBANK",
        "current_price": 960.0,
        "change": 10.0,
        "change_percent": 1.05
    })
    client.get_option_chain = Mock(return_value=[
        {"strike": 950.0, "ce_premium": 50.0, "pe_premium": 45.0},
        {"strike": 960.0, "ce_premium": 40.0, "pe_premium": 55.0}
    ])
    return client


@pytest.fixture
def mock_portfolio_data():
    """Provide mock portfolio data for tests."""
    return {
        "total_margin": 100000.0,
        "available_cash": 50000.0,
        "total_exposure": 150000.0,
        "positions": [
            {
                "symbol": "ICICIBANK",
                "quantity": 100,
                "average_price": 950.0,
                "current_price": 960.0,
                "pnl": 1000.0,
                "margin_used": 50000.0,
                "premium_collected": 5000.0,
                "rom": 10.0,
                "ssr": 5.0,
                "risk_indicator": 6,
                "reward_risk_ratio": 833.33,
                "position_type": "short",
                "expiry": "2024-01-25T00:00:00",
                "strike_price": 950.0,
                "option_type": "PE"
            }
        ],
        "sector_exposure": {"Banking": 0.6, "IT": 0.4},
        "risk_score": 6.5
    }


@pytest.fixture
def mock_sentiment_analysis():
    """Provide mock sentiment analysis data for tests."""
    return SentimentAnalysis(
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


@pytest.fixture
def mock_trade_recommendation():
    """Provide mock trade recommendation data for tests."""
    return TradeRecommendation(
        recommendation_type="new trade",
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


@pytest.fixture
def mock_position():
    """Provide mock position data for tests."""
    from datetime import datetime
    return Position(
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
        reward_risk_ratio=833.33,
        position_type="short",
        expiry=datetime.now(),
        strike_price=950.0,
        option_type="PE"
    )


@pytest.fixture
def mock_portfolio(mock_position):
    """Provide mock portfolio data for tests."""
    return Portfolio(
        total_margin=100000.0,
        available_cash=50000.0,
        total_exposure=150000.0,
        positions=[mock_position],
        sector_exposure={"Banking": 0.6, "IT": 0.4},
        risk_score=6.5
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions for UI tests."""
    with pytest.MonkeyPatch().context() as m:
        # Mock common Streamlit functions
        m.setattr("streamlit.markdown", Mock())
        m.setattr("streamlit.columns", Mock(return_value=[Mock(), Mock()]))
        m.setattr("streamlit.metric", Mock())
        m.setattr("streamlit.button", Mock(return_value=False))
        m.setattr("streamlit.selectbox", Mock(return_value="Test"))
        m.setattr("streamlit.text_input", Mock(return_value="ICICIBANK"))
        m.setattr("streamlit.text_area", Mock(return_value="Test prompt"))
        m.setattr("streamlit.number_input", Mock(return_value=0.0))
        m.setattr("streamlit.expander", Mock())
        m.setattr("streamlit.dataframe", Mock())
        m.setattr("streamlit.plotly_chart", Mock())
        m.setattr("streamlit.error", Mock())
        m.setattr("streamlit.success", Mock())
        m.setattr("streamlit.info", Mock())
        m.setattr("streamlit.warning", Mock())
        m.setattr("streamlit.spinner", Mock())
        yield


@pytest.fixture
def mock_plotly():
    """Mock Plotly functions for chart tests."""
    with pytest.MonkeyPatch().context() as m:
        m.setattr("plotly.graph_objects.Figure", Mock())
        m.setattr("plotly.express.pie", Mock())
        m.setattr("plotly.express.bar", Mock())
        yield


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names."""
    for item in items:
        if "test_mcp_integration" in item.name or "test_server_availability" in item.name:
            item.add_marker(pytest.mark.integration)
        elif "test_data_models" in item.name or "test_services" in item.name:
            item.add_marker(pytest.mark.unit) 