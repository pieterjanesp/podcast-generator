"""MCP Client for arXiv Server

This module provides an MCP client that connects to the arxiv-mcp-server.
It handles the connection lifecycle and exposes the server's tools.

How MCP Works:
    - MCP (Model Context Protocol) is a standard for connecting AI models to external tools
    - The server runs as a subprocess, communicating via stdio (standard input/output)
    - The client sends JSON-RPC requests, the server responds with results
    - Tools are discovered dynamically via `list_tools()`

Architecture:
    - ArxivMCPClient: Manages connection to the arXiv MCP server
    - Uses AsyncExitStack for proper resource cleanup
    - Exposes tools: search_papers, download_paper, list_papers, read_paper

Usage:
    async with ArxivMCPClient() as client:
        # Search for papers
        results = await client.call_tool("search_papers", {"query": "transformers"})

        # Download a specific paper
        await client.call_tool("download_paper", {"paper_id": "2401.12345"})

        # Read the downloaded paper
        content = await client.call_tool("read_paper", {"paper_id": "2401.12345"})

Dependencies:
    - mcp: Official MCP Python SDK
    - arxiv-mcp-server: The arXiv MCP server package (installed as a tool)
"""

from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings


class ArxivMCPClient:
    """Client for connecting to the arXiv MCP server.

    This class manages the lifecycle of an MCP connection to the arxiv-mcp-server.
    It starts the server as a subprocess and communicates via stdio.

    The server provides these tools:
        - search_papers: Search arXiv for papers matching a query
        - download_paper: Download a paper by its arXiv ID
        - list_papers: List all downloaded papers
        - read_paper: Read the content of a downloaded paper

    Example:
        async with ArxivMCPClient() as client:
            tools = await client.list_tools()
            result = await client.call_tool("search_papers", {"query": "LLMs"})
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize the MCP client.

        Args:
            storage_path: Directory where papers will be stored.
                         Defaults to "papers/" in the backend directory.
        """
        self.storage_path = storage_path or str(Path("papers").absolute())
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._tools: list[dict] = []

    async def __aenter__(self) -> "ArxivMCPClient":
        """Connect to the MCP server when entering async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting async context."""
        await self.cleanup()

    async def connect(self):
        """Establish connection to the arXiv MCP server.

        This starts the arxiv-mcp-server as a subprocess using `uv tool run`.
        The server communicates via stdio (stdin/stdout).

        After connecting, we call initialize() to complete the MCP handshake
        and discover available tools.
        """
        # Server parameters for stdio transport
        # Using `uv tool run` to run the installed arxiv-mcp-server
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "tool", "run", "arxiv-mcp-server",
                "--storage-path", self.storage_path
            ],
            env=None  # Inherit environment
        )

        # Start the server subprocess and get stdio transport
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport

        # Create client session for JSON-RPC communication
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        # Initialize the connection (MCP handshake)
        await self.session.initialize()

        # Discover available tools
        response = await self.session.list_tools()
        self._tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in response.tools
        ]

        print(f"  🔌 Connected to arXiv MCP server")
        print(f"     Available tools: {[t['name'] for t in self._tools]}")

    async def cleanup(self):
        """Clean up resources and close the connection."""
        await self.exit_stack.aclose()
        self.session = None

    @property
    def tools(self) -> list[dict]:
        """Get the list of available tools from the server.

        Returns:
            List of tool definitions with name, description, and input_schema.
            Format matches what Claude expects for tool use.
        """
        return self._tools

    async def list_tools(self) -> list[dict]:
        """Fetch and return available tools from the server.

        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")

        response = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in response.tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call (e.g., "search_papers")
            arguments: Tool arguments as a dictionary

        Returns:
            Tool result as a string

        Raises:
            RuntimeError: If not connected to the server
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")

        result = await self.session.call_tool(tool_name, arguments)

        # Extract text content from result
        # MCP returns content as a list of content blocks
        if result.content:
            # Concatenate all text content
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            return "\n".join(texts) if texts else str(result.content)

        return "No result returned"
