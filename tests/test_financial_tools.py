"""Test cases for financial data tools integration."""

from unittest.mock import patch

import pytest
from mcp.types import CallToolRequest, CallToolRequestParams

from mcp_financial_modeling_prep.fmp_client import FMPClient
from mcp_financial_modeling_prep.server import create_server


class TestFinancialTools:
    """Test the financial data tools integration."""

    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        return create_server("test_api_key")

    @pytest.fixture
    def fmp_client(self):
        """Create a test FMP client instance."""
        return FMPClient(api_key="test_key")

    @pytest.mark.asyncio
    async def test_get_company_profile_tool(self, server, fmp_client):
        """Test the get_company_profile tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "companyName": "Apple Inc.",
                    "industry": "Technology",
                    "website": "https://www.apple.com",
                    "description": "Apple Inc. technology company",
                }
            ]

            # Test the FMP client method directly first
            result = await fmp_client.get_company_profile("AAPL")
            assert result["symbol"] == "AAPL"
            assert result["companyName"] == "Apple Inc."

            # Now test the tool handler through the MCP server
            # Access the tool handler from request_handlers
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_company_profile", arguments={"symbol": "AAPL"}
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "Apple Inc." in result.root.content[0].text
            assert "Technology" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_get_income_statement_tool(self, server, fmp_client):
        """Test the get_income_statement tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "date": "2023-09-30",
                    "revenue": 383285000000,
                    "grossProfit": 169148000000,
                    "operatingIncome": 114301000000,
                    "netIncome": 96995000000,
                }
            ]

            # Test the FMP client method directly first
            result = await fmp_client.get_income_statement("AAPL")
            assert result["symbol"] == "AAPL"
            assert result["revenue"] == 383285000000

            # Now test the tool handler through the MCP server
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_income_statement", arguments={"symbol": "AAPL"}
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "383,285,000,000" in result.root.content[0].text
            assert "Revenue" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_get_stock_quote_tool(self, server, fmp_client):
        """Test the get_stock_quote tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "price": 150.25,
                    "changesPercentage": 1.25,
                    "change": 1.85,
                    "dayLow": 148.50,
                    "dayHigh": 152.00,
                    "yearHigh": 198.23,
                    "yearLow": 124.17,
                }
            ]

            # Test the FMP client method directly first
            result = await fmp_client.get_stock_quote("AAPL")
            assert result["symbol"] == "AAPL"
            assert result["price"] == 150.25

            # Now test the tool handler through the MCP server
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(name="get_stock_quote", arguments={"symbol": "AAPL"}),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "150.25" in result.root.content[0].text
            assert "1.25%" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server, fmp_client):
        """Test error handling in financial tools."""
        # Mock the underlying HTTP request to raise an exception
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.side_effect = Exception("API request failed")

            # Test that the client raises the exception
            with pytest.raises(Exception, match="API request failed"):
                await fmp_client.get_company_profile("INVALID")

            # Test that the tool handler catches and formats the error
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_company_profile", arguments={"symbol": "INVALID"}
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "Error" in result.root.content[0].text
            assert "API request failed" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_empty_api_key_handling(self):
        """Test handling of empty API key."""
        # Create client with empty API key
        client_empty_key = FMPClient(api_key="")

        # Test that the client raises ValueError for empty API key
        with pytest.raises(ValueError, match="API key is required"):
            await client_empty_key.get_company_profile("AAPL")

        # Test that the tool handler catches and formats the error
        # Create a server with empty API key
        server_empty_key = create_server("")
        tool_handler = server_empty_key.request_handlers[CallToolRequest]

        # Create a mock request
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="get_company_profile", arguments={"symbol": "AAPL"}),
        )

        # Call the handler
        result = await tool_handler(request)

        assert result.root.content[0].type == "text"
        assert "API key is required" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_invalid_symbol_handling(self, server, fmp_client):
        """Test handling of invalid stock symbols."""
        # Mock the underlying HTTP request to return empty array
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = []

            # Test that the client returns empty dict
            result = await fmp_client.get_company_profile("INVALID")
            assert result == {}

            # Test that the tool handler handles empty data
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_company_profile", arguments={"symbol": "INVALID"}
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "No data found" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_get_historical_prices_tool(self, server, fmp_client):
        """Test the get_historical_prices tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = {
                "symbol": "AAPL",
                "historical": [
                    {
                        "date": "2023-12-01",
                        "open": 189.37,
                        "high": 190.05,
                        "low": 187.45,
                        "close": 189.95,
                        "volume": 48744900,
                    },
                    {
                        "date": "2023-11-30",
                        "open": 190.90,
                        "high": 191.05,
                        "low": 189.88,
                        "close": 189.37,
                        "volume": 43014200,
                    },
                ],
            }

            # Test the FMP client method directly first
            from datetime import date

            from_date = date(2023, 11, 30)
            to_date = date(2023, 12, 1)
            result = await fmp_client.get_historical_prices("AAPL", from_date, to_date)
            assert len(result) == 2
            assert result[0]["date"] == "2023-12-01"

            # Now test the tool handler through the MCP server
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_historical_prices",
                    arguments={
                        "symbol": "AAPL",
                        "from_date": "2023-11-30",
                        "to_date": "2023-12-01",
                    },
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "Historical Prices for AAPL" in result.root.content[0].text
            assert "2023-12-01" in result.root.content[0].text
            assert "189.95" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_get_market_indices_tool(self, server, fmp_client):
        """Test the get_market_indices tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "^GSPC",
                    "name": "S&P 500",
                    "price": 4567.80,
                    "change": 12.34,
                    "changesPercentage": 0.27,
                },
                {
                    "symbol": "^DJI",
                    "name": "Dow Jones",
                    "price": 35678.90,
                    "change": -45.67,
                    "changesPercentage": -0.13,
                },
            ]

            # Test the FMP client method directly first
            result = await fmp_client.get_market_indices()
            assert len(result) == 2
            assert result[0]["symbol"] == "^GSPC"
            assert result[0]["name"] == "S&P 500"

            # Now test the tool handler through the MCP server
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_market_indices",
                    arguments={},
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "Market Indices" in result.root.content[0].text
            assert "S&P 500" in result.root.content[0].text
            assert "4567.80" in result.root.content[0].text

    @pytest.mark.asyncio
    async def test_get_trading_volume_tool(self, server, fmp_client):
        """Test the get_trading_volume tool handler."""
        # Mock the underlying HTTP request on the FMPClient class
        with patch(
            "mcp_financial_modeling_prep.fmp_client.FMPClient._make_request"
        ) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "volume": 48744900,
                    "avgVolume": 45000000,
                    "date": "2023-12-01",
                }
            ]

            # Test the FMP client method directly first
            result = await fmp_client.get_trading_volume("AAPL")
            assert result["symbol"] == "AAPL"
            assert result["volume"] == 48744900

            # Now test the tool handler through the MCP server
            tool_handler = server.request_handlers[CallToolRequest]

            # Create a mock request
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_trading_volume",
                    arguments={"symbol": "AAPL"},
                ),
            )

            # Call the handler
            result = await tool_handler(request)

            assert result.root.content[0].type == "text"
            assert "Trading Volume for AAPL" in result.root.content[0].text
            assert "48,744,900" in result.root.content[0].text
            assert "45,000,000" in result.root.content[0].text
