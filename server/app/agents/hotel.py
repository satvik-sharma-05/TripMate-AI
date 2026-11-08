"""Hotel agent: a tool-calling agent that researches where to stay."""
from app.agents.base import run_agent, trip_summary
from app.state import TravelState
from app.tools.mcp_tools import web_search


async def hotel_agent(state: TravelState) -> dict:
    answer = await run_agent(
        "You are a hotel researcher. Recommend 3-4 hotels across price levels with "
        "nightly prices, and the best areas to stay. Respect any budget in the request.",
        trip_summary(state),
        [web_search],
    )
    return {"hotels": answer}
