"""Flight agent: a tool-calling agent that decides what to search for flights."""
from app.agents.base import run_agent, trip_summary
from app.state import TravelState
from app.tools.mcp_tools import web_search


async def flight_agent(state: TravelState) -> dict:
    answer = await run_agent(
        "You are a flight researcher. Find airlines, typical duration and price range "
        "for the route, plus booking tips.",
        trip_summary(state),
        [web_search],
    )
    return {"flights": answer}
