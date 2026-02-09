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

