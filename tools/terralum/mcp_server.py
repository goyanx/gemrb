#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Small stdio MCP authoring server for the Terralum game pack."""

import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

from build_game import AREAS, CAST_FILE, PROJECT, build, read_cast, read_story, validate_cast, validate_npc


STORY_PATH = PROJECT / "story.json"
SETUP_PATH = PROJECT.parent / "gemrb" / "GUIScripts" / "terralum" / "SetupGame.py"
STANDARD_PATH = PROJECT / "GOLD_STANDARD_GAME_DESIGN_PIPELINE.md"
NPC_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 120},
        "role": {"type": "string", "minLength": 1, "maxLength": 300},
        "goal": {"type": "string", "minLength": 1, "maxLength": 1000},
        "knowledge": {"type": "string", "minLength": 1, "maxLength": 1000},
        "voice": {"type": "string", "minLength": 1, "maxLength": 500},
        "provenance": {"type": "string", "enum": ["canon", "user-confirmed", "adaptation", "unresolved"]},
        "creature": {"type": "string", "enum": ["protagon", "riddler"]},
        "position": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 32767},
                      "minItems": 2, "maxItems": 2},
        "line": {"type": "string", "minLength": 1, "maxLength": 2000},
        "choices": {"type": "array", "maxItems": 3, "items": {
            "type": "object", "properties": {
                "label": {"type": "string", "minLength": 1, "maxLength": 200},
                "reply": {"type": "string", "minLength": 1, "maxLength": 2000},
                "flag": {"type": "string", "pattern": "^TL[A-Z][A-Z0-9_]{1,28}$"},
                "value": {"type": "integer"},
            }, "required": ["label", "reply", "flag", "value"], "additionalProperties": False,
        }},
        "responses": {"type": "array", "maxItems": 24, "items": {
            "type": "object", "properties": {
                "flag": {"type": "string", "pattern": "^TL[A-Z][A-Z0-9_]{1,28}$"},
                "value": {"type": "integer"},
                "line": {"type": "string", "minLength": 1, "maxLength": 2000},
            }, "required": ["flag", "value", "line"], "additionalProperties": False,
        }},
    },
    "required": ["name", "role", "goal", "knowledge", "voice", "provenance", "creature", "position", "line"],
    "additionalProperties": False,
}
TOOLS = [
    {
        "name": "terralum_get_design_standard",
        "description": "Read the Terralum gold-standard design and production baseline before authoring game content.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "terralum_get_project",
        "description": "Inspect Terralum's chapters, locations, and generated game pack.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "terralum_get_scene_cast",
        "description": "Read the named NPC cast and dialogue authored for one Terralum scene area.",
        "inputSchema": {"type": "object", "properties": {
            "area": {"type": "string", "enum": list(AREAS)},
        }, "required": ["area"], "additionalProperties": False},
    },
    {
        "name": "terralum_upsert_scene_npc",
        "description": "Add a scene NPC, or replace an NPC at its zero-based scene-cast index. Include the design-standard role, goal, knowledge, voice, and provenance along with in-game actor and dialogue data.",
        "inputSchema": {"type": "object", "properties": {
            "area": {"type": "string", "enum": list(AREAS)},
            "npc": NPC_INPUT_SCHEMA,
            "npc_index": {"type": "integer", "minimum": 0,
                         "description": "Omit to append a new NPC; provide an existing zero-based index to replace that entry."},
        }, "required": ["area", "npc"], "additionalProperties": False},
    },
    {
        "name": "terralum_register_campaign_flag",
        "description": "Initialize a new Terralum campaign flag to zero at game start so authored NPC choices and scene routes can safely use it.",
        "inputSchema": {"type": "object", "properties": {
            "flag": {"type": "string", "pattern": "^TL[A-Z][A-Z0-9_]{1,28}$"},
        }, "required": ["flag"], "additionalProperties": False},
    },
    {
        "name": "terralum_set_journal_event",
        "description": "Attach a persistent journal entry to a scene beat. Register its campaign flag first; section 1 is an active quest, 2 is a resolved quest, and 4 is the journal timeline.",
        "inputSchema": {"type": "object", "properties": {
            "chapter": {"type": "integer", "minimum": 1, "maximum": 15,
                         "description": "One-based scene index in story.json."},
            "beat": {"type": "integer", "minimum": 1},
            "flag": {"type": "string", "pattern": "^TL[A-Z][A-Z0-9_]{1,28}$"},
            "text": {"type": "string", "minLength": 1, "maxLength": 2000},
            "section": {"type": "integer", "enum": [1, 2, 4]},
        }, "required": ["chapter", "beat", "flag", "text", "section"], "additionalProperties": False},
    },
    {
        "name": "terralum_update_story",
        "description": "Update the campaign title or default hero name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "field": {"type": "string", "enum": ["title", "hero_default_name"]},
                "text": {"type": "string", "minLength": 1, "maxLength": 2000},
            },
            "required": ["field", "text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "terralum_update_beat",
        "description": "Edit a speaker, dialogue line, or action in one chapter beat.",
        "inputSchema": {
            "type": "object",
            "properties": {
              "chapter": {"type": "integer", "minimum": 1, "maximum": 15,
                            "description": "One-based scene index in story.json."},
                "beat": {"type": "integer", "minimum": 1},
                "field": {"type": "string", "enum": ["speaker", "text", "action"]},
                "text": {"type": "string", "minLength": 1, "maxLength": 2000},
            },
            "required": ["chapter", "beat", "field", "text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "terralum_import_area_art",
        "description": "Import a generated PNG for one of the built Terralum scene areas.",
        "inputSchema": {
            "type": "object",
            "properties": {"source_path": {"type": "string", "minLength": 1},
                           "area": {"type": "string", "enum": list(AREAS)}},
            "required": ["source_path", "area"],
            "additionalProperties": False,
        },
    },
    {
        "name": "terralum_build_game",
        "description": "Build the Terralum game pack and GemRB config from source artwork and story.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def result(value):
    return {"content": [{"type": "text", "text": json.dumps(value, indent=2, ensure_ascii=False)}]}


def call_tool(name, arguments):
    if name == "terralum_get_design_standard":
        return result({"path": str(STANDARD_PATH), "markdown": STANDARD_PATH.read_text(encoding="utf-8")})
    if name == "terralum_get_project":
        return result({
            "story": read_story(),
            "areas": {area: str(PROJECT / "art" / image) for area, image in AREAS.items()},
            "game_built": (PROJECT / "build" / "game" / "chitin.key").is_file(),
        })
    if name == "terralum_get_scene_cast":
        area = arguments.get("area")
        if area not in AREAS:
            raise ValueError("Unknown area")
        return result({"area": area, "npcs": read_cast()[area]})
    if name == "terralum_upsert_scene_npc":
        area = arguments.get("area")
        npc = arguments.get("npc")
        npc_index = arguments.get("npc_index")
        if area not in AREAS:
            raise ValueError("Unknown area")
        if npc_index is not None and (type(npc_index) is not int or npc_index < 0):
            raise ValueError("npc_index must be a nonnegative zero-based index")
        validate_npc(npc, area, require_design=True)
        setup = SETUP_PATH.read_text(encoding="utf-8")
        registered_flags = set(re.findall(r'GemRB\.SetGlobal\("(TL[A-Z0-9_]+)", "GLOBAL", 0\)', setup))
        npc_flags = {entry["flag"] for field in ("choices", "responses")
                     for entry in npc.get(field, [])}
        if missing_flags := npc_flags - registered_flags:
            missing = ", ".join(sorted(missing_flags))
            raise ValueError(f"register campaign flags before using them in scene dialogue: {missing}")
        cast = read_cast()
        candidate = dict(npc)
        for key in ("name", "role", "goal", "knowledge", "voice", "line"):
            candidate[key] = candidate[key].strip()
        if npc_index is None:
            if any(person["name"].casefold() == candidate["name"].casefold() for person in cast[area]):
                raise ValueError("NPC name already exists in this area; provide its npc_index to replace it")
            cast[area] = [*cast[area], candidate]
        else:
            if npc_index >= len(cast[area]):
                raise ValueError("npc_index is outside this scene cast")
            if any(index != npc_index and person["name"].casefold() == candidate["name"].casefold()
                   for index, person in enumerate(cast[area])):
                raise ValueError("NPC name already exists at another index in this area")
            cast[area][npc_index] = candidate
        validate_cast(cast)
        temporary = CAST_FILE.with_suffix(CAST_FILE.suffix + ".tmp")
        temporary.write_text(json.dumps(cast, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(CAST_FILE)
        return result({"area": area, "npc_index": cast[area].index(candidate), "npc": candidate})
    if name == "terralum_register_campaign_flag":
        flag = arguments.get("flag")
        if not isinstance(flag, str) or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", flag):
            raise ValueError("flag must begin with TL and use uppercase letters, digits, or underscores")
        setup = SETUP_PATH.read_text(encoding="utf-8")
        declaration = f'GemRB.SetGlobal("{flag}", "GLOBAL", 0)'
        if declaration in setup:
            return result({"flag": flag, "registered": False, "already_initialized": True})
        anchor = "\tGemRB.EnterGame()"
        if anchor not in setup:
            raise ValueError("could not find the game-start initialization point in SetupGame.py")
        SETUP_PATH.write_text(setup.replace(anchor, f"\t{declaration}\n{anchor}", 1), encoding="utf-8")
        return result({"flag": flag, "registered": True, "initial_value": 0})
    if name == "terralum_set_journal_event":
        chapter_index = arguments.get("chapter")
        beat_index = arguments.get("beat")
        flag = arguments.get("flag")
        text = arguments.get("text")
        section = arguments.get("section")
        story = read_story()
        if (type(chapter_index) is not int or not 1 <= chapter_index <= len(story["chapters"])
                or type(beat_index) is not int
                or not 1 <= beat_index <= len(story["chapters"][chapter_index - 1]["beats"])
                or not isinstance(flag, str) or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", flag)
                or not isinstance(text, str) or not text.strip() or len(text) > 2000
                or type(section) is not int or section not in (1, 2, 4)):
            raise ValueError("Invalid scene beat, campaign flag, journal text, or journal section")
        setup = SETUP_PATH.read_text(encoding="utf-8")
        if f'GemRB.SetGlobal("{flag}", "GLOBAL", 0)' not in setup:
            raise ValueError("register the journal event flag before adding the event")
        for scene_number, scene in enumerate(story["chapters"], start=1):
            for beat_number, beat_data in enumerate(scene["beats"], start=1):
                existing = beat_data.get("journal") or {}
                if (existing.get("flag") == flag
                        and (scene_number != chapter_index or beat_number != beat_index)):
                    raise ValueError("journal event flags must be unique across story beats")
        event = {"flag": flag, "section": section, "text": text.strip()}
        story["chapters"][chapter_index - 1]["beats"][beat_index - 1]["journal"] = event
        temporary = STORY_PATH.with_suffix(STORY_PATH.suffix + ".tmp")
        temporary.write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(STORY_PATH)
        return result({"chapter": chapter_index, "beat": beat_index, "journal": event})
    if name == "terralum_update_story":
        field = arguments.get("field")
        value = arguments.get("text")
        if field not in ("title", "hero_default_name") or not isinstance(value, str) or not value.strip() or len(value) > 2000:
            raise ValueError("Invalid story field or text")
        story = read_story()
        story[field] = value.strip()
        STORY_PATH.write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return result({"updated": field, "text": story[field]})
    if name == "terralum_update_beat":
        chapter = arguments.get("chapter")
        beat = arguments.get("beat")
        field = arguments.get("field")
        value = arguments.get("text")
        story = read_story()
        if (type(chapter) is not int or not 1 <= chapter <= len(story["chapters"])
                or type(beat) is not int or not 1 <= beat <= len(story["chapters"][chapter - 1]["beats"])
                or field not in ("speaker", "text", "action")
                or not isinstance(value, str) or not value.strip() or len(value) > 2000):
            raise ValueError("Invalid chapter, beat, field, or text")
        story["chapters"][chapter - 1]["beats"][beat - 1][field] = value.strip()
        STORY_PATH.write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return result({"chapter": chapter, "beat": beat, "updated": field})
    if name == "terralum_build_game":
        return result(build())
    if name == "terralum_import_area_art":
        area = arguments.get("area")
        if area not in AREAS:
            raise ValueError("Unknown area")
        target = PROJECT / "art" / AREAS[area]
        source = Path(arguments.get("source_path", "")).resolve()
        if not source.is_file() or source.suffix.lower() != ".png":
            raise ValueError("source_path must name an existing PNG file")
        with Image.open(source) as image:
            image.verify()
        with Image.open(source) as image:
            if image.width < 640 or image.height < 460:
                raise ValueError("Area art must be at least 640 x 460 pixels")
            dimensions = [image.width, image.height]
        if source != target.resolve():
            shutil.copy2(source, target)
        return result({"area": area, "area_image": str(target), "dimensions": dimensions})
    raise ValueError(f"Unknown tool: {name}")


def handle(message):
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        payload = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "terralum-authoring", "version": "0.2.0"},
        }
    elif method == "tools/list":
        payload = {"tools": TOOLS}
    elif method == "tools/call":
        params = message.get("params") or {}
        payload = call_tool(params.get("name"), params.get("arguments") or {})
    elif method == "ping":
        payload = {}
    elif method and method.startswith("notifications/"):
        return None
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id, "result": payload}


def main():
    for line in sys.stdin:
        message = None
        try:
            message = json.loads(line)
            response = handle(message)
        except Exception as error:
            response = {
                "jsonrpc": "2.0",
                "id": message.get("id") if isinstance(message, dict) else None,
                "error": {"code": -32000, "message": str(error)},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
