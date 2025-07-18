"""MCP server implementation for Financial Modeling Prep API."""

import asyncio
import os
import sys

import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Prompt, Resource, TextContent, Tool

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

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """List available financial tools."""
        return service_registry.get_all_tools()

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """List available financial resources."""
        from pydantic import AnyUrl

        return [
            Resource(
                uri=AnyUrl("financial://templates/analysis"),
                name="Financial Analysis Templates",
                description="Templates for comprehensive financial analysis and reporting",
                mimeType="text/plain",
            ),
            Resource(
                uri=AnyUrl("financial://templates/report"),
                name="Financial Report Templates",
                description="Templates for generating financial reports and summaries",
                mimeType="text/plain",
            ),
            Resource(
                uri=AnyUrl("financial://templates/company"),
                name="Company Analysis Templates",
                description="Templates for company profile and performance analysis",
                mimeType="text/plain",
            ),
        ]

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        """List available financial analysis prompts."""
        from mcp.types import PromptArgument

        return [
            Prompt(
                name="analyze_company",
                description="Analyze a company's financial performance comprehensively",
                arguments=[
                    PromptArgument(
                        name="symbol",
                        description="Stock symbol to analyze",
                        required=True,
                    )
                ],
            ),
            Prompt(
                name="technical_analysis",
                description="Perform technical analysis with indicators and trends",
                arguments=[
                    PromptArgument(
                        name="symbol",
                        description="Stock symbol to analyze",
                        required=True,
                    ),
                    PromptArgument(
                        name="period",
                        description="Time period for analysis (e.g., 20, 50, 200 days)",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="financial_health",
                description="Assess company's financial health using ratios and metrics",
                arguments=[
                    PromptArgument(
                        name="symbol",
                        description="Stock symbol to analyze",
                        required=True,
                    ),
                    PromptArgument(
                        name="benchmark",
                        description="Benchmark symbol for comparison (optional)",
                        required=False,
                    ),
                ],
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls for financial data."""
        return await service_registry.execute_tool(name, arguments)

    return server


async def main():
    """Main entry point for the server."""
    # Get FMP API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("Error: FMP_API_KEY environment variable is required", file=sys.stderr)
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
