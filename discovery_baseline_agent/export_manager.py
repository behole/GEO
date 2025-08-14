import json
import csv
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import pandas as pd
from dataclasses import asdict

from response_analyzer import ResponseAnalysis, Citation
from scoring_engine import BaselineScores, ScoreBreakdown

class JSONExporter:
    """Handles JSON export functionality"""
    
    @staticmethod
    def export_complete_results(
        baseline_scores: BaselineScores,
        analyses: List[ResponseAnalysis],
        insights: Dict[str, Any],
        metadata: Dict[str, Any],
        filepath: str
    ) -> None:
        """Export complete discovery baseline results to JSON"""
        
        # Convert dataclasses to dictionaries
        baseline_scores_dict = asdict(baseline_scores)
        analyses_dict = [asdict(analysis) for analysis in analyses]
        
        # Create comprehensive export structure
        export_data = {
            "meta": {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_version": "1.0.0",
                "baseline_date": baseline_scores.calculation_timestamp,
                **metadata
            },
            "summary": {
                "overall_score": baseline_scores.overall_score,
                "discovery_score": baseline_scores.discovery_score.total_score,
                "context_score": baseline_scores.context_score.total_score,
                "competitive_score": baseline_scores.competitive_score.total_score,
                "data_quality_score": baseline_scores.data_quality_score,
                "total_queries": len(analyses),
                "successful_responses": len([a for a in analyses if a.response_text]),
                "your_brand_mentions": sum(1 for a in analyses if a.your_brand_mentioned),
                "total_citations": sum(len(a.citations) for a in analyses)
            },
            "detailed_scores": baseline_scores_dict,
            "insights": insights,
            "raw_analyses": analyses_dict,
            "performance_metrics": JSONExporter._calculate_performance_metrics(analyses)
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_summary_only(
        baseline_scores: BaselineScores,
        insights: Dict[str, Any],
        metadata: Dict[str, Any],
        filepath: str
    ) -> None:
        """Export summary results only (no raw data)"""
        
        summary_data = {
            "meta": {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_version": "1.0.0",
                "baseline_date": baseline_scores.calculation_timestamp,
                **metadata
            },
            "scores": {
                "overall_score": baseline_scores.overall_score,
                "discovery_score": baseline_scores.discovery_score.total_score,
                "context_score": baseline_scores.context_score.total_score,
                "competitive_score": baseline_scores.competitive_score.total_score,
                "data_quality_score": baseline_scores.data_quality_score
            },
            "score_breakdowns": {
                "discovery": asdict(baseline_scores.discovery_score),
                "context": asdict(baseline_scores.context_score),
                "competitive": asdict(baseline_scores.competitive_score)
            },
            "insights": insights
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _calculate_performance_metrics(analyses: List[ResponseAnalysis]) -> Dict[str, Any]:
        """Calculate additional performance metrics"""
        if not analyses:
            return {}
        
        successful_analyses = [a for a in analyses if a.response_text]
        
        # Engine performance
        engine_stats = {}
        for analysis in analyses:
            engine = analysis.ai_engine
            if engine not in engine_stats:
                engine_stats[engine] = {"total": 0, "successful": 0, "citations": 0}
            
            engine_stats[engine]["total"] += 1
            if analysis.response_text:
                engine_stats[engine]["successful"] += 1
                engine_stats[engine]["citations"] += len(analysis.citations)
        
        # Calculate success rates
        for engine in engine_stats:
            stats = engine_stats[engine]
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
            stats["avg_citations"] = stats["citations"] / stats["successful"] if stats["successful"] > 0 else 0
        
        # Competitor analysis
        all_competitors = set()
        for analysis in successful_analyses:
            all_competitors.update(analysis.competitors_mentioned)
        
        competitor_frequency = {}
        for analysis in successful_analyses:
            for competitor in analysis.competitors_mentioned:
                competitor_frequency[competitor] = competitor_frequency.get(competitor, 0) + 1
        
        # Sort competitors by frequency
        top_competitors = sorted(competitor_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "engine_performance": engine_stats,
            "competitor_analysis": {
                "unique_competitors": len(all_competitors),
                "top_competitors": [{"brand": comp, "mentions": count} for comp, count in top_competitors],
                "competitor_frequency": competitor_frequency
            },
            "response_quality": {
                "avg_length": sum(a.response_length for a in successful_analyses) / len(successful_analyses) if successful_analyses else 0,
                "avg_quality": sum(a.response_quality for a in successful_analyses) / len(successful_analyses) if successful_analyses else 0,
                "responses_with_recommendations": sum(1 for a in successful_analyses if a.contains_recommendations),
                "responses_with_products": sum(1 for a in successful_analyses if a.contains_specific_products)
            }
        }

class CSVExporter:
    """Handles CSV export functionality"""
    
    @staticmethod
    def export_analyses_summary(analyses: List[ResponseAnalysis], filepath: str) -> None:
        """Export response analyses summary to CSV"""
        
        # Prepare data for CSV
        csv_data = []
        for analysis in analyses:
            row = {
                "query": analysis.query,
                "ai_engine": analysis.ai_engine,
                "model": analysis.model,
                "timestamp": analysis.timestamp,
                "response_length": analysis.response_length,
                "response_quality": analysis.response_quality,
                "total_citations": len(analysis.citations),
                "your_brand_mentioned": analysis.your_brand_mentioned,
                "competitors_mentioned": len(analysis.competitors_mentioned),
                "total_brands_mentioned": analysis.total_brands_mentioned,
                "contains_recommendations": analysis.contains_recommendations,
                "contains_specific_products": analysis.contains_specific_products,
                "mention_context": analysis.mention_context or "",
                "top_competitors": ", ".join(analysis.competitors_mentioned[:3]) if analysis.competitors_mentioned else ""
            }
            csv_data.append(row)
        
        # Write CSV
        CSVExporter._write_csv(csv_data, filepath)
    
    @staticmethod
    def export_citations_detail(analyses: List[ResponseAnalysis], filepath: str) -> None:
        """Export detailed citation information to CSV"""
        
        csv_data = []
        for analysis in analyses:
            for citation in analysis.citations:
                row = {
                    "query": analysis.query,
                    "ai_engine": analysis.ai_engine,
                    "model": analysis.model,
                    "timestamp": analysis.timestamp,
                    "brand": citation.brand,
                    "product": citation.product or "",
                    "position": citation.position,
                    "sentiment": citation.sentiment,
                    "mention_type": citation.mention_type,
                    "confidence": citation.confidence,
                    "context": citation.context,
                    "is_your_brand": citation.brand == "your_brand"
                }
                csv_data.append(row)
        
        # Write CSV
        CSVExporter._write_csv(csv_data, filepath)
    
    @staticmethod
    def export_scores_summary(baseline_scores: BaselineScores, filepath: str) -> None:
        """Export scores summary to CSV"""
        
        csv_data = [{
            "metric": "Overall Score",
            "score": baseline_scores.overall_score,
            "confidence": None,
            "category": "Summary"
        }]
        
        # Discovery score components
        for component, score in baseline_scores.discovery_score.component_scores.items():
            csv_data.append({
                "metric": f"Discovery - {component.replace('_', ' ').title()}",
                "score": score,
                "confidence": baseline_scores.discovery_score.confidence,
                "category": "Discovery"
            })
        
        # Context score components
        for component, score in baseline_scores.context_score.component_scores.items():
            csv_data.append({
                "metric": f"Context - {component.replace('_', ' ').title()}",
                "score": score,
                "confidence": baseline_scores.context_score.confidence,
                "category": "Context"
            })
        
        # Competitive score components
        for component, score in baseline_scores.competitive_score.component_scores.items():
            csv_data.append({
                "metric": f"Competitive - {component.replace('_', ' ').title()}",
                "score": score,
                "confidence": baseline_scores.competitive_score.confidence,
                "category": "Competitive"
            })
        
        # Add data quality
        csv_data.append({
            "metric": "Data Quality Score",
            "score": baseline_scores.data_quality_score,
            "confidence": None,
            "category": "Quality"
        })
        
        # Write CSV
        CSVExporter._write_csv(csv_data, filepath)
    
    @staticmethod
    def export_competitor_analysis(analyses: List[ResponseAnalysis], filepath: str) -> None:
        """Export competitor analysis to CSV"""
        
        # Count competitor mentions
        competitor_stats = {}
        
        for analysis in analyses:
            for competitor in analysis.competitors_mentioned:
                if competitor not in competitor_stats:
                    competitor_stats[competitor] = {
                        "total_mentions": 0,
                        "queries_mentioned": 0,
                        "engines_mentioned": set(),
                        "average_position": [],
                        "positive_mentions": 0,
                        "negative_mentions": 0,
                        "neutral_mentions": 0
                    }
                
                competitor_stats[competitor]["total_mentions"] += 1
                competitor_stats[competitor]["queries_mentioned"] += 1
                competitor_stats[competitor]["engines_mentioned"].add(analysis.ai_engine)
                
                # Get citation details for this competitor
                competitor_citations = [c for c in analysis.citations if c.brand == competitor]
                for citation in competitor_citations:
                    competitor_stats[competitor]["average_position"].append(citation.position)
                    if citation.sentiment == "positive":
                        competitor_stats[competitor]["positive_mentions"] += 1
                    elif citation.sentiment == "negative":
                        competitor_stats[competitor]["negative_mentions"] += 1
                    else:
                        competitor_stats[competitor]["neutral_mentions"] += 1
        
        # Convert to CSV data
        csv_data = []
        for competitor, stats in competitor_stats.items():
            avg_position = sum(stats["average_position"]) / len(stats["average_position"]) if stats["average_position"] else 0
            
            csv_data.append({
                "competitor": competitor,
                "total_mentions": stats["total_mentions"],
                "queries_mentioned": stats["queries_mentioned"],
                "engines_count": len(stats["engines_mentioned"]),
                "engines_list": ", ".join(stats["engines_mentioned"]),
                "average_position": round(avg_position, 2),
                "positive_mentions": stats["positive_mentions"],
                "negative_mentions": stats["negative_mentions"],
                "neutral_mentions": stats["neutral_mentions"],
                "sentiment_ratio": round(stats["positive_mentions"] / stats["total_mentions"], 2) if stats["total_mentions"] > 0 else 0
            })
        
        # Sort by total mentions descending
        csv_data.sort(key=lambda x: x["total_mentions"], reverse=True)
        
        # Write CSV
        CSVExporter._write_csv(csv_data, filepath)
    
    @staticmethod
    def _write_csv(data: List[Dict], filepath: str) -> None:
        """Write data to CSV file"""
        if not data:
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

class ExportManager:
    """Main export manager orchestrating all export operations"""
    
    def __init__(self, output_dir: str = "./results"):
        self.output_dir = output_dir
        self.json_exporter = JSONExporter()
        self.csv_exporter = CSVExporter()
    
    def export_all(
        self,
        baseline_scores: BaselineScores,
        analyses: List[ResponseAnalysis],
        insights: Dict[str, Any],
        metadata: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Export all data in multiple formats"""
        
        if not run_id:
            run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # Create run-specific directory
        run_dir = os.path.join(self.output_dir, f"discovery_baseline_{run_id}")
        os.makedirs(run_dir, exist_ok=True)
        
        # File paths
        files_created = {}
        
        # JSON exports
        complete_json = os.path.join(run_dir, "complete_results.json")
        summary_json = os.path.join(run_dir, "summary_results.json")
        
        self.json_exporter.export_complete_results(
            baseline_scores, analyses, insights, metadata, complete_json
        )
        self.json_exporter.export_summary_only(
            baseline_scores, insights, metadata, summary_json
        )
        
        files_created["complete_json"] = complete_json
        files_created["summary_json"] = summary_json
        
        # CSV exports
        analyses_csv = os.path.join(run_dir, "analyses_summary.csv")
        citations_csv = os.path.join(run_dir, "citations_detail.csv")
        scores_csv = os.path.join(run_dir, "scores_summary.csv")
        competitors_csv = os.path.join(run_dir, "competitor_analysis.csv")
        
        self.csv_exporter.export_analyses_summary(analyses, analyses_csv)
        self.csv_exporter.export_citations_detail(analyses, citations_csv)
        self.csv_exporter.export_scores_summary(baseline_scores, scores_csv)
        self.csv_exporter.export_competitor_analysis(analyses, competitors_csv)
        
        files_created["analyses_csv"] = analyses_csv
        files_created["citations_csv"] = citations_csv
        files_created["scores_csv"] = scores_csv
        files_created["competitors_csv"] = competitors_csv
        
        # Create export summary
        summary_file = os.path.join(run_dir, "export_summary.txt")
        try:
            self._create_export_summary(baseline_scores, analyses, run_id, summary_file, files_created)
            files_created["summary_txt"] = summary_file
        except Exception as e:
            print(f"Error creating export summary: {e}")
            import traceback
            traceback.print_exc()
        
        return files_created
    
    def _create_export_summary(
        self,
        baseline_scores: BaselineScores,
        analyses: List[ResponseAnalysis],
        run_id: str,
        filepath: str,
        files_created: Dict[str, str]
    ) -> None:
        """Create a human-readable export summary"""
        
        successful_analyses = [a for a in analyses if a.response_text]
        
        summary_content = f"""Discovery Baseline Agent - Export Summary
========================================

Run ID: {run_id}
Export Date: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
Baseline Date: {baseline_scores.calculation_timestamp}

SCORE SUMMARY
=============
Overall Score: {baseline_scores.overall_score:.1f}/100
Discovery Score: {baseline_scores.discovery_score.total_score:.1f}/100
Context Score: {baseline_scores.context_score.total_score:.1f}/100
Competitive Score: {baseline_scores.competitive_score.total_score:.1f}/100
Data Quality: {baseline_scores.data_quality_score:.1f}/100

KEY METRICS
===========
Total Queries: {len(analyses)}
Successful Responses: {len(successful_analyses)}
Success Rate: {len(successful_analyses)/len(analyses)*100:.1f}%
Your Brand Mentions: {sum(1 for a in analyses if a.your_brand_mentioned)}
Total Citations: {sum(len(a.citations) for a in analyses)}
Unique Competitors: {len(set().union(*(a.competitors_mentioned for a in analyses)))}

FILES CREATED
=============
"""
        
        for file_type, file_path in files_created.items():
            summary_content += f"{file_type}: {os.path.basename(file_path)}\n"
        
        summary_content += f"""
NEXT STEPS
==========
1. Review complete_results.json for detailed analysis
2. Open scores_summary.csv for score breakdowns
3. Analyze competitor_analysis.csv for competitive insights
4. Use citations_detail.csv for specific improvement opportunities

For questions or support, refer to the Discovery Baseline Agent documentation.
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary_content)

# Utility functions for external use
def quick_export_summary(baseline_scores: BaselineScores, output_path: str) -> None:
    """Quick export of just the summary scores"""
    export_manager = ExportManager(os.path.dirname(output_path))
    export_manager.json_exporter.export_summary_only(
        baseline_scores, {}, {}, output_path
    )

def quick_export_csv(analyses: List[ResponseAnalysis], output_path: str) -> None:
    """Quick export of analyses to CSV"""
    CSVExporter.export_analyses_summary(analyses, output_path)