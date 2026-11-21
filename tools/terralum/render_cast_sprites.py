#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later
"""Render any missing 9-direction sprite frames for the named Terralum cast."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_game import NPC_AVATARS, PROJECT, ROOT


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--blender", default=os.environ.get("BLENDER_BIN") or shutil.which("blender"),
			required=not (os.environ.get("BLENDER_BIN") or shutil.which("blender")))
	parser.add_argument("--force", action="store_true", help="rerender complete sprite sets")
	parser.add_argument("--only", action="append", default=[],
			help="render one named identity or asset resref; may be repeated")
	args = parser.parse_args()
	if not Path(args.blender).is_file():
		parser.error(f"Blender executable does not exist: {args.blender}")
	render_script = ROOT / "tools" / "terralum" / "render_npc_sprite.py"
	selected = [avatar for avatar in NPC_AVATARS if not args.only or
			any(selector.casefold() in (avatar["name"].casefold(), avatar["asset"].casefold())
				for selector in args.only)]
	if args.only and len(selected) != len(set(args.only)):
		missing = [selector for selector in args.only if not any(
			selector.casefold() in (avatar["name"].casefold(), avatar["asset"].casefold())
			for avatar in NPC_AVATARS)]
		if missing:
			parser.error("unknown NPC identity or asset: " + ", ".join(missing))
	for avatar in selected:
		output = PROJECT / "art" / "world_sprites" / avatar["asset"]
		frames = [output / f"{direction:02d}_{pose:02d}.png"
			for direction in range(9) for pose in range(4)]
		if not args.force and all(path.is_file() for path in frames):
			print(f"already rendered: {avatar['name']}")
			continue
		command = [args.blender, "--background", "--python", str(render_script), "--",
			str(output), avatar["asset"], avatar["profile"], str(avatar["seed"])]
		result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT, text=True)
		if result.returncode:
			print(result.stdout)
			result.check_returncode()
		if f"Rendered 36 frames for {avatar['asset']}" not in result.stdout:
			print(result.stdout)
			raise RuntimeError(f"Blender did not report a successful render for {avatar['name']}")
		if not all(path.is_file() for path in frames):
			raise RuntimeError(f"Blender did not produce all frames for {avatar['name']}")
		print(f"rendered {avatar['name']} ({avatar['profile']})", flush=True)
	write_contact_sheet()
	print(f"World sprite sets available: {len(NPC_AVATARS)}; rendered selection: {len(selected)}")


def write_contact_sheet():
	cell_w, cell_h, columns = 112, 132, 6
	rows = (len(NPC_AVATARS) + columns - 1) // columns
	sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), (30, 34, 40))
	draw = ImageDraw.Draw(sheet)
	font = ImageFont.load_default()
	for index, avatar in enumerate(NPC_AVATARS):
		x, y = (index % columns) * cell_w, (index // columns) * cell_h
		frame = Image.open(PROJECT / "art" / "world_sprites" / avatar["asset"] / "00_00.png").convert("RGBA")
		sheet.paste(frame, (x + 16, y + 2), frame)
		draw.text((x + 4, y + 100), avatar["name"][:17], fill=(240, 236, 224), font=font)
		draw.text((x + 4, y + 114), avatar["profile"], fill=(205, 180, 110), font=font)
	sheet.save(PROJECT / "art" / "world_sprites" / "cast-contact-sheet.png")


if __name__ == "__main__":
	main()
