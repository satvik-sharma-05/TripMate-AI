"""Wires the agents together into a LangGraph workflow.

LangGraph models an AI workflow as a graph: nodes are agents, edges decide
what runs next. A "checkpointer" saves the state after every step, which is
what lets the graph pause for a human and resume later.

                    ┌─> flight ──┐
    supervisor ─────┼─> hotel  ──┼─> budget ─> itinerary ─> human_review ─approve─> final
         │          └─> weather ─┘                ^              │
         └─blocked─> END    (run in parallel)     └────revise────┘
"""
from langgraph.graph import END, START, StateGraph

from app.agents import (budget_agent, final_agent, flight_agent, hotel_agent, human_review,
                        itinerary_agent, supervisor_agent, weather_agent)
from app.state import TravelState

RESEARCHERS = ["flight_agent", "hotel_agent", "weather_agent"]  # independent -> run in parallel


def after_research(state: TravelState) -> str:
    return "budget_agent" if "budget_agent" in state["agents"] else "itinerary_agent"


def after_supervisor(state: TravelState) -> list[str] | str:
    """Returning a LIST of nodes makes LangGraph run them at the same time."""
    if not state.get("allowed"):
        return END
    chosen = [a for a in RESEARCHERS if a in state["agents"]]
    return chosen or after_research(state)


def after_review(state: TravelState) -> str:
    """Approved -> finish. Rejected -> back to the itinerary agent, then review again."""
    return "final_agent" if state["approved"] else "itinerary_agent"


def build_graph(checkpointer):
    graph = StateGraph(TravelState)

    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("budget_agent", budget_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("human_review", human_review)
    graph.add_node("final_agent", final_agent)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", after_supervisor)
    # Parallel agents that point to the same next node are joined automatically:
    # the next node starts once, after all of them have finished.
    for node in RESEARCHERS:
        graph.add_conditional_edges(node, after_research)
    graph.add_edge("budget_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "human_review")
    graph.add_conditional_edges("human_review", after_review)
    graph.add_edge("final_agent", END)

    return graph.compile(checkpointer=checkpointer)
