# kiteMCP Client

## Overview
This directory contains the MCP client that connects to the kiteMCP server and provides AI-powered trading analysis and recommendations through CLI and web interfaces.

## Files
- `app.py` - Streamlit web UI
- `main.py` - CLI entry point
- `analyzer.py` - Orchestrates all analysis
- `mcp_client.py` - Connects to MCP server
- `llm_client.py` - LLM API wrapper
- `config.py` - Configuration management
- `logging_utils.py` - Logging and feedback tracking
- `opportunity_scanner.py` - AI-powered opportunity scanner
- `risk.py` - Risk analysis functions
- `greeks.py` - Greeks calculation
- `news.py` - News aggregation
- `cli.py` - CLI interface
- `requirements.txt` - Python dependencies
- `env.example` - Environment template
- `README.md` - This file

## Quick Start
```bash
cd MCPClient
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # Edit .env with your API keys and settings
```

## Usage

### CLI Mode
```bash
python main.py full      # Full portfolio analysis
python main.py quick     # Quick overview
python main.py risk      # Risk assessment
python main.py web       # Start web interface
```

### Web Interface
```bash
streamlit run app.py
# Or via main.py
python main.py web
```

## Features
- AI-powered portfolio analysis and recommendations
- Self-improving recommendation engine based on user feedback
- Real-time market data integration
- Advanced portfolio analytics (Greeks, risk, performance)
- Beautiful Streamlit web interface
- Comprehensive logging and history tracking 