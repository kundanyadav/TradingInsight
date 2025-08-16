"""
Portfolio View UI Component for Kite Trading Recommendation App.
Displays portfolio dashboard with sector-wise grouping and position analysis.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.portfolio_service import PortfolioService, PortfolioAnalysis, PositionAnalysis, SectorAnalysis


async def render_portfolio_dashboard(portfolio_service: PortfolioService):
    """Render the main portfolio dashboard."""
    st.markdown("## 📊 Portfolio Dashboard")
    
    try:
        # Get portfolio analysis
        with st.spinner("Loading portfolio analysis..."):
            portfolio_analysis = st.session_state.get('portfolio_analysis')
            if not portfolio_analysis:
                portfolio_analysis = await portfolio_service.get_portfolio_analysis()
                st.session_state.portfolio_analysis = portfolio_analysis
        
        # Portfolio Summary Cards
        render_portfolio_summary(portfolio_analysis)
        
        # Risk Distribution Chart
        render_risk_distribution(portfolio_analysis)
        
        # Sector Analysis
        render_sector_analysis(portfolio_analysis)
        
        # Position Details
        render_position_details(portfolio_analysis)
        
    except Exception as e:
        st.error(f"Failed to load portfolio data: {e}")
        st.info("Please check your MCP server connection.")


def render_portfolio_summary(analysis: PortfolioAnalysis):
    """Render portfolio summary cards."""
    st.markdown("### Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Margin",
            value=f"₹{analysis.total_margin:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Available Cash",
            value=f"₹{analysis.available_cash:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Premium",
            value=f"₹{analysis.total_premium_collected:,.0f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Overall ROI",
            value=f"{analysis.overall_roi:.2f}%",
            delta=None
        )
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Risk Score",
            value=f"{analysis.overall_risk_score:.1f}/10",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Margin Utilization",
            value=f"{analysis.margin_utilization:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Positions",
            value=len(analysis.position_analyses),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Sectors",
            value=len(analysis.sector_analyses),
            delta=None
        )


def render_risk_distribution(analysis: PortfolioAnalysis):
    """Render risk distribution chart."""
    st.markdown("### Risk Distribution")
    
    # Create risk distribution data
    risk_data = analysis.risk_distribution
    risk_df = pd.DataFrame([
        {"Risk Level": risk, "Count": count}
        for risk, count in risk_data.items()
    ])
    
    if not risk_df.empty:
        # Create pie chart
        fig = px.pie(
            risk_df, 
            values='Count', 
            names='Risk Level',
            color_discrete_map={
                'Low Risk': '#28a745',
                'Medium Risk': '#ffc107',
                'High Risk': '#dc3545'
            }
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No positions to display risk distribution.")


def render_sector_analysis(analysis: PortfolioAnalysis):
    """Render sector analysis."""
    st.markdown("### Sector Analysis")
    
    if not analysis.sector_analyses:
        st.info("No sector data available.")
        return
    
    # Create sector data for display
    sector_data = []
    for sector_analysis in analysis.sector_analyses:
        sector_data.append({
            "Sector": sector_analysis.sector,
            "Total Margin": sector_analysis.total_margin,
            "Position Count": sector_analysis.position_count,
            "Exposure %": sector_analysis.exposure_percentage,
            "Total Premium": sector_analysis.total_premium_collected,
            "Avg ROM": sector_analysis.average_rom,
            "Avg SSR": sector_analysis.average_ssr,
            "Avg Risk": sector_analysis.average_risk_indicator,
            "Risk Group": sector_analysis.risk_group
        })
    
    sector_df = pd.DataFrame(sector_data)
    
    # Display sector table
    st.dataframe(
        sector_df,
        column_config={
            "Total Margin": st.column_config.NumberColumn(format="₹%.0f"),
            "Total Premium": st.column_config.NumberColumn(format="₹%.0f"),
            "Exposure %": st.column_config.NumberColumn(format="%.1f%%"),
            "Avg ROM": st.column_config.NumberColumn(format="%.2f%%"),
            "Avg SSR": st.column_config.NumberColumn(format="%.2f%%"),
            "Avg Risk": st.column_config.NumberColumn(format="%.1f")
        },
        hide_index=True
    )
    
    # Sector exposure chart
    if len(sector_data) > 1:
        fig = px.bar(
            sector_df,
            x="Sector",
            y="Exposure %",
            color="Risk Group",
            color_discrete_map={
                'Low Risk': '#28a745',
                'Medium Risk': '#ffc107',
                'High Risk': '#dc3545'
            },
            title="Sector Exposure by Risk Group"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def render_position_details(analysis: PortfolioAnalysis):
    """Render position details."""
    st.markdown("### Position Details")
    
    if not analysis.position_analyses:
        st.info("No positions to display.")
        return
    
    # Create position data for display
    position_data = []
    for pos_analysis in analysis.position_analyses:
        position = pos_analysis.position
        position_data.append({
            "Symbol": position.symbol,
            "Quantity": position.quantity,
            "Current Price": position.current_price,
            "P&L": position.pnl,
            "Margin Used": position.margin_used,
            "Premium Collected": position.premium_collected,
            "ROM": position.rom,
            "SSR": position.ssr,
            "Risk Indicator": position.risk_indicator,
            "ROI %": pos_analysis.roi_percentage,
            "Reward/Risk": pos_analysis.reward_risk_ratio,
            "Risk Group": pos_analysis.risk_group,
            "Margin Efficiency": pos_analysis.margin_efficiency
        })
    
    position_df = pd.DataFrame(position_data)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox(
            "Filter by Risk Group",
            ["All"] + list(position_df["Risk Group"].unique())
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["ROM", "ROI %", "Risk Indicator", "Reward/Risk", "Premium Collected"]
        )
    
    # Apply filters
    if risk_filter != "All":
        position_df = position_df[position_df["Risk Group"] == risk_filter]
    
    # Sort data
    position_df = position_df.sort_values(sort_by, ascending=False)
    
    # Display position table
    st.dataframe(
        position_df,
        column_config={
            "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
            "P&L": st.column_config.NumberColumn(format="₹%.0f"),
            "Margin Used": st.column_config.NumberColumn(format="₹%.0f"),
            "Premium Collected": st.column_config.NumberColumn(format="₹%.0f"),
            "ROM": st.column_config.NumberColumn(format="%.2f%%"),
            "SSR": st.column_config.NumberColumn(format="%.2f%%"),
            "ROI %": st.column_config.NumberColumn(format="%.2f%%"),
            "Reward/Risk": st.column_config.NumberColumn(format="%.2f"),
            "Margin Efficiency": st.column_config.NumberColumn(format="%.3f")
        },
        hide_index=True
    )
    
    # Position performance chart
    if len(position_data) > 1:
        fig = px.scatter(
            position_df,
            x="ROM",
            y="Risk Indicator",
            size="Premium Collected",
            color="Risk Group",
            hover_data=["Symbol", "ROI %"],
            color_discrete_map={
                'Low Risk': '#28a745',
                'Medium Risk': '#ffc107',
                'High Risk': '#dc3545'
            },
            title="Position Performance: ROM vs Risk"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


async def render_position_details_modal(portfolio_service: PortfolioService, symbol: str):
    """Render detailed position analysis in a modal."""
    try:
        with st.spinner(f"Loading details for {symbol}..."):
            position_analysis = await portfolio_service.get_position_details(symbol)
            
            if position_analysis:
                st.markdown(f"### {symbol} Position Details")
                
                position = position_analysis.position
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Current Price", f"₹{position.current_price:.2f}")
                    st.metric("Quantity", position.quantity)
                    st.metric("P&L", f"₹{position.pnl:,.0f}")
                    st.metric("Margin Used", f"₹{position.margin_used:,.0f}")
                
                with col2:
                    st.metric("Premium Collected", f"₹{position.premium_collected:,.0f}")
                    st.metric("ROM", f"{position.rom:.2f}%")
                    st.metric("SSR", f"{position.ssr:.2f}%")
                    st.metric("Risk Indicator", f"{position.risk_indicator}/10")
                
                # Additional metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("ROI %", f"{position_analysis.roi_percentage:.2f}%")
                
                with col2:
                    st.metric("Reward/Risk Ratio", f"{position_analysis.reward_risk_ratio:.2f}")
                
                with col3:
                    st.metric("Risk Group", position_analysis.risk_group)
                
                # Position chart
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode="gauge+number+delta",
                    value=position.rom,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "ROM %"},
                    delta={'reference': 10},
                    gauge={
                        'axis': {'range': [None, 20]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 5], 'color': "lightgray"},
                            {'range': [5, 10], 'color': "gray"},
                            {'range': [10, 20], 'color': "darkgray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 15
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning(f"No position found for {symbol}")
                
    except Exception as e:
        st.error(f"Failed to load position details: {e}")


def render_portfolio_metrics(analysis: PortfolioAnalysis):
    """Render key portfolio metrics."""
    st.markdown("### Key Metrics")
    
    # Create metrics grid
    metrics_data = {
        "Metric": [
            "Total Portfolio Value",
            "Margin Utilization",
            "Average ROM",
            "Average Risk Score",
            "Premium Collection Rate",
            "Risk-Adjusted Return"
        ],
        "Value": [
            f"₹{analysis.total_margin + analysis.available_cash:,.0f}",
            f"{analysis.margin_utilization:.1f}%",
            f"{analysis.overall_roi:.2f}%",
            f"{analysis.overall_risk_score:.1f}/10",
            f"₹{analysis.total_premium_collected:,.0f}",
            f"{analysis.overall_roi / max(analysis.overall_risk_score, 1):.2f}%"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, hide_index=True) 