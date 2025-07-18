"""Financial ratios service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class FinancialRatiosService(BaseFinancialService):
    """Service for retrieving financial ratios analysis."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_financial_ratios"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get financial ratios and metrics for analyzing company performance"

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the financial ratios service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted financial ratios
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_financial_ratios(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the financial ratios data
        current_ratio = result.get("currentRatio")
        quick_ratio = result.get("quickRatio")
        debt_equity_ratio = result.get("debtEquityRatio")
        roe = result.get("returnOnEquity")
        roa = result.get("returnOnAssets")
        gross_profit_margin = result.get("grossProfitMargin")
        net_profit_margin = result.get("netProfitMargin")
        operating_profit_margin = result.get("operatingProfitMargin")

        # Helper function to format percentage
        def format_percentage(value):
            if value is not None:
                return f"{value * 100:.2f}%"
            return "N/A"

        # Helper function to format ratio
        def format_ratio(value):
            if value is not None:
                return f"{value:.2f}"
            return "N/A"

        formatted_text = f"""Financial Ratios for {result.get('symbol', 'N/A')}

Date: {result.get('date', 'N/A')}

LIQUIDITY RATIOS:
Current Ratio: {format_ratio(current_ratio)}
Quick Ratio: {format_ratio(quick_ratio)}

PROFITABILITY RATIOS:
Return on Equity (ROE): {format_percentage(roe)}
Return on Assets (ROA): {format_percentage(roa)}
Gross Profit Margin: {format_percentage(gross_profit_margin)}
Operating Profit Margin: {format_percentage(operating_profit_margin)}
Net Profit Margin: {format_percentage(net_profit_margin)}

LEVERAGE RATIOS:
Debt-to-Equity Ratio: {format_ratio(debt_equity_ratio)}"""

        return [TextContent(type="text", text=formatted_text)]
