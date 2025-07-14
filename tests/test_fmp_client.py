"""Test cases for the Financial Modeling Prep API client."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_financial_modeling_prep.fmp_client import FMPClient


class TestFMPClient:
    """Test the Financial Modeling Prep API client."""

    def test_client_initialization(self):
        """Test that the FMP client initializes correctly."""
        client = FMPClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        assert client.base_url == "https://financialmodelingprep.com/api/v3"

    def test_client_initialization_without_api_key(self):
        """Test that the client can be initialized without API key."""
        client = FMPClient()
        assert client.api_key is None
        assert client.base_url == "https://financialmodelingprep.com/api/v3"

    def test_client_initialization_with_custom_base_url(self):
        """Test that the client can be initialized with custom base URL."""
        custom_url = "https://custom-api.example.com/v3"
        client = FMPClient(api_key="test_key", base_url=custom_url)
        assert client.api_key == "test_key"
        assert client.base_url == custom_url

    @pytest.mark.asyncio
    async def test_get_company_profile(self):
        """Test getting company profile data."""
        client = FMPClient(api_key="test_key")

        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = [
                {"symbol": "AAPL", "companyName": "Apple Inc."}
            ]

            result = await client.get_company_profile("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["companyName"] == "Apple Inc."
            mock_request.assert_called_once_with("/profile/AAPL")

    @pytest.mark.asyncio
    async def test_get_income_statement(self):
        """Test getting income statement data."""
        client = FMPClient(api_key="test_key")

        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "revenue": 1000000}]

            result = await client.get_income_statement("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["revenue"] == 1000000
            mock_request.assert_called_once_with("/income-statement/AAPL")

    @pytest.mark.asyncio
    async def test_get_stock_quote(self):
        """Test getting real-time stock quote."""
        client = FMPClient(api_key="test_key")

        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "price": 150.00}]

            result = await client.get_stock_quote("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["price"] == 150.00
            mock_request.assert_called_once_with("/quote-short/AAPL")

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful API request."""
        client = FMPClient(api_key="test_key")

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response

            result = await client._make_request("/test")

            assert result == {"data": "test"}
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_error(self):
        """Test API request with error response."""
        client = FMPClient(api_key="test_key")

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await client._make_request("/test")

            assert "API request failed" in str(exc_info.value)
            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_without_api_key(self):
        """Test API request without API key raises error."""
        client = FMPClient()

        with pytest.raises(ValueError) as exc_info:
            await client._make_request("/test")

        assert "API key is required" in str(exc_info.value)
