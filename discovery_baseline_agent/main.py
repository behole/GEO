#!/usr/bin/env python3
"""
Discovery Baseline Agent - Main Orchestration Module

This module serves as the main entry point for the Discovery Baseline Agent,
orchestrating all components to establish your current position in AI-powered
search results for mineral sunscreen queries.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

from config import Config
from api_clients import AIClientFactory, ConcurrentQueryManager
from query_matrix import QueryMatrix
from response_analyzer import ResponseAnalyzer, BatchAnalyzer
from scoring_engine import BaselineScoreCalculator
from export_manager import ExportManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('discovery_baseline.log')
    ]
)

logger = logging.getLogger(__name__)

class DiscoveryBaselineAgent:
    """Main orchestration class for the Discovery Baseline Agent"""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """Initialize the agent with optional configuration override"""
        self.config = Config()
        
        # Apply configuration overrides
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)
        
        # Initialize components
        self.clients = None
        self.query_manager = None
        self.batch_analyzer = BatchAnalyzer()
        self.score_calculator = BaselineScoreCalculator()
        self.export_manager = ExportManager(self.config.OUTPUT_DIR)
        
        # Runtime metrics
        self.start_time = None
        self.execution_metrics = {}
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize API clients and validate configuration"""
        logger.info("Initializing Discovery Baseline Agent...")
        
        # Validate configuration
        config_status = self.config.validate()
        if not config_status["valid"]:
            logger.error("Configuration validation failed:")
            for issue in config_status["issues"]:
                logger.error(f"  - {issue}")
            return {"success": False, "error": "Configuration validation failed", "details": config_status}
        
        logger.info(f"Configuration valid. {config_status['enabled_engines']} of {config_status['total_engines']} engines enabled.")
        
        # Create API clients
        try:
            self.clients = AIClientFactory.create_clients()
            self.query_manager = ConcurrentQueryManager(self.clients, self.config.MAX_CONCURRENT_REQUESTS)
            
            logger.info(f"Initialized {len(self.clients)} API clients")
            for client in self.clients:
                logger.info(f"  - {client.get_engine_name()}: {client.model}")
            
            return {"success": True, "clients_initialized": len(self.clients), "engines": AIClientFactory.get_enabled_engines()}
            
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {str(e)}")
            return {"success": False, "error": f"Client initialization failed: {str(e)}"}
    
    async def run_discovery_baseline(
        self,
        query_categories: Optional[List[str]] = None,
        max_queries: Optional[int] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main function to run the complete discovery baseline process
        
        Args:
            query_categories: Specific categories to run (default: all)
            max_queries: Maximum number of queries to execute (default: all)
            run_id: Custom run identifier (default: auto-generated)
        
        Returns:
            Dictionary containing results and metadata
        """
        self.start_time = time.time()
        
        if not run_id:
            run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Starting Discovery Baseline run: {run_id}")
        
        try:
            # Step 1: Initialize
            init_result = await self.initialize()
            if not init_result["success"]:
                return init_result
            
            # Step 2: Prepare queries
            queries = self._prepare_queries(query_categories, max_queries)
            logger.info(f"Prepared {len(queries)} queries for execution")
            
            # Step 3: Execute queries
            logger.info("Executing queries across all AI engines...")
            query_start = time.time()
            
            raw_responses = await self.query_manager.query_batch(
                QueryMatrix.BASE_PROMPT,
                queries
            )
            
            query_duration = time.time() - query_start
            logger.info(f"Query execution completed in {query_duration:.2f} seconds")
            
            # Step 4: Analyze responses
            logger.info("Analyzing AI responses...")
            analysis_start = time.time()
            
            all_responses = [response for batch in raw_responses for response in batch]
            analyses = self.batch_analyzer.analyze_batch(all_responses)
            
            analysis_duration = time.time() - analysis_start
            logger.info(f"Response analysis completed in {analysis_duration:.2f} seconds")
            
            # Step 5: Calculate scores
            logger.info("Calculating baseline scores...")
            score_start = time.time()
            
            baseline_scores = self.score_calculator.calculate_baseline_scores(analyses)
            insights = self.score_calculator.generate_insights(baseline_scores)
            
            score_duration = time.time() - score_start
            logger.info(f"Score calculation completed in {score_duration:.2f} seconds")
            
            # Step 6: Export results
            logger.info("Exporting results...")
            export_start = time.time()
            
            metadata = self._create_metadata(run_id, queries, query_duration, analysis_duration, score_duration)
            files_created = self.export_manager.export_all(
                baseline_scores, analyses, insights, metadata, run_id
            )
            
            export_duration = time.time() - export_start
            total_duration = time.time() - self.start_time
            
            logger.info(f"Export completed in {export_duration:.2f} seconds")
            logger.info(f"Total execution time: {total_duration:.2f} seconds")
            
            # Step 7: Generate summary
            summary = self._create_execution_summary(
                baseline_scores, analyses, total_duration, files_created
            )
            
            logger.info("Discovery Baseline run completed successfully!")
            self._log_summary_results(baseline_scores)
            
            return {
                "success": True,
                "run_id": run_id,
                "baseline_scores": baseline_scores,
                "insights": insights,
                "execution_summary": summary,
                "files_created": files_created,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Discovery Baseline run failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "run_id": run_id,
                "duration": time.time() - self.start_time if self.start_time else 0
            }
    
    def _prepare_queries(self, categories: Optional[List[str]], max_queries: Optional[int]) -> List[str]:
        """Prepare the list of queries to execute"""
        if categories:
            queries = []
            for category in categories:
                queries.extend(QueryMatrix.get_queries_by_category(category))
        else:
            queries = QueryMatrix.get_all_queries()
        
        if max_queries and len(queries) > max_queries:
            queries = queries[:max_queries]
            logger.info(f"Limited to {max_queries} queries")
        
        return queries
    
    def _create_metadata(
        self,
        run_id: str,
        queries: List[str],
        query_duration: float,
        analysis_duration: float,
        score_duration: float
    ) -> Dict[str, Any]:
        """Create execution metadata"""
        return {
            "run_id": run_id,
            "agent_version": "1.0.0",
            "execution_timestamp": datetime.utcnow().isoformat(),
            "total_queries": len(queries),
            "engines_used": len(self.clients),
            "engine_list": [client.get_engine_name() for client in self.clients],
            "timing": {
                "query_execution": query_duration,
                "response_analysis": analysis_duration,
                "score_calculation": score_duration,
                "total_duration": time.time() - self.start_time
            },
            "configuration": {
                "max_concurrent_requests": self.config.MAX_CONCURRENT_REQUESTS,
                "request_timeout": self.config.REQUEST_TIMEOUT,
                "retry_attempts": self.config.RETRY_ATTEMPTS
            }
        }
    
    def _create_execution_summary(
        self,
        baseline_scores,
        analyses: List,
        total_duration: float,
        files_created: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create execution summary"""
        successful_responses = len([a for a in analyses if a.response_text])
        
        return {
            "execution_time": total_duration,
            "queries_executed": len(analyses),
            "successful_responses": successful_responses,
            "success_rate": successful_responses / len(analyses) if analyses else 0,
            "overall_score": baseline_scores.overall_score,
            "files_exported": len(files_created),
            "performance_rating": self._calculate_performance_rating(total_duration, len(analyses))
        }
    
    def _calculate_performance_rating(self, duration: float, total_queries: int) -> str:
        """Calculate performance rating based on execution time"""
        queries_per_minute = (total_queries / duration) * 60
        
        if queries_per_minute >= 30:
            return "Excellent"
        elif queries_per_minute >= 20:
            return "Good"
        elif queries_per_minute >= 10:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _log_summary_results(self, baseline_scores) -> None:
        """Log summary results to console"""
        logger.info("=" * 50)
        logger.info("DISCOVERY BASELINE RESULTS SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Overall Score: {baseline_scores.overall_score:.1f}/100")
        logger.info(f"Discovery Score: {baseline_scores.discovery_score.total_score:.1f}/100")
        logger.info(f"Context Score: {baseline_scores.context_score.total_score:.1f}/100")
        logger.info(f"Competitive Score: {baseline_scores.competitive_score.total_score:.1f}/100")
        logger.info(f"Data Quality: {baseline_scores.data_quality_score:.1f}/100")
        logger.info("=" * 50)

# CLI Interface
async def main():
    """Command line interface for the Discovery Baseline Agent"""
    parser = argparse.ArgumentParser(description="Discovery Baseline Agent for GEO Optimization")
    
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Specific query categories to run",
        choices=list(QueryMatrix.QUERY_CATEGORIES.keys())
    )
    
    parser.add_argument(
        "--max-queries",
        type=int,
        help="Maximum number of queries to execute"
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        help="Custom run identifier"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./results",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration and exit"
    )
    
    parser.add_argument(
        "--list-queries",
        action="store_true",
        help="List all available queries and exit"
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_queries:
        print("Available Query Categories:")
        for category, info in QueryMatrix.get_category_info().items():
            print(f"  {category}: {info['description']} ({info['query_count']} queries)")
        
        print(f"\nTotal queries available: {QueryMatrix.get_total_query_count()}")
        return
    
    # Create agent
    config_override = {"OUTPUT_DIR": args.output_dir} if args.output_dir != "./results" else None
    agent = DiscoveryBaselineAgent(config_override)
    
    if args.validate_only:
        config_status = Config.validate()
        print("Configuration Validation:")
        print(f"Valid: {config_status['valid']}")
        if config_status['issues']:
            print("Issues found:")
            for issue in config_status['issues']:
                print(f"  - {issue}")
        print(f"Enabled engines: {config_status['enabled_engines']}/{config_status['total_engines']}")
        return
    
    # Run discovery baseline
    try:
        result = await agent.run_discovery_baseline(
            query_categories=args.categories,
            max_queries=args.max_queries,
            run_id=args.run_id
        )
        
        if result["success"]:
            print("\n" + "="*60)
            print("DISCOVERY BASELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Run ID: {result['run_id']}")
            print(f"Overall Score: {result['baseline_scores'].overall_score:.1f}/100")
            print(f"Files Created: {len(result['files_created'])}")
            print("\nResults exported to:", Config.OUTPUT_DIR)
            print("="*60)
        else:
            print(f"Discovery Baseline failed: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nDiscovery Baseline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

# Entry point for Claude Code orchestration
async def run_discovery_baseline(
    query_categories: Optional[List[str]] = None,
    max_queries: Optional[int] = None,
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """
    Main function called by Claude Code orchestrator
    Returns: Discovery baseline results + scores
    """
    config_override = {"OUTPUT_DIR": output_dir}
    agent = DiscoveryBaselineAgent(config_override)
    
    return await agent.run_discovery_baseline(
        query_categories=query_categories,
        max_queries=max_queries
    )

if __name__ == "__main__":
    asyncio.run(main())