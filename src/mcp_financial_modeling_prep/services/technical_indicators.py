"""Technical indicators service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class TechnicalIndicatorsService(BaseFinancialService):
    """Service for retrieving technical indicators analysis."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_technical_indicators"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get technical indicators for stock analysis (SMA, EMA, RSI, etc.)"

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
                "indicator_type": {
                    "type": "string",
                    "description": "Type of technical indicator (sma, ema, rsi, etc.)",
                },
                "period": {
                    "type": "integer",
                    "description": "Period for the indicator calculation",
                    "minimum": 1,
                    "maximum": 200,
                },
            },
            "required": ["symbol", "indicator_type", "period"],
        }

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the technical indicators service.

        Args:
            arguments: Tool arguments containing symbol, indicator_type, and period

        Returns:
            List of TextContent with formatted technical indicators
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        indicator_type = arguments.get("indicator_type")
        if not indicator_type:
            return self.create_error_response("Indicator type is required")

        period = arguments.get("period")
        if not period:
            return self.create_error_response("Period is required")

        try:
            period = int(period)
        except (ValueError, TypeError):
            return self.create_error_response("Period must be a valid integer")

        result = await self.fmp_client.get_technical_indicators(symbol, indicator_type, period)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the technical indicators data
        indicator_name = indicator_type.upper()
        formatted_text = f"""Technical Indicators for {symbol}

Indicator: {indicator_name} ({period}-day)

Latest Data:"""

        # Show the most recent 5 data points
        for i, entry in enumerate(result[:5]):
            formatted_text += f"\n\nDate: {entry.get('date', 'N/A')}"
            formatted_text += f"\nClose Price: ${entry.get('close', 'N/A')}"

            # Add the specific indicator value
            indicator_value = entry.get(indicator_type.lower())
            if indicator_value is not None:
                if indicator_type.lower() in ["sma", "ema", "wma", "dema", "tema"]:
                    formatted_text += f"\n{indicator_name}: ${indicator_value:.2f}"
                else:
                    formatted_text += f"\n{indicator_name}: {indicator_value:.2f}"

        if len(result) > 5:
            formatted_text += f"\n\n... and {len(result) - 5} more data points"

        return [TextContent(type="text", text=formatted_text)]
