# MCP Financial Modeling Prep Server

A Model Context Protocol (MCP) server that provides tools, resources, and prompts for financial analysis using the Financial Modeling Prep API.

## Features

### ✅ Currently Implemented
- **Company Profile Data**: Get detailed company information including industry, website, and description
- **Income Statement**: Retrieve company financial statements with revenue, profit, and operating metrics
- **Real-time Stock Quotes**: Get current stock prices, changes, and daily/yearly ranges
- **Historical Stock Prices**: Get historical price data with optional date range filtering
- **Market Indices**: Get market indices data (S&P 500, NASDAQ, DOW) with current prices and changes
- **Trading Volume**: Get trading volume data including current and average volume
- **Financial Ratios**: Comprehensive ratio analysis including liquidity, profitability, and leverage ratios
- **DCF Valuation**: Discounted cash flow valuation with upside/downside analysis
- **Technical Indicators**: Technical analysis tools including SMA, EMA, RSI, MACD, and more
- **Service Architecture**: Clean, maintainable service abstraction pattern for easy extensibility
- **Error Handling**: Comprehensive error handling for API failures and invalid inputs
- **Data Validation**: Input validation and formatted output for all financial data

### 🚧 Planned Features
- **ESG Data**: Environmental, social, and governance ratings
- **Insider Trading**: Track insider transactions
- **Advanced Analysis**: Analyst estimates and earnings forecasts

### 📋 MCP Resources & Prompts
- **Configuration-Based**: Resources and prompts are loaded from JSON configuration files
- **Resources**: 3 financial analysis templates (configurable)
  - `financial://templates/analysis`: Comprehensive financial analysis templates
  - `financial://templates/report`: Financial report generation templates
  - `financial://templates/company`: Company analysis templates
- **Prompts**: 3 structured financial analysis workflows (configurable)
  - `analyze_company`: Complete company financial performance analysis
  - `technical_analysis`: Technical analysis with indicators and trends
  - `financial_health`: Financial health assessment with ratios and metrics
- **Architecture**: Clean separation between Tools (dynamic services) and Resources/Prompts (static configurations)

## Installation

```bash
uv add mcp-financial-modeling-prep
```

## Configuration

Set your Financial Modeling Prep API key:

```bash
export FMP_API_KEY="your_api_key_here"
```

## Usage

Run the MCP server:

```bash
# Make sure you have the FMP_API_KEY environment variable set
export FMP_API_KEY="your_api_key_here"

# Run the server
python -m mcp_financial_modeling_prep.server
```

### Available Tools

1. **get_company_profile**: Get detailed company information
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted company profile with name, industry, website, and description

2. **get_income_statement**: Get company financial statements
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted income statement with revenue, profits, and key metrics

3. **get_stock_quote**: Get real-time stock quotes
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted stock quote with price, changes, and trading ranges

4. **get_historical_prices**: Get historical stock price data
   - Input: `{"symbol": "AAPL", "from_date": "2023-01-01", "to_date": "2023-12-31"}`
   - Returns: Formatted historical prices with open, high, low, close, and volume data

5. **get_market_indices**: Get market indices information
   - Input: `{}` (no parameters required)
   - Returns: Formatted market indices data with current prices and changes

6. **get_trading_volume**: Get trading volume data
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted trading volume with current and average volume

7. **get_financial_ratios**: Get comprehensive financial ratios analysis
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted financial ratios including liquidity, profitability, and leverage ratios

8. **get_dcf_valuation**: Get DCF valuation analysis
   - Input: `{"symbol": "AAPL"}`
   - Returns: Formatted DCF valuation with fair value and upside/downside analysis

9. **get_technical_indicators**: Get technical analysis indicators
   - Input: `{"symbol": "AAPL", "indicator_type": "sma", "period": 20, "timeframe": "1day"}`
   - Returns: Formatted technical indicators with historical data and analysis
   - Supports multiple timeframes: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day
   - Supports multiple indicators: sma, ema, wma, dema, tema, williams, rsi, adx, standarddeviation
   - Optional date range filtering with from_date and to_date parameters

## Development

This project uses Test-Driven Development (TDD) principles.

### Setup

```bash
git clone https://github.com/cplim/mcp-financial-modeling-server
cd mcp-financial-modeling-server
uv sync --dev
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/mcp_financial_modeling_prep --cov-report=term

# Run specific test file
uv run pytest tests/test_financial_tools.py
```

### Code Quality

**Before every commit, run:**
```bash
uv run black --check .
uv run ruff check .
uv run mypy .
```

**To fix formatting issues:**
```bash
uv run ruff check . --fix
uv run black .
```

## Project Status

### ✅ Completed
- [x] Project setup with uv package manager
- [x] Git repository with GitHub integration
- [x] CI/CD pipeline with GitHub Actions
- [x] TDD framework with comprehensive tests
- [x] MCP server basic structure
- [x] FMP API client implementation
- [x] Financial data tools (6 tools implemented)
- [x] Market data tools (historical prices, indices, trading volume)
- [x] Financial analysis tools (ratios, DCF valuation, technical indicators)
- [x] Service abstraction pattern for maintainable architecture
- [x] Error handling and data validation
- [x] Code quality checks (black, ruff, mypy)

### 🚧 In Progress
- [ ] Re-enable 80% code coverage requirement in CI

### 📋 Planned
- [ ] Docker containerization
- [ ] Comprehensive documentation

### 🧪 Test Coverage
- **Total Tests**: 90 (all passing)
- **Test Files**: 5 (server, FMP client, financial tools, services, config loader)
- **Coverage**: Comprehensive mocking and integration testing including resources and prompts
- **Architecture**: Service abstraction pattern with individual service tests
- **Analysis Tools**: Complete TDD implementation for financial analysis services
- **Resources & Prompts**: Full test coverage for MCP resources and prompts functionality
- **Configuration**: Test coverage for configuration-based resource and prompt loading
- **Technical Indicators**: Enhanced API with enums, timeframes, and date range support

## License

MIT License