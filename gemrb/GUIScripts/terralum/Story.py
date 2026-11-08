# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Story text lives in terralum/story.json so authoring tools can edit it safely."""

import json
from pathlib import Path


STORY_FILE = Path(__file__).resolve().parents[3] / "terralum" / "story.json"


def get(key):
	with STORY_FILE.open(encoding="utf-8") as source:
		return json.load(source)[key]
