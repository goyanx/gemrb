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
SETUP_FILE = ROOT / "gemrb" / "GUIScripts" / "terralum" / "SetupGame.py"
AREAS = {
    "tl0001": "alsperia_market.png",
    "tl0008": "deep_archives.png",
    "tl0015": "mistwood_hunters_camp.png",
    "tl0002": "mistwood_road.png",
    "tl0009": "mistwood_ruins.png",
    "tl0003": "lorian_cavern.png",
    "tl0010": "byzantem_arch.png",
    "tl0004": "alsperia_court.png",
    "tl0011": "council_chamber.png",
    "tl0005": "tear_vault.png",
    "tl0012": "observatory_courtyard.png",
    "tl0006": "deep_archives.png",
    "tl0013": "archive_index_hall.png",
    "tl0007": "alsperia_skyport.png",
    "tl0014": "aethercraft_hangar.png",
}
AREA_SONG_INDEX = {
    "tl0001": 1, "tl0002": 3, "tl0003": 2, "tl0004": 1,
    "tl0005": 2, "tl0006": 2, "tl0007": 1, "tl0008": 1,
    "tl0009": 3, "tl0010": 2, "tl0011": 1, "tl0012": 2,
    "tl0013": 2, "tl0014": 1, "tl0015": 3,
}


def read_story():
    story = json.loads((PROJECT / "story.json").read_text(encoding="utf-8"))
    for key in ("title", "hero_default_name"):
        if not isinstance(story.get(key), str) or not story[key].strip():
            raise ValueError(f"story.json: {key} must be nonempty text")
    chapters = story.get("chapters", [])
    if len(chapters) != len(AREAS):
        raise ValueError(f"story.json must define one scene for each of the {len(AREAS)} built areas")
    scene_areas = [chapter.get("area") for chapter in chapters]
    if len(scene_areas) != len(set(scene_areas)) or set(scene_areas) != set(AREAS):
        raise ValueError("story.json must define each built area exactly once")
    journal_flags = set()
    setup_text = SETUP_FILE.read_text(encoding="utf-8")
    initialized_flags = set(re.findall(r'GemRB\.SetGlobal\("(TL[A-Z0-9_]+)", "GLOBAL", 0\)', setup_text))
    for chapter in chapters:
        if (chapter.get("area") not in AREAS or not chapter.get("beats")
                or type(chapter.get("act")) is not int or not 1 <= chapter["act"] <= 7):
            raise ValueError("each chapter needs a built area and story beats")
        if not all(beat.get("speaker") and beat.get("text") and beat.get("action") for beat in chapter["beats"]):
            raise ValueError("each story beat needs a speaker, text, and action")
        for beat in chapter["beats"]:
            event = beat.get("journal")
            if event is None:
                continue
            if (not isinstance(event, dict) or not isinstance(event.get("flag"), str)
                    or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", event["flag"])
                    or not isinstance(event.get("text"), str) or not event["text"].strip()
                    or len(event["text"]) > 2000 or type(event.get("section")) is not int
                    or event["section"] not in (1, 2, 4)):
                raise ValueError("journal events need a unique TL flag, text, and section 1, 2, or 4")
            if event["flag"] in journal_flags:
                raise ValueError(f"journal event flag {event['flag']} is used more than once")
            if event["flag"] not in initialized_flags:
                raise ValueError(f"journal event flag {event['flag']} must be initialized in SetupGame.py")
            journal_flags.add(event["flag"])
    read_cast()
    return story


def validate_npc(person, area, require_design=False):
    if not isinstance(person, dict):
        raise ValueError(f"scene cast for {area} contains a non-object NPC")
    limits = {"name": 120, "line": 2000, "role": 300, "faction": 180, "goal": 1000,
              "knowledge": 1000, "voice": 500}
    if (not isinstance(person.get("name"), str) or not person["name"].strip() or len(person["name"]) > 120
            or not isinstance(person.get("line"), str) or not person["line"].strip() or len(person["line"]) > 2000
            or person.get("creature") not in ("protagon", "riddler")):
        raise ValueError(f"scene cast for {area} has an incomplete NPC")
    position = person.get("position")
    if (not isinstance(position, list) or len(position) != 2
            or any(type(value) is not int or not 0 <= value <= 32767 for value in position)):
        raise ValueError(f"scene cast position for {area} must contain two bounded integer coordinates")
    choices = person.get("choices", [])
    if (not isinstance(choices, list) or len(choices) > 3
            or any(not isinstance(choice, dict)
                   or not isinstance(choice.get("label"), str) or not choice["label"].strip() or len(choice["label"]) > 200
                   or not isinstance(choice.get("reply"), str) or not choice["reply"].strip() or len(choice["reply"]) > 2000
                   or not isinstance(choice.get("flag"), str)
                   or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", choice["flag"])
                   or type(choice.get("value")) is not int for choice in choices)):
        raise ValueError(f"scene dialogue choices for {area} must define up to three complete options")
    responses = person.get("responses", [])
    if (not isinstance(responses, list)
            or len(responses) > 24
            or any(not isinstance(response, dict)
                   or not isinstance(response.get("line"), str) or not response["line"].strip()
                   or len(response["line"]) > 2000
                   or not isinstance(response.get("flag"), str)
                   or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", response["flag"])
                   or type(response.get("value")) is not int for response in responses)):
        raise ValueError(f"scene dialogue responses for {area} must define a flag, value, and line")
    route_lines = person.get("route_lines", {})
    if not isinstance(route_lines, dict) or any(not str(key).isdigit() or not isinstance(value, str) or not value.strip()
                                                for key, value in route_lines.items()):
        raise ValueError(f"scene route lines for {area} must map numeric values to text")
    if require_design:
        for field in ("role", "faction", "goal", "knowledge", "voice"):
            if (not isinstance(person.get(field), str) or not person[field].strip()
                    or len(person[field]) > limits[field]):
                raise ValueError(f"NPC cast entry for {area} needs a nonempty {field}")
        if person.get("provenance") not in ("canon", "user-confirmed", "adaptation", "unresolved"):
            raise ValueError(f"NPC cast entry for {area} needs a recognized provenance label")


def validate_cast(cast):
    if not isinstance(cast, dict):
        raise ValueError("scene_cast.json must contain an object keyed by area")
    if set(cast) != set(AREAS):
        raise ValueError("scene_cast.json must define exactly the built scene areas")
    for area in AREAS:
        people = cast.get(area, [])
        if not isinstance(people, list) or len(people) < 2:
            raise ValueError(f"scene cast for {area} must contain at least two NPCs")
        for person in people:
            validate_npc(person, area, require_design=True)
        names = [person["name"].strip().casefold() for person in people]
        if len(names) != len(set(names)):
            raise ValueError(f"scene cast for {area} must contain unique NPC names")
    return cast


def read_cast():
    return validate_cast(json.loads(CAST_FILE.read_text(encoding="utf-8")))


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
                song_index = AREA_SONG_INDEX[area]
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
