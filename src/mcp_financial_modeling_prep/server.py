"""MCP server implementation for Financial Modeling Prep API."""

import asyncio
import os
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, Prompt
import mcp.server.stdio


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("financial-modeling-prep")
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """List available financial tools."""
        return [
            Tool(
                name="get_company_profile",
                description="Get company profile information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            Tool(
                name="get_income_statement",
                description="Get company income statement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            Tool(
                name="get_stock_quote",
                description="Get real-time stock quote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        ]
    
    @server.list_resources()
    async def handle_list_resources() -> List[Resource]:
        """List available financial resources."""
        return [
            Resource(
                uri="financial://templates/analysis",
                name="Financial Analysis Templates",
                description="Templates for financial analysis",
                mimeType="text/plain"
            )
        ]
    
    @server.list_prompts()
    async def handle_list_prompts() -> List[Prompt]:
        """List available financial analysis prompts."""
        return [
            Prompt(
                name="analyze_company",
                description="Analyze a company's financial performance",
                arguments=[
                    {
                        "name": "symbol",
                        "description": "Stock symbol to analyze",
                        "required": True
                    }
                ]
            )
        ]
    
    return server


async def main():
    """Main entry point for the server."""
    server = create_server()
    
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
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())