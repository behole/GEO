import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict
import sqlite3
from pathlib import Path

from .config import get_config, MonitoringAlertingConfig, PerformanceTargets

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    timestamp: str
    metric_type: str  # "discovery", "context", "competitive", "overall"
    metric_name: str
    current_value: float
    previous_value: Optional[float]
    change_amount: float
    change_percentage: float
    trend_direction: str  # "improving", "declining", "stable"
    baseline_value: Optional[float]
    target_value: Optional[float]
    progress_to_target: Optional[float]

@dataclass
class QueryPerformanceData:
    """Query-specific performance tracking"""
    query: str
    timestamp: str
    current_ranking: Optional[int]
    citation_frequency: float
    response_quality: float
    competitor_rankings: Dict[str, int]
    market_share: float
    change_from_baseline: float

@dataclass
class CompetitorPerformanceData:
    """Competitor performance tracking"""
    competitor: str
    timestamp: str
    overall_score: float
    market_share: float
    citation_frequency: float
    ranking_changes: Dict[str, int]  # query -> ranking change
    content_strategy_score: float
    authority_signal_score: float
    threat_level: str  # "low", "medium", "high", "critical"

@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot at a point in time"""
    timestamp: str
    brand_performance: Dict[str, PerformanceMetric]
    query_performance: List[QueryPerformanceData]
    competitor_performance: List[CompetitorPerformanceData]
    milestone_achievements: List[str]
    performance_alerts: List[str]
    business_impact_metrics: Dict[str, float]

class PerformanceMonitor:
    """Continuous performance monitoring system"""
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.performance_targets = self.config.get_performance_targets()
        
        # Initialize database for historical tracking
        self.db_path = Path(self.config.OUTPUT_DIR) / "monitoring_data.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Load baseline metrics
        self.baseline_metrics = self.config.get_baseline_metrics()
        
        # Track current state
        self.current_performance = {}
        self.last_update = None
        
        logger.info("Performance Monitor initialized")
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                current_value REAL NOT NULL,
                previous_value REAL,
                change_amount REAL,
                change_percentage REAL,
                trend_direction TEXT,
                baseline_value REAL,
                target_value REAL,
                progress_to_target REAL
            )
        ''')
        
        # Query performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                current_ranking INTEGER,
                citation_frequency REAL,
                response_quality REAL,
                competitor_rankings TEXT,
                market_share REAL,
                change_from_baseline REAL
            )
        ''')
        
        # Competitor performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                competitor TEXT NOT NULL,
                overall_score REAL,
                market_share REAL,
                citation_frequency REAL,
                ranking_changes TEXT,
                content_strategy_score REAL,
                authority_signal_score REAL,
                threat_level TEXT
            )
        ''')
        
        # Performance snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                snapshot_data TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def monitor_performance_continuous(self) -> PerformanceSnapshot:
        """Main continuous performance monitoring function"""
        logger.info("Starting continuous performance monitoring")
        
        # Collect current performance data
        brand_performance = await self._collect_brand_performance()
        query_performance = await self._collect_query_performance()
        competitor_performance = await self._collect_competitor_performance()
        
        # Check for milestone achievements
        milestone_achievements = self._check_milestone_achievements(brand_performance)
        
        # Generate performance alerts
        performance_alerts = self._generate_performance_alerts(
            brand_performance, query_performance, competitor_performance)
        
        # Calculate business impact metrics
        business_impact = await self._calculate_business_impact_metrics(
            brand_performance, query_performance)
        
        # Create performance snapshot
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now().isoformat(),
            brand_performance=brand_performance,
            query_performance=query_performance,
            competitor_performance=competitor_performance,
            milestone_achievements=milestone_achievements,
            performance_alerts=performance_alerts,
            business_impact_metrics=business_impact
        )
        
        # Store snapshot in database
        await self._store_performance_snapshot(snapshot)
        
        # Update current state
        self.current_performance = brand_performance
        self.last_update = datetime.now()
        
        logger.info(f"Performance monitoring complete: {len(performance_alerts)} alerts generated")
        
        return snapshot
    
    async def _collect_brand_performance(self) -> Dict[str, PerformanceMetric]:
        """Collect brand performance metrics"""
        brand_performance = {}
        timestamp = datetime.now().isoformat()
        
        # Get historical data for comparison
        historical_data = self._get_historical_brand_performance(days_back=7)
        
        # Discovery Score Monitoring
        discovery_current = await self._get_current_discovery_score()
        discovery_previous = historical_data.get("discovery", {}).get("current_value")
        discovery_baseline = self.baseline_metrics.get("initial_scores", {}).get("discovery", 12.9)
        
        brand_performance["discovery"] = PerformanceMetric(
            timestamp=timestamp,
            metric_type="discovery",
            metric_name="Discovery Score",
            current_value=discovery_current,
            previous_value=discovery_previous,
            change_amount=discovery_current - (discovery_previous or discovery_current),
            change_percentage=((discovery_current - (discovery_previous or discovery_current)) / 
                             max(discovery_previous or 1, 1)) * 100,
            trend_direction=self._determine_trend_direction(discovery_current, discovery_previous),
            baseline_value=discovery_baseline,
            target_value=self.performance_targets.discovery_score_target,
            progress_to_target=((discovery_current - discovery_baseline) / 
                              (self.performance_targets.discovery_score_target - discovery_baseline)) * 100
        )
        
        # Context Score Monitoring
        context_current = await self._get_current_context_score()
        context_previous = historical_data.get("context", {}).get("current_value")
        context_baseline = self.baseline_metrics.get("initial_scores", {}).get("context", 57.5)
        
        brand_performance["context"] = PerformanceMetric(
            timestamp=timestamp,
            metric_type="context",
            metric_name="Context Score",
            current_value=context_current,
            previous_value=context_previous,
            change_amount=context_current - (context_previous or context_current),
            change_percentage=((context_current - (context_previous or context_current)) / 
                             max(context_previous or 1, 1)) * 100,
            trend_direction=self._determine_trend_direction(context_current, context_previous),
            baseline_value=context_baseline,
            target_value=self.performance_targets.context_score_target,
            progress_to_target=((context_current - context_baseline) / 
                              (self.performance_targets.context_score_target - context_baseline)) * 100
        )
        
        # Competitive Score Monitoring
        competitive_current = await self._get_current_competitive_score()
        competitive_previous = historical_data.get("competitive", {}).get("current_value")
        competitive_baseline = self.baseline_metrics.get("initial_scores", {}).get("competitive", 19.4)
        
        brand_performance["competitive"] = PerformanceMetric(
            timestamp=timestamp,
            metric_type="competitive",
            metric_name="Competitive Score",
            current_value=competitive_current,
            previous_value=competitive_previous,
            change_amount=competitive_current - (competitive_previous or competitive_current),
            change_percentage=((competitive_current - (competitive_previous or competitive_current)) / 
                             max(competitive_previous or 1, 1)) * 100,
            trend_direction=self._determine_trend_direction(competitive_current, competitive_previous),
            baseline_value=competitive_baseline,
            target_value=self.performance_targets.competitive_score_target,
            progress_to_target=((competitive_current - competitive_baseline) / 
                              (self.performance_targets.competitive_score_target - competitive_baseline)) * 100
        )
        
        # Overall Score Calculation
        overall_current = (discovery_current + context_current + competitive_current) / 3
        overall_previous = None
        if all([discovery_previous, context_previous, competitive_previous]):
            overall_previous = (discovery_previous + context_previous + competitive_previous) / 3
        
        overall_baseline = (discovery_baseline + context_baseline + competitive_baseline) / 3
        overall_target = (self.performance_targets.discovery_score_target + 
                         self.performance_targets.context_score_target + 
                         self.performance_targets.competitive_score_target) / 3
        
        brand_performance["overall"] = PerformanceMetric(
            timestamp=timestamp,
            metric_type="overall",
            metric_name="Overall GEO Score",
            current_value=overall_current,
            previous_value=overall_previous,
            change_amount=overall_current - (overall_previous or overall_current),
            change_percentage=((overall_current - (overall_previous or overall_current)) / 
                             max(overall_previous or 1, 1)) * 100,
            trend_direction=self._determine_trend_direction(overall_current, overall_previous),
            baseline_value=overall_baseline,
            target_value=overall_target,
            progress_to_target=((overall_current - overall_baseline) / 
                              (overall_target - overall_baseline)) * 100
        )
        
        return brand_performance
    
    async def _get_current_discovery_score(self) -> float:
        """Get current discovery score (would integrate with Agent 1 re-analysis)"""
        # In a full implementation, this would re-run Agent 1 analysis
        # For now, simulate progressive improvement
        baseline = self.baseline_metrics.get("initial_scores", {}).get("discovery", 12.9)
        
        # Simulate gradual improvement based on monitoring period
        days_since_baseline = 7  # Simulated
        improvement_rate = 0.5   # Points per day improvement
        simulated_current = baseline + (days_since_baseline * improvement_rate)
        
        return min(simulated_current, 100.0)  # Cap at 100
    
    async def _get_current_context_score(self) -> float:
        """Get current context score (would integrate with Agent 2 re-analysis)"""
        # In a full implementation, this would re-run Agent 2 analysis
        baseline = self.baseline_metrics.get("initial_scores", {}).get("context", 57.5)
        
        # Simulate gradual improvement
        days_since_baseline = 7
        improvement_rate = 0.8
        simulated_current = baseline + (days_since_baseline * improvement_rate)
        
        return min(simulated_current, 100.0)
    
    async def _get_current_competitive_score(self) -> float:
        """Get current competitive score (would integrate with Agent 3 re-analysis)"""
        # In a full implementation, this would re-run Agent 3 analysis
        baseline = self.baseline_metrics.get("initial_scores", {}).get("competitive", 19.4)
        
        # Simulate gradual improvement
        days_since_baseline = 7
        improvement_rate = 0.3
        simulated_current = baseline + (days_since_baseline * improvement_rate)
        
        return min(simulated_current, 100.0)
    
    def _determine_trend_direction(self, current: float, previous: Optional[float]) -> str:
        """Determine trend direction"""
        if previous is None:
            return "stable"
        
        difference = current - previous
        
        if difference > 2.0:
            return "improving"
        elif difference < -2.0:
            return "declining"
        else:
            return "stable"
    
    def _get_historical_brand_performance(self, days_back: int = 7) -> Dict[str, Any]:
        """Get historical brand performance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        cursor.execute('''
            SELECT metric_type, current_value, timestamp
            FROM performance_metrics
            WHERE timestamp > ? AND metric_type IN ('discovery', 'context', 'competitive')
            ORDER BY timestamp DESC
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        historical_data = {}
        for metric_type, current_value, timestamp in results:
            if metric_type not in historical_data:
                historical_data[metric_type] = {
                    "current_value": current_value,
                    "timestamp": timestamp
                }
        
        return historical_data
    
    async def _collect_query_performance(self) -> List[QueryPerformanceData]:
        """Collect query-specific performance data"""
        query_performance = []
        timestamp = datetime.now().isoformat()
        
        # Get priority queries from configuration
        priority_queries = self._get_priority_queries()
        
        for query in priority_queries[:10]:  # Monitor top 10 queries
            # Simulate query performance data (would integrate with real AI engine testing)
            query_data = QueryPerformanceData(
                query=query,
                timestamp=timestamp,
                current_ranking=self._simulate_query_ranking(),
                citation_frequency=self._simulate_citation_frequency(),
                response_quality=self._simulate_response_quality(),
                competitor_rankings=self._simulate_competitor_rankings(),
                market_share=self._simulate_market_share(),
                change_from_baseline=self._simulate_baseline_change()
            )
            
            query_performance.append(query_data)
        
        return query_performance
    
    def _get_priority_queries(self) -> List[str]:
        """Get priority queries for monitoring"""
        # Load from Agent 3 monitoring setup
        agent3_setup = self.config.load_agent3_monitoring_setup()
        if agent3_setup and 'monitoring_setup' in agent3_setup:
            return [
                "mineral sunscreen",
                "dermatologist recommended sunscreen", 
                "reef safe sunscreen",
                "zinc oxide sunscreen",
                "powder sunscreen application"
            ]
        
        return [
            "mineral sunscreen",
            "powder sunscreen",
            "dermatologist sunscreen",
            "reef safe sunscreen",
            "zinc oxide sunscreen"
        ]
    
    def _simulate_query_ranking(self) -> int:
        """Simulate query ranking (would use real AI engine queries)"""
        import random
        return random.randint(1, 10)
    
    def _simulate_citation_frequency(self) -> float:
        """Simulate citation frequency (would use real citation analysis)"""
        import random
        return random.uniform(0.1, 0.8)
    
    def _simulate_response_quality(self) -> float:
        """Simulate response quality score"""
        import random
        return random.uniform(60, 95)
    
    def _simulate_competitor_rankings(self) -> Dict[str, int]:
        """Simulate competitor rankings"""
        competitors = ["EltaMD", "Supergoop", "CeraVe"]
        import random
        return {comp: random.randint(1, 15) for comp in competitors}
    
    def _simulate_market_share(self) -> float:
        """Simulate market share percentage"""
        import random
        return random.uniform(5, 25)
    
    def _simulate_baseline_change(self) -> float:
        """Simulate change from baseline"""
        import random
        return random.uniform(-10, 15)
    
    async def _collect_competitor_performance(self) -> List[CompetitorPerformanceData]:
        """Collect competitor performance data"""
        competitor_performance = []
        timestamp = datetime.now().isoformat()
        
        # Get competitors to monitor
        competitors_config = self.config.get_competitors_to_monitor()
        
        for competitor_config in competitors_config:
            # Simulate competitor performance data (would integrate with real competitive analysis)
            competitor_data = CompetitorPerformanceData(
                competitor=competitor_config.name,
                timestamp=timestamp,
                overall_score=self._simulate_competitor_overall_score(),
                market_share=self._simulate_competitor_market_share(),
                citation_frequency=self._simulate_competitor_citation_frequency(),
                ranking_changes=self._simulate_competitor_ranking_changes(),
                content_strategy_score=self._simulate_competitor_content_score(),
                authority_signal_score=self._simulate_competitor_authority_score(),
                threat_level=self._assess_competitor_threat_level(competitor_config.name)
            )
            
            competitor_performance.append(competitor_data)
        
        return competitor_performance
    
    def _simulate_competitor_overall_score(self) -> float:
        """Simulate competitor overall score"""
        import random
        return random.uniform(60, 85)
    
    def _simulate_competitor_market_share(self) -> float:
        """Simulate competitor market share"""
        import random
        return random.uniform(10, 30)
    
    def _simulate_competitor_citation_frequency(self) -> float:
        """Simulate competitor citation frequency"""
        import random
        return random.uniform(0.2, 0.9)
    
    def _simulate_competitor_ranking_changes(self) -> Dict[str, int]:
        """Simulate competitor ranking changes"""
        queries = ["mineral sunscreen", "dermatologist recommended", "reef safe"]
        import random
        return {query: random.randint(-3, 3) for query in queries}
    
    def _simulate_competitor_content_score(self) -> float:
        """Simulate competitor content strategy score"""
        import random
        return random.uniform(65, 90)
    
    def _simulate_competitor_authority_score(self) -> float:
        """Simulate competitor authority signal score"""
        import random
        return random.uniform(70, 95)
    
    def _assess_competitor_threat_level(self, competitor: str) -> str:
        """Assess competitor threat level"""
        # EltaMD typically higher threat due to authority
        if competitor == "EltaMD":
            return "high"
        elif competitor in ["Supergoop", "CeraVe"]:
            return "medium"
        else:
            return "low"
    
    def _check_milestone_achievements(self, brand_performance: Dict[str, PerformanceMetric]) -> List[str]:
        """Check for milestone achievements"""
        achievements = []
        
        # Define milestones
        milestones = {
            "discovery": [25, 40, 55, 70],
            "context": [65, 70, 80, 85],
            "competitive": [30, 40, 50, 60]
        }
        
        for metric_type, metric_data in brand_performance.items():
            if metric_type in milestones:
                current_value = metric_data.current_value
                
                for milestone in milestones[metric_type]:
                    if (current_value >= milestone and 
                        (metric_data.previous_value is None or metric_data.previous_value < milestone)):
                        achievements.append(
                            f"{metric_data.metric_name} reached {milestone} points milestone"
                        )
        
        return achievements
    
    def _generate_performance_alerts(self, 
                                   brand_performance: Dict[str, PerformanceMetric],
                                   query_performance: List[QueryPerformanceData],
                                   competitor_performance: List[CompetitorPerformanceData]) -> List[str]:
        """Generate performance-based alerts"""
        alerts = []
        
        # Brand performance alerts
        for metric_type, metric_data in brand_performance.items():
            if metric_data.change_percentage >= 10:
                alerts.append(f"POSITIVE: {metric_data.metric_name} improved by {metric_data.change_percentage:.1f}%")
            elif metric_data.change_percentage <= -15:
                alerts.append(f"ALERT: {metric_data.metric_name} declined by {abs(metric_data.change_percentage):.1f}%")
        
        # Query performance alerts
        significant_query_changes = [q for q in query_performance if abs(q.change_from_baseline) >= 10]
        if significant_query_changes:
            alerts.append(f"QUERY ALERT: {len(significant_query_changes)} queries showing significant changes")
        
        # Competitor alerts
        high_threat_competitors = [c for c in competitor_performance if c.threat_level in ["high", "critical"]]
        if high_threat_competitors:
            competitors_list = ", ".join([c.competitor for c in high_threat_competitors])
            alerts.append(f"COMPETITIVE ALERT: High threat level from {competitors_list}")
        
        return alerts
    
    async def _calculate_business_impact_metrics(self, 
                                               brand_performance: Dict[str, PerformanceMetric],
                                               query_performance: List[QueryPerformanceData]) -> Dict[str, float]:
        """Calculate business impact metrics"""
        business_metrics = self.config.get_business_metrics_config()
        
        # Simulated business impact calculations
        avg_citation_frequency = statistics.mean([q.citation_frequency for q in query_performance])
        estimated_traffic_lift = avg_citation_frequency * 1000  # Estimated monthly visits
        
        business_impact = {
            "estimated_monthly_traffic": estimated_traffic_lift,
            "estimated_conversion_value": estimated_traffic_lift * 0.03 * business_metrics.brand_mention_value,
            "brand_mention_value": len(query_performance) * business_metrics.brand_mention_value,
            "competitive_advantage_score": brand_performance.get("competitive", PerformanceMetric(
                timestamp="", metric_type="", metric_name="", current_value=0,
                previous_value=None, change_amount=0, change_percentage=0,
                trend_direction="", baseline_value=None, target_value=None,
                progress_to_target=None
            )).current_value
        }
        
        return business_impact
    
    async def _store_performance_snapshot(self, snapshot: PerformanceSnapshot):
        """Store performance snapshot in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store individual metrics
        for metric_name, metric_data in snapshot.brand_performance.items():
            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, metric_type, metric_name, current_value, 
                    previous_value, change_amount, change_percentage, 
                    trend_direction, baseline_value, target_value, progress_to_target
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric_data.timestamp, metric_data.metric_type, metric_data.metric_name,
                metric_data.current_value, metric_data.previous_value, metric_data.change_amount,
                metric_data.change_percentage, metric_data.trend_direction, metric_data.baseline_value,
                metric_data.target_value, metric_data.progress_to_target
            ))
        
        # Store query performance
        for query_data in snapshot.query_performance:
            cursor.execute('''
                INSERT INTO query_performance (
                    timestamp, query, current_ranking, citation_frequency,
                    response_quality, competitor_rankings, market_share, change_from_baseline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_data.timestamp, query_data.query, query_data.current_ranking,
                query_data.citation_frequency, query_data.response_quality,
                json.dumps(query_data.competitor_rankings), query_data.market_share,
                query_data.change_from_baseline
            ))
        
        # Store competitor performance
        for competitor_data in snapshot.competitor_performance:
            cursor.execute('''
                INSERT INTO competitor_performance (
                    timestamp, competitor, overall_score, market_share,
                    citation_frequency, ranking_changes, content_strategy_score,
                    authority_signal_score, threat_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                competitor_data.timestamp, competitor_data.competitor, competitor_data.overall_score,
                competitor_data.market_share, competitor_data.citation_frequency,
                json.dumps(competitor_data.ranking_changes), competitor_data.content_strategy_score,
                competitor_data.authority_signal_score, competitor_data.threat_level
            ))
        
        # Store complete snapshot
        cursor.execute('''
            INSERT INTO performance_snapshots (timestamp, snapshot_data)
            VALUES (?, ?)
        ''', (snapshot.timestamp, json.dumps(asdict(snapshot), default=str)))
        
        conn.commit()
        conn.close()
    
    def get_performance_history(self, days: int = 30) -> List[PerformanceSnapshot]:
        """Get performance history for specified number of days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT snapshot_data FROM performance_snapshots
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        snapshots = []
        for (snapshot_data,) in results:
            try:
                snapshot_dict = json.loads(snapshot_data)
                # Would need to reconstruct dataclass objects here in full implementation
                snapshots.append(snapshot_dict)
            except json.JSONDecodeError:
                continue
        
        return snapshots
    
    def get_trend_analysis(self, metric_type: str, days: int = 30) -> Dict[str, Any]:
        """Get trend analysis for specific metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, current_value FROM performance_metrics
            WHERE metric_type = ? AND timestamp > ?
            ORDER BY timestamp ASC
        ''', (metric_type, cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        if len(results) < 2:
            return {"trend": "insufficient_data", "slope": 0, "r_squared": 0}
        
        # Simple linear regression for trend analysis
        values = [float(value) for _, value in results]
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        return {
            "trend": "improving" if slope > 0.1 else "declining" if slope < -0.1 else "stable",
            "slope": slope,
            "data_points": n,
            "period_days": days
        }