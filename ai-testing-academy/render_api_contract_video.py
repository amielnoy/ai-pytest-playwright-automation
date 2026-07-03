#!/usr/bin/env python3
"""Render videos/api-contract-tests.mp4 from the animated HTML explainer + Gemini TTS narration.

Pipeline (audio drives scene timing so voice and visuals stay in sync):
  1. Gemini TTS renders each scene's narration line -> raw PCM -> wav.
  2. Each scene duration = speech length + tail pad.
  3. A single narration track is built (speech + trailing silence per scene, concatenated).
  4. Playwright/Chromium plays the HTML (?rec=1&autoplay=1&dur=...) and records a webm.
  5. ffmpeg muxes the webm video + narration audio into the final mp4.

Run:  .venv/bin/python scripts/render_api_contract_video.py
Needs: GEMINI_API_KEY in .env, ffmpeg/ffprobe on PATH, Playwright Chromium installed.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent          # the ai-testing-academy/ folder
REPO_ROOT = BASE.parent                          # repo root, where .env lives
HTML = BASE / "videos" / "api-contract-tests.html"
OUT = BASE / "videos" / "api-contract-tests.mp4"
BUILD = BASE / "videos" / "_build"

TTS_MODEL = "gemini-2.5-flash-preview-tts"
VOICE = "Charon"           # warm, informative documentary-style voice
STYLE = ("Read aloud in a warm, calm, curious documentary narrator voice, "
         "slightly slower than natural, with thoughtful pauses:\n\n")
TAIL_PAD_S = 0.6           # silence after each line so it doesn't feel rushed
PCM_RATE = 24000           # Gemini TTS returns L16 PCM @ 24 kHz mono

# One narration line per scene, verbatim from api-contract-tests-narration.md (7 scenes).
LINES = [
    "Your UI tests are slow, and they break for reasons that have nothing to do with the "
    "thing you're testing. What if most of them didn't need a browser at all?",
    "Here's the test pyramid. UI tests sit at the top: few, slow, expensive. Underneath them, "
    "API tests. Faster, steadier, and they cover far more of your logic per second.",
    "But there's a rule. Tests never call requests directly. Every call goes through a service "
    "layer, with retries and timeouts, and a service class per endpoint. Change the API in one "
    "place, not in fifty tests.",
    "One test shape, many inputs. Parametrize the query: MacBook, iPhone, Samsung, and one "
    "function becomes a dozen cases. No copy-paste. And no hard-coded status codes: they live "
    "in one constants file.",
    "Now the quiet hero: contract tests. They don't check behavior; they check shape. Is the "
    "status code right? Are the required fields present? Do product IDs and prices actually "
    "parse? Map-driven: one assertion shape across many endpoints.",
    "When the backend changes a field name or drops a value, a contract test fails instantly, "
    "with a clear reason, long before a UI test would flake and leave you guessing.",
    "So push coverage down the pyramid. Let the API layer carry the load, let contracts guard "
    "the shape, and keep the browser for the few flows that truly need it. Fast where it can "
    "be, thorough where it must be.",
]


def load_key() -> str:
    for line in (REPO_ROOT / ".env").read_text().splitlines():
        if line.strip().startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip("\"'")
    sys.exit("GEMINI_API_KEY not found in .env")


def gemini_tts(text: str, key: str) -> bytes:
    """Return raw PCM (s16le, 24 kHz, mono) bytes for `text`."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-goog-api-key": key},
    )
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            return base64.b64decode(b64)
        except Exception as e:  # noqa: BLE001 - retry transient API/network errors
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Gemini TTS failed after retries: {last}")


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main() -> None:
    key = load_key()
    BUILD.mkdir(parents=True, exist_ok=True)

    durations_ms: list[int] = []
    padded_wavs: list[Path] = []

    for i, line in enumerate(LINES):
        print(f"[tts] scene {i + 1}/{len(LINES)} ...", flush=True)
        pcm = gemini_tts(line, key)
        pcm_path = BUILD / f"scene{i}.pcm"
        pcm_path.write_bytes(pcm)

        speech_s = len(pcm) / (2 * PCM_RATE)          # 2 bytes/sample, mono
        scene_s = speech_s + TAIL_PAD_S
        durations_ms.append(round(scene_s * 1000))

        # raw PCM -> wav padded with trailing silence to the full scene length
        padded = BUILD / f"scene{i}.wav"
        ffmpeg("-f", "s16le", "-ar", str(PCM_RATE), "-ac", "1", "-i", str(pcm_path),
               "-af", f"apad=whole_dur={scene_s:.3f}", str(padded))
        padded_wavs.append(padded)

    total_ms = sum(durations_ms)
    print(f"[audio] scene durations (ms): {durations_ms}  total={total_ms}", flush=True)

    # concat all padded scene wavs -> one narration track
    concat_list = BUILD / "concat.txt"
    concat_list.write_text("".join(f"file '{p.name}'\n" for p in padded_wavs))
    voice = BUILD / "voice.m4a"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c:a", "aac", "-b:a", "160k",
           str(voice))

    # record the animation to webm at exact per-scene timing
    dur_param = ",".join(str(d) for d in durations_ms)
    url = f"{HTML.as_uri()}?rec=1&autoplay=1&dur={dur_param}"
    webm = record_webm(url, total_ms)

    # mux video + narration into the final mp4
    print("[mux] encoding mp4 ...", flush=True)
    ffmpeg("-i", str(webm), "-i", str(voice),
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k",
           "-t", f"{total_ms / 1000:.3f}", "-movflags", "+faststart",
           str(OUT))

    # cleanup intermediates
    for p in BUILD.glob("*"):
        p.unlink()
    BUILD.rmdir()
    print(f"[done] wrote {OUT.relative_to(REPO_ROOT)}", flush=True)


def record_webm(url: str, total_ms: int) -> Path:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(BUILD),
            record_video_size={"width": 1280, "height": 720},
        )
        page = ctx.new_page()
        print("[rec] opening explainer ...", flush=True)
        page.goto(url)
        page.wait_for_timeout(total_ms + 900)   # let the whole animation play out
        video_path = page.video.path()
        ctx.close()      # finalizes the webm
        browser.close()
    return Path(video_path)


if __name__ == "__main__":
    main()
