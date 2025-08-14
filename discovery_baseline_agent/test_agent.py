#!/usr/bin/env python3
"""
Test script for Discovery Baseline Agent

This script tests the core functionality of the Discovery Baseline Agent
without requiring API keys or making actual API calls.
"""

import asyncio
import json
import sys
from typing import Dict, List, Any
from datetime import datetime, timezone

from query_matrix import QueryMatrix
from response_analyzer import ResponseAnalysis, Citation, BatchAnalyzer
from scoring_engine import BaselineScoreCalculator
from export_manager import ExportManager

def create_mock_response_data() -> List[Dict[str, Any]]:
    """Create mock response data for testing"""
    mock_responses = [
        {
            "engine": "openai",
            "model": "gpt-4",
            "query": "best mineral sunscreen 2024",
            "response": "For the best mineral sunscreens in 2024, I recommend EltaMD UV Clear which contains zinc oxide and provides excellent protection. Blue Lizard Australian Sunscreen is another top choice with titanium dioxide. For a budget option, consider CeraVe Mineral Sunscreen which offers broad spectrum protection.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        },
        {
            "engine": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "query": "mineral sunscreen for sensitive skin",
            "response": "For sensitive skin, I highly recommend Neutrogena Sensitive Skin Mineral Sunscreen with zinc oxide. It's gentle and non-irritating. Another excellent option is La Roche Posay Anthelios Mineral Sunscreen, which is dermatologist-tested and suitable for even the most sensitive skin types.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        },
        {
            "engine": "google",
            "model": "gemini-1.5-pro",
            "query": "best reef safe sunscreen",
            "response": "The best reef-safe sunscreens use mineral filters like zinc oxide and titanium dioxide. Top recommendations include Badger Classic Unscented Sunscreen, which is completely reef-safe and biodegradable. Stream2Sea Sunscreen is another excellent choice, specifically formulated to be safe for marine life.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        },
        {
            "engine": "openai",
            "model": "gpt-3.5-turbo",
            "query": "mineral vs chemical sunscreen",
            "response": "Mineral sunscreens use zinc oxide or titanium dioxide to physically block UV rays, while chemical sunscreens absorb UV radiation. Mineral options like Supergoop! Zincscreen and Drunk Elephant D-Bronzi provide immediate protection and are generally better for sensitive skin.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        },
        {
            "engine": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "query": "failed query test",
            "response": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": "API rate limit exceeded"
        }
    ]
    
    return mock_responses

def test_query_matrix():
    """Test the query matrix functionality"""
    print("Testing Query Matrix...")
    
    # Test query retrieval
    all_queries = QueryMatrix.get_all_queries()
    print(f"Total queries: {len(all_queries)}")
    
    # Test category info
    category_info = QueryMatrix.get_category_info()
    print(f"Categories: {len(category_info)}")
    
    for category, info in category_info.items():
        print(f"  {category}: {info['query_count']} queries")
    
    # Test validation
    validation = QueryMatrix.validate_queries()
    print(f"Validation: {validation['valid']}")
    print(f"Duplicates: {validation['duplicate_count']}")
    
    assert len(all_queries) >= 50, "Should have at least 50 queries"
    assert validation['valid'], "Query matrix should be valid"
    
    print("✓ Query Matrix tests passed\n")

def test_response_analyzer():
    """Test the response analyzer functionality"""
    print("Testing Response Analyzer...")
    
    # Create mock responses
    mock_responses = create_mock_response_data()
    
    # Analyze responses
    batch_analyzer = BatchAnalyzer()
    analyses = batch_analyzer.analyze_batch(mock_responses)
    
    print(f"Analyzed {len(analyses)} responses")
    
    # Check analysis results
    successful_analyses = [a for a in analyses if a.response_text]
    print(f"Successful analyses: {len(successful_analyses)}")
    
    # Check citations
    total_citations = sum(len(a.citations) for a in analyses)
    print(f"Total citations found: {total_citations}")
    
    # Check competitor detection
    competitors = set()
    for analysis in analyses:
        competitors.update(analysis.competitors_mentioned)
    print(f"Unique competitors found: {len(competitors)}")
    print(f"Competitors: {list(competitors)[:5]}...")  # Show first 5
    
    assert len(analyses) == len(mock_responses), "Should analyze all responses"
    assert total_citations > 0, "Should find some citations"
    
    print("✓ Response Analyzer tests passed\n")
    
    return analyses

def test_scoring_engine(analyses: List[ResponseAnalysis]):
    """Test the scoring engine functionality"""
    print("Testing Scoring Engine...")
    
    # Calculate baseline scores
    score_calculator = BaselineScoreCalculator()
    baseline_scores = score_calculator.calculate_baseline_scores(analyses)
    
    print(f"Overall Score: {baseline_scores.overall_score:.1f}/100")
    print(f"Discovery Score: {baseline_scores.discovery_score.total_score:.1f}/100")
    print(f"Context Score: {baseline_scores.context_score.total_score:.1f}/100")
    print(f"Competitive Score: {baseline_scores.competitive_score.total_score:.1f}/100")
    print(f"Data Quality: {baseline_scores.data_quality_score:.1f}/100")
    
    # Generate insights
    insights = score_calculator.generate_insights(baseline_scores)
    print(f"Generated {len(insights)} insight categories")
    
    assert 0 <= baseline_scores.overall_score <= 100, "Overall score should be 0-100"
    assert 0 <= baseline_scores.data_quality_score <= 100, "Data quality should be 0-100"
    assert insights is not None, "Should generate insights"
    
    print("✓ Scoring Engine tests passed\n")
    
    return baseline_scores, insights

def test_export_manager(baseline_scores, analyses: List[ResponseAnalysis], insights: Dict[str, Any]):
    """Test the export manager functionality"""
    print("Testing Export Manager...")
    
    # Create export manager
    export_manager = ExportManager("./test_results")
    
    # Test metadata
    metadata = {
        "test_run": True,
        "total_queries": len(analyses),
        "test_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Export all data
    try:
        files_created = export_manager.export_all(
            baseline_scores, analyses, insights, metadata, "test_run"
        )
        
        print(f"Created {len(files_created)} files:")
        for file_type, filepath in files_created.items():
            print(f"  {file_type}: {filepath}")
        
        # Verify files exist
        import os
        for filepath in files_created.values():
            assert os.path.exists(filepath), f"File should exist: {filepath}"
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("✓ Export Manager tests passed\n")
    
    return files_created

async def run_integration_test():
    """Run a complete integration test"""
    print("Running Integration Test...")
    print("=" * 50)
    
    try:
        # Test all components
        test_query_matrix()
        analyses = test_response_analyzer()
        baseline_scores, insights = test_scoring_engine(analyses)
        files_created = test_export_manager(baseline_scores, analyses, insights)
        
        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)
        
        # Print summary
        print("\nTEST SUMMARY:")
        print(f"Queries tested: {QueryMatrix.get_total_query_count()}")
        print(f"Responses analyzed: {len(analyses)}")
        print(f"Overall test score: {baseline_scores.overall_score:.1f}/100")
        print(f"Files created: {len(files_created)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration validation"""
    print("Testing Configuration...")
    
    from config import Config
    
    # Test configuration validation
    config_status = Config.validate()
    print(f"Configuration valid: {config_status['valid']}")
    print(f"Enabled engines: {config_status['enabled_engines']}/{config_status['total_engines']}")
    
    if config_status['issues']:
        print("Configuration issues (expected without API keys):")
        for issue in config_status['issues']:
            print(f"  - {issue}")
    
    print("✓ Configuration tests completed\n")

async def main():
    """Main test function"""
    print("Discovery Baseline Agent - Test Suite")
    print("=" * 60)
    
    # Test configuration (will show missing API keys - that's expected)
    test_configuration()
    
    # Run integration test with mock data
    success = await run_integration_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python main.py --validate-only")
        print("3. Run: python main.py --max-queries 5")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())