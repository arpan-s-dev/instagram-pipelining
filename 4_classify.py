"""Keyword-label notes into bundles_by_category/ and labels.jsonl."""

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

COLLECTION_HINTS = {
    "claude-hacks": "claude-ai-skills",
    "internship": "internship-hacks",
    "prep": "career-productivity",
    "tech": "tech-dev",
}


def load_collection_map() -> dict[str, str]:
    out = {}
    if not LINKS_JSONL.exists():
        return out
    for line in LINKS_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["url"]] = rec.get("collection", "unknown")
    return out


def source_url(text: str) -> str:
    m = re.search(r"^source:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def score_categories(text: str, collection: str) -> list[tuple[str, str, int]]:
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


def main():
    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        print(f"No notes in {NOTES_DIR}. Run 3_process.py first.")
        return

    coll_map = load_collection_map()
    CATEGORY_BUNDLES_DIR.mkdir(parents=True, exist_ok=True)

    labels = []
    by_category: dict[str, list[Path]] = defaultdict(list)

    for note in notes:
        raw = note.read_text(encoding="utf-8")
        text = raw.lower()
        src = source_url(raw)
        collection = coll_map.get(src, "unknown")
        scores = score_categories(text, collection)
        slug, name, score = pick_category(scores)

        labels.append({
            "id": note.stem,
            "note": str(note),
            "source": src,
            "instagram_collection": collection,
            "category_slug": slug,
            "category_name": name,
            "score": score,
            "top_matches": [{"slug": s, "name": n, "score": sc} for s, n, sc in scores[:3]],
        })
        by_category[slug].append(note)

    with LABELS_FILE.open("w", encoding="utf-8") as f:
        for rec in labels:
            f.write(json.dumps(rec) + "\n")

    summary_lines = ["# Category summary\n", f"Total items: {len(labels)}\n"]

    for cat in CATEGORIES:
        slug = cat["slug"]
        batch = by_category.get(slug, [])
        if not batch:
            continue
        parts = [n.read_text(encoding="utf-8") for n in sorted(batch)]
        out = CATEGORY_BUNDLES_DIR / f"{slug}.md"
        header = f"<!-- category: {cat['name']} | {len(batch)} items -->\n\n"
        out.write_text(header + "\n\n---\n\n".join(parts), encoding="utf-8")
        summary_lines.append(f"- **{cat['name']}** (`{slug}`): {len(batch)}")
        print(f"  {cat['name']}: {len(batch)}")

    (CATEGORY_BUNDLES_DIR / "_summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"\nWrote {LABELS_FILE} ({len(labels)} labels)")
    print(f"Category bundles: {CATEGORY_BUNDLES_DIR.resolve()}")


if __name__ == "__main__":
    main()
