"""The Large Language Models (LLMs) shared by every agent.

LangChain gives every LLM provider the same interface, so swapping Groq for
OpenAI/Anthropic later means changing only this file.

We use two models: a big one for writing plans, a small fast one for research
agents. Groq's free tier limits tokens per minute AND per day *per model*, so
each model is also the other's backup: if one hits its limit, the other answers.
"""
from datetime import date

from langchain_groq import ChatGroq  # LangChain's wrapper around Groq's fast LLM API

from app.config import GROQ_API_KEY, GROQ_FAST_MODEL, GROQ_MODEL


def _groq(model: str, max_tokens: int) -> ChatGroq:
    return ChatGroq(
        model=model,
        api_key=GROQ_API_KEY,
        temperature=0.3,
        reasoning_effort="low",  # GPT-OSS "thinks" before answering; low = faster, fewer tokens
        max_tokens=max_tokens,   # upper limit on reply length (includes the thinking)
        max_retries=2,           # short waits are retried; long ones switch to the backup model
    )


big_llm = _groq(GROQ_MODEL, max_tokens=5000)          # writer: itineraries need room
fast_llm = _groq(GROQ_FAST_MODEL, max_tokens=1500)    # researchers: short summaries
backup_writer = _groq(GROQ_FAST_MODEL, max_tokens=5000)
backup_researcher = _groq(GROQ_MODEL, max_tokens=1500)

# with_fallbacks: try the first model; if it errors (e.g. rate limit), try the next one.
llm = big_llm.with_fallbacks([backup_writer])


def today() -> str:
    return date.today().strftime("%d %B %Y")  # LLMs don't know today's date unless told


async def ask(system: str, prompt: str) -> str:
    """Send one system instruction + one user prompt to the writer model, return the text."""
    reply = await llm.ainvoke([("system", f"{system} Today is {today()}."), ("user", prompt)])
    return reply.content
