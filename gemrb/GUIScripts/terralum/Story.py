# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Story text lives in terralum/story.json so authoring tools can edit it safely."""

import json
from pathlib import Path


STORY_FILE = Path(__file__).resolve().parents[3] / "terralum" / "story.json"
CAST_FILE = Path(__file__).resolve().parents[3] / "terralum" / "scene_cast.json"
_CAST_CACHE = None


def get(key):
	with STORY_FILE.open(encoding="utf-8") as source:
		return json.load(source)[key]

def chapters():
	return get("chapters")

def cast_catalog():
	global _CAST_CACHE
	if _CAST_CACHE is None:
		with CAST_FILE.open(encoding="utf-8") as source:
			_CAST_CACHE = json.load(source)
	return _CAST_CACHE

def cast(area):
	return cast_catalog()[area.lower()]
