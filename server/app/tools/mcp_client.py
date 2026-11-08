"""Connects to MCP servers and turns their tools into LangChain tools.

- Tavily: a hosted MCP server for live web search (reached over HTTP).
- Weather: our own server in mcp_weather_server.py (started as a subprocess).
"""
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient  # MCP -> LangChain bridge

from app.config import OPENWEATHER_API_KEY, TAVILY_API_KEY

SERVERS = {
    "tavily": {
        "transport": "streamable_http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    },
    "weather": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(Path(__file__).with_name("mcp_weather_server.py"))],
        "env": {"OPENWEATHER_API_KEY": OPENWEATHER_API_KEY},
    },
}

client = MultiServerMCPClient(SERVERS)
tools = {}  # tool name -> tool, filled once at startup


async def load_tools() -> None:
    """Load each server separately so one broken server doesn't stop the app."""
    for name in SERVERS:
        try:
            for tool in await client.get_tools(server_name=name):
                tools[tool.name] = tool
        except Exception as exc:
            print(f"MCP server '{name}' unavailable: {exc}")
    print("MCP tools loaded:", list(tools))


async def call_tool(name: str, **args) -> str:
    """Run an MCP tool. Returns a friendly message instead of crashing if it fails."""
    if name not in tools:
        return f"(live '{name}' data unavailable - use general knowledge and say so)"
    try:
        return str(await tools[name].ainvoke(args))[:1500]  # cap size: free LLM tiers limit tokens/minute
    except Exception as exc:
        return f"(live '{name}' call failed: {exc} - use general knowledge and say so)"
