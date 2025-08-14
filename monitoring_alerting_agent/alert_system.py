import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import get_config, MonitoringAlertingConfig, NotificationChannels
from .performance_monitor import PerformanceSnapshot, PerformanceMetric

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    PERFORMANCE_DECLINE = "performance_decline"
    MILESTONE_ACHIEVEMENT = "milestone_achievement"
    COMPETITIVE_THREAT = "competitive_threat"
    MARKET_OPPORTUNITY = "market_opportunity"
    CONTENT_OPPORTUNITY = "content_opportunity"
    SYSTEM_HEALTH = "system_health"
    ROI_TRACKING = "roi_tracking"

@dataclass
class Alert:
    """Individual alert data structure"""
    id: str
    timestamp: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    details: Dict[str, Any]
    affected_metrics: List[str]
    recommended_actions: List[str]
    stakeholders: List[str]
    auto_resolve: bool
    resolution_deadline: Optional[str]
    related_alerts: List[str]

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Description of the condition
    threshold_function: Callable
    message_template: str
    stakeholders: List[str]
    auto_resolve: bool
    cooldown_minutes: int

class IntelligentAlertSystem:
    """Intelligent alerting system with configurable rules and channels"""
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.notification_channels = self.config.get_notification_channels()
        
        # Alert state tracking
        self.active_alerts = {}
        self.alert_history = []
        self.alert_cooldowns = {}
        
        # Initialize alert rules
        self.alert_rules = self._initialize_alert_rules()
        
        logger.info("Intelligent Alert System initialized")
    
    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Initialize predefined alert rules"""
        rules = []
        
        # Performance improvement alerts
        rules.append(AlertRule(
            name="significant_discovery_improvement",
            alert_type=AlertType.PERFORMANCE_IMPROVEMENT,
            severity=AlertSeverity.MEDIUM,
            condition="Discovery score improves by 10+ points",
            threshold_function=lambda metrics: self._check_score_improvement(metrics, "discovery", 10),
            message_template="🎉 Discovery Score improved by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "client"],
            auto_resolve=True,
            cooldown_minutes=60
        ))
        
        rules.append(AlertRule(
            name="significant_context_improvement",
            alert_type=AlertType.PERFORMANCE_IMPROVEMENT,
            severity=AlertSeverity.MEDIUM,
            condition="Context score improves by 15+ points",
            threshold_function=lambda metrics: self._check_score_improvement(metrics, "context", 15),
            message_template="🎉 Context Score improved by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "client"],
            auto_resolve=True,
            cooldown_minutes=60
        ))
        
        rules.append(AlertRule(
            name="significant_competitive_improvement",
            alert_type=AlertType.PERFORMANCE_IMPROVEMENT,
            severity=AlertSeverity.MEDIUM,
            condition="Competitive score improves by 12+ points",
            threshold_function=lambda metrics: self._check_score_improvement(metrics, "competitive", 12),
            message_template="🎉 Competitive Score improved by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "client"],
            auto_resolve=True,
            cooldown_minutes=60
        ))
        
        # Performance decline alerts
        rules.append(AlertRule(
            name="critical_discovery_decline",
            alert_type=AlertType.PERFORMANCE_DECLINE,
            severity=AlertSeverity.CRITICAL,
            condition="Discovery score declines by 20+ points",
            threshold_function=lambda metrics: self._check_score_decline(metrics, "discovery", 20),
            message_template="🚨 CRITICAL: Discovery Score declined by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "urgent"],
            auto_resolve=False,
            cooldown_minutes=30
        ))
        
        rules.append(AlertRule(
            name="significant_context_decline",
            alert_type=AlertType.PERFORMANCE_DECLINE,
            severity=AlertSeverity.HIGH,
            condition="Context score declines by 25+ points",
            threshold_function=lambda metrics: self._check_score_decline(metrics, "context", 25),
            message_template="⚠️ HIGH: Context Score declined by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "urgent"],
            auto_resolve=False,
            cooldown_minutes=30
        ))
        
        rules.append(AlertRule(
            name="significant_competitive_decline",
            alert_type=AlertType.PERFORMANCE_DECLINE,
            severity=AlertSeverity.HIGH,
            condition="Competitive score declines by 20+ points",
            threshold_function=lambda metrics: self._check_score_decline(metrics, "competitive", 20),
            message_template="⚠️ HIGH: Competitive Score declined by {change:.1f} points to {current:.1f}",
            stakeholders=["team", "urgent"],
            auto_resolve=False,
            cooldown_minutes=30
        ))
        
        # Milestone achievement alerts
        rules.append(AlertRule(
            name="milestone_achievement",
            alert_type=AlertType.MILESTONE_ACHIEVEMENT,
            severity=AlertSeverity.MEDIUM,
            condition="Any score crosses milestone threshold",
            threshold_function=lambda metrics: self._check_milestone_achievement(metrics),
            message_template="🎯 Milestone Achievement: {milestone_details}",
            stakeholders=["client", "team"],
            auto_resolve=True,
            cooldown_minutes=1440  # 24 hours
        ))
        
        # Competitive threat alerts
        rules.append(AlertRule(
            name="competitor_surge",
            alert_type=AlertType.COMPETITIVE_THREAT,
            severity=AlertSeverity.HIGH,
            condition="Competitor gains significant market share",
            threshold_function=lambda metrics: self._check_competitor_surge(metrics),
            message_template="🔴 Competitive Threat: {competitor} showing surge in performance",
            stakeholders=["strategy_team"],
            auto_resolve=False,
            cooldown_minutes=120
        ))
        
        # Market opportunity alerts
        rules.append(AlertRule(
            name="market_opportunity",
            alert_type=AlertType.MARKET_OPPORTUNITY,
            severity=AlertSeverity.MEDIUM,
            condition="New market opportunity detected",
            threshold_function=lambda metrics: self._check_market_opportunity(metrics),
            message_template="💡 Market Opportunity: {opportunity_details}",
            stakeholders=["content_team"],
            auto_resolve=False,
            cooldown_minutes=240
        ))
        
        # Content opportunity alerts
        rules.append(AlertRule(
            name="trending_query_opportunity",
            alert_type=AlertType.CONTENT_OPPORTUNITY,
            severity=AlertSeverity.MEDIUM,
            condition="Query shows significant growth",
            threshold_function=lambda metrics: self._check_trending_query(metrics),
            message_template="📈 Content Opportunity: {query} showing {growth}% growth",
            stakeholders=["content_team"],
            auto_resolve=False,
            cooldown_minutes=360
        ))
        
        # ROI tracking alerts
        rules.append(AlertRule(
            name="roi_milestone",
            alert_type=AlertType.ROI_TRACKING,
            severity=AlertSeverity.MEDIUM,
            condition="ROI reaches significant milestone",
            threshold_function=lambda metrics: self._check_roi_milestone(metrics),
            message_template="💰 ROI Milestone: {roi_details}",
            stakeholders=["client", "team"],
            auto_resolve=True,
            cooldown_minutes=720
        ))
        
        return rules
    
    async def process_performance_snapshot(self, snapshot: PerformanceSnapshot) -> List[Alert]:
        """Process performance snapshot and generate alerts"""
        logger.info("Processing performance snapshot for alerts")
        
        generated_alerts = []
        
        # Process each alert rule
        for rule in self.alert_rules:
            # Check cooldown
            if self._is_in_cooldown(rule.name):
                continue
            
            # Evaluate rule condition
            try:
                rule_triggered = rule.threshold_function(snapshot)
                
                if rule_triggered:
                    alert = await self._create_alert(rule, snapshot, rule_triggered)
                    generated_alerts.append(alert)
                    
                    # Set cooldown
                    self._set_cooldown(rule.name, rule.cooldown_minutes)
                    
                    # Send notifications
                    await self._send_alert_notifications(alert)
                    
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.name}: {str(e)}")
        
        # Update alert tracking
        for alert in generated_alerts:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
        
        logger.info(f"Generated {len(generated_alerts)} alerts")
        
        return generated_alerts
    
    def _check_score_improvement(self, snapshot: PerformanceSnapshot, metric_type: str, threshold: float) -> Optional[Dict[str, Any]]:
        """Check for score improvement above threshold"""
        if metric_type not in snapshot.brand_performance:
            return None
        
        metric = snapshot.brand_performance[metric_type]
        
        if metric.change_amount >= threshold:
            return {
                "metric_type": metric_type,
                "current": metric.current_value,
                "change": metric.change_amount,
                "percentage": metric.change_percentage
            }
        
        return None
    
    def _check_score_decline(self, snapshot: PerformanceSnapshot, metric_type: str, threshold: float) -> Optional[Dict[str, Any]]:
        """Check for score decline below threshold"""
        if metric_type not in snapshot.brand_performance:
            return None
        
        metric = snapshot.brand_performance[metric_type]
        
        if metric.change_amount <= -threshold:
            return {
                "metric_type": metric_type,
                "current": metric.current_value,
                "change": metric.change_amount,
                "percentage": metric.change_percentage
            }
        
        return None
    
    def _check_milestone_achievement(self, snapshot: PerformanceSnapshot) -> Optional[Dict[str, Any]]:
        """Check for milestone achievements"""
        if snapshot.milestone_achievements:
            return {
                "milestones": snapshot.milestone_achievements,
                "milestone_details": "; ".join(snapshot.milestone_achievements)
            }
        
        return None
    
    def _check_competitor_surge(self, snapshot: PerformanceSnapshot) -> Optional[Dict[str, Any]]:
        """Check for competitor performance surges"""
        high_threat_competitors = [
            comp for comp in snapshot.competitor_performance 
            if comp.threat_level in ["high", "critical"]
        ]
        
        if high_threat_competitors:
            return {
                "competitor": high_threat_competitors[0].competitor,
                "threat_level": high_threat_competitors[0].threat_level,
                "score": high_threat_competitors[0].overall_score
            }
        
        return None
    
    def _check_market_opportunity(self, snapshot: PerformanceSnapshot) -> Optional[Dict[str, Any]]:
        """Check for market opportunities"""
        # Check for queries with low competition (high opportunity)
        low_competition_queries = [
            query for query in snapshot.query_performance
            if query.market_share < 15 and query.response_quality > 80
        ]
        
        if low_competition_queries:
            return {
                "opportunity_count": len(low_competition_queries),
                "opportunity_details": f"{len(low_competition_queries)} high-potential, low-competition queries identified"
            }
        
        return None
    
    def _check_trending_query(self, snapshot: PerformanceSnapshot) -> Optional[Dict[str, Any]]:
        """Check for trending query opportunities"""
        high_growth_queries = [
            query for query in snapshot.query_performance
            if query.change_from_baseline > 30
        ]
        
        if high_growth_queries:
            top_query = max(high_growth_queries, key=lambda q: q.change_from_baseline)
            return {
                "query": top_query.query,
                "growth": top_query.change_from_baseline
            }
        
        return None
    
    def _check_roi_milestone(self, snapshot: PerformanceSnapshot) -> Optional[Dict[str, Any]]:
        """Check for ROI milestones"""
        if "estimated_conversion_value" in snapshot.business_impact_metrics:
            conversion_value = snapshot.business_impact_metrics["estimated_conversion_value"]
            
            # Check if ROI crosses significant thresholds
            roi_thresholds = [1000, 5000, 10000, 25000]
            
            for threshold in roi_thresholds:
                if conversion_value >= threshold:
                    return {
                        "roi_details": f"Estimated monthly conversion value reached ${conversion_value:.0f}",
                        "milestone": threshold
                    }
        
        return None
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if alert rule is in cooldown period"""
        if rule_name not in self.alert_cooldowns:
            return False
        
        cooldown_until = self.alert_cooldowns[rule_name]
        return datetime.now() < cooldown_until
    
    def _set_cooldown(self, rule_name: str, minutes: int):
        """Set cooldown period for alert rule"""
        self.alert_cooldowns[rule_name] = datetime.now() + timedelta(minutes=minutes)
    
    async def _create_alert(self, rule: AlertRule, snapshot: PerformanceSnapshot, trigger_data: Dict[str, Any]) -> Alert:
        """Create alert from rule and trigger data"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Format message with trigger data
        try:
            formatted_message = rule.message_template.format(**trigger_data)
        except KeyError:
            formatted_message = rule.message_template
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(rule.alert_type, trigger_data)
        
        # Determine affected metrics
        affected_metrics = self._determine_affected_metrics(rule.alert_type, trigger_data)
        
        # Set resolution deadline for non-auto-resolve alerts
        resolution_deadline = None
        if not rule.auto_resolve:
            if rule.severity == AlertSeverity.CRITICAL:
                resolution_deadline = (datetime.now() + timedelta(hours=4)).isoformat()
            elif rule.severity == AlertSeverity.HIGH:
                resolution_deadline = (datetime.now() + timedelta(hours=24)).isoformat()
            else:
                resolution_deadline = (datetime.now() + timedelta(days=7)).isoformat()
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now().isoformat(),
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=rule.name.replace("_", " ").title(),
            message=formatted_message,
            details=trigger_data,
            affected_metrics=affected_metrics,
            recommended_actions=recommended_actions,
            stakeholders=rule.stakeholders,
            auto_resolve=rule.auto_resolve,
            resolution_deadline=resolution_deadline,
            related_alerts=[]
        )
        
        return alert
    
    def _generate_recommended_actions(self, alert_type: AlertType, trigger_data: Dict[str, Any]) -> List[str]:
        """Generate recommended actions based on alert type"""
        actions = []
        
        if alert_type == AlertType.PERFORMANCE_DECLINE:
            actions.extend([
                "Investigate recent content changes or technical issues",
                "Review competitor activity for potential causes",
                "Run diagnostic analysis on affected metrics",
                "Consider emergency optimization measures"
            ])
        
        elif alert_type == AlertType.COMPETITIVE_THREAT:
            actions.extend([
                "Analyze competitor's recent strategy changes",
                "Review and update competitive positioning",
                "Accelerate high-priority optimization initiatives",
                "Monitor competitor response to our actions"
            ])
        
        elif alert_type == AlertType.MARKET_OPPORTUNITY:
            actions.extend([
                "Prioritize content creation for identified opportunities",
                "Allocate resources to capture market gaps",
                "Monitor opportunity window timing",
                "Prepare rapid response content strategy"
            ])
        
        elif alert_type == AlertType.CONTENT_OPPORTUNITY:
            actions.extend([
                "Create content targeting trending queries",
                "Optimize existing content for new keywords",
                "Monitor query trend sustainability",
                "Prepare content calendar for trend capture"
            ])
        
        elif alert_type == AlertType.PERFORMANCE_IMPROVEMENT:
            actions.extend([
                "Document successful optimization tactics",
                "Scale successful strategies to other areas",
                "Maintain momentum with continued optimization",
                "Share success insights with stakeholders"
            ])
        
        elif alert_type == AlertType.MILESTONE_ACHIEVEMENT:
            actions.extend([
                "Celebrate achievement with team and client",
                "Document milestone factors for replication",
                "Set next milestone targets",
                "Update strategic roadmap based on progress"
            ])
        
        return actions
    
    def _determine_affected_metrics(self, alert_type: AlertType, trigger_data: Dict[str, Any]) -> List[str]:
        """Determine which metrics are affected by the alert"""
        affected = []
        
        if "metric_type" in trigger_data:
            affected.append(trigger_data["metric_type"])
        
        if alert_type == AlertType.COMPETITIVE_THREAT:
            affected.extend(["competitive_score", "market_share"])
        
        elif alert_type == AlertType.CONTENT_OPPORTUNITY:
            affected.extend(["discovery_score", "context_score"])
        
        elif alert_type == AlertType.ROI_TRACKING:
            affected.extend(["business_impact", "conversion_value"])
        
        return affected
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        try:
            # Send Slack notification
            if self.notification_channels.slack_webhook:
                await self._send_slack_notification(alert)
            
            # Send email notifications
            if self.notification_channels.email_alerts:
                await self._send_email_notification(alert)
            
            # Send SMS for critical alerts
            if (alert.severity == AlertSeverity.CRITICAL and 
                self.notification_channels.sms_alerts):
                await self._send_sms_notification(alert)
            
            logger.info(f"Sent notifications for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending notifications for alert {alert.id}: {str(e)}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        if not self.notification_channels.slack_webhook:
            return
        
        # Choose color based on severity
        color_map = {
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.MEDIUM: "#ffeb3b", 
            AlertSeverity.HIGH: "#ff9800",
            AlertSeverity.CRITICAL: "#f44336"
        }
        
        slack_payload = {
            "attachments": [
                {
                    "color": color_map.get(alert.severity, "#36a64f"),
                    "title": f"{alert.severity.value.upper()}: {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Affected Metrics",
                            "value": ", ".join(alert.affected_metrics) if alert.affected_metrics else "None",
                            "short": True
                        },
                        {
                            "title": "Alert Type",
                            "value": alert.alert_type.value.replace("_", " ").title(),
                            "short": True
                        }
                    ],
                    "footer": "GEO Monitoring System",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(
                self.notification_channels.slack_webhook,
                json=slack_payload,
                timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        if not self.notification_channels.email_alerts:
            return
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = "geo-monitoring@brushonblock.com"
            msg['Subject'] = f"GEO Alert: {alert.title}"
            
            # Create email body
            body = f"""
GEO Monitoring Alert

Alert: {alert.title}
Severity: {alert.severity.value.upper()}
Time: {alert.timestamp}

Message: {alert.message}

Affected Metrics: {', '.join(alert.affected_metrics) if alert.affected_metrics else 'None'}

Recommended Actions:
{chr(10).join(f"• {action}" for action in alert.recommended_actions)}

Details: {json.dumps(alert.details, indent=2)}

This is an automated alert from the GEO Monitoring & Alerting Agent.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Note: In production, you would configure SMTP settings
            # For now, just log that email would be sent
            logger.info(f"Email notification prepared for {len(self.notification_channels.email_alerts)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    async def _send_sms_notification(self, alert: Alert):
        """Send SMS notification for critical alerts"""
        if not self.notification_channels.sms_alerts:
            return
        
        # SMS message (keep it short)
        sms_message = f"GEO CRITICAL ALERT: {alert.title}. {alert.message[:100]}..."
        
        # Note: In production, you would integrate with SMS service
        # For now, just log that SMS would be sent
        logger.info(f"SMS notification prepared: {sms_message}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get currently active alerts"""
        active = [alert for alert in self.active_alerts.values() if not alert.auto_resolve]
        
        if severity:
            active = [alert for alert in active if alert.severity == severity]
        
        return sorted(active, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00').replace('+00:00', '')) > cutoff_time
        ]
    
    def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """Manually resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.details["resolved"] = True
            alert.details["resolution_note"] = resolution_note
            alert.details["resolved_at"] = datetime.now().isoformat()
            
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert {alert_id} resolved: {resolution_note}")
            return True
        
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alert status"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            "high_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
            "medium_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
            "low_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.LOW]),
            "alerts_last_24h": len(self.get_alert_history(24)),
            "most_recent_alert": active_alerts[0].timestamp if active_alerts else None,
            "alert_types_active": list(set([a.alert_type.value for a in active_alerts]))
        }
        
        return summary