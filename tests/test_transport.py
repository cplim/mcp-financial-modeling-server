"""Test cases for transport abstraction layer."""

import pytest
from unittest.mock import AsyncMock, Mock

from mcp.server import Server


class TestTransportInterface:
    """Test the transport interface abstract base class."""

    def test_transport_interface_is_abstract(self):
        """Test that TransportInterface cannot be instantiated directly."""
        from mcp_financial_modeling_prep.transport import TransportInterface

        with pytest.raises(TypeError):
            TransportInterface()

    def test_transport_interface_defines_required_methods(self):
        """Test that TransportInterface defines all required abstract methods."""
        from mcp_financial_modeling_prep.transport import TransportInterface

        # Check that all required methods are defined as abstract
        abstract_methods = TransportInterface.__abstractmethods__
        expected_methods = {"run", "get_transport_info"}
        assert abstract_methods == expected_methods


class TestTransportFactory:
    """Test the transport factory functionality."""

    def test_transport_factory_creates_stdio_transport(self):
        """Test that factory creates stdio transport."""
        from mcp_financial_modeling_prep.transport import create_transport

        transport = create_transport("stdio")
        
        assert transport is not None
        assert transport.get_transport_info()["transport"] == "stdio"

    def test_transport_factory_creates_http_transport(self):
        """Test that factory creates HTTP transport."""
        from mcp_financial_modeling_prep.transport import create_transport

        transport = create_transport("http", host="localhost", port=8000)
        
        assert transport is not None
        transport_info = transport.get_transport_info()
        assert transport_info["transport"] == "streamable-http"
        assert transport_info["host"] == "localhost"
        assert transport_info["port"] == 8000

    def test_transport_factory_invalid_transport_raises_error(self):
        """Test that factory raises error for invalid transport type."""
        from mcp_financial_modeling_prep.transport import create_transport

        with pytest.raises(ValueError, match="Unsupported transport type"):
            create_transport("invalid")


class TestStdioTransport:
    """Test the stdio transport implementation."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server."""
        server = Mock(spec=Server)
        server.get_capabilities.return_value = {}
        return server

    def test_stdio_transport_properties(self):
        """Test stdio transport properties."""
        from mcp_financial_modeling_prep.transport.stdio import StdioTransport

        transport = StdioTransport()
        transport_info = transport.get_transport_info()
        
        assert transport_info["transport"] == "stdio"
        assert transport_info["usage"] == "subprocess"

    @pytest.mark.asyncio
    async def test_stdio_transport_run_calls_server(self, mock_server):
        """Test that stdio transport properly runs the server."""
        from mcp_financial_modeling_prep.transport.stdio import StdioTransport
        from unittest.mock import patch, AsyncMock

        transport = StdioTransport()
        
        # Mock the stdio server context manager
        with patch('mcp_financial_modeling_prep.transport.stdio.mcp.server.stdio.stdio_server') as mock_stdio:
            mock_streams = (AsyncMock(), AsyncMock())
            mock_stdio.return_value.__aenter__.return_value = mock_streams
            mock_stdio.return_value.__aexit__ = AsyncMock()
            mock_server.run = AsyncMock()
            
            await transport.run(mock_server)
            
            # Verify server.run was called with correct parameters
            mock_server.run.assert_called_once()


class TestHttpTransport:
    """Test the HTTP transport implementation."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server."""
        server = Mock(spec=Server)
        server.get_capabilities.return_value = {}
        return server

    def test_http_transport_properties(self):
        """Test HTTP transport properties."""
        from mcp_financial_modeling_prep.transport.http import HttpTransport

        transport = HttpTransport(host="0.0.0.0", port=8000)
        transport_info = transport.get_transport_info()
        
        assert transport_info["transport"] == "streamable-http"
        assert transport_info["host"] == "0.0.0.0"
        assert transport_info["port"] == 8000
        assert transport_info["usage"] == "network/container"

    def test_http_transport_default_values(self):
        """Test HTTP transport with default values."""
        from mcp_financial_modeling_prep.transport.http import HttpTransport

        transport = HttpTransport()
        transport_info = transport.get_transport_info()
        
        assert transport_info["host"] == "0.0.0.0"
        assert transport_info["port"] == 8000

    @pytest.mark.asyncio
    async def test_http_transport_run_starts_server(self, mock_server):
        """Test that HTTP transport starts the HTTP server."""
        from mcp_financial_modeling_prep.transport.http import HttpTransport
        from unittest.mock import patch, AsyncMock

        transport = HttpTransport(host="127.0.0.1", port=8001)
        
        # Mock uvicorn server
        with patch('mcp_financial_modeling_prep.transport.http.uvicorn.Server') as mock_uvicorn:
            mock_server_instance = AsyncMock()
            mock_uvicorn.return_value = mock_server_instance
            
            await transport.run(mock_server)
            
            # Verify uvicorn server was created and serve was called
            mock_uvicorn.assert_called_once()
            mock_server_instance.serve.assert_called_once()

    def test_http_transport_has_health_endpoint(self):
        """Test that HTTP transport exposes health endpoint."""
        from mcp_financial_modeling_prep.transport.http import HttpTransport

        transport = HttpTransport()
        
        # Verify health endpoint is available
        health_endpoint = transport.health_check_endpoint()
        assert health_endpoint == "/health"


class TestTransportIntegration:
    """Test transport integration with MCP server."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server."""
        server = Mock(spec=Server)
        server.get_capabilities.return_value = {
            "resources": {},
            "tools": {},
            "prompts": {}
        }
        return server

    @pytest.mark.asyncio
    async def test_transport_run_interface_compliance(self, mock_server):
        """Test that all transports implement the run interface correctly."""
        from mcp_financial_modeling_prep.transport import create_transport

        # Test stdio transport interface
        stdio_transport = create_transport("stdio")
        assert hasattr(stdio_transport, "run")
        assert callable(stdio_transport.run)

        # Test HTTP transport interface
        http_transport = create_transport("http")
        assert hasattr(http_transport, "run")
        assert callable(http_transport.run)

    def test_transport_info_interface_compliance(self):
        """Test that all transports provide transport info correctly."""
        from mcp_financial_modeling_prep.transport import create_transport

        # Test stdio transport info
        stdio_transport = create_transport("stdio")
        stdio_info = stdio_transport.get_transport_info()
        assert "transport" in stdio_info
        assert "usage" in stdio_info

        # Test HTTP transport info
        http_transport = create_transport("http")
        http_info = http_transport.get_transport_info()
        assert "transport" in http_info
        assert "host" in http_info
        assert "port" in http_info
        assert "usage" in http_info