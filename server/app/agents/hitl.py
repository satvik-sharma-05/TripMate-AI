"""Human-in-the-loop (HITL): pause the graph until a person approves the draft.

interrupt() saves the state to the checkpointer and stops. The API returns the
draft to the browser. When the user clicks Approve/Revise, the API resumes the
graph with Command(resume=...) and interrupt() returns that value here.
"""
from langgraph.types import interrupt

from app.state import TravelState


def human_review(state: TravelState) -> dict:
    decision = interrupt({"draft": state["draft"]})  # e.g. {"approved": True, "feedback": ""}
    return {"approved": decision["approved"], "feedback": decision.get("feedback", "")}
