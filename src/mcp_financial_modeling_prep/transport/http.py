"""HTTP transport implementation for MCP server."""

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import TransportInterface


class HttpTransport(TransportInterface):
    """Streamable HTTP transport for containerized/network usage."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize HTTP transport.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self._server = None
    
    async def run(self, server):
        """Run the server using HTTP transport.
        
        Args:
            server: MCP server instance
        """
        self._server = server
        
        # Create Starlette app with MCP streamable HTTP endpoints
        app = Starlette(routes=[
            Route("/mcp", endpoint=self._handle_mcp, methods=["POST", "GET"]),
            Route("/health", endpoint=self._health_check, methods=["GET"]),
            Route("/info", endpoint=self._server_info, methods=["GET"]),
        ])
        
        # Run with uvicorn
        config = uvicorn.Config(
            app, 
            host=self.host, 
            port=self.port,
            log_level="info"
        )
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    
    async def _handle_mcp(self, request):
        """Handle MCP Streamable HTTP protocol.
        
        Args:
            request: Starlette request object
            
        Returns:
            JSON response
        """
        # TODO: Implement MCP Streamable HTTP protocol
        # For now, return a placeholder response
        return JSONResponse({
            "message": "MCP Streamable HTTP endpoint - implementation pending",
            "method": request.method
        })
    
    async def _health_check(self, request):
        """Health check endpoint.
        
        Args:
            request: Starlette request object
            
        Returns:
            JSON response with health status
        """
        return JSONResponse({
            "status": "healthy", 
            "transport": "streamable-http",
            "server": "financial-modeling-prep"
        })
    
    async def _server_info(self, request):
        """Server information endpoint.
        
        Args:
            request: Starlette request object
            
        Returns:
            JSON response with server information
        """
        return JSONResponse({
            "server_name": "financial-modeling-prep",
            "version": "0.1.0",
            "transport": "streamable-http",
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "info": "/info"
            },
            "host": self.host,
            "port": self.port
        })
    
    def get_transport_info(self):
        """Return HTTP transport information."""
        return {
            "transport": "streamable-http",
            "host": self.host,
            "port": self.port,
            "usage": "network/container"
        }
    
    def health_check_endpoint(self):
        """Return health check endpoint path."""
        return "/health"