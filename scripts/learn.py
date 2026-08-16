#!/usr/bin/env python3
"""
learn.py — Automatic failure learning (ReasoningBank pattern).

Scans recent agent logs for negative user feedback, judges real failures with
an LLM, and distills transferable lessons into lessons/<type>.md.

Zero-config by default: paths default to ~/.hermes, LLM defaults to a local
OpenAI-compatible endpoint (override with env vars).

Usage:
    python3 learn.py [--hours 24] [--judge-limit 5] [--dry-run]

Env vars (all optional):
    HERMES_HOME    path to Hermes home (default: ~/.hermes)
    LLM_BASE_URL   OpenAI-compatible endpoint (default: http://localhost:8080/v1)
    LLM_API_KEY    API key (empty = local no-auth)
    LLM_MODEL      model name (default: qwen2.5:7b)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
LESSONS_DIR = HERMES_HOME / "skills" / "lessons"

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8080/v1").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:7b")

# Negative-feedback signals (tune to your language; precision over recall)
NEGATIVE_SIGNALS = [
    "烂", "很差", "太差", "不行", "没做好", "糟糕", "乱码",
    "没照", "不照", "不齐全", "重做", "再试", "不满意", "失败",
    "做不了", "糊弄", "别动", "不对", "错了", "不是这样",
    "bad", "wrong", "terrible", "useless", "broken", "redo", "fails",
]

# Task-type inference (add your own)
TASK_TYPES = [
    ("ppt", ["ppt", "简报", "演示", "slides", "deck", "slide"]),
    ("pdf", ["pdf", "报告", "文档", "report", "doc"]),
    ("research", ["研究", "调研", "搜索", "查一下", "分析", "research", "search"]),
    ("code", ["代码", "写个", "脚本", "程序", "函数", "bug", "code", "script"]),
    ("image", ["画", "图", "图片", "生图", "插图", "配图", "image", "illustration"]),
    ("data", ["数据", "表格", "excel", "统计", "data", "csv"]),
    ("chat", ["聊聊", "解释", "什么", "为什么", "怎么", "explain"]),
]


def detect_task_type(text: str) -> str:
    for ttype, kws in TASK_TYPES:
        for kw in kws:
            if kw in text.lower():
                return ttype
    return "general"


def log_paths():
    """Default: <hermes_home>/logs/agent.log. Add more with --profiles."""
    base = HERMES_HOME / "logs" / "agent.log"
    return [base]


def extract_user_message(line: str):
    """Platform-agnostic user-message extraction from a log line."""
    patterns = [
        re.compile(r"inbound message:.*?(?:text|msg)=['\"]?(.*?)['\"]?\s*$", re.S),
        re.compile(r"Inbound.*?(?:text|msg)=['\"]?(.*?)['\"]?\s*$", re.S),
        re.compile(r"user message: (.*)", re.S),
    ]
    for p in patterns:
        m = p.search(line)
        if m:
            return m.group(1)
    return None


def scan_logs(hours: int) -> list:
    cutoff = datetime.now() - timedelta(hours=hours)
    candidates = []
    for log_path in log_paths():
        if not log_path.exists():
            print(f"⚠️ log not found: {log_path}")
            continue
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                if not m:
                    continue
                try:
                    ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if ts < cutoff:
                    continue
                text = extract_user_message(line)
                if not text:
                    continue
                if any(sig in text for sig in NEGATIVE_SIGNALS) and len(text) > 8:
                    candidates.append({
                        "timestamp": ts.isoformat(),
                        "text": text[:500],
                        "task_type": detect_task_type(text),
                        "profile": "default",
                    })
    return candidates


def judge_with_llm(task_text: str) -> dict:
    """LLM-as-Judge via OpenAI-compatible API."""
    import urllib.request

    if not LLM_API_KEY:
        # try common local no-auth endpoint
        pass
    prompt = f"""You are a task judge for an AI agent. Determine whether the task
below failed, based on the user's feedback. If it failed, distill a transferable lesson.

【User feedback】{task_text}

Output strict JSON:
{{
  "verdict": "success" or "failure" or "unknown",
  "failure_mode": "one-line failure mode (e.g. started coding without a plan)",
  "lesson": "preventive lesson (e.g. define the goal and acceptance criteria before starting)"
}}"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a task judge. Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        f"{LLM_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"]
        # strip markdown fences if present
        content = content.strip().strip("`")
        if content.startswith("json"):
            content = content[4:].strip()
        return json.loads(content)
    except Exception as e:
        return {"verdict": "unknown", "reason": f"judge error: {e}"}


def save_lesson(entry: dict):
    os.makedirs(LESSONS_DIR, exist_ok=True)
    path = LESSONS_DIR / f"{entry['task_type']}.md"
    block = (
        f"\n## {entry['timestamp'][:10]} — failure\n\n"
        f"**失败模式**：{entry['failure_mode']}\n\n"
        f"**教训**：{entry['lesson']}\n\n"
        f"**用户原话**：{entry['text'][:200]}\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
    return path


def main():
    ap = argparse.ArgumentParser(description="Automatic failure learning")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--judge-limit", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    candidates = scan_logs(args.hours)
    print(f"Scanned logs: {len(candidates)} negative-feedback candidates in last {args.hours}h")

    judged = 0
    for c in candidates[:args.judge_limit]:
        result = judge_with_llm(c["text"])
        judged += 1
        if result.get("verdict") == "failure":
            entry = {**c, "failure_mode": result.get("failure_mode", "?"),
                     "lesson": result.get("lesson", "?")}
            if args.dry_run:
                print(f"  [dry-run] would save: {c['task_type']} — {entry['lesson'][:60]}")
            else:
                path = save_lesson(entry)
                print(f"  ✓ lesson saved → {path} ({entry['lesson'][:50]}...)")
        else:
            print(f"  - {c['task_type']}: verdict={result.get('verdict')}")
        time.sleep(0.5)  # be gentle to local LLM

    if judged == 0:
        print("No candidates judged (increase --hours or --judge-limit).")


if __name__ == "__main__":
    main()
