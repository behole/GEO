#!/usr/bin/env python3
"""
GEO System Test Runner
Comprehensive test execution with security focus
"""

import subprocess
import sys
import argparse
from pathlib import Path
import os


def run_security_tests():
    """Run security-focused tests"""
    print("🔒 Running Security Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/security/',
        '-v',
        '--tb=short',
        '-m', 'security or not slow'
    ]
    return subprocess.run(cmd)


def run_unit_tests():
    """Run fast unit tests"""
    print("⚡ Running Unit Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/unit/',
        '-v',
        '--tb=short',
        '-m', 'unit or not slow'
    ]
    return subprocess.run(cmd)


def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running Integration Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/integration/',
        '-v',
        '--tb=short',
        '-m', 'integration or not api'
    ]
    return subprocess.run(cmd)


def run_all_tests():
    """Run complete test suite"""
    print("🧪 Running Complete Test Suite...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short'
    ]
    return subprocess.run(cmd)


def run_quick_tests():
    """Run quick tests only (no slow or API tests)"""
    print("🚀 Running Quick Test Suite...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '-m', 'not slow and not api'
    ]
    return subprocess.run(cmd)


def check_test_environment():
    """Check if test environment is set up correctly"""
    print("🔍 Checking Test Environment...")

    # Check pytest is available
    try:
        import pytest
        print(f"✅ pytest available: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not available - run: pip install pytest pytest-asyncio")
        return False

    # Check core dependencies
    required_modules = ['aiohttp', 'pandas', 'yaml']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            print(f"❌ {module} missing")
            missing_modules.append(module)

    if missing_modules:
        print(f"Missing modules: {missing_modules}")
        print("Run: pip install -r requirements-minimal.txt")
        return False

    # Check test directories exist
    test_dirs = ['tests/unit', 'tests/integration', 'tests/security']
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir} exists")
        else:
            print(f"❌ {test_dir} missing")
            return False

    print("🎯 Test environment ready!")
    return True


def main():
    parser = argparse.ArgumentParser(description='GEO System Test Runner')
    parser.add_argument(
        'suite',
        choices=['all', 'quick', 'security', 'unit', 'integration', 'check'],
        help='Test suite to run'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run with coverage reporting'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Extra verbose output'
    )

    args = parser.parse_args()

    # Set environment for testing
    os.environ['TESTING'] = '1'

    if args.suite == 'check':
        success = check_test_environment()
        sys.exit(0 if success else 1)

    # Check environment first
    if not check_test_environment():
        print("❌ Test environment not ready")
        sys.exit(1)

    # Run selected test suite
    if args.suite == 'security':
        result = run_security_tests()
    elif args.suite == 'unit':
        result = run_unit_tests()
    elif args.suite == 'integration':
        result = run_integration_tests()
    elif args.suite == 'quick':
        result = run_quick_tests()
    elif args.suite == 'all':
        result = run_all_tests()
    else:
        print(f"Unknown test suite: {args.suite}")
        sys.exit(1)

    # Report results
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
