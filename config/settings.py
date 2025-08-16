"""
Configuration settings for Kite Trading Recommendation App.
Application settings, stock scope, filter constraints, and market hours validation.
"""

import os
from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from models.data_models import (
    ApplicationSettings, 
    StockScope, 
    FilterConstraints, 
    MarketHours
)


class TradingAppSettings(BaseSettings):
    """Main application settings."""
    
    # Application settings
    app_name: str = "Kite Trading Recommendation App"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Debug mode")
    
    # MCP Server settings
    mcp_server_url: str = Field(default="http://localhost:8000", description="MCP server URL")
    mcp_timeout: int = Field(default=30, description="MCP server timeout in seconds")
    
    # Cache settings
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    max_retries: int = Field(default=3, description="Maximum API retry attempts")
    retry_delay: float = Field(default=1.0, description="Retry delay in seconds")
    
    # Trading settings
    default_stock_scope: List[str] = Field(
        default=[
            "NIFTY50", "BANKNIFTY", "ICICIBANK", "HDFCBANK", "INFY", "TCS", 
            "RELIANCE", "TATAMOTORS", "AXISBANK", "SBIN", "WIPRO", "HCLTECH"
        ],
        description="Default approved stocks for analysis"
    )
    
    default_sectors: List[str] = Field(
        default=[
            "Banking", "IT", "Auto", "Oil & Gas", "Pharma", "FMCG", 
            "Metals", "Real Estate", "Power", "Telecom"
        ],
        description="Default sectors for analysis"
    )
    
    # Filter constraints
    default_min_ssr: float = Field(default=0.02, description="Default minimum SSR")
    default_min_premium: float = Field(default=0.05, description="Default minimum premium")
    default_min_rom: float = Field(default=0.05, description="Default minimum ROM")
    default_max_risk: int = Field(default=7, description="Default maximum risk indicator")
    
    # Market hours (IST)
    market_start_time: str = Field(default="09:15", description="Market start time")
    market_end_time: str = Field(default="15:30", description="Market end time")
    market_timezone: str = Field(default="Asia/Kolkata", description="Market timezone")
    
    # External API settings
    screener_base_url: str = Field(default="https://www.screener.in", description="Screener.in base URL")
    smart_investing_url: str = Field(default="https://www.smart-investing.in", description="Smart-Investing.in URL")
    tickertape_url: str = Field(default="https://www.tickertape.in", description="Tickertape.in URL")
    stockedge_url: str = Field(default="https://web.stockedge.com", description="StockEdge.com URL")
    
    # Rate limiting
    api_rate_limit: int = Field(default=10, description="API calls per minute")
    web_scraping_delay: float = Field(default=1.0, description="Delay between web scraping requests")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> ApplicationSettings:
    """Get application settings."""
    app_settings = TradingAppSettings()
    
    # Create StockScope
    stock_scope = StockScope(
        approved_stocks=app_settings.default_stock_scope,
        sectors=app_settings.default_sectors
    )
    
    # Create FilterConstraints
    filter_constraints = FilterConstraints(
        min_ssr=app_settings.default_min_ssr,
        min_premium=app_settings.default_min_premium,
        min_rom=app_settings.default_min_rom,
        max_risk=app_settings.default_max_risk
    )
    
    # Create MarketHours
    market_hours = MarketHours(
        start_time=app_settings.market_start_time,
        end_time=app_settings.market_end_time,
        timezone=app_settings.market_timezone
    )
    
    # Create ApplicationSettings
    settings = ApplicationSettings(
        stock_scope=stock_scope,
        filter_constraints=filter_constraints,
        market_hours=market_hours,
        cache_ttl=app_settings.cache_ttl,
        max_retries=app_settings.max_retries,
        retry_delay=app_settings.retry_delay,
        screener_base_url=app_settings.screener_base_url,
        smart_investing_url=app_settings.smart_investing_url,
        tickertape_url=app_settings.tickertape_url,
        stockedge_url=app_settings.stockedge_url
    )
    
    return settings


def get_stock_scope() -> StockScope:
    """Get stock scope configuration."""
    return get_settings().stock_scope


def get_filter_constraints() -> FilterConstraints:
    """Get filter constraints configuration."""
    return get_settings().filter_constraints


def get_market_hours() -> MarketHours:
    """Get market hours configuration."""
    return get_settings().market_hours


def is_market_open() -> bool:
    """Check if Indian market is currently open."""
    market_hours = get_market_hours()
    return market_hours.is_market_open()


def get_approved_stocks() -> List[str]:
    """Get list of approved stocks for analysis."""
    stock_scope = get_stock_scope()
    return stock_scope.approved_stocks


def is_stock_approved(symbol: str) -> bool:
    """Check if a stock is in the approved scope."""
    stock_scope = get_stock_scope()
    return stock_scope.is_stock_approved(symbol)


def validate_trading_hours() -> bool:
    """Validate that current time is within trading hours."""
    if not is_market_open():
        return False
    return True


def get_default_filters() -> dict:
    """Get default filter constraints as dictionary."""
    filters = get_filter_constraints()
    return {
        'min_ssr': filters.min_ssr,
        'min_premium': filters.min_premium,
        'min_rom': filters.min_rom,
        'max_risk': filters.max_risk
    }


# Environment-specific configurations
class DevelopmentSettings(TradingAppSettings):
    """Development environment settings."""
    debug: bool = True
    cache_ttl: int = 60  # Shorter cache for development


class ProductionSettings(TradingAppSettings):
    """Production environment settings."""
    debug: bool = False
    cache_ttl: int = 300  # Longer cache for production


def get_environment_settings() -> TradingAppSettings:
    """Get environment-specific settings."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# Example usage
if __name__ == "__main__":
    # Test settings
    settings = get_settings()
    print(f"App Name: {settings.stock_scope}")
    print(f"Approved Stocks: {get_approved_stocks()}")
    print(f"Market Open: {is_market_open()}")
    print(f"Default Filters: {get_default_filters()}")
    
    # Test stock approval
    test_symbols = ["ICICIBANK", "HDFCBANK", "INVALID_STOCK"]
    for symbol in test_symbols:
        print(f"{symbol} approved: {is_stock_approved(symbol)}") 