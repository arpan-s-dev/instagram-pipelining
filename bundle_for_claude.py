"""Split notes/ into bundles/ files of 25 notes each."""

from config import NOTES_DIR, BUNDLES_DIR

BATCH_SIZE = 25


def main():
    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        print("No notes found. Run 3_process.py first.")
        return

    BUNDLES_DIR.mkdir(exist_ok=True)
    batches = [notes[i:i + BATCH_SIZE] for i in range(0, len(notes), BATCH_SIZE)]

    for i, batch in enumerate(batches, 1):
        parts = [n.read_text(encoding="utf-8") for n in batch]
        out = BUNDLES_DIR / f"bundle_{i:02d}.md"
        out.write_text("\n\n---\n\n".join(parts), encoding="utf-8")
        print(f"wrote {out}  ({len(batch)} items)")

    print(f"\n{len(notes)} items -> {len(batches)} bundle(s) in {BUNDLES_DIR.resolve()}")


if __name__ == "__main__":
    main()
