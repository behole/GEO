"""
Integration tests for AI API clients
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAPIClientIntegration:
    """Integration tests for AI API clients"""

    @pytest.mark.asyncio
    async def test_openai_client_integration(self, mock_env_vars, mock_api_responses):
        """Test OpenAI client integration"""
        try:
            from discovery_baseline_agent.api_clients import OpenAIClient

            with patch('openai.AsyncOpenAI') as mock_openai:
                # Mock the client
                mock_client_instance = AsyncMock()
                mock_openai.return_value = mock_client_instance

                # Mock the completion response
                mock_response = Mock()
                mock_response.choices = [
                    Mock(message=Mock(content="Test OpenAI response"))
                ]
                mock_response.usage = Mock()
                mock_response.usage.prompt_tokens = 50
                mock_response.usage.completion_tokens = 50
                mock_response.usage.total_tokens = 100

                mock_client_instance.chat.completions.create.return_value = mock_response

                # Test client
                client = OpenAIClient(api_key="test_key", model="gpt-4")
                result = await client.query("Test prompt", "Test query")

                # Verify result structure
                assert 'response' in result
                assert 'usage' in result
                assert 'engine' in result
                assert result['engine'] == 'openai'
                assert result['response'] == "Test OpenAI response"
                assert result['usage']['total_tokens'] == 100

        except ImportError:
            pytest.skip("OpenAI client module not available")

    @pytest.mark.asyncio
    async def test_anthropic_client_integration(self, mock_env_vars, mock_api_responses):
        """Test Anthropic client integration"""
        try:
            from discovery_baseline_agent.api_clients import AnthropicClient

            with patch('anthropic.AsyncAnthropic') as mock_anthropic:
                # Mock the client
                mock_client_instance = AsyncMock()
                mock_anthropic.return_value = mock_client_instance

                # Mock the message response
                mock_response = Mock()
                mock_response.content = [Mock(text="Test Anthropic response")]
                mock_response.usage = Mock()
                mock_response.usage.input_tokens = 50
                mock_response.usage.output_tokens = 50

                mock_client_instance.messages.create.return_value = mock_response

                # Test client
                client = AnthropicClient(api_key="test_key", model="claude-3-sonnet")
                result = await client.query("Test prompt", "Test query")

                # Verify result structure
                assert 'response' in result
                assert 'usage' in result
                assert 'engine' in result
                assert result['engine'] == 'anthropic'
                assert result['response'] == "Test Anthropic response"
                assert result['usage']['input_tokens'] == 50
                assert result['usage']['output_tokens'] == 50

        except ImportError:
            pytest.skip("Anthropic client module not available")

    @pytest.mark.asyncio
    async def test_google_client_integration(self, mock_env_vars, mock_api_responses):
        """Test Google AI client integration"""
        try:
            from discovery_baseline_agent.api_clients import GoogleAIClient

            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model:
                    # Mock the model instance
                    mock_model_instance = Mock()
                    mock_model.return_value = mock_model_instance

                    # Mock the response
                    mock_response = Mock()
                    mock_response.text = "Test Google response"
                    mock_response.usage_metadata = Mock()
                    mock_response.usage_metadata.prompt_token_count = 25
                    mock_response.usage_metadata.candidates_token_count = 50

                    mock_model_instance.generate_content.return_value = mock_response

                    # Test client
                    client = GoogleAIClient(api_key="test_key", model="gemini-pro")
                    result = await client.query("Test prompt", "Test query")

                    # Verify result structure
                    assert 'response' in result
                    assert 'usage' in result
                    assert 'engine' in result
                    assert result['engine'] == 'google'
                    assert result['response'] == "Test Google response"
                    assert result['usage']['prompt_tokens'] == 25
                    assert result['usage']['completion_tokens'] == 50

        except ImportError:
            pytest.skip("Google AI client module not available")

    @pytest.mark.asyncio
    async def test_client_error_handling(self, mock_env_vars):
        """Test client error handling"""
        try:
            from discovery_baseline_agent.api_clients import OpenAIClient

            with patch('openai.AsyncOpenAI') as mock_openai:
                mock_client_instance = AsyncMock()
                mock_openai.return_value = mock_client_instance

                # Simulate API error
                mock_client_instance.chat.completions.create.side_effect = Exception("API Error")

                client = OpenAIClient(api_key="test_key", model="gpt-4")

                # Should handle error gracefully
                result = await client.query("Test prompt", "Test query")

                # Should return error result instead of raising
                assert 'success' in result
                assert result['success'] is False
                assert 'error' in result

        except ImportError:
            pytest.skip("OpenAI client module not available")

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, mock_env_vars):
        """Test concurrent API calls work properly"""
        try:
            from discovery_baseline_agent.api_clients import OpenAIClient

            with patch('openai.AsyncOpenAI') as mock_openai:
                mock_client_instance = AsyncMock()
                mock_openai.return_value = mock_client_instance

                # Mock response
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="Concurrent response"))]
                mock_response.usage.total_tokens = 50

                mock_client_instance.chat.completions.create.return_value = mock_response

                client = OpenAIClient(api_key="test_key", model="gpt-4")

                # Test concurrent calls
                tasks = [
                    client.query("Prompt 1", "Query 1"),
                    client.query("Prompt 2", "Query 2"),
                    client.query("Prompt 3", "Query 3")
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # All should succeed
                for result in results:
                    assert not isinstance(result, Exception)
                    assert 'response' in result
                    assert result['response'] == "Concurrent response"

        except ImportError:
            pytest.skip("OpenAI client module not available")


class TestAPIClientManager:
    """Test API client manager functionality"""

    @pytest.mark.asyncio
    async def test_client_factory(self, mock_env_vars):
        """Test client factory creates correct clients"""
        try:
            from discovery_baseline_agent.api_clients import create_ai_clients

            with patch('discovery_baseline_agent.api_clients.OpenAIClient') as mock_openai:
                with patch('discovery_baseline_agent.api_clients.AnthropicClient') as mock_anthropic:
                    with patch('discovery_baseline_agent.api_clients.GoogleAIClient') as mock_google:

                        # Mock client instances
                        mock_openai.return_value = Mock()
                        mock_anthropic.return_value = Mock()
                        mock_google.return_value = Mock()

                        clients = create_ai_clients()

                        # Should create all available clients
                        assert len(clients) > 0

                        # Verify clients were instantiated
                        for client in clients:
                            assert hasattr(client, 'query')
                            assert hasattr(client, 'get_engine_name')

        except ImportError:
            pytest.skip("API client manager not available")

    def test_client_configuration(self, mock_env_vars):
        """Test client configuration loading"""
        try:
            from discovery_baseline_agent.config import Config

            # Test configuration values
            assert Config.MAX_CONCURRENT_REQUESTS == 5
            assert Config.REQUEST_TIMEOUT == 30
            assert Config.RETRY_ATTEMPTS == 3

            # Test engine configuration
            engines = Config.AI_ENGINES
            assert isinstance(engines, dict)

            for engine_name, engine_config in engines.items():
                assert 'enabled' in engine_config
                assert 'models' in engine_config

        except ImportError:
            pytest.skip("Config module not available")
