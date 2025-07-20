"""MCP server implementation for Financial Modeling Prep API."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Prompt, Resource, TextContent, Tool

from .fmp_client import FMPClient
from .schema import SchemaLoader
from .services.registry import ServiceRegistry
from .transport import create_transport


def create_server(api_key: str) -> Server:
    """Create and configure the MCP server.

    Args:
        api_key: Financial Modeling Prep API key
    """
    server: Server = Server("financial-modeling-prep")

    # Initialize FMP client with API key
    fmp_client = FMPClient(api_key=api_key)

    # Initialize schema loader
    schema_loader = SchemaLoader()

    # Initialize service registry
    service_registry = ServiceRegistry(fmp_client, schema_loader)

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """List available financial tools."""
        return service_registry.get_all_tools()

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """List available financial resources."""
        return schema_loader.load_resources()

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        """List available financial analysis prompts."""
        return schema_loader.load_prompts()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls for financial data."""
        return await service_registry.execute_tool(name, arguments)

    return server


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Financial Modeling Prep Server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transport (default: 127.0.0.1 for security)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transport (default: 8000)"
    )
    return parser.parse_args()


async def main():
    """Main entry point for the server."""
    # Parse command line arguments
    args = parse_args()
    
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

    # Create MCP server
    server = create_server(api_key)
    
    # Create transport based on command line arguments
    if args.transport == "stdio":
        transport = create_transport("stdio")
        print("Starting MCP server with stdio transport...", file=sys.stderr)
    elif args.transport == "http":
        transport = create_transport("http", host=args.host, port=args.port)
        print(f"Starting MCP server with HTTP transport on {args.host}:{args.port}...", file=sys.stderr)
        print(f"Health check: http://{args.host}:{args.port}/health", file=sys.stderr)
        print(f"MCP endpoint: http://{args.host}:{args.port}/mcp", file=sys.stderr)
    
    # Run server with selected transport
    await transport.run(server)


if __name__ == "__main__":
    asyncio.run(main())
