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


def load_cookies_txt(path: Path) -> list[dict]:
    cookies = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        domain, _, cpath, secure, expiry, name, value = parts
        c: dict = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": cpath,
            "secure": secure.upper() == "TRUE",
        }
        if expiry.isdigit() and int(expiry) > 0:
            c["expires"] = int(expiry)
        cookies.append(c)
    return cookies


def url_kind(url: str) -> str:
    if "/reel/" in url or "/reels/" in url:
        return "reel"
    if "/p/" in url:
        return "post"
    return "unknown"


def collection_name_from_url(url: str) -> str:
    m = re.search(r"/saved/([^/]+)/\d+", url)
    return m.group(1) if m else "unknown"


def normalize_url(href: str) -> str:
    return href.split("?")[0].rstrip("/") + "/"


async def human_delay(a, b):
    await asyncio.sleep(random.uniform(a, b))


async def needs_login(page) -> bool:
    url = page.url
    if "/accounts/login" in url:
        return True
    if "accountscenter.meta.com" in url:
        return True
    return await page.query_selector("input[name='username']") is not None


async def post_link_count(page) -> int:
    return await page.locator(POST_SELECTOR).count()


async def page_ready(page) -> bool:
    if await needs_login(page):
        return False
    return await post_link_count(page) > 0

