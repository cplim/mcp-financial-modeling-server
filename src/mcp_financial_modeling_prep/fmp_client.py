"""Financial Modeling Prep API client implementation."""

from datetime import date
from enum import Enum
from typing import Any

import httpx


class TimeFrame(Enum):
    """Time frame options for technical indicators."""

    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1hour"
    HOUR_4 = "4hour"
    DAY_1 = "1day"


class IndicatorType(Enum):
    """Technical indicator types."""

    SMA = "sma"  # Simple Moving Average
    EMA = "ema"  # Exponential Moving Average
    WMA = "wma"  # Weighted Moving Average
    DEMA = "dema"  # Double Exponential Moving Average
    TEMA = "tema"  # Triple Exponential Moving Average
    WILLIAMS = "williams"  # Williams %R
    RSI = "rsi"  # Relative Strength Index
    ADX = "adx"  # Average Directional Index
    STANDARDDEVIATION = "standarddeviation"  # Standard Deviation


class FMPClient:
    """Client for interacting with the Financial Modeling Prep API."""

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize the FMP client.

        Args:
            api_key: Financial Modeling Prep API key (required).
            base_url: Base URL for the FMP API. Defaults to
                'https://financialmodelingprep.com/api/v3'.
        """
        self.api_key = api_key
        self.base_url = base_url or "https://financialmodelingprep.com/api/v3"

    async def _make_request(self, endpoint: str) -> list[dict[str, Any]]:
        """Make a request to the FMP API.

        Args:
            endpoint: API endpoint to call

        Returns:
            API response data

        Raises:
            ValueError: If API key is not provided
            Exception: If API request fails
        """
        if not self.api_key:
            raise ValueError("API key is required for FMP API requests")

        url = f"{self.base_url}{endpoint}"
        params = {"apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(
                    f"API request failed with status {response.status_code}: " f"{response.text}"
                )

    async def get_company_profile(self, symbol: str) -> dict[str, Any]:
        """Get company profile information.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Company profile data
        """
        data = await self._make_request(f"/profile/{symbol}")
        return data[0] if data else {}

    async def get_income_statement(self, symbol: str) -> dict[str, Any]:
        """Get company income statement.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Income statement data
        """
        data = await self._make_request(f"/income-statement/{symbol}")
        return data[0] if data else {}

    async def get_stock_quote(self, symbol: str) -> dict[str, Any]:
        """Get real-time stock quote.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Stock quote data
        """
        data = await self._make_request(f"/quote/{symbol}")
        return data[0] if data else {}

    async def get_historical_prices(
        self, symbol: str, from_date: date | None = None, to_date: date | None = None
    ) -> list[dict[str, Any]]:
        """Get historical stock prices.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of historical price data
        """
        endpoint = f"/historical-price-full/{symbol}"
        params = []

        if from_date:
            params.append(f"from={from_date.isoformat()}")
        if to_date:
            params.append(f"to={to_date.isoformat()}")

        if params:
            endpoint += "?" + "&".join(params)

        data = await self._make_request(endpoint)

        # FMP historical API returns nested structure with 'historical' key
        if isinstance(data, dict) and "historical" in data:
            return data["historical"]
        elif isinstance(data, list):
            return data
        else:
            return []

    async def get_market_indices(self) -> list[dict[str, Any]]:
        """Get market indices data.

        Returns:
            List of market indices data
        """
        data = await self._make_request("/quotes/index")
        return data

    async def get_trading_volume(self, symbol: str) -> dict[str, Any]:
        """Get trading volume data.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Trading volume data
        """
        data = await self._make_request(f"/quote/{symbol}")
        return data[0] if data else {}

    async def get_financial_ratios(self, symbol: str) -> dict[str, Any]:
        """Get financial ratios for a company.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Financial ratios data
        """
        data = await self._make_request(f"/ratios/{symbol}")
        return data[0] if data else {}

    async def get_dcf_valuation(self, symbol: str) -> dict[str, Any]:
        """Get DCF valuation for a company.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            DCF valuation data
        """
        data = await self._make_request(f"/discounted-cash-flow/{symbol}")
        return data[0] if data else {}

    async def get_technical_indicators(
        self,
        symbol: str,
        indicator_type: IndicatorType | str | None = None,
        period: int | None = None,
        timeframe: TimeFrame | str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get technical indicators for a stock.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            indicator_type: Type of technical indicator (defaults to SMA)
            period: Period for the indicator calculation (defaults to 20)
            timeframe: Time frame for the data (defaults to 1day)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of technical indicator data
        """
        # Set defaults
        if indicator_type is None:
            indicator_type = IndicatorType.SMA
        if period is None:
            period = 20
        if timeframe is None:
            timeframe = TimeFrame.DAY_1

        # Convert enums to strings if needed
        if isinstance(indicator_type, IndicatorType):
            indicator_type = indicator_type.value
        if isinstance(timeframe, TimeFrame):
            timeframe = timeframe.value

        endpoint = f"/technical_indicator/{timeframe}/{symbol}"
        params = [f"period={period}", f"type={indicator_type}"]

        if from_date:
            params.append(f"from={from_date.isoformat()}")
        if to_date:
            params.append(f"to={to_date.isoformat()}")

        endpoint += "?" + "&".join(params)

        data = await self._make_request(endpoint)
        return data if isinstance(data, list) else []

    async def get_balance_sheet(self, symbol: str) -> dict[str, Any]:
        """Get company balance sheet statement.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Balance sheet data
        """
        data = await self._make_request(f"/balance-sheet-statement/{symbol}")
        return data[0] if data else {}

    async def get_cash_flow(self, symbol: str) -> dict[str, Any]:
        """Get company cash flow statement.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Cash flow statement data
        """
        data = await self._make_request(f"/cash-flow-statement/{symbol}")
        return data[0] if data else {}

    async def get_key_metrics(self, symbol: str) -> dict[str, Any]:
        """Get key financial metrics for a company.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Key metrics data
        """
        data = await self._make_request(f"/key-metrics/{symbol}")
        return data[0] if data else {}

    async def get_enterprise_values(self, symbol: str) -> dict[str, Any]:
        """Get enterprise value metrics for a company.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Enterprise value data
        """
        data = await self._make_request(f"/enterprise-values/{symbol}")
        return data[0] if data else {}

    async def get_sector_performance(self) -> list[dict[str, Any]]:
        """Get sector performance data.

        Returns:
            List of sector performance data
        """
        data = await self._make_request("/sectors-performance")
        return data if isinstance(data, list) else []
