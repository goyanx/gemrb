#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later
"""Compile rendered Terralum NPC sprites into GemRB-compatible BAM V1 files."""

import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITE_ROOT = ROOT / "terralum" / "art" / "world_sprites"


def _palette_for(images):
	"""Build one shared 255-color palette; BAM palette index zero is transparent."""
	cropped = []
	for source in images:
		image = source.convert("RGBA")
		bounds = image.getchannel("A").getbbox()
		cropped.append(image.crop(bounds) if bounds else image.crop((0, 0, 1, 1)))
	width = max(image.width for image in cropped)
	combined = Image.new("RGB", (width, sum(image.height for image in cropped)), (0, 0, 0))
	y = 0
	for image in cropped:
		combined.paste(image.convert("RGB"), (0, y), image.getchannel("A"))
		y += image.height
	quantized = combined.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
	flat = quantized.getpalette()[:255 * 3]
	colors = [(0, 255, 0)]
	colors.extend(tuple(flat[index:index + 3]) for index in range(0, len(flat), 3))
	while len(colors) < 256:
		colors.append((0, 0, 0))
	palette_image = Image.new("P", (1, 1))
	palette_image.putpalette([channel for color in colors for channel in color])
	return colors, palette_image


def _indexed_frame(image, palette_image):
	image = image.convert("RGBA")
	alpha = image.getchannel("A")
	bounds = alpha.getbbox()
	if bounds is None:
		bounds = (0, 0, 1, 1)
	cropped = image.crop(bounds)
	indices = cropped.convert("RGB").quantize(palette=palette_image, dither=Image.Dither.NONE)
	data = bytearray(indices.tobytes())
	alpha_data = cropped.getchannel("A").tobytes()
	for index, opacity in enumerate(alpha_data):
		data[index] = 0 if opacity < 128 else data[index] + 1
	return cropped.width, cropped.height, bounds, bytes(data)


def _bam_bytes(images, cycles, anchor_adjust=(0, 0)):
	"""Write uncompressed BAM V1, retaining a distinct 256-entry palette."""
	colors, palette_image = _palette_for(images)
	frames = [_indexed_frame(image, palette_image) for image in images]
	frame_offset = 24
	cycle_offset = frame_offset + 12 * len(frames)
	palette_offset = cycle_offset + 4 * len(cycles)
	lookup_offset = palette_offset + 256 * 4
	lookup = []
	cycle_records = []
	for frame_indices in cycles:
		cycle_records.append((len(frame_indices), len(lookup)))
		lookup.extend(frame_indices)
	data_offset = lookup_offset + 2 * len(lookup)
	frame_records = []
	frame_data = bytearray()
	for width, height, bounds, pixels in frames:
		left, top, right, bottom = bounds
		# BAM's origin is the bottom-center ground contact point.
		center_x = (right - left) // 2 + anchor_adjust[0]
		center_y = (bottom - top) - 1 + anchor_adjust[1]
		frame_records.append((width, height, center_x, center_y,
			0x80000000 | (data_offset + len(frame_data))))
		frame_data.extend(pixels)
	header = b"BAM V1  " + struct.pack("<HBBIII", len(frames), len(cycles), 0,
		frame_offset, palette_offset, lookup_offset)
	frame_table = b"".join(struct.pack("<HHhhI", *record) for record in frame_records)
	cycle_table = b"".join(struct.pack("<HH", *record) for record in cycle_records)
	palette = b"".join(struct.pack("<BBBB", color[2], color[1], color[0], 0) for color in colors)
	frame_lookup = b"".join(struct.pack("<H", index) for index in lookup)
	return header + frame_table + cycle_table + palette + frame_lookup + frame_data


def write_npc_avatar(name, prefix, output_override):
	"""Compile one actor's 9-direction walk and idle BAM resources."""
	source = SPRITE_ROOT / name
	walk = [Image.open(source / f"{direction:02d}_{pose:02d}.png").convert("RGBA")
		for direction in range(9) for pose in range(4)]
	walk_cycles = [list(range(direction * 4, direction * 4 + 4)) for direction in range(9)]
	walk_bam = _bam_bytes(walk, walk_cycles)

	idle = [Image.open(source / f"{direction:02d}_00.png").convert("RGBA") for direction in range(9)]
	# The standard humanoid's G17 awake stance indexes cycles 63 through 71.
	idle_cycles = [[0] for _ in range(63)]
	idle_cycles.extend([[direction] for direction in range(9)])
	idle_bam = _bam_bytes(idle, idle_cycles)

	ready_cycles = [[0] for _ in range(9)]
	ready_cycles.extend([[direction] for direction in range(9)])
	ready_bam = _bam_bytes(idle, ready_cycles)

	output_override.mkdir(parents=True, exist_ok=True)
	(output_override / f"{prefix}G11.BAM").write_bytes(walk_bam)
	(output_override / f"{prefix}G1.BAM").write_bytes(ready_bam)
	(output_override / f"{prefix}G17.BAM").write_bytes(idle_bam)
	return (len(walk_bam), len(ready_bam), len(idle_bam))
