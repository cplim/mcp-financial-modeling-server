"""Stock quote service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class StockQuoteService(BaseFinancialService):
    """Service for retrieving stock quote information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_stock_quote"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get current stock price and quote information"

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the stock quote service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted stock quote
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_stock_quote(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the stock quote data
        price = result.get("price")
        change = result.get("change")
        change_percent = result.get("changesPercentage")
        day_low = result.get("dayLow")
        day_high = result.get("dayHigh")
        year_low = result.get("yearLow")
        year_high = result.get("yearHigh")

        price_text = f"${price:.2f}" if price is not None else "N/A"
        change_text = f"${change:.2f}" if change is not None else "N/A"
        change_pct_text = f"{change_percent:.2f}%" if change_percent is not None else "N/A"
        day_low_text = f"${day_low:.2f}" if day_low is not None else "N/A"
        day_high_text = f"${day_high:.2f}" if day_high is not None else "N/A"
        year_low_text = f"${year_low:.2f}" if year_low is not None else "N/A"
        year_high_text = f"${year_high:.2f}" if year_high is not None else "N/A"

        formatted_text = f"""Stock Quote for {result.get('symbol', 'N/A')}

Current Price: {price_text}
Change: {change_text} ({change_pct_text})
Day Range: {day_low_text} - {day_high_text}
52-Week Range: {year_low_text} - {year_high_text}"""

        return [TextContent(type="text", text=formatted_text)]
