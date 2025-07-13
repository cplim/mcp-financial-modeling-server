# MCP Financial Modeling Prep Server

A Model Context Protocol (MCP) server that provides tools, resources, and prompts for financial analysis using the Financial Modeling Prep API.

## Features

- **Company Financial Data**: Income statements, balance sheets, cash flow statements
- **Market Data**: Real-time quotes, historical prices, market indices
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
mcp-financial-modeling-prep
```

## Development

This project uses Test-Driven Development (TDD) principles.

### Setup

```bash
git clone https://github.com/yourusername/mcp-financial-modeling-prep
cd mcp-financial-modeling-prep
uv sync --dev
```

### Testing

```bash
uv run pytest
```

### Code Quality

```bash
uv run black .
uv run ruff check .
uv run mypy .
```

## License

MIT License