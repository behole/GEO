import os
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BrandConfig:
    """Brand configuration data"""
    name: str
    website: str
    variations: List[str]

@dataclass
class CompetitorConfig:
    """Competitor configuration data"""
    name: str
    website: str
    priority: str

@dataclass
class ContentTypeConfig:
    """Content type analysis configuration"""
    weight: float
    required_elements: List[str]

@dataclass
class ScoringConfig:
    """Scoring weight configuration"""
    content_structure: float
    citation_worthiness: float
    authority_signals: float
    competitor_gap_coverage: float
    ai_consumption_optimization: float

class Config:
    """Main configuration class for Content Analysis Agent"""
    
    def __init__(self, sector_config_path: Optional[str] = None):
        # Environment variables
        self.BRAND_NAME = os.getenv("BRAND_NAME", "Brush on Block")
        self.BRAND_WEBSITE = os.getenv("BRAND_WEBSITE", "https://brushonblock.com")
        self.BRAND_VARIATIONS = os.getenv("BRAND_VARIATIONS", "").split(",")
        
        # Analysis settings
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.MAX_PAGES_PER_SITE = int(os.getenv("MAX_PAGES_PER_SITE", "100"))
        self.CRAWL_DEPTH = int(os.getenv("CRAWL_DEPTH", "3"))
        
        # Output settings
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./results")
        self.ENABLE_SCREENSHOTS = os.getenv("ENABLE_SCREENSHOTS", "false").lower() == "true"
        self.SAVE_HTML_CONTENT = os.getenv("SAVE_HTML_CONTENT", "true").lower() == "true"
        
        # Selenium settings
        self.USE_SELENIUM = os.getenv("USE_SELENIUM", "false").lower() == "true"
        self.SELENIUM_IMPLICIT_WAIT = int(os.getenv("SELENIUM_IMPLICIT_WAIT", "10"))
        self.CHROME_HEADLESS = os.getenv("CHROME_HEADLESS", "true").lower() == "true"
        
        # Agent 1 integration
        self.AGENT1_RESULTS_PATH = os.getenv("AGENT1_RESULTS_PATH", "../discovery_baseline_agent/results/latest/")
        
        # Load sector configuration
        if sector_config_path:
            self.sector_config = self._load_sector_config(sector_config_path)
        else:
            # Default to beauty sunscreen sector
            default_path = os.path.join(os.path.dirname(__file__), "sector_configs", "beauty_sunscreen.yaml")
            self.sector_config = self._load_sector_config(default_path)
    
    def _load_sector_config(self, config_path: str) -> Dict[str, Any]:
        """Load sector-specific configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Sector configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing sector configuration: {str(e)}")
    
    def get_brand_config(self) -> BrandConfig:
        """Get brand configuration"""
        brand_data = self.sector_config.get("brand", {})
        return BrandConfig(
            name=brand_data.get("name", self.BRAND_NAME),
            website=brand_data.get("website", self.BRAND_WEBSITE),
            variations=brand_data.get("variations", self.BRAND_VARIATIONS)
        )
    
    def get_competitors(self) -> List[CompetitorConfig]:
        """Get competitor configuration"""
        competitors = []
        competitor_data = self.sector_config.get("competitors", {})
        
        for category in ["primary", "secondary"]:
            for comp in competitor_data.get(category, []):
                competitors.append(CompetitorConfig(
                    name=comp["name"],
                    website=comp["website"],
                    priority=comp["priority"]
                ))
        
        return competitors
    
    def get_content_types(self) -> Dict[str, ContentTypeConfig]:
        """Get content type configurations"""
        content_types = {}
        content_data = self.sector_config.get("content_types", {})
        
        for content_type, config in content_data.items():
            content_types[content_type] = ContentTypeConfig(
                weight=config["weight"],
                required_elements=config["required_elements"]
            )
        
        return content_types
    
    def get_scoring_weights(self) -> ScoringConfig:
        """Get scoring configuration"""
        weights = self.sector_config.get("scoring_weights", {})
        return ScoringConfig(
            content_structure=weights.get("content_structure", 0.25),
            citation_worthiness=weights.get("citation_worthiness", 0.25),
            authority_signals=weights.get("authority_signals", 0.20),
            competitor_gap_coverage=weights.get("competitor_gap_coverage", 0.20),
            ai_consumption_optimization=weights.get("ai_consumption_optimization", 0.10)
        )
    
    def get_keywords(self) -> Dict[str, List[str]]:
        """Get sector-specific keywords"""
        return self.sector_config.get("keywords", {})
    
    def get_geo_best_practices(self) -> Dict[str, Any]:
        """Get GEO best practices configuration"""
        return self.sector_config.get("geo_best_practices", {})
    
    def get_quality_benchmarks(self) -> Dict[str, Any]:
        """Get content quality benchmarks"""
        return self.sector_config.get("quality_benchmarks", {})
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the loaded configuration"""
        issues = []
        
        # Check required fields
        required_fields = ["brand", "competitors", "content_types", "scoring_weights"]
        for field in required_fields:
            if field not in self.sector_config:
                issues.append(f"Missing required field: {field}")
        
        # Validate brand configuration
        brand_config = self.sector_config.get("brand", {})
        if not brand_config.get("name"):
            issues.append("Brand name is required")
        if not brand_config.get("website"):
            issues.append("Brand website is required")
        
        # Validate scoring weights sum to 1.0
        weights = self.sector_config.get("scoring_weights", {})
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            issues.append(f"Scoring weights don't sum to 1.0 (current: {total_weight})")
        
        # Validate content type weights
        content_weights = self.sector_config.get("content_types", {})
        if content_weights:
            content_total = sum(config.get("weight", 0) for config in content_weights.values())
            if abs(content_total - 1.0) > 0.01:
                issues.append(f"Content type weights don't sum to 1.0 (current: {content_total})")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "sector": self.sector_config.get("sector", "unknown"),
            "product_type": self.sector_config.get("product_type", "unknown"),
            "competitors_count": len(self.get_competitors()),
            "content_types_count": len(self.get_content_types())
        }

# Singleton instance for global access
_config_instance = None

def get_config(sector_config_path: Optional[str] = None) -> Config:
    """Get or create global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(sector_config_path)
    return _config_instance

def reload_config(sector_config_path: Optional[str] = None) -> Config:
    """Force reload of configuration"""
    global _config_instance
    _config_instance = Config(sector_config_path)
    return _config_instance