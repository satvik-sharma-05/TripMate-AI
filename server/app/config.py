"""All settings in one place, read from the .env file."""
import os

from dotenv import load_dotenv  # python-dotenv: loads KEY=value lines from .env into os.environ

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]          # required: the LLM provider key
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")           # writes plans
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")  # runs research agents
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")    # web search (hotels, flights)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")        # empty = keep memory in RAM (fine for demos)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")  # which websites may call this API
