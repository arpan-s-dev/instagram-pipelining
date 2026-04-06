# Instagram Pipelining

Turn **your own saved Instagram Reels and posts** into a local, searchable knowledge base.

Saved content is easy to forget. This pipeline harvests those saves, downloads the media, extracts captions / speech / on-screen text, then groups items so you can:

- find **useful events and deadlines** buried in Reels
- **track updates** (launches, internships, tools, repos)
- search hacks later instead of scrolling Saved again

Everything stays on your machine. Nothing is uploaded.

---

## What it does

```
Instagram Saved  →  links  →  videos/photos  →  notes  →  labeled bundles
     (you)           harvest      yt-dlp         whisper+OCR     keywords
```

| Stage | Script | Output |
|-------|--------|--------|
| 1. Harvest | `1_harvest_links.py` | `links.txt` + `links.jsonl` |
| 2. Download | `2_download.py` | `videos/` (`.mp4` / images + `.info.json`) |
| 3. Process | `3_process.py` | `notes/<id>.md` (caption + transcript + OCR) |
| 4. Classify | `4_classify.py` | `labels.jsonl` + `bundles_by_category/` |
| Optional | `bundle_for_claude.py` | flat batches in `bundles/` |

Paste a category bundle into Claude (or any chat) to summarize, extract event dates, or build a tracker.

