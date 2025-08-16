"""
Tests for UI components.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import List, Dict, Any

from ui.portfolio_view import render_portfolio_dashboard
from ui.analysis_view import render_analysis_dashboard
from ui.recommendation_view import render_recommendation_dashboard
from services.portfolio_service import PortfolioService
from services.analysis_service import AnalysisService
from services.recommendation_service import RecommendationService
from config.settings import get_settings


class TestPortfolioView:
    """Test portfolio view components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_portfolio_service = Mock(spec=PortfolioService)
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    async def test_render_portfolio_dashboard(self, mock_metric, mock_columns, mock_markdown):
        """Test portfolio dashboard rendering."""
        # Mock portfolio service methods
        self.mock_portfolio_service.get_portfolio_analysis = Mock(return_value={
            'total_positions': 5,
            'total_margin': 100000.0,
            'total_premium': 25000.0,
            'total_roi': 25.0,
            'risk_distribution': {'Low Risk': 2, 'Medium Risk': 2, 'High Risk': 1},
            'sector_analysis': {'Banking': 0.6, 'IT': 0.4},
            'positions': []
        })
        
        # Test dashboard rendering
        await render_portfolio_dashboard(self.mock_portfolio_service)
        
        # Verify that streamlit functions were called
        mock_markdown.assert_called()
        mock_columns.assert_called()
    
    @patch('streamlit.expander')
    @patch('streamlit.dataframe')
    def test_render_position_details(self, mock_dataframe, mock_expander):
        """Test position details rendering."""
        # Mock position data
        position_data = {
            'symbol': 'ICICIBANK',
            'quantity': 100,
            'premium_collected': 5000.0,
            'rom': 10.0,
            'ssr': 5.0,
            'risk_indicator': 6
        }
        
        # Test position details rendering
        from ui.portfolio_view import render_position_details
        render_position_details(position_data)
        
        # Verify that streamlit functions were called
        mock_expander.assert_called()
    
    @patch('plotly.graph_objects.Figure')
    @patch('streamlit.plotly_chart')
    def test_render_risk_distribution(self, mock_plotly_chart, mock_figure):
        """Test risk distribution chart rendering."""
        risk_data = {'Low Risk': 2, 'Medium Risk': 3, 'High Risk': 1}
        
        from ui.portfolio_view import render_risk_distribution
        render_risk_distribution(risk_data)
        
        # Verify that plotly chart was created
        mock_figure.assert_called()


class TestAnalysisView:
    """Test analysis view components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_analysis_service = Mock(spec=AnalysisService)
    
    @patch('streamlit.markdown')
    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    async def test_render_analysis_dashboard(self, mock_button, mock_selectbox, mock_markdown):
        """Test analysis dashboard rendering."""
        # Mock analysis service methods
        self.mock_analysis_service.get_stock_analysis = Mock(return_value={
            'symbol': 'ICICIBANK',
            'sentiment': 'bullish',
            'confidence': 7.5,
            'short_term_target': (950.0, 980.0),
            'medium_term_target': (980.0, 1020.0)
        })
        
        # Test dashboard rendering
        await render_analysis_dashboard(self.mock_analysis_service)
        
        # Verify that streamlit functions were called
        mock_markdown.assert_called()
        mock_selectbox.assert_called()
    
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    async def test_render_stock_analysis(self, mock_button, mock_text_input):
        """Test stock analysis rendering."""
        # Mock stock analysis data
        analysis_data = {
            'symbol': 'ICICIBANK',
            'sentiment': 'bullish',
            'confidence': 7.5,
            'risk_level': 'Medium Risk',
            'short_term_target': 980.0,
            'medium_term_target': 1020.0,
            'key_factors': ['Strong fundamentals', 'Technical breakout']
        }
        
        from ui.analysis_view import display_stock_analysis
        display_stock_analysis(analysis_data)
        
        # Verify that analysis was displayed
        assert True  # If no exception, test passes
    
    @patch('plotly.graph_objects.Figure')
    @patch('streamlit.plotly_chart')
    def test_render_sentiment_gauge(self, mock_plotly_chart, mock_figure):
        """Test sentiment gauge chart rendering."""
        from ui.analysis_view import render_sentiment_gauge
        render_sentiment_gauge('bullish', 7.5)
        
        # Verify that plotly chart was created
        mock_figure.assert_called()


class TestRecommendationView:
    """Test recommendation view components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
        self.mock_recommendation_service = Mock(spec=RecommendationService)
    
    @patch('streamlit.markdown')
    @patch('streamlit.number_input')
    @patch('streamlit.text_area')
    async def test_render_recommendation_dashboard(self, mock_text_area, mock_number_input, mock_markdown):
        """Test recommendation dashboard rendering."""
        # Mock recommendation service methods
        self.mock_recommendation_service.get_trade_recommendations = Mock(return_value={
            'opportunities': [
                {
                    'symbol': 'ICICIBANK',
                    'option_type': 'PE',
                    'strike_price': 950.0,
                    'premium': 5000.0,
                    'rom': 10.0,
                    'ssr': 5.0,
                    'confidence': 7.5,
                    'trade_type': 'new'
                }
            ],
            'portfolio_impact': {
                'total_margin_addition': 50000.0,
                'total_premium_addition': 5000.0,
                'roi_change': 5.0
            }
        })
        
        # Test dashboard rendering
        await render_recommendation_dashboard(self.mock_recommendation_service)
        
        # Verify that streamlit functions were called
        mock_markdown.assert_called()
        mock_number_input.assert_called()
    
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_render_filter_settings(self, mock_metric, mock_columns):
        """Test filter settings rendering."""
        from ui.recommendation_view import render_filter_settings
        render_filter_settings()
        
        # Verify that filter settings were rendered
        mock_columns.assert_called()
        mock_metric.assert_called()
    
    @patch('streamlit.expander')
    def test_display_recommendations(self, mock_expander):
        """Test recommendations display."""
        opportunities = [
            {
                'symbol': 'ICICIBANK',
                'option_type': 'PE',
                'strike_price': 950.0,
                'premium': 5000.0,
                'rom': 10.0,
                'ssr': 5.0,
                'confidence': 7.5,
                'trade_type': 'new',
                'reasoning': 'Strong technical momentum',
                'action_points': ['Buy at market', 'Set stop loss']
            }
        ]
        
        from ui.recommendation_view import display_recommendations
        display_recommendations(opportunities)
        
        # Verify that recommendations were displayed
        mock_expander.assert_called()


class TestUIComponentIntegration:
    """Test UI component integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
    
    def test_ui_component_imports(self):
        """Test that all UI components can be imported."""
        # Test portfolio view imports
        from ui.portfolio_view import (
            render_portfolio_dashboard,
            render_portfolio_summary,
            render_risk_distribution,
            render_sector_analysis,
            render_position_details
        )
        
        # Test analysis view imports
        from ui.analysis_view import (
            render_analysis_dashboard,
            render_stock_analysis,
            render_sector_analysis,
            render_market_overview,
            render_custom_analysis
        )
        
        # Test recommendation view imports
        from ui.recommendation_view import (
            render_recommendation_dashboard,
            render_filter_settings,
            display_recommendations,
            render_portfolio_impact
        )
        
        assert True  # If no import errors, test passes
    
    def test_ui_component_functions_callable(self):
        """Test that UI component functions are callable."""
        from ui.portfolio_view import render_portfolio_dashboard
        from ui.analysis_view import render_analysis_dashboard
        from ui.recommendation_view import render_recommendation_dashboard
        
        assert callable(render_portfolio_dashboard)
        assert callable(render_analysis_dashboard)
        assert callable(render_recommendation_dashboard)


class TestUIErrorHandling:
    """Test UI error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = get_settings()
    
    @patch('streamlit.error')
    async def test_portfolio_service_error_handling(self, mock_error):
        """Test handling of portfolio service errors."""
        mock_portfolio_service = Mock()
        mock_portfolio_service.get_portfolio_analysis = Mock(side_effect=Exception("Service error"))
        
        # Test error handling in portfolio dashboard
        await render_portfolio_dashboard(mock_portfolio_service)
        
        # Verify error was displayed
        mock_error.assert_called()
    
    @patch('streamlit.error')
    async def test_analysis_service_error_handling(self, mock_error):
        """Test handling of analysis service errors."""
        mock_analysis_service = Mock()
        mock_analysis_service.get_stock_analysis = Mock(side_effect=Exception("Analysis error"))
        
        # Test error handling in analysis dashboard
        await render_analysis_dashboard(mock_analysis_service)
        
        # Verify error was displayed
        mock_error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__]) 