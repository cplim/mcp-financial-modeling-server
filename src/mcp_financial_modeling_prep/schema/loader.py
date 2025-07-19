"""Schema loader for MCP resources, prompts, and service tool schemas."""

import json
from pathlib import Path
from typing import Any

from mcp.types import Prompt, PromptArgument, Resource
from pydantic import AnyUrl


class SchemaLoader:
    """Loads MCP resources, prompts, and service tool schemas from schema files."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the schema loader.

        Args:
            config_dir: Directory containing schema files.
                       If None, uses the default schema directory.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        self.schema_dir = config_dir

    def load_resources(self) -> list[Resource]:
        """Load resources from schema file.

        Returns:
            List of Resource objects
        """
        resources_file = self.schema_dir / "resources.json"
        if not resources_file.exists():
            return []

        with open(resources_file) as f:
            config = json.load(f)

        resources = []
        for resource_config in config.get("resources", []):
            resource = Resource(
                uri=AnyUrl(resource_config["uri"]),
                name=resource_config["name"],
                description=resource_config["description"],
                mimeType=resource_config.get("mimeType", "text/plain"),
            )
            resources.append(resource)

        return resources

    def load_prompts(self) -> list[Prompt]:
        """Load prompts from schema file.

        Returns:
            List of Prompt objects
        """
        prompts_file = self.schema_dir / "prompts.json"
        if not prompts_file.exists():
            return []

        with open(prompts_file) as f:
            config = json.load(f)

        prompts = []
        for prompt_config in config.get("prompts", []):
            arguments = []
            for arg_config in prompt_config.get("arguments", []):
                argument = PromptArgument(
                    name=arg_config["name"],
                    description=arg_config["description"],
                    required=arg_config.get("required", True),
                )
                arguments.append(argument)

            prompt = Prompt(
                name=prompt_config["name"],
                description=prompt_config["description"],
                arguments=arguments,
            )
            prompts.append(prompt)

        return prompts

    def load_service_schema(self, service_name: str) -> dict[str, Any] | None:
        """Load service tool schema from JSON schema file.

        Args:
            service_name: Name of the service (without .json extension)

        Returns:
            Service tool schema dictionary, or None if file doesn't exist or is invalid
        """
        tool_schema_file = self.schema_dir / f"services/{service_name}.json"
        if not tool_schema_file.exists():
            return None

        with open(tool_schema_file) as f:
            try:
                schema = json.load(f)
            except json.JSONDecodeError:
                schema = None

        return schema
