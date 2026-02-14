"""
Stage 3 — Transcript + OCR for reels; OCR for photos.

Videos: ffmpeg audio → faster-whisper → frame OCR → notes/<id>.md
Photos:  OCR (+ caption from .info.json) → notes/<id>.md

Run:  python 3_process.py

Env:  WHISPER_DEVICE=cpu   TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytesseract
from PIL import Image

from config import MEDIA_DIR, NOTES_DIR

NUM_FRAMES = 4
MODEL_SIZE = "small"
DEVICE = os.environ.get("WHISPER_DEVICE", "cuda")
COMPUTE = os.environ.get("WHISPER_COMPUTE", "float16" if DEVICE == "cuda" else "int8")
VIDEO_EXTS = {".mp4", ".mov", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

TESSERACT_CMD = os.environ.get("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _smoke_test(model) -> None:
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "test.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
             "-t", "0.5", str(wav)],
            check=True, capture_output=True,
        )
        list(model.transcribe(str(wav), beam_size=1))


def load_model():
    global DEVICE, COMPUTE
    from faster_whisper import WhisperModel

    try:
        m = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE)
        _smoke_test(m)
        print(f"Whisper '{MODEL_SIZE}' on {DEVICE} ({COMPUTE}).")
        return m
    except Exception as e:
        print(f"GPU failed ({e}); falling back to CPU.")
        DEVICE, COMPUTE = "cpu", "int8"
        m = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        print(f"Whisper '{MODEL_SIZE}' on CPU (int8).")
        return m


def extract_audio(video: Path, out_wav: Path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(out_wav)],
        check=True, capture_output=True,
    )


def transcribe(model, wav: Path) -> str:
    segments, _ = model.transcribe(str(wav), beam_size=5)
    return " ".join(seg.text.strip() for seg in segments).strip()


def sample_frames(video: Path, tmpdir: Path, n: int):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True,
    )
    try:
        dur = float(probe.stdout.strip())
    except ValueError:
        dur = 10.0
    frames = []
    for i in range(n):
        t = dur * (i + 1) / (n + 1)
        fp = tmpdir / f"frame_{i}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", str(video),
             "-frames:v", "1", "-q:v", "3", str(fp)],
            check=True, capture_output=True,
        )
        if fp.exists():
            frames.append(fp)
    return frames


def ocr_image(path: Path) -> str:
    try:
        return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception:
        return ""


def ocr_frames(frames) -> str:
    seen = []
    for fp in frames:
        for line in ocr_image(fp).splitlines():
            line = line.strip()
            if len(line) >= 3 and line not in seen:
                seen.append(line)
    return "\n".join(seen)


def get_meta(media: Path) -> tuple[str, str]:
    """Return (caption, source_url)."""
    info = media.with_suffix(".info.json")
    caption, source = "", ""
    if info.exists():
        try:
            data = json.loads(info.read_text(encoding="utf-8"))
            caption = data.get("description") or data.get("title") or ""
            source = data.get("webpage_url") or data.get("url") or ""
        except Exception:
            pass
    if not source:
        stem = media.stem
        source = f"https://www.instagram.com/p/{stem}/"
    return caption, source


def media_kind(path: Path) -> str:
    return "video" if path.suffix.lower() in VIDEO_EXTS else "image"


def write_note(note_path: Path, media_id: str, kind: str, source: str,
               caption: str, transcript: str, onscreen: str):
    title = "Reel" if kind == "video" else "Photo"
    note = (
        f"# {title} {media_id}\n\n"
        f"kind: {kind}\n"
        f"source: {source}\n\n"
        f"## Caption\n{caption or '(none)'}\n\n"
        f"## Transcript\n{transcript or '(none)'}\n\n"
        f"## On-screen text (OCR)\n{onscreen or '(none)'}\n"
    )
    note_path.write_text(note, encoding="utf-8")


def main():
    NOTES_DIR.mkdir(exist_ok=True)
    all_media = sorted(
        p for p in MEDIA_DIR.iterdir()
        if p.suffix.lower() in VIDEO_EXTS | IMAGE_EXTS
    )
    if not all_media:
        print(f"No media in {MEDIA_DIR}. Run 2_download.py first.")
        return

    videos = [p for p in all_media if media_kind(p) == "video"]
    images = [p for p in all_media if media_kind(p) == "image"]
    print(f"Found {len(videos)} videos, {len(images)} images.\n")

    model = load_model() if videos else None

    for media in all_media:
        note_path = NOTES_DIR / f"{media.stem}.md"
        if note_path.exists():
            print(f"skip: {media.name}")
            continue

        kind = media_kind(media)
        print(f"processing ({kind}): {media.name}")
        try:
            caption, source = get_meta(media)
            transcript = "(none)"
            onscreen = "(none)"

            if kind == "video":
                with tempfile.TemporaryDirectory() as td:
                    td = Path(td)
                    wav = td / "audio.wav"
                    extract_audio(media, wav)
                    transcript = transcribe(model, wav) or "(none)"
                    frames = sample_frames(media, td, NUM_FRAMES)
                    onscreen = ocr_frames(frames) or "(none)"
            else:
                onscreen = ocr_image(media) or "(none)"

            write_note(note_path, media.stem, kind, source, caption, transcript, onscreen)
            print(f"   -> {note_path}")
        except Exception as e:
            print(f"   !! failed: {e}")

    print(f"\nDone. Notes in {NOTES_DIR.resolve()}")
    print("Next: python 4_classify.py")  # category bundles


if __name__ == "__main__":
    main()
