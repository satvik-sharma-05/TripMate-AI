"""Itinerary agent: writes the draft, or rewrites it when the human asks for changes."""
from app.agents.base import trip_summary
from app.links import MAPS_LINK_RULE
from app.llm import ask
from app.state import TravelState

STYLE = ("Write clear Markdown: a short summary, a day-by-day plan, and a budget table. "
         f"Stay under 700 words so nothing gets cut off. {MAPS_LINK_RULE}")


def research_notes(state: TravelState) -> str:
    """Collect whatever the specialists found (some may not have run)."""
    parts = {"Flights": "flights", "Hotels": "hotels", "Weather": "weather", "Budget": "budget"}
    return "\n\n".join(f"{title}:\n{state[key]}" for title, key in parts.items() if state.get(key))


async def itinerary_agent(state: TravelState) -> dict:
    if state.get("feedback"):  # the human rejected the previous draft
        task = (f"Revise this draft itinerary.\nUser feedback: {state['feedback']}\n\n"
                f"Previous draft:\n{state['draft']}")
    else:
        task = f"{trip_summary(state)}\n\nResearch:\n{research_notes(state)}\n\nWrite a draft itinerary."
    draft = await ask(f"You are an expert travel planner. {STYLE}", task)
    return {"draft": draft, "feedback": ""}
