# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Stable, distinct clothing palettes for the authored Terralum NPC cast."""

BASE_PALETTES = (
	(0, 5, 4), (1, 21, 2), (22, 62, 23), (3, 53, 1),
	(44, 74, 25), (5, 45, 50), (26, 26, 36), (7, 37, 67),
	(68, 28, 18), (9, 69, 59), (49, 10, 10), (88, 48, 80),
)


def palettes_by_name(cast_catalog):
	"""Assign a stable palette tuple to every unique NPC name in scene data."""
	names = sorted({person["name"] for people in cast_catalog.values() for person in people})
	if len(names) > 89:
		raise ValueError("GemRB NPC palette assignment supports at most 89 unique colors")

	palettes = list(BASE_PALETTES)
	used_major = {palette[1] for palette in palettes}
	major_colors = [color for color in range(89) if color not in used_major]
	while len(palettes) < len(names):
		index = len(palettes)
		base = BASE_PALETTES[index % len(BASE_PALETTES)]
		major = major_colors[index - len(BASE_PALETTES)]
		minor = BASE_PALETTES[(index * 5 + 3) % len(BASE_PALETTES)][2]
		palettes.append((base[0], major, minor))
	return {name: palettes[index] for index, name in enumerate(names)}
