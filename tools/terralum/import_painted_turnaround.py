#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later
"""Convert a 3x3 painted turnaround into GemRB's 9-direction idle source frames.

The first art pass imports painted idle views. It duplicates each authored view
across the four walk-frame slots until hand-painted movement frames are ready.
"""

import argparse
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
FRAME_SIZE = (80, 96)
# Sprite-sheet rows: front-left, front, front-right; side-left, three-quarter,
# side-right; back-left, back, back-right.
DIRECTIONS = ((1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 1))


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("sheet", type=Path, help="transparent 3x3 turnaround PNG")
	parser.add_argument("asset", help="world sprite folder name, such as mara00")
	parser.add_argument("--attack", action="store_true",
		help="import directional attack views as attack_00.png through attack_08.png")
	parser.add_argument("--scale", type=float, default=1.0,
		help="scale the 80x96 frame canvas for a larger actor")
	args = parser.parse_args()
	if args.scale <= 0:
		parser.error("--scale must be positive")
	with Image.open(args.sheet) as source:
		image = source.convert("RGBA")
	output = ROOT / "terralum" / "art" / "world_sprites" / args.asset
	output.mkdir(parents=True, exist_ok=True)
	for direction, (column, row) in enumerate(DIRECTIONS):
		left, right = round(column * image.width / 3), round((column + 1) * image.width / 3)
		top, bottom = round(row * image.height / 3), round((row + 1) * image.height / 3)
		cell = image.crop((left, top, right, bottom))
		alpha = cell.getchannel("A")
		bounds = alpha.getbbox()
		if bounds is None:
			raise ValueError(f"empty transparent cell at row {row}, column {column}")
		cell = cell.crop(bounds)
		frame_size = tuple(round(value * args.scale) for value in FRAME_SIZE)
		cell.thumbnail((round(72 * args.scale), round(88 * args.scale)), Image.Resampling.LANCZOS)
		frame = Image.new("RGBA", frame_size, (0, 0, 0, 0))
		frame.alpha_composite(cell, ((frame_size[0] - cell.width) // 2, frame_size[1] - cell.height))
		if args.attack:
			frame.save(output / f"attack_{direction:02d}.png")
		else:
			for pose in range(4):
				frame.save(output / f"{direction:02d}_{pose:02d}.png")
	mode = "attack" if args.attack else "idle"
	print(f"Imported 9 painted {mode} views for {args.asset} into {output}")


if __name__ == "__main__":
	main()
