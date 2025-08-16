"""
Data models for Kite Trading Recommendation App.
Comprehensive Pydantic models for type safety and data validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from enum import Enum


class PositionType(str, Enum):
    """Position type enumeration."""
    LONG = "long"
    SHORT = "short"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationType(str, Enum):
    """Recommendation type enumeration."""
    NEW_TRADE = "new trade"
    SWAP_TRADE = "swap trade"
    HEDGE_TRADE = "hedge trade"


class Position(BaseModel):
    """Portfolio position model with trading indicators."""
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    margin_used: float
    premium_collected: float
    rom: float = Field(description="Return on Margin: Premium collected / Margin used (percentage)")
    ssr: float = Field(description="Strike Safety Ratio: (Spot price - Strike price) / Spot price (percentage)")
    risk_indicator: int = Field(ge=1, le=10, description="Risk Indicator: 1=min risk, 10=max risk")
    reward_risk_ratio: float = Field(description="Premium collected / Risk indicator")
    position_type: PositionType
    expiry: datetime
    strike_price: float
    option_type: str = Field(description="CE/PE")
    
    @validator('rom', 'ssr')
    def validate_percentages(cls, v):
        """Validate percentage values are reasonable."""
        if v < 0 or v > 100:
            raise ValueError(f"Percentage value {v} must be between 0 and 100")
        return v


class Portfolio(BaseModel):
    """Portfolio model with comprehensive metrics."""
    total_margin: float
    available_cash: float
    total_exposure: float
    positions: List[Position]
    sector_exposure: Dict[str, float]
    risk_score: float = Field(ge=0, le=10)
    
    @validator('total_margin', 'available_cash', 'total_exposure')
    def validate_positive_values(cls, v):
        """Validate financial values are positive."""
        if v < 0:
            raise ValueError(f"Financial value {v} must be positive")
        return v


class SentimentAnalysis(BaseModel):
    """Market sentiment analysis model following ICICIBANK template."""
    symbol: str
    short_term_sentiment: str
    short_term_target: Tuple[float, float]
    short_term_confidence: float = Field(ge=0, le=10)
    short_term_timeframe: str = "Next 2-4 weeks"
    medium_term_sentiment: str
    medium_term_target: Tuple[float, float]
    medium_term_confidence: float = Field(ge=0, le=10)
    medium_term_timeframe: str = "1-3 months"
    key_drivers: List[str]
    risks: List[str]
    summary: str
    financial_analysis: Dict[str, Any] = Field(description="Quarterly results analysis")
    intrinsic_value: Dict[str, Any] = Field(description="Overvalued/undervalued analysis")
    social_sentiment: Dict[str, Any] = Field(description="Social media and analyst ratings")
    
    @validator('short_term_sentiment', 'medium_term_sentiment')
    def validate_sentiment_values(cls, v):
        """Validate sentiment values are valid."""
        valid_sentiments = [
            "bullish", "bearish", "neutral", 
            "Cautiously Positive", "Moderately Positive", "Strongly Positive",
            "Cautiously Negative", "Moderately Negative", "Strongly Negative"
        ]
        if v not in valid_sentiments:
            raise ValueError(f"Sentiment '{v}' must be one of {valid_sentiments}")
        return v


class TradeRecommendation(BaseModel):
    """Trade recommendation model with detailed reasoning."""
    recommendation_type: RecommendationType
    symbol: str
    option_type: str = Field(description="CE/PE")
    strike_price: float
    expiry: str
    quantity: int
    price_range: Tuple[float, float]
    confidence: float = Field(ge=0, le=10)
    trade_driver: str
    risk_assessment: str
    expected_rom: float
    expected_ssr: float
    reasoning: str = Field(description="Full reasoning behind recommendation")
    portfolio_impact: str = Field(description="How this affects portfolio diversification")
    comparison_with_existing: Optional[str] = Field(None, description="For swap trades")
    
    @validator('expected_rom', 'expected_ssr')
    def validate_percentages(cls, v):
        """Validate percentage values are reasonable."""
        if v < 0 or v > 100:
            raise ValueError(f"Percentage value {v} must be between 0 and 100")
        return v


class FilterConstraints(BaseModel):
    """Filter constraints for trade recommendations."""
    min_ssr: float = Field(default=0.02, ge=0, le=1, description="Minimum Strike Safety Ratio")
    min_premium: float = Field(default=0.05, ge=0, le=1, description="Minimum premium percentage")
    min_rom: float = Field(default=0.05, ge=0, le=1, description="Minimum Return on Margin")
    max_risk: int = Field(default=7, ge=1, le=10, description="Maximum risk indicator")


class StockScope(BaseModel):
    """Stock scope configuration."""
    approved_stocks: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    
    def is_stock_approved(self, symbol: str) -> bool:
        """Check if a stock is in the approved scope."""
        return symbol in self.approved_stocks


class MarketHours(BaseModel):
    """Indian market trading hours configuration."""
    start_time: str = "09:15"
    end_time: str = "15:30"
    timezone: str = "Asia/Kolkata"
    
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        from datetime import datetime
        import pytz
        
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check time
        current_time = now.strftime("%H:%M")
        return self.start_time <= current_time <= self.end_time


class ApplicationSettings(BaseModel):
    """Application configuration settings."""
    stock_scope: StockScope
    filter_constraints: FilterConstraints
    market_hours: MarketHours
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    max_retries: int = Field(default=3, description="Maximum API retry attempts")
    retry_delay: float = Field(default=1.0, description="Retry delay in seconds")
    
    # External API settings
    screener_base_url: str = Field(default="https://www.screener.in", description="Screener.in base URL")
    smart_investing_url: str = Field(default="https://www.smart-investing.in", description="Smart-Investing.in URL")
    tickertape_url: str = Field(default="https://www.tickertape.in", description="Tickertape.in URL")
    stockedge_url: str = Field(default="https://web.stockedge.com", description="StockEdge.com URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Example usage and validation
if __name__ == "__main__":
    # Test data models
    position = Position(
        symbol="ICICIBANK",
        quantity=100,
        average_price=1500.0,
        current_price=1520.0,
        pnl=2000.0,
        margin_used=50000.0,
        premium_collected=5000.0,
        rom=10.0,  # 10%
        ssr=5.0,   # 5%
        risk_indicator=6,
        reward_risk_ratio=833.33,  # 5000/6
        position_type=PositionType.SHORT,
        expiry=datetime.now(),
        strike_price=1460.0,
        option_type="PE"
    )
    
    print(f"Position created: {position.symbol}")
    print(f"ROM: {position.rom}%")
    print(f"SSR: {position.ssr}%")
    print(f"Risk Indicator: {position.risk_indicator}/10") 