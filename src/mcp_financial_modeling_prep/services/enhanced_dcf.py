"""Enhanced DCF analysis service with levered DCF and scenario modeling."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class EnhancedDCFAnalysisService(BaseFinancialService):
    """Service for enhanced DCF analysis including levered DCF and scenario modeling."""

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_enhanced_dcf_analysis"

    @property
    def description(self) -> str:
        """Return the service description."""
        return (
            "Perform enhanced DCF analysis with levered DCF, scenario modeling, "
            "and comprehensive financial health metrics"
        )

    def _calculate_levered_dcf(
        self,
        unlevered_dcf: float,
        total_debt: float,
        cash: float,
        shares_outstanding: float,
    ) -> float:
        """Calculate levered DCF (equity value per share).

        Args:
            unlevered_dcf: Unlevered DCF value
            total_debt: Total debt
            cash: Cash and cash equivalents
            shares_outstanding: Number of shares outstanding

        Returns:
            Levered DCF value per share
        """
        if shares_outstanding <= 0:
            return 0.0

        # Equity value = Enterprise value - Net debt
        enterprise_value = unlevered_dcf * shares_outstanding
        net_debt = total_debt - cash
        equity_value = enterprise_value - net_debt

        return equity_value / shares_outstanding

    def _calculate_scenario_dcf(
        self,
        base_dcf: float,
        growth_adjustment: float,
        discount_adjustment: float = 0.0,
    ) -> float:
        """Calculate DCF for different scenarios.

        Args:
            base_dcf: Base case DCF value
            growth_adjustment: Growth rate adjustment
            discount_adjustment: Discount rate adjustment

        Returns:
            Scenario-adjusted DCF value
        """
        # Simple scenario adjustment formula
        growth_factor = 1 + growth_adjustment
        discount_factor = 1 / (1 + discount_adjustment)

        return base_dcf * growth_factor * discount_factor

    def _calculate_financial_health_score(
        self,
        current_ratio: float,
        debt_to_equity: float,
        roe: float,
        free_cash_flow: float,
        revenue: float,
    ) -> tuple[float, str]:
        """Calculate financial health score.

        Args:
            current_ratio: Current assets / current liabilities
            debt_to_equity: Total debt / shareholders' equity
            roe: Return on equity
            free_cash_flow: Free cash flow
            revenue: Total revenue

        Returns:
            Tuple of (score, rating)
        """
        score = 0.0

        # Liquidity (25%)
        if current_ratio >= 2.0:
            score += 25
        elif current_ratio >= 1.5:
            score += 20
        elif current_ratio >= 1.0:
            score += 15

        # Leverage (25%)
        if debt_to_equity <= 0.3:
            score += 25
        elif debt_to_equity <= 0.5:
            score += 20
        elif debt_to_equity <= 1.0:
            score += 15

        # Profitability (25%)
        if roe >= 0.15:
            score += 25
        elif roe >= 0.10:
            score += 20
        elif roe >= 0.05:
            score += 15

        # Cash Generation (25%)
        if revenue > 0:
            fcf_margin = free_cash_flow / revenue
            if fcf_margin >= 0.15:
                score += 25
            elif fcf_margin >= 0.10:
                score += 20
            elif fcf_margin >= 0.05:
                score += 15

        # Determine rating
        if score >= 80:
            rating = "Excellent"
        elif score >= 60:
            rating = "Good"
        elif score >= 40:
            rating = "Fair"
        else:
            rating = "Poor"

        return score, rating

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the enhanced DCF analysis.

        Args:
            arguments: Tool arguments containing symbol and optional parameters

        Returns:
            List of TextContent with enhanced DCF analysis
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        try:
            # Get financial data
            dcf_data = await self.fmp_client.get_dcf_valuation(symbol)
            balance_sheet = await self.fmp_client.get_balance_sheet(symbol)
            cash_flow = await self.fmp_client.get_cash_flow(symbol)
            key_metrics = await self.fmp_client.get_key_metrics(symbol)

            if not dcf_data:
                return self.create_no_data_response(symbol)

            # Extract basic DCF values
            base_dcf = dcf_data.get("dcf", 0.0)
            stock_price = dcf_data.get("Stock Price", 0.0)
            date = dcf_data.get("date", "N/A")

            # Extract additional financial data
            total_debt = balance_sheet.get("totalDebt", 0.0)
            cash = balance_sheet.get("cashAndCashEquivalents", 0.0)
            stockholders_equity = balance_sheet.get("totalStockholdersEquity", 0.0)

            free_cash_flow = cash_flow.get("freeCashFlow", 0.0)

            market_cap = key_metrics.get("marketCap", 0.0)
            enterprise_value = key_metrics.get("enterpriseValue", 0.0)
            beta = key_metrics.get("beta", 1.0)

            # Calculate shares outstanding
            shares_outstanding = market_cap / stock_price if stock_price > 0 else 0

            # Calculate levered DCF
            levered_dcf = self._calculate_levered_dcf(
                base_dcf, total_debt, cash, shares_outstanding
            )

            # Get scenario parameters
            growth_scenarios = arguments.get(
                "growth_scenarios",
                {
                    "bull": 0.15,
                    "base": 0.10,
                    "bear": 0.05,
                },
            )
            discount_adjustment = arguments.get("discount_rate_adjustment", 0.0)

            # Calculate scenario DCF values
            bull_dcf = self._calculate_scenario_dcf(
                base_dcf, growth_scenarios.get("bull", 0.15), discount_adjustment
            )
            base_case_dcf = self._calculate_scenario_dcf(
                base_dcf, growth_scenarios.get("base", 0.10), discount_adjustment
            )
            bear_dcf = self._calculate_scenario_dcf(
                base_dcf, growth_scenarios.get("bear", 0.05), discount_adjustment
            )

            # Calculate financial health metrics
            current_ratio = balance_sheet.get("totalCurrentAssets", 0.0) / max(
                balance_sheet.get("totalCurrentLiabilities", 1.0), 1.0
            )
            debt_to_equity = total_debt / max(stockholders_equity, 1.0)
            roe = key_metrics.get("returnOnEquity", 0.0)
            revenue = cash_flow.get("revenue", balance_sheet.get("totalRevenue", 0.0))

            health_score, health_rating = self._calculate_financial_health_score(
                current_ratio, debt_to_equity, roe, free_cash_flow, revenue
            )

            # Calculate upside/downside
            upside_base = ((base_dcf - stock_price) / stock_price) * 100 if stock_price > 0 else 0
            upside_levered = (
                ((levered_dcf - stock_price) / stock_price) * 100 if stock_price > 0 else 0
            )

            # Format the enhanced DCF analysis
            formatted_text = f"""Enhanced DCF Analysis for {symbol}
Date: {date}

=== CORE VALUATION ===
Current Stock Price: ${stock_price:.2f}
Base DCF Fair Value: ${base_dcf:.2f}
Levered DCF Fair Value: ${levered_dcf:.2f}

Upside/Downside (Base): {upside_base:.1f}%
Upside/Downside (Levered): {upside_levered:.1f}%

=== SCENARIO ANALYSIS ===
Bull Case DCF: ${bull_dcf:.2f} ({growth_scenarios.get('bull', 0.15)*100:.1f}% growth)
Base Case DCF: ${base_case_dcf:.2f} ({growth_scenarios.get('base', 0.10)*100:.1f}% growth)
Bear Case DCF: ${bear_dcf:.2f} ({growth_scenarios.get('bear', 0.05)*100:.1f}% growth)

=== FINANCIAL HEALTH METRICS ===
Financial Health Score: {health_score:.1f}/100 ({health_rating})
Current Ratio: {current_ratio:.2f}
Debt-to-Equity: {debt_to_equity:.2f}
Return on Equity: {roe*100:.1f}%
Free Cash Flow: ${free_cash_flow/1e9:.1f}B

=== VALUATION CONTEXT ===
Market Cap: ${market_cap/1e9:.1f}B
Enterprise Value: ${enterprise_value/1e9:.1f}B
Beta: {beta:.2f}
Net Debt: ${(total_debt - cash)/1e9:.1f}B

=== INVESTMENT THESIS ==="""

            # Add investment thesis based on analysis
            if upside_levered > 20:
                formatted_text += (
                    f"\n🟢 STRONG BUY: {upside_levered:.1f}% upside with "
                    f"{health_rating.lower()} financial health"
                )
            elif upside_levered > 10:
                formatted_text += (
                    f"\n🟡 BUY: {upside_levered:.1f}% upside with "
                    f"{health_rating.lower()} financial health"
                )
            elif upside_levered > -10:
                formatted_text += (
                    f"\n🟠 HOLD: {upside_levered:.1f}% upside/downside with "
                    f"{health_rating.lower()} financial health"
                )
            else:
                formatted_text += (
                    f"\n🔴 SELL: {upside_levered:.1f}% downside with "
                    f"{health_rating.lower()} financial health"
                )

            return [TextContent(type="text", text=formatted_text)]

        except Exception as e:
            return self.create_error_response(f"Error performing enhanced DCF analysis: {str(e)}")
