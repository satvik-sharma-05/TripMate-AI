"""Supervisor + guardrail: checks the request is about travel, then picks agents."""
from typing import Literal

from pydantic import BaseModel, Field  # Pydantic: defines the exact JSON shape we want back

from app.llm import backup_writer, big_llm, today
from app.state import TravelState

SPECIALISTS = ["flight_agent", "hotel_agent", "weather_agent", "budget_agent"]


class Plan(BaseModel):
    allowed: bool = Field(description="True only if the request is about travel and not harmful")
    reasoning: str = Field(description="One sentence explaining the decision")
    agents: list[Literal["flight_agent", "hotel_agent", "weather_agent", "budget_agent"]]
    # Strict mode needs every field filled in, so "unknown" values are "" or 0 (no defaults).
    destination: str = Field(description="Destination (suggest one if the user did not)")
    origin: str = Field(description="Starting city, or empty")
    dates: str = Field(description="Travel dates or month as written by the user, or empty")
    days: int = Field(description="Trip length in days, 0 if not given")


PROMPT = """You are the supervisor of a travel-planning team. Today is {today}.
1. Guardrail: allow only travel requests (destinations, flights, hotels, weather,
   budget, visas, sightseeing...). Block unrelated or harmful requests.
2. If allowed, choose only the specialists needed:
   flight_agent (flights), hotel_agent (stays), weather_agent (weather/packing),
   budget_agent (costs). For a full trip plan, choose all of them.
3. Extract destination, origin, travel dates and number of days if mentioned.
   If no destination is given, choose the best one for the origin, dates, budget and
   group, and say in the reasoning that you suggested it.
Always answer in the required format, even when blocking (allowed=false, agents=[])."""

# with_structured_output forces the LLM to reply with a valid Plan object (no JSON parsing by hand).
# json_schema + strict=True makes Groq *enforce* that exact shape, so parsing never fails.
def _structured(model):
    return model.with_structured_output(Plan, method="json_schema", strict=True)


planner = _structured(big_llm).with_fallbacks([_structured(backup_writer)])


async def supervisor_agent(state: TravelState) -> dict:
    plan: Plan = await planner.ainvoke(
        [("system", PROMPT.format(today=today())), ("user", state["query"])])
    if not plan.allowed:
        return {"allowed": False, "reasoning": plan.reasoning, "agents": [],
                "final": f"Sorry, I can only help with travel planning. {plan.reasoning}"}
    return {"allowed": True, "reasoning": plan.reasoning,
            "agents": [a for a in SPECIALISTS if a in plan.agents],  # keep a fixed order
            "destination": plan.destination, "origin": plan.origin,
            "dates": plan.dates, "days": plan.days}
