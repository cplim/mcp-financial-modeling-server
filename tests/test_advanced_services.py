"""Test cases for advanced financial analysis services."""

from unittest.mock import patch

import pytest
from mcp.types import TextContent, Tool

from mcp_financial_modeling_prep.fmp_client import FMPClient


class TestEnhancedDCFAnalysisService:
    """Test the Enhanced DCF Analysis service."""

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
        """Create an enhanced DCF analysis service instance."""
        from mcp_financial_modeling_prep.services.enhanced_dcf import EnhancedDCFAnalysisService

        return EnhancedDCFAnalysisService(fmp_client, config_loader)

    def test_service_properties(self, service):
        """Test that service properties are correctly defined."""
        assert service.name == "get_enhanced_dcf_analysis"
        assert "enhanced" in service.description.lower()
        assert "dcf" in service.description.lower()
        assert isinstance(service.input_schema, dict)
        assert service.input_schema["type"] == "object"
        assert "symbol" in service.input_schema["properties"]
        assert service.input_schema["required"] == ["symbol"]

    def test_get_tool_definition(self, service):
        """Test that the service can generate a proper tool definition."""
        tool = service.get_tool_definition()
        assert isinstance(tool, Tool)
        assert tool.name == "get_enhanced_dcf_analysis"
        assert tool.description == service.description
        assert tool.inputSchema == service.input_schema

    @patch("mcp_financial_modeling_prep.fmp_client.FMPClient._make_request")
    async def test_execute_success(self, mock_make_request, service):
        """Test successful execution of enhanced DCF analysis."""

        # Mock API responses based on endpoint
        def mock_response(endpoint):
            if "/discounted-cash-flow/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "date": "2023-12-31",
                        "dcf": 180.50,
                        "Stock Price": 150.00,
                    }
                ]
            elif "/balance-sheet-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "totalDebt": 123456789000,
                        "totalStockholdersEquity": 789012345000,
                        "totalCurrentAssets": 400000000000,
                        "totalCurrentLiabilities": 200000000000,
                        "cashAndCashEquivalents": 50000000000,
                    }
                ]
            elif "/cash-flow-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "operatingCashFlow": 12345678900,
                        "freeCashFlow": 9876543210,
                    }
                ]
            elif "/key-metrics/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "enterpriseValue": 2500000000000,
                        "marketCap": 2400000000000,
                        "beta": 1.2,
                        "returnOnEquity": 0.12,
                    }
                ]
            return []

        mock_make_request.side_effect = mock_response

        # Execute the service
        result = await service.execute({"symbol": "AAPL"})

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"

        # Check that the result contains enhanced DCF analysis
        content = result[0].text
        assert "Enhanced DCF Analysis" in content
        assert "AAPL" in content
        assert "Levered DCF" in content
        assert "SCENARIO ANALYSIS" in content
        assert "FINANCIAL HEALTH METRICS" in content

        # Verify API calls were made
        assert mock_make_request.call_count == 4
        mock_make_request.assert_any_call("/discounted-cash-flow/AAPL")
        mock_make_request.assert_any_call("/balance-sheet-statement/AAPL")
        mock_make_request.assert_any_call("/cash-flow-statement/AAPL")
        mock_make_request.assert_any_call("/key-metrics/AAPL")

    @patch("mcp_financial_modeling_prep.fmp_client.FMPClient._make_request")
    async def test_execute_with_scenario_parameters(self, mock_make_request, service):
        """Test execution with scenario analysis parameters."""

        # Mock API responses based on endpoint
        def mock_response(endpoint):
            if "/discounted-cash-flow/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "date": "2023-12-31",
                        "dcf": 180.50,
                        "Stock Price": 150.00,
                    }
                ]
            elif "/balance-sheet-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "totalDebt": 100000000000,
                        "totalStockholdersEquity": 500000000000,
                    }
                ]
            elif "/cash-flow-statement/" in endpoint:
                return [{"symbol": "AAPL", "freeCashFlow": 10000000000}]
            elif "/key-metrics/" in endpoint:
                return [{"symbol": "AAPL", "marketCap": 2400000000000, "beta": 1.2}]
            return []

        mock_make_request.side_effect = mock_response

        # Execute with scenario parameters
        result = await service.execute(
            {
                "symbol": "AAPL",
                "growth_scenarios": {"bull": 0.15, "base": 0.10, "bear": 0.05},
                "discount_rate_adjustment": 0.02,
            }
        )

        # Verify result contains scenario analysis
        assert isinstance(result, list)
        assert len(result) == 1
        content = result[0].text
        assert "Bull Case" in content
        assert "Base Case" in content
        assert "Bear Case" in content

    @patch("mcp_financial_modeling_prep.fmp_client.FMPClient._make_request")
    async def test_execute_no_data(self, mock_make_request, service):
        """Test execution when no DCF data is available."""
        mock_make_request.return_value = []

        result = await service.execute({"symbol": "INVALID"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "No data found for symbol: INVALID" in result[0].text

    async def test_execute_invalid_symbol(self, service):
        """Test execution with invalid symbol."""
        result = await service.execute({"symbol": ""})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "Symbol is required" in result[0].text

    def test_input_schema_validation(self, service):
        """Test that input schema supports advanced parameters."""
        schema = service.input_schema
        properties = schema["properties"]

        # Required fields
        assert "symbol" in properties
        assert schema["required"] == ["symbol"]

        # Optional advanced parameters
        assert "growth_scenarios" in properties
        assert "discount_rate_adjustment" in properties
        assert "terminal_growth_rate" in properties
        assert "tax_rate" in properties

        # Check parameter types
        assert properties["growth_scenarios"]["type"] == "object"
        assert properties["discount_rate_adjustment"]["type"] == "number"
        assert properties["terminal_growth_rate"]["type"] == "number"
        assert properties["tax_rate"]["type"] == "number"


class TestAdvancedFinancialHealthService:
    """Test the Advanced Financial Health service."""

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
        """Create an advanced financial health service instance."""
        from mcp_financial_modeling_prep.services.advanced_financial_health import (
            AdvancedFinancialHealthService,
        )

        return AdvancedFinancialHealthService(fmp_client, config_loader)

    def test_service_properties(self, service):
        """Test that service properties are correctly defined."""
        assert service.name == "get_advanced_financial_health"
        assert "financial health" in service.description.lower()
        assert "altman" in service.description.lower()
        assert "piotroski" in service.description.lower()
        assert isinstance(service.input_schema, dict)

    @patch("mcp_financial_modeling_prep.fmp_client.FMPClient._make_request")
    async def test_execute_success(self, mock_make_request, service):
        """Test successful execution of advanced financial health analysis."""

        # Mock API responses based on endpoint
        def mock_response(endpoint):
            if "/balance-sheet-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "totalAssets": 1000000000000,
                        "totalCurrentAssets": 400000000000,
                        "totalCurrentLiabilities": 200000000000,
                        "totalLiabilities": 300000000000,
                        "totalStockholdersEquity": 700000000000,
                        "retainedEarnings": 500000000000,
                        "longTermDebt": 100000000000,
                    }
                ]
            elif "/income-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "revenue": 400000000000,
                        "ebitda": 120000000000,
                        "netIncome": 90000000000,
                        "grossProfit": 180000000000,
                    }
                ]
            elif "/cash-flow-statement/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "operatingCashFlow": 100000000000,
                        "freeCashFlow": 80000000000,
                    }
                ]
            elif "/key-metrics/" in endpoint:
                return [
                    {
                        "symbol": "AAPL",
                        "marketCap": 2400000000000,
                        "sharesOutstanding": 16000000000,
                        "returnOnAssets": 0.09,
                        "returnOnEquity": 0.12,
                    }
                ]
            return []

        mock_make_request.side_effect = mock_response

        # Execute the service
        result = await service.execute({"symbol": "AAPL"})

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"

        # Check that the result contains financial health analysis
        content = result[0].text
        assert "Advanced Financial Health Analysis" in content
        assert "Altman Z-Score" in content
        assert "Piotroski F-Score" in content
        assert "Financial Strength Rating" in content
        assert "AAPL" in content

    async def test_altman_z_score_calculation(self, service):
        """Test that Altman Z-Score is calculated correctly."""
        # This test will verify the calculation logic once implemented
        # For now, we're just setting up the test structure
        pass

    async def test_piotroski_f_score_calculation(self, service):
        """Test that Piotroski F-Score is calculated correctly."""
        # This test will verify the calculation logic once implemented
        # For now, we're just setting up the test structure
        pass


# TODO: Implement SectorAnalysisService tests when the service is implemented
# class TestSectorAnalysisService:
#     """Test the Sector Analysis service."""
