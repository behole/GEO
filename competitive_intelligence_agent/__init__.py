"""
Competitive Intelligence Agent (Agent 3)

Analyzes competitor content strategies and market positioning to identify
opportunities for improved GEO performance through competitive intelligence.
"""

from .competitive_intelligence_agent import CompetitiveIntelligenceAgent, run_competitive_intelligence
from .config import get_config, CompetitiveIntelligenceConfig
from .competitor_strategy_analyzer import CompetitorStrategyAnalyzer
from .market_position_tracker import MarketPositionTracker
from .strategic_insights_generator import StrategicInsightsGenerator

__version__ = "1.0.0"
__author__ = "GEO Optimization Framework"

__all__ = [
    "CompetitiveIntelligenceAgent",
    "run_competitive_intelligence",
    "get_config",
    "CompetitiveIntelligenceConfig",
    "CompetitorStrategyAnalyzer", 
    "MarketPositionTracker",
    "StrategicInsightsGenerator"
]