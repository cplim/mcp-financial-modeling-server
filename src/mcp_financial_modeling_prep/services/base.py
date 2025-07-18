"""Base service class for financial data tools."""

from abc import ABC, abstractmethod
from typing import Any

from mcp.types import TextContent, Tool

from ..config.loader import ConfigLoader
from ..fmp_client import FMPClient


class BaseFinancialService(ABC):
    """Abstract base class for financial data services."""

    def __init__(self, fmp_client: FMPClient, config_loader: ConfigLoader):
        """Initialize the service with FMP client and config loader.

        Args:
            fmp_client: Financial Modeling Prep API client
            config_loader: Configuration loader for schemas
        """
        self.fmp_client = fmp_client
        self.config_loader = config_loader

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the service name (tool name)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the service description."""
        pass

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for input parameters.

        Loads schema from configuration file based on service name.
        Raises ValueError if no schema configuration is found.
        """
        schema = self.config_loader.load_service_schema(self.name)
        if not schema:
            raise ValueError(f"No schema configuration found for service: {self.name}")
        return schema

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the service with given arguments.

        Args:
            arguments: Tool arguments from MCP call

        Returns:
            List of TextContent responses
        """
        pass

    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition for this service."""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
        )

    def validate_symbol(self, arguments: dict[str, Any]) -> str | None:
        """Validate and extract symbol from arguments.

        Args:
            arguments: Tool arguments

        Returns:
            Symbol string if valid, None if invalid
        """
        symbol = arguments.get("symbol", "")
        if not symbol:
            return None
        return symbol

    def create_error_response(self, message: str) -> list[TextContent]:
        """Create an error response.

        Args:
            message: Error message

        Returns:
            List with single TextContent error response
        """
        return [TextContent(type="text", text=f"Error: {message}")]

    def create_no_data_response(self, symbol: str) -> list[TextContent]:
        """Create a no data found response.

        Args:
            symbol: Stock symbol

        Returns:
            List with single TextContent no data response
        """
        return [TextContent(type="text", text=f"No data found for symbol: {symbol}")]
