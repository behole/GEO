import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    significant: float
    critical: float

@dataclass
class CompetitorMonitoringConfig:
    """Configuration for competitor monitoring"""
    name: str
    priority: str  # "high", "medium", "low"
    monitoring_frequency: str  # "daily", "weekly", "bi-weekly"
    focus_areas: List[str]

@dataclass
class PerformanceTargets:
    """Performance target configuration"""
    discovery_score_target: float
    context_score_target: float
    competitive_score_target: float
    timeline_weeks: int

@dataclass
class BusinessMetrics:
    """Business metrics tracking configuration"""
    track_conversions: bool
    roi_attribution: bool
    brand_mention_value: float
    traffic_attribution: bool

@dataclass
class NotificationChannels:
    """Notification channel configuration"""
    slack_webhook: Optional[str]
    email_alerts: List[str]
    dashboard_url: Optional[str]
    sms_alerts: List[str]

class MonitoringAlertingConfig:
    """Main configuration class for Monitoring & Alerting Agent"""
    
    def __init__(self, sector_config_path: Optional[str] = None):
        # Environment variables
        self.BRAND_NAME = os.getenv("BRAND_NAME", "Brush on Block")
        self.BRAND_WEBSITE = os.getenv("BRAND_WEBSITE", "https://brushonblock.com")
        
        # Monitoring settings
        self.MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.REAL_TIME_MONITORING = os.getenv("REAL_TIME_MONITORING", "true").lower() == "true"
        self.MONITORING_INTERVAL_HOURS = int(os.getenv("MONITORING_INTERVAL_HOURS", "6"))
        self.ALERT_SENSITIVITY = os.getenv("ALERT_SENSITIVITY", "medium")  # high, medium, low
        
        # Data retention settings
        self.DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "365"))
        self.HISTORICAL_ANALYSIS_DAYS = int(os.getenv("HISTORICAL_ANALYSIS_DAYS", "90"))
        self.TREND_ANALYSIS_WINDOW_DAYS = int(os.getenv("TREND_ANALYSIS_WINDOW_DAYS", "30"))
        
        # Performance settings
        self.MAX_CONCURRENT_MONITORS = int(os.getenv("MAX_CONCURRENT_MONITORS", "5"))
        self.MONITOR_TIMEOUT = int(os.getenv("MONITOR_TIMEOUT", "60"))
        self.RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
        
        # Output settings
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./monitoring_results")
        self.DASHBOARD_ENABLED = os.getenv("DASHBOARD_ENABLED", "true").lower() == "true"
        self.SAVE_RAW_MONITORING_DATA = os.getenv("SAVE_RAW_MONITORING_DATA", "true").lower() == "true"
        
        # Integration paths
        self.AGENT1_RESULTS_PATH = os.getenv("AGENT1_RESULTS_PATH", "./results/")
        self.AGENT2_RESULTS_PATH = os.getenv("AGENT2_RESULTS_PATH", "./results/")
        self.AGENT3_RESULTS_PATH = os.getenv("AGENT3_RESULTS_PATH", "./results/")
        
        # Alert thresholds from specification
        self.ALERT_THRESHOLDS = {
            "performance_changes": {
                "discovery_score": AlertThreshold(significant=10, critical=20),
                "context_score": AlertThreshold(significant=15, critical=25),
                "competitive_score": AlertThreshold(significant=12, critical=20)
            },
            "competitive_movements": {
                "market_share_change": {"watch": 5, "alert": 10, "urgent": 20},
                "new_competitor_emergence": {"citation_threshold": 25}
            },
            "opportunity_detection": {
                "content_gap_score": {"threshold": 75},
                "query_trend_growth": {"percentage": 30}
            }
        }
        
        # Load sector configuration
        if sector_config_path:
            self.sector_config = self._load_sector_config(sector_config_path)
        else:
            # Default to beauty sunscreen monitoring config
            default_path = os.path.join(os.path.dirname(__file__), "sector_configs", "beauty_sunscreen_monitoring.yaml")
            self.sector_config = self._load_sector_config(default_path)
    
    def _load_sector_config(self, config_path: str) -> Dict[str, Any]:
        """Load sector-specific monitoring configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.warning(f"Sector configuration file not found: {config_path}, using defaults")
            return self._get_default_sector_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing sector configuration: {str(e)}")
    
    def _get_default_sector_config(self) -> Dict[str, Any]:
        """Get default sector configuration"""
        return {
            "monitoring_config": {
                "key_queries_subset": 20,
                "competitor_focus": 5,
                "alert_sensitivity": "medium",
                "performance_targets": {
                    "discovery_score_target": 60,
                    "context_score_target": 75,
                    "competitive_score_target": 45,
                    "timeline_weeks": 12
                },
                "business_metrics": {
                    "track_conversions": True,
                    "roi_attribution": True,
                    "brand_mention_value": 50,
                    "traffic_attribution": True
                },
                "notification_channels": {
                    "slack_webhook": None,
                    "email_alerts": [],
                    "dashboard_url": None,
                    "sms_alerts": []
                }
            }
        }
    
    def get_competitors_to_monitor(self) -> List[CompetitorMonitoringConfig]:
        """Get competitor monitoring configuration"""
        competitors = []
        
        # Load from Agent 3 results first
        agent3_setup = self.load_agent3_monitoring_setup()
        if agent3_setup and 'monitoring_setup' in agent3_setup:
            for competitor_name in agent3_setup['monitoring_setup'].get('competitors_to_track', []):
                competitors.append(CompetitorMonitoringConfig(
                    name=competitor_name,
                    priority="high",
                    monitoring_frequency="weekly",
                    focus_areas=["content_strategy", "authority_signals", "market_position"]
                ))
        
        # Fallback to sector config
        if not competitors:
            competitor_config = self.sector_config.get("monitoring_config", {}).get("competitors", [])
            for comp in competitor_config:
                # Handle both string and dict competitors
                if isinstance(comp, str):
                    competitors.append(CompetitorMonitoringConfig(
                        name=comp,
                        priority="medium",
                        monitoring_frequency="weekly",
                        focus_areas=["content_strategy", "market_position"]
                    ))
                elif isinstance(comp, dict):
                    competitors.append(CompetitorMonitoringConfig(
                        name=comp.get("name", ""),
                        priority=comp.get("priority", "medium"),
                        monitoring_frequency=comp.get("monitoring_frequency", "weekly"),
                        focus_areas=comp.get("focus_areas", [])
                    ))
        
        return competitors
    
    def get_performance_targets(self) -> PerformanceTargets:
        """Get performance target configuration"""
        targets = self.sector_config.get("monitoring_config", {}).get("performance_targets", {})
        
        return PerformanceTargets(
            discovery_score_target=targets.get("discovery_score_target", 60),
            context_score_target=targets.get("context_score_target", 75),
            competitive_score_target=targets.get("competitive_score_target", 45),
            timeline_weeks=targets.get("timeline_weeks", 12)
        )
    
    def get_business_metrics_config(self) -> BusinessMetrics:
        """Get business metrics configuration"""
        metrics = self.sector_config.get("monitoring_config", {}).get("business_metrics", {})
        
        return BusinessMetrics(
            track_conversions=metrics.get("track_conversions", True),
            roi_attribution=metrics.get("roi_attribution", True),
            brand_mention_value=metrics.get("brand_mention_value", 50),
            traffic_attribution=metrics.get("traffic_attribution", True)
        )
    
    def get_notification_channels(self) -> NotificationChannels:
        """Get notification channel configuration"""
        channels = self.sector_config.get("monitoring_config", {}).get("notification_channels", {})
        
        return NotificationChannels(
            slack_webhook=channels.get("slack_webhook") or os.getenv("SLACK_WEBHOOK"),
            email_alerts=channels.get("email_alerts", []),
            dashboard_url=channels.get("dashboard_url") or os.getenv("DASHBOARD_URL"),
            sms_alerts=channels.get("sms_alerts", [])
        )
    
    def load_agent1_results(self) -> Optional[Dict[str, Any]]:
        """Load Agent 1 (Discovery Baseline) results"""
        agent1_path = Path(self.AGENT1_RESULTS_PATH)
        
        try:
            # Look for discovery baseline results (try both naming patterns)
            for results_file in agent1_path.glob("**/complete_results.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
            
            for results_file in agent1_path.glob("**/geo_analysis_complete.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
                    
            # Look for any JSON results file in discovery directories
            for discovery_dir in agent1_path.glob("discovery_baseline_*"):
                json_files = list(discovery_dir.glob("*.json"))
                if json_files:
                    # Sort by modification time to get the latest
                    json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    with open(json_files[0], 'r') as f:
                        return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 1 results: {str(e)}")
        
        return None
    
    def load_agent2_results(self) -> Optional[Dict[str, Any]]:
        """Load Agent 2 (Content Analysis) results"""
        agent2_path = Path(self.AGENT2_RESULTS_PATH)
        
        try:
            # Look for content analysis complete results
            for results_file in agent2_path.glob("**/content_analysis_complete.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
                    
            # Look for any JSON results file in content analysis directories
            for content_dir in agent2_path.glob("content_analysis_*"):
                json_files = list(content_dir.glob("*.json"))
                if json_files:
                    # Sort by modification time to get the latest
                    json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    with open(json_files[0], 'r') as f:
                        return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 2 results: {str(e)}")
        
        return None
    
    def load_agent3_results(self) -> Optional[Dict[str, Any]]:
        """Load Agent 3 (Competitive Intelligence) results"""
        agent3_path = Path(self.AGENT3_RESULTS_PATH)
        
        try:
            # Look for competitive intelligence complete results
            for results_file in agent3_path.glob("**/competitive_intelligence_complete.json"):
                with open(results_file, 'r') as f:
                    return json.load(f)
                    
            # Look for any JSON results file in competitive intelligence directories
            for competitive_dir in agent3_path.glob("competitive_intelligence_*"):
                json_files = list(competitive_dir.glob("*.json"))
                if json_files:
                    # Sort by modification time to get the latest
                    json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    with open(json_files[0], 'r') as f:
                        return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 3 results: {str(e)}")
        
        return None
    
    def load_agent3_monitoring_setup(self) -> Optional[Dict[str, Any]]:
        """Load Agent 3 monitoring setup specifically"""
        agent3_path = Path(self.AGENT3_RESULTS_PATH)
        
        try:
            # Look for Agent 4 monitoring setup file from Agent 3
            for setup_file in agent3_path.glob("**/agent4_monitoring_setup.json"):
                with open(setup_file, 'r') as f:
                    return json.load(f)
            
            # Look in competitive intelligence directories specifically
            for competitive_dir in agent3_path.glob("competitive_intelligence_*"):
                setup_files = list(competitive_dir.glob("agent4_monitoring_setup.json"))
                if setup_files:
                    # Sort by modification time to get the latest
                    setup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    with open(setup_files[0], 'r') as f:
                        return json.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load Agent 3 monitoring setup: {str(e)}")
        
        return None
    
    def get_baseline_metrics(self) -> Dict[str, Any]:
        """Get baseline metrics from all agents"""
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "agent1_baseline": None,
            "agent2_baseline": None,
            "agent3_baseline": None,
            "initial_scores": {
                "discovery": 12.9,  # From user specification
                "context": 57.5,
                "competitive": 19.4
            }
        }
        
        # Load baseline data from agents
        agent1_data = self.load_agent1_results()
        if agent1_data:
            baseline["agent1_baseline"] = {
                "query_count": agent1_data.get("query_count", 0),
                "average_score": agent1_data.get("average_score", 0),
                "top_competitors": agent1_data.get("top_competitors", [])
            }
        
        agent2_data = self.load_agent2_results()
        if agent2_data:
            baseline["agent2_baseline"] = {
                "overall_content_score": agent2_data.get("overall_content_score", 0),
                "content_gaps": len(agent2_data.get("content_gaps", [])),
                "optimization_opportunities": len(agent2_data.get("optimization_opportunities", []))
            }
        
        agent3_data = self.load_agent3_results()
        if agent3_data:
            baseline["agent3_baseline"] = {
                "competitors_analyzed": len(agent3_data.get("competitors_analyzed", [])),
                "market_gaps": len(agent3_data.get("market_gap_opportunities", [])),
                "strategic_insights": len(agent3_data.get("strategic_insights", []))
            }
        
        return baseline
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate monitoring configuration"""
        issues = []
        
        # Check monitoring settings
        if not self.MONITORING_ENABLED:
            issues.append("Monitoring is disabled")
        
        if self.MONITORING_INTERVAL_HOURS < 1:
            issues.append("Monitoring interval too short (minimum 1 hour)")
        
        # Check agent integration
        agent_integration = {
            "agent1_available": self.load_agent1_results() is not None,
            "agent2_available": self.load_agent2_results() is not None,
            "agent3_available": self.load_agent3_results() is not None
        }
        
        if not any(agent_integration.values()):
            issues.append("No agent results available for monitoring")
        
        # Check notification channels
        notification_channels = self.get_notification_channels()
        has_notifications = any([
            notification_channels.slack_webhook,
            notification_channels.email_alerts,
            notification_channels.sms_alerts
        ])
        
        if not has_notifications:
            issues.append("No notification channels configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "agent_integration": agent_integration,
            "competitors_to_monitor": len(self.get_competitors_to_monitor()),
            "monitoring_enabled": self.MONITORING_ENABLED,
            "alert_sensitivity": self.ALERT_SENSITIVITY
        }

# Singleton instance for global access
_config_instance = None

def get_config(sector_config_path: Optional[str] = None) -> MonitoringAlertingConfig:
    """Get or create global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = MonitoringAlertingConfig(sector_config_path)
    return _config_instance

def reload_config(sector_config_path: Optional[str] = None) -> MonitoringAlertingConfig:
    """Force reload of configuration"""
    global _config_instance
    _config_instance = MonitoringAlertingConfig(sector_config_path)
    return _config_instance

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)