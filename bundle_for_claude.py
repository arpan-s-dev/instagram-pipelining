"""
Bundle raw notes for Claude (unchanged workflow) OR use 4_classify.py for categories.

Run:  python bundle_for_claude.py          # flat batches of 25
      python 4_classify.py                 # sorted by topic category
"""

from pathlib import Path

from config import NOTES_DIR, BUNDLES_DIR

BATCH_SIZE = 25  # keep pastes under typical chat limits


def main():
    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        print("No notes found. Run 3_process.py first.")
        return

    BUNDLES_DIR.mkdir(exist_ok=True)
    batches = [notes[i:i + BATCH_SIZE] for i in range(0, len(notes), BATCH_SIZE)]

    for bi, batch in enumerate(batches, 1):
        parts = [n.read_text(encoding="utf-8") for n in batch]
        out = BUNDLES_DIR / f"bundle_{bi:02d}.md"
        out.write_text("\n\n---\n\n".join(parts), encoding="utf-8")
        print(f"wrote {out}  ({len(batch)} items)")

    print(f"\n{len(notes)} items → {len(batches)} bundle(s) in {BUNDLES_DIR.resolve()}")
    print("For labeled bundles by topic, run: python 4_classify.py")


if __name__ == "__main__":
    main()
