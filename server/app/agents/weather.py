"""Weather agent: a tool-calling agent using our own weather MCP server.

It decides by itself: if the trip is within 5 days it checks the live forecast,
otherwise it describes the usual climate for the travel month.
"""
from app.agents.base import run_agent, trip_summary
from app.state import TravelState
from app.tools.mcp_tools import current_weather, weather_forecast


async def weather_agent(state: TravelState) -> dict:
    answer = await run_agent(
        "You are a travel weather expert. If the trip starts within the next 5 days, use "
        "the forecast tool. If it is later, or no dates are given, describe the typical "
        "climate for the travel month instead (say it is typical, not a forecast). "
        "End with packing advice.",
        trip_summary(state),
        [current_weather, weather_forecast],
    )
    return {"weather": answer}
