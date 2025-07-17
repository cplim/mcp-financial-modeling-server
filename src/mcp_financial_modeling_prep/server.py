"""MCP server implementation for Financial Modeling Prep API."""

import asyncio
import os
import sys

import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Prompt, Resource, TextContent, Tool

from .fmp_client import FMPClient


def create_server(api_key: str) -> Server:
    """Create and configure the MCP server.

    Args:
        api_key: Financial Modeling Prep API key
    """
    server: Server = Server("financial-modeling-prep")

    # Initialize FMP client with API key
    fmp_client = FMPClient(api_key=api_key)

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
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
                            "description": "Stock symbol (e.g., AAPL)",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_income_statement",
                description="Get company income statement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_stock_quote",
                description="Get real-time stock quote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_historical_prices",
                description="Get historical stock prices",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)",
                        },
                        "from_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (optional)",
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format (optional)",
                        },
                    },
                    "required": ["symbol"],
                },
            ),
            Tool(
                name="get_market_indices",
                description="Get market indices data",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_trading_volume",
                description="Get trading volume data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL)",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
        ]

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """List available financial resources."""
        from pydantic import AnyUrl

        return [
            Resource(
                uri=AnyUrl("financial://templates/analysis"),
                name="Financial Analysis Templates",
                description="Templates for financial analysis",
                mimeType="text/plain",
            )
        ]

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        """List available financial analysis prompts."""
        from mcp.types import PromptArgument

        return [
            Prompt(
                name="analyze_company",
                description="Analyze a company's financial performance",
                arguments=[
                    PromptArgument(
                        name="symbol",
                        description="Stock symbol to analyze",
                        required=True,
                    )
                ],
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls for financial data."""
        try:
            if name == "get_company_profile":
                symbol = arguments.get("symbol", "")
                if not symbol:
                    return [TextContent(type="text", text="Error: Symbol is required")]

                result = await fmp_client.get_company_profile(symbol)
                if not result:
                    return [
                        TextContent(
                            type="text", text=f"No data found for symbol: {symbol}"
                        )
                    ]

                # Format the company profile data
                formatted_text = f"""Company Profile for {result.get('symbol', 'N/A')}

Company Name: {result.get('companyName', 'N/A')}
Industry: {result.get('industry', 'N/A')}
Website: {result.get('website', 'N/A')}
Description: {result.get('description', 'N/A')}"""

                return [TextContent(type="text", text=formatted_text)]

            elif name == "get_income_statement":
                symbol = arguments.get("symbol", "")
                if not symbol:
                    return [TextContent(type="text", text="Error: Symbol is required")]

                result = await fmp_client.get_income_statement(symbol)
                if not result:
                    return [
                        TextContent(
                            type="text", text=f"No data found for symbol: {symbol}"
                        )
                    ]

                # Format the income statement data
                revenue = result.get("revenue", 0)
                gross_profit = result.get("grossProfit", 0)
                operating_income = result.get("operatingIncome", 0)
                net_income = result.get("netIncome", 0)

                formatted_text = f"""Income Statement for {result.get('symbol', 'N/A')}

Date: {result.get('date', 'N/A')}
Revenue: ${revenue:,.0f}
Gross Profit: ${gross_profit:,.0f}
Operating Income: ${operating_income:,.0f}
Net Income: ${net_income:,.0f}"""

                return [TextContent(type="text", text=formatted_text)]

            elif name == "get_stock_quote":
                symbol = arguments.get("symbol", "")
                if not symbol:
                    return [TextContent(type="text", text="Error: Symbol is required")]

                result = await fmp_client.get_stock_quote(symbol)
                if not result:
                    return [
                        TextContent(
                            type="text", text=f"No data found for symbol: {symbol}"
                        )
                    ]

                # Format the stock quote data
                price = result.get("price", 0)
                change = result.get("change", 0)
                change_percent = result.get("changesPercentage", 0)
                day_low = result.get("dayLow", 0)
                day_high = result.get("dayHigh", 0)
                year_low = result.get("yearLow", 0)
                year_high = result.get("yearHigh", 0)

                formatted_text = f"""Stock Quote for {result.get('symbol', 'N/A')}

Current Price: ${price:.2f}
Change: ${change:.2f} ({change_percent:.2f}%)
Day Range: ${day_low:.2f} - ${day_high:.2f}
52-Week Range: ${year_low:.2f} - ${year_high:.2f}"""

                return [TextContent(type="text", text=formatted_text)]

            elif name == "get_historical_prices":
                symbol = arguments.get("symbol", "")
                if not symbol:
                    return [TextContent(type="text", text="Error: Symbol is required")]

                from_date_str = arguments.get("from_date")
                to_date_str = arguments.get("to_date")

                # Parse date strings if provided
                from_date = None
                to_date = None

                if from_date_str:
                    try:
                        from datetime import datetime

                        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        return [
                            TextContent(
                                type="text",
                                text="Error: Invalid from_date format. Use YYYY-MM-DD",
                            )
                        ]

                if to_date_str:
                    try:
                        from datetime import datetime

                        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        return [
                            TextContent(
                                type="text",
                                text="Error: Invalid to_date format. Use YYYY-MM-DD",
                            )
                        ]

                historical_data = await fmp_client.get_historical_prices(
                    symbol, from_date, to_date
                )
                if not historical_data:
                    return [
                        TextContent(
                            type="text",
                            text=f"No historical data found for symbol: {symbol}",
                        )
                    ]

                # Format the historical prices data
                formatted_text = f"Historical Prices for {symbol}\n\n"
                for price in historical_data[:10]:  # Show first 10 entries
                    formatted_text += f"Date: {price.get('date', 'N/A')}\n"
                    formatted_text += f"Open: ${price.get('open', 0):.2f}\n"
                    formatted_text += f"High: ${price.get('high', 0):.2f}\n"
                    formatted_text += f"Low: ${price.get('low', 0):.2f}\n"
                    formatted_text += f"Close: ${price.get('close', 0):.2f}\n"
                    formatted_text += f"Volume: {price.get('volume', 0):,}\n\n"

                if len(historical_data) > 10:
                    formatted_text += f"... and {len(historical_data) - 10} more entries"

                return [TextContent(type="text", text=formatted_text)]

            elif name == "get_market_indices":
                indices_data = await fmp_client.get_market_indices()
                if not indices_data:
                    return [
                        TextContent(
                            type="text", text="No market indices data available"
                        )
                    ]

                # Format the market indices data
                formatted_text = "Market Indices\n\n"
                for index in indices_data:
                    formatted_text += (
                        f"Index: {index.get('name', index.get('symbol', 'N/A'))}\n"
                    )
                    formatted_text += f"Symbol: {index.get('symbol', 'N/A')}\n"
                    formatted_text += f"Price: ${index.get('price', 0):.2f}\n"
                    change_pct = index.get('changesPercentage', 0)
                    change_val = index.get('change', 0)
                    formatted_text += f"Change: ${change_val:.2f} ({change_pct:.2f}%)\n\n"

                return [TextContent(type="text", text=formatted_text)]

            elif name == "get_trading_volume":
                symbol = arguments.get("symbol", "")
                if not symbol:
                    return [TextContent(type="text", text="Error: Symbol is required")]

                result = await fmp_client.get_trading_volume(symbol)
                if not result:
                    return [
                        TextContent(
                            type="text",
                            text=f"No trading volume data found for symbol: {symbol}",
                        )
                    ]

                # Format the trading volume data
                formatted_text = f"""Trading Volume for {result.get('symbol', 'N/A')}

Current Volume: {result.get('volume', 0):,}
Average Volume: {result.get('avgVolume', 0):,}
Date: {result.get('date', 'N/A')}"""

                return [TextContent(type="text", text=formatted_text)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

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
