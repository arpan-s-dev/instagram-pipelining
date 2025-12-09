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
    urls = [
        line.strip()
        for line in LINKS_TXT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    valid_urls = [url for url in urls if VALID_URL.match(url)]
    skipped = len(urls) - len(valid_urls)
    print(f"Downloading {len(valid_urls)} valid items...")
    if skipped:
        print(f"Skipping {skipped} malformed link(s).")
    print()

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as tf:
        tf.write("\n".join(valid_urls) + "\n")
        url_file = tf.name

