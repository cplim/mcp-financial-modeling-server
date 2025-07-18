"""Advanced Financial Health service with Altman Z-Score and Piotroski F-Score."""

from typing import Any

from mcp.types import TextContent

from .base import BaseFinancialService


class AdvancedFinancialHealthService(BaseFinancialService):
    """Service for advanced financial health analysis including Altman Z-Score and Piotroski F-Score."""  # noqa: E501

    @property
    def name(self) -> str:
        """Return the service name."""
        return "get_advanced_financial_health"

    @property
    def description(self) -> str:
        """Return the service description."""
        return (
            "Perform advanced financial health analysis including "
            "Altman Z-Score and Piotroski F-Score"
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for input parameters."""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., AAPL)",
                }
            },
            "required": ["symbol"],
        }

    def _calculate_altman_z_score(
        self,
        working_capital: float,
        total_assets: float,
        retained_earnings: float,
        ebit: float,
        market_cap: float,
        total_liabilities: float,
        revenue: float,
    ) -> tuple[float, str]:
        """Calculate Altman Z-Score for bankruptcy prediction.

        Args:
            working_capital: Working capital (current assets - current liabilities)
            total_assets: Total assets
            retained_earnings: Retained earnings
            ebit: Earnings before interest and taxes
            market_cap: Market capitalization
            total_liabilities: Total liabilities
            revenue: Total revenue

        Returns:
            Tuple of (z_score, interpretation)
        """
        if total_assets <= 0:
            return 0.0, "Insufficient data"

        # Altman Z-Score formula:
        # Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        # Where:
        # A = Working Capital / Total Assets
        # B = Retained Earnings / Total Assets
        # C = EBIT / Total Assets
        # D = Market Cap / Total Liabilities
        # E = Revenue / Total Assets

        a = working_capital / total_assets
        b = retained_earnings / total_assets
        c = ebit / total_assets
        d = market_cap / max(total_liabilities, 1.0)
        e = revenue / total_assets

        z_score = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e

        # Interpretation
        if z_score > 2.99:
            interpretation = "Safe Zone - Low bankruptcy risk"
        elif z_score > 1.81:
            interpretation = "Gray Zone - Moderate bankruptcy risk"
        else:
            interpretation = "Distress Zone - High bankruptcy risk"

        return z_score, interpretation

    def _calculate_piotroski_f_score(
        self,
        net_income: float,
        operating_cash_flow: float,
        total_assets: float,
        current_assets: float,
        current_liabilities: float,
        long_term_debt: float,
        shares_outstanding: float,
        gross_margin: float,
        asset_turnover: float,
        roa: float,
        previous_year_data: dict[str, Any] | None = None,
    ) -> tuple[int, str]:
        """Calculate Piotroski F-Score for financial strength.

        Args:
            net_income: Net income
            operating_cash_flow: Operating cash flow
            total_assets: Total assets
            current_assets: Current assets
            current_liabilities: Current liabilities
            long_term_debt: Long-term debt
            shares_outstanding: Shares outstanding
            gross_margin: Gross margin
            asset_turnover: Asset turnover ratio
            roa: Return on assets
            previous_year_data: Previous year data for trend analysis

        Returns:
            Tuple of (f_score, interpretation)
        """
        score = 0

        # Profitability (4 points)
        # 1. Positive net income
        if net_income > 0:
            score += 1

        # 2. Positive return on assets
        if roa > 0:
            score += 1

        # 3. Positive operating cash flow
        if operating_cash_flow > 0:
            score += 1

        # 4. Operating cash flow > net income (quality of earnings)
        if operating_cash_flow > net_income:
            score += 1

        # Leverage, Liquidity, and Source of Funds (3 points)
        # 5. Decreased long-term debt ratio (year over year)
        if previous_year_data and previous_year_data.get("long_term_debt", 0) > 0:
            prev_debt_ratio = previous_year_data["long_term_debt"] / max(
                previous_year_data.get("total_assets", 1), 1
            )
            current_debt_ratio = long_term_debt / max(total_assets, 1)
            if current_debt_ratio < prev_debt_ratio:
                score += 1

        # 6. Increased current ratio (year over year)
        current_ratio = current_assets / max(current_liabilities, 1)
        if previous_year_data and previous_year_data.get("current_liabilities", 0) > 0:
            prev_current_ratio = previous_year_data.get("current_assets", 0) / max(
                previous_year_data["current_liabilities"], 1
            )
            if current_ratio > prev_current_ratio:
                score += 1

        # 7. No new shares issued (maintained or decreased shares outstanding)
        if previous_year_data and previous_year_data.get("shares_outstanding", 0) > 0:
            if shares_outstanding <= previous_year_data["shares_outstanding"]:
                score += 1

        # Operating Efficiency (2 points)
        # 8. Increased gross margin (year over year)
        if previous_year_data and previous_year_data.get("gross_margin", 0) > 0:
            if gross_margin > previous_year_data["gross_margin"]:
                score += 1

        # 9. Increased asset turnover (year over year)
        if previous_year_data and previous_year_data.get("asset_turnover", 0) > 0:
            if asset_turnover > previous_year_data["asset_turnover"]:
                score += 1

        # Interpretation
        if score >= 7:
            interpretation = "High Quality - Strong financial position"
        elif score >= 5:
            interpretation = "Good Quality - Solid financial position"
        elif score >= 3:
            interpretation = "Average Quality - Moderate financial position"
        else:
            interpretation = "Poor Quality - Weak financial position"

        return score, interpretation

    def _calculate_financial_strength_rating(
        self,
        altman_z_score: float,
        piotroski_f_score: int,
        current_ratio: float,
        debt_to_equity: float,
        roe: float,
        roa: float,
    ) -> tuple[int, str]:
        """Calculate overall financial strength rating.

        Args:
            altman_z_score: Altman Z-Score
            piotroski_f_score: Piotroski F-Score
            current_ratio: Current ratio
            debt_to_equity: Debt-to-equity ratio
            roe: Return on equity
            roa: Return on assets

        Returns:
            Tuple of (rating, description)
        """
        rating = 0.0

        # Altman Z-Score contribution (30%)
        if altman_z_score > 2.99:
            rating += 30
        elif altman_z_score > 1.81:
            rating += 20
        else:
            rating += 10

        # Piotroski F-Score contribution (30%)
        rating += (piotroski_f_score / 9) * 30

        # Liquidity contribution (15%)
        if current_ratio >= 2.0:
            rating += 15
        elif current_ratio >= 1.5:
            rating += 12
        elif current_ratio >= 1.0:
            rating += 8
        else:
            rating += 4

        # Leverage contribution (15%)
        if debt_to_equity <= 0.3:
            rating += 15
        elif debt_to_equity <= 0.6:
            rating += 12
        elif debt_to_equity <= 1.0:
            rating += 8
        else:
            rating += 4

        # Profitability contribution (10%)
        profit_score = (max(roe, 0) + max(roa, 0)) * 50  # Scale to 0-10
        rating += min(profit_score, 10)

        # Determine rating description
        if rating >= 85:
            description = "AAA - Excellent"
        elif rating >= 75:
            description = "AA - Very Good"
        elif rating >= 65:
            description = "A - Good"
        elif rating >= 55:
            description = "BBB - Satisfactory"
        elif rating >= 45:
            description = "BB - Speculative"
        elif rating >= 35:
            description = "B - Highly Speculative"
        else:
            description = "CCC - Substantial Risk"

        return int(rating), description

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the advanced financial health analysis.

        Args:
            arguments: Tool arguments containing symbol

        Returns:
            List of TextContent with advanced financial health analysis
        """
        symbol = self.validate_symbol(arguments)
        if not symbol:
            return self.create_error_response("Symbol is required")

        try:
            # Get financial data
            balance_sheet = await self.fmp_client.get_balance_sheet(symbol)
            income_statement = await self.fmp_client.get_income_statement(symbol)
            cash_flow = await self.fmp_client.get_cash_flow(symbol)
            key_metrics = await self.fmp_client.get_key_metrics(symbol)

            if not balance_sheet and not income_statement:
                return self.create_no_data_response(symbol)

            # Extract financial data
            total_assets = balance_sheet.get("totalAssets", 0.0)
            current_assets = balance_sheet.get("totalCurrentAssets", 0.0)
            current_liabilities = balance_sheet.get("totalCurrentLiabilities", 0.0)
            total_liabilities = balance_sheet.get("totalLiabilities", 0.0)
            retained_earnings = balance_sheet.get("retainedEarnings", 0.0)
            long_term_debt = balance_sheet.get("longTermDebt", 0.0)
            stockholders_equity = balance_sheet.get("totalStockholdersEquity", 0.0)

            revenue = income_statement.get("revenue", 0.0)
            net_income = income_statement.get("netIncome", 0.0)
            gross_profit = income_statement.get("grossProfit", 0.0)
            ebit = income_statement.get("ebitda", 0.0)  # Using EBITDA as proxy for EBIT

            operating_cash_flow = cash_flow.get("operatingCashFlow", 0.0)
            free_cash_flow = cash_flow.get("freeCashFlow", 0.0)

            market_cap = key_metrics.get("marketCap", 0.0)
            shares_outstanding = key_metrics.get("sharesOutstanding", 0.0)
            roe = key_metrics.get("returnOnEquity", 0.0)
            roa = key_metrics.get("returnOnAssets", 0.0)

            # Calculate derived metrics
            working_capital = current_assets - current_liabilities
            current_ratio = current_assets / max(current_liabilities, 1.0)
            debt_to_equity = total_liabilities / max(stockholders_equity, 1.0)
            gross_margin = gross_profit / max(revenue, 1.0)
            asset_turnover = revenue / max(total_assets, 1.0)

            # Calculate scores
            altman_z_score, altman_interpretation = self._calculate_altman_z_score(
                working_capital,
                total_assets,
                retained_earnings,
                ebit,
                market_cap,
                total_liabilities,
                revenue,
            )

            piotroski_f_score, piotroski_interpretation = self._calculate_piotroski_f_score(
                net_income,
                operating_cash_flow,
                total_assets,
                current_assets,
                current_liabilities,
                long_term_debt,
                shares_outstanding,
                gross_margin,
                asset_turnover,
                roa,
            )

            overall_rating, rating_description = self._calculate_financial_strength_rating(
                altman_z_score,
                piotroski_f_score,
                current_ratio,
                debt_to_equity,
                roe,
                roa,
            )

            # Format the analysis
            formatted_text = f"""Advanced Financial Health Analysis for {symbol}

=== FINANCIAL HEALTH SCORES ===
Altman Z-Score: {altman_z_score:.2f}
└─ {altman_interpretation}

Piotroski F-Score: {piotroski_f_score}/9
└─ {piotroski_interpretation}

Overall Financial Strength Rating: {overall_rating}/100 ({rating_description})

=== KEY FINANCIAL METRICS ===
Liquidity:
• Current Ratio: {current_ratio:.2f}
• Working Capital: ${working_capital/1e9:.1f}B

Leverage:
• Debt-to-Equity: {debt_to_equity:.2f}
• Long-term Debt: ${long_term_debt/1e9:.1f}B

Profitability:
• Return on Equity: {roe*100:.1f}%
• Return on Assets: {roa*100:.1f}%
• Gross Margin: {gross_margin*100:.1f}%

Cash Flow:
• Operating Cash Flow: ${operating_cash_flow/1e9:.1f}B
• Free Cash Flow: ${free_cash_flow/1e9:.1f}B

=== BANKRUPTCY RISK ANALYSIS ===
Altman Z-Score Components:
• Working Capital/Total Assets: {working_capital/max(total_assets, 1):.3f}
• Retained Earnings/Total Assets: {retained_earnings/max(total_assets, 1):.3f}
• EBIT/Total Assets: {ebit/max(total_assets, 1):.3f}
• Market Cap/Total Liabilities: {market_cap/max(total_liabilities, 1):.3f}
• Revenue/Total Assets: {revenue/max(total_assets, 1):.3f}

=== FINANCIAL STRENGTH SUMMARY ==="""

            # Add summary based on overall rating
            if overall_rating >= 75:
                formatted_text += (
                    f"\n🟢 STRONG: {symbol} demonstrates excellent financial health "
                    f"with low bankruptcy risk"
                )
            elif overall_rating >= 55:
                formatted_text += (
                    f"\n🟡 STABLE: {symbol} shows good financial health with manageable risk"
                )
            elif overall_rating >= 35:
                formatted_text += (
                    f"\n🟠 CAUTION: {symbol} has moderate financial health with some concerns"
                )
            else:
                formatted_text += (
                    f"\n🔴 WEAK: {symbol} shows poor financial health with significant risks"
                )

            return [TextContent(type="text", text=formatted_text)]

        except Exception as e:
            return self.create_error_response(
                f"Error performing financial health analysis: {str(e)}"
            )
