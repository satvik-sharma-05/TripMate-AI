# Deployment Guide

You can deploy TripMate AI (free) in two ways:

| Option | What runs where | When to pick it |
|---|---|---|
| **A. Render only** (recommended) | Render runs the API **and** serves the React site from one URL | Simplest: one service, no CORS setup |
| **B. Render + Vercel** | Render runs the API, Vercel hosts the React site | You want the frontend on Vercel's fast CDN |

Both options start with steps 0 and 1.

---

## 0. What you need

- A GitHub account
- A [Render](https://render.com) account (sign in with GitHub)
- A [Vercel](https://vercel.com) account (Option B only)
- API keys:
  | Key | Where to get it | Required? |
  |---|---|---|
  | `GROQ_API_KEY` | https://console.groq.com/keys | Yes |
  | `TAVILY_API_KEY` | https://app.tavily.com | Yes (web search) |
  | `OPENWEATHER_API_KEY` | https://home.openweathermap.org/api_keys | Yes (weather) |

> Never commit `server/.env`. It is already in `.gitignore`, so only `.env.example` (with placeholder values) goes to GitHub.

---

## 1. Push the code to GitHub

The repo is already initialised and the files are staged. From the project root:

```bash
git commit -m "Initial commit: TripMate AI"
```

Then create an **empty** repo on GitHub (no README or .gitignore), for example `tripmate-ai`, and run:

```bash
git remote add origin https://github.com/<your-username>/tripmate-ai.git
git push -u origin main
```

Check on GitHub that `server/.env` is **not** listed.

### Project layout (what gets deployed)

```
Multi-Agent/
├── client/            React + Vite frontend      → Vercel (Option B)
│   ├── vercel.json    SPA routing for Vercel
│   └── .env.example   VITE_API_URL (Option B only)
├── server/            FastAPI + LangGraph backend
│   ├── app/           agents, graph, MCP tools, API
│   └── .env.example   copy to .env for local runs
├── Dockerfile         builds client + server into one image → Render
├── render.yaml        Render Blueprint (web service + Postgres)
└── docker-compose.yml run everything locally with Docker
```

---

## 2. Option A: Render only (one URL)

The `Dockerfile` first builds the React app, then FastAPI serves it next to the API.

1. Render dashboard → **New** → **Blueprint**.
2. Select your `tripmate-ai` repo. Render reads `render.yaml` and creates:
   - `tripmate-ai`: the web service (Docker)
   - `tripmate-db`: a free PostgreSQL database that stores HITL review state
3. Render asks you for the 3 secret values (`GROQ_API_KEY`, `TAVILY_API_KEY`, `OPENWEATHER_API_KEY`). Paste them in.
4. Click **Apply**. The first build takes about 5 to 8 minutes.
5. Open `https://tripmate-ai.onrender.com` (Render shows the exact URL).
   - `/health` should return `{"status":"ok"}`.
   - `/plan` is the planner.

That's it. Every `git push` to `main` redeploys automatically.

---

## 3. Option B: Render (API) + Vercel (frontend)

### 3.1 Backend on Render
Do **Option A** first. Your API is then live at `https://tripmate-ai.onrender.com`.

### 3.2 Frontend on Vercel
1. Vercel dashboard → **Add New** → **Project** → import the `tripmate-ai` repo.
2. Settings:
   | Setting | Value |
   |---|---|
   | Root Directory | `client` |
   | Framework Preset | Vite (detected automatically) |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |
3. **Environment Variables**: add
   `VITE_API_URL` = `https://tripmate-ai.onrender.com` (no trailing slash)
4. Click **Deploy**. You get a URL like `https://tripmate-ai.vercel.app`.

### 3.3 Allow Vercel to call the API (CORS)
Render → `tripmate-ai` → **Environment** → set
`CORS_ORIGINS` = `https://tripmate-ai.vercel.app`
then save. Render restarts the service.

> `VITE_*` variables are baked into the JavaScript at **build time**. If you change `VITE_API_URL`, redeploy on Vercel.

---

## 4. Environment variables reference

| Variable | Where | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Render | LLM calls |
| `TAVILY_API_KEY` | Render | Web search (through MCP) |
| `OPENWEATHER_API_KEY` | Render | Weather MCP server |
| `DATABASE_URL` | Render (set automatically) | Postgres checkpointer. If empty, the app uses in-memory storage instead. |
| `GROQ_MODEL` / `GROQ_FAST_MODEL` | Render (optional) | Override the default models |
| `CORS_ORIGINS` | Render | `*`, or your Vercel URL (comma-separated if several) |
| `VITE_API_URL` | Vercel | Backend URL. Leave unset for Option A. |

---

## 5. Free-tier things to know

- **Cold starts:** the free Render service sleeps after 15 minutes without traffic, and the first request then takes about 50 seconds. Before an interview demo, open `/health` once to wake it up.
- **Free Postgres expires after 30 days.** After that, either create a new one, or delete `DATABASE_URL`. The app then falls back to in-memory storage, which loses paused reviews whenever the service restarts.
- **Groq free limits:** 8,000 tokens per minute and 200,000 tokens per day per model. If you hit them, the app shows a "rate limit" message. Wait a minute (or until the next day) and try again.

---

## 6. Run locally (for reference)

```bash
# Backend
cd server
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
copy .env.example .env                                # then fill in your keys
uvicorn main:app --reload --port 8000

# Frontend (second terminal)
cd client
npm install
npm run dev                                           # http://localhost:5173 (proxies /api to :8000)
```

Or run everything with Docker: `docker compose up --build`, then open http://localhost:8000.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| Render build fails at `npm ci` | Make sure `client/package-lock.json` is committed |
| Page loads, but "Something went wrong" | Render → **Logs**. Usually a missing or invalid API key, or a Groq rate limit |
| Vercel site shows CORS errors in the console | `CORS_ORIGINS` on Render must exactly match the Vercel URL (https, no trailing slash) |
| Vercel site calls `/api/...` on vercel.app and gets 404 | `VITE_API_URL` is not set. Add it and redeploy |
| Refreshing `/plan` gives 404 | Option A: already handled by FastAPI. Option B: already handled by `client/vercel.json` |
| "Nothing is paused on this thread" after review | The service restarted while using in-memory storage. Make sure `DATABASE_URL` is set |
