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

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the technical indicators service.

        Args:
            arguments: Tool arguments containing symbol and optional parameters

        Returns:
            List of TextContent with formatted technical indicators
        """
        from datetime import date

        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        # Get optional parameters
        indicator_type = arguments.get("indicator_type")
        period = arguments.get("period")
        timeframe = arguments.get("timeframe")
        from_date_str = arguments.get("from_date")
        to_date_str = arguments.get("to_date")

        # Parse dates if provided
        from_date = None
        to_date = None
        if from_date_str:
            try:
                from_date = date.fromisoformat(from_date_str)
            except ValueError:
                return self.create_error_response("Invalid from_date format. Use YYYY-MM-DD")

        if to_date_str:
            try:
                to_date = date.fromisoformat(to_date_str)
            except ValueError:
                return self.create_error_response("Invalid to_date format. Use YYYY-MM-DD")

        # Convert period to int if provided
        if period is not None:
            try:
                period = int(period)
            except (ValueError, TypeError):
                return self.create_error_response("Period must be a valid integer")

        result = await self.fmp_client.get_technical_indicators(
            symbol=symbol,
            indicator_type=indicator_type,
            period=period,
            timeframe=timeframe,
            from_date=from_date,
            to_date=to_date,
        )

        if not result:
            return self.create_no_data_response(symbol)

        # Get the actual values used (with defaults)
        actual_indicator = indicator_type or "sma"
        actual_period = period or 20
        actual_timeframe = timeframe or "1day"

        # Format the technical indicators data
        indicator_name = actual_indicator.upper()
        formatted_text = f"""Technical Indicators for {symbol}

Indicator: {indicator_name} ({actual_period}-period)
Timeframe: {actual_timeframe}"""

        if from_date or to_date:
            date_range = f"Date Range: {from_date_str or 'N/A'} to {to_date_str or 'N/A'}"
            formatted_text += f"\n{date_range}"

        formatted_text += "\n\nLatest Data:"

        # Show the most recent 5 data points
        for i, entry in enumerate(result[:5]):
            formatted_text += f"\n\nDate: {entry.get('date', 'N/A')}"
            formatted_text += f"\nClose Price: ${entry.get('close', 'N/A')}"

            # Add the specific indicator value
            indicator_value = entry.get(actual_indicator.lower())
            if indicator_value is not None:
                if actual_indicator.lower() in ["sma", "ema", "wma", "dema", "tema"]:
                    formatted_text += f"\n{indicator_name}: ${indicator_value:.2f}"
                else:
                    formatted_text += f"\n{indicator_name}: {indicator_value:.2f}"

        if len(result) > 5:
            formatted_text += f"\n\n... and {len(result) - 5} more data points"

        return [TextContent(type="text", text=formatted_text)]
