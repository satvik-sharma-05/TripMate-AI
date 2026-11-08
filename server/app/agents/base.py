"""Shared helper that builds a tool-calling ("ReAct") agent.

A ReAct agent loops:  think -> call a tool -> read the result -> think again ...
until it decides it has enough information and writes an answer.
LangChain's create_agent builds that loop for us (it is a small LangGraph graph).
"""
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
import logging

from langgraph.errors import GraphRecursionError

from app.llm import backup_researcher, fast_llm, today

logger = logging.getLogger("uvicorn.error")


async def run_agent(role: str, task: str, tools: list) -> str:
    names = ", ".join(t.name for t in tools)
    agent = create_agent(
        fast_llm,
        tools,
        system_prompt=f"{role} Today is {today()}. Only these tools exist: {names}. "
                      "Use at most 2 tool calls, then answer in under 200 words with "
                      "concrete facts and numbers. Include the source URL next to each fact.",
        # Middleware = hooks around each model call. This one switches to the backup
        # model if the main one fails (e.g. Groq rate limit reached).
        middleware=[ModelFallbackMiddleware(backup_researcher)],
    )
    # Models sometimes call a tool that doesn't exist (Groq then rejects the request),
    # so we try twice before giving up.
    for _ in range(2):
        try:
            # recursion_limit caps the loop so a confused agent can't run forever
            # (each model call and each tool call counts as one step).
            result = await agent.ainvoke({"messages": [("user", task)]}, {"recursion_limit": 12})
            return result["messages"][-1].content
        except GraphRecursionError:
            break
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise  # let the API show the friendly rate-limit message
            logger.warning("Agent attempt failed: %s", ascii(e)[:200])
    # One failing agent shouldn't break the whole trip plan, so we return a note instead.
    return "No live data found for this part; use typical estimates."


def trip_summary(state) -> str:
    """One line describing the trip, given to every specialist."""
    return (f"Trip request: {state['query']}\nOrigin: {state.get('origin') or 'unknown'}; "
            f"destination: {state.get('destination') or 'unknown'}; "
            f"dates: {state.get('dates') or 'not given'}; days: {state.get('days') or 'not given'}.")
