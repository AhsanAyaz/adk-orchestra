"""
Single LlmAgent demo — the "soloist" from slide 1.

Shows:
- Basic LlmAgent with a custom Python tool
- How docstrings drive tool calling

Run: adk web (from adk-orchestra/)  →  select "single_agent"
Ask: "What's the weather in Stockholm?" or "What's the weather in Tokyo?"
"""
from google.adk.agents import LlmAgent

MODEL = "gemini-flash-latest"


def get_weather(city: str) -> dict:
    """Retrieves the current weather for a city.

    Args:
        city: The city name to look up.

    Returns:
        dict: status and result or error message.
    """
    data = {
        "stockholm": "Sunny, 22°C",
        "london": "Cloudy, 15°C",
        "new york": "Partly cloudy, 18°C",
        "tokyo": "Rainy, 20°C",
        "prishtina": "Clear, 24°C",
        "berlin": "Overcast, 17°C",
        "paris": "Sunny, 21°C",
    }
    report = data.get(city.lower())
    if report:
        return {"status": "success", "report": report}
    return {"status": "error", "error_message": f"No weather data for '{city}'."}


root_agent = LlmAgent(
    name="SingleAgent",
    model=MODEL,
    description="A weather assistant that looks up current conditions for cities.",
    instruction=(
        "You help users check the weather. "
        "Always use the get_weather tool to look up conditions for any city they ask about."
    ),
    tools=[get_weather],
)
