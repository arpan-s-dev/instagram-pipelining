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
        "slug": "career-productivity",
        "name": "Career & Productivity",
        "keywords": [
            "productivity", "deep work", "notion", "calendar", "habit", "routine",
            "time management", "pomodoro", "second brain", "job", "interview",
        ],
    },
    {
        "slug": "psychology-hacks",
        "name": "Psychology Hacks",
        "keywords": [
            "psychology", "dopamine", "cognitive", "mindset", "anxiety", "therapy",
            "habit loop", "discipline", "motivation", "stoic", "mental", "emotion",
            "procrastination", "focus",
        ],
    },
    {
        "slug": "philosophy",
        "name": "Philosophy",
        "keywords": [
            "philosophy", "philosopher", "existential", "nihilism", "stoicism",
            "seneca", "marcus aurelius", "nietzsche", "socrates", "meaning",
            "ethics", "wisdom",
        ],
    },
    {
        "slug": "lifehacks",
        "name": "Lifehacks",
        "keywords": [
            "life hack", "lifehack", "tip", "trick", "how to", "hack", "save money",
            "clean", "organize", "cooking", "travel", "shortcut",
        ],
    },
    {
        "slug": "tech-dev",
        "name": "Tech & Dev",
        "keywords": [
            "python", "javascript", "react", "api", "docker", "kubernetes", "aws",
            "linux", "terminal", "debug", "code", "programming", "developer",
            "database", "sql", "typescript", "rust", "java",
        ],
    },
    {
        "slug": "finance-business",
        "name": "Finance & Business",
        "keywords": [
            "money", "invest", "stock", "crypto", "startup", "business", "revenue",
            "marketing", "sales", "entrepreneur", "budget", "finance",
        ],
    },
    {
        "slug": "health-fitness",
        "name": "Health & Fitness",
        "keywords": [
            "workout", "gym", "fitness", "health", "sleep", "nutrition", "protein",
            "meditation", "yoga", "run", "lift",
        ],
    },
    {
        "slug": "events-deadlines",
        "name": "Events & Deadlines",
        "keywords": [
            "event", "deadline", "hackathon", "conference", "webinar",
            "workshop", "meetup", "apply by", "closing date", "rsvp",
            "career fair", "office hours",
        ],
    },
    {
        "slug": "news-updates",
        "name": "News & Updates",
        "keywords": [
            "update", "announcement", "launch", "release", "new feature",
            "changelog", "breaking", "now available", "just dropped",
        ],
    },
    {
        "slug": "creativity-design",
        "name": "Creativity & Design",
        "keywords": [
            "design", "figma", "ui", "ux", "creative", "art", "video edit",
            "photography", "canva", "aesthetic",
        ],
    },
    {
        "slug": "other",
        "name": "Other / Uncategorized",
        "keywords": [],  # catch-all when nothing else scores
    },
]

MIN_CLASSIFY_SCORE = 1   # minimum keyword hits to assign (else → other)
