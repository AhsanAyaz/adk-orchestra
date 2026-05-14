"""
SequentialAgent demo — the "assembly line" from slides.

Pipeline: CodeWriter → CodeReviewer → CodeRefactorer
Each step reads the previous step's output via session state.

Run: adk web (from adk-orchestra/)  →  select "sequential_pipeline"
Ask: "Write a function that checks if a number is prime"

Watch the State tab: generated_code → review_comments → refactored_code appear one by one.
"""
from google.adk.agents import LlmAgent, SequentialAgent

MODEL = "gemini-flash-latest"

writer = LlmAgent(
    name="CodeWriter",
    model=MODEL,
    description="Writes Python code from a user spec.",
    instruction=(
        "Write a clean Python implementation for the user's spec. "
        "Output ONLY the code inside a ```python``` block. No explanations."
    ),
    output_key="generated_code",
)

reviewer = LlmAgent(
    name="CodeReviewer",
    model=MODEL,
    description="Reviews generated code for bugs and quality issues.",
    instruction=(
        "Review the following Python code:\n"
        "```python\n{generated_code}\n```\n\n"
        "List any bugs, edge cases, or quality issues as a bullet list. "
        "If the code looks good, say exactly: 'No major issues found.'"
    ),
    output_key="review_comments",
)

refactorer = LlmAgent(
    name="CodeRefactorer",
    model=MODEL,
    description="Refactors code applying reviewer feedback.",
    instruction=(
        "Refactor the following Python code:\n"
        "```python\n{generated_code}\n```\n\n"
        "Apply these review comments:\n{review_comments}\n\n"
        "Output ONLY the final improved code inside a ```python``` block."
    ),
    output_key="refactored_code",
)

root_agent = SequentialAgent(
    name="CodePipeline",
    description="A three-stage code pipeline: write → review → refactor.",
    sub_agents=[writer, reviewer, refactorer],
)
