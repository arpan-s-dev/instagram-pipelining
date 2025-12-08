"""
Stage 2 — Download saved reels (.mp4) and photos (.jpg/.webp) + metadata.

Reads links.txt (from stage 1) into ./videos/ (reels and photos together).
Captions saved as .info.json next to each file.

Run:  python 2_download.py
"""

import re
import subprocess
import tempfile
from pathlib import Path

from config import LINKS_TXT, MEDIA_DIR, COOKIES_FILE

VALID_URL = re.compile(r"^https://www\.instagram\.com/(p|reel|reels)/[A-Za-z0-9_-]+/?$")


def main():
    if not LINKS_TXT.exists():
        print(f"No {LINKS_TXT} found. Run 1_harvest_links.py first.")
        return

    MEDIA_DIR.mkdir(exist_ok=True)
