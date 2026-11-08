# TripMate AI — Multi-Agent Travel Planner

**🌐 Live demo: [tripmate-ai-2hmx.onrender.com](https://tripmate-ai-2hmx.onrender.com/)**
*(Free hosting: the first load after it has been idle can take up to a minute while the server wakes up.)*

A team of AI agents plans a trip: a **supervisor** checks the request is about travel
(**guardrail**) and picks which **specialists** to run. Then an itinerary agent writes a
draft that a **human approves or revises** before the final plan is produced.

## Tech stack (what each piece does)
| Tool | Role |
|---|---|
| **LangGraph** | Runs the agents as a graph (nodes = agents, edges = what runs next) and can pause for a human |
| **LangChain + Groq** | Calls the LLM (GPT-OSS 120B on Groq) using the same interface for any provider |
| **MCP** (Model Context Protocol) | Standard way to give agents tools: Tavily web search + our own weather server |
| **FastAPI** | The web API the browser talks to |
| **React + Vite** | Frontend UI (React = components, Vite = dev server and build tool) |
| **PostgreSQL** | Saves paused conversations (optional; RAM is used if not set) |

## Project layout
```
client/                  Frontend (React + Vite)
  src/
    main.jsx             Mounts React into index.html
    App.jsx              Router: / (Home), /about, /plan
    api.js               All backend calls
    hooks/usePlanner.js  State + logic (result, loading, error)
    pages/               Home, About, Plan
    components/          Navbar, Footer, PlannerForm, Workflow, ResultCard, ReviewPanel
    styles.css
server/
  main.py                App startup: loads MCP tools, opens memory, builds graph
  app/
    config.py            Settings from .env
    llm.py               The shared LLM + ask() helper
    state.py             Shared state every agent reads/writes
    graph.py             Wires agents together (the workflow)
    memory.py            Where checkpoints are saved (Postgres or RAM)
    api.py               HTTP endpoints
    agents/              One file per agent
      supervisor.py        guardrail + picks agents (structured output)
      flight.py hotel.py   web search via Tavily MCP
      weather.py           our weather MCP server
      budget.py            LLM cost analysis
      itinerary.py         combines everything into a draft
      hitl.py              Human-in-the-Loop: pauses for approval (interrupt)
      final.py             polishes or revises the draft
    tools/
      mcp_client.py        connects to MCP servers
      mcp_weather_server.py  our own MCP server (OpenWeather)
      mcp_tools.py           MCP tools wrapped for agents (@tool)
  tests/test_graph.py    Runs the graph with a fake LLM
```

## Flow
```
                ┌─> flight ──┐
supervisor ─────┼─> hotel  ──┼─> budget ─> itinerary ─> human_review ─approve─> final ─> END
     │          └─> weather ─┘                ^              │
     └─blocked─> END   (parallel, only        └───revise─────┘
                        the ones chosen)
```
- Flight, hotel and weather are **tool-calling agents**: the model decides what to search.
- Progress is **streamed** to the browser (Server-Sent Events) as each agent finishes.

## Run locally
```bash
cd server
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
copy .env.example .env                              # then add your keys
uvicorn main:app --reload
```
In a second terminal:
```bash
cd client
npm install
npm run dev          # http://localhost:5173 (calls to /api are forwarded to :8000)
```
Production-style: `npm run build` in `client/`, then FastAPI serves the app at http://localhost:8000.
Tests: `python -m pytest` in `server/`.

**Docker (with PostgreSQL):** `docker compose up --build`

> On Windows, run PostgreSQL mode through Docker. psycopg's async driver doesn't
> support the Windows default event loop, so leave `DATABASE_URL` empty for local runs.

## API
- `POST /api/plan` `{"message": "..."}` → `{thread_id, status: needs_review|blocked, answer, agents, reasoning}`
- `POST /api/plan/{thread_id}/review` `{"approved": true|false, "feedback": "..."}` → final plan
