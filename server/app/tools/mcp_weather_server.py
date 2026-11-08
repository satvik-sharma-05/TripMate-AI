"""Our own MCP server that exposes OpenWeather as two tools.

MCP (Model Context Protocol) is a standard "plug" between AI apps and tools.
Any MCP client (our agents, Claude Desktop, Cursor...) can launch this file
and call its tools without knowing how they work inside.
"""
import os

import httpx  # HTTP client for calling the OpenWeather REST API
from mcp.server.fastmcp import FastMCP  # FastMCP turns plain functions into MCP tools

mcp = FastMCP("weather")
API = "https://api.openweathermap.org/data/2.5"


def _get(endpoint: str, city: str) -> dict:
    params = {"q": city, "appid": os.environ["OPENWEATHER_API_KEY"], "units": "metric"}
    response = httpx.get(f"{API}/{endpoint}", params=params, timeout=20)
    response.raise_for_status()
    return response.json()


@mcp.tool()  # the docstring becomes the tool description the client sees
def get_current_weather(city: str) -> dict:
    """Current weather for a city."""
    d = _get("weather", city)
    return {"city": d["name"], "temp_c": d["main"]["temp"],
            "humidity": d["main"]["humidity"], "condition": d["weather"][0]["description"]}


@mcp.tool()
def get_forecast(city: str) -> list[dict]:
    """Forecast for the next ~5 days (one entry per day)."""
    items = _get("forecast", city)["list"][::8]  # API returns 3-hour steps; 8 steps = 1 day
    return [{"time": i["dt_txt"], "temp_c": i["main"]["temp"],
             "condition": i["weather"][0]["description"]} for i in items]


if __name__ == "__main__":
    mcp.run(transport="stdio")  # talk to the client over stdin/stdout
