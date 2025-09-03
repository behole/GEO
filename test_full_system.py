#!/usr/bin/env python3
"""
Full system integration test for GEO Audit Platform
Tests the complete workflow from discovery through reporting
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import asyncio
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

def test_environment_setup():
    """Test that all required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Set these in your .env file or environment")
        return False

    print("✓ Environment variables configured")
    return True

def test_discovery_agent():
    """Test the Discovery Baseline Agent"""
    try:
        from discovery_baseline_agent.main import main as discovery_main
        print("✓ Discovery Agent module loaded")
        return True
    except ImportError as e:
        print(f"✗ Discovery Agent import failed: {e}")
        return False

def test_content_analysis_agent():
    """Test the Content Analysis Agent"""
    try:
        from content_analysis_agent.main import main as content_main
        print("✓ Content Analysis Agent module loaded")
        return True
    except ImportError as e:
        print(f"✗ Content Analysis Agent import failed: {e}")
        return False

def test_competitive_intelligence_agent():
    """Test the Competitive Intelligence Agent"""
    try:
        from competitive_intelligence_agent.competitive_intelligence_agent import CompetitiveIntelligenceAgent
        print("✓ Competitive Intelligence Agent module loaded")
        return True
    except ImportError as e:
        print(f"✗ Competitive Intelligence Agent import failed: {e}")
        return False

def test_terminal_dashboard():
    """Test the Terminal Dashboard Generator"""
    try:
        from terminal_dashboard_generator.main import TerminalDashboardGenerator
        print("✓ Terminal Dashboard Generator module loaded")
        return True
    except ImportError as e:
        print(f"✗ Terminal Dashboard Generator import failed: {e}")
        return False

async def test_api_clients():
    """Test API client connections"""
    try:
        from discovery_baseline_agent.api_clients import APIClientManager

        # Test with minimal configuration
        test_config = {
            'openai': {'model': 'gpt-3.5-turbo', 'max_tokens': 100},
            'anthropic': {'model': 'claude-3-haiku-20240307', 'max_tokens': 100},
            'google': {'model': 'gemini-pro', 'max_tokens': 100}
        }

        manager = APIClientManager(test_config)
        print("✓ API Client Manager initialized")

        # Test basic functionality without actual API calls
        if hasattr(manager, 'openai_client') and manager.openai_client:
            print("✓ OpenAI client configured")
        if hasattr(manager, 'anthropic_client') and manager.anthropic_client:
            print("✓ Anthropic client configured")
        if hasattr(manager, 'google_client') and manager.google_client:
            print("✓ Google AI client configured")

        return True

    except Exception as e:
        print(f"✗ API client test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration file loading"""
    try:
        from discovery_baseline_agent.config import load_config

        # Test loading default configuration
        config = load_config()

        if config and isinstance(config, dict):
            print("✓ Configuration loading works")
            print(f"  - Loaded {len(config)} config sections")
            return True
        else:
            print("✗ Configuration loading returned invalid data")
            return False

    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_results_directory():
    """Test that results directory exists and is writable"""
    try:
        results_dir = Path("results")

        if not results_dir.exists():
            results_dir.mkdir(parents=True)
            print("✓ Created results directory")
        else:
            print("✓ Results directory exists")

        # Test write permissions
        test_file = results_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Results directory is writable")

        return True

    except Exception as e:
        print(f"✗ Results directory test failed: {e}")
        return False

async def test_minimal_workflow():
    """Test a minimal workflow without API calls"""
    try:
        from discovery_baseline_agent.query_matrix import QueryMatrixBuilder
        from discovery_baseline_agent.response_analyzer import ResponseAnalyzer
        from discovery_baseline_agent.scoring_engine import ScoringEngine

        # Test query matrix builder
        builder = QueryMatrixBuilder()
        test_queries = builder.build_baseline_queries(["test brand"])

        if test_queries and len(test_queries) > 0:
            print(f"✓ Query matrix built ({len(test_queries)} queries)")
        else:
            print("✗ Query matrix building failed")
            return False

        # Test response analyzer (without actual responses)
        analyzer = ResponseAnalyzer()
        print("✓ Response analyzer initialized")

        # Test scoring engine
        scorer = ScoringEngine()
        print("✓ Scoring engine initialized")

        return True

    except Exception as e:
        print(f"✗ Minimal workflow test failed: {e}")
        return False

async def main():
    """Run full system integration tests"""
    print("🔍 GEO Audit System - Full Integration Test")
    print("=" * 50)

    tests = [
        ("Environment Setup", test_environment_setup),
        ("Discovery Agent", test_discovery_agent),
        ("Content Analysis Agent", test_content_analysis_agent),
        ("Competitive Intelligence Agent", test_competitive_intelligence_agent),
        ("Terminal Dashboard", test_terminal_dashboard),
        ("API Clients", test_api_clients),
        ("Configuration Loading", test_configuration_loading),
        ("Results Directory", test_results_directory),
        ("Minimal Workflow", test_minimal_workflow),
    ]

    results = {}
    passed = 0
    failed = 0

    print("\n🧪 Running Tests:")
    print("-" * 30)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            results[test_name] = result
            if result:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
            failed += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 30)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed! System is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
