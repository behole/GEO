#!/usr/bin/env python3
"""
Agent 2: Content Analysis Agent
Comprehensive content analysis and optimization system for GEO audit

This agent analyzes website content against GEO best practices, identifies
content gaps through competitive analysis, and provides actionable recommendations.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import get_config, reload_config
from content_scraper import ContentScraper
from content_scorer import ContentScorer
from competitor_analyzer import CompetitorAnalyzer
from export_manager import ExportManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_analysis_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContentAnalysisAgent:
    """Main orchestrator for content analysis and optimization"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = get_config(config_path)
        self.brand_config = self.config.get_brand_config()
        logger.info(f"Initialized Content Analysis Agent for {self.brand_config.name}")
    
    async def run_full_analysis(self, max_pages_per_site: int = 50) -> Dict[str, Any]:
        """Run complete content analysis workflow"""
        logger.info("Starting full content analysis workflow")
        
        try:
            # Step 1: Brand content analysis
            logger.info("Step 1: Analyzing brand content...")
            brand_analysis = await self._analyze_brand_content(max_pages_per_site)
            
            # Step 2: Competitive gap analysis
            logger.info("Step 2: Running competitive analysis...")
            competitive_analysis = await self._run_competitive_analysis(max_pages_per_site)
            
            # Step 3: Generate comprehensive recommendations
            logger.info("Step 3: Generating recommendations...")
            recommendations = self._generate_comprehensive_recommendations(
                brand_analysis, competitive_analysis
            )
            
            # Step 4: Integration with Agent 1 (if available)
            logger.info("Step 4: Integrating with Agent 1 results...")
            agent1_integration = await self._integrate_with_agent1()
            
            # Compile final results
            results = {
                "agent_info": {
                    "name": "Content Analysis Agent (Agent 2)",
                    "version": "1.0.0",
                    "analysis_timestamp": brand_analysis.get("analysis_timestamp"),
                    "brand": self.brand_config.name,
                    "website": self.brand_config.website
                },
                "brand_content_analysis": brand_analysis,
                "competitive_gap_analysis": competitive_analysis,
                "comprehensive_recommendations": recommendations,
                "agent1_integration": agent1_integration,
                "summary": self._generate_executive_summary(
                    brand_analysis, competitive_analysis, recommendations
                )
            }
            
            logger.info("Content analysis workflow completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in content analysis workflow: {str(e)}")
            raise
    
    async def _analyze_brand_content(self, max_pages: int) -> Dict[str, Any]:
        """Analyze brand's own content"""
        scraper = ContentScraper(self.config)
        scorer = ContentScorer(self.config)
        
        async with scraper:
            # Scrape brand website
            site_analysis = await scraper.scrape_website(self.brand_config.website, max_pages)
            
            # Score content against GEO best practices
            site_score = scorer.score_site(site_analysis)
            
            # Compile brand analysis
            return {
                "domain": site_analysis.domain,
                "pages_analyzed": site_analysis.successful_scrapes,
                "pages_failed": site_analysis.failed_scrapes,
                "overall_score": site_score.aggregate_scores.get("overall_score", 0),
                "content_structure_score": site_score.aggregate_scores.get("content_structure_avg", 0),
                "citation_worthiness_score": site_score.aggregate_scores.get("citation_worthiness_avg", 0),
                "authority_signals_score": site_score.aggregate_scores.get("authority_signals_avg", 0),
                "ai_consumption_score": site_score.aggregate_scores.get("ai_consumption_avg", 0),
                "content_gaps": site_score.content_gaps,
                "priority_recommendations": site_score.priority_recommendations,
                "site_level_issues": site_score.site_level_issues,
                "detailed_page_scores": [
                    {
                        "url": page.url,
                        "page_type": page.page_type,
                        "overall_score": page.overall_score,
                        "recommendations": page.recommendations,
                        "content_structure": page.content_structure.total_score,
                        "citation_worthiness": page.citation_worthiness.total_score,
                        "authority_signals": page.authority_signals.total_score,
                        "ai_consumption": page.ai_consumption.total_score
                    }
                    for page in site_score.page_scores
                ],
                "analysis_timestamp": site_score.scoring_timestamp
            }
    
    async def _run_competitive_analysis(self, max_pages: int) -> Dict[str, Any]:
        """Run competitive gap analysis"""
        analyzer = CompetitorAnalyzer(self.config)
        
        gap_analysis = await analyzer.analyze_competitive_landscape(max_pages)
        
        return {
            "brand_vs_competitors": {
                "brand_name": gap_analysis.brand_analysis.competitor_name,
                "brand_score": gap_analysis.brand_analysis.site_score.aggregate_scores.get("overall_score", 0),
                "competitors_analyzed": len(gap_analysis.competitor_analyses),
                "competitor_scores": {
                    analysis.competitor_name: analysis.site_score.aggregate_scores.get("overall_score", 0)
                    for analysis in gap_analysis.competitor_analyses
                }
            },
            "identified_gaps": [
                {
                    "type": gap.gap_type,
                    "description": gap.description,
                    "priority": gap.priority,
                    "estimated_effort": gap.estimated_effort,
                    "business_impact": gap.business_impact,
                    "competitor_examples": gap.competitor_examples
                }
                for gap in gap_analysis.identified_gaps
            ],
            "competitive_advantages": gap_analysis.competitive_advantages,
            "priority_recommendations": gap_analysis.priority_recommendations,
            "content_opportunity_matrix": gap_analysis.content_opportunity_matrix,
            "competitor_insights": {
                analysis.competitor_name: {
                    "content_types_found": analysis.content_types_found,
                    "unique_features": analysis.unique_content_features,
                    "authority_metrics": analysis.authority_metrics,
                    "keyword_coverage_top10": dict(sorted(
                        analysis.keyword_coverage.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:10])
                }
                for analysis in gap_analysis.competitor_analyses
            },
            "analysis_timestamp": gap_analysis.analysis_timestamp
        }
    
    def _generate_comprehensive_recommendations(self, brand_analysis: Dict[str, Any], 
                                              competitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive, prioritized recommendations"""
        
        # Collect all recommendations
        brand_recommendations = brand_analysis.get("priority_recommendations", [])
        competitive_recommendations = competitive_analysis.get("priority_recommendations", [])
        content_gaps = brand_analysis.get("content_gaps", [])
        identified_gaps = competitive_analysis.get("identified_gaps", [])
        
        # Categorize recommendations
        immediate_actions = []
        short_term_goals = []
        long_term_strategy = []
        
        # Process brand-specific recommendations
        overall_score = brand_analysis.get("overall_score", 0)
        
        if overall_score < 40:
            immediate_actions.append("CRITICAL: Conduct comprehensive content audit - overall quality is poor")
        elif overall_score < 60:
            immediate_actions.append("URGENT: Address fundamental content quality issues")
        
        # Add high-priority competitive gaps to immediate actions
        high_priority_gaps = [gap for gap in identified_gaps if gap.get("priority") == "high"]
        for gap in high_priority_gaps[:3]:
            immediate_actions.append(f"Competitive Gap: {gap.get('description', '')}")
        
        # Categorize by effort and impact
        low_effort_high_impact = []
        medium_effort_actions = []
        high_effort_strategic = []
        
        for gap in identified_gaps:
            effort = gap.get("estimated_effort", "medium")
            impact = gap.get("business_impact", "medium")
            description = gap.get("description", "")
            
            if effort == "low" and impact in ["high", "medium"]:
                low_effort_high_impact.append(description)
            elif effort == "medium":
                medium_effort_actions.append(description)
            elif effort == "high" and impact == "high":
                high_effort_strategic.append(description)
        
        # Generate action plan
        action_plan = {
            "immediate_actions_0_30_days": immediate_actions + low_effort_high_impact[:3],
            "short_term_goals_1_3_months": medium_effort_actions[:4] + brand_recommendations[:3],
            "long_term_strategy_3_12_months": high_effort_strategic[:3] + content_gaps[:2],
            "quick_wins": low_effort_high_impact,
            "content_creation_priorities": self._prioritize_content_creation(identified_gaps),
            "technical_improvements": self._extract_technical_recommendations(brand_analysis),
            "competitive_positioning": self._generate_positioning_recommendations(competitive_analysis)
        }
        
        return {
            "executive_summary": self._generate_recommendation_summary(brand_analysis, competitive_analysis),
            "action_plan": action_plan,
            "roi_estimates": self._estimate_roi(identified_gaps),
            "success_metrics": self._define_success_metrics(brand_analysis, competitive_analysis)
        }
    
    def _prioritize_content_creation(self, gaps: List[Dict[str, Any]]) -> List[str]:
        """Prioritize content creation based on gaps"""
        content_gaps = [gap for gap in gaps if gap.get("type") == "missing_content_type"]
        
        # Sort by priority and business impact
        def gap_score(gap):
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            impact_scores = {"high": 3, "medium": 2, "low": 1}
            return priority_scores.get(gap.get("priority", "low"), 1) + impact_scores.get(gap.get("business_impact", "low"), 1)
        
        sorted_gaps = sorted(content_gaps, key=gap_score, reverse=True)
        
        return [gap.get("description", "") for gap in sorted_gaps[:5]]
    
    def _extract_technical_recommendations(self, brand_analysis: Dict[str, Any]) -> List[str]:
        """Extract technical improvement recommendations"""
        technical_recs = []
        
        # Check scores for technical issues
        ai_score = brand_analysis.get("ai_consumption_score", 0)
        authority_score = brand_analysis.get("authority_signals_score", 0)
        structure_score = brand_analysis.get("content_structure_score", 0)
        
        if ai_score < 50:
            technical_recs.append("Implement structured data markup (JSON-LD, Schema.org)")
            technical_recs.append("Optimize content for voice search and AI consumption")
        
        if authority_score < 50:
            technical_recs.append("Add author information and credentials to content")
            technical_recs.append("Increase external authority links to scientific sources")
        
        if structure_score < 50:
            technical_recs.append("Improve heading hierarchy and content structure")
            technical_recs.append("Optimize paragraph and sentence length for readability")
        
        # Add site-level issues
        site_issues = brand_analysis.get("site_level_issues", [])
        technical_recs.extend(site_issues[:3])
        
        return technical_recs[:6]
    
    def _generate_positioning_recommendations(self, competitive_analysis: Dict[str, Any]) -> List[str]:
        """Generate competitive positioning recommendations"""
        positioning = []
        
        advantages = competitive_analysis.get("competitive_advantages", [])
        if advantages:
            positioning.append(f"Leverage competitive advantages: {'; '.join(advantages[:2])}")
        
        # Find best performing competitor for benchmarking
        competitor_scores = competitive_analysis.get("brand_vs_competitors", {}).get("competitor_scores", {})
        if competitor_scores:
            best_competitor = max(competitor_scores.items(), key=lambda x: x[1])
            positioning.append(f"Benchmark against {best_competitor[0]} (score: {best_competitor[1]:.1f})")
        
        # Add opportunity matrix insights
        opportunity_matrix = competitive_analysis.get("content_opportunity_matrix", {})
        high_impact_low_effort = opportunity_matrix.get("high_impact_low_effort", [])
        if high_impact_low_effort:
            positioning.append("Focus on high-impact, low-effort opportunities first")
        
        return positioning
    
    def _estimate_roi(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate ROI for addressing content gaps"""
        roi_estimates = {
            "high_roi_opportunities": [],
            "investment_required": {"low": 0, "medium": 0, "high": 0},
            "expected_impact": {"high": 0, "medium": 0, "low": 0}
        }
        
        for gap in gaps:
            effort = gap.get("estimated_effort", "medium")
            impact = gap.get("business_impact", "medium")
            
            roi_estimates["investment_required"][effort] += 1
            roi_estimates["expected_impact"][impact] += 1
            
            # High impact + low/medium effort = high ROI
            if impact == "high" and effort in ["low", "medium"]:
                roi_estimates["high_roi_opportunities"].append(gap.get("description", ""))
        
        return roi_estimates
    
    def _define_success_metrics(self, brand_analysis: Dict[str, Any], 
                               competitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for tracking improvement"""
        current_score = brand_analysis.get("overall_score", 0)
        competitor_avg = sum(competitive_analysis.get("brand_vs_competitors", {}).get("competitor_scores", {}).values()) / max(1, len(competitive_analysis.get("brand_vs_competitors", {}).get("competitor_scores", {})))
        
        return {
            "current_baseline": {
                "overall_score": current_score,
                "content_structure": brand_analysis.get("content_structure_score", 0),
                "citation_worthiness": brand_analysis.get("citation_worthiness_score", 0),
                "authority_signals": brand_analysis.get("authority_signals_score", 0),
                "ai_consumption": brand_analysis.get("ai_consumption_score", 0)
            },
            "30_day_targets": {
                "overall_score_improvement": min(100, current_score + 15),
                "priority_gaps_addressed": 3,
                "new_content_pieces": 5
            },
            "90_day_targets": {
                "overall_score": min(100, current_score + 30),
                "competitive_gap_closure": "50%",
                "authority_score_improvement": 20
            },
            "annual_goals": {
                "overall_score": min(100, max(75, competitor_avg + 10)),
                "market_position": "Top 3 in content quality",
                "content_gaps_eliminated": "80%"
            },
            "kpi_tracking": [
                "Monthly content quality score",
                "Competitive gap closure rate", 
                "New high-quality content publication",
                "Authority link acquisition",
                "Structured data implementation progress"
            ]
        }
    
    async def _integrate_with_agent1(self) -> Dict[str, Any]:
        """Integrate with Agent 1 baseline results if available"""
        agent1_path = Path(self.config.AGENT1_RESULTS_PATH)
        
        integration = {
            "agent1_available": False,
            "baseline_data": None,
            "cross_agent_insights": [],
            "integrated_recommendations": []
        }
        
        try:
            if agent1_path.exists():
                # Look for latest Agent 1 results
                latest_results = None
                for results_file in agent1_path.glob("**/query_results.json"):
                    with open(results_file, 'r') as f:
                        latest_results = json.load(f)
                    break
                
                if latest_results:
                    integration["agent1_available"] = True
                    integration["baseline_data"] = {
                        "discovery_score": latest_results.get("summary", {}).get("avg_discovery_score", 0),
                        "context_score": latest_results.get("summary", {}).get("avg_context_score", 0),
                        "competitive_score": latest_results.get("summary", {}).get("avg_competitive_score", 0),
                        "total_citations": latest_results.get("summary", {}).get("total_brand_citations", 0),
                        "analysis_timestamp": latest_results.get("analysis_metadata", {}).get("timestamp", "")
                    }
                    
                    # Generate cross-agent insights
                    integration["cross_agent_insights"] = self._generate_cross_agent_insights(latest_results)
                    integration["integrated_recommendations"] = self._generate_integrated_recommendations(latest_results)
                    
        except Exception as e:
            logger.warning(f"Could not integrate with Agent 1: {str(e)}")
        
        return integration
    
    def _generate_cross_agent_insights(self, agent1_results: Dict[str, Any]) -> List[str]:
        """Generate insights by combining Agent 1 and Agent 2 results"""
        insights = []
        
        discovery_score = agent1_results.get("summary", {}).get("avg_discovery_score", 0)
        total_citations = agent1_results.get("summary", {}).get("total_brand_citations", 0)
        
        if discovery_score < 30:
            insights.append("Agent 1 shows low discovery in AI engines - content optimization is critical")
        
        if total_citations < 10:
            insights.append("Agent 1 shows few brand citations - focus on citation-worthy content creation")
        
        # Cross-reference with content gaps
        insights.append("Content gaps identified in Agent 2 align with low citation rates in Agent 1")
        
        return insights
    
    def _generate_integrated_recommendations(self, agent1_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations that combine both agents' insights"""
        recommendations = []
        
        # Combine discovery and content analysis insights
        recommendations.append("Prioritize content types that show high citation potential in Agent 1 analysis")
        recommendations.append("Focus on query categories with low brand visibility for content creation")
        recommendations.append("Align content optimization with AI engines that showed best response in Agent 1")
        
        return recommendations
    
    def _generate_recommendation_summary(self, brand_analysis: Dict[str, Any], 
                                       competitive_analysis: Dict[str, Any]) -> str:
        """Generate executive summary of recommendations"""
        brand_score = brand_analysis.get("overall_score", 0)
        gaps_count = len(competitive_analysis.get("identified_gaps", []))
        
        if brand_score < 40:
            urgency = "CRITICAL"
            action = "immediate comprehensive overhaul"
        elif brand_score < 60:
            urgency = "HIGH"
            action = "significant improvements across multiple areas"
        else:
            urgency = "MODERATE"
            action = "targeted optimizations and competitive gap closure"
        
        return f"""
        {urgency} PRIORITY: Brand content quality ({brand_score:.1f}/100) requires {action}.
        
        Key Findings:
        - {gaps_count} competitive content gaps identified
        - {len(brand_analysis.get('content_gaps', []))} content types need development
        - {len(competitive_analysis.get('competitive_advantages', []))} competitive advantages to leverage
        
        Immediate focus should be on high-impact, low-effort improvements while building
        long-term content strategy to address fundamental gaps and competitive positioning.
        """.strip()
    
    def _generate_executive_summary(self, brand_analysis: Dict[str, Any], 
                                   competitive_analysis: Dict[str, Any], 
                                   recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of entire analysis"""
        
        return {
            "overall_content_health": self._assess_content_health(brand_analysis),
            "competitive_position": self._assess_competitive_position(competitive_analysis),
            "priority_focus_areas": recommendations.get("action_plan", {}).get("immediate_actions_0_30_days", [])[:3],
            "expected_outcomes": [
                "Improved AI engine visibility and citation rates",
                "Enhanced content authority and trustworthiness", 
                "Competitive content gap closure",
                "Better user engagement and conversion"
            ],
            "investment_summary": recommendations.get("roi_estimates", {}),
            "timeline_overview": {
                "immediate": "0-30 days: Quick wins and critical fixes",
                "short_term": "1-3 months: Content creation and optimization",
                "long_term": "3-12 months: Strategic positioning and market leadership"
            }
        }
    
    def _assess_content_health(self, brand_analysis: Dict[str, Any]) -> str:
        """Assess overall content health"""
        score = brand_analysis.get("overall_score", 0)
        
        if score >= 75:
            return "EXCELLENT - Content is well-optimized for GEO"
        elif score >= 60:
            return "GOOD - Some optimization opportunities exist"
        elif score >= 40:
            return "FAIR - Significant improvements needed"
        else:
            return "POOR - Comprehensive content overhaul required"
    
    def _assess_competitive_position(self, competitive_analysis: Dict[str, Any]) -> str:
        """Assess competitive positioning"""
        brand_vs_comp = competitive_analysis.get("brand_vs_competitors", {})
        brand_score = brand_vs_comp.get("brand_score", 0)
        competitor_scores = brand_vs_comp.get("competitor_scores", {}).values()
        
        if not competitor_scores:
            return "Unable to assess - no competitor data available"
        
        avg_competitor = sum(competitor_scores) / len(competitor_scores)
        
        if brand_score > avg_competitor + 15:
            return "LEADING - Outperforming most competitors"
        elif brand_score > avg_competitor:
            return "COMPETITIVE - Performing above average"
        elif brand_score > avg_competitor - 10:
            return "LAGGING - Below average but recoverable"
        else:
            return "SIGNIFICANTLY BEHIND - Major competitive disadvantage"

async def main():
    """Main entry point for Content Analysis Agent"""
    parser = argparse.ArgumentParser(description="Content Analysis Agent for GEO Optimization")
    parser.add_argument("--config", type=str, help="Path to sector configuration file")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to analyze per site")
    parser.add_argument("--output-dir", type=str, default="./results", help="Output directory for results")
    parser.add_argument("--export-format", choices=["json", "csv", "both"], default="both", help="Export format")
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = ContentAnalysisAgent(args.config)
        
        # Run full analysis
        results = await agent.run_full_analysis(args.max_pages)
        
        # Export results
        export_manager = ExportManager(args.output_dir)
        await export_manager.export_content_analysis(results, args.export_format)
        
        print(f"\n{'='*80}")
        print("CONTENT ANALYSIS AGENT - EXECUTIVE SUMMARY")
        print(f"{'='*80}")
        print(f"Brand: {results['agent_info']['brand']}")
        print(f"Analysis completed: {results['agent_info']['analysis_timestamp']}")
        print(f"Overall content health: {results['summary']['overall_content_health']}")
        print(f"Competitive position: {results['summary']['competitive_position']}")
        print(f"\nTop 3 Priority Actions:")
        for i, action in enumerate(results['summary']['priority_focus_areas'], 1):
            print(f"{i}. {action}")
        print(f"\nDetailed results exported to: {args.output_dir}")
        print(f"{'='*80}\n")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())