"""
ParallelAgent demo — "fan-out / gather" from slides.

Three researchers run concurrently, each writing a UNIQUE output_key.
A Synthesizer runs after all three complete (wrapped in SequentialAgent).

google_search is used here as a grounding tool (Gemini built-in).
Rule: each agent that uses google_search has NO other tools.

Run: adk web (from adk-orchestra/)  →  select "parallel_research"
Ask: "Research the future of renewable energy"

Watch the Events tab: branch events from all three researchers interleave in real time.

⚠️  Pitfall shown: each branch uses a unique output_key — no race condition.
"""
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

MODEL = "gemini-flash-latest"

renewable_researcher = LlmAgent(
    name="RenewableResearcher",
    model=MODEL,
    description="Researches renewable energy trends.",
    instruction=(
        "Research the 3 most important recent developments in renewable energy. "
        "Output a 2-sentence summary."
    ),
    tools=[google_search],
    output_key="renewable_result",
)

ev_researcher = LlmAgent(
    name="EVResearcher",
    model=MODEL,
    description="Researches electric vehicle technology trends.",
    instruction=(
        "Research the latest key advances in electric vehicle technology. "
        "Output a 2-sentence summary."
    ),
    tools=[google_search],
    output_key="ev_result",
)

carbon_researcher = LlmAgent(
    name="CarbonResearcher",
    model=MODEL,
    description="Researches carbon capture methods.",
    instruction=(
        "Research the most promising current carbon capture methods and breakthroughs. "
        "Output a 2-sentence summary."
    ),
    tools=[google_search],
    output_key="carbon_result",
)

research_team = ParallelAgent(
    name="ResearchTeam",
    description="Three concurrent researchers covering renewable energy, EVs, and carbon capture.",
    sub_agents=[renewable_researcher, ev_researcher, carbon_researcher],
)

synthesizer = LlmAgent(
    name="Synthesizer",
    model=MODEL,
    description="Combines parallel research into a structured report.",
    instruction=(
        "Combine the following research into one structured markdown report with three sections:\n\n"
        "**Renewable Energy:**\n{renewable_result}\n\n"
        "**Electric Vehicles:**\n{ev_result}\n\n"
        "**Carbon Capture:**\n{carbon_result}\n\n"
        "Add a short 'Key Takeaways' section at the end."
    ),
)

root_agent = SequentialAgent(
    name="ResearchAndSynthesize",
    description="Fan-out to three parallel researchers, then synthesize into one report.",
    sub_agents=[research_team, synthesizer],
)
