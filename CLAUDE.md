# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

This project uses **uv** as the package manager exclusively. All commands should use uv.

### Development Setup
```bash
uv sync --dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=src/mcp_financial_modeling_prep --cov-report=term

# Run a single test file
uv run pytest tests/test_server.py
uv run pytest tests/test_financial_tools.py
uv run pytest tests/test_fmp_client.py
uv run pytest tests/test_services.py

# Run a specific test
uv run pytest tests/test_server.py::TestMCPServer::test_server_creation
uv run pytest tests/test_financial_tools.py::TestFinancialTools::test_get_company_profile_tool
uv run pytest tests/test_services.py::TestCompanyProfileService::test_execute_success
```

### Code Quality
```bash
# ALWAYS run before committing (required for CI to pass)
uv run black --check .
uv run ruff check .
uv run mypy .

# Fix auto-fixable linting issues
uv run ruff check . --fix

# Format code (run after fixing lint issues)
uv run black .

# Run all quality checks in one command
uv run black --check . && uv run ruff check . && uv run mypy .
```

### Build and Package
```bash
uv build
```

## Architecture Overview

This is a **Model Context Protocol (MCP) server** that integrates with the Financial Modeling Prep API to provide financial analysis tools, resources, and prompts.

### Key Architectural Components

**MCP Server Structure** (`src/mcp_financial_modeling_prep/server.py`):
- `create_server()`: Factory function that creates and configures the MCP server instance
- **Tools**: Six financial tools are defined with JSON schemas for input validation
- **Resources**: Provides financial analysis templates via custom URI scheme (`financial://`)
- **Prompts**: Defines structured prompts for financial analysis with typed arguments
- `main()`: Async entry point that runs the server using stdio communication
- **Service Architecture**: Uses ServiceRegistry for tool discovery and dispatch

**Project Structure**:
- **src layout**: Source code in `src/mcp_financial_modeling_prep/` for proper packaging
- **Service Architecture**: Financial tools organized into service classes in `src/mcp_financial_modeling_prep/services/`
- **Test-Driven Development**: Tests in `tests/` directory with pytest configuration
- **Type Safety**: Uses modern Python typing with mypy (relaxed mode for MCP compatibility)

### Development Methodology

**Test-Driven Development (TDD)**: 
- Write failing tests first, then implement functionality to pass them
- All new features should follow this pattern
- Current test coverage focuses on server creation and basic functionality

**Pre-Commit Requirements**:
- ALWAYS run `uv run black --check .` before committing
- ALWAYS run `uv run ruff check .` before committing  
- ALWAYS run `uv run mypy .` before committing
- CI will fail if any of these checks fail

**MCP Integration Points**:
- Server uses decorators (`@server.list_tools()`, `@server.list_resources()`, `@server.list_prompts()`) to register handlers
- Tool schemas use JSON Schema format for input validation
- Resources use Pydantic AnyUrl for URI handling
- Prompts use MCP PromptArgument types for structured arguments

### Configuration Details

**Python Version**: Requires Python >=3.10 (MCP library constraint)

**CI/CD Pipeline**: 
- Multi-Python version testing (3.10, 3.11, 3.12)
- Code quality gates: black formatting, ruff linting, mypy type checking
- Automatic builds on main branch pushes

**Package Management**:
- Uses uv with dependency groups for development tools
- All dependencies defined in pyproject.toml
- Development dependencies include pytest and code quality tools

## Environment Configuration

The server expects `FMP_API_KEY` environment variable for Financial Modeling Prep API access. This is required for the server to start - it will exit with an error if not provided.

## Important Implementation Notes

**MCP Server Lifecycle**: 
- Server communicates via stdio streams
- Uses async/await throughout for proper MCP protocol handling
- Server capabilities are defined through the MCP framework's get_capabilities() method

**Type Compatibility**:
- MyPy is configured in relaxed mode due to MCP library type compatibility
- Manual type annotations are added where needed for key functions
- Import statements use modern Python patterns (no typing.List, use list[T])

**Current Implementation Status**:
- ✅ FMP API client implementation (complete with TDD)
- ✅ Tool handlers for Financial Modeling Prep API calls (9 tools implemented)
- ✅ Service abstraction pattern for maintainable architecture
- ✅ Enhanced error handling and validation (comprehensive)
- ✅ Full test coverage with proper MCP testing patterns (86 tests)
- ✅ Market data tools (historical prices, indices, trading volume)
- ✅ Financial analysis tools (ratios, DCF valuation, technical indicators)
- ✅ MCP resources and prompts for financial analysis workflows
- ✅ Configuration-based resources and prompts (JSON files)
- 🚧 Docker containerization support (planned)
- 🚧 Advanced financial analysis tools (planned)

**Service Architecture Implementation**:
- **BaseFinancialService**: Abstract base class defining service interface
- **Individual Services**: CompanyProfileService, IncomeStatementService, StockQuoteService, HistoricalPricesService, MarketIndicesService, TradingVolumeService, FinancialRatiosService, DCFValuationService, TechnicalIndicatorsService
- **ServiceRegistry**: Manages service discovery and tool execution
- **Clean Separation**: Each service handles its own validation, formatting, and error handling
- **Extensibility**: New tools can be added by creating new service classes

**Configuration Architecture Implementation**:
- **ConfigLoader**: Loads MCP resources and prompts from JSON configuration files
- **Configuration Files**: `resources.json` and `prompts.json` in `/src/mcp_financial_modeling_prep/config/`
- **Clean Separation**: Tools (dynamic services) vs Resources/Prompts (static configurations)
- **Extensibility**: New resources and prompts can be added by modifying JSON configuration files
- **Testability**: Full test coverage for configuration loading with temporary files

**Testing Patterns**:
- Mock `FMPClient._make_request` at class level for comprehensive testing
- Use `CallToolRequest` and `CallToolRequestParams` for proper MCP testing
- Access results via `result.root.content[0].text` for ServerResult objects
- Test both successful data retrieval and error handling scenarios
- Service abstraction tests verify proper inheritance and interface compliance
- Integration tests ensure services work correctly through the registry

## Development Best Practices

- Always update documentation before committing and pushing code