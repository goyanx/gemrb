#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Validate scene-specific searchmap output and footpath connectivity."""

import importlib.util
import json
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("terralum_build_game", ROOT / "tools" / "terralum" / "build_game.py")
build_game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_game)

searchmap_specs = build_game.read_searchmaps()
terrain = (build_game.SOURCE / "override" / "terrain.2da").read_text(encoding="ascii")
passability_row = terrain.split("PASSABLE", 1)[1].splitlines()[0].split()
assert len(passability_row) == 16
passability = [bool(int(bits) & 1) for bits in passability_row]

expected = {
    "tl0002": {
        "routes": [(84, 7), (44, 92)],
        "blocked": [(8, 40), (27, 82), (72, 82), (92, 42), (54, 25)],
        "description": "ruined watchpost road and southern approach",
    },
    "tl0015": {
        "routes": [(59, 10), (76, 92)],
        "blocked": [(10, 35), (93, 42), (60, 44), (24, 66), (80, 78)],
        "description": "north trail and stepping-stone route",
    },
    "tl0016": {
        "routes": [(24, 5), (95, 27), (72, 92)],
        "blocked": [(5, 45), (56, 20), (90, 76), (30, 88)],
        "description": "north, east, and south trail branches",
    },
}
assert set(searchmap_specs) == set(expected)
cast_by_area = json.loads(build_game.CAST_FILE.read_text(encoding="utf-8"))
story = build_game.read_story()
chapters_by_area = {chapter["area"]: chapter for chapter in story["chapters"]}

for area, map_spec in searchmap_specs.items():
    image = build_game.write_searchmap(build_game.SOURCE / "override" / "AR0100SR.BMP", map_spec)
    assert image.mode == "P"
    assert image.size == (100, 96)

    def walkable(cell):
        x, y = cell
        return 0 <= x < image.width and 0 <= y < image.height and passability[image.getpixel((x, y))]

    # The area is 1600x1152 game pixels, matching 100x96 searchmap cells.
    def to_cell(position):
        return (position[0] * image.width // 1600, position[1] * image.height // 1152)

    start = to_cell((800, 585))
    npcs = [to_cell(person["position"]) for person in cast_by_area[area]]
    encounter_positions = [to_cell(beat["spawn_position"])
                           for beat in chapters_by_area[area]["beats"] if beat.get("spawn_position")]
    targets = [start, *npcs, *encounter_positions, *expected[area]["routes"]]
    assert all(walkable(cell) for cell in targets), f"{area}: start or actor on blocked cell: {targets}"

    # Four-way connectivity is stricter than the engine's diagonal walk options.
    queue = deque([start])
    reachable = {start}
    while queue:
        x, y = queue.popleft()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor not in reachable and walkable(neighbor):
                reachable.add(neighbor)
                queue.append(neighbor)
    assert all(cell in reachable for cell in targets), f"{area}: disconnected route: {targets}"
    assert all(not walkable(cell) for cell in expected[area]["blocked"]), f"{area}: a solid prop became walkable"
    assert len(reachable) > 1000, f"{area}: walkable region is unexpectedly small"
    print(f"{area}: {len(reachable)} cells; start, {len(npcs)} NPCs, {len(encounter_positions)} encounter spawns, and {expected[area]['description']} connected")
    image.close()
