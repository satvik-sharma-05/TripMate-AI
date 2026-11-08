"""The shared "notebook" that every agent reads from and writes to.

In LangGraph, each node (agent) receives the current state and returns only
the fields it wants to update. LangGraph merges them and saves a checkpoint.
Agents running in parallel must write to *different* fields.
"""
from typing import TypedDict


class TravelState(TypedDict, total=False):
    query: str                # the user's original request
    # Set by the supervisor
    allowed: bool             # did the guardrail accept the request?
    reasoning: str            # why the supervisor chose these agents
    agents: list[str]         # which specialists to run
    destination: str
    origin: str
    dates: str                # e.g. "15-20 December 2026" or "March"
    days: int
    # Written by specialist agents (each writes its own field, so they can run in parallel)
    flights: str
    hotels: str
    weather: str
    budget: str
    draft: str                # itinerary waiting for human review
    # Human-in-the-loop
    approved: bool
    feedback: str             # the latest revision request
    final: str                # the finished answer shown to the user
