"""Test cases for the MCP server."""

import pytest

from mcp_financial_modeling_prep.server import create_server


class TestMCPServer:
    """Test the MCP server creation and basic functionality."""

    def test_server_creation(self):
        """Test that the MCP server can be created."""
        server = create_server("test_api_key")
        assert server is not None

    def test_server_has_name(self):
        """Test that the server has the correct name."""
        server = create_server("test_api_key")
        assert server.name == "financial-modeling-prep"

    def test_server_is_instance(self):
        """Test that the server is a proper MCP Server instance."""
        from mcp.server import Server

        server = create_server("test_api_key")
        assert isinstance(server, Server)

    @pytest.fixture
    def server(self):
        """Create a server instance for testing."""
        return create_server("test_api_key")

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test that server lists available tools."""
        from mcp.types import ListToolsRequest

        tools_handler = server.request_handlers[ListToolsRequest]
        tools_result = await tools_handler(ListToolsRequest(method="tools/list"))
        tools = tools_result.root.tools

        assert len(tools) == 9  # Should have 9 tools
        tool_names = [tool.name for tool in tools]
        assert "get_company_profile" in tool_names
        assert "get_stock_quote" in tool_names
        assert "get_financial_ratios" in tool_names

    @pytest.mark.asyncio
    async def test_list_resources(self, server):
        """Test that server lists available resources."""
        from mcp.types import ListResourcesRequest

        resources_handler = server.request_handlers[ListResourcesRequest]
        resources_result = await resources_handler(ListResourcesRequest(method="resources/list"))
        resources = resources_result.root.resources

        assert len(resources) >= 3  # Should have at least 3 resources
        resource_names = [resource.name for resource in resources]
        assert "Financial Analysis Templates" in resource_names
        assert "Financial Report Templates" in resource_names
        assert "Company Analysis Templates" in resource_names

        # Check that URIs are properly formatted
        resource_uris = [str(resource.uri) for resource in resources]
        assert "financial://templates/analysis" in resource_uris
        assert "financial://templates/report" in resource_uris
        assert "financial://templates/company" in resource_uris

    @pytest.mark.asyncio
    async def test_list_prompts(self, server):
        """Test that server lists available prompts."""
        from mcp.types import ListPromptsRequest

        prompts_handler = server.request_handlers[ListPromptsRequest]
        prompts_result = await prompts_handler(ListPromptsRequest(method="prompts/list"))
        prompts = prompts_result.root.prompts

        assert len(prompts) >= 3  # Should have at least 3 prompts
        prompt_names = [prompt.name for prompt in prompts]
        assert "analyze_company" in prompt_names
        assert "technical_analysis" in prompt_names
        assert "financial_health" in prompt_names

        # Check that all prompts have required arguments
        analyze_company_prompt = next((p for p in prompts if p.name == "analyze_company"), None)
        assert analyze_company_prompt is not None
        assert len(analyze_company_prompt.arguments) >= 1
        assert any(arg.name == "symbol" for arg in analyze_company_prompt.arguments)

        technical_analysis_prompt = next(
            (p for p in prompts if p.name == "technical_analysis"), None
        )
        assert technical_analysis_prompt is not None
        assert len(technical_analysis_prompt.arguments) >= 2
        assert any(arg.name == "symbol" for arg in technical_analysis_prompt.arguments)
        assert any(arg.name == "period" for arg in technical_analysis_prompt.arguments)


class TestServerTransportSupport:
    """Test server transport selection and argument parsing."""

    def test_parse_args_default_stdio(self):
        """Test that default arguments select stdio transport."""
        from mcp_financial_modeling_prep.server import parse_args
        from unittest.mock import patch

        with patch("sys.argv", ["server.py"]):
            args = parse_args()
            assert args.transport == "stdio"

    def test_parse_args_stdio_transport(self):
        """Test that stdio transport can be explicitly selected."""
        from mcp_financial_modeling_prep.server import parse_args
        from unittest.mock import patch

        with patch("sys.argv", ["server.py", "--transport", "stdio"]):
            args = parse_args()
            assert args.transport == "stdio"

    def test_parse_args_http_transport(self):
        """Test that HTTP transport can be selected."""
        from mcp_financial_modeling_prep.server import parse_args
        from unittest.mock import patch

        with patch("sys.argv", ["server.py", "--transport", "http"]):
            args = parse_args()
            assert args.transport == "http"
            assert args.host == "127.0.0.1"
            assert args.port == 8000

    def test_parse_args_http_with_custom_host_port(self):
        """Test that HTTP transport accepts custom host and port."""
        from mcp_financial_modeling_prep.server import parse_args
        from unittest.mock import patch

        with patch(
            "sys.argv",
            ["server.py", "--transport", "http", "--host", "127.0.0.1", "--port", "9000"],
        ):
            args = parse_args()
            assert args.transport == "http"
            assert args.host == "127.0.0.1"
            assert args.port == 9000

    def test_parse_args_invalid_transport_raises_error(self):
        """Test that invalid transport choice raises error."""
        from mcp_financial_modeling_prep.server import parse_args
        from unittest.mock import patch
        import pytest

        with patch("sys.argv", ["server.py", "--transport", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    @pytest.mark.asyncio
    async def test_main_with_stdio_transport(self):
        """Test main function with stdio transport."""
        from mcp_financial_modeling_prep.server import main
        from unittest.mock import patch, AsyncMock, MagicMock
        import os

        # Mock environment variable
        with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
            with patch("sys.argv", ["server.py", "--transport", "stdio"]):
                with patch(
                    "mcp_financial_modeling_prep.server.create_transport"
                ) as mock_create_transport:
                    mock_transport = AsyncMock()
                    mock_create_transport.return_value = mock_transport

                    await main()

                    mock_create_transport.assert_called_once_with("stdio")
                    mock_transport.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_http_transport(self):
        """Test main function with HTTP transport."""
        from mcp_financial_modeling_prep.server import main
        from unittest.mock import patch, AsyncMock, MagicMock
        import os

        # Mock environment variable
        with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
            with patch(
                "sys.argv",
                ["server.py", "--transport", "http", "--host", "127.0.0.1", "--port", "9000"],
            ):
                with patch(
                    "mcp_financial_modeling_prep.server.create_transport"
                ) as mock_create_transport:
                    mock_transport = AsyncMock()
                    mock_create_transport.return_value = mock_transport

                    await main()

                    mock_create_transport.assert_called_once_with(
                        "http", host="127.0.0.1", port=9000
                    )
                    mock_transport.run.assert_called_once()

    def test_main_missing_api_key_exits(self):
        """Test that main function exits when FMP_API_KEY is missing."""
        from mcp_financial_modeling_prep.server import main
        from unittest.mock import patch
        import os
        import pytest
        import asyncio

        # Remove FMP_API_KEY from environment
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["server.py"]):
                with pytest.raises(SystemExit):
                    asyncio.run(main())
