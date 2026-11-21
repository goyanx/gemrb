#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later
"""Render the reference contact sheet for imported painted NPC turnarounds."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "terralum" / "art" / "reference" / "painted_turnarounds"
CHARACTERS = (
	("Archivist Mara", "mara.png"),
	("King Edmon", "edmon.png"),
	("Queen Alisande", "alisande.png"),
	("Scout Tessa", "tessa.png"),
	("Scholar Inessa", "inessa.png"),
	("Waywarden Saren", "saren.png"),
	("Lost Wayfarer", "wayfarer.png"),
	("Dorian the Seer", "dorian.png"),
	("Royal Scribe Oren", "oren.png"),
	("Courier Pell", "pell.png"),
	("Courier Eren", "eren.png"),
)
CELL = (240, 252)
COLUMNS = 3
ROWS = (len(CHARACTERS) + COLUMNS - 1) // COLUMNS
BACKGROUND = (30, 32, 37)


def main():
	canvas = Image.new("RGB", (CELL[0] * COLUMNS, CELL[1] * ROWS), BACKGROUND)
	draw = ImageDraw.Draw(canvas)
	font = ImageFont.load_default()
	for index, (name, filename) in enumerate(CHARACTERS):
		x = (index % COLUMNS) * CELL[0]
		y = (index // COLUMNS) * CELL[1]
		with Image.open(ART / filename) as source:
			sheet = source.convert("RGBA")
			sheet.thumbnail((CELL[0] - 16, CELL[1] - 42), Image.Resampling.LANCZOS)
			canvas.paste(sheet, (x + (CELL[0] - sheet.width) // 2,
				y + (CELL[1] - 34 - sheet.height) // 2), sheet)
		label = draw.textbbox((0, 0), name, font=font)
		label_width = label[2] - label[0]
		draw.text((x + (CELL[0] - label_width) // 2, y + CELL[1] - 27),
			name, fill=(235, 225, 207), font=font)
	canvas.save(ART / "contact-sheet.png")
	print(f"Rendered {len(CHARACTERS)} painted NPC turnaround references")


if __name__ == "__main__":
	main()
