#!/usr/bin/env python3
"""
upgrade.py — Auto-upgrade skills from lessons (closes the learning loop).

Reads lessons/<type>.md produced by learn.py and patches the corresponding
skill with the distilled lesson. Idempotent (state file), append-only
(never overwrites your skills), dry-run by default.

Usage:
    python3 upgrade.py             # dry-run: show what would be patched
    python3 upgrade.py --apply     # actually patch
    python3 upgrade.py --force     # ignore idempotency

Env vars:
    HERMES_HOME    path to Hermes home (default: ~/.hermes)
"""

import os
import re
import sys
import json
import hashlib
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
LESSONS_DIR = HERMES_HOME / "skills" / "lessons"
SKILLS_DIR = HERMES_HOME / "skills"
STATE_FILE = Path(__file__).parent / ".upgrade_state.json"
SECTION_TITLE = "## Lessons (auto-upgraded)"

# Lesson type → skills to upgrade. Customize freely — default maps are generic.
TYPE_MAP = {
    "ppt":      ["ppt-workflow-order", "ppt-authoring"],
    "image":    ["image-gen-toolchain", "bra-v7-image-generation"],
    "code":     ["agent-behavior-core", "systematic-debugging"],
    "research": ["skill-router"],
    "general":  ["agent-behavior-core"],
    "pdf":      ["report-production-pipeline"],
    "video":    ["technical-video-production"],
    "data":     ["data-collection-toolchain"],
}


def parse_lessons():
    items = []
    if not LESSONS_DIR.is_dir():
        return items
    seen = set()
    for fn in sorted(os.listdir(LESSONS_DIR)):
        if not fn.endswith(".md"):
            continue
        typ = fn[:-3]
        content = (LESSONS_DIR / fn).read_text(encoding="utf-8", errors="ignore")
        blocks = re.split(r"^##\s+", content, flags=re.M)
        for b in blocks[1:]:
            date_m = re.match(r"(\d{4}-\d{2}-\d{2})[^\n]*", b)
            lesson_m = re.search(r"\*\*教训\*\*[:：]\s*(.+?)(?:\n\n|\Z)", b, re.S)
            if date_m and lesson_m:
                key = (typ, date_m.group(1))
                if key in seen:
                    continue
                seen.add(key)
                items.append({
                    "type": typ,
                    "date": date_m.group(1),
                    "lesson": lesson_m.group(1).strip()[:300],
                })
    return items


def find_skill(skill_name):
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files and os.path.basename(root) == skill_name:
            return Path(root) / "SKILL.md"
    return None


def is_patched(lesson):
    if not STATE_FILE.exists():
        return False
    h = hashlib.md5(lesson["lesson"].encode()).hexdigest()[:10]
    return h in json.loads(STATE_FILE.read_text()).get("patched", [])


def mark_patched(lesson):
    state = {"patched": []}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    h = hashlib.md5(lesson["lesson"].encode()).hexdigest()[:10]
    if h not in state["patched"]:
        state["patched"].append(h)
        state["patched"] = state["patched"][-200:]
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=1))


def patch_skill(skill_path, lesson):
    content = skill_path.read_text(encoding="utf-8", errors="ignore")
    block = f"- **{lesson['date']}** [{lesson['type']}]：{lesson['lesson']}\n"
    if lesson["lesson"][:20] in content:
        return False, "already present (skip)"
    if SECTION_TITLE in content:
        idx = content.index(SECTION_TITLE)
        insert_at = content.index("\n", idx) + 1
        new_content = content[:insert_at] + "\n" + block + content[insert_at:]
    else:
        new_content = content + f"\n{SECTION_TITLE}\n\n{block}"
    skill_path.write_text(new_content, encoding="utf-8")
    return True, "patched"


def main():
    apply = "--apply" in sys.argv
    force = "--force" in sys.argv
    lessons = parse_lessons()
    print(f"Parsed {len(lessons)} lessons from {LESSONS_DIR}")

    plan = []
    for lesson in lessons:
        if not force and is_patched(lesson):
            continue
        for target in TYPE_MAP.get(lesson["type"], ["agent-behavior-core"]):
            sp = find_skill(target)
            if sp:
                plan.append((lesson, sp, target))

    print(f"Planned upgrades: {len(plan)}")
    for lesson, sp, t in plan:
        print(f"  [{lesson['type']}] {lesson['date']} → {t}: {lesson['lesson'][:60]}...")

    if not apply:
        print("\n[dry-run] Not applied. Run with --apply to patch.")
        return

    done = 0
    for lesson, sp, t in plan:
        ok, msg = patch_skill(sp, lesson)
        if ok:
            mark_patched(lesson)
            done += 1
        print(f"  {t}: {msg}")
    print(f"\nDone: {done} skills upgraded")


if __name__ == "__main__":
    main()
