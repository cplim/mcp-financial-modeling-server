"""Test cases for financial data tools integration."""

from unittest.mock import patch

import pytest

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
        # Mock the underlying HTTP request
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

            # Test the FMP client method directly first
            result = await fmp_client.get_company_profile("AAPL")
            assert result["symbol"] == "AAPL"
            assert result["companyName"] == "Apple Inc."

            # Now test the tool handler (this will require implementing the handler)
            # Execute the tool
            result = await server._execute_tool(
                "get_company_profile", {"symbol": "AAPL"}
            )

            assert result["content"][0]["type"] == "text"
            assert "Apple Inc." in result["content"][0]["text"]
            assert "Technology" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_get_income_statement_tool(self, server, fmp_client):
        """Test the get_income_statement tool handler."""
        # Mock the underlying HTTP request
        with patch.object(fmp_client, "_make_request") as mock_request:
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

            # Now test the tool handler
            result = await server._execute_tool(
                "get_income_statement", {"symbol": "AAPL"}
            )

            assert result["content"][0]["type"] == "text"
            assert "383,285,000,000" in result["content"][0]["text"]
            assert "Revenue" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_get_stock_quote_tool(self, server, fmp_client):
        """Test the get_stock_quote tool handler."""
        # Mock the underlying HTTP request
        with patch.object(fmp_client, "_make_request") as mock_request:
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

            # Now test the tool handler
            result = await server._execute_tool("get_stock_quote", {"symbol": "AAPL"})

            assert result["content"][0]["type"] == "text"
            assert "150.25" in result["content"][0]["text"]
            assert "1.25%" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server, fmp_client):
        """Test error handling in financial tools."""
        # Mock the underlying HTTP request to raise an exception
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.side_effect = Exception("API request failed")

            # Test that the client raises the exception
            with pytest.raises(Exception, match="API request failed"):
                await fmp_client.get_company_profile("INVALID")

            # Test that the tool handler catches and formats the error
            result = await server._execute_tool(
                "get_company_profile", {"symbol": "INVALID"}
            )

            assert result["content"][0]["type"] == "text"
            assert "Error" in result["content"][0]["text"]
            assert "API request failed" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_empty_api_key_handling(self, server):
        """Test handling of empty API key."""
        # Create client with empty API key
        client_empty_key = FMPClient(api_key="")

        # Test that the client raises ValueError for empty API key
        with pytest.raises(ValueError, match="API key is required"):
            await client_empty_key.get_company_profile("AAPL")

        # Test that the tool handler catches and formats the error
        result = await server._execute_tool("get_company_profile", {"symbol": "AAPL"})

        assert result["content"][0]["type"] == "text"
        assert "API key is required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_invalid_symbol_handling(self, server, fmp_client):
        """Test handling of invalid stock symbols."""
        # Mock the underlying HTTP request to return empty array
        with patch.object(fmp_client, "_make_request") as mock_request:
            mock_request.return_value = []

            # Test that the client returns empty dict
            result = await fmp_client.get_company_profile("INVALID")
            assert result == {}

            # Test that the tool handler handles empty data
            result = await server._execute_tool(
                "get_company_profile", {"symbol": "INVALID"}
            )

            assert result["content"][0]["type"] == "text"
            assert "No data found" in result["content"][0]["text"]
