"""
Recommendation View UI Component for Kite Trading Recommendation App.
Displays trade recommendations, filter constraints, and portfolio impact analysis.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.recommendation_service import RecommendationService, TradeOpportunity, FilterConstraints, RecommendationResult


async def render_recommendation_dashboard(recommendation_service: RecommendationService):
    """Render the main recommendation dashboard."""
    st.markdown("## 💡 Trade Recommendations Dashboard")
    
    # Filter settings
    render_filter_settings()
    
    # Get recommendations
    if st.button("🔍 Get Recommendations", type="primary"):
        await get_recommendations(recommendation_service)
    
    # Display recommendations
    if "recommendations" in st.session_state:
        display_recommendations(st.session_state["recommendations"])
    
    # Portfolio impact analysis
    if "portfolio_impact" in st.session_state:
        render_portfolio_impact(st.session_state["portfolio_impact"])
    
    # Risk assessment
    if "risk_assessment" in st.session_state:
        render_risk_assessment(st.session_state["risk_assessment"])


def render_filter_settings():
    """Render filter settings interface."""
    st.markdown("### 🔧 Filter Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Risk & Return Filters")
        min_ssr = st.number_input(
            "Minimum SSR (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="Spot to Strike Ratio"
        )
        
        min_premium = st.number_input(
            "Minimum Premium (₹)",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=10.0,
            help="Minimum premium collected"
        )
        
        min_rom = st.number_input(
            "Minimum ROM (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="Return on Margin"
        )
    
    with col2:
        st.markdown("#### ⚠️ Risk Management")
        max_risk_indicator = st.number_input(
            "Maximum Risk Indicator",
            min_value=1,
            max_value=10,
            value=10,
            step=1,
            help="Maximum risk level (1-10)"
        )
        
        # Stock scope
        st.markdown("#### 📋 Stock Scope")
        approved_stocks = st.text_area(
            "Approved Stocks (one per line)",
            value="ICICIBANK\nRELIANCE\nTCS\nINFY\nHDFCBANK",
            height=100,
            help="Stocks to analyze for recommendations"
        )
    
    # Store filter settings
    st.session_state.filter_constraints = FilterConstraints(
        min_ssr=min_ssr,
        min_premium=min_premium,
        min_rom=min_rom,
        max_risk_indicator=max_risk_indicator,
        approved_stocks=[stock.strip() for stock in approved_stocks.split('\n') if stock.strip()]
    )


async def get_recommendations(recommendation_service: RecommendationService):
    """Get trade recommendations based on filters."""
    try:
        with st.spinner("Finding trade opportunities..."):
            filters = st.session_state.get("filter_constraints")
            if not filters:
                st.error("Please configure filter settings first")
                return
            
            result = await recommendation_service.get_trade_recommendations(filters)
            
            st.session_state["recommendations"] = result.opportunities
            st.session_state["portfolio_impact"] = result.portfolio_impact
            st.session_state["risk_assessment"] = result.risk_assessment
            st.session_state["recommendation_summary"] = result.recommendations_summary
            
            st.success(f"Found {len(result.opportunities)} trade opportunities!")
            
    except Exception as e:
        st.error(f"Failed to get recommendations: {e}")


def display_recommendations(opportunities: List[TradeOpportunity]):
    """Display trade recommendations."""
    st.markdown("### 📋 Trade Recommendations")
    
    if not opportunities:
        st.info("No trade opportunities found based on current filters.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Opportunities", len(opportunities))
    
    with col2:
        avg_rom = sum(opp.rom for opp in opportunities) / len(opportunities)
        st.metric("Average ROM", f"{avg_rom:.2f}%")
    
    with col3:
        avg_confidence = sum(opp.confidence for opp in opportunities) / len(opportunities)
        st.metric("Average Confidence", f"{avg_confidence:.1f}/10")
    
    with col4:
        total_premium = sum(opp.premium for opp in opportunities)
        st.metric("Total Premium", f"₹{total_premium:,.0f}")
    
    # Filter and sort options
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Confidence", "ROM", "Premium", "Risk Indicator", "SSR"]
        )
    
    with col2:
        trade_type_filter = st.selectbox(
            "Filter by Trade Type",
            ["All"] + list(set(opp.trade_type for opp in opportunities))
        )
    
    # Sort opportunities
    if sort_by == "Confidence":
        sorted_opportunities = sorted(opportunities, key=lambda x: x.confidence, reverse=True)
    elif sort_by == "ROM":
        sorted_opportunities = sorted(opportunities, key=lambda x: x.rom, reverse=True)
    elif sort_by == "Premium":
        sorted_opportunities = sorted(opportunities, key=lambda x: x.premium, reverse=True)
    elif sort_by == "Risk Indicator":
        sorted_opportunities = sorted(opportunities, key=lambda x: x.risk_indicator)
    elif sort_by == "SSR":
        sorted_opportunities = sorted(opportunities, key=lambda x: x.ssr, reverse=True)
    else:
        sorted_opportunities = opportunities
    
    # Filter by trade type
    if trade_type_filter != "All":
        sorted_opportunities = [opp for opp in sorted_opportunities if opp.trade_type == trade_type_filter]
    
    # Display opportunities
    for i, opportunity in enumerate(sorted_opportunities, 1):
        with st.expander(f"{i}. {opportunity.symbol} {opportunity.option_type} - {opportunity.trade_type.title()}"):
            display_opportunity_details(opportunity)


def display_opportunity_details(opportunity: TradeOpportunity):
    """Display detailed opportunity information."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Trade Details")
        st.write(f"**Symbol:** {opportunity.symbol}")
        st.write(f"**Option Type:** {opportunity.option_type}")
        st.write(f"**Strike Price:** ₹{opportunity.strike_price:,.2f}")
        st.write(f"**Premium:** ₹{opportunity.premium:,.2f}")
        st.write(f"**Margin Required:** ₹{opportunity.margin_required:,.0f}")
    
    with col2:
        st.markdown("#### 📈 Performance Metrics")
        st.write(f"**ROM:** {opportunity.rom:.2f}%")
        st.write(f"**SSR:** {opportunity.ssr:.2f}%")
        st.write(f"**Risk Indicator:** {opportunity.risk_indicator}/10")
        st.write(f"**Confidence:** {opportunity.confidence:.1f}/10")
        st.write(f"**Trade Type:** {opportunity.trade_type.title()}")
    
    # Reasoning
    st.markdown("#### 🎯 Reasoning")
    st.write(opportunity.reasoning)
    
    # Action points
    st.markdown("#### 📋 Action Points")
    if opportunity.action_points:
        for i, action in enumerate(opportunity.action_points, 1):
            st.write(f"{i}. {action}")
    else:
        st.info("No specific action points provided")
    
    # Performance chart
    render_opportunity_chart(opportunity)


def render_opportunity_chart(opportunity: TradeOpportunity):
    """Render opportunity performance chart."""
    st.markdown("#### 📊 Performance Visualization")
    
    # Create radar chart for opportunity metrics
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[opportunity.rom, opportunity.ssr, opportunity.confidence * 10, 
           10 - opportunity.risk_indicator, opportunity.premium / 100],
        theta=['ROM (%)', 'SSR (%)', 'Confidence', 'Safety', 'Premium (₹100)'],
        fill='toself',
        name=opportunity.symbol
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 20]
            )),
        showlegend=False,
        title=f"{opportunity.symbol} Opportunity Metrics"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_portfolio_impact(portfolio_impact: Dict[str, Any]):
    """Render portfolio impact analysis."""
    st.markdown("### 📊 Portfolio Impact Analysis")
    
    if not portfolio_impact:
        st.info("No portfolio impact data available")
        return
    
    # Impact metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Margin Addition",
            f"₹{portfolio_impact.get('total_margin_addition', 0):,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Premium Addition",
            f"₹{portfolio_impact.get('total_premium_addition', 0):,.0f}",
            delta=None
        )
    
    with col3:
        roi_change = portfolio_impact.get('roi_change', 0)
        st.metric(
            "ROI Change",
            f"{roi_change:+.2f}%",
            delta=f"{roi_change:+.2f}%"
        )
    
    with col4:
        utilization_change = portfolio_impact.get('margin_utilization_change', 0)
        st.metric(
            "Margin Utilization Change",
            f"{utilization_change:+.1f}%",
            delta=f"{utilization_change:+.1f}%"
        )
    
    # Impact visualization
    render_portfolio_impact_chart(portfolio_impact)


def render_portfolio_impact_chart(portfolio_impact: Dict[str, Any]):
    """Render portfolio impact chart."""
    st.markdown("#### 📈 Impact Visualization")
    
    # Create impact comparison chart
    metrics = ["Current", "After Recommendations"]
    margin_values = [
        portfolio_impact.get('new_total_margin', 0) - portfolio_impact.get('total_margin_addition', 0),
        portfolio_impact.get('new_total_margin', 0)
    ]
    premium_values = [
        portfolio_impact.get('new_total_premium', 0) - portfolio_impact.get('total_premium_addition', 0),
        portfolio_impact.get('new_total_premium', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Margin',
        x=metrics,
        y=margin_values,
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        name='Total Premium',
        x=metrics,
        y=premium_values,
        marker_color='green'
    ))
    
    fig.update_layout(
        title="Portfolio Impact: Before vs After Recommendations",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_assessment(risk_assessment: Dict[str, Any]):
    """Render risk assessment."""
    st.markdown("### ⚠️ Risk Assessment")
    
    if not risk_assessment:
        st.info("No risk assessment data available")
        return
    
    # Risk metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Risk Level",
            risk_assessment.get("risk_level", "Unknown"),
            delta=None
        )
    
    with col2:
        st.metric(
            "Risk Score",
            f"{risk_assessment.get('risk_score', 0):.1f}/10",
            delta=None
        )
    
    with col3:
        st.metric(
            "Recommendations",
            risk_assessment.get("recommendation_count", 0),
            delta=None
        )
    
    # Risk factors
    st.markdown("#### ⚠️ Risk Factors")
    risk_factors = risk_assessment.get("risk_factors", [])
    if risk_factors:
        for i, factor in enumerate(risk_factors, 1):
            st.write(f"{i}. {factor}")
    else:
        st.info("No specific risk factors identified")
    
    # Risk gauge
    render_risk_gauge(risk_assessment)


def render_risk_gauge(risk_assessment: Dict[str, Any]):
    """Render risk gauge chart."""
    st.markdown("#### 📊 Risk Gauge")
    
    risk_score = risk_assessment.get("risk_score", 0)
    risk_level = risk_assessment.get("risk_level", "Unknown")
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Risk Level: {risk_level}"},
        delta={'reference': 5},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 3], 'color': "green"},
                {'range': [3, 7], 'color': "yellow"},
                {'range': [7, 10], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_recommendation_summary():
    """Render recommendation summary."""
    if "recommendation_summary" in st.session_state:
        st.markdown("### 📝 Recommendation Summary")
        st.write(st.session_state["recommendation_summary"])


def render_opportunity_comparison(opportunities: List[TradeOpportunity]):
    """Render opportunity comparison chart."""
    if not opportunities:
        return
    
    st.markdown("### 📊 Opportunity Comparison")
    
    # Prepare data for comparison
    symbols = [opp.symbol for opp in opportunities]
    rom_values = [opp.rom for opp in opportunities]
    confidence_values = [opp.confidence for opp in opportunities]
    risk_values = [opp.risk_indicator for opp in opportunities]
    
    # Create comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='ROM (%)',
        x=symbols,
        y=rom_values,
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        name='Confidence',
        x=symbols,
        y=[c * 10 for c in confidence_values],  # Scale to 0-100
        marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        name='Risk Indicator',
        x=symbols,
        y=risk_values,
        marker_color='red'
    ))
    
    fig.update_layout(
        title="Opportunity Comparison",
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_trade_type_distribution(opportunities: List[TradeOpportunity]):
    """Render trade type distribution."""
    if not opportunities:
        return
    
    st.markdown("### 📊 Trade Type Distribution")
    
    # Count trade types
    trade_types = {}
    for opp in opportunities:
        trade_type = opp.trade_type
        trade_types[trade_type] = trade_types.get(trade_type, 0) + 1
    
    # Create pie chart
    fig = px.pie(
        values=list(trade_types.values()),
        names=list(trade_types.keys()),
        title="Distribution by Trade Type"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True) 