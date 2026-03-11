"""
Bundle raw notes for Claude (unchanged workflow) OR use 4_classify.py for categories.

Run:  python bundle_for_claude.py          # flat batches of 25
      python 4_classify.py                 # sorted by topic category
"""

from pathlib import Path

from config import NOTES_DIR, BUNDLES_DIR

BATCH_SIZE = 25


def main():
    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        print("No notes found. Run 3_process.py first.")
        return

