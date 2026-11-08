"""Booking & exploring links, built by code (never by the AI, so they can't be made up).

Each link is a search URL on a well-known site, pre-filled with the trip details.
"""
from urllib.parse import quote_plus

# How the AI should link places: a Google Maps search URL always works.
MAPS_LINK_RULE = (
    "Make every hotel, attraction and restaurant a Markdown link to Google Maps using exactly "
    "this format: [Name](https://www.google.com/maps/search/?api=1&query=Name+City). "
    "You may also keep real https links that appear in the research. Never invent other URLs."
)


def booking_links(state: dict) -> str:
    """A Markdown section with search links for the trip, or '' if there is no destination."""
    dest, origin, dates = state.get("destination"), state.get("origin"), state.get("dates") or ""
    if not dest:
        return ""
    d = quote_plus(dest)
    links = []
    if origin and "flight_agent" in state.get("agents", []):
        q = quote_plus(f"Flights from {origin} to {dest} {dates}".strip())
        links.append(f"- ✈️ [Flights on Google Flights](https://www.google.com/travel/flights?q={q})")
    links += [
        f"- 🏨 [Hotels on Booking.com](https://www.booking.com/searchresults.html?ss={d})",
        f"- 🏠 [Stays on Airbnb](https://www.airbnb.com/s/{quote_plus(dest)}/homes)",
        f"- 🗺️ [Things to do on Google Maps](https://www.google.com/maps/search/?api=1&query=things+to+do+in+{d})",
        f"- ⭐ [Reviews on Tripadvisor](https://www.tripadvisor.com/Search?q={d})",
    ]
    return "\n\n---\n\n## Book & explore\n" + "\n".join(links)
