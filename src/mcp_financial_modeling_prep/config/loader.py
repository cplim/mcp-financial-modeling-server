"""Configuration loader for MCP resources and prompts."""

import json
from pathlib import Path

from mcp.types import Prompt, PromptArgument, Resource
from pydantic import AnyUrl


class ConfigLoader:
    """Loads MCP resources and prompts from configuration files."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the configuration loader.

        Args:
            config_dir: Directory containing configuration files.
                       If None, uses the default config directory.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        self.config_dir = config_dir

    def load_resources(self) -> list[Resource]:
        """Load resources from configuration file.

        Returns:
            List of Resource objects
        """
        resources_file = self.config_dir / "resources.json"
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
        """Load prompts from configuration file.

        Returns:
            List of Prompt objects
        """
        prompts_file = self.config_dir / "prompts.json"
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
