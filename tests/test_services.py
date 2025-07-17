"""Test cases for financial services abstraction."""

from unittest.mock import patch

import pytest
from mcp.types import TextContent, Tool

from mcp_financial_modeling_prep.fmp_client import FMPClient


class TestBaseFinancialService:
    """Test the base financial service abstract class."""

    def test_base_service_is_abstract(self):
        """Test that BaseFinancialService cannot be instantiated directly."""
        from mcp_financial_modeling_prep.services.base import BaseFinancialService

        with pytest.raises(TypeError):
            BaseFinancialService(FMPClient("test_key"))

    def test_base_service_defines_required_methods(self):
        """Test that BaseFinancialService defines all required abstract methods."""
        from mcp_financial_modeling_prep.services.base import BaseFinancialService

        # Check that all required methods are defined as abstract
        abstract_methods = BaseFinancialService.__abstractmethods__
        expected_methods = {"name", "description", "input_schema", "execute"}
        assert abstract_methods == expected_methods


class TestCompanyProfileService:
    """Test the company profile service."""

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client."""
        return FMPClient("test_key")

    @pytest.fixture
    def service(self, fmp_client):
        """Create a company profile service instance."""
        from mcp_financial_modeling_prep.services.company_profile import CompanyProfileService

        return CompanyProfileService(fmp_client)

    def test_service_properties(self, service):
        """Test that service properties are correctly defined."""
        assert service.name == "get_company_profile"
        assert service.description == "Get company profile information"
        assert isinstance(service.input_schema, dict)
        assert service.input_schema["required"] == ["symbol"]

    def test_get_tool_definition(self, service):
        """Test that service returns correct tool definition."""
        tool = service.get_tool_definition()

        assert isinstance(tool, Tool)
        assert tool.name == "get_company_profile"
        assert tool.description == "Get company profile information"
        assert tool.inputSchema == service.input_schema

    @pytest.mark.asyncio
    async def test_execute_success(self, service, fmp_client):
        """Test successful execution of company profile service."""
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "companyName": "Apple Inc.",
                    "industry": "Technology",
                    "website": "https://www.apple.com",
                    "description": "Apple Inc. technology company",
                }
            ]

            result = await service.execute({"symbol": "AAPL"})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "Apple Inc." in result[0].text
            assert "Technology" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_missing_symbol(self, service):
        """Test execution with missing symbol."""
        result = await service.execute({})

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "Error: Symbol is required" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_no_data(self, service, fmp_client):
        """Test execution when no data is found."""
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = []

            result = await service.execute({"symbol": "INVALID"})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "No data found for symbol: INVALID" in result[0].text


class TestServiceRegistry:
    """Test the service registry."""

    def test_registry_initialization(self):
        """Test that service registry can be initialized."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        registry = ServiceRegistry(fmp_client)

        assert registry.fmp_client == fmp_client
        assert hasattr(registry, "services")

    def test_registry_registers_services(self):
        """Test that registry registers all services."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        registry = ServiceRegistry(fmp_client)

        # Should register all expected services
        expected_services = [
            "get_company_profile",
            "get_income_statement",
            "get_stock_quote",
            "get_historical_prices",
            "get_market_indices",
            "get_trading_volume",
        ]

        for service_name in expected_services:
            assert service_name in registry.services
            assert hasattr(registry.services[service_name], "execute")

    def test_registry_get_all_tools(self):
        """Test that registry returns all tool definitions."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        registry = ServiceRegistry(fmp_client)

        tools = registry.get_all_tools()

        assert len(tools) == 6  # Should have 6 tools
        assert all(isinstance(tool, Tool) for tool in tools)

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "get_company_profile",
            "get_income_statement",
            "get_stock_quote",
            "get_historical_prices",
            "get_market_indices",
            "get_trading_volume",
        ]

        for name in expected_names:
            assert name in tool_names

    @pytest.mark.asyncio
    async def test_registry_execute_tool(self):
        """Test that registry can execute tools by name."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        registry = ServiceRegistry(fmp_client)

        # Test executing a known tool
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "companyName": "Apple Inc."}]

            result = await registry.execute_tool("get_company_profile", {"symbol": "AAPL"})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Apple Inc." in result[0].text

    @pytest.mark.asyncio
    async def test_registry_execute_unknown_tool(self):
        """Test that registry handles unknown tools."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        registry = ServiceRegistry(fmp_client)

        result = await registry.execute_tool("unknown_tool", {})

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown tool: unknown_tool" in result[0].text
