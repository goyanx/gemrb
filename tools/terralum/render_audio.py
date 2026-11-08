#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Render Terralum narration with a local Kokoro ONNX model and original ambience."""

import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro


PROJECT = Path(__file__).resolve().parents[2] / "terralum"
SAMPLE_RATE = 24000


def encode(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                    "-c:a", "libvorbis", "-q:a", "4", str(target)], check=True)


def make_ambience(target, notes, seed):
    # Slow harmonic pads and filtered wind; 32 seconds loops without a hard edge.
    rng = np.random.default_rng(seed)
    seconds = 32
    frames = SAMPLE_RATE * seconds
    t = np.arange(frames, dtype=np.float32) / SAMPLE_RATE
    music = np.zeros(frames, dtype=np.float32)
    for frequency in notes:
        modulation = 0.5 + 0.5 * np.sin(2 * math.pi * t / seconds)
        music += np.sin(2 * math.pi * frequency * t + 0.16 * np.sin(2 * math.pi * 0.11 * t)) * modulation
        music += 0.25 * np.sin(2 * math.pi * frequency * 2 * t)
    wind = rng.standard_normal(frames).astype(np.float32)
    cumulative = np.cumsum(np.pad(wind, (1800, 0)), dtype=np.float64)
    wind = ((cumulative[1800:] - cumulative[:-1800]) / 1800).astype(np.float32)
    fade = np.sin(math.pi * np.arange(frames, dtype=np.float32) / frames) ** 2
    music = (music / max(1, len(notes)) * 0.10 + wind * 0.07) * fade
    with tempfile.TemporaryDirectory() as temporary:
        wav = Path(temporary) / "ambience.wav"
        sf.write(wav, music, SAMPLE_RATE)
        encode(wav, target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--voices", type=Path, required=True)
    parser.add_argument("--voice", default="af_heart")
    args = parser.parse_args()
    chapters = json.loads((PROJECT / "story.json").read_text(encoding="utf-8"))["chapters"]
    kokoro = Kokoro(str(args.model), str(args.voices))
    for chapter in chapters:
        samples, sample_rate = kokoro.create(chapter["narration"], voice=args.voice, speed=0.97, lang="en-us")
        with tempfile.TemporaryDirectory() as temporary:
            wav = Path(temporary) / "narration.wav"
            sf.write(wav, samples, sample_rate)
            encode(wav, PROJECT / "audio" / (chapter["voice"] + ".ogg"))
        print(chapter["voice"], flush=True)
    for name, notes, seed in (("TLCITY", (110, 164.81, 220), 1),
                              ("TLWOOD", (82.41, 123.47, 164.81), 2),
                              ("TLCAVE", (73.42, 110, 146.83), 3)):
        folder = PROJECT / "audio" / "music" / name
        make_ambience(folder / (name + "A.ogg"), notes, seed)
        (PROJECT / "audio" / "music" / (name.lower() + ".mus")).write_text(
            f"{name}\n1\nA A @TAG end\n", encoding="ascii")
        print(name, flush=True)


if __name__ == "__main__":
    main()
