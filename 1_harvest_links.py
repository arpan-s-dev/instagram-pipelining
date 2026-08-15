"""Harvest saved Instagram posts/reels into links.txt + links.jsonl."""

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
        cookie = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": cpath,
            "secure": secure.upper() == "TRUE",
        }
        if expiry.isdigit() and int(expiry) > 0:
            cookie["expires"] = int(expiry)
        cookies.append(cookie)
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
    if "/accounts/login" in page.url or "accountscenter.meta.com" in page.url:
        return True
    return await page.query_selector("input[name='username']") is not None


async def post_link_count(page) -> int:
    return await page.locator(POST_SELECTOR).count()


async def page_ready(page) -> bool:
    if await needs_login(page):
        return False
    return await post_link_count(page) > 0


async def wait_for_login(page, probe: str, timeout_sec=300):
    if not await page_ready(page):
        print("\nLog in in the browser window. Don't close it.\n")

    start = time.monotonic()
    while not await page_ready(page):
        elapsed = int(time.monotonic() - start)
        if elapsed > timeout_sec:
            raise TimeoutError("Login timed out. Export cookies.txt and re-run.")
        if elapsed % 15 == 0 and elapsed > 0:
            print(f"    waiting for saved posts ({elapsed}s)")
        await asyncio.sleep(2)

    if probe not in page.url:
        await page.goto(probe, wait_until="domcontentloaded", timeout=60000)
        await human_delay(2, 3)
    print(f"Ready — {await post_link_count(page)} posts visible.\n")


async def harvest_page(page, url: str, collection: str) -> list[dict]:
    print(f"\n--- Harvesting: {collection}")
    print(f"    {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await human_delay(3, 5)

    if not await page_ready(page):
        print("Skipping (login required or empty).")
        return []

    found: dict[str, dict] = {}
    stale = 0

    while stale < MAX_STALE_SCROLLS:
        hrefs = await page.eval_on_selector_all(
            POST_SELECTOR,
            "els => els.map(e => e.href)",
        )
        before = len(found)
        for h in hrefs:
            clean = normalize_url(h)
            found[clean] = {
                "url": clean,
                "collection": collection,
                "kind": url_kind(clean),
            }
        gained = len(found) - before
        if gained == 0:
            stale += 1
        else:
            stale = 0
            print(f"    {len(found)} links")

        await page.mouse.wheel(0, random.randint(1500, 2500))
        await human_delay(*SCROLL_PAUSE)

    print(f"--- Done: {len(found)} links from {collection}")
    return list(found.values())


async def discover_collections(page) -> list[tuple[str, str]]:
    index = f"https://www.instagram.com/{USERNAME}/saved/"
    await page.goto(index, wait_until="domcontentloaded", timeout=60000)
    await human_delay(3, 5)

    hrefs = await page.eval_on_selector_all(
        "a[href*='/saved/']",
        "els => els.map(e => e.href)",
    )
    seen = set()
    collections = []
    for h in hrefs:
        clean = h.split("?")[0].rstrip("/")
        if not COLLECTION_RE.search(clean) or clean in seen:
            continue
        seen.add(clean)
        name = collection_name_from_url(clean + "/")
        collections.append((clean + "/", name))

    collections = [(u, n) for u, n in collections if n != "all-posts"]
    print(f"Discovered {len(collections)} collections on /saved/")
    for _, name in collections:
        print(f"    - {name}")
    return collections


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh", action="store_true", help="Delete ig_session/ and start clean")
    args = parser.parse_args()

    if args.fresh and SESSION_DIR.exists():
        shutil.rmtree(SESSION_DIR)
        print(f"Deleted {SESSION_DIR}/\n")

    all_posts_url = f"https://www.instagram.com/{USERNAME}/saved/all-posts/"
    records: dict[str, dict] = {}

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            args=["--disable-blink-features=AutomationControlled"],
        )
        await ctx.add_init_script(STEALTH_INIT)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if COOKIES_FILE.exists():
            cookies = load_cookies_txt(COOKIES_FILE)
            ig = [c for c in cookies if "instagram.com" in c.get("domain", "")]
            await ctx.add_cookies(ig)
            print(f"Loaded {len(ig)} cookies from {COOKIES_FILE}")
            await page.goto(all_posts_url, wait_until="domcontentloaded", timeout=60000)
            await human_delay(3, 5)
            if not await page_ready(page):
                print("cookies.txt invalid — trying manual login.\n")
                await wait_for_login(page, all_posts_url)
            else:
                print("Cookies OK.\n")
        else:
            print("No cookies.txt — log in in the browser.\n")
            await page.goto(all_posts_url, wait_until="domcontentloaded", timeout=60000)
            await wait_for_login(page, all_posts_url)

        for rec in await harvest_page(page, all_posts_url, "all-posts"):
            records[rec["url"]] = rec

        for url, name in await discover_collections(page):
            for rec in await harvest_page(page, url, name):
                if rec["url"] not in records:
                    records[rec["url"]] = rec
                elif records[rec["url"]]["collection"] == "all-posts":
                    records[rec["url"]]["collection"] = name

        for url in EXTRA_COLLECTIONS:
            coll = collection_name_from_url(url)
            for rec in await harvest_page(page, url, coll):
                if rec["url"] not in records:
                    records[rec["url"]] = rec

        await ctx.close()

    sorted_records = sorted(records.values(), key=lambda r: r["url"])
    LINKS_TXT.write_text("\n".join(r["url"] for r in sorted_records), encoding="utf-8")
    with LINKS_JSONL.open("w", encoding="utf-8") as f:
        for rec in sorted_records:
            f.write(json.dumps(rec) + "\n")

    reels = sum(1 for r in sorted_records if r["kind"] == "reel")
    posts = sum(1 for r in sorted_records if r["kind"] == "post")
    print(f"\nWrote {len(sorted_records)} unique links")
    print(f"  reels: {reels}  photos/posts: {posts}")
    print(f"  {LINKS_TXT.resolve()}")
    print(f"  {LINKS_JSONL.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
