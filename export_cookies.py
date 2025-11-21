"""Export Instagram cookies from ig_session to cookies.txt for yt-dlp."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_DIR = Path("ig_session")
OUT = Path("cookies.txt")


def to_netscape(cookies: list[dict]) -> str:
    lines = [
        "# Netscape HTTP Cookie File",
        "# Exported from ig_session for yt-dlp",
        "",
    ]
    for c in cookies:
        domain = c["domain"]
        include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure") else "FALSE"
        expires = c.get("expires", -1)
        expiry = str(int(expires)) if expires and expires > 0 else "0"
        lines.append(
            f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiry}\t{c['name']}\t{c['value']}"
        )
    return "\n".join(lines) + "\n"


async def main():
    if not SESSION_DIR.exists():
        print(f"No {SESSION_DIR}/ — log in via 1_harvest_links.py first.")
        return

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=True,
            channel="chrome",
        )
        all_cookies = await ctx.cookies("https://www.instagram.com")
        await ctx.close()

    ig = [c for c in all_cookies if "instagram.com" in c.get("domain", "")]
    if not ig:
        print("No Instagram cookies found in ig_session.")
        return

    OUT.write_text(to_netscape(ig), encoding="utf-8")
    print(f"Wrote {len(ig)} cookies to {OUT.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
