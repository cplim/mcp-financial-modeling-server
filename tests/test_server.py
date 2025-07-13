"""Test cases for the MCP server."""

import pytest
from mcp_financial_modeling_prep.server import create_server


class TestMCPServer:
    """Test the MCP server creation and basic functionality."""

    def test_server_creation(self):
        """Test that the MCP server can be created."""
        server = create_server()
        assert server is not None

    def test_server_has_name(self):
        """Test that the server has the correct name."""
        server = create_server()
        assert server.name == "financial-modeling-prep"

    def test_server_is_instance(self):
        """Test that the server is a proper MCP Server instance."""
        from mcp.server import Server
        server = create_server()
        assert isinstance(server, Server)