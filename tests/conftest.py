"""
Pytest configuration and fixtures for GEO system testing
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root():
    """Project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_anthropic_key',
        'GOOGLE_AI_API_KEY': 'test_google_key',
        'MAX_CONCURRENT_REQUESTS': '5',
        'REQUEST_TIMEOUT': '30',
        'RETRY_ATTEMPTS': '3'
    }):
        yield

@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing"""
    return {
        'openai': {
            'choices': [{'message': {'content': 'Test OpenAI response'}}],
            'usage': {'total_tokens': 100}
        },
        'anthropic': {
            'content': [{'text': 'Test Anthropic response'}],
            'usage': {'input_tokens': 50, 'output_tokens': 50}
        },
        'google': {
            'text': 'Test Google response',
            'usage_metadata': {'total_token_count': 75}
        }
    }

@pytest.fixture
def sample_brand_config():
    """Sample brand configuration for testing"""
    return {
        'brand': 'TestBrand',
        'website': 'testbrand.com',
        'sector': 'generic',
        'competitors': ['competitor1.com', 'competitor2.com']
    }

class MockAsyncClient:
    """Mock async HTTP client for testing"""
    def __init__(self, response_data=None):
        self.response_data = response_data or {'test': 'response'}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, **kwargs):
        mock_response = Mock()
        mock_response.json.return_value = self.response_data
        mock_response.status_code = 200
        return mock_response

@pytest.fixture
def mock_async_client():
    """Mock async HTTP client"""
    return MockAsyncClient
