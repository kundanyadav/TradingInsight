"""
Main Streamlit application for Kite Trading Recommendation App.
Entry point with session state management, MCP server connection, and navigation.
"""

import streamlit as st
import asyncio
import logging
from datetime import datetime
import pytz
from typing import Dict, Any, Optional

from config.settings import get_settings, is_market_open, get_default_filters
from services.mcp_client import MCPClient
from services.market_analyst import MarketAnalyst
from services.recommendation_agent import RecommendationAgent
from services.portfolio_service import PortfolioService
from services.analysis_service import AnalysisService
from services.recommendation_service import RecommendationService
from ui.portfolio_view import render_portfolio_dashboard
from ui.analysis_view import render_analysis_dashboard
from ui.recommendation_view import render_recommendation_dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Kite Trading Recommendation App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None
    
    if 'filters' not in st.session_state:
        st.session_state.filters = get_default_filters()
    
    if 'stock_scope' not in st.session_state:
        settings = get_settings()
        st.session_state.stock_scope = settings.stock_scope.approved_stocks
    
    if 'market_analyses' not in st.session_state:
        st.session_state.market_analyses = {}
    
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    
    if 'mcp_connected' not in st.session_state:
        st.session_state.mcp_connected = False
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    
    # Initialize services
    if 'portfolio_service' not in st.session_state:
        st.session_state.portfolio_service = None
    
    if 'analysis_service' not in st.session_state:
        st.session_state.analysis_service = None
    
    if 'recommendation_service' not in st.session_state:
        st.session_state.recommendation_service = None


def check_market_status():
    """Check and display market status."""
    market_open = is_market_open()
    ist_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        status_color = "status-online" if market_open else "status-offline"
        status_text = "🟢 Market Open" if market_open else "🔴 Market Closed"
        st.markdown(f'<span class="status-indicator {status_color}"></span>{status_text}', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**IST Time:** {ist_time.strftime('%H:%M:%S')}")
    
    with col3:
        if market_open:
            st.success("✅ Trading Active")
        else:
            st.warning("⚠️ Outside Trading Hours")


async def connect_to_mcp_server():
    """Connect to MCP server and initialize services."""
    try:
        settings = get_settings()
        
        # Initialize MCP client
        mcp_client = MCPClient(settings)
        await mcp_client.connect()
        
        # Initialize market analyst
        market_analyst = MarketAnalyst(mcp_client, settings)
        
        # Initialize recommendation agent
        recommendation_agent = RecommendationAgent(mcp_client, market_analyst, settings)
        
        # Initialize portfolio service
        portfolio_service = PortfolioService(mcp_client, settings)
        
        # Initialize analysis service
        analysis_service = AnalysisService(market_analyst, mcp_client, settings)
        
        # Initialize recommendation service
        recommendation_service = RecommendationService(recommendation_agent, mcp_client, portfolio_service, settings)
        
        st.session_state.mcp_connected = True
        st.session_state.mcp_client = mcp_client
        st.session_state.market_analyst = market_analyst
        st.session_state.recommendation_agent = recommendation_agent
        st.session_state.portfolio_service = portfolio_service
        st.session_state.analysis_service = analysis_service
        st.session_state.recommendation_service = recommendation_service
        
        logger.info("Successfully connected to MCP server and initialized all services")
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        st.error(f"Failed to connect to MCP server: {e}")
        st.session_state.mcp_connected = False
        return False


def render_sidebar():
    """Render the sidebar with navigation and settings."""
    st.sidebar.title("📊 Trading Insight")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Dashboard", "📈 Portfolio", "🔍 Analysis", "💡 Recommendations", "⚙️ Settings"]
    )
    
    st.sidebar.markdown("---")
    
    # Market Status
    st.sidebar.subheader("Market Status")
    market_open = is_market_open()
    if market_open:
        st.sidebar.success("Market Open")
    else:
        st.sidebar.error("Market Closed")
    
    # Connection Status
    st.sidebar.subheader("Connection Status")
    if st.session_state.mcp_connected:
        st.sidebar.success("MCP Server Connected")
    else:
        st.sidebar.error("MCP Server Disconnected")
        if st.sidebar.button("🔄 Reconnect"):
            asyncio.run(connect_to_mcp_server())
    
    # Quick Actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    if st.sidebar.button("📊 Update Portfolio"):
        if st.session_state.mcp_connected:
            asyncio.run(refresh_portfolio_data())
    
    return page


async def refresh_portfolio_data():
    """Refresh portfolio data from MCP server."""
    try:
        if st.session_state.mcp_connected and st.session_state.portfolio_service:
            portfolio_analysis = await st.session_state.portfolio_service.get_portfolio_analysis()
            st.session_state.portfolio_analysis = portfolio_analysis
            st.session_state.last_refresh = datetime.now()
            st.success("Portfolio data updated successfully!")
    except Exception as e:
        st.error(f"Failed to refresh portfolio data: {e}")


def render_dashboard():
    """Render the main dashboard."""
    st.markdown('<h1 class="main-header">Kite Trading Recommendation App</h1>', unsafe_allow_html=True)
    
    # Market status
    check_market_status()
    
    # Connection status
    if not st.session_state.mcp_connected:
        st.warning("⚠️ Not connected to MCP server. Please check connection.")
        if st.button("🔌 Connect to MCP Server"):
            asyncio.run(connect_to_mcp_server())
        return
    
    # Dashboard content
    st.markdown("### Welcome to Trading Insight!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Quick Stats")
        if st.session_state.portfolio_service:
            try:
                portfolio_analysis = st.session_state.get('portfolio_analysis')
                if portfolio_analysis:
                    st.metric("Total Margin", f"₹{portfolio_analysis.total_margin:,.0f}")
                    st.metric("Available Cash", f"₹{portfolio_analysis.available_cash:,.0f}")
                    st.metric("Total Premium", f"₹{portfolio_analysis.total_premium_collected:,.0f}")
                    st.metric("Overall ROI", f"{portfolio_analysis.overall_roi:.2f}%")
                else:
                    st.info("Click 'Update Portfolio' to load data")
            except Exception as e:
                st.error(f"Error loading portfolio data: {e}")
    
    with col2:
        st.markdown("#### 🎯 Quick Actions")
        if st.button("📈 View Portfolio"):
            st.switch_page("Portfolio")
        if st.button("🔍 Market Analysis"):
            st.switch_page("Analysis")
        if st.button("💡 Get Recommendations"):
            st.switch_page("Recommendations")
    
    # Recent activity
    st.markdown("### Recent Activity")
    if st.session_state.last_refresh:
        st.info(f"Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No recent activity")


def render_portfolio():
    """Render the portfolio page."""
    st.markdown("## 📈 Portfolio Analysis")
    
    if not st.session_state.mcp_connected:
        st.error("Not connected to MCP server")
        return
    
    if not st.session_state.portfolio_service:
        st.error("Portfolio service not initialized")
        return
    
    # Render portfolio dashboard
    asyncio.run(render_portfolio_dashboard(st.session_state.portfolio_service))


def render_analysis():
    """Render the analysis page."""
    st.markdown("## 🔍 Market Analysis")
    
    if not st.session_state.mcp_connected:
        st.error("Not connected to MCP server")
        return
    
    if not st.session_state.analysis_service:
        st.error("Analysis service not initialized")
        return
    
    # Render analysis dashboard
    asyncio.run(render_analysis_dashboard(st.session_state.analysis_service))


def render_recommendations():
    """Render the recommendations page."""
    st.markdown("## 💡 Trade Recommendations")
    
    if not st.session_state.mcp_connected:
        st.error("Not connected to MCP server")
        return
    
    if not st.session_state.recommendation_service:
        st.error("Recommendation service not initialized")
        return
    
    # Render recommendation dashboard
    asyncio.run(render_recommendation_dashboard(st.session_state.recommendation_service))


def render_settings():
    """Render the settings page."""
    st.markdown("## ⚙️ Settings")
    
    settings = get_settings()
    
    st.markdown("### Application Settings")
    
    # Market hours
    st.markdown("#### Trading Hours")
    st.info(f"Market opens: {settings.trading_hours.start_time}")
    st.info(f"Market closes: {settings.trading_hours.end_time}")
    
    # Stock scope
    st.markdown("#### Approved Stocks")
    approved_stocks = st.text_area(
        "Approved stocks (one per line)",
        value="\n".join(settings.stock_scope.approved_stocks),
        height=200
    )
    
    # Default filters
    st.markdown("#### Default Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        default_min_ssr = st.number_input("Default Min SSR (%)", 0.0, 100.0, settings.default_filters.min_ssr)
        default_min_premium = st.number_input("Default Min Premium (₹)", 0.0, 10000.0, settings.default_filters.min_premium)
    
    with col2:
        default_min_rom = st.number_input("Default Min ROM (%)", 0.0, 100.0, settings.default_filters.min_rom)
        default_max_risk = st.number_input("Default Max Risk", 1, 10, settings.default_filters.max_risk_indicator)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        st.info("Note: Some settings may require application restart to take effect.")


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Connect to MCP server if not connected
    if not st.session_state.mcp_connected:
        if st.button("🔌 Connect to MCP Server"):
            asyncio.run(connect_to_mcp_server())
        else:
            st.warning("Please connect to MCP server to use the application.")
            return
    
    # Render sidebar and get current page
    page = render_sidebar()
    
    # Render page content based on selection
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "📈 Portfolio":
        render_portfolio()
    elif page == "🔍 Analysis":
        render_analysis()
    elif page == "💡 Recommendations":
        render_recommendations()
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main() 