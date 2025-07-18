"""Integration tests for FMP API client.

These tests make actual HTTP requests to the Financial Modeling Prep API.
They require a valid FMP_API_KEY environment variable to be set.
These tests are marked as integration tests and can be run separately.
"""

import os
from datetime import date, timedelta

import pytest

from mcp_financial_modeling_prep.fmp_client import FMPClient, IndicatorType, TimeFrame

# Skip all tests in this module if FMP_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("FMP_API_KEY"), reason="FMP_API_KEY environment variable not set"
)


class TestFMPClientIntegration:
    """Integration tests for FMP API client."""

    @pytest.fixture
    def client(self):
        """Create FMP client with real API key."""
        api_key = os.getenv("FMP_API_KEY")
        return FMPClient(api_key=api_key)

    @pytest.fixture
    def test_symbol(self):
        """Test symbol to use for API calls."""
        return "AAPL"  # Apple Inc. - reliable test symbol

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_company_profile_integration(self, client, test_symbol):
        """Test get_company_profile with real API call."""
        result = await client.get_company_profile(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "companyName" in result
        assert "industry" in result
        assert "website" in result
        assert "description" in result

        # Verify Apple-specific data
        assert "Apple" in result["companyName"]
        assert result["website"] == "https://www.apple.com"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_income_statement_integration(self, client, test_symbol):
        """Test get_income_statement with real API call."""
        result = await client.get_income_statement(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "revenue" in result
        assert "netIncome" in result
        assert "date" in result
        assert "grossProfit" in result

        # Verify data types
        assert isinstance(result["revenue"], int | float)
        assert isinstance(result["netIncome"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_stock_quote_integration(self, client, test_symbol):
        """Test get_stock_quote with real API call."""
        result = await client.get_stock_quote(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "price" in result
        assert "change" in result
        assert "changesPercentage" in result
        assert "dayHigh" in result
        assert "dayLow" in result
        assert "volume" in result

        # Verify data types
        assert isinstance(result["price"], int | float)
        assert isinstance(result["volume"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_historical_prices_integration(self, client, test_symbol):
        """Test get_historical_prices with real API call."""
        # Test with date range (last 30 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        result = await client.get_historical_prices(test_symbol, start_date, end_date)

        # Verify response structure
        assert isinstance(result, list)
        assert len(result) > 0  # Should have historical data

        # Verify first entry structure
        first_entry = result[0]
        assert "date" in first_entry
        assert "open" in first_entry
        assert "high" in first_entry
        assert "low" in first_entry
        assert "close" in first_entry
        assert "volume" in first_entry

        # Verify data types
        assert isinstance(first_entry["open"], int | float)
        assert isinstance(first_entry["close"], int | float)
        assert isinstance(first_entry["volume"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_market_indices_integration(self, client):
        """Test get_market_indices with real API call."""
        result = await client.get_market_indices()

        # Verify response structure
        assert isinstance(result, list)
        assert len(result) > 0  # Should have market indices

        # Find S&P 500 index
        sp500 = next((idx for idx in result if "^GSPC" in idx.get("symbol", "")), None)
        assert sp500 is not None, "S&P 500 index not found in results"

        # Verify structure
        assert "symbol" in sp500
        assert "name" in sp500
        assert "price" in sp500
        assert "change" in sp500

        # Verify data types
        assert isinstance(sp500["price"], int | float)
        assert isinstance(sp500["change"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_trading_volume_integration(self, client, test_symbol):
        """Test get_trading_volume with real API call."""
        result = await client.get_trading_volume(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "volume" in result
        assert "avgVolume" in result

        # Verify data types
        assert isinstance(result["volume"], int | float)
        assert isinstance(result["avgVolume"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_financial_ratios_integration(self, client, test_symbol):
        """Test get_financial_ratios with real API call."""
        result = await client.get_financial_ratios(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "date" in result
        assert "currentRatio" in result
        assert "quickRatio" in result
        assert "returnOnEquity" in result
        assert "returnOnAssets" in result
        assert "debtEquityRatio" in result

        # Verify data types
        assert isinstance(result["currentRatio"], int | float)
        assert isinstance(result["returnOnEquity"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_dcf_valuation_integration(self, client, test_symbol):
        """Test get_dcf_valuation with real API call."""
        result = await client.get_dcf_valuation(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "date" in result
        assert "dcf" in result
        assert "Stock Price" in result

        # Verify data types
        assert isinstance(result["dcf"], int | float)
        assert isinstance(result["Stock Price"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_technical_indicators_integration(self, client, test_symbol):
        """Test get_technical_indicators with real API call."""
        # Test with default parameters
        result = await client.get_technical_indicators(test_symbol)

        # Verify response structure
        assert isinstance(result, list)
        assert len(result) > 0  # Should have indicator data

        # Verify first entry structure
        first_entry = result[0]
        assert "date" in first_entry
        assert "open" in first_entry
        assert "high" in first_entry
        assert "low" in first_entry
        assert "close" in first_entry
        assert "volume" in first_entry
        assert "sma" in first_entry  # Default indicator

        # Verify data types
        assert isinstance(first_entry["close"], int | float)
        assert isinstance(first_entry["sma"], int | float)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_technical_indicators_with_params_integration(self, client, test_symbol):
        """Test get_technical_indicators with specific parameters."""
        result = await client.get_technical_indicators(
            test_symbol, IndicatorType.RSI, 14, TimeFrame.DAY_1
        )

        # Verify response structure
        assert isinstance(result, list)
        assert len(result) > 0  # Should have indicator data

        # Verify first entry has RSI data
        first_entry = result[0]
        assert "date" in first_entry
        assert "rsi" in first_entry  # RSI indicator

        # Verify RSI value is within expected range (0-100)
        rsi_value = first_entry["rsi"]
        assert isinstance(rsi_value, int | float)
        assert 0 <= rsi_value <= 100

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_error_handling_integration(self, client):
        """Test API error handling with invalid symbol."""
        with pytest.raises(Exception) as exc_info:
            await client.get_company_profile("INVALID_SYMBOL_12345")

        # Verify error message contains API status code
        assert "API request failed" in str(exc_info.value)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_empty_response_handling_integration(self, client):
        """Test handling of empty responses."""
        # Use a symbol that might not have technical indicator data
        result = await client.get_technical_indicators("INVALID_SYMBOL_12345")

        # Should return empty list for invalid symbol
        assert isinstance(result, list)
        # Note: FMP API might return empty list or raise error - both are valid

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_balance_sheet_integration(self, client, test_symbol):
        """Test get_balance_sheet with real API call."""
        result = await client.get_balance_sheet(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "totalAssets" in result
        assert "totalLiabilities" in result
        assert "totalStockholdersEquity" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_cash_flow_integration(self, client, test_symbol):
        """Test get_cash_flow with real API call."""
        result = await client.get_cash_flow(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "operatingCashFlow" in result
        assert "freeCashFlow" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_key_metrics_integration(self, client, test_symbol):
        """Test get_key_metrics with real API call."""
        result = await client.get_key_metrics(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "marketCap" in result
        assert "enterpriseValue" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_enterprise_values_integration(self, client, test_symbol):
        """Test get_enterprise_values with real API call."""
        result = await client.get_enterprise_values(test_symbol)

        # Verify response structure
        assert isinstance(result, dict)
        assert result.get("symbol") == test_symbol
        assert "enterpriseValue" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_sector_performance_integration(self, client):
        """Test get_sector_performance with real API call."""
        result = await client.get_sector_performance()

        # Verify response structure
        assert isinstance(result, list)
        assert len(result) > 0  # Should have sector data

        # Check first sector entry
        first_sector = result[0]
        assert "sector" in first_sector
        assert "changesPercentage" in first_sector
