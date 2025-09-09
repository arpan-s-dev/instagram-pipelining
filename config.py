"""
Shared settings for Instagram Pipelining.

Set IG_USERNAME in the environment, or edit USERNAME below.
Re-run stage 4 after changing CATEGORIES.
"""

import os
from pathlib import Path

# --- account ---
USERNAME = os.environ.get("IG_USERNAME", "YOUR_INSTAGRAM_USERNAME")

# --- paths ---
SESSION_DIR = Path("ig_session")
COOKIES_FILE = Path("cookies.txt")
LINKS_TXT = Path("links.txt")
LINKS_JSONL = Path("links.jsonl")       # url + collection metadata
MEDIA_DIR = Path("videos")              # reels (.mp4) and photos (.jpg, .webp)
NOTES_DIR = Path("notes")
LABELS_FILE = Path("labels.jsonl")      # auto-classification output
BUNDLES_DIR = Path("bundles")
CATEGORY_BUNDLES_DIR = Path("bundles_by_category")

# --- harvest ---
SCROLL_PAUSE = (2.0, 4.0)
MAX_STALE_SCROLLS = 8                   # higher for large saved libraries

# Optional: extra collection URLs (auto-discovery also runs on /saved/)
EXTRA_COLLECTIONS: list[str] = []
