"""MCP tools for the agents: each @tool forwards to an MCP server via call_tool().

@tool turns a Python function into something an LLM can call: the function
name, arguments and docstring are sent to the model, which then decides
*whether*, *when* and *with what arguments* to call it.
Each tool forwards to an MCP server via call_tool().
"""
from langchain_core.tools import tool

from app.tools.mcp_client import call_tool


@tool
async def web_search(query: str) -> str:
    """Search the web. Use specific queries, e.g. 'Mumbai to Goa flights price December'."""
    return await call_tool("tavily_search", query=query)


@tool
async def current_weather(city: str) -> str:
    """Current weather for a city."""
    return await call_tool("get_current_weather", city=city)


@tool
async def weather_forecast(city: str) -> str:
    """Daily forecast for the next 5 days only. Useless for trips further in the future."""
    return await call_tool("get_forecast", city=city)
