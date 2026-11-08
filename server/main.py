"""Entry point. Run with:  uvicorn main:app --reload

FastAPI is a Python web framework: it turns functions into HTTP endpoints and
validates request JSON with Pydantic models automatically.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import router
from app.config import CORS_ORIGINS
from app.graph import build_graph
from app.memory import open_checkpointer
from app.tools.mcp_client import load_tools

logger = logging.getLogger("uvicorn.error")  # reuse uvicorn's logger so errors appear in its output


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at startup (before yield) and once at shutdown (after yield)."""
    await load_tools()
    async with open_checkpointer() as checkpointer:
        app.state.graph = build_graph(checkpointer)
        yield


app = FastAPI(title="TripMate AI", lifespan=lifespan)
# CORS lets a frontend hosted on another domain call this API.
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", ascii(exc))  # ascii(): safe on any console encoding
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})


@app.get("/health")
async def health():
    return {"status": "ok"}


class SPAStaticFiles(StaticFiles):
    """Serves React's index.html for unknown paths, so /about and /plan work on refresh."""

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            return await super().get_response("index.html", scope)


# Production: serve the built React app (client/dist, made by `npm run build`) at "/".
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client" / "dist"
if CLIENT_DIR.is_dir():
    app.mount("/", SPAStaticFiles(directory=CLIENT_DIR, html=True), name="client")
