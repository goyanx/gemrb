#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Small stdio MCP authoring server for the Terralum game pack."""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

from build_game import AREAS, PROJECT, build, read_story


STORY_PATH = PROJECT / "story.json"
TOOLS = [
    {
        "name": "terralum_get_project",
        "description": "Inspect Terralum's chapters, locations, and generated game pack.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
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
                "chapter": {"type": "integer", "minimum": 1, "maximum": 7},
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
        "description": "Import a generated PNG for one of the seven Terralum areas.",
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
    if name == "terralum_get_project":
        return result({
            "story": read_story(),
            "areas": {area: str(PROJECT / "art" / image) for area, image in AREAS.items()},
            "game_built": (PROJECT / "build" / "game" / "chitin.key").is_file(),
        })
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
            "serverInfo": {"name": "terralum-authoring", "version": "0.1.0"},
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
