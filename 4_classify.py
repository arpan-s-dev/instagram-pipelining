"""
Stage 4 — Auto-label notes into categories (local keyword scoring).

Reads notes/*.md, scores against categories in config.py, writes:
  labels.jsonl              — one JSON record per item
  bundles_by_category/      — one .md per category (paste into Claude to refine)
  bundles_by_category/_summary.md — counts per category

This is a first pass. Paste category bundles into Claude to fix mislabels.

Run:  python 4_classify.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

from config import (
    CATEGORIES,
    MIN_CLASSIFY_SCORE,
    NOTES_DIR,
    LABELS_FILE,
    CATEGORY_BUNDLES_DIR,
    LINKS_JSONL,
)

# Instagram collection name → category slug hints (boost score)
COLLECTION_HINTS = {
    "claude-hacks": "claude-ai-skills",
    "internship": "internship-hacks",
    "prep": "career-productivity",
    "tech": "tech-dev",
}


def load_collection_map() -> dict[str, str]:
    """Map post URL → Instagram saved collection name."""
    out = {}
    if not LINKS_JSONL.exists():
        return out
    for line in LINKS_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        out[rec["url"]] = rec.get("collection", "unknown")
    return out


def note_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def source_url(text: str) -> str:
    m = re.search(r"^source:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def score_categories(text: str, collection: str) -> list[tuple[str, str, int]]:
    """Return [(slug, name, score), ...] sorted by score desc."""
    scores = []
    hint_slug = COLLECTION_HINTS.get(collection)

    for cat in CATEGORIES:
        if cat["slug"] == "other":
            continue
        score = 0
        for kw in cat["keywords"]:
            if kw in text:
                score += text.count(kw)
        if hint_slug and cat["slug"] == hint_slug:
            score += 3
        if score > 0:
            scores.append((cat["slug"], cat["name"], score))

    scores.sort(key=lambda x: -x[2])
    return scores


def pick_category(scores: list[tuple[str, str, int]]) -> tuple[str, str, int]:
    if not scores or scores[0][2] < MIN_CLASSIFY_SCORE:
        other = next(c for c in CATEGORIES if c["slug"] == "other")
        return other["slug"], other["name"], 0
    return scores[0]

