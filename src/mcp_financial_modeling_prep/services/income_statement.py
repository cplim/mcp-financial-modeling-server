"""Income statement service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class IncomeStatementService(BaseFinancialService):
    """Service for retrieving income statement information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_income_statement"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get income statement information for a company"

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
        """Execute the income statement service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted income statement
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_income_statement(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the income statement data
        revenue = result.get("revenue")
        gross_profit = result.get("grossProfit")
        operating_income = result.get("operatingIncome")
        net_income = result.get("netIncome")

        revenue_text = f"${revenue:,.0f}" if revenue is not None else "N/A"
        gross_profit_text = f"${gross_profit:,.0f}" if gross_profit is not None else "N/A"
        operating_income_text = (
            f"${operating_income:,.0f}" if operating_income is not None else "N/A"
        )
        net_income_text = f"${net_income:,.0f}" if net_income is not None else "N/A"

        formatted_text = f"""Income Statement for {result.get('symbol', 'N/A')}

Date: {result.get('date', 'N/A')}
Revenue: {revenue_text}
Gross Profit: {gross_profit_text}
Operating Income: {operating_income_text}
Net Income: {net_income_text}"""

        return [TextContent(type="text", text=formatted_text)]
