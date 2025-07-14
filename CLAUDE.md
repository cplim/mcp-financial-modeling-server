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

# Run a specific test
uv run pytest tests/test_server.py::TestMCPServer::test_server_creation
uv run pytest tests/test_financial_tools.py::TestFinancialTools::test_get_company_profile_tool
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
- **Tools**: Three financial tools are defined (`get_company_profile`, `get_income_statement`, `get_stock_quote`) with JSON schemas for input validation
- **Resources**: Provides financial analysis templates via custom URI scheme (`financial://`)
- **Prompts**: Defines structured prompts for financial analysis with typed arguments
- `main()`: Async entry point that runs the server using stdio communication

**Project Structure**:
- **src layout**: Source code in `src/mcp_financial_modeling_prep/` for proper packaging
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
- ✅ Tool handlers for Financial Modeling Prep API calls (3 tools implemented)
- ✅ Enhanced error handling and validation (comprehensive)
- ✅ Full test coverage with proper MCP testing patterns
- 🚧 Docker containerization support (planned)
- 🚧 Additional financial tools (planned)

**Tool Handler Implementation**:
- Uses `@server.call_tool()` decorator for proper MCP protocol integration
- Returns `list[TextContent]` for formatted output
- Handles errors gracefully with user-friendly messages
- Integrates with `FMPClient` for actual API calls
- Tests use `server.request_handlers[CallToolRequest]` for proper MCP testing

**Testing Patterns**:
- Mock `FMPClient._make_request` at class level for comprehensive testing
- Use `CallToolRequest` and `CallToolRequestParams` for proper MCP testing
- Access results via `result.root.content[0].text` for ServerResult objects
- Test both successful data retrieval and error handling scenarios