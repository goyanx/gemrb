#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Check complete NPC portrait coverage, generated resources, and stable palettes."""

import json
import os
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "terralum"
sys.path.insert(0, str(ROOT / "tools" / "terralum"))
sys.path.insert(0, str(ROOT / "gemrb" / "GUIScripts" / "terralum"))

from build_game import PORTRAITS, PORTRAIT_SHEETS, read_cast
from NPCPalette import palettes_by_name


class PortraitCoverageTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.cast = read_cast()
		cls.people = [person for scene in cls.cast.values() for person in scene]
		cls.by_name = {person["name"]: person for person in cls.people}
		cls.pack = Path(os.environ.get("TERRALUM_GAME_OUTPUT", PROJECT / "build" / "game")).resolve()

	def test_every_named_npc_has_a_unique_portrait_resource(self):
		self.assertEqual(len(self.by_name), 42)
		refs = {person.get("portrait") for person in self.by_name.values()}
		self.assertNotIn(None, refs)
		self.assertEqual(len(refs), len(self.by_name))
		self.assertEqual(refs, set(PORTRAITS) - {"ALGORE"})
		self.assertIn("ALGORE", PORTRAITS)  # player portrait is included outside the NPC cast.
		for ref in refs:
			self.assertLessEqual(len(ref) + 1, 8, f"{ref} plus M/S suffix exceeds GemRB's 8-character resref")

	def test_each_portrait_is_built_at_medium_and_small_sizes(self):
		for ref in PORTRAITS:
			for suffix, expected_size in (("M", (169, 224)), ("S", (64, 64))):
				path = self.pack / "override" / f"{ref}{suffix}.bmp"
				self.assertTrue(path.is_file(), f"missing portrait resource {path.name}")
				with Image.open(path) as portrait:
					self.assertEqual(portrait.size, expected_size)

	def test_portrait_sheet_coordinates_fit_their_grid(self):
		for sheet_index, column, row in PORTRAITS.values():
			path, columns, rows = PORTRAIT_SHEETS[sheet_index]
			self.assertLess(column, columns, path.name)
			self.assertLess(row, rows, path.name)
			with Image.open(path) as sheet:
				self.assertGreater(sheet.width // columns, 0)
				self.assertGreater(sheet.height // rows, 0)

	def test_cast_palettes_are_stable_and_distinct(self):
		first = palettes_by_name(self.cast)
		second = palettes_by_name(dict(reversed(list(self.cast.items()))))
		self.assertEqual(first, second)
		self.assertEqual(len(first), len(self.by_name))
		self.assertEqual(len(set(first.values())), len(first))
		for scene in self.cast.values():
			palettes = [first[person["name"]] for person in scene]
			self.assertEqual(len(palettes), len(set(palettes)))


if __name__ == "__main__":
	unittest.main()
