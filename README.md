# EvolveAgent

**Make your AI agent smarter every day — zero config, download & run.**

[中文](README.zh.md) | English

## The Problem

Your agent keeps doing this, doesn't it?

- Repeats the **same mistake N times** — corrected yesterday, stepped on today
- Has **300 skills installed but executes almost none** — the right one never gets called, the irrelevant ones get shipped every request
- Prompt grows **fatter and fatter** — burning tokens and attention every turn

You've tried "memory systems". The uncomfortable truth: **memory solves "does it remember", not "does it obey"** — two completely different problems.

## The Philosophy: Rules as Code, Not Docs

A skill file is a *document* — it works only if the model reads it AND decides to comply. Unreliable.

**EvolveAgent turns lessons into CODE.** A lesson is compiled into a guardrail rule that **executes before the task** and can **block it (exit 2)**. No model compliance involved — the rule either passes or it doesn't.

## Four Scripts, One Evolution Loop

| Script | Stage | Usage |
|--------|-------|-------|
| `planner.py` | Force a 5-step plan before tasks. **Blocks (exit 2) if goal isn't clear** | `python3 planner.py "task"` |
| `learn.py` | Scan logs for negative feedback → LLM judge → **lessons distilled** | `python3 learn.py --hours 24` |
| `upgrade.py` | Lessons → **compiled into guardrail CODE** (`guardrails/<type>.py` with rule data + check functions) | `python3 upgrade.py --apply` |
| `guardrail.py` | **Enforce before execution**: run the rule code, block on violation (exit 2), print lesson checklist | `python3 guardrail.py <type> "task"` |

```
failure log → learn.py → lessons/<type>.md → upgrade.py → guardrails/<type>.py (CODE)
                                                          ↓
              before the task: guardrail.py <type> "task" → violation = exit 2
```

## Install (10 seconds, zero config)

```bash
cp -r evolve-agent ~/.hermes/skills/
# restart your gateway. Done.

# Optional: daily self-evolution via cron
#   0 1 * * *  learn.py --hours 24 && upgrade.py --apply
# Optional: enforce before tasks (make it step 1 of your agent workflow)
#   python3 guardrail.py <type> "<task description>"
```

## Verify It Works (30 seconds)

```bash
cd evolve-agent/scripts
python3 planner.py "some task"        # empty goal → exit 2
python3 guardrail.py ppt "make ppt"   # too-short description → exit 2
```

Blocked = working. That's it.

## Why It Works

1. **System 1 / System 2** (Kahneman): instinctive behavior → code; real judgment → LLM
2. **Move critical paths out of the LLM**: reliability comes from code execution, not model compliance — guardrails are code, violations get blocked
3. **Failures are gold**: lessons are compiled into executable rules and enforced before the next task (ReasoningBank, ICLR 2026)

## Configuration (all optional — works out of the box)

| Env var | Default | Description |
|---------|---------|-------------|
| `HERMES_HOME` | `~/.hermes` | Hermes data directory |
| `LLM_BASE_URL` | `http://localhost:8080/v1` | Any OpenAI-compatible endpoint (Ollama, Gemma, DeepSeek, OpenAI, Qwen...) |
| `LLM_API_KEY` | empty | empty = local, no auth |
| `LLM_MODEL` | `qwen2.5:7b` | Judge model |

## Pitfalls (we fell in so you don't)

- The LLM judge at **70% accuracy is enough** — don't chase perfection, chase iteration
- Lessons must be **transferable** ("how to think about this task type"), not "what I did this one time"
- **`upgrade.py` writes code, not docs** — appending a lesson to a markdown skill file is exactly what this package does NOT do
- Task types are **generic words** (ppt/pdf/research/code/image/data/chat) — never bound to any specific skill name

## Framework Support — Read This First

**✅ Hermes: download & run, zero config.** That is the only zero-setup guarantee.

**⚠️ Other agent frameworks: the mechanism works, but you MUST adapt it yourself** (two small edits):

| Script | Hermes default (zero config) | Other frameworks: what you must change |
|--------|------------------------------|----------------------------------------|
| `learn.py` | parses `inbound message: text=...` log lines | rewrite `extract_user_message()` regex for your log format |
| `upgrade.py` | reads lessons from `~/.hermes/skills/lessons/` | point `LESSONS_DIR` at your lessons dir |
| `planner.py` / `guardrail.py` | nothing | nothing — framework-free by design |

Everything is configurable via `HERMES_HOME` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` env vars.

## License

MIT
