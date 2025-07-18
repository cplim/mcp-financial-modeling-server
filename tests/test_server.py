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
