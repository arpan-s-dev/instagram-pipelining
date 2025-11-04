"""
Stage 1 — Harvest ALL saved reels and photos from Instagram.

Opens a visible Chrome window (or uses cookies.txt / ig_session).

Harvest order:
  1. /saved/all-posts/  — everything you've saved
  2. Auto-discovered collections from /saved/
  3. Any EXTRA_COLLECTIONS in config.py

Writes:
  links.txt   — one URL per line (for yt-dlp)
  links.jsonl — url + collection + kind metadata (for labeling)

Run:  python 1_harvest_links.py
      python 1_harvest_links.py --fresh
"""

import argparse
import asyncio
import json
import random
import re
import shutil
import time
from pathlib import Path
from playwright.async_api import async_playwright

from config import (
    USERNAME,
    SESSION_DIR,
    COOKIES_FILE,
    LINKS_TXT,
    LINKS_JSONL,
    EXTRA_COLLECTIONS,
    SCROLL_PAUSE,
    MAX_STALE_SCROLLS,
)

STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = { runtime: {} };
"""

POST_SELECTOR = "a[href*='/p/'], a[href*='/reel/'], a[href*='/reels/']"
COLLECTION_RE = re.compile(r"/saved/[^/]+/\d+/?$")

