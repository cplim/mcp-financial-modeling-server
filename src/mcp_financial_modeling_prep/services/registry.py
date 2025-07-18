"""Service registry for financial data tools."""

from typing import Any

from mcp.types import TextContent, Tool

from ..config.loader import ConfigLoader
from ..fmp_client import FMPClient
from .base import BaseFinancialService
from .company_profile import CompanyProfileService
from .dcf_valuation import DCFValuationService
from .financial_ratios import FinancialRatiosService
from .historical_prices import HistoricalPricesService
from .income_statement import IncomeStatementService
from .market_indices import MarketIndicesService
from .stock_quote import StockQuoteService
from .technical_indicators import TechnicalIndicatorsService
from .trading_volume import TradingVolumeService


class ServiceRegistry:
    """Registry for managing financial data services."""

    def __init__(self, fmp_client: FMPClient, config_loader: ConfigLoader):
        """Initialize the service registry.

        Args:
            fmp_client: Financial Modeling Prep API client
            config_loader: Configuration loader for schemas
        """
        self.fmp_client = fmp_client
        self.config_loader = config_loader
        self.services: dict[str, BaseFinancialService] = {}
        self._register_services()

    def _register_services(self) -> None:
        """Register all available services."""
        # Register all service classes
        service_classes = [
            CompanyProfileService,
            IncomeStatementService,
            StockQuoteService,
            HistoricalPricesService,
            MarketIndicesService,
            TradingVolumeService,
            FinancialRatiosService,
            DCFValuationService,
            TechnicalIndicatorsService,
        ]

        for service_class in service_classes:
            service = service_class(self.fmp_client, self.config_loader)  # type: ignore[abstract]
            self.services[service.name] = service

    def get_all_tools(self) -> list[Tool]:
        """Get all tool definitions from registered services.

        Returns:
            List of Tool definitions
        """
        return [service.get_tool_definition() for service in self.services.values()]

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        if tool_name not in self.services:
            return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]

        try:
            service = self.services[tool_name]
            return await service.execute(arguments)
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
