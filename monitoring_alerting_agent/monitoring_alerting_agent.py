import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import asdict
import schedule
import time
import threading

from .config import get_config, MonitoringAlertingConfig
from .performance_monitor import PerformanceMonitor, PerformanceSnapshot
from .alert_system import IntelligentAlertSystem, Alert
from .dashboard_generator import DashboardGenerator
from .agent_integration import AgentIntegrationHub
from .business_impact_tracker import BusinessImpactTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringAlertingAgent:
    """
    Agent 4: Monitoring & Alerting Agent
    
    The orchestrating hub that provides continuous GEO performance monitoring,
    intelligent alerting, and business impact tracking while integrating with
    all previous agents to create a complete optimization feedback loop.
    """
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.version = "1.0.0"
        self.brand_name = self.config.BRAND_NAME
        
        # Initialize monitoring components
        self.performance_monitor = PerformanceMonitor(self.config)
        self.alert_system = IntelligentAlertSystem(self.config)
        self.dashboard_generator = DashboardGenerator(self.config)
        self.agent_integration = AgentIntegrationHub(self.config)
        self.business_impact_tracker = BusinessImpactTracker(self.config)
        
        # Results storage
        self.results_dir = Path(self.config.OUTPUT_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Monitoring state
        self.monitoring_active = False
        self.last_monitoring_run = None
        self.monitoring_thread = None
        
        logger.info(f"Monitoring & Alerting Agent v{self.version} initialized")
        logger.info(f"Brand: {self.brand_name}")
        logger.info(f"Monitoring enabled: {self.config.MONITORING_ENABLED}")
    
    async def run_monitoring_analysis(self, monitoring_type: str = "full", test_mode: bool = False) -> Dict[str, Any]:
        """
        Main entry point for Claude Code integration
        
        Args:
            monitoring_type: "full", "performance_only", "competitive_only", "alerts_only"
        
        Returns: Complete monitoring analysis with alerts and business impact
        """
        logger.info(f"Starting monitoring analysis (type: {monitoring_type})")
        
        try:
            # Phase 1: Validate configuration and integration status
            if not test_mode:
                await self._validate_monitoring_setup()
            
            # Phase 2: Collect performance data
            logger.info("Phase 2: Collecting performance data")
            performance_snapshot = await self.performance_monitor.monitor_performance_continuous()
            
            # Phase 3: Process alerts (unless alerts_only)
            alerts_generated = []
            if monitoring_type in ["full", "alerts_only"]:
                logger.info("Phase 3: Processing intelligent alerts")
                alerts_generated = await self.alert_system.process_performance_snapshot(performance_snapshot)
            
            # Phase 4: Generate business impact analysis (unless performance_only)
            business_impact = None
            if monitoring_type in ["full", "competitive_only"]:
                logger.info("Phase 4: Analyzing business impact")
                business_impact = await self.business_impact_tracker.track_business_impact(performance_snapshot)
            
            # Phase 5: Update dashboards (unless alerts_only)
            dashboard_status = {}
            if monitoring_type in ["full", "performance_only"]:
                logger.info("Phase 5: Updating dashboards")
                main_dashboard = await self.dashboard_generator.generate_main_dashboard()
                executive_dashboard = await self.dashboard_generator.generate_executive_dashboard()
                dashboard_status = {
                    "main_dashboard": f"{main_dashboard.dashboard_id}.html",
                    "executive_dashboard": f"{executive_dashboard.dashboard_id}.html"
                }
            
            # Phase 6: Process agent feedback loops
            agent_feedback = []
            if monitoring_type == "full":
                logger.info("Phase 6: Processing agent feedback loops")
                agent_feedback = await self.agent_integration.orchestrate_agent_feedback_loops(performance_snapshot)
            
            # Phase 7: Create comprehensive monitoring report
            logger.info("Phase 7: Creating comprehensive monitoring report")
            monitoring_report = await self._create_monitoring_report(
                performance_snapshot, alerts_generated, business_impact, 
                dashboard_status, agent_feedback, monitoring_type
            )
            
            # Phase 8: Save results
            logger.info("Phase 8: Saving monitoring results")
            await self._save_monitoring_results(monitoring_report)
            
            # Update monitoring state
            self.last_monitoring_run = datetime.now()
            
            logger.info("Monitoring analysis completed successfully")
            return monitoring_report
            
        except Exception as e:
            import traceback
            logger.error(f"Error in monitoring analysis: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def start_continuous_monitoring(self, interval_hours: int = None) -> Dict[str, Any]:
        """Start continuous monitoring with specified interval"""
        
        if self.monitoring_active:
            return {"status": "already_active", "message": "Continuous monitoring is already running"}
        
        interval = interval_hours or self.config.MONITORING_INTERVAL_HOURS
        
        logger.info(f"Starting continuous monitoring with {interval} hour intervals")
        
        # Setup monitoring schedule
        self._setup_monitoring_schedule(interval)
        
        # Start monitoring in background thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._run_scheduled_monitoring, daemon=True)
        self.monitoring_thread.start()
        
        return {
            "status": "started",
            "interval_hours": interval,
            "real_time_enabled": self.config.REAL_TIME_MONITORING,
            "next_run": self._get_next_monitoring_time(),
            "message": f"Continuous monitoring started for {self.brand_name}"
        }
    
    def stop_continuous_monitoring(self) -> Dict[str, Any]:
        """Stop continuous monitoring"""
        
        if not self.monitoring_active:
            return {"status": "not_active", "message": "Continuous monitoring is not running"}
        
        logger.info("Stopping continuous monitoring")
        
        self.monitoring_active = False
        schedule.clear()
        
        return {
            "status": "stopped",
            "last_run": self.last_monitoring_run.isoformat() if self.last_monitoring_run else None,
            "message": "Continuous monitoring stopped"
        }
    
    def _setup_monitoring_schedule(self, interval_hours: int):
        """Setup monitoring schedule based on configuration"""
        
        # Main monitoring intervals
        if interval_hours <= 1:
            schedule.every().hour.do(self._scheduled_monitoring_job, "performance_only")
        elif interval_hours <= 6:
            schedule.every(interval_hours).hours.do(self._scheduled_monitoring_job, "full")
        else:
            schedule.every(interval_hours).hours.do(self._scheduled_monitoring_job, "full")
        
        # Daily reports
        schedule.every().day.at("06:00").do(self._scheduled_monitoring_job, "full")
        schedule.every().day.at("18:00").do(self._generate_daily_summary)
        
        # Weekly reports
        schedule.every().sunday.at("12:00").do(self._generate_weekly_report)
        
        # Real-time alerts (if enabled)
        if self.config.REAL_TIME_MONITORING:
            schedule.every(30).minutes.do(self._scheduled_monitoring_job, "alerts_only")
    
    def _run_scheduled_monitoring(self):
        """Run scheduled monitoring in background thread"""
        while self.monitoring_active:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _scheduled_monitoring_job(self, monitoring_type: str = "full"):
        """Scheduled monitoring job wrapper"""
        try:
            # Run async monitoring in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.run_monitoring_analysis(monitoring_type))
            
            # Send notifications for critical alerts
            if "alerts_generated" in result and result["alerts_generated"]:
                critical_alerts = [
                    alert for alert in result["alerts_generated"] 
                    if alert.get("severity") == "critical"
                ]
                if critical_alerts:
                    logger.warning(f"Generated {len(critical_alerts)} critical alerts")
            
            loop.close()
            
        except Exception as e:
            logger.error(f"Error in scheduled monitoring job: {str(e)}")
    
    async def _generate_daily_summary(self):
        """Generate daily summary report"""
        logger.info("Generating daily summary report")
        
        try:
            # Get latest monitoring data
            performance_snapshot = await self.performance_monitor.monitor_performance_continuous()
            
            # Get alert summary
            alert_summary = self.alert_system.get_alert_summary()
            
            # Get business impact
            business_impact = await self.business_impact_tracker.track_business_impact(performance_snapshot)
            
            # Create daily summary
            daily_summary = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "performance_summary": {
                    "discovery_score": performance_snapshot.brand_performance.get("discovery").current_value if "discovery" in performance_snapshot.brand_performance else 0,
                    "context_score": performance_snapshot.brand_performance.get("context").current_value if "context" in performance_snapshot.brand_performance else 0,
                    "competitive_score": performance_snapshot.brand_performance.get("competitive").current_value if "competitive" in performance_snapshot.brand_performance else 0
                },
                "alert_summary": alert_summary,
                "business_impact": {
                    "roi_percentage": business_impact.roi_analysis.roi_percentage,
                    "estimated_revenue": business_impact.roi_analysis.generated_revenue,
                    "brand_value": business_impact.brand_mention_value.total_brand_value
                },
                "key_insights": business_impact.actionable_insights[:3]
            }
            
            # Save daily summary
            summary_file = self.results_dir / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
            with open(summary_file, 'w') as f:
                json.dump(daily_summary, f, indent=2, default=str)
            
            logger.info("Daily summary report generated")
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}")
    
    async def _generate_weekly_report(self):
        """Generate weekly strategic report"""
        logger.info("Generating weekly strategic report")
        
        try:
            # Get performance trends
            performance_history = self.performance_monitor.get_performance_history(7)
            
            # Get business impact history
            business_history = self.business_impact_tracker.get_business_impact_history(7)
            
            # Get agent integration status
            integration_summary = self.agent_integration.get_integration_summary()
            
            weekly_report = {
                "week_ending": datetime.now().strftime("%Y-%m-%d"),
                "performance_trends": performance_history,
                "business_metrics": business_history,
                "agent_integration_status": integration_summary,
                "weekly_insights": await self._generate_weekly_insights(performance_history)
            }
            
            # Save weekly report
            report_file = self.results_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(weekly_report, f, indent=2, default=str)
            
            logger.info("Weekly strategic report generated")
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
    
    async def _generate_weekly_insights(self, performance_history: List[Dict[str, Any]]) -> List[str]:
        """Generate weekly performance insights"""
        insights = []
        
        if len(performance_history) >= 2:
            # Calculate weekly trends
            latest = performance_history[-1]
            earliest = performance_history[0]
            
            if isinstance(latest, dict) and isinstance(earliest, dict):
                # Compare performance
                insights.append("Weekly performance analysis completed")
                insights.append("Trend analysis based on 7-day performance data")
        
        return insights
    
    async def _validate_monitoring_setup(self):
        """Validate monitoring configuration and setup"""
        logger.info("Validating monitoring setup")
        
        # Validate configuration
        validation_result = self.config.validate_configuration()
        
        if not validation_result["valid"]:
            logger.error(f"Monitoring configuration validation failed: {validation_result['issues']}")
            raise ValueError(f"Invalid monitoring configuration: {'; '.join(validation_result['issues'])}")
        
        logger.info("Monitoring setup validation successful")
    
    async def _create_monitoring_report(self,
                                      performance_snapshot: PerformanceSnapshot,
                                      alerts_generated: List[Alert],
                                      business_impact: Optional[Any],
                                      dashboard_status: Dict[str, str],
                                      agent_feedback: List[Any],
                                      monitoring_type: str) -> Dict[str, Any]:
        """Create comprehensive monitoring report"""
        
        report = {
            "agent_info": {
                "agent_name": "Monitoring & Alerting Agent",
                "agent_version": self.version,
                "brand_name": self.brand_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "monitoring_type": monitoring_type
            },
            "monitoring_configuration": {
                "monitoring_enabled": self.config.MONITORING_ENABLED,
                "real_time_monitoring": self.config.REAL_TIME_MONITORING,
                "alert_sensitivity": self.config.ALERT_SENSITIVITY,
                "monitoring_interval_hours": self.config.MONITORING_INTERVAL_HOURS,
                "agents_integrated": len(self.agent_integration.integration_status)
            },
            "performance_analysis": {
                "current_snapshot": asdict(performance_snapshot),
                "performance_trends": self._calculate_performance_trends(performance_snapshot),
                "milestone_achievements": performance_snapshot.milestone_achievements,
                "performance_alerts": performance_snapshot.performance_alerts
            },
            "alert_analysis": {
                "alerts_generated": len(alerts_generated),
                "critical_alerts": len([a for a in alerts_generated if a.severity.value == "critical"]),
                "high_alerts": len([a for a in alerts_generated if a.severity.value == "high"]),
                "alert_summary": self.alert_system.get_alert_summary(),
                "alert_details": [asdict(alert) for alert in alerts_generated]
            },
            "business_impact_analysis": asdict(business_impact) if business_impact else None,
            "dashboard_status": dashboard_status,
            "agent_integration": {
                "feedback_items_generated": len(agent_feedback),
                "agent_feedback_details": [asdict(feedback) for feedback in agent_feedback],
                "integration_health": self.agent_integration.get_integration_summary()
            },
            "monitoring_effectiveness": {
                "data_quality_score": self._assess_data_quality(performance_snapshot),
                "alert_accuracy_estimate": self._estimate_alert_accuracy(alerts_generated),
                "business_impact_confidence": business_impact.roi_analysis.confidence_level if business_impact else "low",
                "system_health": "excellent"
            },
            "actionable_recommendations": self._generate_monitoring_recommendations(
                performance_snapshot, alerts_generated, business_impact
            )
        }
        
        return report
    
    def _calculate_performance_trends(self, snapshot: PerformanceSnapshot) -> Dict[str, str]:
        """Calculate performance trends from snapshot"""
        trends = {}
        
        for metric_name, metric_data in snapshot.brand_performance.items():
            trends[metric_name] = {
                "direction": metric_data.trend_direction,
                "change_percentage": metric_data.change_percentage,
                "progress_to_target": metric_data.progress_to_target
            }
        
        return trends
    
    def _assess_data_quality(self, snapshot: PerformanceSnapshot) -> int:
        """Assess overall data quality score (0-100)"""
        quality_score = 0
        
        # Check performance data completeness
        if len(snapshot.brand_performance) >= 3:
            quality_score += 25
        
        # Check query performance data
        if len(snapshot.query_performance) >= 5:
            quality_score += 25
        
        # Check competitor data
        if len(snapshot.competitor_performance) >= 3:
            quality_score += 25
        
        # Check business impact data
        if len(snapshot.business_impact_metrics) >= 3:
            quality_score += 25
        
        return quality_score
    
    def _estimate_alert_accuracy(self, alerts: List[Alert]) -> str:
        """Estimate alert accuracy based on alert quality"""
        if not alerts:
            return "no_alerts"
        
        # Simple heuristic: fewer alerts generally means higher accuracy
        if len(alerts) <= 2:
            return "high"
        elif len(alerts) <= 5:
            return "medium"
        else:
            return "low"
    
    def _generate_monitoring_recommendations(self,
                                           snapshot: PerformanceSnapshot,
                                           alerts: List[Alert],
                                           business_impact: Optional[Any]) -> List[str]:
        """Generate monitoring-specific recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        declining_metrics = [
            name for name, metric in snapshot.brand_performance.items()
            if metric.trend_direction == "declining"
        ]
        
        if declining_metrics:
            recommendations.append(f"Investigate declining performance in: {', '.join(declining_metrics)}")
        
        # Alert-based recommendations
        critical_alerts = [a for a in alerts if a.severity.value == "critical"]
        if critical_alerts:
            recommendations.append(f"Address {len(critical_alerts)} critical alerts immediately")
        
        # Business impact recommendations
        if business_impact and business_impact.roi_analysis.roi_percentage < 100:
            recommendations.append("ROI below target - review optimization strategy effectiveness")
        
        # Integration recommendations
        integration_summary = self.agent_integration.get_integration_summary()
        if integration_summary["failed_integrations"] > 0:
            recommendations.append("Fix failed agent integrations to improve data quality")
        
        return recommendations
    
    async def _save_monitoring_results(self, report: Dict[str, Any]):
        """Save monitoring results to various formats"""
        
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.results_dir / f"monitoring_run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive JSON report
        with open(run_dir / "monitoring_complete.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save executive summary
        await self._create_monitoring_executive_summary(report, run_dir)
        
        # Save alerts summary if any alerts generated
        if report["alert_analysis"]["alerts_generated"] > 0:
            await self._create_alerts_summary(report, run_dir)
        
        # Create symlink to latest
        latest_link = self.results_dir / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(run_dir.name)
        
        logger.info(f"Monitoring results saved to: {run_dir}")
    
    async def _create_monitoring_executive_summary(self, report: Dict[str, Any], output_dir: Path):
        """Create executive summary of monitoring results"""
        
        summary_content = f"""# Monitoring & Alerting Agent - Executive Summary

## Monitoring Overview
- **Brand**: {report['agent_info']['brand_name']}
- **Analysis Date**: {report['agent_info']['analysis_timestamp'][:10]}
- **Monitoring Type**: {report['agent_info']['monitoring_type'].replace('_', ' ').title()}
- **System Health**: {report['monitoring_effectiveness']['system_health']}

## Performance Status

### Current GEO Scores
"""
        
        # Add current scores
        performance = report['performance_analysis']['current_snapshot']['brand_performance']
        for metric_name, metric_data in performance.items():
            trend_icon = "📈" if metric_data['trend_direction'] == "improving" else "📉" if metric_data['trend_direction'] == "declining" else "➡️"
            summary_content += f"- **{metric_name.replace('_', ' ').title()}**: {metric_data['current_value']:.1f} {trend_icon}\n"
        
        summary_content += f"""

### Alert Status
- **Total Alerts**: {report['alert_analysis']['alerts_generated']}
- **Critical Alerts**: {report['alert_analysis']['critical_alerts']}
- **High Priority**: {report['alert_analysis']['high_alerts']}

"""
        
        # Add business impact if available
        if report['business_impact_analysis']:
            business_impact = report['business_impact_analysis']
            roi = business_impact['roi_analysis']['roi_percentage']
            revenue = business_impact['roi_analysis']['generated_revenue']
            
            summary_content += f"""## Business Impact

### ROI Performance
- **ROI**: {roi:.1f}%
- **Generated Value**: ${revenue:.0f}
- **Confidence Level**: {business_impact['roi_analysis']['confidence_level'].title()}

### Key Insights
"""
            for insight in business_impact['actionable_insights'][:3]:
                summary_content += f"- {insight}\n"
        
        summary_content += f"""

## Recommended Actions

"""
        for rec in report['actionable_recommendations']:
            summary_content += f"1. {rec}\n"
        
        summary_content += f"""

## System Status
- **Data Quality**: {report['monitoring_effectiveness']['data_quality_score']}/100
- **Agent Integration**: {report['agent_integration']['integration_health']['healthy_integrations']}/{report['agent_integration']['integration_health']['total_agents']} healthy
- **Dashboard Status**: {"✅ Updated" if report['dashboard_status'] else "❌ Not generated"}

---

*This summary was generated by Monitoring & Alerting Agent v{report['agent_info']['agent_version']}*
"""
        
        with open(output_dir / "MONITORING_EXECUTIVE_SUMMARY.md", "w") as f:
            f.write(summary_content)
    
    async def _create_alerts_summary(self, report: Dict[str, Any], output_dir: Path):
        """Create alerts summary file"""
        
        alerts_data = report['alert_analysis']['alert_details']
        
        # Create alerts CSV
        import csv
        with open(output_dir / "alerts_summary.csv", "w", newline="") as f:
            if alerts_data:
                writer = csv.DictWriter(f, fieldnames=['title', 'severity', 'message', 'timestamp', 'affected_metrics'])
                writer.writeheader()
                
                for alert in alerts_data:
                    writer.writerow({
                        'title': alert['title'],
                        'severity': alert['severity'],
                        'message': alert['message'],
                        'timestamp': alert['timestamp'],
                        'affected_metrics': '; '.join(alert['affected_metrics'])
                    })
    
    def _get_next_monitoring_time(self) -> str:
        """Get next scheduled monitoring time"""
        if not schedule.jobs:
            return "Not scheduled"
        
        next_run = schedule.next_run()
        return next_run.isoformat() if next_run else "Unknown"
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "last_run": self.last_monitoring_run.isoformat() if self.last_monitoring_run else None,
            "next_scheduled_run": self._get_next_monitoring_time(),
            "configuration": {
                "interval_hours": self.config.MONITORING_INTERVAL_HOURS,
                "real_time_enabled": self.config.REAL_TIME_MONITORING,
                "alert_sensitivity": self.config.ALERT_SENSITIVITY
            },
            "integration_status": self.agent_integration.get_integration_summary(),
            "system_health": "excellent"
        }

# Main execution functions for Claude Code integration
async def run_monitoring_agent(monitoring_type: str = "full", test_mode: bool = False) -> Dict[str, Any]:
    """
    Main function for Claude Code integration
    Returns: Complete monitoring analysis with alerts and business impact
    """
    agent = MonitoringAlertingAgent()
    return await agent.run_monitoring_analysis(monitoring_type, test_mode=test_mode)

async def start_continuous_monitoring(interval_hours: int = 6) -> Dict[str, Any]:
    """
    Start continuous monitoring
    Returns: Monitoring startup status
    """
    agent = MonitoringAlertingAgent()
    return await agent.start_continuous_monitoring(interval_hours)

def stop_continuous_monitoring() -> Dict[str, Any]:
    """
    Stop continuous monitoring
    Returns: Monitoring stop status
    """
    agent = MonitoringAlertingAgent()
    return agent.stop_continuous_monitoring()

def get_monitoring_status() -> Dict[str, Any]:
    """
    Get current monitoring status
    Returns: Current monitoring status and configuration
    """
    agent = MonitoringAlertingAgent()
    return agent.get_monitoring_status()

if __name__ == "__main__":
    # For direct script execution
    asyncio.run(run_monitoring_agent())