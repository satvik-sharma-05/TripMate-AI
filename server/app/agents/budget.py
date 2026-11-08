"""Budget agent: uses the LLM to judge if the trip fits the user's budget."""
from app.llm import ask
from app.state import TravelState


async def budget_agent(state: TravelState) -> dict:
    answer = await ask(
        "You are a practical travel budget analyst. Label estimates as approximate.",
        f"Request: {state['query']}\nFlights: {state.get('flights', '')}\n"
        f"Hotels: {state.get('hotels', '')}\n\n"
        "Give: cost breakdown, budget risks, money-saving tips, overall feasibility.",
    )
    return {"budget": answer}
