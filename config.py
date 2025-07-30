"""
Simple Configuration Management for kiteMCP Client.
"""

import os
from typing import Dict, Any


def get_config() -> Dict[str, Any]:
    """Get application configuration from environment variables."""
    return {
        # LLM Configuration
        "llm_model": os.getenv("LLM_MODEL", "openai"),
        "model_name": os.getenv("MODEL_NAME", "gpt-4"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
        
        # MCP Server Configuration
        "mcp_server_host": os.getenv("MCP_SERVER_HOST", "localhost"),
        "mcp_server_port": int(os.getenv("MCP_SERVER_PORT", "8000")),
        "mcp_transport": os.getenv("MCP_TRANSPORT", "stdio"),
        
        # Trading Configuration
        "risk_tolerance": os.getenv("RISK_TOLERANCE", "medium"),
        "max_position_size": float(os.getenv("MAX_POSITION_SIZE", "0.02")),
        "stop_loss_percentage": float(os.getenv("STOP_LOSS_PERCENTAGE", "0.05")),
        "max_portfolio_risk": float(os.getenv("MAX_PORTFOLIO_RISK", "0.10")),
        
        # Analysis Configuration
        "analysis_timeframe": os.getenv("ANALYSIS_TIMEFRAME", "1d"),
        "sentiment_threshold": float(os.getenv("SENTIMENT_THRESHOLD", "0.6")),
        
        # UI Configuration
        "ui_theme": os.getenv("UI_THEME", "light"),
        "refresh_interval": int(os.getenv("REFRESH_INTERVAL", "300")),
        
        # Logging Configuration
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_file": os.getenv("LOG_FILE"),
    }


def get_llm_config() -> Dict[str, Any]:
    """Get LLM-specific configuration."""
    config = get_config()
    
    if config["llm_model"] == "openai":
        return {
            "api_key": config["openai_api_key"],
            "model": config["model_name"],
            "temperature": 0.1,
            "max_tokens": 4000
        }
    elif config["llm_model"] == "deepseek":
        return {
            "api_key": config["deepseek_api_key"],
            "model": config["model_name"],
            "temperature": 0.1,
            "max_tokens": 4000
        }
    else:
        raise ValueError(f"Unsupported LLM model: {config['llm_model']}")


def get_mcp_config() -> Dict[str, Any]:
    """Get MCP server configuration."""
    config = get_config()
    return {
        "host": config["mcp_server_host"],
        "port": config["mcp_server_port"],
        "transport": config["mcp_transport"]
    }


def get_trading_config() -> Dict[str, Any]:
    """Get trading configuration."""
    config = get_config()
    return {
        "risk_tolerance": config["risk_tolerance"],
        "max_position_size": config["max_position_size"],
        "stop_loss_percentage": config["stop_loss_percentage"],
        "max_portfolio_risk": config["max_portfolio_risk"]
    }


def validate_config() -> bool:
    """Validate that required configuration is present."""
    config = get_config()
    
    # Check LLM configuration
    if config["llm_model"] == "openai" and not config["openai_api_key"]:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if config["llm_model"] == "deepseek" and not config["deepseek_api_key"]:
        print("❌ DEEPSEEK_API_KEY not found in environment variables")
        return False
    
    print("✅ Configuration validated successfully")
    return True


def print_config():
    """Print current configuration (without sensitive data)."""
    config = get_config()
    
    print("📋 Current Configuration:")
    print("-" * 30)
    print(f"LLM Model: {config['llm_model']}")
    print(f"Model Name: {config['model_name']}")
    print(f"Risk Tolerance: {config['risk_tolerance']}")
    print(f"Max Position Size: {config['max_position_size']}")
    print(f"Max Portfolio Risk: {config['max_portfolio_risk']}")
    print(f"MCP Transport: {config['mcp_transport']}")
    print("-" * 30)


if __name__ == "__main__":
    # Test configuration
    print_config()
    validate_config() 