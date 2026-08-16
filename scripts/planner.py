#!/usr/bin/env python3
"""
planner.py — End-with-the-end task planner (5 steps, enforced).

Run this BEFORE starting any multi-step / agentic task. It produces a
task_plan.md with the five-step plan and BLOCKS (exit 2) if the goal or
acceptance criteria are missing — the most common cause of agent flailing.

Usage:
    python3 planner.py "task description"          # skeleton mode
    python3 planner.py                             # interactive (guided prompts)
    python3 planner.py "..." --output plan.md

Exit codes:
    0  plan complete and valid
    2  validation failed (goal/acceptance empty) — do NOT start working
"""

import sys
import os
import json
import argparse
import datetime

STEPS = {
    "1_goal": {"deliverable": "", "acceptance": ""},
    "2_constraints": {"measured": "", "source": ""},
    "3_path": {"path": "", "risk": "", "fallback": ""},
    "4_classify": {"type": "", "runner": ""},
    "5_verify": {"real_test": "", "delivery_check": ""},
}

HINTS = {
    "1_goal": "If you can't write the deliverable, you don't understand the task — ask first.",
    "2_constraints": "Measure > guess: 20 minutes of measuring beats 4 hours of trial and error.",
    "3_path": "Pick the path inside your circle of influence. Don't bet on the environment changing.",
    "4_classify": "Deterministic work → code/scripts. Real judgment/generation → LLM.",
    "5_verify": "A real task passing is the only 'done'. 'Pipeline works' is not a result.",
}


def interactive(task: str) -> dict:
    plan = {k: dict(v) for k, v in STEPS.items()}
    print("\n" + "=" * 56)
    print(f"Task: {task}")
    print("Five-step plan (Enter to skip — skips get blocked by validation)")
    print("=" * 56)
    for step, fields in STEPS.items():
        print(f"\n【{step}】{HINTS[step]}")
        for field in fields:
            val = input(f"  {field}? ").strip()
            plan[step][field] = val
    return plan


def skeleton(task: str) -> dict:
    return {k: dict(v) for k, v in STEPS.items()}


def validate(plan: dict) -> list:
    issues = []
    if not plan["1_goal"]["deliverable"]:
        issues.append("Deliverable is empty — what does the user get in hand?")
    if not plan["1_goal"]["acceptance"]:
        issues.append("Acceptance criteria are empty — how do we know it's done?")
    return issues


def render(task: str, plan: dict, issues: list) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Task Plan (end with the end) | {now}",
        "",
        f"**Task**: {task}",
        "",
        "## Step 1 — Goal",
        f"- Deliverable: {plan['1_goal']['deliverable'] or '（empty）'}",
        f"- Acceptance: {plan['1_goal']['acceptance'] or '（empty）'}",
        "",
        "## Step 2 — Constraints",
        f"- Measured: {plan['2_constraints']['measured'] or '（empty）'}",
        f"- Source: {plan['2_constraints']['source'] or '（empty）'}",
        "",
        "## Step 3 — Path",
        f"- Path: {plan['3_path']['path'] or '（empty）'}",
        f"- Risk: {plan['3_path']['risk'] or '（empty）'}",
        f"- Fallback: {plan['3_path']['fallback'] or '（empty）'}",
        "",
        "## Step 4 — Classify",
        f"- Task type: {plan['4_classify']['type'] or '（empty）'}",
        f"- Runner: {plan['4_classify']['runner'] or '（empty）'}",
        "",
        "## Step 5 — Verify",
        f"- Real-task test: {plan['5_verify']['real_test'] or '（empty）'}",
        f"- Delivery check: {plan['5_verify']['delivery_check'] or '（empty）'}",
        "",
    ]
    if issues:
        lines += ["## ⚠️ VALIDATION FAILED — do NOT start", ""]
        lines += [f"- {i}" for i in issues]
        lines += [""]
    else:
        lines += ["✅ Plan valid. You may start.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="End-with-the-end planner")
    ap.add_argument("task", nargs="?", help="task description (omit for interactive)")
    ap.add_argument("--output", "-o", default="task_plan.md")
    args = ap.parse_args()

    task = args.task or input("Task description? ")
    if not task.strip():
        print("Error: no task description.")
        sys.exit(1)

    plan = interactive(task) if not args.task else skeleton(task)
    issues = validate(plan)
    md = render(task, plan, issues)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nPlan written to {args.output}")
    if issues:
        print("❌ Validation failed:")
        for i in issues:
            print(f"   - {i}")
        sys.exit(2)
    print("✅ Validation passed. Go.")


if __name__ == "__main__":
    main()
