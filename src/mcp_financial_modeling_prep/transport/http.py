"""HTTP transport implementation for MCP server."""

import json
import asyncio
from typing import Any, Dict

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
from starlette.requests import Request

from . import TransportInterface


class HttpTransport(TransportInterface):
    """Streamable HTTP transport for containerized/network usage."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
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
        app = Starlette(
            routes=[
                Route("/mcp", endpoint=self._handle_mcp, methods=["POST", "GET"]),
                Route("/health", endpoint=self._health_check, methods=["GET"]),
                Route("/info", endpoint=self._server_info, methods=["GET"]),
            ]
        )

        # Run with uvicorn
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

    async def _handle_mcp(self, request: Request):
        """Handle MCP Streamable HTTP protocol.

        Args:
            request: Starlette request object

        Returns:
            JSON response for POST or SSE stream for GET
        """
        # Validate MCP protocol version header
        protocol_version = request.headers.get("MCP-Protocol-Version")
        if not protocol_version:
            return JSONResponse({"error": "Missing MCP-Protocol-Version header"}, status_code=400)

        if request.method == "POST":
            return await self._handle_mcp_post(request)
        elif request.method == "GET":
            return await self._handle_mcp_get(request)
        else:
            return JSONResponse({"error": f"Method {request.method} not allowed"}, status_code=405)

    async def _handle_mcp_post(self, request: Request):
        """Handle POST request with JSON-RPC message.

        Args:
            request: Starlette request object

        Returns:
            JSON response
        """
        try:
            # Parse JSON-RPC message
            json_data = await request.json()

            # Validate JSON-RPC format
            if not isinstance(json_data, dict) or "jsonrpc" not in json_data:
                return JSONResponse({"error": "Invalid JSON-RPC format"}, status_code=400)

            # Process MCP message through server
            # For now, return a success response
            response_data = {
                "jsonrpc": "2.0",
                "id": json_data.get("id"),
                "result": {
                    "status": "processed",
                    "method": json_data.get("method"),
                    "transport": "streamable-http",
                },
            }

            return JSONResponse(response_data)

        except json.JSONDecodeError:
            return JSONResponse({"error": "Invalid JSON payload"}, status_code=400)
        except Exception as e:
            return JSONResponse({"error": f"Internal error: {str(e)}"}, status_code=500)

    async def _handle_mcp_get(self, request: Request):
        """Handle GET request for Server-Sent Events stream.

        Args:
            request: Starlette request object

        Returns:
            SSE streaming response
        """
        # Validate Accept header includes text/event-stream
        accept_header = request.headers.get("accept", "")
        if "text/event-stream" not in accept_header:
            return JSONResponse(
                {"error": "Accept header must include text/event-stream"}, status_code=400
            )

        async def generate_sse_stream():
            """Generate Server-Sent Events stream."""
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"

            # Simulate streaming capability - in real implementation,
            # this would handle actual MCP message streaming
            await asyncio.sleep(0.1)

            # Send sample MCP response
            response_data = {
                "jsonrpc": "2.0",
                "method": "notifications/tools/list_changed",
                "params": {"transport": "streamable-http"},
            }
            yield f"data: {json.dumps(response_data)}\n\n"

            # End stream
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    async def _health_check(self, request):
        """Health check endpoint.

        Args:
            request: Starlette request object

        Returns:
            JSON response with health status
        """
        return JSONResponse(
            {
                "status": "healthy",
                "transport": "streamable-http",
                "server": "financial-modeling-prep",
            }
        )

    async def _server_info(self, request):
        """Server information endpoint.

        Args:
            request: Starlette request object

        Returns:
            JSON response with server information
        """
        return JSONResponse(
            {
                "server_name": "financial-modeling-prep",
                "version": "0.1.0",
                "transport": "streamable-http",
                "endpoints": {"mcp": "/mcp", "health": "/health", "info": "/info"},
                "host": self.host,
                "port": self.port,
            }
        )

    def get_transport_info(self):
        """Return HTTP transport information."""
        return {
            "transport": "streamable-http",
            "host": self.host,
            "port": self.port,
            "usage": "network/container",
        }

    def health_check_endpoint(self):
        """Return health check endpoint path."""
        return "/health"
