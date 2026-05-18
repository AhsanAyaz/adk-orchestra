"""
ContentOrchestra — the full composition from slides.

Combines all three workflow primitives:

  Stage 1 — SequentialAgent (ResearchTeam)
    Research runs sequentially to stay within free-tier rate limits.
    For paid quota, swap SequentialAgent → ParallelAgent on the ResearchTeam.
    ├── TrendResearcher    → trends
    ├── AudienceResearcher → audience
    └── CompetitorResearcher → competitors

  Stage 2 — Outliner (SequentialAgent step)
    reads trends + audience + competitors → outline

  Stage 3 — Drafter (SequentialAgent step)
    reads outline → draft

  Stage 4 — LoopAgent (RefinementLoop, max 3 iterations)
    ├── Reviser  reads draft + critique? → draft (overwrites each loop)
    └── Critic   reads draft + audience  → exit_loop or critique

All wrapped in a root SequentialAgent: research → outline → draft → refine.

Run: adk web (from adk-orchestra/)  →  select "content_orchestra"
Ask: "AI developer tools in 2026"

Watch: State tab shows all keys fill in order.
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.tool_context import ToolContext

MODEL = "gemini-flash-latest"

# ── Stage 1: Parallel Research ────────────────────────────────────────────────

trend_researcher = LlmAgent(
    name="TrendResearcher",
    model=MODEL,
    description="Finds current trends for a given topic.",
    instruction=(
        "Find 3 current trends about: {topic?}\n"
        "If no topic is provided, use the user's original message as the topic.\n"
        "Output a short bullet list of trends."
    ),
    tools=[google_search],
    output_key="trends",
)

audience_researcher = LlmAgent(
    name="AudienceResearcher",
    model=MODEL,
    description="Identifies the target audience for a topic.",
    instruction=(
        "Identify the target audience for: {topic?}\n"
        "If no topic is provided, use the user's original message as the topic.\n"
        "Output 3 concise persona bullets (role, goal, pain point)."
    ),
    tools=[google_search],
    output_key="audience",
)

competitor_researcher = LlmAgent(
    name="CompetitorResearcher",
    model=MODEL,
    description="Finds competing content for a topic.",
    instruction=(
        "Find 3 existing articles or resources about: {topic?}\n"
        "If no topic is provided, use the user's original message as the topic.\n"
        "Output: title + one-line summary for each."
    ),
    tools=[google_search],
    output_key="competitors",
)

research_team = SequentialAgent(
    name="ResearchTeam",
    description="Three sequential researchers: trends, audience, and competitors.",
    sub_agents=[trend_researcher, audience_researcher, competitor_researcher],
)

# ── Stage 2: Outline ──────────────────────────────────────────────────────────

outliner = LlmAgent(
    name="Outliner",
    model=MODEL,
    description="Builds a content outline from research.",
    instruction=(
        "Build a 5-section article outline for: {topic?}\n\n"
        "Use this research:\n"
        "Trends: {trends}\n"
        "Audience: {audience}\n"
        "Competitors (to differentiate from): {competitors}\n\n"
        "Output a numbered outline with a one-sentence description per section."
    ),
    output_key="outline",
)

# ── Stage 3: First Draft ──────────────────────────────────────────────────────

drafter = LlmAgent(
    name="Drafter",
    model=MODEL,
    description="Writes a first draft from the outline.",
    instruction=(
        "Write a complete first draft article following this outline:\n{outline}\n\n"
        "Target audience: {audience}\n"
        "Make it engaging, clear, and approximately 400 words."
    ),
    output_key="draft",
)

# ── Stage 4: Refinement Loop ──────────────────────────────────────────────────

def exit_loop(tool_context: ToolContext) -> dict:
    """Signal that the draft is publish-ready and the loop should end.

    Returns:
        dict: Status. After calling, output the word "Approved" and stop.
    """
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    if tool_context.state.get("_exit_loop_called"):
        return {
            "status": "noop",
            "message": "exit_loop was already called this turn. Do not call it again. Output the word Approved and stop.",
        }
    tool_context.state["_exit_loop_called"] = True
    return {
        "status": "loop_exited",
        "message": "Loop terminated. Output the word Approved and stop generating.",
    }


reviser = LlmAgent(
    name="Reviser",
    model=MODEL,
    description="Revises the draft based on critic feedback.",
    instruction=(
        "Revise the following article draft:\n{draft}\n\n"
        "Apply this critique (empty on first revision pass):\n{critique?}\n\n"
        "Output ONLY the full revised article."
    ),
    output_key="draft",  # intentionally overwrites draft each iteration
)

critic = LlmAgent(
    name="Critic",
    model=MODEL,
    description="Reviews the draft and either approves or requests improvements.",
    instruction=(
        "Critique the following article:\n{draft}\n\n"
        "Check: Is it clear, accurate, engaging, and well-structured for this audience?\n"
        "Audience: {audience}\n\n"
        "Decide ONE of these two paths and do exactly one of them:\n\n"
        "PATH A — Article is publish-ready:\n"
        "  1. Call the exit_loop tool exactly ONCE.\n"
        "  2. Then output the single word: Approved.\n"
        "  3. STOP. Do not call exit_loop again.\n\n"
        "PATH B — Article still needs work:\n"
        "  1. Do NOT call exit_loop.\n"
        "  2. Output exactly 2-3 specific improvements as a bullet list.\n"
        "  3. Nothing else."
    ),
    tools=[exit_loop],
    output_key="critique",
)

refinement_loop = LoopAgent(
    name="RefinementLoop",
    description="Iterative revise–critique loop, max 3 passes.",
    max_iterations=3,
    sub_agents=[reviser, critic],
)

# ── Root: Full Orchestra ──────────────────────────────────────────────────────

root_agent = SequentialAgent(
    name="ContentOrchestra",
    description=(
        "Full content pipeline: research → outline → draft → iterative refinement. "
        "Give it a topic and it produces a polished article."
    ),
    sub_agents=[research_team, outliner, drafter, refinement_loop],
)
