"""Company profile service."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class CompanyProfileService(BaseFinancialService):
    """Service for retrieving company profile information."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_company_profile"

    @property
    def description(self) -> str:
        """Return the service description."""
        return "Get company profile information"

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the company profile service.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with formatted company profile
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        result = await self.fmp_client.get_company_profile(symbol)
        if not result:
            return self.create_no_data_response(symbol)

        # Format the company profile data
        formatted_text = f"""Company Profile for {result.get('symbol', 'N/A')}

Company Name: {result.get('companyName', 'N/A')}
Industry: {result.get('industry', 'N/A')}
Website: {result.get('website', 'N/A')}
Description: {result.get('description', 'N/A')}"""

        return [TextContent(type="text", text=formatted_text)]
