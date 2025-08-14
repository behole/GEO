import json
import csv
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Union
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """Handles exporting content analysis results in various formats"""
    
    def __init__(self, output_dir: str = "./results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"content_analysis_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        logger.info(f"Export manager initialized. Results will be saved to: {self.session_dir}")
    
    async def export_content_analysis(self, results: Dict[str, Any], 
                                    export_format: str = "both") -> Dict[str, str]:
        """Export complete content analysis results"""
        files_created = {}
        
        try:
            if export_format in ["json", "both"]:
                json_files = await self._export_json_results(results)
                files_created.update(json_files)
            
            if export_format in ["csv", "both"]:
                csv_files = await self._export_csv_results(results)
                files_created.update(csv_files)
            
            # Create summary report
            summary_file = await self._create_summary_report(results)
            files_created["summary_report"] = str(summary_file)
            
            # Create export manifest
            manifest_file = self._create_export_manifest(files_created, results)
            files_created["manifest"] = str(manifest_file)
            
            logger.info(f"Export completed successfully. {len(files_created)} files created.")
            return files_created
            
        except Exception as e:
            logger.error(f"Error during export: {str(e)}")
            raise
    
    async def _export_json_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Export results in JSON format"""
        json_files = {}
        
        # Complete results
        complete_file = self.session_dir / "content_analysis_complete.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        json_files["complete_analysis"] = str(complete_file)
        
        # Brand analysis only
        brand_file = self.session_dir / "brand_content_analysis.json"
        with open(brand_file, 'w', encoding='utf-8') as f:
            json.dump(results.get("brand_content_analysis", {}), f, indent=2, ensure_ascii=False, default=str)
        json_files["brand_analysis"] = str(brand_file)
        
        # Competitive analysis only
        competitive_file = self.session_dir / "competitive_gap_analysis.json"
        with open(competitive_file, 'w', encoding='utf-8') as f:
            json.dump(results.get("competitive_gap_analysis", {}), f, indent=2, ensure_ascii=False, default=str)
        json_files["competitive_analysis"] = str(competitive_file)
        
        # Recommendations only
        recommendations_file = self.session_dir / "comprehensive_recommendations.json"
        with open(recommendations_file, 'w', encoding='utf-8') as f:
            json.dump(results.get("comprehensive_recommendations", {}), f, indent=2, ensure_ascii=False, default=str)
        json_files["recommendations"] = str(recommendations_file)
        
        return json_files
    
    async def _export_csv_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Export results in CSV format"""
        csv_files = {}
        
        # Page scores CSV
        page_scores_file = await self._export_page_scores_csv(results)
        if page_scores_file:
            csv_files["page_scores"] = str(page_scores_file)
        
        # Content gaps CSV
        gaps_file = await self._export_content_gaps_csv(results)
        if gaps_file:
            csv_files["content_gaps"] = str(gaps_file)
        
        # Competitive analysis CSV
        competitive_file = await self._export_competitive_analysis_csv(results)
        if competitive_file:
            csv_files["competitive_analysis"] = str(competitive_file)
        
        # Recommendations CSV
        recommendations_file = await self._export_recommendations_csv(results)
        if recommendations_file:
            csv_files["recommendations"] = str(recommendations_file)
        
        return csv_files
    
    async def _export_page_scores_csv(self, results: Dict[str, Any]) -> Union[Path, None]:
        """Export page scores to CSV"""
        brand_analysis = results.get("brand_content_analysis", {})
        page_scores = brand_analysis.get("detailed_page_scores", [])
        
        if not page_scores:
            return None
        
        file_path = self.session_dir / "page_scores_detailed.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'url', 'page_type', 'overall_score', 'content_structure', 
                'citation_worthiness', 'authority_signals', 'ai_consumption',
                'recommendations_count', 'top_recommendation'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in page_scores:
                recommendations = page.get('recommendations', [])
                writer.writerow({
                    'url': page.get('url', ''),
                    'page_type': page.get('page_type', ''),
                    'overall_score': round(page.get('overall_score', 0), 2),
                    'content_structure': round(page.get('content_structure', 0), 2),
                    'citation_worthiness': round(page.get('citation_worthiness', 0), 2),
                    'authority_signals': round(page.get('authority_signals', 0), 2),
                    'ai_consumption': round(page.get('ai_consumption', 0), 2),
                    'recommendations_count': len(recommendations),
                    'top_recommendation': recommendations[0] if recommendations else ''
                })
        
        return file_path
    
    async def _export_content_gaps_csv(self, results: Dict[str, Any]) -> Union[Path, None]:
        """Export content gaps to CSV"""
        competitive_analysis = results.get("competitive_gap_analysis", {})
        gaps = competitive_analysis.get("identified_gaps", [])
        
        if not gaps:
            return None
        
        file_path = self.session_dir / "content_gaps_analysis.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'gap_type', 'description', 'priority', 'estimated_effort', 
                'business_impact', 'competitor_examples_count', 'first_competitor_example'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for gap in gaps:
                examples = gap.get('competitor_examples', [])
                writer.writerow({
                    'gap_type': gap.get('type', ''),
                    'description': gap.get('description', ''),
                    'priority': gap.get('priority', ''),
                    'estimated_effort': gap.get('estimated_effort', ''),
                    'business_impact': gap.get('business_impact', ''),
                    'competitor_examples_count': len(examples),
                    'first_competitor_example': examples[0] if examples else ''
                })
        
        return file_path
    
    async def _export_competitive_analysis_csv(self, results: Dict[str, Any]) -> Union[Path, None]:
        """Export competitive analysis to CSV"""
        competitive_analysis = results.get("competitive_gap_analysis", {})
        competitor_insights = competitive_analysis.get("competitor_insights", {})
        brand_vs_competitors = competitive_analysis.get("brand_vs_competitors", {})
        
        if not competitor_insights:
            return None
        
        file_path = self.session_dir / "competitive_benchmarking.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'competitor_name', 'overall_score', 'content_types_count', 
                'unique_features_count', 'top_keyword', 'top_keyword_mentions',
                'authority_score', 'avg_word_count'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Add brand data
            brand_name = brand_vs_competitors.get('brand_name', 'Brand')
            brand_score = brand_vs_competitors.get('brand_score', 0)
            writer.writerow({
                'competitor_name': f"{brand_name} (BRAND)",
                'overall_score': round(brand_score, 2),
                'content_types_count': 'N/A',
                'unique_features_count': 'N/A', 
                'top_keyword': 'N/A',
                'top_keyword_mentions': 'N/A',
                'authority_score': 'N/A',
                'avg_word_count': 'N/A'
            })
            
            # Add competitor data
            competitor_scores = brand_vs_competitors.get('competitor_scores', {})
            for competitor, insights in competitor_insights.items():
                content_types = insights.get('content_types_found', {})
                unique_features = insights.get('unique_features', [])
                keyword_coverage = insights.get('keyword_coverage_top10', {})
                authority_metrics = insights.get('authority_metrics', {})
                
                top_keyword = max(keyword_coverage.items(), key=lambda x: x[1]) if keyword_coverage else ('', 0)
                
                writer.writerow({
                    'competitor_name': competitor,
                    'overall_score': round(competitor_scores.get(competitor, 0), 2),
                    'content_types_count': len(content_types),
                    'unique_features_count': len(unique_features),
                    'top_keyword': top_keyword[0],
                    'top_keyword_mentions': top_keyword[1],
                    'authority_score': round(authority_metrics.get('avg_authority_score', 0), 2),
                    'avg_word_count': round(authority_metrics.get('avg_word_count', 0), 0)
                })
        
        return file_path
    
    async def _export_recommendations_csv(self, results: Dict[str, Any]) -> Union[Path, None]:
        """Export recommendations to CSV"""
        recommendations = results.get("comprehensive_recommendations", {})
        action_plan = recommendations.get("action_plan", {})
        
        file_path = self.session_dir / "action_plan_recommendations.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['timeline', 'priority', 'recommendation', 'category']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Immediate actions
            for rec in action_plan.get("immediate_actions_0_30_days", []):
                writer.writerow({
                    'timeline': '0-30 days',
                    'priority': 'HIGH',
                    'recommendation': rec,
                    'category': 'Immediate Action'
                })
            
            # Short term goals
            for rec in action_plan.get("short_term_goals_1_3_months", []):
                writer.writerow({
                    'timeline': '1-3 months',
                    'priority': 'MEDIUM',
                    'recommendation': rec,
                    'category': 'Short Term Goal'
                })
            
            # Long term strategy
            for rec in action_plan.get("long_term_strategy_3_12_months", []):
                writer.writerow({
                    'timeline': '3-12 months', 
                    'priority': 'STRATEGIC',
                    'recommendation': rec,
                    'category': 'Long Term Strategy'
                })
            
            # Quick wins
            for rec in action_plan.get("quick_wins", []):
                writer.writerow({
                    'timeline': 'Immediate',
                    'priority': 'QUICK WIN',
                    'recommendation': rec,
                    'category': 'Quick Win'
                })
        
        return file_path
    
    async def _create_summary_report(self, results: Dict[str, Any]) -> Path:
        """Create executive summary report"""
        file_path = self.session_dir / "EXECUTIVE_SUMMARY.md"
        
        agent_info = results.get("agent_info", {})
        summary = results.get("summary", {})
        brand_analysis = results.get("brand_content_analysis", {})
        competitive_analysis = results.get("competitive_gap_analysis", {})
        recommendations = results.get("comprehensive_recommendations", {})
        
        content = f"""# Content Analysis Agent - Executive Summary

## Analysis Overview
- **Brand**: {agent_info.get('brand', 'Unknown')}
- **Website**: {agent_info.get('website', 'Unknown')}
- **Analysis Date**: {agent_info.get('analysis_timestamp', 'Unknown')}
- **Agent Version**: {agent_info.get('version', '1.0.0')}

## Key Findings

### Content Health Assessment
**Overall Health**: {summary.get('overall_content_health', 'Unknown')}

**Scores Summary**:
- Overall Score: {brand_analysis.get('overall_score', 0):.1f}/100
- Content Structure: {brand_analysis.get('content_structure_score', 0):.1f}/100
- Citation Worthiness: {brand_analysis.get('citation_worthiness_score', 0):.1f}/100
- Authority Signals: {brand_analysis.get('authority_signals_score', 0):.1f}/100
- AI Consumption: {brand_analysis.get('ai_consumption_score', 0):.1f}/100

### Competitive Position
**Position**: {summary.get('competitive_position', 'Unknown')}

**Competitive Overview**:
- Competitors Analyzed: {competitive_analysis.get('brand_vs_competitors', {}).get('competitors_analyzed', 0)}
- Content Gaps Identified: {len(competitive_analysis.get('identified_gaps', []))}
- Competitive Advantages: {len(competitive_analysis.get('competitive_advantages', []))}

## Priority Actions (Next 30 Days)

"""
        
        priority_actions = summary.get('priority_focus_areas', [])
        for i, action in enumerate(priority_actions, 1):
            content += f"{i}. {action}\n"
        
        content += f"""

## Investment & ROI Summary

**High ROI Opportunities**: {len(recommendations.get('roi_estimates', {}).get('high_roi_opportunities', []))}

**Investment Required**:
- Low Effort Items: {recommendations.get('roi_estimates', {}).get('investment_required', {}).get('low', 0)}
- Medium Effort Items: {recommendations.get('roi_estimates', {}).get('investment_required', {}).get('medium', 0)} 
- High Effort Items: {recommendations.get('roi_estimates', {}).get('investment_required', {}).get('high', 0)}

## Timeline Overview

**Immediate (0-30 days)**: {summary.get('timeline_overview', {}).get('immediate', 'Quick wins and critical fixes')}

**Short-term (1-3 months)**: {summary.get('timeline_overview', {}).get('short_term', 'Content creation and optimization')}

**Long-term (3-12 months)**: {summary.get('timeline_overview', {}).get('long_term', 'Strategic positioning and market leadership')}

## Success Metrics & Targets

### 30-Day Targets
- Overall Score Improvement: +{recommendations.get('success_metrics', {}).get('30_day_targets', {}).get('overall_score_improvement', 15 - brand_analysis.get('overall_score', 0)):.1f} points
- Priority Gaps Addressed: {recommendations.get('success_metrics', {}).get('30_day_targets', {}).get('priority_gaps_addressed', 3)}
- New Content Pieces: {recommendations.get('success_metrics', {}).get('30_day_targets', {}).get('new_content_pieces', 5)}

### 90-Day Targets
- Overall Score Target: {recommendations.get('success_metrics', {}).get('90_day_targets', {}).get('overall_score', 'TBD')}/100
- Authority Score Improvement: +{recommendations.get('success_metrics', {}).get('90_day_targets', {}).get('authority_score_improvement', 20)} points

### Annual Goals
- Target Overall Score: {recommendations.get('success_metrics', {}).get('annual_goals', {}).get('overall_score', 'TBD')}/100
- Market Position Goal: {recommendations.get('success_metrics', {}).get('annual_goals', {}).get('market_position', 'Market leader')}

## Next Steps

1. Review detailed analysis files for specific page-level recommendations
2. Prioritize immediate actions based on resource availability
3. Establish content creation workflow for gap closure
4. Set up monthly monitoring and progress tracking
5. Plan competitive analysis refresh in 90 days

---

*This summary was generated by Content Analysis Agent v{agent_info.get('version', '1.0.0')}*
*For detailed data, see accompanying JSON and CSV files*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _create_export_manifest(self, files_created: Dict[str, str], 
                               results: Dict[str, Any]) -> Path:
        """Create manifest of exported files"""
        file_path = self.session_dir / "export_manifest.json"
        
        manifest = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "agent_version": results.get("agent_info", {}).get("version", "1.0.0"),
                "brand": results.get("agent_info", {}).get("brand", "Unknown"),
                "analysis_timestamp": results.get("agent_info", {}).get("analysis_timestamp", "Unknown")
            },
            "files_created": files_created,
            "file_descriptions": {
                "complete_analysis": "Complete analysis results in JSON format",
                "brand_analysis": "Brand-specific content analysis",
                "competitive_analysis": "Competitive gap analysis and benchmarking",
                "recommendations": "Comprehensive recommendations and action plan",
                "page_scores": "Detailed page-by-page scoring (CSV)",
                "content_gaps": "Identified content gaps with priorities (CSV)",
                "competitive_benchmarking": "Competitor comparison data (CSV)",
                "action_plan_recommendations": "Prioritized recommendations by timeline (CSV)",
                "summary_report": "Executive summary in Markdown format",
                "manifest": "This file - describes all exported files"
            },
            "usage_instructions": {
                "executive_review": "Start with EXECUTIVE_SUMMARY.md for high-level overview",
                "detailed_analysis": "Review complete_analysis.json for full technical details",
                "action_planning": "Use action_plan_recommendations.csv to prioritize work",
                "competitive_insights": "Review competitive_benchmarking.csv for market positioning",
                "page_optimization": "Use page_scores_detailed.csv to prioritize page improvements"
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
        
        return file_path