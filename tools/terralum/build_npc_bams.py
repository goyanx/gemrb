#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later
"""Compile rendered Terralum NPC sprites into GemRB-compatible BAM V1 files."""

import struct
from pathlib import Path

from PIL import Image, ImageEnhance

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
		# BAM index zero is transparent. Quantizing against Pillow's padded
		# 256-entry palette can still emit index 255; clamp after shifting so it
		# maps to BAM's last valid opaque palette entry instead of overflowing.
		data[index] = 0 if opacity < 128 else min(data[index] + 1, 255)
	return cropped.width, cropped.height, bounds, bytes(data)


def _open_world_frame(path):
	"""Boost muted costume colors so nearby actors stay recognizable in-game."""
	with Image.open(path) as source:
		image = source.convert("RGBA")
	rgb = image.convert("RGB")
	rgb = ImageEnhance.Color(rgb).enhance(1.7)
	rgb = ImageEnhance.Contrast(rgb).enhance(1.16)
	rgb.putalpha(image.getchannel("A"))
	return rgb


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


def _scale_bam_v1(data, factor):
	"""Scale raw indexed BAM V1 frames while preserving palette and cycles."""
	if data[:8] != b"BAM V1  ":
		raise ValueError("protagonist scale source must be BAM V1")
	frame_count, cycle_count, compressed, frame_offset, palette_offset, lookup_offset = \
		struct.unpack_from("<HBBIII", data, 8)
	if compressed:
		raise ValueError("compressed BAM V1 frames are not supported for protagonist scaling")
	frames = [struct.unpack_from("<HHhhI", data, frame_offset + index * 12)
		for index in range(frame_count)]
	cycle_offset = frame_offset + 12 * frame_count
	cycles = [struct.unpack_from("<HH", data, cycle_offset + index * 4)
		for index in range(cycle_count)]
	lookup_count = max((start + count for count, start in cycles), default=0)
	lookups = data[lookup_offset:lookup_offset + lookup_count * 2]
	palette = data[palette_offset:palette_offset + 1024]
	new_frame_offset = 24
	new_cycle_offset = new_frame_offset + 12 * frame_count
	new_palette_offset = new_cycle_offset + 4 * cycle_count
	new_lookup_offset = new_palette_offset + 1024
	new_data_offset = new_lookup_offset + len(lookups)
	new_records = []
	new_pixels = bytearray()
	for width, height, center_x, center_y, frame_flags in frames:
		if not frame_flags & 0x80000000:
			raise ValueError("compressed BAM V1 frame cannot be scaled")
		pixels_offset = frame_flags & 0x7FFFFFFF
		pixels = data[pixels_offset:pixels_offset + width * height]
		if len(pixels) != width * height:
			raise ValueError("truncated BAM V1 frame data")
		new_width, new_height = max(1, round(width * factor)), max(1, round(height * factor))
		image = Image.frombytes("P", (width, height), pixels)
		image.putpalette([channel for entry in range(256)
			for channel in (palette[entry * 4 + 2], palette[entry * 4 + 1], palette[entry * 4])])
		resized = image.resize((new_width, new_height), Image.Resampling.NEAREST).tobytes()
		new_records.append((new_width, new_height, round(center_x * factor),
			round(center_y * factor), 0x80000000 | (new_data_offset + len(new_pixels))))
		new_pixels.extend(resized)
	header = b"BAM V1  " + struct.pack("<HBBIII", frame_count, cycle_count, 0,
		new_frame_offset, new_palette_offset, new_lookup_offset)
	frame_table = b"".join(struct.pack("<HHhhI", *record) for record in new_records)
	cycle_table = b"".join(struct.pack("<HH", *cycle) for cycle in cycles)
	return header + frame_table + cycle_table + palette + lookups + new_pixels


def _vhr_fallback_bam(data, first_cycle):
	"""Reuse G17 idle directions at a VHR stance's fixed cycle offset."""
	if data[:8] != b"BAM V1  ":
		raise ValueError("VHR fallback source must be BAM V1")
	frame_count, cycle_count, compressed, frame_offset, palette_offset, lookup_offset = \
		struct.unpack_from("<HBBIII", data, 8)
	if compressed:
		raise ValueError("compressed BAM V1 frames cannot back VHR fallback stances")
	frames = [struct.unpack_from("<HHhhI", data, frame_offset + index * 12)
		for index in range(frame_count)]
	cycle_offset = frame_offset + frame_count * 12
	cycles = [struct.unpack_from("<HH", data, cycle_offset + index * 4)
		for index in range(cycle_count)]
	lookup_count = max((start + count for count, start in cycles), default=0)
	lookups = [struct.unpack_from("<H", data, lookup_offset + index * 2)[0]
		for index in range(lookup_count)]
	idle_frames = []
	for direction in range(9):
		count, start = cycles[63 + direction]
		if not count:
			raise ValueError("G17 source is missing an awake idle direction")
		idle_frames.append(lookups[start])
	old_data_offset = lookup_offset + lookup_count * 2
	pixels = data[old_data_offset:]
	new_cycle_count = first_cycle + 9
	cycle_lookups = [idle_frames[0]] * first_cycle + idle_frames
	new_frame_offset = 24
	new_cycle_offset = new_frame_offset + frame_count * 12
	new_palette_offset = new_cycle_offset + new_cycle_count * 4
	new_lookup_offset = new_palette_offset + 1024
	new_data_offset = new_lookup_offset + new_cycle_count * 2
	frame_table = []
	for width, height, center_x, center_y, frame_flags in frames:
		old_pixels_offset = frame_flags & 0x7FFFFFFF
		new_flags = 0x80000000 | (new_data_offset + old_pixels_offset - old_data_offset)
		frame_table.append((width, height, center_x, center_y, new_flags))
	header = b"BAM V1  " + struct.pack("<HBBIII", frame_count, new_cycle_count, 0,
		new_frame_offset, new_palette_offset, new_lookup_offset)
	frame_records = b"".join(struct.pack("<HHhhI", *record) for record in frame_table)
	cycle_records = b"".join(struct.pack("<HH", 1, index) for index in range(new_cycle_count))
	lookup_bytes = b"".join(struct.pack("<H", index) for index in cycle_lookups)
	palette = data[palette_offset:palette_offset + 1024]
	return header + frame_records + cycle_records + palette + lookup_bytes + pixels


def write_scaled_player_avatar(source_override, output_override, factor=2.00):
	"""Give the playable Algoreth and his scene cameo one larger animation."""
	base_creature = bytearray((source_override / "protagon.cre").read_bytes())
	if base_creature[:8] != b"CRE V1.0":
		raise ValueError("protagon.cre must be a supported CRE V1.0 source")
	animation_id, prefix = 0xC8F0, "TLPG"
	struct.pack_into("<I", base_creature, 0x28, animation_id)
	(output_override / "algopc.cre").write_bytes(base_creature)
	# The game party is instantiated from protagonist.cre. Previously only the
	# scripted scene cameo used algopc.cre, so it looked enlarged while the
	# controllable character stayed at the demo's original scale.
	(output_override / "protagon.cre").write_bytes(base_creature)
	with (output_override / "avatars.2da").open("a", encoding="utf-8", newline="") as table:
		table.write(f"\n0x{animation_id:04X} {prefix} {prefix} {prefix} {prefix} 0 2 0 *")
	player_stances = {}
	for suffix in ("G11", "G1", "G17"):
		# The demo has no separate G1 ready BAM; its G17 is the idle stance
		# source used for both modes.
		source_suffix = "G17" if suffix == "G1" else suffix
		source = source_override / f"CHMB1{source_suffix}.BAM"
		player_stances[suffix] = _scale_bam_v1(source.read_bytes(), factor)
		(output_override / f"{prefix}{suffix}.BAM").write_bytes(player_stances[suffix])
	# VHR stances address fixed cycle offsets. The source G17 BAM only has
	# populated awake orientations at 63-71; aliases must explicitly map those
	# nine frames to each requested stance offset, including G1 ready at 9-17.
	for suffix, first_cycle in (("G1", 9), ("G12", 18), ("G13", 27), ("G14", 36),
							("G15", 45), ("G16", 54), ("G18", 72), ("G19", 81)):
		(output_override / f"{prefix}{suffix}.BAM").write_bytes(
			_vhr_fallback_bam(player_stances["G17"], first_cycle))


def write_npc_avatar(name, prefix, output_override):
	"""Compile one actor's 9-direction walk and idle BAM resources."""
	source = SPRITE_ROOT / name
	walk = [_open_world_frame(source / f"{direction:02d}_{pose:02d}.png")
		for direction in range(9) for pose in range(4)]
	walk_cycles = [list(range(direction * 4, direction * 4 + 4)) for direction in range(9)]
	walk_bam = _bam_bytes(walk, walk_cycles)

	idle = [_open_world_frame(source / f"{direction:02d}_00.png") for direction in range(9)]
	attack_paths = [source / f"attack_{direction:02d}.png" for direction in range(9)]
	attack = [_open_world_frame(path) for path in attack_paths] if all(
		path.is_file() for path in attack_paths) else idle
	# The standard humanoid's G17 awake stance indexes cycles 63 through 71.
	idle_cycles = [[0] for _ in range(63)]
	idle_cycles.extend([[direction] for direction in range(9)])
	idle_bam = _bam_bytes(idle, idle_cycles)

	ready_cycles = [[0] for _ in range(9)]
	ready_cycles.extend([[direction] for direction in range(9)])
	ready_bam = _bam_bytes(idle, ready_cycles)

	# GemRB's mirrored-human animation type addresses these stances at fixed
	# VHR cycle offsets. Reuse the directional idle frames as safe fallback
	# poses, while keeping every expected cycle index present in the BAM.
	stance_bams = {}
	for suffix, first_cycle in (("G12", 18), ("G13", 27), ("G14", 36),
							("G15", 45), ("G16", 54), ("G18", 72), ("G19", 81)):
		cycles = [[0] for _ in range(first_cycle)]
		cycles.extend([[direction] for direction in range(9)])
		stance_bams[suffix] = _bam_bytes(idle, cycles)

	output_override.mkdir(parents=True, exist_ok=True)
	(output_override / f"{prefix}G11.BAM").write_bytes(walk_bam)
	(output_override / f"{prefix}G1.BAM").write_bytes(ready_bam)
	(output_override / f"{prefix}G17.BAM").write_bytes(idle_bam)
	for suffix, data in stance_bams.items():
		(output_override / f"{prefix}{suffix}.BAM").write_bytes(data)

	# IE_ANI_CODE_MIRROR resolves the three weapon families to a1-a3,
	# a4-a6, or a7-a9 during melee. Supply all directional action BAMs.
	attack_frames = []
	attack_cycles = []
	for direction in range(9):
		start = len(attack_frames)
		attack_frames.extend((idle[direction], attack[direction], idle[direction]))
		attack_cycles.append([start, start + 1, start + 2])
	attack_bam = _bam_bytes(attack_frames, attack_cycles)
	for suffix in range(1, 10):
		(output_override / f"{prefix}a{suffix}.BAM").write_bytes(attack_bam)
	return (len(walk_bam), len(ready_bam), len(idle_bam))
