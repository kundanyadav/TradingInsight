name: "MCP Client App Enhancement - Comprehensive Trading Assistant"
description: |

## Purpose
Enhance the existing MCP client app to provide a more robust, feature-rich trading assistant with improved error handling, real-time data integration, and advanced analytics capabilities.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Transform the existing MCP client app into a comprehensive, production-ready trading assistant that seamlessly integrates with the kiteMCP server, provides real-time portfolio analysis, advanced risk management, and intelligent trading recommendations.

## Why
- **Business Value**: Enable traders to make informed decisions with AI-powered analysis
- **User Impact**: Reduce trading risks and improve portfolio performance through intelligent insights
- **Integration**: Seamless connection between MCP server capabilities and client-side analytics
- **Problems Solved**: Manual analysis complexity, risk management gaps, missed opportunities

## What
### User-Visible Behavior
- Real-time portfolio monitoring with live P&L updates
- Advanced risk assessment with VaR calculations and stress testing
- Intelligent opportunity scanning with AI-powered recommendations
- Comprehensive news aggregation with sentiment analysis
- Greeks analysis for options positions
- Interactive web interface with Streamlit
- CLI interface for power users
- Automated logging and performance tracking

### Technical Requirements
- Enhanced MCP client with robust error handling and reconnection logic
- Real-time data streaming from kiteMCP server
- Advanced analytics engine with multiple analysis types
- Comprehensive test suite with unit and integration tests
- Production-ready logging and monitoring
- Configuration management with environment variables
- Performance optimization for large portfolios

### Success Criteria
- [ ] MCP client connects reliably with automatic reconnection
- [ ] Real-time portfolio updates with <5 second latency
- [ ] Advanced risk analysis with VaR and stress testing
- [ ] AI-powered trading recommendations with 80%+ accuracy
- [ ] Comprehensive test coverage (>90%)
- [ ] Production-ready error handling and logging
- [ ] Web interface loads in <3 seconds
- [ ] CLI interface provides all web features

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://modelcontextprotocol.io/docs
  why: MCP protocol specification and best practices for client-server communication
  
- url: https://kite.trade/docs/connect/v3/
  why: Kite Connect API documentation for trading data and authentication
  
- url: https://streamlit.io/docs
  why: Streamlit web framework documentation for UI components and state management
  
- file: KiteAIApp/mcp_client.py
  why: Current MCP client implementation to understand existing patterns and improve upon
  
- file: KiteAIApp/app.py
  why: Current Streamlit web interface to understand UI patterns and state management
  
- file: KiteAIApp/analyzer.py
  why: Portfolio analysis logic to enhance with advanced analytics
  
- file: KiteAIApp/risk.py
  why: Risk management functions to expand with VaR and stress testing
  
- file: kiteMCPServer/mcp_server.py
  why: MCP server implementation to understand available tools, prompts, and resources
  
- doc: https://pandas.pydata.org/docs/
  section: Data manipulation and analysis
  critical: Use pandas for efficient data processing and analysis
  
- doc: https://plotly.com/python/
  section: Interactive charts and dashboards
  critical: Use Plotly for real-time interactive visualizations
```

### Current Codebase Tree
```bash
KiteAIApp/
├── .cursor/
│   ├── PRPs/
│   └── rules/
├── .venv/
├── __init__.py
├── app.py                 # Streamlit web interface
├── analyzer.py            # Portfolio analysis logic
├── cli.py                # Command-line interface
├── config.py             # Configuration management
├── greeks.py             # Options Greeks calculations
├── llm_client.py         # LLM integration
├── logging_utils.py      # Logging utilities
├── main.py               # Main entry point
├── mcp_client.py         # MCP client implementation
├── news.py               # News aggregation
├── opportunity_scanner.py # Opportunity scanning
├── risk.py               # Risk management
├── requirements.txt      # Dependencies
└── env.example          # Environment variables template
```

### Desired Codebase Tree
```bash
KiteAIApp/
├── .cursor/
│   ├── PRPs/
│   └── rules/
├── .venv/
├── __init__.py
├── app.py                 # Enhanced Streamlit web interface
├── analyzer.py            # Enhanced portfolio analysis
├── cli.py                # Enhanced CLI interface
├── config.py             # Enhanced configuration management
├── greeks.py             # Enhanced Greeks calculations
├── llm_client.py         # Enhanced LLM integration
├── logging_utils.py      # Enhanced logging utilities
├── main.py               # Enhanced main entry point
├── mcp_client.py         # Enhanced MCP client with reconnection
├── news.py               # Enhanced news aggregation
├── opportunity_scanner.py # Enhanced opportunity scanning
├── risk.py               # Enhanced risk management with VaR
├── requirements.txt      # Updated dependencies
├── env.example          # Updated environment variables
├── tests/               # NEW: Comprehensive test suite
│   ├── __init__.py
│   ├── test_mcp_client.py
│   ├── test_analyzer.py
│   ├── test_risk.py
│   └── test_integration.py
├── utils/               # NEW: Utility functions
│   ├── __init__.py
│   ├── data_processing.py
│   ├── validation.py
│   └── helpers.py
└── docs/                # NEW: Documentation
    ├── API.md
    ├── SETUP.md
    └── USAGE.md
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: MCP client requires proper error handling for connection failures
# Example: kiteMCPServer may not be running, causing connection errors
# Example: Kite Connect API has rate limits (10 requests/second)
# Example: Streamlit session state must be initialized before use
# Example: Async functions must be properly awaited in Streamlit
# Example: pandas DataFrames should be converted to dict for JSON serialization
# Example: Plotly charts need proper layout configuration for responsive design
```

## Implementation Blueprint

### Data Models and Structure
```python
# Enhanced data models for better type safety and consistency
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class PortfolioPosition(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    pnl: float
    pnl_percentage: float
    instrument_type: str
    exchange: str

class RiskMetrics(BaseModel):
    var_95: float
    var_99: float
    max_drawdown: float
    sharpe_ratio: float
    beta: float
    correlation_matrix: Dict[str, Dict[str, float]]

class TradingRecommendation(BaseModel):
    action: str  # "BUY", "SELL", "HOLD", "HEDGE"
    symbol: str
    reason: str
    confidence: float
    risk_level: str
    target_price: Optional[float]
    stop_loss: Optional[float]

class MCPConnectionStatus(BaseModel):
    connected: bool
    last_heartbeat: datetime
    tools_available: List[str]
    prompts_available: List[str]
    resources_available: List[str]
```

### List of Tasks to be Completed

```yaml
Task 1: ENHANCE mcp_client.py
  - ADD robust error handling with automatic reconnection
  - ADD connection status monitoring
  - ADD retry logic for failed API calls
  - ADD comprehensive logging
  - ADD async context manager support
  - PRESERVE existing method signatures

Task 2: ENHANCE analyzer.py
  - ADD advanced portfolio analytics (VaR, Sharpe ratio, beta)
  - ADD correlation analysis between positions
  - ADD sector-wise analysis
  - ADD performance attribution
  - ADD historical analysis capabilities
  - KEEP existing analysis functions

Task 3: ENHANCE risk.py
  - ADD Value at Risk (VaR) calculations
  - ADD stress testing scenarios
  - ADD Monte Carlo simulations
  - ADD portfolio heat maps
  - ADD risk decomposition
  - KEEP existing risk functions

Task 4: CREATE tests/ directory
  - CREATE test_mcp_client.py with connection tests
  - CREATE test_analyzer.py with analytics tests
  - CREATE test_risk.py with risk calculation tests
  - CREATE test_integration.py with end-to-end tests
  - ADD pytest fixtures and mocks

Task 5: CREATE utils/ directory
  - CREATE data_processing.py for data manipulation
  - CREATE validation.py for input validation
  - CREATE helpers.py for common utilities
  - ADD type hints and documentation

Task 6: ENHANCE app.py
  - ADD real-time data updates
  - ADD advanced visualizations
  - ADD interactive filters
  - ADD export functionality
  - ADD performance optimizations
  - KEEP existing UI components

Task 7: ENHANCE cli.py
  - ADD all web interface features
  - ADD batch processing capabilities
  - ADD configuration management
  - ADD export options
  - ADD verbose logging options

Task 8: UPDATE requirements.txt
  - ADD testing dependencies (pytest, pytest-asyncio)
  - ADD data analysis libraries (scipy, numpy)
  - ADD visualization libraries (plotly, seaborn)
  - ADD monitoring libraries (prometheus-client)
  - UPDATE existing dependencies

Task 9: CREATE docs/ directory
  - CREATE API.md with comprehensive API documentation
  - CREATE SETUP.md with installation and configuration
  - CREATE USAGE.md with usage examples and best practices
  - ADD code examples and troubleshooting guides
```

### Per Task Pseudocode

```python
# Task 1: Enhanced MCP Client
class EnhancedMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.connection_status = MCPConnectionStatus()
        self.retry_config = RetryConfig(max_attempts=3, backoff_factor=2)
        self.logger = setup_logger("mcp_client")
    
    async def connect(self) -> bool:
        """Enhanced connection with automatic retry and monitoring"""
        for attempt in range(self.retry_config.max_attempts):
            try:
                # PATTERN: Use existing connection logic
                server_params = StdioServerParameters(
                    command="python",
                    args=["../kiteMCPServer/mcp_server.py"]
                )
                
                self.session = await stdio_client(server_params)
                await self.session.initialize()
                await self._discover_capabilities()
                
                # CRITICAL: Update connection status
                self.connection_status.connected = True
                self.connection_status.last_heartbeat = datetime.now()
                
                self.logger.info("Successfully connected to MCP server")
                return True
                
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_config.max_attempts - 1:
                    await asyncio.sleep(self.retry_config.backoff_factor ** attempt)
        
        return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced tool calling with error handling and retry"""
        if not self.session or not self.connection_status.connected:
            await self._ensure_connection()
        
        # PATTERN: Use existing retry decorator
        @retry(attempts=3, backoff=exponential)
        async def _call_tool():
            result = await self.session.call_tool(tool_name, arguments or {})
            return result.content
        
        try:
            return await _call_tool()
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}

# Task 2: Enhanced Portfolio Analyzer
class EnhancedPortfolioAnalyzer:
    def __init__(self, mcp_client: EnhancedMCPClient):
        self.mcp_client = mcp_client
        self.logger = setup_logger("portfolio_analyzer")
    
    async def analyze_portfolio_advanced(self) -> Dict[str, Any]:
        """Advanced portfolio analysis with risk metrics"""
        try:
            # PATTERN: Use existing portfolio data fetching
            portfolio_data = await self.mcp_client.get_portfolio()
            
            # NEW: Calculate advanced metrics
            risk_metrics = self._calculate_risk_metrics(portfolio_data)
            correlation_matrix = self._calculate_correlations(portfolio_data)
            sector_analysis = self._analyze_sectors(portfolio_data)
            
            # PATTERN: Use existing recommendation format
            recommendations = await self._generate_recommendations(
                portfolio_data, risk_metrics
            )
            
            return {
                "success": True,
                "portfolio": portfolio_data,
                "risk_metrics": risk_metrics,
                "correlation_matrix": correlation_matrix,
                "sector_analysis": sector_analysis,
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Advanced analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_risk_metrics(self, portfolio_data: Dict) -> RiskMetrics:
        """Calculate VaR, Sharpe ratio, and other risk metrics"""
        # CRITICAL: Use scipy for statistical calculations
        import scipy.stats as stats
        
        returns = self._calculate_returns(portfolio_data)
        
        # Calculate VaR at 95% and 99% confidence levels
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Calculate Sharpe ratio (assuming risk-free rate of 2%)
        excess_returns = returns - 0.02/252  # Daily risk-free rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            max_drawdown=self._calculate_max_drawdown(returns),
            sharpe_ratio=sharpe_ratio,
            beta=self._calculate_beta(returns),
            correlation_matrix=self._calculate_correlations(portfolio_data)
        )

# Task 3: Enhanced Risk Management
class EnhancedRiskManager:
    def __init__(self, mcp_client: EnhancedMCPClient):
        self.mcp_client = mcp_client
        self.logger = setup_logger("risk_manager")
    
    async def calculate_var(self, confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate Value at Risk with Monte Carlo simulation"""
        try:
            portfolio_data = await self.mcp_client.get_portfolio()
            
            # CRITICAL: Use Monte Carlo simulation for VaR
            returns = self._calculate_historical_returns(portfolio_data)
            simulated_returns = self._monte_carlo_simulation(returns, 10000)
            
            var_value = np.percentile(simulated_returns, (1 - confidence_level) * 100)
            
            return {
                "success": True,
                "var": var_value,
                "confidence_level": confidence_level,
                "portfolio_value": self._calculate_portfolio_value(portfolio_data)
            }
            
        except Exception as e:
            self.logger.error(f"VaR calculation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _monte_carlo_simulation(self, returns: np.ndarray, simulations: int) -> np.ndarray:
        """Run Monte Carlo simulation for risk analysis"""
        # CRITICAL: Use numpy for efficient array operations
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Generate random returns based on historical distribution
        simulated_returns = np.random.normal(
            mean_return, std_return, (simulations, len(returns))
        )
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + simulated_returns, axis=1)
        
        return cumulative_returns[:, -1] - 1  # Final portfolio return

# Task 4: Test Suite
class TestMCPClient:
    """Comprehensive tests for MCP client functionality"""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create MCP client for testing"""
        client = EnhancedMCPClient()
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_connection_success(self, mcp_client):
        """Test successful connection to MCP server"""
        # CRITICAL: Mock the MCP server for testing
        with patch('mcp.client.stdio.stdio_client') as mock_client:
            mock_session = AsyncMock()
            mock_client.return_value = mock_session
            
            result = await mcp_client.connect()
            
            assert result is True
            assert mcp_client.connection_status.connected is True
    
    @pytest.mark.asyncio
    async def test_connection_failure_with_retry(self, mcp_client):
        """Test connection failure with automatic retry"""
        with patch('mcp.client.stdio.stdio_client') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            result = await mcp_client.connect()
            
            assert result is False
            assert mcp_client.connection_status.connected is False
            assert mock_client.call_count == 3  # Max retry attempts

# Task 6: Enhanced Web Interface
def render_enhanced_portfolio_dashboard():
    """Enhanced portfolio dashboard with real-time updates"""
    st.subheader("📊 Enhanced Portfolio Dashboard")
    
    # CRITICAL: Use session state for caching
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    
    # Real-time data refresh
    if st.button("🔄 Refresh Data") or st.session_state.portfolio_data is None:
        with st.spinner("Fetching latest portfolio data..."):
            # PATTERN: Use existing MCP client
            mcp_client = create_mcp_client()
            portfolio_data = asyncio.run(mcp_client.get_portfolio())
            st.session_state.portfolio_data = portfolio_data
    
    if st.session_state.portfolio_data:
        # Enhanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # CRITICAL: Use Plotly for interactive charts
            fig = go.Figure()
            # Add portfolio value over time
            fig.add_trace(go.Scatter(
                x=portfolio_data.get('dates', []),
                y=portfolio_data.get('values', []),
                mode='lines+markers',
                name='Portfolio Value'
            ))
            fig.update_layout(title="Portfolio Value Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk metrics visualization
            risk_metrics = st.session_state.portfolio_data.get('risk_metrics', {})
            if risk_metrics:
                st.metric("VaR (95%)", f"₹{risk_metrics.get('var_95', 0):,.2f}")
                st.metric("Sharpe Ratio", f"{risk_metrics.get('sharpe_ratio', 0):.2f}")
                st.metric("Max Drawdown", f"{risk_metrics.get('max_drawdown', 0):.2f}%")
```

### Integration Points
```yaml
DATABASE:
  - No database required (uses MCP server for data)
  
CONFIG:
  - add to: config.py
  - pattern: "MCP_RETRY_ATTEMPTS = int(os.getenv('MCP_RETRY_ATTEMPTS', '3'))"
  - pattern: "MCP_CONNECTION_TIMEOUT = int(os.getenv('MCP_CONNECTION_TIMEOUT', '30'))"
  - pattern: "RISK_CONFIDENCE_LEVEL = float(os.getenv('RISK_CONFIDENCE_LEVEL', '0.95'))"
  
ROUTES:
  - No new routes (uses existing Streamlit interface)
  
LOGGING:
  - add to: logging_utils.py
  - pattern: "setup_logger('mcp_client', level=logging.INFO)"
  - pattern: "setup_logger('portfolio_analyzer', level=logging.INFO)"
  - pattern: "setup_logger('risk_manager', level=logging.INFO)"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check KiteAIApp/ --fix  # Auto-fix what's possible
mypy KiteAIApp/              # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE tests/test_mcp_client.py with these test cases:
@pytest.mark.asyncio
async def test_enhanced_mcp_client_connection():
    """Test enhanced MCP client connection with retry logic"""
    client = EnhancedMCPClient()
    result = await client.connect()
    assert result is True
    assert client.connection_status.connected is True

@pytest.mark.asyncio
async def test_portfolio_analysis_advanced():
    """Test advanced portfolio analysis with risk metrics"""
    client = EnhancedMCPClient()
    analyzer = EnhancedPortfolioAnalyzer(client)
    result = await analyzer.analyze_portfolio_advanced()
    assert result["success"] is True
    assert "risk_metrics" in result
    assert "correlation_matrix" in result

@pytest.mark.asyncio
async def test_risk_calculations():
    """Test VaR and risk metric calculations"""
    client = EnhancedMCPClient()
    risk_manager = EnhancedRiskManager(client)
    result = await risk_manager.calculate_var(confidence_level=0.95)
    assert result["success"] is True
    assert "var" in result
    assert result["confidence_level"] == 0.95
```

```bash
# Run and iterate until passing:
uv run pytest tests/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the MCP server
cd kiteMCPServer && python mcp_server.py

# In another terminal, test the enhanced client
cd KiteAIApp && python -m pytest tests/test_integration.py -v

# Test the web interface
streamlit run app.py

# Expected: All tests pass, web interface loads successfully
# If error: Check logs at logs/kitemcp_client.log for stack trace
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check KiteAIApp/`
- [ ] No type errors: `uv run mypy KiteAIApp/`
- [ ] MCP client connects successfully with retry logic
- [ ] Advanced portfolio analysis works with risk metrics
- [ ] VaR calculations are accurate and reasonable
- [ ] Web interface loads and displays real-time data
- [ ] CLI interface provides all enhanced features
- [ ] Error handling is comprehensive and informative
- [ ] Logging is informative but not verbose
- [ ] Documentation is complete and accurate

---

## Anti-Patterns to Avoid
- ❌ Don't break existing API contracts without migration plan
- ❌ Don't skip validation because "it should work"
- ❌ Don't ignore failing tests - fix them
- ❌ Don't use sync functions in async context
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific
- ❌ Don't forget to handle MCP server disconnections
- ❌ Don't ignore rate limits in Kite Connect API
- ❌ Don't create new patterns when existing ones work

---

## Score: 9/10
**Confidence Level**: High confidence in one-pass implementation success through comprehensive context, existing codebase patterns, and clear implementation blueprint. 