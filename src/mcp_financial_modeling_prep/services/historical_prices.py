"""Historical prices service."""

from datetime import date
from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class HistoricalPricesService(BaseFinancialService):
    """Service for retrieving historical price information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_historical_prices"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get historical price data for a stock symbol"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for input parameters."""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., AAPL)",
                },
                "from_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Start date for historical data (YYYY-MM-DD)",
                },
                "to_date": {
                    "type": "string",
                    "format": "date",
                    "description": "End date for historical data (YYYY-MM-DD)",
                },
            },
            "required": ["symbol"],
        }

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the historical prices service.

        Args:
            arguments: Tool arguments containing symbol and optional dates

        Returns:
            List of TextContent with formatted historical prices
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        # Parse dates if provided
        from_date = None
        to_date = None

        if "from_date" in arguments:
            try:
                from_date = date.fromisoformat(arguments["from_date"])
            except ValueError:
                return self.create_error_response("Invalid from_date format. Use YYYY-MM-DD")

        if "to_date" in arguments:
            try:
                to_date = date.fromisoformat(arguments["to_date"])
            except ValueError:
                return self.create_error_response("Invalid to_date format. Use YYYY-MM-DD")

        result = await self.fmp_client.get_historical_prices(symbol, from_date, to_date)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the historical prices data
        formatted_text = f"Historical Prices for {symbol}\n\n"

        # Show first 5 entries to avoid overwhelming output
        for i, entry in enumerate(result[:5]):
            formatted_text += f"Date: {entry.get('date', 'N/A')} | "
            formatted_text += f"Open: ${entry.get('open', 'N/A')} | "
            formatted_text += f"High: ${entry.get('high', 'N/A')} | "
            formatted_text += f"Low: ${entry.get('low', 'N/A')} | "
            formatted_text += f"Close: ${entry.get('close', 'N/A')} | "
            formatted_text += f"Volume: {entry.get('volume', 'N/A')}\n"

        if len(result) > 5:
            formatted_text += f"\n... and {len(result) - 5} more entries"

        return [TextContent(type="text", text=formatted_text)]
