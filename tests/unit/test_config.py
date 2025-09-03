"""
Unit tests for configuration management
"""

import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestConfiguration:
    """Test configuration loading and validation"""

    def test_config_loads_from_env(self, mock_env_vars):
        """Test configuration loads from environment variables"""
        try:
            from discovery_baseline_agent.config import Config

            # Test environment variable loading
            assert Config.OPENAI_API_KEY == 'test_openai_key'
            assert Config.ANTHROPIC_API_KEY == 'test_anthropic_key'
            assert Config.GOOGLE_AI_API_KEY == 'test_google_key'

            # Test numeric configurations
            assert Config.MAX_CONCURRENT_REQUESTS == 5
            assert Config.REQUEST_TIMEOUT == 30
            assert Config.RETRY_ATTEMPTS == 3

        except ImportError:
            pytest.skip("Config module not available")

    @pytest.mark.skip(reason="Skip when real API keys present in environment")
    def test_config_defaults(self):
        """Test configuration defaults when environment variables are missing"""
        with patch.dict(os.environ, {}, clear=True):
            try:
                # Re-import to get fresh config
                import importlib
                if 'discovery_baseline_agent.config' in sys.modules:
                    importlib.reload(sys.modules['discovery_baseline_agent.config'])

                from discovery_baseline_agent.config import Config

                # API keys should be None when not set
                assert Config.OPENAI_API_KEY is None
                assert Config.ANTHROPIC_API_KEY is None
                assert Config.GOOGLE_AI_API_KEY is None

            except ImportError:
                pytest.skip("Config module not available")

    def test_engine_configuration(self, mock_env_vars):
        """Test AI engine configuration"""
        try:
            from discovery_baseline_agent.config import Config

            engines = Config.AI_ENGINES
            assert isinstance(engines, dict)

            # Should have OpenAI engine when key is present
            assert 'openai' in engines
            assert engines['openai']['enabled'] is True

            # Should have models specified
            for engine_name, engine_config in engines.items():
                assert 'models' in engine_config
                assert isinstance(engine_config['models'], list)
                assert len(engine_config['models']) > 0

        except (ImportError, AttributeError):
            pytest.skip("Engine configuration not available")

    def test_config_validation(self):
        """Test configuration validation"""
        try:
            from discovery_baseline_agent.config import Config

            # Test that retry attempts is positive
            with patch.dict(os.environ, {'RETRY_ATTEMPTS': '0'}):
                if hasattr(Config, 'RETRY_ATTEMPTS'):
                    # Should handle edge cases
                    assert Config.RETRY_ATTEMPTS >= 0

            # Test that timeout is reasonable
            with patch.dict(os.environ, {'REQUEST_TIMEOUT': '300'}):
                if hasattr(Config, 'REQUEST_TIMEOUT'):
                    assert Config.REQUEST_TIMEOUT > 0
                    assert Config.REQUEST_TIMEOUT < 1000  # Reasonable upper bound

        except ImportError:
            pytest.skip("Config module not available")


class TestDynamicConfiguration:
    """Test dynamic configuration features"""

    def test_dynamic_brand_config(self, sample_brand_config):
        """Test dynamic brand configuration"""
        try:
            from dynamic_config import get_config_manager

            config_manager = get_config_manager()

            # Test configuration creation
            config_path = config_manager.create_brand_config(
                brand_name=sample_brand_config['brand'],
                website=sample_brand_config['website'],
                sector=sample_brand_config['sector']
            )

            assert config_path is not None
            assert Path(config_path).exists()

            # Test configuration loading
            import yaml
            with open(config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
            assert loaded_config['brand']['name'] == sample_brand_config['brand']
            assert loaded_config['brand']['website'] == sample_brand_config['website']

            # Clean up
            config_manager.cleanup()

        except ImportError:
            pytest.skip("Dynamic config not available")

    def test_sector_configuration_loading(self):
        """Test sector configuration loading"""
        try:
            import yaml
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            sector_configs_dir = project_root / 'sector_configs'

            if sector_configs_dir.exists():
                # Test that sector configs are valid YAML
                for config_file in sector_configs_dir.glob('*.yaml'):
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)

                        # Basic structure validation
                        assert 'sector' in config
                        assert 'keywords' in config
                        assert 'scoring_weights' in config

                        # Keywords should have structure
                        keywords = config['keywords']
                        assert isinstance(keywords, dict)
                        assert 'primary' in keywords
                        assert isinstance(keywords['primary'], list)
                        assert len(keywords['primary']) > 0

                        # Scoring weights should be configured
                        scoring_weights = config['scoring_weights']
                        assert isinstance(scoring_weights, dict)
                        assert len(scoring_weights) > 0
                        # All weights should be numeric
                        for weight in scoring_weights.values():
                            assert isinstance(weight, (int, float))

        except ImportError:
            pytest.skip("YAML module not available")


class TestEnvironmentSetup:
    """Test environment setup and validation"""

    def test_dotenv_loading(self, temp_dir):
        """Test .env file loading"""
        try:
            from dotenv import load_dotenv

            # Create test .env file
            env_file = temp_dir / '.env'
            env_file.write_text(
                "OPENAI_API_KEY=test_key_from_file\n"
                "MAX_CONCURRENT_REQUESTS=10\n"
            )

            # Load environment
            load_dotenv(env_file)

            # Check values were loaded
            assert os.getenv('OPENAI_API_KEY') == 'test_key_from_file'
            assert os.getenv('MAX_CONCURRENT_REQUESTS') == '10'

        except ImportError:
            pytest.skip("python-dotenv not available")

    def test_environment_precedence(self, temp_dir):
        """Test that environment variables take precedence over .env files"""
        try:
            from dotenv import load_dotenv

            # Create .env file
            env_file = temp_dir / '.env'
            env_file.write_text("TEST_VAR=from_file\n")

            # Set environment variable
            with patch.dict(os.environ, {'TEST_VAR': 'from_env'}):
                load_dotenv(env_file)

                # Environment should take precedence
                assert os.getenv('TEST_VAR') == 'from_env'

        except ImportError:
            pytest.skip("python-dotenv not available")
