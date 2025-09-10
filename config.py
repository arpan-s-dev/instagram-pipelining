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

# --- classify ---
# Each category: slug (folder name), display name, keywords (lowercase).
# Stage 4 scores note text against keywords; best match wins.
# Ties / low scores go to "other". Refine keywords anytime.
CATEGORIES = [
    {
        "slug": "claude-ai-skills",
        "name": "Claude / AI Skills",
        "keywords": [
            "claude", "anthropic", "cursor", "prompt", "mcp", "opus", "sonnet",
            "artifacts", "claude code", "system prompt",
        ],
    },
    {
        "slug": "ai-hacks",
        "name": "AI Hacks",
        "keywords": [
            "chatgpt", "openai", "gemini", "copilot", "llm", "ai tool", "midjourney",
            "stable diffusion", "perplexity", "agent", "rag", "fine-tune", "gpt",
        ],
    },
    {
        "slug": "github-repos",
        "name": "GitHub Repos",
        "keywords": [
            "github", "gitlab", "repository", "repo", "open source", "star this",
            "pull request", "readme", "npm install", "pip install",
        ],
    },
    {
        "slug": "internship-hacks",
        "name": "Internship Hacks",
        "keywords": [
            "internship", "intern", "recruiter", "referral", "leetcode", "oa",
            "online assessment", "resume", "cold email", "linkedin", "handshake",
            "career fair", "new grad", "ng", "faang", "application",
        ],
    },
    {
