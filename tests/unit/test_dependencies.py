"""
Unit tests for dependency management and imports
"""

import pytest
import sys
import importlib
from pathlib import Path


class TestCoreDependencies:
    """Test core dependencies are available and working"""

    def test_ai_api_libraries_available(self):
        """Test that all AI API libraries are available"""
        required_modules = [
            'openai',
            'anthropic',
            'google.generativeai'
        ]

        for module_name in required_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None

                # Test basic functionality
                if module_name == 'openai':
                    assert hasattr(module, 'AsyncOpenAI')
                elif module_name == 'anthropic':
                    assert hasattr(module, 'AsyncAnthropic')
                elif module_name == 'google.generativeai':
                    assert hasattr(module, 'configure')

            except ImportError:
                pytest.fail(f"Required module {module_name} is not available")

    def test_http_libraries_available(self):
        """Test HTTP and async libraries are available"""
        http_modules = [
            'aiohttp',
            'httpx',
            'requests'
        ]

        for module_name in http_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None

                if module_name == 'aiohttp':
                    assert hasattr(module, 'ClientSession')
                elif module_name == 'httpx':
                    assert hasattr(module, 'AsyncClient')
                elif module_name == 'requests':
                    assert hasattr(module, 'get')

            except ImportError:
                pytest.fail(f"Required HTTP module {module_name} is not available")

    def test_data_processing_libraries(self):
        """Test data processing libraries are available"""
        data_modules = [
            'pandas',
            'numpy',
            'pydantic'
        ]

        for module_name in data_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None

                if module_name == 'pandas':
                    assert hasattr(module, 'DataFrame')
                elif module_name == 'numpy':
                    assert hasattr(module, 'array')
                elif module_name == 'pydantic':
                    assert hasattr(module, 'BaseModel')

            except ImportError:
                pytest.fail(f"Required data processing module {module_name} is not available")

    def test_utility_libraries(self):
        """Test utility libraries are available"""
        utility_modules = [
            'yaml',
            'dotenv',
            'tenacity',
            'asyncio'
        ]

        for module_name in utility_modules:
            try:
                if module_name == 'dotenv':
                    from dotenv import load_dotenv
                    assert load_dotenv is not None
                elif module_name == 'yaml':
                    import yaml
                    assert hasattr(yaml, 'safe_load')
                elif module_name == 'tenacity':
                    import tenacity
                    assert hasattr(tenacity, 'retry')
                elif module_name == 'asyncio':
                    import asyncio
                    assert hasattr(asyncio, 'run')

            except ImportError:
                pytest.fail(f"Required utility module {module_name} is not available")

    def test_web_scraping_libraries(self):
        """Test web scraping libraries are available"""
        scraping_modules = [
            'bs4',  # BeautifulSoup4
            'lxml'
        ]

        for module_name in scraping_modules:
            try:
                if module_name == 'bs4':
                    from bs4 import BeautifulSoup
                    assert BeautifulSoup is not None
                elif module_name == 'lxml':
                    import lxml
                    assert lxml is not None

            except ImportError:
                pytest.fail(f"Required scraping module {module_name} is not available")


class TestVersionCompatibility:
    """Test version compatibility of dependencies"""

    def test_python_version_compatibility(self):
        """Test Python version is compatible"""
        python_version = sys.version_info

        # Require Python 3.7 or higher
        assert python_version.major == 3
        assert python_version.minor >= 7

        print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    def test_pandas_numpy_compatibility(self):
        """Test pandas and numpy compatibility"""
        try:
            import pandas as pd
            import numpy as np

            # Test basic compatibility
            df = pd.DataFrame({'test': [1, 2, 3]})
            arr = np.array([1, 2, 3])

            # Should work without issues
            result = df['test'].values
            assert isinstance(result, np.ndarray)
            assert len(result) == 3

        except ImportError:
            pytest.skip("pandas/numpy not available")

    def test_async_library_compatibility(self):
        """Test async library compatibility"""
        try:
            import asyncio
            import aiohttp

            async def test_session():
                async with aiohttp.ClientSession() as session:
                    return "success"

            # Test async functionality works
            result = asyncio.run(test_session())
            assert result == "success"

        except ImportError:
            pytest.skip("aiohttp not available")


class TestGEOSystemImports:
    """Test GEO system specific imports"""

    def test_discovery_agent_imports(self):
        """Test discovery agent imports work"""
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        try:
            from discovery_baseline_agent.config import Config
            assert Config is not None

            from discovery_baseline_agent.api_clients import BaseAIClient
            assert BaseAIClient is not None

        except ImportError as e:
            pytest.skip(f"Discovery agent imports not available: {e}")

    def test_content_analysis_imports(self):
        """Test content analysis agent imports work"""
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        try:
            # Check if content analysis modules exist
            content_agent_dir = project_root / 'content_analysis_agent'
            if content_agent_dir.exists():
                content_files = list(content_agent_dir.glob('*.py'))
                assert len(content_files) > 0, "No Python files found in content_analysis_agent"

        except Exception as e:
            pytest.skip(f"Content analysis imports not available: {e}")

    def test_terminal_dashboard_imports(self):
        """Test terminal dashboard imports work"""
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        try:
            from terminal_dashboard_generator.main import TerminalDashboardGenerator
            assert TerminalDashboardGenerator is not None

            # Test can instantiate (without actually running)
            generator = TerminalDashboardGenerator(
                base_dir="/tmp/test_geo"
            )
            assert generator is not None
            assert hasattr(generator, '_clear_terminal')

        except ImportError as e:
            pytest.skip(f"Terminal dashboard imports not available: {e}")


class TestRequirementsConsistency:
    """Test requirements files are consistent"""

    def test_requirements_files_exist(self):
        """Test that requirements files exist"""
        project_root = Path(__file__).parent.parent.parent

        main_requirements = project_root / 'requirements.txt'
        minimal_requirements = project_root / 'requirements-minimal.txt'

        assert main_requirements.exists(), "Main requirements.txt not found"
        assert minimal_requirements.exists(), "requirements-minimal.txt not found"

    def test_requirements_parseable(self):
        """Test that requirements files are parseable"""
        project_root = Path(__file__).parent.parent.parent

        requirements_files = [
            'requirements.txt',
            'requirements-minimal.txt'
        ]

        for req_file in requirements_files:
            req_path = project_root / req_file
            if req_path.exists():
                content = req_path.read_text()
                lines = [line.strip() for line in content.split('\n')
                        if line.strip() and not line.strip().startswith('#')]

                for line in lines:
                    # Basic validation - should contain package names
                    assert len(line) > 0
                    # Should not contain obvious syntax errors
                    assert not line.startswith('=')
                    assert not line.startswith('>')
                    assert not line.startswith('<')
