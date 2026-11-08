#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Assemble the Terralum game pack from GemRB's redistributable demo data."""

import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "demo"
PROJECT = ROOT / "terralum"
OUTPUT = PROJECT / "build" / "game"
AREA_IMAGE = PROJECT / "art" / "observatory_courtyard.png"
STORY_KEYS = (
    "title", "hero_default_name", "opening", "first_objective",
    "discovery", "second_objective", "arrival", "study_label", "descend_label",
)


def read_story():
    story = json.loads((PROJECT / "story.json").read_text(encoding="utf-8"))
    for key in STORY_KEYS:
        if not isinstance(story.get(key), str) or not story[key].strip():
            raise ValueError(f"story.json: {key} must be nonempty text")
    return story


def write_tis(image_path, reference_path, target_path):
    """Replace the 25x18 paletted tiles while preserving the demo WED layout."""
    with reference_path.open("rb") as source:
        header = source.read(24)
    signature, count, record_size, offset, tile_size = struct.unpack("<8s4I", header)
    if (signature, count, record_size, offset, tile_size) != (b"TIS V1  ", 450, 5120, 24, 64):
        raise ValueError("The demo AR0100 tileset layout changed")

    with Image.open(image_path) as original:
        image = original.convert("RGB")
    # Center crop preserves the image's proportions before fitting the demo area.
    desired_ratio = 25 / 18
    width, height = image.size
    if width / height > desired_ratio:
        new_width = round(height * desired_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = round(width / desired_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    image = image.resize((1600, 1152), Image.Resampling.LANCZOS)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("wb") as output:
        output.write(header)
        for tile_y in range(18):
            for tile_x in range(25):
                tile = image.crop((tile_x * 64, tile_y * 64, (tile_x + 1) * 64, (tile_y + 1) * 64))
                indexed = tile.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                rgb = indexed.getpalette()[:768]
                # GemRB reads BGRA palette entries; the fourth byte is unused.
                palette = bytearray()
                for index in range(256):
                    red, green, blue = rgb[index * 3:index * 3 + 3]
                    palette.extend((blue, green, red, 0))
                output.write(palette)
                output.write(indexed.tobytes())
    return image


def build():
    story = read_story()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SOURCE, OUTPUT)
    image = write_tis(AREA_IMAGE, SOURCE / "override" / "ar0100.tis", OUTPUT / "override" / "ar0100.tis")
    image.save(OUTPUT / "override" / "ar0100.png")

    gemrb_ini = OUTPUT / "override" / "gemrb.ini"
    ini_text = gemrb_ini.read_text(encoding="utf-8")
    gemrb_ini.write_text(ini_text.replace("WindowTitle = GemRB demo", f"WindowTitle = {story['title']}"), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_key_file.py"), str(OUTPUT)],
        check=True, capture_output=True, text=True,
    )
    def config_text(path_formatter):
        return (
            f"GameType = terralum\nGamePath = {path_formatter(OUTPUT)}\n"
            f"GemRBPath = {path_formatter(ROOT / 'gemrb')}\n"
            f"PluginsPath = {path_formatter(ROOT / 'build' / 'gemrb' / 'plugins')}\n"
            "Width = 1280\nHeight = 800\nSkipIntroVideos = 0\n"
        )

    config = PROJECT / "build" / "terralum.cfg"
    config.write_text(config_text(lambda path: path.as_posix()), encoding="utf-8")
    wsl_config = None
    if re.match(r"^[A-Za-z]:", str(ROOT)):
        def wsl_path(path):
            posix = path.as_posix()
            return f"/mnt/{posix[0].lower()}/{posix[3:]}"
        wsl_config = PROJECT / "build" / "terralum-wsl.cfg"
        wsl_config.write_text(config_text(wsl_path), encoding="utf-8")
    return {
        "game_path": str(OUTPUT), "config_path": str(config),
        "wsl_config_path": str(wsl_config) if wsl_config else None, "tiles": 450,
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
