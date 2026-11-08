"""Final agent: polishes the draft the human approved."""
from app.links import MAPS_LINK_RULE
from app.llm import ask
from app.state import TravelState

SECTIONS = "Trip Summary, Flights, Hotels, Weather, Day-by-Day Itinerary, Estimated Budget, Final Tips"


async def final_agent(state: TravelState) -> dict:
    final = await ask(
        "You are a professional travel assistant. Write clear Markdown, under 900 words. "
        f"Keep every link from the draft. {MAPS_LINK_RULE}",
        # The draft already contains the research, so we don't send it again (saves tokens).
        f"The user approved this draft. Keep its decisions and polish it into a final plan "
        f"using these sections: {SECTIONS}.\n\nRequest: {state['query']}\n\nDraft:\n{state['draft']}",
    )
    return {"final": final}
