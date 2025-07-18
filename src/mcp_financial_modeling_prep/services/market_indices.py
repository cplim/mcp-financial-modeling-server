"""Market indices service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class MarketIndicesService(BaseFinancialService):
    """Service for retrieving market indices information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_market_indices"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get market indices information (S&P 500, NASDAQ, DOW)"

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the market indices service.

        Args:
            arguments: Tool arguments (none required)

        Returns:
            List of TextContent with formatted market indices
        """
        result = await self.fmp_client.get_market_indices()
        if not result:
            return [TextContent(type="text", text="No market indices data available")]

        # Format the market indices data
        formatted_text = "Market Indices\n\n"
        for index in result:
            formatted_text += f"Index: {index.get('name', index.get('symbol', 'N/A'))}\n"
            formatted_text += f"Symbol: {index.get('symbol', 'N/A')}\n"

            # Format price with proper handling of missing values
            price = index.get("price")
            if price is not None:
                formatted_text += f"Price: ${price:.2f}\n"
            else:
                formatted_text += "Price: N/A\n"

            # Format change values with proper handling of missing values
            change_pct = index.get("changesPercentage")
            change_val = index.get("change")
            if change_val is not None and change_pct is not None:
                formatted_text += f"Change: ${change_val:.2f} ({change_pct:.2f}%)\n\n"
            else:
                formatted_text += "Change: N/A\n\n"

        return [TextContent(type="text", text=formatted_text)]
