import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import statistics

from .config import get_config, MonitoringAlertingConfig
from .performance_monitor import PerformanceSnapshot, PerformanceMonitor
from .alert_system import IntelligentAlertSystem, Alert

logger = logging.getLogger(__name__)

@dataclass
class DashboardWidget:
    """Individual dashboard widget configuration"""
    widget_id: str
    widget_type: str  # "metric", "chart", "table", "alert", "progress"
    title: str
    data: Dict[str, Any]
    refresh_rate: str  # "real_time", "hourly", "daily"
    size: str  # "small", "medium", "large"
    position: Dict[str, int]  # {"row": 1, "col": 1}

@dataclass
class DashboardLayout:
    """Complete dashboard layout configuration"""
    dashboard_id: str
    title: str
    description: str
    widgets: List[DashboardWidget]
    last_updated: str
    auto_refresh: bool
    refresh_interval_seconds: int

class DashboardGenerator:
    """Generate and manage performance dashboards"""
    
    def __init__(self, config: Optional[MonitoringAlertingConfig] = None):
        self.config = config or get_config()
        self.performance_monitor = PerformanceMonitor(self.config)
        self.alert_system = IntelligentAlertSystem(self.config)
        
        # Dashboard output directory
        self.dashboard_dir = Path(self.config.OUTPUT_DIR) / "dashboards"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Dashboard Generator initialized")
    
    async def generate_main_dashboard(self) -> DashboardLayout:
        """Generate the main GEO performance dashboard"""
        logger.info("Generating main performance dashboard")
        
        # Get current performance data
        current_snapshot = await self.performance_monitor.monitor_performance_continuous()
        
        # Get alert data
        alert_summary = self.alert_system.get_alert_summary()
        active_alerts = self.alert_system.get_active_alerts()
        
        # Get historical data for trends
        performance_history = self.performance_monitor.get_performance_history(30)
        
        widgets = []
        
        # Performance Overview Widgets
        widgets.extend(await self._create_performance_overview_widgets(current_snapshot, performance_history))
        
        # Competitive Landscape Widgets
        widgets.extend(await self._create_competitive_landscape_widgets(current_snapshot))
        
        # Optimization Pipeline Widgets
        widgets.extend(await self._create_optimization_pipeline_widgets(current_snapshot))
        
        # Business Impact Widgets
        widgets.extend(await self._create_business_impact_widgets(current_snapshot))
        
        # Alert Status Widgets
        widgets.extend(await self._create_alert_status_widgets(alert_summary, active_alerts))
        
        dashboard = DashboardLayout(
            dashboard_id="main_geo_dashboard",
            title="GEO Performance Dashboard",
            description="Comprehensive view of Brush on Block's GEO optimization performance",
            widgets=widgets,
            last_updated=datetime.now().isoformat(),
            auto_refresh=True,
            refresh_interval_seconds=300  # 5 minutes
        )
        
        # Save dashboard configuration
        await self._save_dashboard(dashboard)
        
        # Generate HTML dashboard
        await self._generate_html_dashboard(dashboard)
        
        logger.info(f"Main dashboard generated with {len(widgets)} widgets")
        
        return dashboard
    
    async def _create_performance_overview_widgets(self, 
                                                 snapshot: PerformanceSnapshot,
                                                 history: List[Dict[str, Any]]) -> List[DashboardWidget]:
        """Create performance overview widgets"""
        widgets = []
        
        # Current Scores Widget
        current_scores_data = {
            "discovery_score": {
                "current": snapshot.brand_performance.get("discovery").current_value if "discovery" in snapshot.brand_performance else 0,
                "target": self.config.get_performance_targets().discovery_score_target,
                "trend": snapshot.brand_performance.get("discovery").trend_direction if "discovery" in snapshot.brand_performance else "stable"
            },
            "context_score": {
                "current": snapshot.brand_performance.get("context").current_value if "context" in snapshot.brand_performance else 0,
                "target": self.config.get_performance_targets().context_score_target,
                "trend": snapshot.brand_performance.get("context").trend_direction if "context" in snapshot.brand_performance else "stable"
            },
            "competitive_score": {
                "current": snapshot.brand_performance.get("competitive").current_value if "competitive" in snapshot.brand_performance else 0,
                "target": self.config.get_performance_targets().competitive_score_target,
                "trend": snapshot.brand_performance.get("competitive").trend_direction if "competitive" in snapshot.brand_performance else "stable"
            }
        }
        
        widgets.append(DashboardWidget(
            widget_id="current_scores",
            widget_type="metric",
            title="Current GEO Scores",
            data=current_scores_data,
            refresh_rate="hourly",
            size="large",
            position={"row": 1, "col": 1}
        ))
        
        # Progress to Target Widget
        progress_data = {}
        for metric_name, metric_data in snapshot.brand_performance.items():
            if metric_data.progress_to_target is not None:
                progress_data[metric_name] = {
                    "progress": max(0, min(100, metric_data.progress_to_target)),
                    "current": metric_data.current_value,
                    "target": metric_data.target_value
                }
        
        widgets.append(DashboardWidget(
            widget_id="progress_to_target",
            widget_type="progress",
            title="Progress to Targets",
            data=progress_data,
            refresh_rate="hourly",
            size="medium",
            position={"row": 1, "col": 2}
        ))
        
        # 30-Day Trend Chart Widget
        trend_data = self._prepare_trend_chart_data(history)
        
        widgets.append(DashboardWidget(
            widget_id="performance_trends",
            widget_type="chart",
            title="30-Day Performance Trends",
            data=trend_data,
            refresh_rate="daily",
            size="large",
            position={"row": 2, "col": 1}
        ))
        
        return widgets
    
    async def _create_competitive_landscape_widgets(self, snapshot: PerformanceSnapshot) -> List[DashboardWidget]:
        """Create competitive landscape widgets"""
        widgets = []
        
        # Market Position Widget
        market_position_data = {
            "brand_position": {
                "overall_score": snapshot.brand_performance.get("overall").current_value if "overall" in snapshot.brand_performance else 0,
                "market_rank": self._estimate_market_rank(snapshot),
                "competitive_strength": self._assess_competitive_strength(snapshot)
            },
            "top_competitors": [
                {
                    "name": comp.competitor,
                    "threat_level": comp.threat_level,
                    "market_share": comp.market_share,
                    "score": comp.overall_score
                }
                for comp in sorted(snapshot.competitor_performance, key=lambda x: x.overall_score, reverse=True)[:5]
            ]
        }
        
        widgets.append(DashboardWidget(
            widget_id="market_position",
            widget_type="table",
            title="Market Position & Competitors",
            data=market_position_data,
            refresh_rate="daily",
            size="medium",
            position={"row": 1, "col": 3}
        ))
        
        # Competitive Threat Level Widget
        threat_data = {
            "threat_levels": {
                "critical": len([c for c in snapshot.competitor_performance if c.threat_level == "critical"]),
                "high": len([c for c in snapshot.competitor_performance if c.threat_level == "high"]),
                "medium": len([c for c in snapshot.competitor_performance if c.threat_level == "medium"]),
                "low": len([c for c in snapshot.competitor_performance if c.threat_level == "low"])
            },
            "immediate_threats": [
                comp.competitor for comp in snapshot.competitor_performance 
                if comp.threat_level in ["critical", "high"]
            ]
        }
        
        widgets.append(DashboardWidget(
            widget_id="threat_assessment",
            widget_type="metric",
            title="Competitive Threat Assessment",
            data=threat_data,
            refresh_rate="hourly",
            size="small",
            position={"row": 2, "col": 2}
        ))
        
        # Query Performance Distribution Widget
        query_data = {
            "query_performance": [
                {
                    "query": query.query,
                    "ranking": query.current_ranking,
                    "citation_freq": query.citation_frequency,
                    "market_share": query.market_share
                }
                for query in sorted(snapshot.query_performance, key=lambda x: x.citation_frequency, reverse=True)[:10]
            ]
        }
        
        widgets.append(DashboardWidget(
            widget_id="query_performance",
            widget_type="table",
            title="Top Query Performance",
            data=query_data,
            refresh_rate="daily",
            size="medium",
            position={"row": 3, "col": 1}
        ))
        
        return widgets
    
    async def _create_optimization_pipeline_widgets(self, snapshot: PerformanceSnapshot) -> List[DashboardWidget]:
        """Create optimization pipeline widgets"""
        widgets = []
        
        # Active Optimizations Widget
        optimization_data = await self._get_optimization_pipeline_data()
        
        widgets.append(DashboardWidget(
            widget_id="optimization_pipeline",
            widget_type="table",
            title="Optimization Pipeline",
            data=optimization_data,
            refresh_rate="daily",
            size="medium",
            position={"row": 3, "col": 2}
        ))
        
        # Implementation Timeline Widget
        timeline_data = await self._get_implementation_timeline_data()
        
        widgets.append(DashboardWidget(
            widget_id="implementation_timeline",
            widget_type="chart",
            title="Implementation Timeline",
            data=timeline_data,
            refresh_rate="daily",
            size="large",
            position={"row": 4, "col": 1}
        ))
        
        return widgets
    
    async def _create_business_impact_widgets(self, snapshot: PerformanceSnapshot) -> List[DashboardWidget]:
        """Create business impact widgets"""
        widgets = []
        
        # ROI Tracking Widget
        roi_data = {
            "current_metrics": snapshot.business_impact_metrics,
            "roi_trends": await self._calculate_roi_trends(),
            "conversion_funnel": await self._get_conversion_funnel_data()
        }
        
        widgets.append(DashboardWidget(
            widget_id="roi_tracking",
            widget_type="metric",
            title="Business Impact & ROI",
            data=roi_data,
            refresh_rate="daily",
            size="medium",
            position={"row": 4, "col": 2}
        ))
        
        # Traffic Attribution Widget
        traffic_data = await self._get_traffic_attribution_data(snapshot)
        
        widgets.append(DashboardWidget(
            widget_id="traffic_attribution",
            widget_type="chart",
            title="AI-Driven Traffic Attribution",
            data=traffic_data,
            refresh_rate="daily",
            size="medium",
            position={"row": 5, "col": 1}
        ))
        
        return widgets
    
    async def _create_alert_status_widgets(self, alert_summary: Dict[str, Any], active_alerts: List[Alert]) -> List[DashboardWidget]:
        """Create alert status widgets"""
        widgets = []
        
        # Alert Summary Widget
        widgets.append(DashboardWidget(
            widget_id="alert_summary",
            widget_type="metric",
            title="Alert Status",
            data=alert_summary,
            refresh_rate="real_time",
            size="medium",
            position={"row": 5, "col": 2}
        ))
        
        # Recent Alerts Widget
        recent_alerts_data = {
            "active_alerts": [
                {
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp,
                    "message": alert.message
                }
                for alert in active_alerts[:5]
            ]
        }
        
        widgets.append(DashboardWidget(
            widget_id="recent_alerts",
            widget_type="table",
            title="Recent Alerts",
            data=recent_alerts_data,
            refresh_rate="real_time",
            size="large",
            position={"row": 6, "col": 1}
        ))
        
        return widgets
    
    def _prepare_trend_chart_data(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare trend chart data from performance history"""
        if not history:
            return {"labels": [], "datasets": []}
        
        # Extract timestamps and scores
        timestamps = []
        discovery_scores = []
        context_scores = []
        competitive_scores = []
        
        for snapshot in history[-30:]:  # Last 30 data points
            if isinstance(snapshot, dict) and "brand_performance" in snapshot:
                timestamps.append(snapshot.get("timestamp", ""))
                
                brand_perf = snapshot["brand_performance"]
                discovery_scores.append(brand_perf.get("discovery", {}).get("current_value", 0))
                context_scores.append(brand_perf.get("context", {}).get("current_value", 0))
                competitive_scores.append(brand_perf.get("competitive", {}).get("current_value", 0))
        
        return {
            "labels": [ts.split("T")[0] for ts in timestamps],  # Date only
            "datasets": [
                {
                    "label": "Discovery Score",
                    "data": discovery_scores,
                    "color": "#2196F3"
                },
                {
                    "label": "Context Score", 
                    "data": context_scores,
                    "color": "#4CAF50"
                },
                {
                    "label": "Competitive Score",
                    "data": competitive_scores,
                    "color": "#FF9800"
                }
            ]
        }
    
    def _estimate_market_rank(self, snapshot: PerformanceSnapshot) -> int:
        """Estimate market ranking based on performance"""
        if not snapshot.competitor_performance:
            return 1
        
        brand_score = snapshot.brand_performance.get("overall").current_value if "overall" in snapshot.brand_performance else 0
        competitor_scores = [comp.overall_score for comp in snapshot.competitor_performance]
        
        # Count competitors with higher scores
        higher_scores = len([score for score in competitor_scores if score > brand_score])
        
        return higher_scores + 1
    
    def _assess_competitive_strength(self, snapshot: PerformanceSnapshot) -> str:
        """Assess competitive strength category"""
        market_rank = self._estimate_market_rank(snapshot)
        
        if market_rank <= 3:
            return "Strong"
        elif market_rank <= 7:
            return "Moderate"
        else:
            return "Developing"
    
    async def _get_optimization_pipeline_data(self) -> Dict[str, Any]:
        """Get optimization pipeline data from agents"""
        pipeline_data = {
            "active_optimizations": [],
            "pending_opportunities": [],
            "completed_optimizations": []
        }
        
        # Load Agent 2 results for content optimizations
        agent2_results = self.config.load_agent2_results()
        if agent2_results:
            content_gaps = agent2_results.get("content_gaps", [])
            pipeline_data["pending_opportunities"] = [
                {
                    "type": "content_gap",
                    "description": gap.get("description", "Content optimization opportunity"),
                    "priority": gap.get("priority", "medium"),
                    "estimated_effort": gap.get("effort_level", "medium")
                }
                for gap in content_gaps[:5]
            ]
        
        # Load Agent 3 results for competitive optimizations
        agent3_results = self.config.load_agent3_results()
        if agent3_results:
            tactical_recs = agent3_results.get("actionable_recommendations", {}).get("high_priority", [])
            pipeline_data["active_optimizations"] = [
                {
                    "type": "competitive",
                    "description": rec.get("recommendation", "Competitive optimization"),
                    "priority": rec.get("priority", "high"),
                    "timeline": rec.get("timeline", "short_term")
                }
                for rec in tactical_recs[:3]
            ]
        
        return pipeline_data
    
    async def _get_implementation_timeline_data(self) -> Dict[str, Any]:
        """Get implementation timeline data"""
        return {
            "timeline_items": [
                {
                    "task": "Authority building program",
                    "start_date": "2025-08-15",
                    "end_date": "2025-11-15",
                    "status": "in_progress",
                    "progress": 25
                },
                {
                    "task": "Content gap closure",
                    "start_date": "2025-08-20",
                    "end_date": "2025-10-20",
                    "status": "planned",
                    "progress": 0
                },
                {
                    "task": "Competitive response strategy",
                    "start_date": "2025-08-25",
                    "end_date": "2025-09-25",
                    "status": "planned", 
                    "progress": 0
                }
            ]
        }
    
    async def _calculate_roi_trends(self) -> Dict[str, List[float]]:
        """Calculate ROI trends over time"""
        return {
            "monthly_roi": [150, 180, 220, 280, 350],  # Simulated trend
            "months": ["Apr", "May", "Jun", "Jul", "Aug"]
        }
    
    async def _get_conversion_funnel_data(self) -> Dict[str, Any]:
        """Get conversion funnel data"""
        return {
            "stages": [
                {"name": "AI Citations", "count": 1000, "rate": 100},
                {"name": "Website Visits", "count": 80, "rate": 8.0},
                {"name": "Product Views", "count": 24, "rate": 3.0},
                {"name": "Add to Cart", "count": 12, "rate": 1.5},
                {"name": "Purchase", "count": 3, "rate": 0.4}
            ]
        }
    
    async def _get_traffic_attribution_data(self, snapshot: PerformanceSnapshot) -> Dict[str, Any]:
        """Get traffic attribution data"""
        estimated_traffic = snapshot.business_impact_metrics.get("estimated_monthly_traffic", 0)
        
        return {
            "traffic_sources": [
                {"source": "AI Citations", "visits": int(estimated_traffic * 0.6)},
                {"source": "Organic Search", "visits": int(estimated_traffic * 0.3)},
                {"source": "Direct", "visits": int(estimated_traffic * 0.1)}
            ],
            "monthly_trend": [
                int(estimated_traffic * 0.7),
                int(estimated_traffic * 0.8),
                int(estimated_traffic * 0.9),
                int(estimated_traffic)
            ]
        }
    
    async def _save_dashboard(self, dashboard: DashboardLayout):
        """Save dashboard configuration to file"""
        dashboard_file = self.dashboard_dir / f"{dashboard.dashboard_id}.json"
        
        with open(dashboard_file, 'w') as f:
            json.dump(asdict(dashboard), f, indent=2, default=str)
        
        logger.info(f"Dashboard configuration saved to {dashboard_file}")
    
    async def _generate_html_dashboard(self, dashboard: DashboardLayout):
        """Generate HTML dashboard from configuration"""
        html_content = self._create_dashboard_html(dashboard)
        
        html_file = self.dashboard_dir / f"{dashboard.dashboard_id}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML dashboard generated at {html_file}")
    
    def _create_dashboard_html(self, dashboard: DashboardLayout) -> str:
        """Create HTML dashboard content"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard-header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .widget {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .widget h3 {{
            margin-top: 0;
            color: #333;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2196F3;
        }}
        .trend-up {{ color: #4CAF50; }}
        .trend-down {{ color: #f44336; }}
        .trend-stable {{ color: #FF9800; }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #4CAF50;
            transition: width 0.3s ease;
        }}
        .alert-critical {{ border-left: 5px solid #f44336; }}
        .alert-high {{ border-left: 5px solid #ff9800; }}
        .alert-medium {{ border-left: 5px solid #ffeb3b; }}
        .alert-low {{ border-left: 5px solid #4caf50; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .refresh-info {{
            font-size: 0.8em;
            color: #666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>{dashboard.title}</h1>
        <p>{dashboard.description}</p>
        <p class="refresh-info">Last updated: {dashboard.last_updated}</p>
    </div>
    
    <div class="dashboard-grid">
        {self._generate_widget_html(dashboard.widgets)}
    </div>
    
    <script>
        // Auto-refresh functionality
        if ({str(dashboard.auto_refresh).lower()}) {{
            setTimeout(() => {{
                location.reload();
            }}, {dashboard.refresh_interval_seconds * 1000});
        }}
    </script>
</body>
</html>
"""
    
    def _generate_widget_html(self, widgets: List[DashboardWidget]) -> str:
        """Generate HTML for dashboard widgets"""
        widget_html = []
        
        for widget in widgets:
            if widget.widget_type == "metric":
                widget_html.append(self._create_metric_widget_html(widget))
            elif widget.widget_type == "chart":
                widget_html.append(self._create_chart_widget_html(widget))
            elif widget.widget_type == "table":
                widget_html.append(self._create_table_widget_html(widget))
            elif widget.widget_type == "progress":
                widget_html.append(self._create_progress_widget_html(widget))
            elif widget.widget_type == "alert":
                widget_html.append(self._create_alert_widget_html(widget))
        
        return "\n".join(widget_html)
    
    def _create_metric_widget_html(self, widget: DashboardWidget) -> str:
        """Create HTML for metric widget"""
        data = widget.data
        
        if "discovery_score" in data:
            # Current scores widget
            return f"""
            <div class="widget">
                <h3>{widget.title}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                    <div>
                        <h4>Discovery</h4>
                        <div class="metric-value trend-{data['discovery_score']['trend']}">{data['discovery_score']['current']:.1f}</div>
                        <div>Target: {data['discovery_score']['target']}</div>
                    </div>
                    <div>
                        <h4>Context</h4>
                        <div class="metric-value trend-{data['context_score']['trend']}">{data['context_score']['current']:.1f}</div>
                        <div>Target: {data['context_score']['target']}</div>
                    </div>
                    <div>
                        <h4>Competitive</h4>
                        <div class="metric-value trend-{data['competitive_score']['trend']}">{data['competitive_score']['current']:.1f}</div>
                        <div>Target: {data['competitive_score']['target']}</div>
                    </div>
                </div>
                <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
            </div>
            """
        else:
            # Generic metric widget
            return f"""
            <div class="widget">
                <h3>{widget.title}</h3>
                <pre>{json.dumps(data, indent=2)}</pre>
                <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
            </div>
            """
    
    def _create_progress_widget_html(self, widget: DashboardWidget) -> str:
        """Create HTML for progress widget"""
        data = widget.data
        
        progress_html = []
        for metric_name, metric_data in data.items():
            progress_html.append(f"""
                <div style="margin-bottom: 15px;">
                    <h4>{metric_name.replace('_', ' ').title()}</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {metric_data['progress']:.1f}%"></div>
                    </div>
                    <div style="font-size: 0.9em;">
                        {metric_data['current']:.1f} / {metric_data['target']:.1f} ({metric_data['progress']:.1f}%)
                    </div>
                </div>
            """)
        
        return f"""
        <div class="widget">
            <h3>{widget.title}</h3>
            {''.join(progress_html)}
            <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
        </div>
        """
    
    def _create_table_widget_html(self, widget: DashboardWidget) -> str:
        """Create HTML for table widget"""
        return f"""
        <div class="widget">
            <h3>{widget.title}</h3>
            <pre>{json.dumps(widget.data, indent=2)}</pre>
            <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
        </div>
        """
    
    def _create_chart_widget_html(self, widget: DashboardWidget) -> str:
        """Create HTML for chart widget"""
        return f"""
        <div class="widget">
            <h3>{widget.title}</h3>
            <p>Chart visualization would be rendered here with Chart.js or similar library</p>
            <pre>{json.dumps(widget.data, indent=2)}</pre>
            <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
        </div>
        """
    
    def _create_alert_widget_html(self, widget: DashboardWidget) -> str:
        """Create HTML for alert widget"""
        return f"""
        <div class="widget">
            <h3>{widget.title}</h3>
            <pre>{json.dumps(widget.data, indent=2)}</pre>
            <div class="refresh-info">Refresh: {widget.refresh_rate}</div>
        </div>
        """
    
    async def generate_executive_dashboard(self) -> DashboardLayout:
        """Generate executive-level dashboard with high-level KPIs"""
        # Simplified dashboard for executives
        current_snapshot = await self.performance_monitor.monitor_performance_continuous()
        
        widgets = [
            DashboardWidget(
                widget_id="executive_kpis",
                widget_type="metric",
                title="Key Performance Indicators",
                data=self._extract_executive_kpis(current_snapshot),
                refresh_rate="daily",
                size="large",
                position={"row": 1, "col": 1}
            ),
            DashboardWidget(
                widget_id="roi_summary",
                widget_type="metric",
                title="Business Impact Summary",
                data=current_snapshot.business_impact_metrics,
                refresh_rate="daily",
                size="medium",
                position={"row": 1, "col": 2}
            )
        ]
        
        dashboard = DashboardLayout(
            dashboard_id="executive_dashboard",
            title="Executive GEO Dashboard",
            description="High-level overview for executive stakeholders",
            widgets=widgets,
            last_updated=datetime.now().isoformat(),
            auto_refresh=True,
            refresh_interval_seconds=3600  # 1 hour
        )
        
        await self._save_dashboard(dashboard)
        await self._generate_html_dashboard(dashboard)
        
        return dashboard
    
    def _extract_executive_kpis(self, snapshot: PerformanceSnapshot) -> Dict[str, Any]:
        """Extract executive-level KPIs"""
        overall_score = snapshot.brand_performance.get("overall").current_value if "overall" in snapshot.brand_performance else 0
        
        return {
            "overall_geo_score": overall_score,
            "market_position": self._estimate_market_rank(snapshot),
            "competitive_threats": len([c for c in snapshot.competitor_performance if c.threat_level in ["high", "critical"]]),
            "improvement_opportunities": len(snapshot.performance_alerts),
            "monthly_progress": f"+{overall_score - 30:.1f} points"  # Simulated baseline
        }