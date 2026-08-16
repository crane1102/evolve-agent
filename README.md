# EvolveAgent

**Make your AI agent smarter every day — zero config, download & run.**

[中文](README.zh.md) | English

## The Problem

Your agent keeps doing this, doesn't it?

- Repeats the **same mistake N times** — corrected yesterday, stepped on today
- Has **300 skills installed but executes almost none** — the right one never gets called, the irrelevant ones get shipped every request
- Prompt grows **fatter and fatter** — burning tokens and attention every turn

You've tried "memory systems". The uncomfortable truth: **memory solves "does it remember", not "does it obey"** — two completely different problems.

## The Fix

Three scripts that close a **self-evolution loop**:

| Script | Superpower | Usage |
|--------|-----------|-------|
| `planner.py` | Forces a 5-step plan before every task. **Blocks you (exit 2) if the goal isn't clear** — kills the "4-hour flailing" failure mode | `python3 planner.py "task"` |
| `learn.py` | Scans logs for negative feedback → an LLM judge decides real failures → **lessons auto-distilled** | `python3 learn.py --hours 24` |
| `upgrade.py` | Lessons **auto-patch the matching skill** (idempotent, append-only) | `python3 upgrade.py --apply` |

```
failure log → LLM judge → lessons/<type>.md → upgrade.py patches the skill
   → next task reads the upgraded skill → never repeats that mistake → loop
```

## Install (10 seconds, zero config)

```bash
cp -r evolve-agent ~/.hermes/skills/
# restart your gateway. Done.

# Optional: daily self-evolution via cron
#   0 1 * * *  learn.py --hours 24 && upgrade.py --apply
```

## Verify It Works (30 seconds)

```bash
cd evolve-agent/scripts
python3 planner.py "some task"    # leaves goal empty → blocked with exit 2
```

Blocked = working. That's it.

## Why It Works

1. **System 1 / System 2** (Kahneman): instinctive behavior → code; real judgment → LLM
2. **Move critical paths out of the LLM**: reliability comes from code execution, not model compliance
3. **Failures are gold**: counterfactual signals from failures teach more than successes (ReasoningBank, ICLR 2026)

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
- **Idempotency is mandatory** — without it, skills get polluted by the same lesson forever
- **Append-only** — purification is incremental improvement, never a rewrite of user skills

## How It Fits the Hermes Skill Model

`evolve-agent/` is a plain Hermes skill directory: `SKILL.md` (routing + instructions) + `scripts/` (the actual logic). Drop it into your skills dir and the index picks it up automatically. The deterministic parts (validation, dedup, patching) live in the scripts — **no model sampling on the critical path**.

## License

MIT
