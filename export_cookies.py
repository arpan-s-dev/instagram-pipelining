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

