#!/usr/bin/env python3
"""
Simplified full system integration test for GEO Audit Platform
Tests core functionality with actual class names and imports
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

def test_environment():
    """Check environment setup"""
    print("Environment Setup:")

    # Check .env files
    env_files = ['.env', 'discovery_baseline_agent/.env', 'content_analysis_agent/.env', 'competitive_intelligence_agent/.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"  ✓ Found {env_file}")
        else:
            print(f"  ⚠️ Missing {env_file}")

    # Check API keys (without showing values)
    api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    configured = 0
    for key in api_keys:
        if os.getenv(key):
            print(f"  ✓ {key} configured")
            configured += 1
        else:
            print(f"  ⚠️ {key} not set")

    return configured > 0

def test_core_modules():
    """Test core module imports"""
    print("\nCore Module Imports:")

    modules_to_test = [
        ("Discovery Agent Config", "discovery_baseline_agent.config", "Config"),
        ("Discovery Agent API Clients", "discovery_baseline_agent.api_clients", "OpenAIClient"),
        ("Discovery Agent Query Matrix", "discovery_baseline_agent.query_matrix", "QueryMatrix"),
        ("Content Analysis Main", "content_analysis_agent.main", None),
        ("Competitive Intelligence", "competitive_intelligence_agent.competitive_intelligence_agent", "CompetitiveIntelligenceAgent"),
        ("Terminal Dashboard", "terminal_dashboard_generator.main", "TerminalDashboardGenerator"),
    ]

    passed = 0
    for name, module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name] if class_name else [''])
            if class_name:
                getattr(module, class_name)
            print(f"  ✓ {name}")
            passed += 1
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
        except AttributeError as e:
            print(f"  ✗ {name}: Missing {class_name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    return passed

def test_configuration():
    """Test configuration loading"""
    print("\nConfiguration Test:")

    try:
        from discovery_baseline_agent.config import Config

        print(f"  ✓ Config class loaded")
        print(f"  - Max concurrent requests: {Config.MAX_CONCURRENT_REQUESTS}")
        print(f"  - Request timeout: {Config.REQUEST_TIMEOUT}")
        print(f"  - Output dir: {Config.OUTPUT_DIR}")

        # Test validation
        validation = Config.validate()
        print(f"  - Config validation: {len(validation.get('issues', []))} issues")

        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False

def test_query_matrix():
    """Test query matrix functionality"""
    print("\nQuery Matrix Test:")

    try:
        from discovery_baseline_agent.query_matrix import QueryMatrix

        matrix = QueryMatrix()
        print(f"  ✓ QueryMatrix instantiated")

        # Test basic properties
        if hasattr(matrix, 'BASE_PROMPT'):
            print(f"  ✓ Base prompt defined")

        if hasattr(matrix, 'QUERY_CATEGORIES'):
            categories = len(matrix.QUERY_CATEGORIES)
            print(f"  ✓ Query categories: {categories}")

            total_queries = sum(len(cat.get('queries', [])) for cat in matrix.QUERY_CATEGORIES.values())
            print(f"  ✓ Total queries: {total_queries}")

        return True
    except Exception as e:
        print(f"  ✗ Query matrix test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and permissions"""
    print("\nFile Structure Test:")

    # Check main directories
    required_dirs = ['discovery_baseline_agent', 'content_analysis_agent', 'competitive_intelligence_agent', 'terminal_dashboard_generator', 'results']

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {dir_name}/ directory exists")
        else:
            print(f"  ✗ {dir_name}/ directory missing")

    # Test results directory writability
    results_dir = Path("results")
    try:
        if not results_dir.exists():
            results_dir.mkdir(parents=True)

        test_file = results_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print(f"  ✓ Results directory writable")
        return True
    except Exception as e:
        print(f"  ✗ Results directory test failed: {e}")
        return False

def test_dependencies():
    """Test critical dependencies"""
    print("\nDependency Test:")

    critical_deps = [
        'openai', 'anthropic', 'google.generativeai',
        'pandas', 'numpy', 'requests', 'aiohttp',
        'yaml', 'json', 'asyncio'
    ]

    passed = 0
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
            passed += 1
        except ImportError:
            print(f"  ✗ {dep} missing")

    return passed

def main():
    """Run simplified system tests"""
    print("🔍 GEO Audit System - Simplified Integration Test")
    print("=" * 55)

    # Run tests
    tests = [
        ("Environment", test_environment),
        ("Core Modules", test_core_modules),
        ("Configuration", test_configuration),
        ("Query Matrix", test_query_matrix),
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
    ]

    total_passed = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        try:
            result = test_func()
            if isinstance(result, bool):
                if result:
                    total_passed += 1
                    print(f"  → {test_name}: PASSED")
                else:
                    print(f"  → {test_name}: FAILED")
            elif isinstance(result, int):
                if result > 0:
                    total_passed += 1
                    print(f"  → {test_name}: PASSED ({result} items)")
                else:
                    print(f"  → {test_name}: FAILED")
        except Exception as e:
            print(f"  → {test_name}: ERROR - {e}")

    # Final summary
    print("\n" + "=" * 55)
    print("📊 System Test Summary")
    print("-" * 25)
    print(f"Tests Passed: {total_passed}/{total_tests}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")

    if total_passed == total_tests:
        print("\n🎉 System ready for operation!")
        return 0
    elif total_passed >= total_tests * 0.7:  # 70% threshold
        print("\n⚠️ System mostly operational, but some issues detected")
        return 1
    else:
        print("\n❌ System has significant issues - requires attention")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
