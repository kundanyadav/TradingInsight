name: "Kite Trading Recommendation App - Complete Implementation"
description: |

## Purpose
Build a comprehensive trading recommendation application for Indian stock markets that analyzes portfolio positions, market conditions, and external factors to identify profitable opportunities while managing risk/reward, ROI, margin, and portfolio diversification.

## Core Principles
1. **Risk-First Approach**: Prioritize capital preservation and risk management
2. **Data-Driven Decisions**: Base all recommendations on comprehensive market analysis
3. **Portfolio Optimization**: Focus on overall portfolio health rather than individual trades
4. **Real-Time Integration**: Seamless connection with Kite trading platform
5. **Professional Analysis**: Expert-level market research and sentiment analysis

---

## Goal
Create a sophisticated trading recommendation system that combines portfolio analysis, market sentiment, and external factors to provide actionable trading opportunities for Indian stock markets, with focus on options trading and risk management.

## Why
- **Business Value**: Automated analysis reduces emotional trading decisions and improves profitability
- **User Impact**: Professional-grade market analysis accessible to individual traders
- **Integration**: Seamless integration with existing Kite trading infrastructure
- **Risk Management**: Systematic approach to portfolio diversification and risk control

## What
A multi-component application with:
1. **MCP Server**: Existing Kite integration providing portfolio data, news, and market analysis
2. **Market Analyst Agent**: LLM-based professional equity research analyst with years of experience
3. **Orchestration & UI Engine**: Streamlit-based interface for portfolio management and analysis
4. **Recommendation Agent**: Expert investment fund manager and financial advisor for options trading strategies

### Key Features:
- **Portfolio Analysis**: Sector-wise grouping, position metrics, risk indicators, ROI calculations
- **Market Sentiment Analysis**: Short-term (<1 month) and medium-term (1-3 months) analysis
- **Options Trading Focus**: ROM, SSR, premium analysis, risk-reward optimization
- **Risk Management**: Portfolio diversification, margin management, cash management
- **Professional Analysis**: Financial results analysis, intrinsic value assessment, social media sentiment
- **Customizable Filters**: SSR, minimum premium, minimum ROM, risk indicator thresholds
- **Stock Scope Management**: Restricted analysis to approved stock list only

### Key Trading Indicators:
- **ROM (Return on Margin)**: Premium collected divided by margin used (percentage)
- **SSR (Strike Safety Ratio)**: (Spot price minus strike price) as percentage of spot price (bigger number is better)
- **RI (Risk Indicator)**: 1-10 scale showing risk based on market analyst analysis (1=minimum risk, 10=maximum risk)
- **Reward-Risk Ratio**: Premium collected divided by risk indicator
- **ROI**: Premium collected divided by margin used

### Success Criteria
- [ ] MCP client successfully connects to existing MCP server and provides real-time portfolio data
- [ ] Market analyst agent provides professional-grade sentiment analysis with confidence scores (1-10 scale)
- [ ] UI displays comprehensive portfolio metrics: sector grouping, position analysis, ROI, ROM, SSR, risk indicators
- [ ] Recommendation agent generates actionable trading opportunities (new trade, swap trade, hedge trade)
- [ ] All components integrate seamlessly with proper error handling
- [ ] Application follows Indian market trading hours and regulations
- [ ] Stock scope list is enforced - no analysis of unauthorized stocks
- [ ] Custom filters work correctly (SSR, minimum premium, minimum ROM, risk indicator)
- [ ] Professional analysis includes financial results, intrinsic value, social media sentiment

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://kite.trade/docs/connect/v3/
  why: KiteConnect API documentation for portfolio and market data access
  
- url: https://docs.pydantic.ai/
  why: PydanticAI for structured data validation and LLM integration
  
- url: https://langchain-ai.github.io/langgraph/
  why: LangGraph for building complex LLM workflows and agent orchestration
  
- url: https://docs.streamlit.io/
  why: Streamlit for building the web-based UI interface
  
- url: https://www.screener.in/
  why: Financial results and fundamental data source
  
- url: https://www.smart-investing.in/
  why: Stock intrinsic value analysis
  
- url: https://www.tickertape.in/
  why: Analyst ratings and market mood data
  
- url: https://www.tickertape.in/market-mood-index
  why: Market mood index for overall sentiment analysis
  
- url: https://web.stockedge.com/fii-activity
  why: FII activity data for institutional sentiment
  
- file: kiteMCPServer/mcp_server.py
  why: Existing MCP server pattern to extend for enhanced functionality
  
- file: kiteMCPServer/tools.py
  why: Current tools implementation pattern to follow for new tools
  
- file: kiteMCPServer/prompts.py
  why: Existing prompt structure for market analysis templates

# CRITICAL EXAMPLES FROM FEATURE REQUIREMENT
- example: ICICIBANK sentiment analysis template
  why: Professional analysis format with confidence scores and timeframes
  
- example: Trade recommendation examples (new trade, swap trade)
  why: Specific format for actionable trade recommendations with reasoning
```

### Current Codebase tree
```bash
Kite2.0/
├── kiteMCPServer/
│   ├── __init__.py
│   ├── env.example
│   ├── mcp_server.py
│   ├── prompts.py
│   ├── README.md
│   ├── requirements.txt
│   ├── resources.py
│   └── tools.py
└── TradingInsight/
    ├── __init__.py
    ├── FeatureRequirement/
    │   └── FeatureRequirement.md
    ├── requirements.txt
    └── .cursor/
        ├── PRPs/
        │   ├── templates/
        │   └── examples/
        └── rules/
```

### Desired Codebase tree with files to be added
```bash
Kite2.0/
├── kiteMCPServer/                 # EXISTING: MCP server (unchanged)
│   ├── __init__.py
│   ├── env.example
│   ├── mcp_server.py
│   ├── prompts.py
│   ├── README.md
│   ├── requirements.txt
│   ├── resources.py
│   └── tools.py
└── TradingInsight/
    ├── __init__.py
    ├── FeatureRequirement/
    │   └── FeatureRequirement.md
    ├── requirements.txt
    ├── main.py                    # NEW: Streamlit app entry point
    ├── ui/
    │   ├── __init__.py
    │   ├── portfolio_view.py      # NEW: Portfolio display components
    │   ├── analysis_view.py       # NEW: Market analysis components
    │   └── recommendation_view.py # NEW: Recommendation display
    ├── services/
    │   ├── __init__.py
    │   ├── mcp_client.py          # NEW: MCP server client
    │   ├── market_analyst.py      # NEW: Market analyst agent
    │   ├── recommendation_agent.py # NEW: Recommendation agent
    │   ├── portfolio_service.py   # NEW: Portfolio data processing
    │   ├── analysis_service.py    # NEW: Market analysis orchestration
    │   └── recommendation_service.py # NEW: Recommendation processing
    ├── models/
    │   ├── __init__.py
    │   ├── data_models.py         # NEW: All Pydantic models
    │   ├── portfolio.py           # NEW: Portfolio data models
    │   ├── analysis.py            # NEW: Analysis result models
    │   └── recommendations.py     # NEW: Recommendation models
    ├── config/
    │   ├── __init__.py
    │   └── settings.py            # NEW: Application configuration
    └── tests/
        ├── __init__.py
        ├── test_mcp_client.py
        ├── test_market_analyst.py
        ├── test_recommendation_agent.py
        ├── test_portfolio_service.py
        ├── test_analysis_service.py
        └── test_recommendation_service.py
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: MCP server is separate project - DO NOT MODIFY
# Example: Use MCP client to connect to existing server

# CRITICAL: KiteConnect requires authentication before any API calls
# Example: kite.set_access_token(data["access_token"])

# CRITICAL: PydanticAI requires structured data models for LLM integration
# Example: Use @pydantic_ai.model for data validation

# CRITICAL: LangGraph requires proper state management for agent workflows
# Example: Use StateGraph for managing agent state transitions

# CRITICAL: Streamlit requires session state for data persistence
# Example: Use st.session_state for storing portfolio data

# CRITICAL: Indian market trading hours: 9:15 AM - 3:30 PM IST
# Example: Check market hours before making recommendations

# CRITICAL: Options expiry is last Thursday of every month
# Example: Calculate expiry dates dynamically

# CRITICAL: Trading Indicators Definitions
# ROM = Premium collected / Margin used (percentage)
# SSR = (Spot price - Strike price) / Spot price (percentage, bigger is better)
# RI = Risk Indicator (1-10 scale, 1=min risk, 10=max risk)
# Reward-Risk Ratio = Premium collected / Risk indicator
```

## Implementation Blueprint

### Data models and structure

Create comprehensive Pydantic models for type safety and data validation:

```python
# models/portfolio.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PositionType(str, Enum):
    LONG = "long"
    SHORT = "short"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Position(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    margin_used: float
    premium_collected: float
    rom: float  # Return on Margin: Premium collected / Margin used (percentage)
    ssr: float  # Strike Safety Ratio: (Spot price - Strike price) / Spot price (percentage)
    risk_indicator: int = Field(ge=1, le=10)  # Risk Indicator: 1=min risk, 10=max risk
    reward_risk_ratio: float  # Premium collected / Risk indicator
    position_type: PositionType
    expiry: datetime
    strike_price: float
    option_type: str  # CE/PE

class Portfolio(BaseModel):
    total_margin: float
    available_cash: float
    total_exposure: float
    positions: List[Position]
    sector_exposure: Dict[str, float]
    risk_score: float = Field(ge=0, le=10)

# models/analysis.py
class SentimentAnalysis(BaseModel):
    symbol: str
    short_term_sentiment: str
    short_term_target: tuple[float, float]
    short_term_confidence: float = Field(ge=0, le=10)
    short_term_timeframe: str = "Next 2-4 weeks"
    medium_term_sentiment: str
    medium_term_target: tuple[float, float]
    medium_term_confidence: float = Field(ge=0, le=10)
    medium_term_timeframe: str = "1-3 months"
    key_drivers: List[str]
    risks: List[str]
    summary: str
    financial_analysis: Dict[str, Any]  # Quarterly results analysis
    intrinsic_value: Dict[str, Any]     # Overvalued/undervalued analysis
    social_sentiment: Dict[str, Any]    # Social media and analyst ratings
    
    # Example format from FeatureRequirement.md:
    # Short-Term View (<1 Month)
    # • Sentiment: Cautiously Positive
    # • Target Price Range: ₹1,520 – ₹1,550
    # • Time Frame: Next 2–4 weeks
    # • Confidence Score: 8.5 / 10
    # Key Drivers: [list of drivers]
    # Risks: [list of risks]
    # Summary: [clear summary]

# models/recommendations.py
class RecommendationType(str, Enum):
    NEW_TRADE = "new trade"
    SWAP_TRADE = "swap trade"
    HEDGE_TRADE = "hedge trade"

class TradeRecommendation(BaseModel):
    recommendation_type: RecommendationType
    symbol: str
    option_type: str  # CE/PE
    strike_price: float
    expiry: str
    quantity: int
    price_range: tuple[float, float]
    confidence: float = Field(ge=0, le=10)
    trade_driver: str
    risk_assessment: str
    expected_rom: float
    expected_ssr: float
    reasoning: str  # Full reasoning behind recommendation
    portfolio_impact: str  # How this affects portfolio diversification
    comparison_with_existing: Optional[str] = None  # For swap trades
    
    # Recommendation Example format from FeatureRequirement.md:
    # Recommendation type: new trade
    # Trade details: take a new position by Selling 1 lot of ICICIBANK AUG 1460 PE 
    # in option price range of 16.05 - 17.10
    # Confidence: 8.5/10
    # Trade driver: [detailed reasoning with financial numbers, sentiment, ROM, SSR]
    # 
    # For swap trades:
    # Recommendation type: swap trade
    # Trade details: take new position AND square off existing position
    # [detailed comparison of ROM, SSR, risk factors]
```

### list of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1: MCP Client Integration
CREATE TradingInsight/services/mcp_client.py:
  - IMPLEMENT client to connect to existing MCP server
  - ADD error handling for connection failures
  - ADD data caching mechanism for portfolio data
  - IMPLEMENT retry logic for API calls

CREATE TradingInsight/models/data_models.py:
  - DEFINE Pydantic models for portfolio, analysis, and recommendations
  - INCLUDE validation rules for Indian market data
  - ADD serialization methods for MCP communication

Task 2: Market Analyst Agent Implementation
CREATE TradingInsight/services/market_analyst.py:
  - IMPLEMENT professional equity research analyst role with years of experience
  - ADD sentiment analysis for short-term (<1 month) and medium-term (1-3 months)
  - INCLUDE financial results analysis from screener.in with quarterly trends
  - ADD web search integration for news and social media sentiment
  - IMPLEMENT intrinsic value analysis from smart-investing.in and simplywall.st
  - ADD analyst ratings and market mood from tickertape.in
  - INCLUDE FII activity analysis from stockedge.com
  - ADD self-assessment and iterative improvement
  - USE MCP client to get portfolio and market data
  - IMPLEMENT confidence scoring (1-10 scale) for all analysis
  - FOLLOW ICICIBANK analysis template format with clear structure

Task 3: Recommendation Agent Implementation
CREATE TradingInsight/services/recommendation_agent.py:
  - IMPLEMENT experienced investment fund manager and financial advisor role
  - ADD options chain analysis for trade identification (new trade, swap trade, hedge trade)
  - INCLUDE portfolio optimization algorithms with diversification focus
  - ADD risk-reward ratio calculations (ROM, SSR, premium analysis)
  - IMPLEMENT trade comparison and swap logic with existing positions
  - ADD confidence scoring (1-10 scale) and detailed reasoning
  - USE MCP client to get portfolio and options data
  - INCLUDE self-review and iterative improvement until satisfied
  - ADD portfolio balancing and risk reduction recommendations
  - FOLLOW trade recommendation template format with specific examples

Task 4: Streamlit UI Foundation
CREATE TradingInsight/main.py:
  - SETUP Streamlit application structure
  - ADD session state management
  - IMPLEMENT MCP server connection
  - ADD basic navigation and layout

Task 5: Portfolio Service Implementation
CREATE TradingInsight/services/portfolio_service.py:
  - IMPLEMENT portfolio data processing from MCP server
  - ADD sector-wise grouping with total margin, position count, exposure %
  - INCLUDE position-wise analysis: premium collected, ROM, SSR, risk indicator (1-10)
  - ADD margin and cash management calculations
  - IMPLEMENT ROI calculations (premium collected / margin used)
  - ADD reward-risk ratio (premium collected / risk indicator)
  - INCLUDE risk group classification based on risk indicators
  - CALCULATE ROM = Premium collected / Margin used (percentage)
  - CALCULATE SSR = (Spot price - Strike price) / Spot price (percentage)
  - CALCULATE Risk Indicator = 1-10 scale from market analyst analysis

Task 6: Analysis Service Implementation
CREATE TradingInsight/services/analysis_service.py:
  - IMPLEMENT market analyst agent integration
  - ADD sentiment analysis display for individual stocks, sectors, and market
  - INCLUDE sector and market analysis on demand
  - ADD custom prompt handling for user-defined analysis
  - IMPLEMENT analysis caching for performance
  - ADD confidence score visualization (1-10 scale)
  - INCLUDE financial results, intrinsic value, and social sentiment display

Task 7: Recommendation Service Implementation
CREATE TradingInsight/services/recommendation_service.py:
  - IMPLEMENT recommendation agent integration
  - ADD trade opportunity identification (new, swap, hedge trades)
  - INCLUDE filter constraint handling (SSR, minimum premium, minimum ROM, risk indicator)
  - ADD recommendation validation and confidence scoring
  - IMPLEMENT action point parsing and reasoning display
  - ADD portfolio data collation for recommendation prompts
  - INCLUDE user prompt review and confirmation workflow
  - ADD recommendation comparison with existing positions

Task 8: UI Components Implementation
CREATE TradingInsight/ui/portfolio_view.py:
  - IMPLEMENT portfolio dashboard with sector-wise grouping
  - ADD position-wise view: premium collected, ROM, SSR, risk indicator (1-10)
  - INCLUDE reward-risk ratio and risk group classifications
  - ADD total ROI calculations and exposure percentages
  - INCLUDE on-demand analysis for each position's underlying stock

CREATE TradingInsight/ui/analysis_view.py:
  - IMPLEMENT market analysis display for stocks, sectors, and market
  - ADD sentiment analysis visualization with confidence scores
  - INCLUDE custom prompt input interface for user-defined analysis
  - ADD financial results, intrinsic value, and social sentiment display
  - INCLUDE short-term and medium-term analysis views

CREATE TradingInsight/ui/recommendation_view.py:
  - IMPLEMENT recommendation display with trade details
  - ADD confidence score visualization and reasoning display
  - INCLUDE filter constraint interface (SSR, premium, ROM, risk indicator)
  - ADD stock scope list management interface
  - INCLUDE user prompt review and confirmation workflow
  - ADD action point formatting and portfolio impact analysis

Task 9: Configuration and Settings
CREATE TradingInsight/config/settings.py:
  - IMPLEMENT application configuration
  - ADD stock scope list management (restrict analysis to approved stocks only)
  - INCLUDE filter constraint settings (SSR, minimum premium, minimum ROM, risk indicator)
  - ADD trading hours validation (9:15 AM - 3:30 PM IST)
  - INCLUDE Indian market regulations and compliance
  - ADD portfolio diversification rules and limits

Task 10: Testing Implementation
CREATE TradingInsight/tests/:
  - IMPLEMENT unit tests for all services
  - ADD integration tests for MCP communication
  - INCLUDE UI component tests
  - ADD mock data for testing scenarios
```

### Per task pseudocode as needed added to each task

```python
# Task 1: MCP Client Integration
# Pseudocode for MCP client connection
class MCPClient:
    async def connect_to_mcp_server(self):
        # PATTERN: Connect to existing MCP server without modification
        try:
            # CRITICAL: Use existing MCP server endpoints
            self.connection = await connect_to_mcp_server()
            return True
        except ConnectionError:
            st.error("Failed to connect to MCP server")
            return False
    
    async def get_portfolio_data(self):
        # PATTERN: Use existing MCP tools
        return await self.connection.call_tool("get_portfolio")
    
    async def get_market_data(self, symbol: str):
        # PATTERN: Use existing MCP tools
        return await self.connection.call_tool("get_market_indicators", symbol)

# Task 2: Market Analyst Agent
# Pseudocode for sentiment analysis
@pydantic_ai.model
class MarketAnalyst:
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
    
    async def analyze_sentiment(self, symbol: str, timeframe: str = "both") -> SentimentAnalysis:
        # PATTERN: Use structured prompts for consistent analysis
        prompt = self.build_analysis_prompt(symbol, timeframe)
        
        # CRITICAL: Get market data from MCP server
        market_data = await self.mcp_client.get_market_data(symbol)
        
        # CRITICAL: Include financial data from screener.in with quarterly trends
        financial_data = await self.get_financial_data(symbol)
        
        # CRITICAL: Include news and social media sentiment
        news_data = await self.search_web_for_news(symbol)
        
        # CRITICAL: Get intrinsic value analysis
        intrinsic_value = await self.get_intrinsic_value(symbol)
        
        # CRITICAL: Get analyst ratings and market mood
        analyst_ratings = await self.get_analyst_ratings(symbol)
        
        # CRITICAL: Get FII activity data
        fii_data = await self.get_fii_activity(symbol)
        
        # CRITICAL: Self-assessment for confidence scoring (1-10 scale)
        analysis = await self.llm.analyze(prompt, market_data, financial_data, 
                                        news_data, intrinsic_value, analyst_ratings, fii_data)
        confidence = await self.self_assess(analysis)
        
        # CRITICAL: Follow ICICIBANK template format
        return SentimentAnalysis(
            symbol=symbol,
            short_term_sentiment=analysis.short_term,  # e.g., "Cautiously Positive"
            short_term_confidence=confidence.short_term,  # e.g., 8.5/10
            short_term_target=analysis.short_term_target,  # e.g., (1520, 1550)
            short_term_timeframe="Next 2-4 weeks",
            medium_term_sentiment=analysis.medium_term,  # e.g., "Moderately Positive"
            medium_term_confidence=confidence.medium_term,  # e.g., 7.5/10
            medium_term_target=analysis.medium_term_target,  # e.g., (1570, 1620)
            medium_term_timeframe="1-3 months",
            key_drivers=analysis.key_drivers,  # e.g., ["Strong Q1 earnings", "Technical breakout"]
            risks=analysis.risks,  # e.g., ["Profit-taking", "Limited upside"]
            summary=analysis.summary,  # Clear actionable summary
            financial_analysis=financial_data,
            intrinsic_value=intrinsic_value,
            social_sentiment=analyst_ratings
        )

# Task 3: Recommendation Agent
# Pseudocode for trade recommendation
@pydantic_ai.model
class RecommendationAgent:
    def __init__(self, mcp_client: MCPClient, market_analyst: MarketAnalyst):
        self.mcp_client = mcp_client
        self.market_analyst = market_analyst
    
    async def find_opportunities(self, portfolio: Portfolio, filters: Dict) -> List[TradeRecommendation]:
        # PATTERN: Use portfolio constraints for filtering
        available_margin = portfolio.available_cash
        
        # CRITICAL: Check stock scope list
        scope_stocks = self.get_scope_stocks()
        
        # CRITICAL: Apply user-defined filters
        min_ssr = filters.get('min_ssr', 0.02)
        min_premium = filters.get('min_premium', 0.05)
        min_rom = filters.get('min_rom', 0.05)
        max_risk = filters.get('max_risk', 7)
        
        # CRITICAL: Analyze options chain for each stock
        opportunities = []
        for stock in scope_stocks:
            # CRITICAL: Get options data from MCP server
            option_chain = await self.mcp_client.get_option_chain(stock)
            analysis = await self.market_analyst.analyze_sentiment(stock)
            
            # CRITICAL: Calculate ROM, SSR, risk indicators
            for option in option_chain:
                rom = self.calculate_rom(option, portfolio)
                ssr = self.calculate_ssr(option)
                risk = self.calculate_risk_indicator(option, analysis)
                
                # CRITICAL: Apply filter criteria
                if (rom >= min_rom and ssr >= min_ssr and 
                    option['premium'] >= min_premium and risk <= max_risk):
                    
                    recommendation = self.create_recommendation(option, analysis, portfolio)
                    opportunities.append(recommendation)
        
        # CRITICAL: Self-review and improve until satisfied
        final_recommendations = await self.self_review_and_improve(opportunities)
        return self.rank_recommendations(final_recommendations)
    
    def create_recommendation(self, option, analysis, portfolio):
        # CRITICAL: Determine recommendation type
        if self.should_swap_existing(option, portfolio):
            rec_type = RecommendationType.SWAP_TRADE
        elif self.should_hedge(option, portfolio):
            rec_type = RecommendationType.HEDGE_TRADE
        else:
            rec_type = RecommendationType.NEW_TRADE
        
        # CRITICAL: Calculate key metrics
        rom = self.calculate_rom(option, portfolio)  # Premium collected / Margin used
        ssr = self.calculate_ssr(option)  # (Spot price - Strike price) / Spot price
        risk = self.calculate_risk_indicator(option, analysis)  # 1-10 scale
        
        return TradeRecommendation(
            recommendation_type=rec_type,
            symbol=option['symbol'],
            option_type=option['type'],
            strike_price=option['strike'],
            expiry=option['expiry'],
            quantity=option['lot_size'],
            price_range=option['price_range'],
            confidence=analysis.short_term_confidence,
            trade_driver=self.build_trade_driver(option, analysis, rom, ssr),
            risk_assessment=self.assess_risk(option, analysis),
            expected_rom=rom,
            expected_ssr=ssr,
            reasoning=self.build_reasoning(option, analysis, portfolio),
            portfolio_impact=self.assess_portfolio_impact(option, portfolio)
        )
    
    def build_trade_driver(self, option, analysis, rom, ssr):
        # CRITICAL: Follow template format from FeatureRequirement.md
        return f"""
        - {option['symbol']} posted strong financial performance and positive sentiment
        - Currently the portfolio has relatively less exposure to this sector
        - The trade is offering good ROM at {rom:.1%} and SSR of {ssr:.1%}
        - Overall positive sentiments for the sector
        """

# Task 4: Streamlit UI Foundation
# Pseudocode for main application
def main():
    # PATTERN: Initialize session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'min_ssr': 0.02,
            'min_premium': 0.05,
            'min_rom': 0.05,
            'max_risk': 7
        }
    if 'stock_scope' not in st.session_state:
        st.session_state.stock_scope = ['NIFTY50', 'BANKNIFTY', 'ICICIBANK', 'HDFCBANK']
    
    # CRITICAL: Connect to MCP server
    mcp_client = connect_to_mcp_server()
    
    # PATTERN: Setup navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Portfolio", "Analysis", "Recommendations", "Settings"]
    )
    
    # CRITICAL: Check market hours (9:15 AM - 3:30 PM IST)
    if not is_market_open():
        st.warning("Market is currently closed")
    
    # Route to appropriate page
    if page == "Portfolio":
        portfolio_view.render(mcp_client)
    elif page == "Analysis":
        analysis_view.render(mcp_client)
    elif page == "Recommendations":
        recommendation_view.render(mcp_client, st.session_state.filters)
    elif page == "Settings":
        settings_view.render(st.session_state.filters, st.session_state.stock_scope)
```

### Integration Points
```yaml
DATABASE:
  - cache: "Redis for portfolio data caching"
  - session: "Streamlit session state for user preferences"
  
CONFIG:
  - add to: TradingInsight/config/settings.py
  - pattern: "STOCK_SCOPE_LIST = ['NIFTY50', 'BANKNIFTY', ...]"
  - pattern: "MIN_ROM_THRESHOLD = 0.05"
  - pattern: "MIN_SSR_THRESHOLD = 0.02"
  
ROUTES:
  - add to: TradingInsight/main.py
  - pattern: "st.page_config(layout='wide')"
  - pattern: "st.sidebar for navigation"
  
MCP_INTEGRATION:
  - client: TradingInsight/services/mcp_client.py
  - pattern: "Connect to existing MCP server without modification"
  - pattern: "Use existing MCP tools: get_portfolio, get_market_indicators, get_option_chain"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check TradingInsight/ --fix
ruff check kiteMCPServer/ --fix
mypy TradingInsight/
mypy kiteMCPServer/

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE test files with these test cases:

def test_portfolio_service():
    """Portfolio data processing works correctly"""
    portfolio_data = mock_portfolio_data()
    result = portfolio_service.process_portfolio(portfolio_data)
    assert result.total_margin > 0
    assert len(result.positions) > 0

def test_mcp_client():
    """MCP client connects to server and retrieves data"""
    client = MCPClient()
    assert client.connect_to_mcp_server()
    portfolio_data = client.get_portfolio_data()
    assert portfolio_data is not None

def test_market_analyst():
    """Market analyst provides valid sentiment analysis"""
    mcp_client = MCPClient()
    market_analyst = MarketAnalyst(mcp_client)
    analysis = market_analyst.analyze_sentiment("ICICIBANK")
    assert analysis.short_term_confidence >= 0
    assert analysis.short_term_confidence <= 10
    assert analysis.short_term_sentiment in ["bullish", "bearish", "neutral", "Cautiously Positive"]
    assert analysis.medium_term_confidence >= 0
    assert analysis.medium_term_confidence <= 10
    assert analysis.financial_analysis is not None
    assert analysis.intrinsic_value is not None
    assert analysis.social_sentiment is not None
    assert len(analysis.key_drivers) > 0
    assert len(analysis.risks) > 0
    assert analysis.summary is not None

def test_recommendation_agent():
    """Recommendation agent generates valid trade recommendations"""
    mcp_client = MCPClient()
    market_analyst = MarketAnalyst(mcp_client)
    recommendation_agent = RecommendationAgent(mcp_client, market_analyst)
    portfolio = mock_portfolio()
    filters = {'min_ssr': 0.02, 'min_premium': 0.05, 'min_rom': 0.05, 'max_risk': 7}
    recommendations = recommendation_agent.find_opportunities(portfolio, filters)
    for rec in recommendations:
        assert rec.confidence >= 0
        assert rec.confidence <= 10
        assert rec.symbol in STOCK_SCOPE_LIST
        assert rec.recommendation_type in ["new trade", "swap trade", "hedge trade"]
        assert rec.reasoning is not None
        assert rec.portfolio_impact is not None
        assert rec.expected_rom > 0  # ROM should be positive
        assert rec.expected_ssr > 0  # SSR should be positive
        assert "ROM" in rec.trade_driver  # Should mention ROM in trade driver
        assert "SSR" in rec.trade_driver  # Should mention SSR in trade driver

def test_streamlit_ui():
    """UI components render without errors"""
    # Test portfolio view rendering
    # Test analysis view rendering
    # Test recommendation view rendering
```

```bash
# Run and iterate until passing:
uv run pytest TradingInsight/tests/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the MCP server (separate project)
cd kiteMCPServer
uv run python mcp_server.py

# Start the Streamlit app (in new terminal)
cd ../TradingInsight
uv run streamlit run main.py

# Test the complete workflow
# 1. MCP client connects to server successfully
# 2. Portfolio data loads correctly from MCP server
# 3. Market analysis generates sentiment using MCP data
# 4. Recommendations are generated with MCP integration
# 5. UI displays all components properly
```

## Final validation Checklist
- [ ] All tests pass: `uv run pytest TradingInsight/tests/ -v`
- [ ] No linting errors: `uv run ruff check TradingInsight/`
- [ ] No type errors: `uv run mypy TradingInsight/`
- [ ] MCP client connects to existing MCP server successfully
- [ ] Portfolio data retrieved from MCP server correctly
- [ ] Market analyst provides professional analysis using MCP data
- [ ] Recommendation agent generates actionable trades with MCP integration
- [ ] UI displays all portfolio metrics correctly (ROM, SSR, risk indicators, ROI)
- [ ] Error cases handled gracefully
- [ ] Indian market hours respected (9:15 AM - 3:30 PM IST)
- [ ] Stock scope list enforced - no analysis of unauthorized stocks
- [ ] Custom filters work correctly (SSR, premium, ROM, risk indicator)
- [ ] Professional analysis includes financial results, intrinsic value, social sentiment
- [ ] Short-term and medium-term analysis provided with confidence scores
- [ ] Recommendation types include new trade, swap trade, and hedge trade
- [ ] No modifications made to kiteMCPServer project

---

## Anti-Patterns to Avoid
- ❌ Don't modify the MCP server - it's a separate project
- ❌ Don't ignore market hours - check before making recommendations
- ❌ Don't skip stock scope validation - only analyze allowed stocks
- ❌ Don't hardcode risk thresholds - make them configurable
- ❌ Don't use sync functions in async contexts
- ❌ Don't ignore API rate limits - implement proper throttling
- ❌ Don't skip confidence scoring - always provide confidence levels
- ❌ Don't ignore portfolio constraints - respect margin limits
- ❌ Don't skip error handling for external API calls
- ❌ Don't assume MCP server is always available - handle connection failures

## Confidence Score: 9.5/10

**Reasoning for high confidence:**
- Comprehensive requirements with detailed examples and templates provided
- Clear separation of concerns (MCP server unchanged, all new logic in TradingInsight)
- Well-defined data models with explicit indicator calculations (ROM, SSR, RI)
- Professional-grade analysis templates with exact format specifications
- Complete user workflow mapping from UI to recommendations
- Comprehensive testing strategy with validation of all key metrics
- Indian market-specific constraints and compliance clearly defined
- Detailed pseudocode reflecting real-world implementation patterns

**Areas requiring minimal attention:**
- Edge cases in MCP data integration (normal for any complex system)
- User preference refinements during real-world usage
- Minor API rate limiting optimizations (handled in current design) 