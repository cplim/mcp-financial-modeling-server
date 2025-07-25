"""Test cases for the Financial Modeling Prep API client."""

from datetime import date
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

    def test_client_initialization_with_custom_base_url(self):
        """Test that the client can be initialized with custom base URL."""
        custom_url = "https://custom-api.example.com/v3"
        client = FMPClient(api_key="test_key", base_url=custom_url)
        assert client.api_key == "test_key"
        assert client.base_url == custom_url

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
    async def test_make_request_with_empty_api_key(self):
        """Test API request with empty API key raises error."""
        client = FMPClient(api_key="")

        with pytest.raises(ValueError) as exc_info:
            await client._make_request("/test")

        assert "API key is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_historical_prices(self):
        """Test getting historical stock prices."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
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

            from_date = date(2023, 11, 30)
            to_date = date(2023, 12, 1)
            result = await client.get_historical_prices("AAPL", from_date, to_date)

            assert len(result) == 2
            assert result[0]["date"] == "2023-12-01"
            assert result[0]["close"] == 189.95
            mock_request.assert_called_once_with(
                "/historical-price-full/AAPL?from=2023-11-30&to=2023-12-01"
            )

    @pytest.mark.asyncio
    async def test_get_market_indices(self):
        """Test getting market indices data."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
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

            result = await client.get_market_indices()

            assert len(result) == 2
            assert result[0]["symbol"] == "^GSPC"
            assert result[0]["name"] == "S&P 500"
            assert result[0]["price"] == 4567.80
            mock_request.assert_called_once_with("/quotes/index")

    @pytest.mark.asyncio
    async def test_get_trading_volume(self):
        """Test getting trading volume data."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {
                    "symbol": "AAPL",
                    "avgVolume": 45000000,
                    "volume": 48744900,
                    "date": "2023-12-01",
                }
            ]

            result = await client.get_trading_volume("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["avgVolume"] == 45000000
            assert result["volume"] == 48744900
            mock_request.assert_called_once_with("/quote/AAPL")

    @pytest.mark.asyncio
    async def test_get_historical_prices_empty_response(self):
        """Test historical prices with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            # Test empty dict response
            mock_request.return_value = {}
            result = await client.get_historical_prices("INVALID")
            assert result == []

            # Test empty list response
            mock_request.return_value = []
            result = await client.get_historical_prices("INVALID")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_historical_prices_no_dates(self):
        """Test historical prices without date parameters."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"symbol": "AAPL", "historical": []}

            result = await client.get_historical_prices("AAPL")

            assert result == []
            mock_request.assert_called_once_with("/historical-price-full/AAPL")

    @pytest.mark.asyncio
    async def test_get_market_indices_empty_response(self):
        """Test market indices with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            result = await client.get_market_indices()

            assert result == []
            mock_request.assert_called_once_with("/quotes/index")

    @pytest.mark.asyncio
    async def test_get_trading_volume_empty_response(self):
        """Test trading volume with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            result = await client.get_trading_volume("INVALID")

            assert result == {}
            mock_request.assert_called_once_with("/quote/INVALID")

    @pytest.mark.asyncio
    async def test_get_historical_prices_invalid_date_types(self):
        """Test historical prices with invalid date types."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"symbol": "AAPL", "historical": []}

            # Test with only from_date
            from_date = date(2023, 1, 1)
            result = await client.get_historical_prices("AAPL", from_date=from_date)

            assert result == []
            mock_request.assert_called_once_with("/historical-price-full/AAPL?from=2023-01-01")

            # Test with only to_date
            mock_request.reset_mock()
            to_date = date(2023, 12, 31)
            result = await client.get_historical_prices("AAPL", to_date=to_date)

            assert result == []
            mock_request.assert_called_once_with("/historical-price-full/AAPL?to=2023-12-31")

    @pytest.mark.asyncio
    async def test_get_income_statement(self):
        """Test getting income statement data."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "revenue": 1000000}]

            result = await client.get_income_statement("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["revenue"] == 1000000
            mock_request.assert_called_once_with("/income-statement/AAPL")

    @pytest.mark.asyncio
    async def test_get_company_profile(self):
        """Test getting company profile data."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "companyName": "Apple Inc."}]

            result = await client.get_company_profile("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["companyName"] == "Apple Inc."
            mock_request.assert_called_once_with("/profile/AAPL")

    @pytest.mark.asyncio
    async def test_get_company_profile_empty_response(self):
        """Test company profile with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            result = await client.get_company_profile("INVALID")

            assert result == {}
            mock_request.assert_called_once_with("/profile/INVALID")

    @pytest.mark.asyncio
    async def test_get_income_statement_empty_response(self):
        """Test income statement with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            result = await client.get_income_statement("INVALID")

            assert result == {}
            mock_request.assert_called_once_with("/income-statement/INVALID")

    @pytest.mark.asyncio
    async def test_get_stock_quote(self):
        """Test getting real-time stock quote."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [{"symbol": "AAPL", "price": 150.00}]

            result = await client.get_stock_quote("AAPL")

            assert result["symbol"] == "AAPL"
            assert result["price"] == 150.00
            mock_request.assert_called_once_with("/quote/AAPL")

    @pytest.mark.asyncio
    async def test_get_stock_quote_empty_response(self):
        """Test stock quote with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            result = await client.get_stock_quote("INVALID")

            assert result == {}
            mock_request.assert_called_once_with("/quote/INVALID")

    @pytest.mark.asyncio
    async def test_get_company_profile_api_error(self):
        """Test company profile with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 404")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_company_profile("INVALID")

    @pytest.mark.asyncio
    async def test_get_income_statement_api_error(self):
        """Test income statement with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 404")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_income_statement("INVALID")

    @pytest.mark.asyncio
    async def test_get_stock_quote_api_error(self):
        """Test stock quote with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 404")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_stock_quote("INVALID")

    @pytest.mark.asyncio
    async def test_get_historical_prices_api_error(self):
        """Test historical prices with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 404")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_historical_prices("INVALID")

    @pytest.mark.asyncio
    async def test_get_market_indices_api_error(self):
        """Test market indices with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 500")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_market_indices()

    @pytest.mark.asyncio
    async def test_get_trading_volume_api_error(self):
        """Test trading volume with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 404")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_trading_volume("INVALID")

    # Financial Analysis Tools Tests
    @pytest.mark.asyncio
    async def test_get_financial_ratios(self):
        """Test get_financial_ratios method."""
        client = FMPClient(api_key="test_key")
        mock_response = [
            {
                "symbol": "AAPL",
                "date": "2023-12-31",
                "currentRatio": 1.029,
                "quickRatio": 0.985,
                "cashRatio": 0.298,
                "daysOfSalesOutstanding": 62.443,
                "daysOfInventoryOutstanding": 10.636,
                "operatingCycle": 73.079,
                "daysOfPayablesOutstanding": 106.040,
                "cashConversionCycle": -32.961,
                "grossProfitMargin": 0.441,
                "operatingProfitMargin": 0.298,
                "pretaxProfitMargin": 0.299,
                "netProfitMargin": 0.253,
                "effectiveTaxRate": 0.152,
                "returnOnAssets": 0.223,
                "returnOnEquity": 1.474,
                "returnOnCapitalEmployed": 0.299,
                "netIncomePerEBT": 0.848,
                "ebtPerEbit": 1.001,
                "ebitPerRevenue": 0.298,
                "debtRatio": 0.318,
                "debtEquityRatio": 1.969,
                "longTermDebtToCapitalization": 0.663,
                "totalDebtToCapitalization": 0.663,
            }
        ]

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.get_financial_ratios("AAPL")

            assert result == mock_response[0]
            assert result["symbol"] == "AAPL"
            assert result["returnOnEquity"] == 1.474

    @pytest.mark.asyncio
    async def test_get_financial_ratios_empty_response(self):
        """Test get_financial_ratios with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_financial_ratios("INVALID")
            assert result == {}

    @pytest.mark.asyncio
    async def test_get_dcf_valuation(self):
        """Test get_dcf_valuation method."""
        client = FMPClient(api_key="test_key")
        mock_response = [
            {"symbol": "AAPL", "date": "2023-12-31", "dcf": 181.50, "Stock Price": 193.60}
        ]

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.get_dcf_valuation("AAPL")

            assert result == mock_response[0]
            assert result["symbol"] == "AAPL"
            assert result["dcf"] == 181.50

    @pytest.mark.asyncio
    async def test_get_dcf_valuation_empty_response(self):
        """Test get_dcf_valuation with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_dcf_valuation("INVALID")
            assert result == {}

    @pytest.mark.asyncio
    async def test_get_technical_indicators(self):
        """Test get_technical_indicators method."""
        from mcp_financial_modeling_prep.fmp_client import IndicatorType

        client = FMPClient(api_key="test_key")
        mock_response = [
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

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.get_technical_indicators("AAPL", IndicatorType.SMA, 10)

            assert result == mock_response
            assert result[0]["sma"] == 191.25
            mock_request.assert_called_once_with(
                "/technical_indicator/1day/AAPL?period=10&type=sma"
            )

    @pytest.mark.asyncio
    async def test_get_technical_indicators_empty_response(self):
        """Test get_technical_indicators with empty response."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_technical_indicators("INVALID")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_financial_ratios_api_error(self):
        """Test get_financial_ratios with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 500")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_financial_ratios("AAPL")

    @pytest.mark.asyncio
    async def test_get_dcf_valuation_api_error(self):
        """Test get_dcf_valuation with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 500")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_dcf_valuation("AAPL")

    @pytest.mark.asyncio
    async def test_get_technical_indicators_api_error(self):
        """Test get_technical_indicators with API error."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API request failed with status 500")

            with pytest.raises(Exception, match="API request failed"):
                await client.get_technical_indicators("AAPL")

    @pytest.mark.asyncio
    async def test_get_technical_indicators_with_defaults(self):
        """Test get_technical_indicators with default parameters."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_technical_indicators("AAPL")

            assert result == []
            mock_request.assert_called_once_with(
                "/technical_indicator/1day/AAPL?period=20&type=sma"
            )

    @pytest.mark.asyncio
    async def test_get_technical_indicators_with_enums(self):
        """Test get_technical_indicators with enum parameters."""
        from mcp_financial_modeling_prep.fmp_client import IndicatorType, TimeFrame

        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_technical_indicators(
                "AAPL", IndicatorType.RSI, 14, TimeFrame.HOUR_1
            )

            assert result == []
            mock_request.assert_called_once_with(
                "/technical_indicator/1hour/AAPL?period=14&type=rsi"
            )

    @pytest.mark.asyncio
    async def test_get_technical_indicators_with_strings(self):
        """Test get_technical_indicators with string parameters."""
        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            result = await client.get_technical_indicators("AAPL", "ema", 50, "5min")

            assert result == []
            mock_request.assert_called_once_with(
                "/technical_indicator/5min/AAPL?period=50&type=ema"
            )

    @pytest.mark.asyncio
    async def test_get_technical_indicators_with_dates(self):
        """Test get_technical_indicators with date parameters."""
        from datetime import date

        client = FMPClient(api_key="test_key")

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []
            from_date = date(2023, 1, 1)
            to_date = date(2023, 12, 31)
            result = await client.get_technical_indicators(
                "AAPL", from_date=from_date, to_date=to_date
            )

            assert result == []
            mock_request.assert_called_once_with(
                "/technical_indicator/1day/AAPL?period=20&type=sma&from=2023-01-01&to=2023-12-31"
            )
