"""Trading volume service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class TradingVolumeService(BaseFinancialService):
    """Service for retrieving trading volume information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_trading_volume"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get trading volume data for a stock symbol"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for input parameters."""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., AAPL)",
                }
            },
            "required": ["symbol"],
        }

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the trading volume service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted trading volume
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_trading_volume(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the trading volume data
        volume = result.get("volume")
        avg_volume = result.get("avgVolume")

        volume_text = f"{volume:,}" if volume is not None else "N/A"
        avg_volume_text = f"{avg_volume:,}" if avg_volume is not None else "N/A"

        formatted_text = f"""Trading Volume for {result.get('symbol', 'N/A')}

Current Volume: {volume_text}
Average Volume: {avg_volume_text}
Date: {result.get('date', 'N/A')}"""

        return [TextContent(type="text", text=formatted_text)]
