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
# Run all tests (unit tests only)
uv run pytest

# Run tests with coverage report
uv run pytest --cov=src/mcp_financial_modeling_prep --cov-report=term

# Run a single test file
uv run pytest tests/test_server.py
uv run pytest tests/test_financial_tools.py
uv run pytest tests/test_fmp_client.py
uv run pytest tests/test_services.py
uv run pytest tests/test_advanced_services.py
uv run pytest tests/test_config_loader.py

# Run a specific test
uv run pytest tests/test_server.py::TestMCPServer::test_server_creation
uv run pytest tests/test_financial_tools.py::TestFinancialTools::test_get_company_profile_tool
uv run pytest tests/test_services.py::TestCompanyProfileService::test_execute_success
uv run pytest tests/test_advanced_services.py::TestEnhancedDCFAnalysisService::test_execute_success
uv run pytest tests/test_config_loader.py::TestSchemaLoader::test_load_service_schema_with_valid_config

# Run integration tests (requires FMP_API_KEY)
export FMP_API_KEY="your_api_key_here"
uv run pytest tests/test_fmp_integration.py -m integration

# Run integration tests with helper script
python scripts/run_integration_tests.py
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
- **Tools**: 11 financial tools with schema-driven JSON schemas for input validation
- **Resources**: Provides financial analysis templates via custom URI scheme (`financial://`)
- **Prompts**: Defines structured prompts for financial analysis with typed arguments
- `main()`: Async entry point that runs the server using stdio communication
- **Service Architecture**: Uses ServiceRegistry with explicit SchemaLoader dependency injection

**Project Structure**:
- **src layout**: Source code in `src/mcp_financial_modeling_prep/` for proper packaging
- **Service Architecture**: Financial tools organized into service classes in `src/mcp_financial_modeling_prep/services/`
- **Schema-Driven**: JSON schema files in `src/mcp_financial_modeling_prep/schema/services/`
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
- Tool schemas use JSON Schema format for input validation loaded from configuration files
- Resources use Pydantic AnyUrl for URI handling
- Prompts use MCP PromptArgument types for structured arguments
- Explicit dependency injection: SchemaLoader → ServiceRegistry → Individual Services

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
- ✅ Tool handlers for Financial Modeling Prep API calls (11 tools implemented)
- ✅ Service abstraction pattern for maintainable architecture
- ✅ Enhanced error handling and validation (comprehensive)
- ✅ Full test coverage with proper MCP testing patterns (105 tests)
- ✅ Market data tools (historical prices, indices, trading volume)
- ✅ Financial analysis tools (ratios, DCF valuation, technical indicators)
- ✅ Technical indicators with enums, timeframes, and date range support
- ✅ MCP resources and prompts for financial analysis workflows
- ✅ Configuration-based resources and prompts (JSON files)
- ✅ Configuration-driven service schemas (JSON files)
- ✅ Advanced financial analysis tools (Enhanced DCF, Financial Health)
- 🚧 Docker containerization support (planned)
- 🚧 Additional advanced analysis tools (Sector Analysis, Portfolio Risk, etc.)

**Service Architecture Implementation**:
- **BaseFinancialService**: Abstract base class with required SchemaLoader dependency injection
- **Individual Services**: CompanyProfileService, IncomeStatementService, StockQuoteService, HistoricalPricesService, MarketIndicesService, TradingVolumeService, FinancialRatiosService, DCFValuationService, TechnicalIndicatorsService, EnhancedDCFAnalysisService, AdvancedFinancialHealthService
- **ServiceRegistry**: Manages service discovery and tool execution with explicit SchemaLoader dependency
- **Clean Separation**: Each service handles its own formatting and error handling, schemas are externalized
- **Extensibility**: New tools can be added by creating service classes and corresponding JSON schema files

**Configuration Architecture Implementation**:
- **SchemaLoader**: Loads MCP resources, prompts, and service schemas from JSON configuration files
- **Configuration Files**: 
  - `resources.json` and `prompts.json` in `/src/mcp_financial_modeling_prep/schema/`
  - Service schemas in `/src/mcp_financial_modeling_prep/schema/services/` (11 JSON files)
- **Clean Separation**: Business logic (services) vs Configuration (JSON files)
- **Extensibility**: New resources, prompts, and services can be added by modifying JSON configuration files
- **Testability**: Full test coverage for configuration loading with temporary files and explicit dependency injection

**Advanced Financial Analysis Tools**:
- **Enhanced DCF Analysis**: Levered DCF calculations with scenario modeling (bull/base/bear cases), financial health scoring, and investment thesis generation
- **Advanced Financial Health**: Comprehensive analysis including Altman Z-Score for bankruptcy prediction, Piotroski F-Score for financial strength, and overall financial strength rating
- **Sophisticated Calculations**: 
  - Levered DCF with enterprise value adjustments
  - Scenario-based DCF modeling with customizable growth rates
  - Multi-factor financial health scoring (liquidity, leverage, profitability, cash generation)
  - 9-point Piotroski F-Score with trend analysis
  - Color-coded investment recommendations based on quantitative analysis

**Testing Patterns**:
- Mock `FMPClient._make_request` at class level for comprehensive testing
- Use `CallToolRequest` and `CallToolRequestParams` for proper MCP testing
- Access results via `result.root.content[0].text` for ServerResult objects
- Test both successful data retrieval and error handling scenarios
- Service abstraction tests verify proper inheritance and interface compliance
- Integration tests ensure services work correctly through the registry
- Configuration-driven tests with temporary JSON files for schema validation

## Development Best Practices

- Always update documentation before committing and pushing code

## Adding New Financial Analysis Services

To add a new financial analysis service with the schema-driven architecture:

1. **Create Service Schema**: Add a JSON schema file in `src/mcp_financial_modeling_prep/schema/services/`
   - Name it `{service_name}.json` (e.g., `get_sector_analysis.json`)
   - Define input parameters, types, and validation rules
   - Follow JSON Schema specification

2. **Create Service Class**: Implement the service in `src/mcp_financial_modeling_prep/services/`
   - Inherit from `BaseFinancialService`
   - Implement `name`, `description`, and `execute` methods
   - `input_schema` is automatically loaded from JSON file
   - Constructor requires both `FMPClient` and `SchemaLoader`

3. **Register Service**: Add the service to `ServiceRegistry` in `registry.py`
   - Import the service class
   - Add to `service_classes` list in `_register_services()`

4. **Add Tests**: Create comprehensive tests following TDD approach
   - Use `config_loader` fixture for dependency injection
   - Mock `FMPClient._make_request` for isolated testing
   - Test both successful execution and error handling
   - Validate schema loading and input validation

5. **Update Integration Tests**: If new FMP API endpoints are used
   - Add integration tests to `test_fmp_integration.py`
   - Update `scripts/run_integration_tests.py` if needed

## Git Workflow Best Practices

- From now onwards create a new branch in git before making any code changes
- Once code has been committed, pushed and passes in CI, merge it back to main
- All branches should begin with 'feature/' prefix
- **Remember when renaming files, use 'git mv' rather than 'mv' to preserve history**

## API Documentation

- Remember that the API documentation is located here: https://site.financialmodelingprep.com/developer/docs