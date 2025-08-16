"""
Analysis View UI Component for Kite Trading Recommendation App.
Displays market analysis, sentiment analysis, and custom analysis features.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.analysis_service import AnalysisService, MarketAnalysis, SectorAnalysis, CustomAnalysis


async def render_analysis_dashboard(analysis_service: AnalysisService):
    """Render the main analysis dashboard."""
    st.markdown("## 🔍 Market Analysis Dashboard")
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Stock Analysis", "Sector Analysis", "Market Overview", "Custom Analysis"]
    )
    
    if analysis_type == "Stock Analysis":
        await render_stock_analysis(analysis_service)
    elif analysis_type == "Sector Analysis":
        await render_sector_analysis(analysis_service)
    elif analysis_type == "Market Overview":
        await render_market_overview(analysis_service)
    elif analysis_type == "Custom Analysis":
        await render_custom_analysis(analysis_service)


async def render_stock_analysis(analysis_service: AnalysisService):
    """Render stock analysis interface."""
    st.markdown("### 📈 Stock Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol", "ICICIBANK", placeholder="e.g., ICICIBANK, RELIANCE")
    
    with col2:
        if st.button("🔍 Analyze Stock", type="primary"):
            if symbol:
                await analyze_stock(analysis_service, symbol.upper())
            else:
                st.error("Please enter a stock symbol")
    
    # Display cached analysis if available
    cache_key = f"stock_analysis_{symbol.upper()}"
    if cache_key in st.session_state:
        display_stock_analysis(st.session_state[cache_key])


async def analyze_stock(analysis_service: AnalysisService, symbol: str):
    """Analyze a specific stock."""
    try:
        with st.spinner(f"Analyzing {symbol}..."):
            analysis = await analysis_service.get_stock_analysis(symbol)
            st.session_state[f"stock_analysis_{symbol}"] = analysis
            display_stock_analysis(analysis)
            st.success(f"Analysis completed for {symbol}")
    except Exception as e:
        st.error(f"Failed to analyze {symbol}: {e}")


def display_stock_analysis(analysis: MarketAnalysis):
    """Display stock analysis results."""
    st.markdown(f"### 📊 Analysis Results for {analysis.symbol}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Sentiment",
            analysis.sentiment.title(),
            delta=None,
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Confidence",
            f"{analysis.confidence:.1f}/10",
            delta=None
        )
    
    with col3:
        st.metric(
            "Risk Level",
            analysis.risk_level,
            delta=None
        )
    
    with col4:
        st.metric(
            "Analysis Date",
            analysis.analysis_date.strftime("%m/%d"),
            delta=None
        )
    
    # Price targets
    st.markdown("#### 🎯 Price Targets")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Short-term Target (1 month)",
            f"₹{analysis.short_term_target:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Medium-term Target (3 months)",
            f"₹{analysis.medium_term_target:,.2f}",
            delta=None
        )
    
    # Key factors
    st.markdown("#### 🚀 Key Factors")
    if analysis.key_factors:
        for i, factor in enumerate(analysis.key_factors, 1):
            st.write(f"{i}. {factor}")
    else:
        st.info("No key factors identified")
    
    # Sentiment gauge chart
    render_sentiment_gauge(analysis.sentiment, analysis.confidence)
    
    # Risk assessment
    render_risk_assessment(analysis.risk_level, analysis.confidence)


async def render_sector_analysis(analysis_service: AnalysisService):
    """Render sector analysis interface."""
    st.markdown("### 🏭 Sector Analysis")
    
    # Sector selection
    sectors = ["Banking", "IT", "Pharma", "Auto", "FMCG", "Energy", "Real Estate"]
    selected_sector = st.selectbox("Select Sector", sectors)
    
    if st.button("🔍 Analyze Sector", type="primary"):
        await analyze_sector(analysis_service, selected_sector)
    
    # Display cached sector analysis
    cache_key = f"sector_analysis_{selected_sector}"
    if cache_key in st.session_state:
        display_sector_analysis(st.session_state[cache_key])


async def analyze_sector(analysis_service: AnalysisService, sector: str):
    """Analyze a specific sector."""
    try:
        with st.spinner(f"Analyzing {sector} sector..."):
            analysis = await analysis_service.get_sector_analysis(sector)
            st.session_state[f"sector_analysis_{sector}"] = analysis
            display_sector_analysis(analysis)
            st.success(f"Sector analysis completed for {sector}")
    except Exception as e:
        st.error(f"Failed to analyze {sector} sector: {e}")


def display_sector_analysis(analysis: SectorAnalysis):
    """Display sector analysis results."""
    st.markdown(f"### 📊 {analysis.sector} Sector Analysis")
    
    # Sector metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Sector Sentiment",
            analysis.sentiment.title(),
            delta=None
        )
    
    with col2:
        st.metric(
            "Confidence",
            f"{analysis.confidence:.1f}/10",
            delta=None
        )
    
    with col3:
        st.metric(
            "Analysis Date",
            analysis.analysis_date.strftime("%m/%d"),
            delta=None
        )
    
    # Top performers
    st.markdown("#### 🏆 Top Performers")
    if analysis.top_performers:
        for i, stock in enumerate(analysis.top_performers, 1):
            st.write(f"{i}. {stock}")
    else:
        st.info("No top performers identified")
    
    # Key drivers
    st.markdown("#### 🚀 Key Drivers")
    if analysis.key_drivers:
        for i, driver in enumerate(analysis.key_drivers, 1):
            st.write(f"{i}. {driver}")
    else:
        st.info("No key drivers identified")
    
    # Risk factors
    st.markdown("#### ⚠️ Risk Factors")
    if analysis.risk_factors:
        for i, risk in enumerate(analysis.risk_factors, 1):
            st.write(f"{i}. {risk}")
    else:
        st.info("No risk factors identified")
    
    # Sector sentiment chart
    render_sector_sentiment_chart(analysis)


async def render_market_overview(analysis_service: AnalysisService):
    """Render market overview interface."""
    st.markdown("### 📈 Market Overview")
    
    if st.button("🔄 Refresh Market Overview", type="primary"):
        await analyze_market_overview(analysis_service)
    
    # Display cached market overview
    if "market_overview" in st.session_state:
        display_market_overview(st.session_state["market_overview"])


async def analyze_market_overview(analysis_service: AnalysisService):
    """Analyze overall market."""
    try:
        with st.spinner("Analyzing market overview..."):
            overview = await analysis_service.get_market_overview()
            st.session_state["market_overview"] = overview
            display_market_overview(overview)
            st.success("Market overview updated")
    except Exception as e:
        st.error(f"Failed to analyze market overview: {e}")


def display_market_overview(overview: Dict[str, Any]):
    """Display market overview results."""
    st.markdown("### 📊 Market Overview")
    
    # Market sentiment
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Market Sentiment",
            overview.get("sentiment", "Neutral").title(),
            delta=None
        )
    
    with col2:
        st.metric(
            "Confidence",
            f"{overview.get('confidence', 0):.1f}/10",
            delta=None
        )
    
    with col3:
        st.metric(
            "Analysis Date",
            overview.get("analysis_date", datetime.now()).strftime("%m/%d"),
            delta=None
        )
    
    # Key drivers
    st.markdown("#### 🚀 Key Market Drivers")
    key_drivers = overview.get("key_drivers", [])
    if key_drivers:
        for i, driver in enumerate(key_drivers, 1):
            st.write(f"{i}. {driver}")
    else:
        st.info("No key drivers identified")
    
    # Risk factors
    st.markdown("#### ⚠️ Market Risk Factors")
    risk_factors = overview.get("risk_factors", [])
    if risk_factors:
        for i, risk in enumerate(risk_factors, 1):
            st.write(f"{i}. {risk}")
    else:
        st.info("No risk factors identified")
    
    # Market outlook
    st.markdown("#### 🔮 Market Outlook")
    outlook = overview.get("outlook", "")
    if outlook:
        st.write(outlook)
    else:
        st.info("No outlook available")
    
    # Sector performance
    st.markdown("#### 📊 Sector Performance")
    sector_performance = overview.get("sector_performance", {})
    if sector_performance:
        render_sector_performance_chart(sector_performance)
    else:
        st.info("No sector performance data available")


async def render_custom_analysis(analysis_service: AnalysisService):
    """Render custom analysis interface."""
    st.markdown("### 🎯 Custom Analysis")
    
    # Custom prompt input
    prompt = st.text_area(
        "Enter your custom analysis prompt",
        placeholder="e.g., Analyze the impact of RBI policy changes on banking stocks",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Market Analysis", "Sector Analysis", "Stock Analysis", "General"]
        )
    
    with col2:
        if st.button("🔍 Analyze", type="primary"):
            if prompt:
                await analyze_custom(analysis_service, prompt, analysis_type)
            else:
                st.error("Please enter an analysis prompt")
    
    # Display cached custom analysis
    if "custom_analysis" in st.session_state:
        display_custom_analysis(st.session_state["custom_analysis"])


async def analyze_custom(analysis_service: AnalysisService, prompt: str, analysis_type: str):
    """Perform custom analysis."""
    try:
        with st.spinner("Performing custom analysis..."):
            analysis = await analysis_service.get_custom_analysis(prompt)
            st.session_state["custom_analysis"] = analysis
            display_custom_analysis(analysis)
            st.success("Custom analysis completed")
    except Exception as e:
        st.error(f"Failed to perform custom analysis: {e}")


def display_custom_analysis(analysis: CustomAnalysis):
    """Display custom analysis results."""
    st.markdown("### 📊 Custom Analysis Results")
    
    # Analysis metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Confidence",
            f"{analysis.confidence:.1f}/10",
            delta=None
        )
    
    with col2:
        st.metric(
            "Key Points",
            len(analysis.key_points),
            delta=None
        )
    
    with col3:
        st.metric(
            "Recommendations",
            len(analysis.recommendations),
            delta=None
        )
    
    # Analysis text
    st.markdown("#### 📝 Analysis")
    st.write(analysis.analysis)
    
    # Key points
    st.markdown("#### 🎯 Key Points")
    if analysis.key_points:
        for i, point in enumerate(analysis.key_points, 1):
            st.write(f"{i}. {point}")
    else:
        st.info("No key points identified")
    
    # Recommendations
    st.markdown("#### 💡 Recommendations")
    if analysis.recommendations:
        for i, rec in enumerate(analysis.recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.info("No recommendations provided")


def render_sentiment_gauge(sentiment: str, confidence: float):
    """Render sentiment gauge chart."""
    st.markdown("#### 📊 Sentiment Gauge")
    
    # Convert sentiment to numeric value
    sentiment_map = {"bullish": 1, "neutral": 0.5, "bearish": 0}
    sentiment_value = sentiment_map.get(sentiment.lower(), 0.5)
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=sentiment_value * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Sentiment: {sentiment.title()}"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "red"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_risk_assessment(risk_level: str, confidence: float):
    """Render risk assessment chart."""
    st.markdown("#### ⚠️ Risk Assessment")
    
    risk_map = {"Low Risk": 1, "Medium Risk": 2, "High Risk": 3}
    risk_value = risk_map.get(risk_level, 2)
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=risk_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Risk Level: {risk_level}"},
        gauge={
            'axis': {'range': [None, 3]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 1], 'color': "green"},
                {'range': [1, 2], 'color': "yellow"},
                {'range': [2, 3], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 2.5
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_sector_sentiment_chart(analysis: SectorAnalysis):
    """Render sector sentiment chart."""
    st.markdown("#### 📊 Sector Sentiment")
    
    sentiment_data = {
        "Sentiment": [analysis.sentiment],
        "Confidence": [analysis.confidence],
        "Sector": [analysis.sector]
    }
    
    df = pd.DataFrame(sentiment_data)
    
    fig = px.bar(
        df,
        x="Sector",
        y="Confidence",
        color="Sentiment",
        color_discrete_map={
            "bullish": "#28a745",
            "neutral": "#ffc107",
            "bearish": "#dc3545"
        },
        title=f"{analysis.sector} Sector Sentiment"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_sector_performance_chart(sector_performance: Dict[str, Any]):
    """Render sector performance chart."""
    if not sector_performance:
        return
    
    sectors = list(sector_performance.keys())
    performances = list(sector_performance.values())
    
    fig = px.bar(
        x=sectors,
        y=performances,
        title="Sector Performance",
        labels={"x": "Sector", "y": "Performance"}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True) 