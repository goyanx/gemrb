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
area = "tl0015"
map_spec = searchmap_specs[area]
image = build_game.write_searchmap(build_game.SOURCE / "override" / "AR0100SR.BMP", map_spec)
assert image.mode == "P"
assert image.size == (100, 96)

terrain = (build_game.SOURCE / "override" / "terrain.2da").read_text(encoding="ascii")
passability_row = terrain.split("PASSABLE", 1)[1].splitlines()[0].split()
assert len(passability_row) == 16
passability = [bool(int(bits) & 1) for bits in passability_row]

def walkable(cell):
    x, y = cell
    return 0 <= x < image.width and 0 <= y < image.height and passability[image.getpixel((x, y))]


# The area is 1600x1152 game pixels, matching 100x96 searchmap cells.
def to_cell(position):
    return (position[0] * image.width // 1600, position[1] * image.height // 1152)


start = to_cell((800, 585))
cast = json.loads(build_game.CAST_FILE.read_text(encoding="utf-8"))[area]
npcs = [to_cell(person["position"]) for person in cast]
landmarks = [(59, 10), (76, 92)]  # north trail and stepping-stone approach
targets = [start, *npcs, *landmarks]
assert all(walkable(cell) for cell in targets), f"start or actor on blocked searchmap cell: {targets}"

# Four-way connectivity is stricter than the engine's diagonal walk options and
# therefore rules out movement paths that only touch corners.
queue = deque([start])
reachable = {start}
while queue:
    x, y = queue.popleft()
    for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if neighbor not in reachable and walkable(neighbor):
            reachable.add(neighbor)
            queue.append(neighbor)
assert all(cell in reachable for cell in targets), f"disconnected camp route: {targets}"

blocked_landmarks = [(10, 35), (93, 42), (60, 44), (24, 66), (80, 78)]
assert all(not walkable(cell) for cell in blocked_landmarks), "shelter, cart, firepit, or boulder became walkable"
assert len(reachable) > 1500, "camp clearing and trails are unexpectedly small"
print(f"{area}: {len(reachable)} passable cells; start, {len(npcs)} NPCs, north trail, and stepping-stone route connected")
