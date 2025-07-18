"""DCF valuation service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class DCFValuationService(BaseFinancialService):
    """Service for retrieving DCF valuation analysis."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_dcf_valuation"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get discounted cash flow (DCF) valuation for a company"

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the DCF valuation service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted DCF valuation
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_dcf_valuation(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the DCF valuation data
        dcf_value = result.get("dcf")
        stock_price = result.get("Stock Price")

        # Calculate upside/downside if both values are available
        upside_text = ""
        if dcf_value is not None and stock_price is not None:
            upside_percentage = ((dcf_value - stock_price) / stock_price) * 100
            upside_text = f"\nUpside/Downside: {upside_percentage:.2f}%"
            if upside_percentage > 0:
                upside_text += " (Undervalued)"
            elif upside_percentage < 0:
                upside_text += " (Overvalued)"
            else:
                upside_text += " (Fair Value)"

        dcf_text = f"${dcf_value:.2f}" if dcf_value is not None else "N/A"
        price_text = f"${stock_price:.2f}" if stock_price is not None else "N/A"

        formatted_text = f"""DCF Valuation Analysis for {result.get('symbol', 'N/A')}

Date: {result.get('date', 'N/A')}

DCF Fair Value: {dcf_text}
Current Stock Price: {price_text}{upside_text}"""

        return [TextContent(type="text", text=formatted_text)]
