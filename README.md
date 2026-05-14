# ADK Orchestra

Demo agents for the **Zero to Agentic Orchestra** talk — live code examples for every workflow primitive in [Google ADK](https://google.github.io/adk-docs/).

## Setup

```bash
./setup.sh
# edit .env and add your GOOGLE_API_KEY (from aistudio.google.com)
source .venv/bin/activate
adk web
```

Pick any agent from the dropdown and start chatting.

---

## Agents

### 1. `single_agent` — The Soloist
A single `LlmAgent` with a custom Python tool.

**Concepts:** `LlmAgent`, tool docstrings, function tools  
**Try:** `What's the weather in Stockholm?`

---

### 2. `sequential_pipeline` — The Assembly Line
Three agents chained in order: **CodeWriter → CodeReviewer → CodeRefactorer**.  
Each step reads the previous step's output via `output_key` → session state.

**Concepts:** `SequentialAgent`, `output_key`, `{state_key}` templates  
**Try:** `Write a function that checks if a number is prime`  
**Watch:** State tab — `generated_code` → `review_comments` → `refactored_code` fill in order

---

### 3. `parallel_research` — Fan-out / Gather
Three researchers run **concurrently**, each writing a unique key. A Synthesizer combines them after.

**Concepts:** `ParallelAgent`, unique `output_key` per branch, fan-out pattern  
**Try:** `Research the future of renewable energy`  
**Watch:** Events tab — branch events from all three researchers interleave in real time

> ⚠️ Each parallel branch must write to a **different** `output_key` — same key = silent overwrite.

---

### 4. `loop_refinement` — Iterative Refinement
A **Writer–Critic loop** that runs until the Critic is satisfied or `max_iterations` is hit.

**Concepts:** `LoopAgent`, `exit_loop` tool, `{key?}` optional state, `max_iterations`  
**Try:** `Write a short blog post about why Python is great for beginners`  
**Watch:** State tab — `current_doc` and `critique` update on every iteration

> ⚠️ Always set `max_iterations` — a never-satisfied critic will loop forever (and run up your bill).

---

### 5. `content_orchestra` — The Full Orchestra
All three primitives composed into one pipeline:

```
ParallelAgent  (research: trends + audience + competitors)
      ↓
  Outliner  →  Drafter
      ↓
LoopAgent  (Reviser ↔ Critic, max 3 passes)
```

**Concepts:** Everything above, composed  
**Try:** `AI developer tools in 2026`  
**Watch:** State tab shows every key fill in sequence; Events tab shows the full event stream

---

## How data flows

```
output_key="result"          →  writes to session.state["result"]
instruction="... {result}"   →  reads from session.state["result"]
```

This is the wire between agents. No manual state management needed.

## `google_search` grounding

Researcher agents use `google_search` as a **Gemini built-in grounding tool** — not a regular function call. Two rules:

1. An agent using `google_search` must have **no other tools** in its `tools` list.
2. Don't tell the model to "call google_search" in the instruction — just describe the research task and grounding activates automatically.

## Resources

| | |
|---|---|
| Official docs | google.github.io/adk-docs |
| Python SDK | github.com/google/adk-python |
| Sample agents | github.com/google/adk-samples |
| This talk's repo | github.com/AhsanAyaz/ai-agents-google-adk |
