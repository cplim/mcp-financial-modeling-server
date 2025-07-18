"""Test cases for configuration loader."""

import json
import tempfile
from pathlib import Path

from mcp.types import Prompt, Resource

from mcp_financial_modeling_prep.config.loader import ConfigLoader


class TestConfigLoader:
    """Test the configuration loader."""

    def test_config_loader_initialization(self):
        """Test that config loader can be initialized."""
        loader = ConfigLoader()
        assert loader.config_dir is not None

    def test_config_loader_with_custom_directory(self):
        """Test that config loader can be initialized with custom directory."""
        custom_dir = Path("/tmp/test_config")
        loader = ConfigLoader(config_dir=custom_dir)
        assert loader.config_dir == custom_dir

    def test_load_resources_with_valid_config(self):
        """Test loading resources from valid configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create test resources config
            resources_config = {
                "resources": [
                    {
                        "uri": "financial://test/resource1",
                        "name": "Test Resource 1",
                        "description": "Test resource description",
                        "mimeType": "text/plain",
                    },
                    {
                        "uri": "financial://test/resource2",
                        "name": "Test Resource 2",
                        "description": "Another test resource",
                        "mimeType": "application/json",
                    },
                ]
            }

            with open(config_dir / "resources.json", "w") as f:
                json.dump(resources_config, f)

            loader = ConfigLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert len(resources) == 2
            assert all(isinstance(r, Resource) for r in resources)
            assert resources[0].name == "Test Resource 1"
            assert str(resources[0].uri) == "financial://test/resource1"
            assert resources[1].mimeType == "application/json"

    def test_load_resources_with_missing_config(self):
        """Test loading resources when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            loader = ConfigLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert resources == []

    def test_load_prompts_with_valid_config(self):
        """Test loading prompts from valid configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create test prompts config
            prompts_config = {
                "prompts": [
                    {
                        "name": "test_prompt",
                        "description": "Test prompt description",
                        "arguments": [
                            {"name": "symbol", "description": "Stock symbol", "required": True},
                            {
                                "name": "optional_param",
                                "description": "Optional parameter",
                                "required": False,
                            },
                        ],
                    }
                ]
            }

            with open(config_dir / "prompts.json", "w") as f:
                json.dump(prompts_config, f)

            loader = ConfigLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert len(prompts) == 1
            assert all(isinstance(p, Prompt) for p in prompts)
            assert prompts[0].name == "test_prompt"
            assert len(prompts[0].arguments) == 2
            assert prompts[0].arguments[0].required is True
            assert prompts[0].arguments[1].required is False

    def test_load_prompts_with_missing_config(self):
        """Test loading prompts when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            loader = ConfigLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert prompts == []

    def test_load_resources_with_empty_config(self):
        """Test loading resources with empty configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create empty config
            with open(config_dir / "resources.json", "w") as f:
                json.dump({}, f)

            loader = ConfigLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert resources == []

    def test_load_prompts_with_empty_config(self):
        """Test loading prompts with empty configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create empty config
            with open(config_dir / "prompts.json", "w") as f:
                json.dump({}, f)

            loader = ConfigLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert prompts == []

    def test_load_resources_with_default_mimetype(self):
        """Test loading resources with default mimeType."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create resources config without mimeType
            resources_config = {
                "resources": [
                    {
                        "uri": "financial://test/resource",
                        "name": "Test Resource",
                        "description": "Test resource description",
                    }
                ]
            }

            with open(config_dir / "resources.json", "w") as f:
                json.dump(resources_config, f)

            loader = ConfigLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert len(resources) == 1
            assert resources[0].mimeType == "text/plain"

    def test_load_prompts_with_default_required(self):
        """Test loading prompts with default required value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create prompts config without required field
            prompts_config = {
                "prompts": [
                    {
                        "name": "test_prompt",
                        "description": "Test prompt description",
                        "arguments": [{"name": "symbol", "description": "Stock symbol"}],
                    }
                ]
            }

            with open(config_dir / "prompts.json", "w") as f:
                json.dump(prompts_config, f)

            loader = ConfigLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert len(prompts) == 1
            assert prompts[0].arguments[0].required is True
