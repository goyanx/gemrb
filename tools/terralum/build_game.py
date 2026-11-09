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
CAST_FILE = PROJECT / "scene_cast.json"
AREA_IMAGE = PROJECT / "art" / "observatory_courtyard.png"
AREAS = {
    "tl0001": "alsperia_market.png",
    "tl0002": "mistwood_road.png",
    "tl0003": "lorian_cavern.png",
    "tl0004": "alsperia_court.png",
    "tl0005": "tear_vault.png",
    "tl0006": "deep_archives.png",
    "tl0007": "alsperia_skyport.png",
}


def read_story():
    story = json.loads((PROJECT / "story.json").read_text(encoding="utf-8"))
    for key in ("title", "hero_default_name"):
        if not isinstance(story.get(key), str) or not story[key].strip():
            raise ValueError(f"story.json: {key} must be nonempty text")
    chapters = story.get("chapters", [])
    if len(chapters) != 7:
        raise ValueError("story.json must define seven chapters")
    for chapter in chapters:
        if chapter.get("area") not in AREAS or not chapter.get("beats"):
            raise ValueError("each chapter needs a built area and story beats")
        if not all(beat.get("speaker") and beat.get("text") and beat.get("action") for beat in chapter["beats"]):
            raise ValueError("each story beat needs a speaker, text, and action")
    cast = json.loads(CAST_FILE.read_text(encoding="utf-8"))
    for area in AREAS:
        people = cast.get(area, [])
        if len(people) < 2:
            raise ValueError(f"scene cast for {area} must contain at least two NPCs")
        for person in people:
            if not person.get("name") or not person.get("line") or person.get("creature") not in ("protagon", "riddler"):
                raise ValueError(f"scene cast for {area} has an incomplete NPC")
            if len(person.get("position", [])) != 2 or any(not isinstance(value, int) for value in person["position"]):
                raise ValueError(f"scene cast position for {area} must contain two integer coordinates")
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

    # Keep the demo's walkmesh and entrances until Terralum has authored area
    # geometry. Remove its actors and interactive tutorial objects.
    for area, image_name in AREAS.items():
        upper = area.upper().encode("ascii")
        for suffix in (".are", ".WED", ".mos", "LM.BMP", "SR.BMP", "HT.BMP", "TMP.BMP"):
            source_name = "ar0100" + suffix if suffix in (".are", ".mos") else "AR0100" + suffix
            data = (SOURCE / "override" / source_name).read_bytes()
            if suffix in (".are", ".WED"):
                data = data.replace(b"AR0100", upper)
            if suffix == ".are":
                data = bytearray(data)
                struct.pack_into("<H", data, 0x58, 0)  # actor count
                struct.pack_into("<H", data, 0x5A, 0)  # region count
                struct.pack_into("<I", data, 0x64, 0)  # spawn count
                struct.pack_into("<H", data, 0x74, 0)  # container count
                struct.pack_into("<H", data, 0x76, 0)  # item count
                struct.pack_into("<I", data, 0xA4, 0)  # door count
                song_offset = struct.unpack_from("<I", data, 0xBC)[0]
                song_index = {"tl0001": 1, "tl0002": 3, "tl0003": 2,
                              "tl0004": 1, "tl0005": 2, "tl0006": 2,
                              "tl0007": 1}[area]
                struct.pack_into("<II", data, song_offset, song_index, song_index)
            target_name = area + suffix if suffix in (".are", ".mos") else area.upper() + suffix
            (OUTPUT / "override" / target_name).write_bytes(data)
        write_tis(PROJECT / "art" / image_name, SOURCE / "override" / "ar0100.tis", OUTPUT / "override" / (area + ".tis"))

    game = OUTPUT / "override" / "gem-demo.gam"
    game.write_bytes(game.read_bytes().replace(b"AR0100", b"TL0001"))
    for table in ("startare.2da", "mastarea.2da"):
        path = OUTPUT / "override" / table
        path.write_text(path.read_text(encoding="ascii").replace("AR0100", "TL0001"), encoding="ascii")
    startpos = OUTPUT / "override" / "startpos.2da"
    startpos.write_text(startpos.read_text(encoding="ascii").replace("1409    585", "800     585").replace("1035    917", "600     917"), encoding="ascii")
    songs = OUTPUT / "override" / "songlist.2da"
    songs.write_text(songs.read_text(encoding="ascii").replace("mx0100.mus", "tlcity.mus").replace("mx0110.mus", "tlcave.mus")
                     + "3       mistwood        tlwood.mus\n", encoding="ascii")
    actions = OUTPUT / "override" / "action.ids"
    actions.write_text(actions.read_text(encoding="ascii") + "\n3 Attack(O:Target*)\n", encoding="ascii")
    for sound in (PROJECT / "audio").glob("tln*.ogg"):
        shutil.copy2(sound, OUTPUT / "override" / sound.name)
    for music in (PROJECT / "audio" / "music").rglob("*"):
        if music.is_file():
            destination = OUTPUT / "music" / music.relative_to(PROJECT / "audio" / "music")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(music, destination)

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
        "areas": list(AREAS), "chapters": len(story["chapters"]),
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
