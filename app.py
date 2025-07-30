import streamlit as st
from news import aggregate_news_and_macro
from opportunity_scanner import scan_opportunities, DEFAULT_STOCK_LIST, DEFAULT_THRESHOLDS
from greeks import summarize_portfolio_greeks, per_position_greeks
from risk import margin_utilization_alert, stress_test, calculate_var
from logging_utils import log_portfolio_summary, log_recommendation, log_user_action, read_log_history
from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import json
import re
import os

# Store user-submitted news links and active feature in session state
if 'user_news_links' not in st.session_state:
    st.session_state['user_news_links'] = []
if 'active_feature' not in st.session_state:
    st.session_state['active_feature'] = None
if 'last_portfolio' not in st.session_state:
    st.session_state['last_portfolio'] = None

SETTINGS_FILE = "user_settings.json"

def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def profile_settings_sidebar():
    st.sidebar.subheader("👤 Profile & Settings")
    settings = load_user_settings()
    # Preferred stock list
    st.sidebar.markdown("**Preferred Stock List (comma-separated):**")
    preferred_stocks = st.sidebar.text_area("Preferred Stocks", value=settings.get("preferred_stocks", ""), key="profile_stocks")
    # Default thresholds
    st.sidebar.markdown("**Default Thresholds:**")
    def_val = lambda k, v: float(settings.get("thresholds", {}).get(k, v))
    t_min_premium = st.sidebar.number_input("Min Premium", value=def_val("min_premium", 10.0), min_value=0.0, key="profile_min_premium")
    t_max_risk = st.sidebar.number_input("Max Risk", value=def_val("max_risk", 0.05), min_value=0.0, max_value=1.0, key="profile_max_risk")
    t_min_liquidity = st.sidebar.number_input("Min Open Interest", value=def_val("min_liquidity", 1000.0), min_value=0.0, key="profile_min_liquidity")
    t_min_time_decay = st.sidebar.number_input("Min Time Decay", value=def_val("min_time_decay", 0.01), min_value=0.0, key="profile_min_time_decay")
    # Custom news sources
    st.sidebar.markdown("**Custom News Sources (one per line):**")
    custom_news = st.sidebar.text_area("News URLs", value="\n".join(settings.get("custom_news", [])), key="profile_news")
    if st.sidebar.button("Save Settings"):
        new_settings = {
            "preferred_stocks": preferred_stocks,
            "thresholds": {
                "min_premium": t_min_premium,
                "max_risk": t_max_risk,
                "min_liquidity": t_min_liquidity,
                "min_time_decay": t_min_time_decay,
            },
            "custom_news": [line.strip() for line in custom_news.splitlines() if line.strip()]
        }
        save_user_settings(new_settings)
        st.sidebar.success("Settings saved!")
    # Quick apply buttons for Opportunity Scanner
    if preferred_stocks.strip():
        if st.sidebar.button("Apply Preferred Stocks to Scanner"):
            st.session_state["oppscanner_stock_input"] = preferred_stocks
    if st.sidebar.button("Apply Default Thresholds to Scanner"):
        st.session_state["oppscanner_thresholds"] = {
            "min_premium": t_min_premium,
            "max_risk": t_max_risk,
            "min_liquidity": t_min_liquidity,
            "min_time_decay": t_min_time_decay,
        }
    if custom_news.strip():
        if st.sidebar.button("Add Custom News to Dashboard"):
            for url in [line.strip() for line in custom_news.splitlines() if line.strip()]:
                if url not in st.session_state.get('user_news_links', []):
                    st.session_state.setdefault('user_news_links', []).append(url)

def render_news_dashboard():
    st.subheader("📰 Market News & Macroeconomic Indicators (India & USA)")
    st.markdown("**Submit your own news links (URLs):**")
    user_link = st.text_input("Paste a news link (URL) and press Enter", "", key="user_news_input")
    if user_link:
        if user_link not in st.session_state['user_news_links']:
            st.session_state['user_news_links'].append(user_link)
            st.success("News link added!")
        st.session_state['active_feature'] = 'news'
    if st.session_state['user_news_links']:
        st.markdown("**User-submitted News Links:**")
        for link in st.session_state['user_news_links']:
            st.markdown(f"- [{link}]({link})")
    for country in ["India", "USA"]:
        st.markdown(f"#### {country}")
        news_macro = aggregate_news_and_macro(country)
        news = news_macro.get("news", [])
        macro = news_macro.get("macro_indicators", [])
        st.markdown("**Top News Headlines:**")
        for article in news:
            st.markdown(f"- [{article.get('title')}]({article.get('url')}) <sub>{article.get('source', '')}</sub>")
            if article.get('description'):
                st.caption(article['description'])
        st.markdown("**Macroeconomic Indicators:**")
        for indicator in macro:
            st.markdown(f"- [{indicator['name']}]({indicator['url']})")

def get_recent_feedback_summary(n=5):
    """Return a summary string of the most recent n feedback entries (accept/reject with reasons)."""
    logs = read_log_history()
    feedback_logs = [log for log in logs if log['event_type'] in ('user_action:accepted', 'user_action:rejected')]
    if not feedback_logs:
        return "No recent feedback yet."
    summary_lines = []
    for log in feedback_logs[-n:]:
        action = 'ACCEPTED' if log['event_type'] == 'user_action:accepted' else 'REJECTED'
        opp = log['data']
        reason = opp.get('reason', '')
        summary_lines.append(f"{action}: {opp.get('symbol', '')} {opp.get('type', '')} {opp.get('strike', '')} | Reason: {reason}")
    return '\n'.join(summary_lines)

NIFTY50_LIST = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HDFC", "KOTAKBANK", "LT", "SBIN", "AXISBANK",
    "ITC", "HCLTECH", "BHARTIARTL", "ASIANPAINT", "BAJFINANCE", "MARUTI", "SUNPHARMA", "ULTRACEMCO", "TITAN",
    "NESTLEIND", "WIPRO", "POWERGRID", "ONGC", "ADANIPORTS", "HINDUNILVR", "JSWSTEEL", "TATAMOTORS", "COALINDIA",
    "GRASIM", "NTPC", "TATASTEEL", "BPCL", "DIVISLAB", "BRITANNIA", "CIPLA", "EICHERMOT", "HEROMOTOCO", "HDFCLIFE",
    "INDUSINDBK", "M&M", "SHREECEM", "BAJAJFINSV", "BAJAJ-AUTO", "DRREDDY", "UPL", "TECHM", "SBILIFE", "APOLLOHOSP"
]

def render_opportunity_scanner():
    st.subheader("🔎 Opportunity Scanner (AI-Powered)")
    st.markdown("Scan option chains for new trade opportunities in the stocks you specify. All context (news, sentiment, positions, greeks, technicals, feedback) is used.")
    st.markdown("**Recent Feedback:**")
    feedback_context = get_recent_feedback_summary(5)
    st.info(feedback_context)
    # Use session state for quick apply
    stock_input = st.text_area(
        "Stocks to scan (comma-separated, e.g. RELIANCE, TCS, INFY, IRCTC, DMART)",
        value=st.session_state.get("oppscanner_stock_input", ""),
        key="oppscanner_stock_input",
        help="Enter stock symbols separated by commas."
    )
    scan_list = sorted(set([s.strip().upper() for s in stock_input.split(",") if s.strip()]))
    st.markdown(f"**Scan list ({len(scan_list)} stocks):**")
    st.info(", ".join(scan_list) if scan_list else "No stocks selected.")
    # Use session state for quick apply thresholds
    th = st.session_state.get("oppscanner_thresholds", DEFAULT_THRESHOLDS)
    st.markdown("**Thresholds:**")
    min_premium = st.number_input("Minimum Premium", value=float(th["min_premium"]), min_value=0.0, key="oppscanner_min_premium")
    max_risk = st.number_input("Maximum Risk (fraction of margin)", value=float(th["max_risk"]), min_value=0.0, max_value=1.0, key="oppscanner_max_risk")
    min_liquidity = st.number_input("Minimum Open Interest", value=float(th["min_liquidity"]), min_value=0.0, key="oppscanner_min_liquidity")
    min_time_decay = st.number_input("Minimum Time Decay (Theta)", value=float(th["min_time_decay"]), min_value=0.0, key="oppscanner_min_time_decay")
    thresholds = {
        "min_premium": min_premium,
        "max_risk": max_risk,
        "min_liquidity": min_liquidity,
        "min_time_decay": min_time_decay,
    }
    if st.button("Scan for Opportunities (AI)", type="primary"):
        if not scan_list:
            st.warning("Please enter at least one stock symbol to scan.")
            return
        with st.spinner("Gathering context and generating AI recommendations..."):
            import asyncio
            from analyzer import Analyzer
            analyzer = Analyzer()
            news_sentiment = asyncio.run(analyzer.analyze_news_sentiment_for_stocks(scan_list))
            st.markdown("**News Sentiment by Stock:**")
            for symbol in scan_list:
                st.markdown(f"**{symbol}:** {news_sentiment.get(symbol, 'No sentiment available')}")
            llm_output = asyncio.run(analyzer.generate_full_context_recommendations(scan_list, feedback_context))
        st.markdown("**AI-Powered Recommendations:**")
        import re
        json_match = re.search(r'(\[.*?\])', llm_output, re.DOTALL)
        if json_match:
            try:
                recs = json.loads(json_match.group(1))
                df = pd.DataFrame(recs)
                st.dataframe(df[["action", "symbol", "option_type", "strike", "expiry", "rationale", "expected_outcome", "risk_management"]], use_container_width=True)
                st.markdown("**Provide Feedback on Recommendations:**")
                for i, rec in enumerate(recs):
                    col1, col2, col3 = st.columns([3,1,2])
                    with col1:
                        st.markdown(f"{rec['action']} {rec['symbol']} {rec['option_type']} {rec['strike']} {rec['expiry']} | Rationale: {rec['rationale']}")
                    with col3:
                        reason = st.text_input(f"Reason for feedback {i}", "", key=f"reason_ai_{i}")
                    with col2:
                        if st.button(f"Accept AI {i}"):
                            log_user_action("accepted", {**rec, "reason": reason})
                            st.success(f"Accepted: {rec['symbol']} {rec['option_type']} {rec['strike']} | Reason: {reason}")
                        if st.button(f"Reject AI {i}"):
                            log_user_action("rejected", {**rec, "reason": reason})
                            st.warning(f"Rejected: {rec['symbol']} {rec['option_type']} {rec['strike']} | Reason: {reason}")
                impact_text = llm_output[json_match.end():].strip()
                if impact_text:
                    st.markdown("**Portfolio Impact Assessment:**")
                    st.info(impact_text)
            except Exception as e:
                st.warning(f"Could not parse recommendations as JSON: {e}")
                st.write(llm_output)
        else:
            st.write(llm_output)

def render_greeks_summary(portfolio_data: Dict):
    st.subheader("Σ Greeks Summary")
    if not portfolio_data or "net" not in portfolio_data:
        st.info("No portfolio data available for Greeks calculation.")
        return
    positions = portfolio_data["net"]
    portfolio_greeks = summarize_portfolio_greeks(positions)
    st.markdown("**Portfolio Greeks:**")
    st.write(portfolio_greeks)
    st.markdown("**Per-Position Greeks:**")
    pos_greeks = per_position_greeks(positions)
    df = pd.DataFrame(pos_greeks)
    display_cols = ["tradingsymbol", "quantity", "delta", "gamma", "theta", "vega"]
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True)

def render_risk_overview(portfolio_data: Dict):
    st.subheader("⚠️ Risk Overview")
    if not portfolio_data:
        st.info("No portfolio data available for risk analysis.")
        return
    st.markdown("**Margin Utilization Alert:**")
    alert = margin_utilization_alert(portfolio_data)
    st.write(alert["message"])
    st.progress(min(alert["utilization"], 1.0))
    st.markdown("**Stress Test (5% Market Drop):**")
    stress = stress_test(portfolio_data, 0.05)
    st.write(f"Total Simulated P&L: ₹{stress['total_simulated_pnl']:.2f}")
    df = pd.DataFrame(stress["simulated_positions"])
    display_cols = ["tradingsymbol", "market_value", "pnl", "simulated_market_value", "simulated_pnl"]
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True)
    st.markdown("**Value at Risk (VaR, 95% confidence):**")
    var = calculate_var(portfolio_data, 0.95)
    st.write(f"Estimated VaR: ₹{var['VaR']:.2f} at 95% confidence")

def render_history():
    st.subheader("📜 Analysis & Recommendation History")
    logs = read_log_history()
    if not logs:
        st.info("No history found yet.")
        return
    # Filtering/search UI
    event_types = sorted(set(log['event_type'] for log in logs))
    selected_event = st.selectbox("Filter by event type", ["All"] + event_types, index=0)
    search_text = st.text_input("Search in data", "")
    filtered_logs = logs
    if selected_event != "All":
        filtered_logs = [log for log in filtered_logs if log['event_type'] == selected_event]
    if search_text:
        filtered_logs = [log for log in filtered_logs if search_text.lower() in str(log['data']).lower()]
    df = pd.DataFrame(filtered_logs)
    if not df.empty:
        st.dataframe(df[["timestamp", "event_type"]], use_container_width=True)
        st.markdown("**Click a row in the table above to see details below.**")
        # Show details for the last filtered log entry
        last = filtered_logs[-1]
        st.markdown(f"**Last Entry Details:**\n- Timestamp: {last['timestamp']}\n- Event: {last['event_type']}\n- Data: {last['data']}")
    else:
        st.info("No matching history found.")
    # Performance chart for performance_indicators
    perf_logs = [log for log in logs if log['event_type'] == 'user_action:performance_indicators']
    if perf_logs:
        perf_df = pd.DataFrame([log['data']['performance_indicators'] for log in perf_logs])
        perf_df['timestamp'] = pd.to_datetime(perf_df['timestamp'])
        st.markdown("**Portfolio Performance Over Time:**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['roi'], mode='lines+markers', name='ROI (%)'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['total_value'], mode='lines+markers', name='Total Value'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['total_pnl'], mode='lines+markers', name='Total P&L'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['delta'], mode='lines+markers', name='Delta'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['gamma'], mode='lines+markers', name='Gamma'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['theta'], mode='lines+markers', name='Theta'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['vega'], mode='lines+markers', name='Vega'))
        fig.update_layout(title='Portfolio Performance & Greeks Over Time', xaxis_title='Time', yaxis_title='Value', legend_title='Metric', height=500)
        st.plotly_chart(fig, use_container_width=True)
    # Feedback summary
    accept_count = sum(1 for log in logs if log['event_type'] == 'user_action:accepted')
    reject_count = sum(1 for log in logs if log['event_type'] == 'user_action:rejected')
    total_feedback = accept_count + reject_count
    if total_feedback > 0:
        st.markdown(f"**Feedback Summary:**\n- Accepted: {accept_count}\n- Rejected: {reject_count}\n- Acceptance Rate: {accept_count / total_feedback * 100:.1f}%")

def log_portfolio_changes(new_portfolio):
    """Log changes in portfolio positions (buy/sell) compared to last portfolio."""
    last = st.session_state.get('last_portfolio')
    if last is None or 'net' not in last or 'net' not in new_portfolio:
        st.session_state['last_portfolio'] = new_portfolio
        return
    last_positions = {p['tradingsymbol']: p for p in last['net']}
    new_positions = {p['tradingsymbol']: p for p in new_portfolio['net']}
    # Detect buys
    for symbol in new_positions:
        if symbol not in last_positions:
            log_user_action('buy', {'symbol': symbol, 'details': new_positions[symbol]})
    # Detect sells
    for symbol in last_positions:
        if symbol not in new_positions:
            log_user_action('sell', {'symbol': symbol, 'details': last_positions[symbol]})
    st.session_state['last_portfolio'] = new_portfolio

def log_portfolio_performance_indicators(portfolio_data):
    """Log key portfolio performance indicators for performance tracking over time, including Greeks and margin."""
    if not portfolio_data or "net" not in portfolio_data:
        return
    positions = portfolio_data["net"]
    total_positions = len(positions)
    total_value = sum(pos.get("market_value", 0) for pos in positions)
    total_pnl = sum(pos.get("pnl", 0) for pos in positions)
    roi = (total_pnl / total_value * 100) if total_value > 0 else 0
    # Portfolio-level Greeks
    greeks = summarize_portfolio_greeks(positions)
    # Margin used/available
    margin_used = portfolio_data.get("margin_used", None)
    margin_total = portfolio_data.get("margin_total", None)
    margin_available = margin_total - margin_used if margin_used is not None and margin_total is not None else None
    indicators = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_positions": total_positions,
        "total_value": total_value,
        "total_pnl": total_pnl,
        "roi": roi,
        "delta": greeks.get("delta"),
        "gamma": greeks.get("gamma"),
        "theta": greeks.get("theta"),
        "vega": greeks.get("vega"),
        "margin_used": margin_used,
        "margin_available": margin_available,
        "margin_total": margin_total,
    }
    log_event = {
        "performance_indicators": indicators
    }
    log_user_action("performance_indicators", log_event)

def render_portfolio_summary():
    import pandas as pd
    import plotly.graph_objs as go
    st.subheader("💼 Portfolio Summary")
    # Add Refresh button
    if st.button("🔄 Refresh Portfolio") or 'portfolio_summary_refresh' not in st.session_state:
        st.session_state['portfolio_summary_refresh'] = True
    if not st.session_state.get('portfolio_summary_refresh', False):
        return
    from analyzer import analyze_portfolio
    import asyncio
    result = asyncio.run(analyze_portfolio())
    portfolio_data = result.get("portfolio", {})
    if not portfolio_data or "net" not in portfolio_data:
        st.info("No portfolio data available.")
        return
    positions = portfolio_data["net"]
    # Table of open positions
    df = pd.DataFrame(positions)
    if not df.empty:
        # Calculate days held
        if "entry_date" in df.columns:
            df["days_held"] = (pd.Timestamp.now() - pd.to_datetime(df["entry_date"])).dt.days
        else:
            df["days_held"] = None
        # Calculate % return
        if "pnl" in df.columns and "market_value" in df.columns:
            df["pct_return"] = df["pnl"] / df["market_value"] * 100
        else:
            df["pct_return"] = None
        display_cols = [c for c in ["tradingsymbol", "type", "quantity", "entry_date", "entry_price", "market_value", "pnl", "pct_return", "days_held"] if c in df.columns]
        st.markdown("**Open Positions:**")
        st.dataframe(df[display_cols], use_container_width=True)
    else:
        st.info("No open positions.")
    # Portfolio-level performance chart (over time)
    from logging_utils import read_log_history
    logs = read_log_history()
    perf_logs = [log for log in logs if log['event_type'] == 'user_action:performance_indicators']
    if perf_logs:
        perf_df = pd.DataFrame([log['data']['performance_indicators'] for log in perf_logs])
        perf_df['timestamp'] = pd.to_datetime(perf_df['timestamp'])
        st.markdown("**Portfolio Performance Over Time:**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['roi'], mode='lines+markers', name='ROI (%)'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['total_value'], mode='lines+markers', name='Total Value'))
        fig.add_trace(go.Scatter(x=perf_df['timestamp'], y=perf_df['total_pnl'], mode='lines+markers', name='Total P&L'))
        fig.update_layout(title='Portfolio Performance Over Time', xaxis_title='Time', yaxis_title='Value', legend_title='Metric', height=400)
        st.plotly_chart(fig, use_container_width=True)
    # Theta decay per position and portfolio
    if "theta" in df.columns:
        st.markdown("**Theta Decay (per position):**")
        st.dataframe(df[["tradingsymbol", "theta"]], use_container_width=True)
        total_theta = df["theta"].sum()
        st.markdown(f"**Total Portfolio Theta Decay:** {total_theta:.2f}")
    # User prompt for additional metrics
    st.markdown("---")
    st.markdown("**Would you like to see any additional metrics in your portfolio summary?**")
    extra_metrics = st.text_input("Enter metrics (comma-separated, e.g. margin used, sector exposure, VaR, etc.)", "")
    if extra_metrics:
        st.info(f"You requested: {extra_metrics}. This feature will be added soon!")
    # Recommendations for further analytics
    st.markdown("---")
    st.markdown("**Recommended additional analytics:**\n- Realized vs. unrealized P&L\n- Sector/industry breakdown\n- Largest winners/losers\n- Risk metrics (VaR, margin utilization)\n- Upcoming expiries\n- Custom alerts (e.g. high theta decay, expiring soon)")
    # --- Advanced Analytics ---
    st.markdown("---")
    st.markdown("## 📊 Advanced Analytics")
    # 1. Realized vs. Unrealized P&L
    logs = read_log_history()
    closed_positions = []
    for log in logs:
        if log['event_type'] == 'user_action:sell':
            data = log['data']
            if 'pnl' in data:
                closed_positions.append(data)
    realized_pnl = sum(p.get('pnl', 0) for p in closed_positions)
    unrealized_pnl = df['pnl'].sum() if 'pnl' in df.columns else 0
    st.markdown(f"**Realized P&L:** ₹{realized_pnl:.2f}")
    st.markdown(f"**Unrealized P&L:** ₹{unrealized_pnl:.2f}")
    # 2. Sector/Industry Breakdown
    if 'sector' in df.columns:
        st.markdown("**Sector/Industry Breakdown:**")
        sector_counts = df.groupby('sector')['market_value'].sum()
        import plotly.express as px
        fig_sector = px.pie(sector_counts, values=sector_counts.values, names=sector_counts.index, title='Portfolio by Sector')
        st.plotly_chart(fig_sector, use_container_width=True)
    else:
        st.info("Add a 'sector' column to your position data for sector breakdown.")
    # 3. Largest Winners/Losers
    if 'pnl' in df.columns:
        st.markdown("**Top 3 Winners:**")
        winners = df.sort_values('pnl', ascending=False).head(3)
        st.dataframe(winners[[c for c in ['tradingsymbol', 'pnl', 'pct_return'] if c in winners.columns]], use_container_width=True)
        st.markdown("**Top 3 Losers:**")
        losers = df.sort_values('pnl').head(3)
        st.dataframe(losers[[c for c in ['tradingsymbol', 'pnl', 'pct_return'] if c in losers.columns]], use_container_width=True)
    # 4. Risk Metrics (VaR, margin utilization)
    st.markdown("**Risk Metrics:**")
    try:
        from risk import calculate_var
        var = calculate_var(portfolio_data, 0.95)
        st.markdown(f"Value at Risk (95%): ₹{var['VaR']:.2f}")
    except Exception:
        st.info("VaR calculation not available.")
    margin_used = portfolio_data.get('margin_used', None)
    margin_total = portfolio_data.get('margin_total', None)
    if margin_used is not None and margin_total is not None:
        st.markdown(f"Margin Utilization: {margin_used / margin_total * 100:.1f}% ({margin_used} / {margin_total})")
    # 5. Upcoming Expiries
    if 'expiry' in df.columns:
        import pandas as pd
        st.markdown("**Upcoming Expiries (next 7 days):**")
        df['expiry_dt'] = pd.to_datetime(df['expiry'], errors='coerce')
        soon = df[df['expiry_dt'] <= pd.Timestamp.now() + pd.Timedelta(days=7)]
        if not soon.empty:
            st.dataframe(soon[[c for c in ['tradingsymbol', 'expiry', 'quantity', 'pnl'] if c in soon.columns]], use_container_width=True)
        else:
            st.info("No positions expiring in the next 7 days.")
    # 6. Custom Alerts
    alerts = []
    if 'theta' in df.columns and df['theta'].abs().max() > 1000:
        alerts.append("High theta decay detected in one or more positions!")
    if 'expiry_dt' in df.columns and not df[df['expiry_dt'] <= pd.Timestamp.now() + pd.Timedelta(days=3)].empty:
        alerts.append("Some positions are expiring within 3 days!")
    if 'pnl' in df.columns and df['pnl'].min() < -10000:
        alerts.append("Large loss detected in at least one position!")
    if alerts:
        st.markdown("**⚠️ Alerts:**")
        for alert in alerts:
            st.warning(alert)

def main():
    st.set_page_config(
        page_title="kiteMCP - AI Trading Assistant",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown('<h1 class="main-header">📈 kiteMCP - AI Trading Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    st.sidebar.subheader("💼 Portfolio Summary")
    if st.sidebar.button("Show Portfolio Summary"):
        st.session_state['active_feature'] = 'portfolio_summary'
    st.sidebar.subheader("📰 News Dashboard")
    if st.sidebar.button("Show News & Macro Dashboard"):
        st.session_state['active_feature'] = 'news'
    st.sidebar.subheader("🔎 Opportunity Scanner")
    if st.sidebar.button("Show Opportunity Scanner"):
        st.session_state['active_feature'] = 'scanner'
    st.sidebar.subheader("Σ Greeks Summary")
    if st.sidebar.button("Show Greeks Summary"):
        st.session_state['active_feature'] = 'greeks'
    st.sidebar.subheader("⚠️ Risk Overview")
    if st.sidebar.button("Show Risk Overview"):
        st.session_state['active_feature'] = 'risk'
    st.sidebar.subheader("📜 History")
    if st.sidebar.button("Show History"):
        st.session_state['active_feature'] = 'history'
    # Add profile/settings sidebar to the app
    profile_settings_sidebar()
    # Feature display logic
    if st.session_state['active_feature'] == 'portfolio_summary':
        render_portfolio_summary()
    elif st.session_state['active_feature'] == 'news':
        render_news_dashboard()
    elif st.session_state['active_feature'] == 'scanner':
        render_opportunity_scanner()
    elif st.session_state['active_feature'] == 'greeks':
        try:
            from analyzer import analyze_portfolio
            import asyncio
            result = asyncio.run(analyze_portfolio())
            portfolio_data = result.get("portfolio", {})
            log_portfolio_summary(portfolio_data)
            log_portfolio_changes(portfolio_data)
            log_portfolio_performance_indicators(portfolio_data)
        except Exception:
            portfolio_data = {}
        render_greeks_summary(portfolio_data)
    elif st.session_state['active_feature'] == 'risk':
        try:
            from analyzer import analyze_portfolio
            import asyncio
            result = asyncio.run(analyze_portfolio())
            portfolio_data = result.get("portfolio", {})
            log_portfolio_summary(portfolio_data)
            log_portfolio_changes(portfolio_data)
            log_portfolio_performance_indicators(portfolio_data)
        except Exception:
            portfolio_data = {}
        render_risk_overview(portfolio_data)
    elif st.session_state['active_feature'] == 'history':
        render_history()
    else:
        st.info("Select a feature from the sidebar to get started.")

if __name__ == "__main__":
    main() 