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
- **Service Architecture**: Clean, maintainable service abstraction pattern for easy extensibility
- **Error Handling**: Comprehensive error handling for API failures and invalid inputs
- **Data Validation**: Input validation and formatted output for all financial data

### 🚧 Planned Features
- **Financial Analysis**: DCF valuation, financial ratios, analyst estimates
- **ESG Data**: Environmental, social, and governance ratings
- **Insider Trading**: Track insider transactions

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
- [x] Service abstraction pattern for maintainable architecture
- [x] Error handling and data validation
- [x] Code quality checks (black, ruff, mypy)

### 🚧 In Progress
- [ ] Re-enable 80% code coverage requirement in CI

### 📋 Planned
- [ ] Financial analysis tools
- [ ] Resources and prompts for financial analysis
- [ ] Docker containerization
- [ ] Comprehensive documentation

### 🧪 Test Coverage
- **Total Tests**: 49 (all passing)
- **Test Files**: 4 (server, FMP client, financial tools, services)
- **Coverage**: Comprehensive mocking and integration testing
- **Architecture**: Service abstraction pattern with individual service tests

## License

MIT License