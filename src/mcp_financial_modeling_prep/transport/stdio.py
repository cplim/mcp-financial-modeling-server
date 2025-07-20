"""Stdio transport implementation for MCP server."""

import mcp.server.stdio
from mcp.server.models import InitializationOptions

from . import TransportInterface


class StdioTransport(TransportInterface):
    """Stdio transport for subprocess usage."""
    
    async def run(self, server):
        """Run the server using stdio transport.
        
        Args:
            server: MCP server instance
        """
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="financial-modeling-prep",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(),
                ),
            )
    
    def get_transport_info(self):
        """Return stdio transport information."""
        return {
            "transport": "stdio",
            "usage": "subprocess"
        }