"""
Portfolio Service for Kite Trading Recommendation App.
Processes portfolio data from MCP server and provides portfolio analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from models.data_models import Portfolio, Position, ApplicationSettings
from services.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SectorAnalysis:
    """Sector-wise portfolio analysis."""
    sector: str
    total_margin: float
    position_count: int
    exposure_percentage: float
    total_premium_collected: float
    average_rom: float
    average_ssr: float
    average_risk_indicator: float
    risk_group: str


@dataclass
class PositionAnalysis:
    """Detailed position analysis."""
    position: Position
    roi_percentage: float
    reward_risk_ratio: float
    risk_group: str
    margin_efficiency: float


@dataclass
class PortfolioAnalysis:
    """Complete portfolio analysis."""
    total_margin: float
    available_cash: float
    total_exposure: float
    total_premium_collected: float
    overall_roi: float
    overall_risk_score: float
    sector_analyses: List[SectorAnalysis]
    position_analyses: List[PositionAnalysis]
    risk_distribution: Dict[str, int]
    margin_utilization: float


class PortfolioService:
    """Service for portfolio data processing and analysis."""
    
    def __init__(self, mcp_client: MCPClient, settings: ApplicationSettings):
        """Initialize portfolio service."""
        self.mcp_client = mcp_client
        self.settings = settings
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
    
    def _calculate_rom(self, premium_collected: float, margin_used: float) -> float:
        """Calculate ROM (Return on Margin)."""
        if margin_used <= 0:
            return 0.0
        return (premium_collected / margin_used) * 100
    
    def _calculate_ssr(self, spot_price: float, strike_price: float) -> float:
        """Calculate SSR (Spot to Strike Ratio)."""
        if spot_price <= 0:
            return 0.0
        return ((spot_price - strike_price) / spot_price) * 100
    
    def _calculate_roi(self, premium_collected: float, margin_used: float) -> float:
        """Calculate ROI (Return on Investment)."""
        if margin_used <= 0:
            return 0.0
        return (premium_collected / margin_used) * 100
    
    def _calculate_reward_risk_ratio(self, premium_collected: float, risk_indicator: int) -> float:
        """Calculate reward-risk ratio."""
        if risk_indicator <= 0:
            return 0.0
        return premium_collected / risk_indicator
    
    def _classify_risk_group(self, risk_indicator: int) -> str:
        """Classify position into risk group based on risk indicator."""
        if risk_indicator <= 3:
            return "Low Risk"
        elif risk_indicator <= 6:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def _calculate_margin_efficiency(self, premium_collected: float, margin_used: float) -> float:
        """Calculate margin efficiency (premium collected per unit margin)."""
        if margin_used <= 0:
            return 0.0
        return premium_collected / margin_used
    
    async def get_portfolio_analysis(self) -> PortfolioAnalysis:
        """Get comprehensive portfolio analysis."""
        try:
            logger.info("Getting portfolio analysis...")
            
            # Get portfolio data from MCP server
            portfolio = await self.mcp_client.get_portfolio_data()
            
            # Calculate overall metrics
            total_margin = portfolio.total_margin
            available_cash = portfolio.available_cash
            total_exposure = portfolio.total_exposure
            total_premium_collected = sum(pos.premium_collected for pos in portfolio.positions)
            
            # Calculate overall ROI
            overall_roi = self._calculate_roi(total_premium_collected, total_margin)
            
            # Calculate overall risk score (average of position risk indicators)
            if portfolio.positions:
                overall_risk_score = sum(pos.risk_indicator for pos in portfolio.positions) / len(portfolio.positions)
            else:
                overall_risk_score = 5.0
            
            # Calculate margin utilization
            margin_utilization = (total_margin / (total_margin + available_cash)) * 100 if (total_margin + available_cash) > 0 else 0
            
            # Analyze positions
            position_analyses = []
            for position in portfolio.positions:
                roi_percentage = self._calculate_roi(position.premium_collected, position.margin_used)
                reward_risk_ratio = self._calculate_reward_risk_ratio(position.premium_collected, position.risk_indicator)
                risk_group = self._classify_risk_group(position.risk_indicator)
                margin_efficiency = self._calculate_margin_efficiency(position.premium_collected, position.margin_used)
                
                position_analysis = PositionAnalysis(
                    position=position,
                    roi_percentage=roi_percentage,
                    reward_risk_ratio=reward_risk_ratio,
                    risk_group=risk_group,
                    margin_efficiency=margin_efficiency
                )
                position_analyses.append(position_analysis)
            
            # Analyze sectors
            sector_analyses = self._analyze_sectors(portfolio)
            
            # Calculate risk distribution
            risk_distribution = self._calculate_risk_distribution(position_analyses)
            
            # Create portfolio analysis
            portfolio_analysis = PortfolioAnalysis(
                total_margin=total_margin,
                available_cash=available_cash,
                total_exposure=total_exposure,
                total_premium_collected=total_premium_collected,
                overall_roi=overall_roi,
                overall_risk_score=overall_risk_score,
                sector_analyses=sector_analyses,
                position_analyses=position_analyses,
                risk_distribution=risk_distribution,
                margin_utilization=margin_utilization
            )
            
            logger.info("Portfolio analysis completed successfully")
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"Failed to get portfolio analysis: {e}")
            raise
    
    def _analyze_sectors(self, portfolio: Portfolio) -> List[SectorAnalysis]:
        """Analyze portfolio by sectors."""
        sector_data: Dict[str, Dict[str, Any]] = {}
        
        for position in portfolio.positions:
            # Determine sector (for demo, use symbol prefix)
            sector = position.symbol[:3] if len(position.symbol) >= 3 else "Other"
            
            if sector not in sector_data:
                sector_data[sector] = {
                    "total_margin": 0.0,
                    "position_count": 0,
                    "total_premium_collected": 0.0,
                    "rom_values": [],
                    "ssr_values": [],
                    "risk_indicators": []
                }
            
            sector_data[sector]["total_margin"] += position.margin_used
            sector_data[sector]["position_count"] += 1
            sector_data[sector]["total_premium_collected"] += position.premium_collected
            sector_data[sector]["rom_values"].append(position.rom)
            sector_data[sector]["ssr_values"].append(position.ssr)
            sector_data[sector]["risk_indicators"].append(position.risk_indicator)
        
        sector_analyses = []
        total_margin = portfolio.total_margin
        
        for sector, data in sector_data.items():
            exposure_percentage = (data["total_margin"] / total_margin) * 100 if total_margin > 0 else 0
            average_rom = sum(data["rom_values"]) / len(data["rom_values"]) if data["rom_values"] else 0
            average_ssr = sum(data["ssr_values"]) / len(data["ssr_values"]) if data["ssr_values"] else 0
            average_risk_indicator = sum(data["risk_indicators"]) / len(data["risk_indicators"]) if data["risk_indicators"] else 5
            
            risk_group = self._classify_risk_group(int(average_risk_indicator))
            
            sector_analysis = SectorAnalysis(
                sector=sector,
                total_margin=data["total_margin"],
                position_count=data["position_count"],
                exposure_percentage=exposure_percentage,
                total_premium_collected=data["total_premium_collected"],
                average_rom=average_rom,
                average_ssr=average_ssr,
                average_risk_indicator=average_risk_indicator,
                risk_group=risk_group
            )
            sector_analyses.append(sector_analysis)
        
        return sector_analyses
    
    def _calculate_risk_distribution(self, position_analyses: List[PositionAnalysis]) -> Dict[str, int]:
        """Calculate risk distribution across positions."""
        risk_distribution = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
        
        for analysis in position_analyses:
            risk_distribution[analysis.risk_group] += 1
        
        return risk_distribution
    
    async def get_position_details(self, symbol: str) -> Optional[PositionAnalysis]:
        """Get detailed analysis for a specific position."""
        try:
            portfolio = await self.mcp_client.get_portfolio_data()
            
            for position in portfolio.positions:
                if position.symbol == symbol:
                    roi_percentage = self._calculate_roi(position.premium_collected, position.margin_used)
                    reward_risk_ratio = self._calculate_reward_risk_ratio(position.premium_collected, position.risk_indicator)
                    risk_group = self._classify_risk_group(position.risk_indicator)
                    margin_efficiency = self._calculate_margin_efficiency(position.premium_collected, position.margin_used)
                    
                    return PositionAnalysis(
                        position=position,
                        roi_percentage=roi_percentage,
                        reward_risk_ratio=reward_risk_ratio,
                        risk_group=risk_group,
                        margin_efficiency=margin_efficiency
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get position details for {symbol}: {e}")
            raise
    
    def get_portfolio_summary(self, analysis: PortfolioAnalysis) -> Dict[str, Any]:
        """Get portfolio summary for display."""
        return {
            "total_margin": analysis.total_margin,
            "available_cash": analysis.available_cash,
            "total_exposure": analysis.total_exposure,
            "total_premium_collected": analysis.total_premium_collected,
            "overall_roi": analysis.overall_roi,
            "overall_risk_score": analysis.overall_risk_score,
            "margin_utilization": analysis.margin_utilization,
            "position_count": len(analysis.position_analyses),
            "sector_count": len(analysis.sector_analyses),
            "risk_distribution": analysis.risk_distribution
        } 