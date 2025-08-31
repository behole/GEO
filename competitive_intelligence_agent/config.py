import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CompetitorConfig:
    """Individual competitor configuration"""
    name: str
    website: str
    priority: str
    focus_areas: List[str]
    market_share_estimate: float = 0.0

@dataclass
class QueryExtensionConfig:
    """Query extension configuration"""
    base_queries: List[str]
    competitor_specific: List[str]
    long_tail_variations: List[str]
    seasonal_queries: List[str]

@dataclass  
class AuthoritySignalConfig:
    """Authority signal analysis configuration"""
    expert_indicators: List[str]
    clinical_indicators: List[str]
    certification_indicators: List[str]
    award_indicators: List[str]

@dataclass
class AnalysisWeights:
    """Scoring weights for competitive analysis"""
    content_depth: float
    authority_signals: float
    ai_optimization: float
    citation_worthiness: float
    content_freshness: float

class CompetitiveIntelligenceConfig:
    """Main configuration class for Competitive Intelligence Agent"""
    
    def __init__(self, sector_config_path: Optional[str] = None):
        # Environment variables
        self.BRAND_NAME = os.getenv("BRAND_NAME", "Brush on Block")
        self.BRAND_WEBSITE = os.getenv("BRAND_WEBSITE", "https://brushonblock.com")
        
        # Analysis settings
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "3"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "45"))
        self.RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.MAX_COMPETITORS_ANALYZED = int(os.getenv("MAX_COMPETITORS_ANALYZED", "10"))
        self.ANALYSIS_DEPTH_DAYS = int(os.getenv("ANALYSIS_DEPTH_DAYS", "30"))
        
        # Query expansion settings
        self.BASE_QUERY_EXPANSION_FACTOR = float(os.getenv("BASE_QUERY_EXPANSION_FACTOR", "2.0"))
        self.INCLUDE_BRAND_COMPARISON_QUERIES = os.getenv("INCLUDE_BRAND_COMPARISON_QUERIES", "true").lower() == "true"
        self.INCLUDE_SEASONAL_QUERIES = os.getenv("INCLUDE_SEASONAL_QUERIES", "true").lower() == "true"
        
        # Output settings
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./intelligence_results")
        self.ENABLE_DETAILED_REPORTING = os.getenv("ENABLE_DETAILED_REPORTING", "true").lower() == "true"
        self.SAVE_RAW_ANALYSIS_DATA = os.getenv("SAVE_RAW_ANALYSIS_DATA", "true").lower() == "true"
        
        # Load sector configuration
        if sector_config_path:
            self.sector_config = self._load_sector_config(sector_config_path)
        else:
            # Default to beauty sunscreen competitive config
            default_path = os.path.join(os.path.dirname(__file__), "sector_configs", "beauty_sunscreen_competitive.yaml")
            self.sector_config = self._load_sector_config(default_path)
        
        # Integration paths
        agent_paths = self.sector_config.get("agent_paths", {})
        self.AGENT1_RESULTS_PATH = agent_paths.get("agent1_results", os.getenv("AGENT1_RESULTS_PATH", "../discovery_baseline_agent/results/latest/"))
        self.AGENT2_RESULTS_PATH = agent_paths.get("agent2_results", os.getenv("AGENT2_RESULTS_PATH", "../content_analysis_agent/results/latest/"))
    
    def _load_sector_config(self, config_path: str) -> Dict[str, Any]:
        """Load sector-specific competitive intelligence configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Sector configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing sector configuration: {str(e)}")
    
    def get_competitors(self) -> List[CompetitorConfig]:
        """Get competitor configuration list"""
        competitors = []
        competitor_data = self.sector_config.get("competitive_analysis", {}).get("competitors", {})
        
        for category in ["primary", "secondary", "emerging"]:
            for comp in competitor_data.get(category, []):
                competitors.append(CompetitorConfig(
                    name=comp["name"],
                    website=comp["website"],
                    priority=comp["priority"],
                    focus_areas=comp.get("focus_areas", []),
                    market_share_estimate=comp.get("market_share_estimate", 0.0)
                ))
        
        return competitors[:self.MAX_COMPETITORS_ANALYZED]
    
    def get_query_extensions(self) -> QueryExtensionConfig:
        """Get query extension configuration"""
        query_config = self.sector_config.get("competitive_analysis", {}).get("query_extensions", {})
        
        return QueryExtensionConfig(
            base_queries=query_config.get("base_queries", []),
            competitor_specific=query_config.get("competitor_specific", []),
            long_tail_variations=query_config.get("long_tail_variations", []),
            seasonal_queries=query_config.get("seasonal_queries", [])
        )
    
    def get_authority_signals(self) -> AuthoritySignalConfig:
        """Get authority signal analysis configuration"""
        authority_config = self.sector_config.get("competitive_analysis", {}).get("authority_signals", {})
        
        return AuthoritySignalConfig(
            expert_indicators=authority_config.get("expert_indicators", []),
            clinical_indicators=authority_config.get("clinical_indicators", []),
            certification_indicators=authority_config.get("certification_indicators", []),
            award_indicators=authority_config.get("award_indicators", [])
        )
    
    def get_content_analysis_focus(self) -> List[str]:
        """Get content types to focus analysis on"""
        return self.sector_config.get("competitive_analysis", {}).get("content_types_to_analyze", [])
    
    def get_analysis_weights(self) -> AnalysisWeights:
        """Get analysis scoring weights"""
        weights = self.sector_config.get("competitive_analysis", {}).get("analysis_weights", {})
        
        return AnalysisWeights(
            content_depth=weights.get("content_depth", 0.25),
            authority_signals=weights.get("authority_signals", 0.25),
            ai_optimization=weights.get("ai_optimization", 0.20),
            citation_worthiness=weights.get("citation_worthiness", 0.20),
            content_freshness=weights.get("content_freshness", 0.10)
        )
    
    def get_market_intelligence_config(self) -> Dict[str, Any]:
        """Get market intelligence analysis configuration"""
        return self.sector_config.get("competitive_analysis", {}).get("market_intelligence", {})
    
    def load_agent1_results(self) -> Optional[Dict[str, Any]]:
        """Load Agent 1 (Discovery Baseline) results for integration"""
        agent1_path = Path(self.AGENT1_RESULTS_PATH)
        
        try:
            # Look for latest query results
            for results_file in agent1_path.glob("**/query_results.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
                    
            # Look for any JSON results file
            json_files = list(agent1_path.glob("**/*.json"))
            if json_files:
                with open(json_files[0], 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 1 results: {str(e)}")
        
        return None
    
    def load_agent2_results(self) -> Optional[Dict[str, Any]]:
        """Load Agent 2 (Content Analysis) results for integration"""
        agent2_path = Path(self.AGENT2_RESULTS_PATH)
        
        try:
            # Look for content analysis complete results
            for results_file in agent2_path.glob("**/content_analysis_complete.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
                    
            # Look for any JSON results file
            json_files = list(agent2_path.glob("**/*.json"))
            if json_files:
                with open(json_files[0], 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 2 results: {str(e)}")
        
        return None
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate competitive intelligence configuration"""
        issues = []
        
        # Check required fields
        required_fields = ["competitive_analysis"]
        for field in required_fields:
            if field not in self.sector_config:
                issues.append(f"Missing required field: {field}")
        
        # Validate competitors
        competitors = self.get_competitors()
        if not competitors:
            issues.append("No competitors configured for analysis")
        elif len(competitors) < 2:
            issues.append("Need at least 2 competitors for meaningful analysis")
        
        # Validate analysis weights
        weights = self.get_analysis_weights()
        total_weight = (
            weights.content_depth + 
            weights.authority_signals + 
            weights.ai_optimization + 
            weights.citation_worthiness + 
            weights.content_freshness
        )
        
        if abs(total_weight - 1.0) > 0.01:
            issues.append(f"Analysis weights don't sum to 1.0 (current: {total_weight})")
        
        # Check integration paths
        agent1_results = self.load_agent1_results()
        agent2_results = self.load_agent2_results()
        
        integration_status = {
            "agent1_available": agent1_results is not None,
            "agent2_available": agent2_results is not None
        }
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "competitors_configured": len(competitors),
            "integration_status": integration_status,
            "sector": self.sector_config.get("sector", "unknown"),
            "analysis_depth_days": self.ANALYSIS_DEPTH_DAYS
        }

# Singleton instance for global access
_config_instance = None

def get_config(sector_config_path: Optional[str] = None) -> CompetitiveIntelligenceConfig:
    """Get or create global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = CompetitiveIntelligenceConfig(sector_config_path)
    return _config_instance

def reload_config(sector_config_path: Optional[str] = None) -> CompetitiveIntelligenceConfig:
    """Force reload of configuration"""
    global _config_instance
    _config_instance = CompetitiveIntelligenceConfig(sector_config_path)
    return _config_instance
