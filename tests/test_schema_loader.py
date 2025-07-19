"""Test cases for schema loader."""

import json
import tempfile
from pathlib import Path

from mcp.types import Prompt, Resource

from mcp_financial_modeling_prep.schema.loader import SchemaLoader


class TestSchemaLoader:
    """Test the schema loader."""

    def test_schema_loader_initialization(self):
        """Test that schema loader can be initialized."""
        loader = SchemaLoader()
        assert loader.schema_dir is not None

    def test_schema_loader_with_custom_directory(self):
        """Test that schema loader can be initialized with custom directory."""
        custom_dir = Path("/tmp/test_schema")
        loader = SchemaLoader(config_dir=custom_dir)
        assert loader.schema_dir == custom_dir

    def test_load_resources_with_valid_config(self):
        """Test loading resources from valid schema file."""
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

            loader = SchemaLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert len(resources) == 2
            assert all(isinstance(r, Resource) for r in resources)
            assert resources[0].name == "Test Resource 1"
            assert str(resources[0].uri) == "financial://test/resource1"
            assert resources[1].mimeType == "application/json"

    def test_load_resources_with_missing_config(self):
        """Test loading resources when schema file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            loader = SchemaLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert resources == []

    def test_load_prompts_with_valid_config(self):
        """Test loading prompts from valid schema file."""
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

            loader = SchemaLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert len(prompts) == 1
            assert all(isinstance(p, Prompt) for p in prompts)
            assert prompts[0].name == "test_prompt"
            assert len(prompts[0].arguments) == 2
            assert prompts[0].arguments[0].required is True
            assert prompts[0].arguments[1].required is False

    def test_load_prompts_with_missing_config(self):
        """Test loading prompts when schema file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            loader = SchemaLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert prompts == []

    def test_load_resources_with_empty_config(self):
        """Test loading resources with empty schema file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create empty config
            with open(config_dir / "resources.json", "w") as f:
                json.dump({}, f)

            loader = SchemaLoader(config_dir=config_dir)
            resources = loader.load_resources()

            assert resources == []

    def test_load_prompts_with_empty_config(self):
        """Test loading prompts with empty schema file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create empty config
            with open(config_dir / "prompts.json", "w") as f:
                json.dump({}, f)

            loader = SchemaLoader(config_dir=config_dir)
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

            loader = SchemaLoader(config_dir=config_dir)
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

            loader = SchemaLoader(config_dir=config_dir)
            prompts = loader.load_prompts()

            assert len(prompts) == 1
            assert prompts[0].arguments[0].required is True

    def test_load_service_schema_with_valid_config(self):
        """Test loading service schema from valid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            services_dir = config_dir / "services"
            services_dir.mkdir()

            # Create test service schema
            service_schema = {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"},
                    "optional_param": {"type": "number", "description": "Optional parameter"},
                },
                "required": ["symbol"],
            }

            with open(services_dir / "company_profile.json", "w") as f:
                json.dump(service_schema, f)

            loader = SchemaLoader(config_dir=config_dir)
            schema = loader.load_service_schema("company_profile")

            assert schema == service_schema
            assert schema["type"] == "object"
            assert "symbol" in schema["properties"]
            assert schema["required"] == ["symbol"]

    def test_load_service_schema_with_missing_file(self):
        """Test loading service schema when JSON file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            services_dir = config_dir / "services"
            services_dir.mkdir()

            loader = SchemaLoader(config_dir=config_dir)
            schema = loader.load_service_schema("nonexistent_service")

            assert schema is None

    def test_load_service_schema_with_missing_services_directory(self):
        """Test loading service schema when services directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            loader = SchemaLoader(config_dir=config_dir)
            schema = loader.load_service_schema("company_profile")

            assert schema is None

    def test_load_service_schema_with_invalid_json(self):
        """Test loading service schema with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            services_dir = config_dir / "services"
            services_dir.mkdir()

            # Create invalid JSON file
            with open(services_dir / "invalid_service.json", "w") as f:
                f.write("{ invalid json content")

            loader = SchemaLoader(config_dir=config_dir)
            schema = loader.load_service_schema("invalid_service")

            assert schema is None
