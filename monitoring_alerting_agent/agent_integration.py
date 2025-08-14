import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path

from .config import get_config, MonitoringAlertingConfig
from .performance_monitor import PerformanceSnapshot
from .alert_system import IntelligentAlertSystem, Alert

logger = logging.getLogger(__name__)

@dataclass
class AgentFeedback:
    """Feedback data for agent optimization"""
    agent_name: str
    timestamp: str
    feedback_type: str  # "performance_insight", "optimization_suggestion", "trend_update"
    priority: str  # "low", "medium", "high", "critical"
    data: Dict[str, Any]
    recommendations: List[str]
    expected_impact: str

@dataclass
class IntegrationStatus:
    """Status of agent integrations"""
    agent_name: str
    last_data_update: str
    data_availability: bool
    integration_health: str  # "excellent", "good", "degraded", "failed"
    next_scheduled_run: Optional[str]
    feedback_sent: bool

class AgentIntegrationHub:
    """Central hub for agent integration and feedback loops"""
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.alert_system = IntelligentAlertSystem(self.config)
        
        # Track integration status
        self.integration_status = {}
        self.feedback_history = []
        
        # Agent orchestration settings
        self.feedback_enabled = True
        self.auto_trigger_agents = False  # For safety, require manual triggers
        
        logger.info("Agent Integration Hub initialized")
    
    async def orchestrate_agent_feedback_loops(self, snapshot: PerformanceSnapshot) -> List[AgentFeedback]:
        """Main orchestration function for agent feedback loops"""
        logger.info("Orchestrating agent feedback loops")
        
        feedback_items = []
        
        # Update integration status
        await self._update_integration_status()
        
        # Generate feedback for Agent 1 (Discovery Baseline)
        agent1_feedback = await self._generate_agent1_feedback(snapshot)
        if agent1_feedback:
            feedback_items.append(agent1_feedback)
        
        # Generate feedback for Agent 2 (Content Analysis)
        agent2_feedback = await self._generate_agent2_feedback(snapshot)
        if agent2_feedback:
            feedback_items.append(agent2_feedback)
        
        # Generate feedback for Agent 3 (Competitive Intelligence)
        agent3_feedback = await self._generate_agent3_feedback(snapshot)
        if agent3_feedback:
            feedback_items.append(agent3_feedback)
        
        # Store feedback for historical tracking
        self.feedback_history.extend(feedback_items)
        
        # Save feedback to files for agent consumption
        await self._save_feedback_for_agents(feedback_items)
        
        logger.info(f"Generated {len(feedback_items)} feedback items for agents")
        
        return feedback_items
    
    async def _update_integration_status(self):
        """Update integration status for all agents"""
        
        # Agent 1 Integration Status
        agent1_data = self.config.load_agent1_results()
        self.integration_status["agent1"] = IntegrationStatus(
            agent_name="Discovery Baseline Agent",
            last_data_update=self._get_data_timestamp(agent1_data),
            data_availability=agent1_data is not None,
            integration_health=self._assess_integration_health("agent1", agent1_data),
            next_scheduled_run=self._get_next_scheduled_run("agent1"),
            feedback_sent=self._check_feedback_sent("agent1")
        )
        
        # Agent 2 Integration Status
        agent2_data = self.config.load_agent2_results()
        self.integration_status["agent2"] = IntegrationStatus(
            agent_name="Content Analysis Agent",
            last_data_update=self._get_data_timestamp(agent2_data),
            data_availability=agent2_data is not None,
            integration_health=self._assess_integration_health("agent2", agent2_data),
            next_scheduled_run=self._get_next_scheduled_run("agent2"),
            feedback_sent=self._check_feedback_sent("agent2")
        )
        
        # Agent 3 Integration Status
        agent3_data = self.config.load_agent3_results()
        self.integration_status["agent3"] = IntegrationStatus(
            agent_name="Competitive Intelligence Agent",
            last_data_update=self._get_data_timestamp(agent3_data),
            data_availability=agent3_data is not None,
            integration_health=self._assess_integration_health("agent3", agent3_data),
            next_scheduled_run=self._get_next_scheduled_run("agent3"),
            feedback_sent=self._check_feedback_sent("agent3")
        )
    
    def _get_data_timestamp(self, agent_data: Optional[Dict[str, Any]]) -> str:
        """Extract timestamp from agent data"""
        if not agent_data:
            return "No data available"
        
        # Look for various timestamp fields
        timestamp_fields = ["analysis_timestamp", "timestamp", "created_at", "last_updated"]
        
        for field in timestamp_fields:
            if field in agent_data:
                return agent_data[field]
        
        return "Unknown"
    
    def _assess_integration_health(self, agent_name: str, agent_data: Optional[Dict[str, Any]]) -> str:
        """Assess integration health status"""
        if not agent_data:
            return "failed"
        
        # Check data recency
        timestamp = self._get_data_timestamp(agent_data)
        if timestamp == "No data available" or timestamp == "Unknown":
            return "degraded"
        
        try:
            data_age = datetime.now() - datetime.fromisoformat(timestamp.replace('Z', '+00:00').replace('+00:00', ''))
            
            if data_age < timedelta(hours=24):
                return "excellent"
            elif data_age < timedelta(days=7):
                return "good"
            else:
                return "degraded"
        except ValueError:
            return "degraded"
    
    def _get_next_scheduled_run(self, agent_name: str) -> Optional[str]:
        """Get next scheduled run for agent (placeholder)"""
        # In full implementation, this would integrate with scheduling system
        return None
    
    def _check_feedback_sent(self, agent_name: str) -> bool:
        """Check if feedback has been sent to agent recently"""
        recent_feedback = [
            f for f in self.feedback_history[-10:]  # Last 10 feedback items
            if f.agent_name.lower().startswith(agent_name.replace("agent", "").strip())
        ]
        
        return len(recent_feedback) > 0
    
    async def _generate_agent1_feedback(self, snapshot: PerformanceSnapshot) -> Optional[AgentFeedback]:
        """Generate feedback for Agent 1 (Discovery Baseline)"""
        
        # Analyze discovery score trends
        discovery_metric = snapshot.brand_performance.get("discovery")
        if not discovery_metric:
            return None
        
        feedback_data = {
            "current_discovery_score": discovery_metric.current_value,
            "trend_direction": discovery_metric.trend_direction,
            "change_percentage": discovery_metric.change_percentage,
            "progress_to_target": discovery_metric.progress_to_target
        }
        
        recommendations = []
        priority = "medium"
        
        # Generate specific recommendations based on performance
        if discovery_metric.trend_direction == "declining":
            recommendations.extend([
                "Re-run baseline analysis to identify new competitor threats",
                "Expand query matrix to capture emerging search patterns",
                "Focus on queries where discovery score is dropping most"
            ])
            priority = "high"
            
        elif discovery_metric.trend_direction == "improving":
            recommendations.extend([
                "Document successful query optimization patterns",
                "Expand successful strategies to underperforming queries",
                "Consider increasing query matrix size to capture more opportunities"
            ])
            priority = "medium"
        
        # Query performance insights
        high_performing_queries = [
            q for q in snapshot.query_performance 
            if q.citation_frequency > 0.6
        ]
        
        low_performing_queries = [
            q for q in snapshot.query_performance 
            if q.citation_frequency < 0.2
        ]
        
        feedback_data.update({
            "high_performing_queries": [q.query for q in high_performing_queries],
            "low_performing_queries": [q.query for q in low_performing_queries],
            "query_optimization_opportunities": len(low_performing_queries)
        })
        
        if low_performing_queries:
            recommendations.append(f"Prioritize optimization for {len(low_performing_queries)} underperforming queries")
        
        return AgentFeedback(
            agent_name="Discovery Baseline Agent",
            timestamp=datetime.now().isoformat(),
            feedback_type="performance_insight",
            priority=priority,
            data=feedback_data,
            recommendations=recommendations,
            expected_impact="10-20% improvement in discovery scores through targeted query optimization"
        )
    
    async def _generate_agent2_feedback(self, snapshot: PerformanceSnapshot) -> Optional[AgentFeedback]:
        """Generate feedback for Agent 2 (Content Analysis)"""
        
        # Analyze context score trends
        context_metric = snapshot.brand_performance.get("context")
        if not context_metric:
            return None
        
        feedback_data = {
            "current_context_score": context_metric.current_value,
            "trend_direction": context_metric.trend_direction,
            "change_percentage": context_metric.change_percentage,
            "progress_to_target": context_metric.progress_to_target
        }
        
        recommendations = []
        priority = "medium"
        
        # Load Agent 2 results for specific feedback
        agent2_results = self.config.load_agent2_results()
        
        if agent2_results:
            # Analyze content gap closure progress
            content_gaps = agent2_results.get("content_gaps", [])
            optimization_opportunities = agent2_results.get("optimization_opportunities", [])
            
            feedback_data.update({
                "content_gaps_remaining": len(content_gaps),
                "optimization_opportunities": len(optimization_opportunities),
                "gap_closure_priority": "high" if len(content_gaps) > 5 else "medium"
            })
        
        # Performance-based recommendations
        if context_metric.trend_direction == "declining":
            recommendations.extend([
                "Re-analyze content quality scores for recent changes",
                "Prioritize high-impact content optimizations",
                "Review competitor content strategies that may be affecting performance"
            ])
            priority = "high"
            
        elif context_metric.current_value < context_metric.target_value:
            recommendations.extend([
                "Accelerate content gap closure initiatives", 
                "Focus on AI consumption optimization techniques",
                "Implement structured data markup for better context understanding"
            ])
        
        # Query-specific content insights
        content_opportunities = []
        for query in snapshot.query_performance:
            if query.response_quality < 75:  # Below quality threshold
                content_opportunities.append({
                    "query": query.query,
                    "current_quality": query.response_quality,
                    "improvement_potential": 100 - query.response_quality
                })
        
        if content_opportunities:
            feedback_data["content_optimization_opportunities"] = content_opportunities[:5]
            recommendations.append(f"Optimize content for {len(content_opportunities)} queries with quality scores below 75")
        
        return AgentFeedback(
            agent_name="Content Analysis Agent",
            timestamp=datetime.now().isoformat(),
            feedback_type="optimization_suggestion",
            priority=priority,
            data=feedback_data,
            recommendations=recommendations,
            expected_impact="15-25% improvement in context scores through targeted content optimization"
        )
    
    async def _generate_agent3_feedback(self, snapshot: PerformanceSnapshot) -> Optional[AgentFeedback]:
        """Generate feedback for Agent 3 (Competitive Intelligence)"""
        
        # Analyze competitive score trends
        competitive_metric = snapshot.brand_performance.get("competitive")
        if not competitive_metric:
            return None
        
        feedback_data = {
            "current_competitive_score": competitive_metric.current_value,
            "trend_direction": competitive_metric.trend_direction,
            "change_percentage": competitive_metric.change_percentage,
            "progress_to_target": competitive_metric.progress_to_target
        }
        
        recommendations = []
        priority = "medium"
        
        # Competitive landscape analysis
        high_threat_competitors = [
            comp for comp in snapshot.competitor_performance 
            if comp.threat_level in ["high", "critical"]
        ]
        
        emerging_opportunities = [
            comp for comp in snapshot.competitor_performance
            if comp.overall_score < competitive_metric.current_value
        ]
        
        feedback_data.update({
            "high_threat_competitors": len(high_threat_competitors),
            "immediate_threats": [comp.competitor for comp in high_threat_competitors],
            "competitive_opportunities": len(emerging_opportunities),
            "market_position_trend": competitive_metric.trend_direction
        })
        
        # Threat-based recommendations
        if high_threat_competitors:
            recommendations.extend([
                f"Develop response strategy for {len(high_threat_competitors)} high-threat competitors",
                "Accelerate authority building initiatives to counter competitive pressure",
                "Monitor competitor content strategies for defensive opportunities"
            ])
            priority = "high"
        
        # Opportunity-based recommendations
        if emerging_opportunities:
            recommendations.extend([
                "Capitalize on competitive weaknesses in authority signals",
                "Expand content into areas where competitors are underperforming",
                "Implement aggressive optimization in competitor weak spots"
            ])
        
        # Load Agent 3 results for strategic insights
        agent3_results = self.config.load_agent3_results()
        if agent3_results:
            market_gaps = agent3_results.get("key_findings", {}).get("market_gap_opportunities", 0)
            
            feedback_data["market_gap_opportunities"] = market_gaps
            
            if market_gaps > 10:
                recommendations.append("Prioritize capture of identified market gap opportunities")
        
        return AgentFeedback(
            agent_name="Competitive Intelligence Agent",
            timestamp=datetime.now().isoformat(),
            feedback_type="trend_update",
            priority=priority,
            data=feedback_data,
            recommendations=recommendations,
            expected_impact="20-30% improvement in competitive positioning through strategic response"
        )
    
    async def _save_feedback_for_agents(self, feedback_items: List[AgentFeedback]):
        """Save feedback items to files for agent consumption"""
        feedback_dir = Path(self.config.OUTPUT_DIR) / "agent_feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        for feedback in feedback_items:
            # Create agent-specific feedback file
            agent_name_clean = feedback.agent_name.lower().replace(" ", "_")
            filename = f"{agent_name_clean}_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = feedback_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(asdict(feedback), f, indent=2, default=str)
            
            # Create/update latest feedback file
            latest_filepath = feedback_dir / f"{agent_name_clean}_latest_feedback.json"
            with open(latest_filepath, 'w') as f:
                json.dump(asdict(feedback), f, indent=2, default=str)
        
        logger.info(f"Saved feedback for {len(feedback_items)} agents")
    
    async def trigger_agent_rerun(self, agent_name: str, priority: str = "normal") -> Dict[str, Any]:
        """Trigger agent re-run based on feedback (placeholder for future implementation)"""
        logger.info(f"Trigger requested for {agent_name} with priority {priority}")
        
        # In full implementation, this would:
        # 1. Check if agent re-run is warranted
        # 2. Queue agent execution with appropriate parameters
        # 3. Update scheduling system
        # 4. Return execution status
        
        return {
            "agent": agent_name,
            "priority": priority,
            "status": "queued",
            "estimated_completion": "Not implemented",
            "feedback_driven": True
        }
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get integration status summary"""
        return {
            "total_agents": len(self.integration_status),
            "healthy_integrations": len([
                status for status in self.integration_status.values() 
                if status.integration_health in ["excellent", "good"]
            ]),
            "degraded_integrations": len([
                status for status in self.integration_status.values()
                if status.integration_health == "degraded"
            ]),
            "failed_integrations": len([
                status for status in self.integration_status.values()
                if status.integration_health == "failed"
            ]),
            "feedback_items_generated": len(self.feedback_history),
            "last_feedback_timestamp": self.feedback_history[-1].timestamp if self.feedback_history else None,
            "integration_details": {
                name: asdict(status) for name, status in self.integration_status.items()
            }
        }
    
    def get_feedback_history(self, agent_name: Optional[str] = None, hours: int = 24) -> List[AgentFeedback]:
        """Get feedback history for specific agent or all agents"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_feedback = []
        for feedback in self.feedback_history:
            try:
                feedback_time = datetime.fromisoformat(feedback.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                if feedback_time > cutoff_time:
                    if agent_name is None or agent_name.lower() in feedback.agent_name.lower():
                        filtered_feedback.append(feedback)
            except ValueError:
                continue
        
        return sorted(filtered_feedback, key=lambda f: f.timestamp, reverse=True)
    
    async def validate_agent_feedback_loops(self) -> Dict[str, Any]:
        """Validate that feedback loops are working correctly"""
        validation_results = {
            "feedback_loop_health": "excellent",
            "issues_found": [],
            "recommendations": [],
            "last_validation": datetime.now().isoformat()
        }
        
        # Check data freshness
        for agent_name, status in self.integration_status.items():
            if status.integration_health in ["degraded", "failed"]:
                validation_results["issues_found"].append(
                    f"{status.agent_name} integration is {status.integration_health}"
                )
                validation_results["recommendations"].append(
                    f"Check {status.agent_name} data pipeline and scheduling"
                )
        
        # Check feedback generation
        recent_feedback = self.get_feedback_history(hours=48)
        if len(recent_feedback) == 0:
            validation_results["issues_found"].append("No feedback generated in last 48 hours")
            validation_results["recommendations"].append("Check feedback generation logic and agent performance data")
        
        # Determine overall health
        if validation_results["issues_found"]:
            if len(validation_results["issues_found"]) >= 3:
                validation_results["feedback_loop_health"] = "poor"
            elif len(validation_results["issues_found"]) >= 2:
                validation_results["feedback_loop_health"] = "degraded"
            else:
                validation_results["feedback_loop_health"] = "good"
        
        return validation_results