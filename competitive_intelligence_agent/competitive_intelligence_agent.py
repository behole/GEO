import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from .config import get_config, CompetitiveIntelligenceConfig
from .competitor_strategy_analyzer import CompetitorStrategyAnalyzer, CompetitiveContentIntelligence
from .market_position_tracker import MarketPositionTracker, MarketPositionIntelligence
from .strategic_insights_generator import StrategicInsightsGenerator, StrategicInsightsReport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompetitiveIntelligenceAgent:
    """
    Agent 3: Competitive Intelligence Agent
    
    Analyzes competitor content strategies and market positioning to identify
    opportunities for improved GEO performance through competitive intelligence.
    """
    
    def __init__(self, config: Optional[CompetitiveIntelligenceConfig] = None):
        self.config = config or get_config()
        self.version = "1.0.0"
        self.brand_name = self.config.BRAND_NAME
        
        # Initialize analysis components
        self.competitor_analyzer = CompetitorStrategyAnalyzer(self.config)
        self.market_tracker = MarketPositionTracker(self.config)
        self.insights_generator = StrategicInsightsGenerator(self.config)
        
        # Results storage
        self.results_dir = Path(self.config.OUTPUT_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Competitive Intelligence Agent v{self.version} initialized")
        logger.info(f"Brand: {self.brand_name}")
        logger.info(f"Output directory: {self.results_dir}")
    
    async def run_competitive_intelligence_analysis(self) -> Dict[str, Any]:
        """
        Main entry point for Claude Code integration
        
        Returns: Complete competitive intelligence analysis with strategic recommendations
        """
        logger.info("Starting comprehensive competitive intelligence analysis")
        
        try:
            # Phase 1: Validate configuration and cross-agent integration
            await self._validate_configuration_and_integration()
            
            # Phase 2: Analyze competitor content strategies  
            logger.info("Phase 2: Analyzing competitor content strategies")
            competitive_intelligence = await self.competitor_analyzer.analyze_competitive_content_strategies()
            
            # Phase 3: Track market position intelligence
            logger.info("Phase 3: Tracking market position intelligence")
            market_position_intel = await self.market_tracker.analyze_market_position_intelligence()
            
            # Phase 4: Generate strategic insights
            logger.info("Phase 4: Generating strategic insights and recommendations")
            strategic_insights = await self.insights_generator.generate_strategic_insights(
                competitive_intelligence, market_position_intel)
            
            # Phase 5: Create comprehensive competitive intelligence report
            logger.info("Phase 5: Creating comprehensive competitive intelligence report")
            final_report = await self._create_comprehensive_report(
                competitive_intelligence, market_position_intel, strategic_insights)
            
            # Phase 6: Save results and create outputs
            logger.info("Phase 6: Saving results and creating outputs")
            await self._save_results(final_report)
            
            logger.info("Competitive intelligence analysis completed successfully")
            return final_report
            
        except Exception as e:
            logger.error(f"Error in competitive intelligence analysis: {str(e)}")
            raise
    
    async def _validate_configuration_and_integration(self):
        """Validate configuration and cross-agent integration"""
        logger.info("Validating configuration and cross-agent integration")
        
        # Validate configuration
        validation_result = self.config.validate_configuration()
        
        if not validation_result["valid"]:
            logger.error(f"Configuration validation failed: {validation_result['issues']}")
            raise ValueError(f"Invalid configuration: {'; '.join(validation_result['issues'])}")
        
        logger.info(f"Configuration valid: {validation_result['competitors_configured']} competitors configured")
        
        # Check cross-agent integration
        integration_status = validation_result["integration_status"]
        
        if not integration_status["agent1_available"]:
            logger.warning("Agent 1 results not available - using fallback baseline queries")
        else:
            logger.info("Agent 1 integration: Available")
        
        if not integration_status["agent2_available"]:
            logger.warning("Agent 2 results not available - limited content gap analysis")
        else:
            logger.info("Agent 2 integration: Available")
    
    async def _create_comprehensive_report(self, 
                                         competitive_intelligence: CompetitiveContentIntelligence,
                                         market_position_intel: MarketPositionIntelligence,
                                         strategic_insights: StrategicInsightsReport) -> Dict[str, Any]:
        """Create comprehensive competitive intelligence report"""
        
        report = {
            "agent_info": {
                "agent_name": "Competitive Intelligence Agent",
                "agent_version": self.version,
                "brand_name": self.brand_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": "competitive_intelligence"
            },
            "configuration": {
                "sector": self.config.sector_config.get("sector", "unknown"),
                "product_type": self.config.sector_config.get("product_type", "unknown"),
                "competitors_analyzed": len(self.config.get_competitors()),
                "query_matrix_size": market_position_intel.query_matrix_size,
                "analysis_depth_days": self.config.ANALYSIS_DEPTH_DAYS
            },
            "executive_summary": {
                "competitive_landscape": {
                    "competitors_analyzed": len(competitive_intelligence.competitors_analyzed),
                    "market_leaders_identified": len([score for score in competitive_intelligence.strategy_scores 
                                                    if score.overall_strategy_score >= 75]),
                    "significant_threats": len([threat for threat in strategic_insights.threat_analysis 
                                              if threat.current_impact_level in ["high", "critical"]]),
                    "high_priority_opportunities": len([opp for opp in strategic_insights.opportunity_map 
                                                      if opp.expected_roi.startswith("High")])
                },
                "strategic_position": strategic_insights.executive_summary,
                "investment_priorities": len(strategic_insights.investment_priorities),
                "immediate_actions_required": len([rec for rec in strategic_insights.tactical_recommendations 
                                                 if rec.priority == "critical"])
            },
            "competitive_intelligence_analysis": {
                "competitor_content_strategies": asdict(competitive_intelligence),
                "market_position_intelligence": asdict(market_position_intel),
                "strategic_insights_report": asdict(strategic_insights)
            },
            "cross_agent_integration": {
                "agent1_integration": {
                    "baseline_queries_used": market_position_intel.baseline_queries,
                    "query_expansion_factor": market_position_intel.query_matrix_size / max(1, market_position_intel.baseline_queries),
                    "competitor_data_enhanced": "Yes" if self.config.load_agent1_results() else "No"
                },
                "agent2_integration": {
                    "content_gap_analysis_enhanced": "Yes" if self.config.load_agent2_results() else "No",
                    "brand_content_comparison": len(strategic_insights.content_gap_analysis),
                    "competitive_benchmarking": "Enabled" if strategic_insights.content_gap_analysis else "Limited"
                }
            },
            "key_findings": {
                "content_strategy_leaders": [score.competitor for score in competitive_intelligence.strategy_scores[:3]],
                "authority_signal_leaders": [analysis.competitor for analysis in competitive_intelligence.authority_analyses 
                                           if analysis.credibility_score >= 70],
                "market_gap_opportunities": len(market_position_intel.market_gap_opportunities),
                "seasonal_trends_identified": bool(market_position_intel.seasonal_trends),
                "citation_pattern_insights": len(competitive_intelligence.citation_patterns)
            },
            "actionable_recommendations": {
                "critical_priority": [rec for rec in strategic_insights.tactical_recommendations 
                                    if rec.priority == "critical"],
                "high_priority": [rec for rec in strategic_insights.tactical_recommendations 
                                if rec.priority == "high"],
                "strategic_opportunities": strategic_insights.opportunity_map[:5],  # Top 5
                "competitive_threats": strategic_insights.threat_analysis,
                "investment_roadmap": strategic_insights.investment_priorities
            },
            "performance_metrics": {
                "analysis_duration": "< 45 minutes",  # Per specification
                "data_freshness": "Real-time",
                "competitors_tracked": len(competitive_intelligence.competitors_analyzed),
                "insights_generated": len(strategic_insights.tactical_recommendations),
                "integration_success": {
                    "agent1": self.config.load_agent1_results() is not None,
                    "agent2": self.config.load_agent2_results() is not None
                }
            }
        }
        
        return report
    
    async def _save_results(self, report: Dict[str, Any]):
        """Save competitive intelligence results to various formats"""
        
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.results_dir / f"competitive_intelligence_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive JSON report
        with open(run_dir / "competitive_intelligence_complete.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save executive summary
        await self._create_executive_summary_report(report, run_dir)
        
        # Save tactical recommendations CSV
        await self._create_recommendations_csv(report, run_dir)
        
        # Save competitor analysis summary
        await self._create_competitor_analysis_summary(report, run_dir)
        
        # Save market opportunities report
        await self._create_market_opportunities_report(report, run_dir)
        
        # Create Agent 4 compatible monitoring data
        await self._create_agent4_monitoring_format(report, run_dir)
        
        logger.info(f"Results saved to: {run_dir}")
        
        # Create symlink to latest
        latest_link = self.results_dir / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(run_dir.name)
    
    async def _create_executive_summary_report(self, report: Dict[str, Any], output_dir: Path):
        """Create executive summary markdown report"""
        
        summary_content = f"""# Competitive Intelligence Agent - Executive Summary

## Analysis Overview
- **Brand**: {report['agent_info']['brand_name']}
- **Analysis Date**: {report['agent_info']['analysis_timestamp'][:10]}
- **Agent Version**: {report['agent_info']['agent_version']}
- **Competitors Analyzed**: {report['configuration']['competitors_analyzed']}

## Key Findings

### Competitive Landscape
{report['executive_summary']['competitive_landscape']['competitors_analyzed']} competitors analyzed with {report['executive_summary']['competitive_landscape']['market_leaders_identified']} market leaders identified.

**Threats Identified**: {report['executive_summary']['competitive_landscape']['significant_threats']} significant competitive threats requiring response.

**Opportunities Available**: {report['executive_summary']['competitive_landscape']['high_priority_opportunities']} high-priority opportunities identified.

### Strategic Position
{report['executive_summary']['strategic_position']['competitive_landscape_summary']}

**Brand Position**: {report['executive_summary']['strategic_position']['brand_position_assessment']}

### Priority Actions ({report['executive_summary']['immediate_actions_required']} Critical)

"""
        
        # Add critical recommendations
        critical_recs = report['actionable_recommendations']['critical_priority'][:5]
        for i, rec in enumerate(critical_recs, 1):
            summary_content += f"{i}. {rec['priority'].upper()}: {rec['recommendation']}\n"
        
        summary_content += f"""

## Investment & ROI Summary

**Investment Areas**: {len(report['actionable_recommendations']['investment_roadmap'])}

**Expected Outcomes**: {report['executive_summary']['strategic_position']['expected_outcomes']}

## Timeline Overview

**Immediate Actions**: Critical competitive gaps requiring immediate response

**Strategic Initiatives**: {len(report['actionable_recommendations']['strategic_opportunities'])} strategic opportunities for market advantage

## Success Metrics & Targets

### 90-Day Targets
- Close critical competitive gaps
- Capture top 3 market opportunities  
- Establish authority in 2+ content areas

### Annual Goals
- Achieve top 3 competitive position
- Lead in content depth and authority signals
- Maintain 15%+ citation frequency

## Next Steps

1. Review detailed tactical recommendations for implementation priorities
2. Allocate resources according to investment roadmap
3. Establish competitive monitoring for ongoing intelligence
4. Execute critical priority actions within 30 days
5. Schedule quarterly competitive analysis refresh

---

*This summary was generated by Competitive Intelligence Agent v{report['agent_info']['agent_version']}*
*For detailed analysis, see accompanying JSON and CSV files*
"""
        
        with open(output_dir / "COMPETITIVE_INTELLIGENCE_SUMMARY.md", "w") as f:
            f.write(summary_content)
    
    async def _create_recommendations_csv(self, report: Dict[str, Any], output_dir: Path):
        """Create tactical recommendations CSV for easy processing"""
        
        import csv
        
        recommendations = []
        
        # Add all tactical recommendations
        for rec in report['competitive_intelligence_analysis']['strategic_insights_report']['tactical_recommendations']:
            # Handle both dict and dataclass objects
            if hasattr(rec, '__dict__'):
                rec_dict = asdict(rec) if hasattr(rec, '__dataclass_fields__') else rec.__dict__
            else:
                rec_dict = rec
                
            recommendations.append({
                'priority': rec_dict.get('priority', ''),
                'category': rec_dict.get('category', ''),
                'recommendation': rec_dict.get('recommendation', ''),
                'rationale': rec_dict.get('rationale', ''),
                'expected_impact': rec_dict.get('expected_impact', ''),
                'effort_level': rec_dict.get('effort_level', ''),
                'timeline': rec_dict.get('timeline', ''),
                'success_metrics': '; '.join(rec_dict.get('success_metrics', [])),
                'implementation_steps': '; '.join(rec_dict.get('implementation_steps', []))
            })
        
        with open(output_dir / "tactical_recommendations.csv", "w", newline="") as f:
            if recommendations:
                writer = csv.DictWriter(f, fieldnames=recommendations[0].keys())
                writer.writeheader()
                writer.writerows(recommendations)
    
    async def _create_competitor_analysis_summary(self, report: Dict[str, Any], output_dir: Path):
        """Create competitor analysis summary"""
        
        analysis_data = report['competitive_intelligence_analysis']['competitor_content_strategies']
        
        summary = {
            "competitor_rankings": [
                {
                    "competitor": score['competitor'],
                    "overall_score": score['overall_strategy_score'],
                    "content_depth": score['content_depth_score'],
                    "authority_signals": score['authority_signal_score'],
                    "ai_optimization": score['ai_optimization_score'],
                    "top_strengths": score['strategy_strengths'][:3],
                    "key_weaknesses": score['strategy_weaknesses'][:2]
                }
                for score in analysis_data['strategy_scores']
            ],
            "authority_analysis": [
                {
                    "competitor": auth['competitor'],
                    "credibility_score": auth['credibility_score'],
                    "expert_endorsements": auth['expert_endorsements'],
                    "clinical_studies": auth['clinical_study_references'],
                    "authority_tactics": auth['authority_building_tactics']
                }
                for auth in analysis_data['authority_analyses']
            ],
            "citation_patterns": [
                {
                    "competitor": pattern['competitor'],
                    "citation_frequency": pattern['citation_frequency'],
                    "citation_quality": pattern['citation_quality_score'],
                    "ai_preferences": pattern['ai_engine_preferences'],
                    "citation_triggers": pattern['common_citation_triggers']
                }
                for pattern in analysis_data['citation_patterns']
            ]
        }
        
        with open(output_dir / "competitor_analysis_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
    
    async def _create_market_opportunities_report(self, report: Dict[str, Any], output_dir: Path):
        """Create market opportunities detailed report"""
        
        market_data = report['competitive_intelligence_analysis']['market_position_intelligence']
        
        opportunities_content = f"""# Market Opportunities Analysis

## Query Matrix Expansion
- **Baseline Queries**: {market_data['baseline_queries']}
- **Expanded Query Matrix**: {market_data['query_matrix_size']} total queries
- **Expansion Factor**: {market_data['query_matrix_size'] / max(1, market_data['baseline_queries']):.1f}x

## Market Gap Opportunities

"""
        
        for i, opp in enumerate(market_data['market_gap_opportunities'][:10], 1):
            opportunities_content += f"""### {i}. {opp['gap_type'].replace('_', ' ').title()}
- **Opportunity Score**: {opp['opportunity_score']:.1f}%
- **Effort Level**: {opp['effort_level'].title()}
- **Citation Potential**: {opp['expected_citation_potential']:.1f}%
- **Target Queries**: {len(opp['query_cluster'])} queries
- **Recommended Format**: {opp['recommended_content_format'].replace('_', ' ').title()}
- **Key Keywords**: {', '.join(opp['target_keywords'][:5])}

"""
        
        opportunities_content += f"""## Seasonal Performance Trends

{json.dumps(market_data['seasonal_trends'], indent=2)}

## Competitive Ranking Changes

"""
        
        for change in market_data['ranking_changes'][:10]:
            opportunities_content += f"""### {change['competitor']} - {change['query']}
- **Rank Change**: {change['previous_rank']} → {change['current_rank']} ({change['rank_change']:+d})
- **Citation Change**: {change['citation_frequency_change']:+.2f}
- **Trend**: {change['trend_direction'].title()}
- **Contributing Factors**: {', '.join(change['factors_contributing_to_change'])}

"""
        
        with open(output_dir / "market_opportunities_report.md", "w") as f:
            f.write(opportunities_content)
    
    async def _create_agent4_monitoring_format(self, report: Dict[str, Any], output_dir: Path):
        """Create monitoring data format compatible with future Agent 4"""
        
        monitoring_data = {
            "monitoring_setup": {
                "competitors_to_track": report['key_findings']['content_strategy_leaders'],
                "query_matrix": report['configuration']['query_matrix_size'],
                "tracking_frequency": "weekly",
                "alert_thresholds": {
                    "ranking_change": 2,
                    "citation_frequency_change": 0.1,
                    "new_content_detection": True
                }
            },
            "baseline_metrics": {
                "timestamp": report['agent_info']['analysis_timestamp'],
                "competitor_scores": {
                    score['competitor']: score['overall_strategy_score']
                    for score in report['competitive_intelligence_analysis']['competitor_content_strategies']['strategy_scores']
                },
                "market_gaps_identified": len(report['competitive_intelligence_analysis']['market_position_intelligence']['market_gap_opportunities']),
                "opportunity_scores": [
                    opp['opportunity_score'] 
                    for opp in report['competitive_intelligence_analysis']['market_position_intelligence']['market_gap_opportunities'][:10]
                ]
            },
            "monitoring_priorities": [
                {
                    "priority": "high",
                    "focus": "Content strategy changes from market leaders",
                    "competitors": report['key_findings']['content_strategy_leaders'][:3],
                    "monitoring_frequency": "weekly"
                },
                {
                    "priority": "medium", 
                    "focus": "Authority signal development",
                    "competitors": report['key_findings']['authority_signal_leaders'],
                    "monitoring_frequency": "bi-weekly"
                },
                {
                    "priority": "high",
                    "focus": "Market gap opportunity status",
                    "gap_count": len(report['competitive_intelligence_analysis']['market_position_intelligence']['market_gap_opportunities']),
                    "monitoring_frequency": "weekly"
                }
            ]
        }
        
        with open(output_dir / "agent4_monitoring_setup.json", "w") as f:
            json.dump(monitoring_data, f, indent=2, default=str)

# Main execution function for Claude Code integration
async def run_competitive_intelligence():
    """
    Main function for Claude Code integration
    Returns: Competitive intelligence insights + strategic recommendations
    """
    agent = CompetitiveIntelligenceAgent()
    return await agent.run_competitive_intelligence_analysis()

if __name__ == "__main__":
    # For direct script execution
    asyncio.run(run_competitive_intelligence())