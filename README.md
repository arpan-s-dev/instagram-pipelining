# Instagram Pipelining

Local scripts that pull **your saved Instagram Reels and posts**, then turn them into markdown notes you can search. I use it to find events, internship stuff, and tool links I saved months ago and then forgot about.

Nothing is uploaded. Media and notes stay on disk.

## Pipelining diagram

```mermaid
flowchart LR
    A[Saved Reels / posts] --> B[1 harvest<br/>Playwright]
    B --> C[2 download<br/>yt-dlp]
    C --> D[3 process<br/>Whisper + OCR]
    D --> E[4 classify<br/>keywords]
    E --> F[searchable notes]
```

```mermaid
flowchart LR
    IG[Instagram Saved] -->|Chrome| H[1_harvest_links.py]
    H -->|links.txt| DL[2_download.py]
    DL -->|videos/*.mp4| PR[3_process.py]
    PR -->|notes/*.md| CL[4_classify.py]
    CL --> OUT[bundles_by_category/]
```

## Pipeline


Four numbered scripts, in order. Each writes files the next one reads. Stages 2 and 3 skip work that's already done.

```mermaid
flowchart TB
    subgraph in [your Instagram]
        SAV[Saved all-posts]
        COL[collections: internship, gym, ...]
    end

    subgraph auth [login]
        CK[cookies.txt]
        SES[ig_session/]
    end

    subgraph p1 [1_harvest_links.py]
        H[scroll saved pages]
    end

    subgraph p2 [2_download.py]
        D[download each URL]
    end

    subgraph p3 [3_process.py]
        AV[audio + frames]
        TX[transcript + OCR]
    end

    subgraph p4 [4_classify.py]
        LB[keyword buckets]
    end

    SAV --> H
    COL --> H
    CK -.-> H
    SES -.-> H
    H -->|links.txt<br/>links.jsonl| D
    CK -.-> D
    D -->|videos/id.mp4<br/>videos/id.info.json| AV
    AV --> TX
    TX -->|notes/id.md| LB
    LB --> OUT[labels.jsonl<br/>bundles_by_category/]
```

```powershell
python 1_harvest_links.py
python 2_download.py
python 3_process.py
python 4_classify.py
```

Optional: `python bundle_for_claude.py` — 25 notes per file, no categories.

## Architecture

Offline, single-machine. You run Python scripts; they talk to Instagram only during harvest/download, then everything else is local files.

```mermaid
flowchart TB
    U[you / terminal]

    subgraph machine [this folder]
        subgraph cli [scripts]
            S1[1_harvest_links.py]
            S2[2_download.py]
            S3[3_process.py]
            S4[4_classify.py]
            S5[bundle_for_claude.py]
            EX[export_cookies.py]
        end

        CFG[config.py<br/>USERNAME, CATEGORIES, paths]

        subgraph store [local files — gitignored]
            CK[(cookies.txt)]
            SES[(ig_session/)]
            L[(links.txt + links.jsonl)]
            V[(videos/*.mp4 + .info.json)]
            N[(notes/*.md)]
            LAB[(labels.jsonl)]
            BC[(bundles_by_category/)]
            BN[(bundles/)]
        end
    end

    subgraph external [outside]
        IG[instagram.com]
        CH[Chrome]
    end

    U --> S1
    U --> S2
    U --> S3
    U --> S4
    U --> S5
    CFG --> S1
    CFG --> S2
    CFG --> S3
    CFG --> S4
    CFG --> S5

    S1 <--> CH
    CH <--> IG
    CK --> S1
    SES --> S1
    S1 --> L
    EX --> CK

    L --> S2
    CK --> S2
    S2 <--> IG
    S2 --> V

    V --> S3
    S3 --> N

    N --> S4
    L -.-> S4
    S4 --> LAB
    S4 --> BC
    N --> S5
    S5 --> BN
```

**Layers**

```mermaid
flowchart LR
    subgraph L1 [1. Control]
        PY[Python 3.10+]
        CF[config.py]
    end

    subgraph L2 [2. Acquire]
        PW[Playwright]
        CR[Chrome]
        YT[yt-dlp]
    end

    subgraph L3 [3. Extract]
        FF[ffmpeg]
        WH[faster-whisper]
        TES[Tesseract + Pillow]
    end

    subgraph L4 [4. Organize]
        KW[keyword classifier]
        MD[markdown notes / bundles]
    end

    PY --> PW
    CF --> KW
    PW --> CR
    CR --> YT
    YT --> FF
    FF --> WH
    FF --> TES
    WH --> MD
    TES --> MD
    KW --> MD
```

No API server, no database. `config.py` is the only “settings” file. GPU is optional (Whisper tries CUDA, then CPU).

**Stage 3 (one video):**


```mermaid
flowchart LR
    MP4[id.mp4] -->|ffmpeg -vn| WAV[16kHz wav]
    MP4 -->|ffmpeg -ss| FR[4 frames]
    JSON[id.info.json] -->|caption| MD
    WAV --> WH[Whisper small]
    FR --> OCR[Tesseract]
    WH -->|transcript| MD[notes/id.md]
    OCR -->|on-screen text| MD
```

## Tools

| What | Tool | Where |
|------|------|--------|
| Open Instagram, scroll Saved | Playwright + installed Chrome | `1_harvest_links.py` |
| Stay logged in | `cookies.txt` or `ig_session/` | harvest + download |
| Fetch Reels / photos | yt-dlp | `2_download.py` |
| Pull audio and stills | ffmpeg, ffprobe | `3_process.py` |
| Speech → text | faster-whisper (`small`, CUDA then CPU) | `3_process.py` |
| On-screen text | Tesseract + Pillow | `3_process.py` |
| Buckets (events, internships, …) | keywords in `config.py` | `4_classify.py` |

```mermaid
flowchart LR
    subgraph py [pip]
        P[playwright]
        Y[yt-dlp]
        FW[faster-whisper]
        PT[pytesseract]
        PI[pillow]
    end

    subgraph sys [system]
        CR[Chrome]
        F[ffmpeg]
        TR[Tesseract OCR]
    end

    P --> CR
    Y --> F
    FW --> F
    PT --> TR
    PI --> PT
```

## Setup


Python 3.10+, plus ffmpeg and Tesseract on PATH.

```powershell
pip install -r requirements.txt
playwright install chromium
winget install Gyan.FFmpeg
winget install UB-Mannheim.TesseractOCR
```

```powershell
$env:IG_USERNAME = "your_username"
# if tesseract isn't on PATH:
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Saved / private posts need a logged-in session. Easiest path: export `cookies.txt` from Chrome (Get cookies.txt LOCALLY) while you're logged into Instagram, drop it in this folder. After a Playwright login you can also run `python export_cookies.py`.

## Run

```powershell
python 1_harvest_links.py    # Chrome window; log in if asked
python 2_download.py         # skips files already in videos/
python 3_process.py          # skips notes that already exist
python 4_classify.py         # labels.jsonl + bundles_by_category/
```

`2` and `3` are safe to re-run. Harvest scrolls `/saved/all-posts/` then whatever collections it finds on `/saved/`.

Optional: `python bundle_for_claude.py` dumps notes into 25-item files under `bundles/` if you don't care about categories.

## Files that show up locally

These are gitignored (cookies, URLs, videos, notes):

```
cookies.txt          ig_session/
links.txt            links.jsonl
videos/              notes/
labels.jsonl         bundles/   bundles_by_category/
```

Edit `CATEGORIES` in `config.py` and re-run stage 4 when the buckets are wrong. Keyword matching is crude — internship-related words in particular over-match.

Use this on your own saved content. Instagram will sometimes bounce harvest (login loop) or yt-dlp (deleted post, dead cookies).
