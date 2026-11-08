"""Every agent is an async function: takes the state, returns updated fields."""
from app.agents.budget import budget_agent
from app.agents.final import final_agent
from app.agents.flight import flight_agent
from app.agents.hotel import hotel_agent
from app.agents.hitl import human_review
from app.agents.itinerary import itinerary_agent
from app.agents.supervisor import SPECIALISTS, supervisor_agent
from app.agents.weather import weather_agent
