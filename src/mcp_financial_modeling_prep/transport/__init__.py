"""Transport abstraction layer for MCP server."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from mcp.server import Server


class TransportInterface(ABC):
    """Abstract base class for MCP transport implementations."""

    @abstractmethod
    async def run(self, server: Server) -> None:
        """Run the transport with the given MCP server.

        Args:
            server: MCP server instance to run
        """
        pass

    @abstractmethod
    def get_transport_info(self) -> Dict[str, Any]:
        """Return transport-specific information.

        Returns:
            Dictionary containing transport configuration and metadata
        """
        pass


def create_transport(transport_type: str, **kwargs) -> TransportInterface:
    """Factory function to create transport instances.

    Args:
        transport_type: Type of transport ("stdio" or "http")
        **kwargs: Transport-specific configuration parameters

    Returns:
        Transport instance

    Raises:
        ValueError: If transport_type is not supported
    """
    if transport_type == "stdio":
        from .stdio import StdioTransport

        return StdioTransport()
    elif transport_type == "http":
        from .http import HttpTransport

        return HttpTransport(**kwargs)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")


__all__ = ["TransportInterface", "create_transport"]
