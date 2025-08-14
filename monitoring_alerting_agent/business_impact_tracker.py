import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import statistics
import sqlite3
from pathlib import Path

from .config import get_config, MonitoringAlertingConfig, BusinessMetrics
from .performance_monitor import PerformanceSnapshot

logger = logging.getLogger(__name__)

@dataclass
class ConversionStage:
    """Individual stage in the conversion funnel"""
    stage_name: str
    timestamp: str
    visitors: int
    conversion_rate: float
    stage_value: float
    attribution_source: str  # "ai_citation", "organic_search", "direct"

@dataclass
class ROICalculation:
    """ROI calculation data"""
    timestamp: str
    period_days: int
    investment_amount: float
    generated_revenue: float
    roi_percentage: float
    roi_attribution: Dict[str, float]  # By source/tactic
    confidence_level: str  # "low", "medium", "high"

@dataclass
class BrandMentionValue:
    """Brand mention value calculation"""
    timestamp: str
    total_mentions: int
    qualified_mentions: int  # High-quality citations
    estimated_value_per_mention: float
    total_brand_value: float
    mention_sentiment: Dict[str, int]  # positive, neutral, negative
    mention_sources: Dict[str, int]  # ai_engines, social, press, etc.

@dataclass
class TrafficAttribution:
    """Traffic attribution analysis"""
    timestamp: str
    total_traffic: int
    ai_driven_traffic: int
    ai_attribution_percentage: float
    traffic_sources: Dict[str, int]
    quality_metrics: Dict[str, float]  # bounce_rate, session_duration, etc.
    conversion_tracking: Dict[str, float]

@dataclass
class BusinessImpactReport:
    """Complete business impact analysis"""
    timestamp: str
    reporting_period_days: int
    conversion_funnel: List[ConversionStage]
    roi_analysis: ROICalculation
    brand_mention_value: BrandMentionValue
    traffic_attribution: TrafficAttribution
    competitive_advantage_metrics: Dict[str, float]
    business_kpis: Dict[str, float]
    actionable_insights: List[str]

class BusinessImpactTracker:
    """Track and quantify business impact of GEO optimizations"""
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.business_metrics = self.config.get_business_metrics_config()
        
        # Initialize database for business impact tracking
        self.db_path = Path(self.config.OUTPUT_DIR) / "business_impact.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_business_database()
        
        # Business metrics configuration
        self.conversion_funnel_stages = [
            "ai_citation", "website_visit", "product_view", "add_to_cart", "purchase"
        ]
        
        logger.info("Business Impact Tracker initialized")
    
    def _init_business_database(self):
        """Initialize business impact database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversion tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversion_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                visitors INTEGER,
                conversion_rate REAL,
                stage_value REAL,
                attribution_source TEXT
            )
        ''')
        
        # ROI tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roi_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                period_days INTEGER,
                investment_amount REAL,
                generated_revenue REAL,
                roi_percentage REAL,
                roi_attribution TEXT,
                confidence_level TEXT
            )
        ''')
        
        # Brand mention tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_mentions INTEGER,
                qualified_mentions INTEGER,
                estimated_value_per_mention REAL,
                total_brand_value REAL,
                mention_sentiment TEXT,
                mention_sources TEXT
            )
        ''')
        
        # Traffic attribution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_attribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_traffic INTEGER,
                ai_driven_traffic INTEGER,
                ai_attribution_percentage REAL,
                traffic_sources TEXT,
                quality_metrics TEXT,
                conversion_tracking TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def track_business_impact(self, performance_snapshot: PerformanceSnapshot) -> BusinessImpactReport:
        """Main function to track and analyze business impact"""
        logger.info("Tracking business impact from performance data")
        
        timestamp = datetime.now().isoformat()
        
        # Analyze conversion funnel
        conversion_funnel = await self._analyze_conversion_funnel(performance_snapshot)
        
        # Calculate ROI
        roi_analysis = await self._calculate_roi_impact(performance_snapshot)
        
        # Track brand mention value
        brand_mention_value = await self._track_brand_mention_value(performance_snapshot)
        
        # Analyze traffic attribution
        traffic_attribution = await self._analyze_traffic_attribution(performance_snapshot)
        
        # Calculate competitive advantage metrics
        competitive_metrics = await self._calculate_competitive_advantage_metrics(performance_snapshot)
        
        # Generate business KPIs
        business_kpis = await self._generate_business_kpis(
            conversion_funnel, roi_analysis, brand_mention_value, traffic_attribution
        )
        
        # Generate actionable insights
        actionable_insights = await self._generate_business_insights(
            roi_analysis, brand_mention_value, traffic_attribution, competitive_metrics
        )
        
        # Create business impact report
        impact_report = BusinessImpactReport(
            timestamp=timestamp,
            reporting_period_days=30,
            conversion_funnel=conversion_funnel,
            roi_analysis=roi_analysis,
            brand_mention_value=brand_mention_value,
            traffic_attribution=traffic_attribution,
            competitive_advantage_metrics=competitive_metrics,
            business_kpis=business_kpis,
            actionable_insights=actionable_insights
        )
        
        # Store in database
        await self._store_business_impact_data(impact_report)
        
        logger.info("Business impact tracking completed")
        
        return impact_report
    
    async def _analyze_conversion_funnel(self, snapshot: PerformanceSnapshot) -> List[ConversionStage]:
        """Analyze the conversion funnel from AI citations to purchases"""
        
        # Calculate base metrics from AI citations
        total_citations = sum([query.citation_frequency for query in snapshot.query_performance])
        
        # Simulate conversion funnel based on industry benchmarks and configuration
        conversion_stages = []
        
        # Stage 1: AI Citations (baseline)
        ai_citations = int(total_citations * 1000)  # Scale up for realistic numbers
        
        conversion_stages.append(ConversionStage(
            stage_name="ai_citation",
            timestamp=snapshot.timestamp,
            visitors=ai_citations,
            conversion_rate=100.0,  # Base stage
            stage_value=ai_citations * self.business_metrics.brand_mention_value,
            attribution_source="ai_citation"
        ))
        
        # Stage 2: Website Visits
        citation_to_visit_rate = 0.08  # 8% of citations lead to visits
        website_visits = int(ai_citations * citation_to_visit_rate)
        
        conversion_stages.append(ConversionStage(
            stage_name="website_visit",
            timestamp=snapshot.timestamp,
            visitors=website_visits,
            conversion_rate=citation_to_visit_rate * 100,
            stage_value=website_visits * 2.50,  # Estimated value per visit
            attribution_source="ai_citation"
        ))
        
        # Stage 3: Product Views
        visit_to_product_rate = 0.30  # 30% of visits view products
        product_views = int(website_visits * visit_to_product_rate)
        
        conversion_stages.append(ConversionStage(
            stage_name="product_view", 
            timestamp=snapshot.timestamp,
            visitors=product_views,
            conversion_rate=visit_to_product_rate * 100,
            stage_value=product_views * 5.00,  # Higher intent value
            attribution_source="ai_citation"
        ))
        
        # Stage 4: Add to Cart
        product_to_cart_rate = 0.15  # 15% add to cart
        add_to_cart = int(product_views * product_to_cart_rate)
        
        conversion_stages.append(ConversionStage(
            stage_name="add_to_cart",
            timestamp=snapshot.timestamp,
            visitors=add_to_cart,
            conversion_rate=product_to_cart_rate * 100,
            stage_value=add_to_cart * 12.50,  # High intent value
            attribution_source="ai_citation"
        ))
        
        # Stage 5: Purchase
        cart_to_purchase_rate = 0.25  # 25% complete purchase
        purchases = int(add_to_cart * cart_to_purchase_rate)
        average_order_value = 25.99  # From configuration
        
        conversion_stages.append(ConversionStage(
            stage_name="purchase",
            timestamp=snapshot.timestamp,
            visitors=purchases,
            conversion_rate=cart_to_purchase_rate * 100,
            stage_value=purchases * average_order_value,
            attribution_source="ai_citation"
        ))
        
        return conversion_stages
    
    async def _calculate_roi_impact(self, snapshot: PerformanceSnapshot) -> ROICalculation:
        """Calculate ROI from GEO optimization efforts"""
        
        # Estimate investment (would be tracked from actual spending)
        monthly_investment = 5000.0  # Estimated monthly GEO investment
        
        # Calculate revenue attribution
        # Get revenue from conversion funnel
        estimated_monthly_revenue = snapshot.business_impact_metrics.get("estimated_conversion_value", 0)
        
        # Add brand value and traffic value
        brand_value = snapshot.business_impact_metrics.get("brand_mention_value", 0)
        traffic_value = snapshot.business_impact_metrics.get("estimated_monthly_traffic", 0) * 2.50  # Value per visit
        
        total_generated_value = estimated_monthly_revenue + brand_value + traffic_value
        
        # Calculate ROI
        roi_percentage = ((total_generated_value - monthly_investment) / monthly_investment) * 100
        
        # ROI attribution breakdown
        roi_attribution = {
            "direct_conversions": (estimated_monthly_revenue / total_generated_value) * 100 if total_generated_value > 0 else 0,
            "brand_awareness": (brand_value / total_generated_value) * 100 if total_generated_value > 0 else 0,
            "traffic_value": (traffic_value / total_generated_value) * 100 if total_generated_value > 0 else 0
        }
        
        # Determine confidence level based on data quality
        confidence_level = self._determine_roi_confidence(snapshot)
        
        return ROICalculation(
            timestamp=snapshot.timestamp,
            period_days=30,
            investment_amount=monthly_investment,
            generated_revenue=total_generated_value,
            roi_percentage=roi_percentage,
            roi_attribution=roi_attribution,
            confidence_level=confidence_level
        )
    
    def _determine_roi_confidence(self, snapshot: PerformanceSnapshot) -> str:
        """Determine confidence level in ROI calculations"""
        # Factors affecting confidence:
        # - Data recency
        # - Number of data points
        # - Consistency of metrics
        
        data_quality_score = 0
        
        # Check query performance data points
        if len(snapshot.query_performance) >= 10:
            data_quality_score += 30
        elif len(snapshot.query_performance) >= 5:
            data_quality_score += 20
        else:
            data_quality_score += 10
        
        # Check competitor data availability
        if len(snapshot.competitor_performance) >= 3:
            data_quality_score += 25
        elif len(snapshot.competitor_performance) >= 1:
            data_quality_score += 15
        
        # Check business metrics availability
        if len(snapshot.business_impact_metrics) >= 3:
            data_quality_score += 25
        
        # Check alert consistency (fewer alerts = more stable data)
        if len(snapshot.performance_alerts) <= 2:
            data_quality_score += 20
        elif len(snapshot.performance_alerts) <= 5:
            data_quality_score += 10
        
        if data_quality_score >= 80:
            return "high"
        elif data_quality_score >= 60:
            return "medium"
        else:
            return "low"
    
    async def _track_brand_mention_value(self, snapshot: PerformanceSnapshot) -> BrandMentionValue:
        """Track and calculate brand mention value"""
        
        # Calculate total mentions from AI citations
        total_mentions = len(snapshot.query_performance)
        
        # Determine qualified mentions (high-quality citations)
        qualified_mentions = len([
            query for query in snapshot.query_performance
            if query.citation_frequency > 0.4 and query.response_quality > 75
        ])
        
        # Calculate brand value
        estimated_value_per_mention = self.business_metrics.brand_mention_value
        total_brand_value = qualified_mentions * estimated_value_per_mention
        
        # Simulate mention sentiment (would integrate with sentiment analysis)
        mention_sentiment = {
            "positive": int(qualified_mentions * 0.7),
            "neutral": int(qualified_mentions * 0.25),
            "negative": int(qualified_mentions * 0.05)
        }
        
        # Simulate mention sources
        mention_sources = {
            "ai_engines": qualified_mentions,
            "social_media": int(qualified_mentions * 0.3),
            "press_coverage": int(qualified_mentions * 0.1),
            "industry_blogs": int(qualified_mentions * 0.2)
        }
        
        return BrandMentionValue(
            timestamp=snapshot.timestamp,
            total_mentions=total_mentions,
            qualified_mentions=qualified_mentions,
            estimated_value_per_mention=estimated_value_per_mention,
            total_brand_value=total_brand_value,
            mention_sentiment=mention_sentiment,
            mention_sources=mention_sources
        )
    
    async def _analyze_traffic_attribution(self, snapshot: PerformanceSnapshot) -> TrafficAttribution:
        """Analyze traffic attribution to AI-driven sources"""
        
        # Calculate AI-driven traffic
        estimated_monthly_traffic = int(snapshot.business_impact_metrics.get("estimated_monthly_traffic", 0))
        ai_driven_traffic = int(estimated_monthly_traffic * 0.6)  # 60% from AI citations
        
        ai_attribution_percentage = (ai_driven_traffic / max(estimated_monthly_traffic, 1)) * 100
        
        # Traffic source breakdown
        traffic_sources = {
            "ai_citations": ai_driven_traffic,
            "organic_search": int(estimated_monthly_traffic * 0.3),
            "direct": int(estimated_monthly_traffic * 0.1)
        }
        
        # Quality metrics (simulated - would integrate with analytics)
        quality_metrics = {
            "bounce_rate": 35.5,  # Lower is better
            "avg_session_duration": 2.8,  # Minutes
            "pages_per_session": 3.2,
            "conversion_rate": 3.1  # Percentage
        }
        
        # Conversion tracking by source
        conversion_tracking = {
            "ai_citation_conversion_rate": 4.2,  # Higher quality traffic
            "organic_search_conversion_rate": 2.8,
            "direct_conversion_rate": 5.1
        }
        
        return TrafficAttribution(
            timestamp=snapshot.timestamp,
            total_traffic=estimated_monthly_traffic,
            ai_driven_traffic=ai_driven_traffic,
            ai_attribution_percentage=ai_attribution_percentage,
            traffic_sources=traffic_sources,
            quality_metrics=quality_metrics,
            conversion_tracking=conversion_tracking
        )
    
    async def _calculate_competitive_advantage_metrics(self, snapshot: PerformanceSnapshot) -> Dict[str, float]:
        """Calculate competitive advantage metrics"""
        
        # Brand performance vs competitors
        brand_overall_score = snapshot.brand_performance.get("overall").current_value if "overall" in snapshot.brand_performance else 0
        
        if snapshot.competitor_performance:
            competitor_scores = [comp.overall_score for comp in snapshot.competitor_performance]
            avg_competitor_score = statistics.mean(competitor_scores)
            max_competitor_score = max(competitor_scores)
            
            competitive_gap = brand_overall_score - avg_competitor_score
            leader_gap = brand_overall_score - max_competitor_score
        else:
            competitive_gap = 0
            leader_gap = 0
        
        # Market share estimation
        estimated_market_share = self._estimate_market_share(snapshot)
        
        # Competitive velocity (rate of improvement)
        competitive_velocity = self._calculate_competitive_velocity(snapshot)
        
        return {
            "competitive_gap": competitive_gap,
            "leader_gap": leader_gap,
            "estimated_market_share": estimated_market_share,
            "competitive_velocity": competitive_velocity,
            "brand_strength_index": brand_overall_score,
            "competitive_threat_level": self._assess_overall_threat_level(snapshot)
        }
    
    def _estimate_market_share(self, snapshot: PerformanceSnapshot) -> float:
        """Estimate market share based on citation frequency and performance"""
        if not snapshot.query_performance:
            return 0.0
        
        # Simple market share estimation based on citation frequency
        total_citations = sum([query.citation_frequency for query in snapshot.query_performance])
        avg_citation_frequency = total_citations / len(snapshot.query_performance)
        
        # Scale to reasonable market share percentage (0-15%)
        estimated_share = min(15.0, avg_citation_frequency * 20)
        
        return estimated_share
    
    def _calculate_competitive_velocity(self, snapshot: PerformanceSnapshot) -> float:
        """Calculate rate of competitive improvement"""
        # Get average change percentage across all brand metrics
        changes = []
        for metric_name, metric_data in snapshot.brand_performance.items():
            if metric_data.change_percentage is not None:
                changes.append(metric_data.change_percentage)
        
        if changes:
            return statistics.mean(changes)
        else:
            return 0.0
    
    def _assess_overall_threat_level(self, snapshot: PerformanceSnapshot) -> float:
        """Assess overall competitive threat level (0-100)"""
        if not snapshot.competitor_performance:
            return 0.0
        
        threat_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        threat_levels = [threat_scores.get(comp.threat_level, 0) for comp in snapshot.competitor_performance]
        
        return statistics.mean(threat_levels)
    
    async def _generate_business_kpis(self, 
                                   conversion_funnel: List[ConversionStage],
                                   roi_analysis: ROICalculation,
                                   brand_value: BrandMentionValue,
                                   traffic_attribution: TrafficAttribution) -> Dict[str, float]:
        """Generate key business KPIs"""
        
        # Revenue metrics
        total_revenue = sum([stage.stage_value for stage in conversion_funnel if stage.stage_name == "purchase"])
        
        # Customer acquisition metrics
        total_customers = sum([stage.visitors for stage in conversion_funnel if stage.stage_name == "purchase"])
        customer_acquisition_cost = roi_analysis.investment_amount / max(total_customers, 1)
        
        # Lifetime value estimation (simplified)
        estimated_ltv = 78.00  # Estimated customer lifetime value
        ltv_to_cac_ratio = estimated_ltv / max(customer_acquisition_cost, 1)
        
        return {
            "monthly_revenue": total_revenue,
            "monthly_customers": total_customers,
            "customer_acquisition_cost": customer_acquisition_cost,
            "lifetime_value": estimated_ltv,
            "ltv_cac_ratio": ltv_to_cac_ratio,
            "roi_percentage": roi_analysis.roi_percentage,
            "brand_awareness_value": brand_value.total_brand_value,
            "ai_traffic_percentage": traffic_attribution.ai_attribution_percentage,
            "average_order_value": total_revenue / max(total_customers, 1),
            "conversion_rate": (total_customers / max(traffic_attribution.total_traffic, 1)) * 100
        }
    
    async def _generate_business_insights(self,
                                        roi_analysis: ROICalculation,
                                        brand_value: BrandMentionValue,
                                        traffic_attribution: TrafficAttribution,
                                        competitive_metrics: Dict[str, float]) -> List[str]:
        """Generate actionable business insights"""
        insights = []
        
        # ROI insights
        if roi_analysis.roi_percentage > 200:
            insights.append(f"Excellent ROI of {roi_analysis.roi_percentage:.1f}% - consider scaling investment")
        elif roi_analysis.roi_percentage > 100:
            insights.append(f"Positive ROI of {roi_analysis.roi_percentage:.1f}% - strong performance")
        elif roi_analysis.roi_percentage > 0:
            insights.append(f"Marginal ROI of {roi_analysis.roi_percentage:.1f}% - optimization needed")
        else:
            insights.append(f"Negative ROI of {roi_analysis.roi_percentage:.1f}% - urgent strategy review required")
        
        # Brand value insights
        qualified_rate = brand_value.qualified_mentions / max(brand_value.total_mentions, 1) * 100
        if qualified_rate > 75:
            insights.append(f"High-quality brand mentions at {qualified_rate:.1f}% - strong brand positioning")
        elif qualified_rate > 50:
            insights.append(f"Moderate brand mention quality at {qualified_rate:.1f}% - room for improvement")
        else:
            insights.append(f"Low brand mention quality at {qualified_rate:.1f}% - focus on authority building")
        
        # Traffic attribution insights
        if traffic_attribution.ai_attribution_percentage > 50:
            insights.append(f"Strong AI traffic attribution at {traffic_attribution.ai_attribution_percentage:.1f}% - GEO strategy working")
        else:
            insights.append(f"Low AI traffic attribution at {traffic_attribution.ai_attribution_percentage:.1f}% - increase GEO focus")
        
        # Competitive insights
        if competitive_metrics["competitive_gap"] > 10:
            insights.append("Strong competitive position - maintain advantage and expand market share")
        elif competitive_metrics["competitive_gap"] > 0:
            insights.append("Slight competitive advantage - focus on widening the gap")
        else:
            insights.append("Behind competitors - aggressive optimization strategy needed")
        
        # Market share insights
        market_share = competitive_metrics.get("estimated_market_share", 0)
        if market_share > 10:
            insights.append(f"Strong market share of {market_share:.1f}% - consider premium positioning")
        elif market_share > 5:
            insights.append(f"Growing market share of {market_share:.1f}% - continue current strategy")
        else:
            insights.append(f"Low market share of {market_share:.1f}% - focus on market penetration")
        
        return insights
    
    async def _store_business_impact_data(self, impact_report: BusinessImpactReport):
        """Store business impact data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store conversion funnel data
        for stage in impact_report.conversion_funnel:
            cursor.execute('''
                INSERT INTO conversion_tracking (
                    timestamp, stage_name, visitors, conversion_rate, 
                    stage_value, attribution_source
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                stage.timestamp, stage.stage_name, stage.visitors,
                stage.conversion_rate, stage.stage_value, stage.attribution_source
            ))
        
        # Store ROI data
        cursor.execute('''
            INSERT INTO roi_tracking (
                timestamp, period_days, investment_amount, generated_revenue,
                roi_percentage, roi_attribution, confidence_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            impact_report.roi_analysis.timestamp, impact_report.roi_analysis.period_days,
            impact_report.roi_analysis.investment_amount, impact_report.roi_analysis.generated_revenue,
            impact_report.roi_analysis.roi_percentage, json.dumps(impact_report.roi_analysis.roi_attribution),
            impact_report.roi_analysis.confidence_level
        ))
        
        # Store brand mention data
        cursor.execute('''
            INSERT INTO brand_mentions (
                timestamp, total_mentions, qualified_mentions,
                estimated_value_per_mention, total_brand_value,
                mention_sentiment, mention_sources
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            impact_report.brand_mention_value.timestamp, impact_report.brand_mention_value.total_mentions,
            impact_report.brand_mention_value.qualified_mentions, impact_report.brand_mention_value.estimated_value_per_mention,
            impact_report.brand_mention_value.total_brand_value, json.dumps(impact_report.brand_mention_value.mention_sentiment),
            json.dumps(impact_report.brand_mention_value.mention_sources)
        ))
        
        # Store traffic attribution data
        cursor.execute('''
            INSERT INTO traffic_attribution (
                timestamp, total_traffic, ai_driven_traffic, ai_attribution_percentage,
                traffic_sources, quality_metrics, conversion_tracking
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            impact_report.traffic_attribution.timestamp, impact_report.traffic_attribution.total_traffic,
            impact_report.traffic_attribution.ai_driven_traffic, impact_report.traffic_attribution.ai_attribution_percentage,
            json.dumps(impact_report.traffic_attribution.traffic_sources), json.dumps(impact_report.traffic_attribution.quality_metrics),
            json.dumps(impact_report.traffic_attribution.conversion_tracking)
        ))
        
        conn.commit()
        conn.close()
    
    def get_business_impact_history(self, days: int = 90) -> Dict[str, List[Any]]:
        """Get business impact history for specified period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get ROI history
        cursor.execute('''
            SELECT * FROM roi_tracking
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (cutoff_date,))
        roi_history = cursor.fetchall()
        
        # Get traffic attribution history
        cursor.execute('''
            SELECT * FROM traffic_attribution
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (cutoff_date,))
        traffic_history = cursor.fetchall()
        
        conn.close()
        
        return {
            "roi_history": roi_history,
            "traffic_history": traffic_history,
            "period_days": days
        }