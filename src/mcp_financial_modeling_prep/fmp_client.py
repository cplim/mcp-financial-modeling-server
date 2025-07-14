"""Financial Modeling Prep API client implementation."""

import os
from typing import Any

import httpx


class FMPClient:
    """Client for interacting with the Financial Modeling Prep API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """Initialize the FMP client.

        Args:
            api_key: Financial Modeling Prep API key. If not provided, will try to get
                from environment.
            base_url: Base URL for the FMP API. Defaults to
                'https://financialmodelingprep.com/api/v3'.
        """
        self.api_key = api_key or os.getenv("FMP_API_KEY")
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
                    f"API request failed with status {response.status_code}: "
                    f"{response.text}"
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
        data = await self._make_request(f"/quote-short/{symbol}")
        return data[0] if data else {}
