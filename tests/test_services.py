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
        expected_methods = {"name", "description", "execute"}
        assert abstract_methods == expected_methods


class TestCompanyProfileService:
    """Test the company profile service."""

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client."""
        return FMPClient("test_key")

    @pytest.fixture
    def config_loader(self):
        """Create a test config loader."""
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        return ConfigLoader()

    @pytest.fixture
    def service(self, fmp_client, config_loader):
        """Create a company profile service instance."""
        from mcp_financial_modeling_prep.services.company_profile import CompanyProfileService

        return CompanyProfileService(fmp_client, config_loader)

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
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        config_loader = ConfigLoader()
        registry = ServiceRegistry(fmp_client, config_loader)

        assert registry.fmp_client == fmp_client
        assert registry.config_loader == config_loader
        assert hasattr(registry, "services")

    def test_registry_registers_services(self):
        """Test that registry registers all services."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        config_loader = ConfigLoader()
        registry = ServiceRegistry(fmp_client, config_loader)

        # Should register all expected services
        expected_services = [
            "get_company_profile",
            "get_income_statement",
            "get_stock_quote",
            "get_historical_prices",
            "get_market_indices",
            "get_trading_volume",
            "get_financial_ratios",
            "get_dcf_valuation",
            "get_technical_indicators",
        ]

        for service_name in expected_services:
            assert service_name in registry.services
            assert hasattr(registry.services[service_name], "execute")

    def test_registry_get_all_tools(self):
        """Test that registry returns all tool definitions."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        config_loader = ConfigLoader()
        registry = ServiceRegistry(fmp_client, config_loader)

        tools = registry.get_all_tools()

        assert len(tools) == 9  # Should have 9 tools
        assert all(isinstance(tool, Tool) for tool in tools)

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "get_company_profile",
            "get_income_statement",
            "get_stock_quote",
            "get_historical_prices",
            "get_market_indices",
            "get_trading_volume",
            "get_financial_ratios",
            "get_dcf_valuation",
            "get_technical_indicators",
        ]

        for name in expected_names:
            assert name in tool_names

    @pytest.mark.asyncio
    async def test_registry_execute_tool(self):
        """Test that registry can execute tools by name."""
        from mcp_financial_modeling_prep.services.registry import ServiceRegistry

        fmp_client = FMPClient("test_key")
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        config_loader = ConfigLoader()
        registry = ServiceRegistry(fmp_client, config_loader)

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
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        config_loader = ConfigLoader()
        registry = ServiceRegistry(fmp_client, config_loader)

        result = await registry.execute_tool("unknown_tool", {})

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown tool: unknown_tool" in result[0].text


class TestFinancialRatiosService:
    """Test the financial ratios service."""

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client."""
        return FMPClient("test_key")

    @pytest.fixture
    def config_loader(self):
        """Create a test config loader."""
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        return ConfigLoader()

    @pytest.fixture
    def service(self, fmp_client, config_loader):
        """Create a test financial ratios service."""
        from mcp_financial_modeling_prep.services.financial_ratios import FinancialRatiosService

        return FinancialRatiosService(fmp_client, config_loader)

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "get_financial_ratios"
        assert "financial ratios" in service.description.lower()
        assert service.input_schema["type"] == "object"
        assert "symbol" in service.input_schema["properties"]
        assert service.input_schema["required"] == ["symbol"]

    def test_get_tool_definition(self, service):
        """Test get_tool_definition method."""
        tool = service.get_tool_definition()
        assert tool.name == "get_financial_ratios"
        assert tool.description == service.description
        assert tool.inputSchema == service.input_schema

    @pytest.mark.asyncio
    async def test_execute_success(self, service, fmp_client):
        """Test successful execution of financial ratios service."""
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "date": "2023-12-31",
                    "currentRatio": 1.029,
                    "quickRatio": 0.985,
                    "debtEquityRatio": 1.969,
                    "returnOnEquity": 1.474,
                    "returnOnAssets": 0.223,
                    "grossProfitMargin": 0.441,
                    "netProfitMargin": 0.253,
                    "operatingProfitMargin": 0.298,
                }
            ]

            result = await service.execute({"symbol": "AAPL"})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "Financial Ratios for AAPL" in result[0].text
            assert "147.40%" in result[0].text  # ROE formatted as percentage
            assert "1.97" in result[0].text  # Debt-to-Equity ratio

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


class TestDCFValuationService:
    """Test the DCF valuation service."""

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client."""
        return FMPClient("test_key")

    @pytest.fixture
    def config_loader(self):
        """Create a test config loader."""
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        return ConfigLoader()

    @pytest.fixture
    def service(self, fmp_client, config_loader):
        """Create a test DCF valuation service."""
        from mcp_financial_modeling_prep.services.dcf_valuation import DCFValuationService

        return DCFValuationService(fmp_client, config_loader)

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "get_dcf_valuation"
        assert "dcf" in service.description.lower()
        assert service.input_schema["type"] == "object"
        assert "symbol" in service.input_schema["properties"]
        assert service.input_schema["required"] == ["symbol"]

    def test_get_tool_definition(self, service):
        """Test get_tool_definition method."""
        tool = service.get_tool_definition()
        assert tool.name == "get_dcf_valuation"
        assert tool.description == service.description
        assert tool.inputSchema == service.input_schema

    @pytest.mark.asyncio
    async def test_execute_success(self, service, fmp_client):
        """Test successful execution of DCF valuation service."""
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = [
                {"symbol": "AAPL", "date": "2023-12-31", "dcf": 181.50, "Stock Price": 193.60}
            ]

            result = await service.execute({"symbol": "AAPL"})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "DCF Valuation Analysis for AAPL" in result[0].text
            assert "$181.50" in result[0].text  # DCF value
            assert "$193.60" in result[0].text  # Stock price
            assert "Overvalued" in result[0].text  # Should show overvalued

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


class TestTechnicalIndicatorsService:
    """Test the technical indicators service."""

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client."""
        return FMPClient("test_key")

    @pytest.fixture
    def config_loader(self):
        """Create a test config loader."""
        from mcp_financial_modeling_prep.config.loader import ConfigLoader

        return ConfigLoader()

    @pytest.fixture
    def service(self, fmp_client, config_loader):
        """Create a test technical indicators service."""
        from mcp_financial_modeling_prep.services.technical_indicators import (
            TechnicalIndicatorsService,
        )

        return TechnicalIndicatorsService(fmp_client, config_loader)

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "get_technical_indicators"
        assert "technical" in service.description.lower()
        assert service.input_schema["type"] == "object"
        assert "symbol" in service.input_schema["properties"]
        assert "indicator_type" in service.input_schema["properties"]
        assert "period" in service.input_schema["properties"]
        assert "timeframe" in service.input_schema["properties"]
        assert "from_date" in service.input_schema["properties"]
        assert "to_date" in service.input_schema["properties"]
        assert service.input_schema["required"] == ["symbol"]

    def test_get_tool_definition(self, service):
        """Test get_tool_definition method."""
        tool = service.get_tool_definition()
        assert tool.name == "get_technical_indicators"
        assert tool.description == service.description
        assert tool.inputSchema == service.input_schema

    @pytest.mark.asyncio
    async def test_execute_success(self, service, fmp_client):
        """Test successful execution of technical indicators service."""
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = [
                {
                    "date": "2023-12-29",
                    "open": 193.11,
                    "high": 194.66,
                    "low": 193.11,
                    "close": 193.58,
                    "volume": 42628802,
                    "sma": 191.25,
                }
            ]

            result = await service.execute(
                {"symbol": "AAPL", "indicator_type": "sma", "period": 10}
            )

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "Technical Indicators for AAPL" in result[0].text
            assert "SMA (10-period)" in result[0].text
            assert "$191.25" in result[0].text

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
