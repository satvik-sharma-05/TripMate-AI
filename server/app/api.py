"""HTTP endpoints the frontend calls. Both stream live progress.

POST /api/plan                     -> start a plan; streams steps, stops at the draft
POST /api/plan/{thread_id}/review  -> approve (final plan) or send feedback (new draft)

Streaming uses Server-Sent Events (SSE): the response stays open and the server
writes one `data: {...}` line per event as each agent finishes.
"""
import json
import logging
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.links import booking_links

router = APIRouter(prefix="/api")
logger = logging.getLogger("uvicorn.error")


class PlanRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)


class ReviewRequest(BaseModel):
    approved: bool
    feedback: str = Field("", max_length=2000)


def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"  # SSE format: "data: <json>" + blank line


async def stream_run(graph, graph_input, thread_id: str):
    """Run the graph, yielding one event per finished agent, then the final result."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        # stream_mode="updates" yields {node_name: fields_it_changed} after every step.
        async for update in graph.astream(graph_input, config, stream_mode="updates"):
            for node, changes in update.items():
                if node == "__interrupt__":
                    continue
                step = {"type": "step", "node": node}
                if node == "supervisor":  # send the plan early so the UI can show it
                    step |= {"agents": changes.get("agents", []), "reasoning": changes.get("reasoning", "")}
                yield event(step)

        snapshot = await graph.aget_state(config)  # the saved state after the run
        state, paused = snapshot.values, bool(snapshot.next)
        if paused:
            status, answer = "needs_review", state["draft"] + booking_links(state)
        elif state.get("allowed"):
            status, answer = "done", state.get("final", "") + booking_links(state)
        else:
            status, answer = "blocked", state.get("final", "")
        yield event({"type": "result", "thread_id": thread_id, "status": status, "answer": answer,
                     "agents": state.get("agents", []), "reasoning": state.get("reasoning", "")})
    except Exception as exc:
        logger.error("Run failed: %s", ascii(exc))
        busy = "rate limit" in str(exc).lower()  # every model hit its free-tier limit
        yield event({"type": "error", "message": (
            "The AI service is at its free usage limit right now. Please try again in a few minutes."
            if busy else "Something went wrong. Please try again.")})


def sse(generator) -> StreamingResponse:
    return StreamingResponse(generator, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/plan")
async def start_plan(body: PlanRequest, request: Request):
    thread_id = uuid.uuid4().hex  # each plan gets its own saved conversation
    return sse(stream_run(request.app.state.graph, {"query": body.message}, thread_id))


@router.post("/plan/{thread_id}/review")
async def review_plan(thread_id: str, body: ReviewRequest, request: Request):
    if not body.approved and not body.feedback.strip():
        raise HTTPException(400, "Please write feedback when asking for changes.")
    graph = request.app.state.graph
    snapshot = await graph.aget_state({"configurable": {"thread_id": thread_id}})
    if not snapshot.next:  # nothing is paused on this thread
        raise HTTPException(404, "No draft is waiting for review on this thread.")
    # Command(resume=...) wakes up the paused human_review node with the user's decision.
    return sse(stream_run(graph, Command(resume=body.model_dump()), thread_id))
