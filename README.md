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

---

## Stack

| Layer | Tech |
|-------|------|
| Browser harvest | Playwright + your installed Chrome |
| Auth | `cookies.txt` or a local `ig_session/` profile |
| Download | yt-dlp |
| Audio / frames | ffmpeg |
| Transcript | faster-whisper (GPU if available, else CPU) |
| On-screen text | Tesseract + Pillow |
| Labels | keyword scoring in `config.py` |

---

## Setup

**Python 3.10+**, plus system tools:

```powershell
pip install -r requirements.txt
playwright install chromium
winget install Gyan.FFmpeg
winget install UB-Mannheim.TesseractOCR
```

Set your Instagram username (no `@`):

```powershell
$env:IG_USERNAME = "your_username"
```

Optional Tesseract path on Windows:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Cookies (needed for saved / private items)

1. Log into Instagram in Chrome.
2. Export cookies with a “Get cookies.txt LOCALLY” extension.
3. Save the file as `cookies.txt` in this folder.

You can also run `python export_cookies.py` after a successful Playwright login to write `cookies.txt` from `ig_session/`.

---

## Run

```powershell
python 1_harvest_links.py    # visible Chrome; log in if asked
python 2_download.py         # skips files already in videos/
python 3_process.py          # skips notes already written
python 4_classify.py
```

Harvest uses `/saved/all-posts/` plus auto-discovered collections. It does **not** need a hardcoded collection list.

Downloads and notes are incremental: re-running skips work that already exists.

