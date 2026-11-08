"""Runs the whole graph with a fake LLM and fake agents: no API keys or internet needed.
Run with:  python -m pytest  (from the server folder)
"""
import asyncio
import os

os.environ.setdefault("GROQ_API_KEY", "test")

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents import budget, final, flight, hotel, itinerary, supervisor, weather
from app.agents.supervisor import Plan
from app.graph import build_graph

ALL = ["flight_agent", "hotel_agent", "weather_agent", "budget_agent"]


class FakePlanner:
    def __init__(self, plan): self.plan = plan
    async def ainvoke(self, _): return self.plan


async def fake_ask(system, prompt): return "revised" if "Revise" in prompt else "fake answer"
async def fake_agent(role, task, tools): return "fake research"


def setup(plan, monkeypatch):
    monkeypatch.setattr(supervisor, "planner", FakePlanner(plan))
    for module in (budget, itinerary, final):
        monkeypatch.setattr(module, "ask", fake_ask)
    for module in (flight, hotel, weather):
        monkeypatch.setattr(module, "run_agent", fake_agent)
    graph = build_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "t1"}}
    return graph, config, asyncio.run(graph.ainvoke({"query": "Trip to Tokyo"}, config))


def test_full_trip_with_revision_loop(monkeypatch):
    plan = Plan(allowed=True, reasoning="full trip", destination="Tokyo", origin="", dates="", days=0, agents=ALL)
    graph, config, state = setup(plan, monkeypatch)
    assert "__interrupt__" in state and state["draft"] == "fake answer"
    assert all(state[k] for k in ("flights", "hotels", "weather", "budget"))

    # Reject -> a new draft is written and the graph pauses for review again.
    state = asyncio.run(graph.ainvoke(Command(resume={"approved": False, "feedback": "cheaper"}), config))
    assert "__interrupt__" in state and state["draft"] == "revised"

    # Approve -> final plan.
    state = asyncio.run(graph.ainvoke(Command(resume={"approved": True}), config))
    assert state["final"] == "fake answer"


def test_only_selected_agents_run(monkeypatch):
    plan = Plan(allowed=True, reasoning="weather", destination="Tokyo", origin="", dates="", days=0, agents=["weather_agent"])
    _, _, state = setup(plan, monkeypatch)
    assert state["weather"] and not state.get("flights") and not state.get("budget")


def test_guardrail_blocks_off_topic(monkeypatch):
    plan = Plan(allowed=False, reasoning="Not travel.", destination="", origin="", dates="", days=0, agents=[])
    _, _, state = setup(plan, monkeypatch)
    assert "__interrupt__" not in state and "only help with travel" in state["final"]
