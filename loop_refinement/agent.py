"""
LoopAgent demo — "iterative refinement" from slides.

Writer improves the document each iteration.
Critic reviews it and either calls exit_loop (done) or outputs improvements (loop again).
Capped at 5 iterations as a safety net.

Run: adk web (from adk-orchestra/)  →  select "loop_refinement"
Ask: "Write a short blog post about why Python is great for beginners"

Watch the State tab: current_doc and critique update on each iteration.
The loop stops when the Critic is satisfied.

Key patterns shown:
  - {critique?}  →  silently empty on iteration 1 (no KeyError)
  - exit_loop tool sets actions.escalate = True to break the loop
  - max_iterations=5 is the non-negotiable safety net
"""
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext

MODEL = "gemini-flash-latest"


def exit_loop(tool_context: ToolContext) -> dict:
    """Call this tool ONLY when the document is clear, complete, and publish-ready.
    Do NOT call it if there are still improvements to be made.

    Returns:
        dict: Empty — signals the loop to stop.
    """
    tool_context.actions.escalate = True
    return {}


writer = LlmAgent(
    name="Writer",
    model=MODEL,
    description="Writes and improves a document based on critic feedback.",
    instruction=(
        "You are a skilled writer. Your job is to produce or improve a document.\n\n"
        "Current document:\n{current_doc?}\n\n"
        "Critic feedback to address (empty on first pass):\n{critique?}\n\n"
        "If this is the first pass, write a complete first draft based on the user's original request.\n"
        "If there is critique, revise the document to address every point.\n"
        "Output ONLY the full revised document — no explanations, no commentary."
    ),
    output_key="current_doc",
)

critic = LlmAgent(
    name="Critic",
    model=MODEL,
    description="Reviews the document and either approves it or requests improvements.",
    instruction=(
        "You are an exacting editor. Review this document:\n\n"
        "{current_doc}\n\n"
        "Criteria: Is it clear, well-structured, engaging, and free of errors?\n\n"
        "If the document meets all criteria and is publish-ready, call the exit_loop tool.\n"
        "Otherwise, output exactly 2-3 specific, actionable improvements — nothing else."
    ),
    tools=[exit_loop],
    output_key="critique",
)

root_agent = LoopAgent(
    name="RefinementLoop",
    description="Iteratively refines a document with a Writer–Critic loop until publish-ready.",
    max_iterations=5,
    sub_agents=[writer, critic],
)
