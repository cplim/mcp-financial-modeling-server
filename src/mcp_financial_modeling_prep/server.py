"""MCP server implementation for Financial Modeling Prep API."""

import asyncio
import os
import sys
from pathlib import Path

import mcp.server.stdio
from mcp.server import Server
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.types import Prompt, Resource, TextContent, Tool

from .config import ConfigLoader
from .fmp_client import FMPClient
from .services.registry import ServiceRegistry


def create_server(api_key: str) -> Server:
    """Create and configure the MCP server.

    Args:
        api_key: Financial Modeling Prep API key
    """
    server: Server = Server("financial-modeling-prep")

    # Initialize FMP client with API key
    fmp_client = FMPClient(api_key=api_key)

    # Initialize service registry
    service_registry = ServiceRegistry(fmp_client)

    # Initialize configuration loader
    config_loader = ConfigLoader()

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """List available financial tools."""
        return service_registry.get_all_tools()

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """List available financial resources."""
        return config_loader.load_resources()

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        """List available financial analysis prompts."""
        return config_loader.load_prompts()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls for financial data."""
        return await service_registry.execute_tool(name, arguments)

    return server


async def main():
    """Main entry point for the server."""
    # Load environment variables from .env file if it exists
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Get FMP API key from environment (supports both system env vars and .env file)
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("Error: FMP_API_KEY environment variable is required", file=sys.stderr)
        print("Create a .env file with FMP_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)

    server = create_server(api_key)

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="financial-modeling-prep",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
