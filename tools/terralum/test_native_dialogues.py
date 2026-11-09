#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Check the native Alistair DLG and its compiled dialog.tlk references."""

import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "terralum"
sys.path.insert(0, str(ROOT / "tools" / "terralum"))
sys.path.insert(0, str(ROOT / "tools" / "tlk_convert"))

from build_game import read_native_dialogues
from tlk import Tlk


class NativeDialogueResourceTests(unittest.TestCase):
    def test_compiled_alistair_dialogue_and_tlk(self):
        pack = PROJECT / "build" / "game"
        dlg_path = pack / "override" / "alistar.dlg"
        tlk_path = pack / "dialog.tlk"
        self.assertTrue(dlg_path.is_file(), "build the game pack before checking DLG resources")
        self.assertTrue(tlk_path.is_file())
        data = dlg_path.read_bytes()
        header = struct.unpack_from("<8s11I", data)
        (signature, state_count, states_offset, transition_count, transitions_offset,
         state_triggers_offset, state_trigger_count, transition_triggers_offset,
         transition_trigger_count, actions_offset, action_count, flags) = header
        self.assertEqual(signature, b"DLG V1.0")
        self.assertEqual(states_offset, 52)
        self.assertEqual(transitions_offset, states_offset + state_count * 16)
        self.assertEqual(state_triggers_offset, transitions_offset + transition_count * 32)
        self.assertEqual(transition_triggers_offset, state_triggers_offset + state_trigger_count * 8)
        self.assertEqual(transition_trigger_count, 0)
        self.assertEqual(actions_offset, transition_triggers_offset)
        self.assertEqual(action_count, 0)
        self.assertEqual(flags, 0)
        self.assertEqual(len(data), actions_offset + sum(
            struct.unpack_from("<I", data, state_triggers_offset + i * 8 + 4)[0]
            for i in range(state_trigger_count)
        ))

        with tlk_path.open("rb") as stream:
            talk_table = Tlk(stream)
        self.assertGreater(len(talk_table), 115)
        key_data = (pack / "chitin.key").read_bytes()
        self.assertEqual(key_data[:8], b"KEY V1  ")
        _bif_count, resource_count, _bif_offset, resources_offset = struct.unpack_from("<4I", key_data, 8)
        resources = [struct.unpack_from("<8sHI", key_data, resources_offset + index * 14)[:2]
                     for index in range(resource_count)]
        self.assertIn((b"alistar\0", 0x3F3), resources)
        authored = read_native_dialogues()["ALISTAR"]["states"]
        states = [struct.unpack_from("<4I", data, states_offset + i * 16)
                  for i in range(state_count)]
        transitions = [struct.unpack_from("<5I8sI", data, transitions_offset + i * 32)
                       for i in range(transition_count)]
        for state_index, (say_ref, first, count, trigger_index) in enumerate(states):
            self.assertLess(say_ref, len(talk_table))
            self.assertLessEqual(first + count, transition_count)
            self.assertEqual(talk_table[say_ref]["string"].decode("utf-8"), authored[state_index]["say"])
            for local_index, (flags, text_ref, _journal, _trigger, _action, _dialog, next_state) in enumerate(
                    transitions[first:first + count]):
                self.assertTrue(flags & 0x01)
                self.assertLess(text_ref, len(talk_table))
                self.assertEqual(talk_table[text_ref]["string"].decode("utf-8"),
                                 authored[state_index]["transitions"][local_index]["text"])
                if flags & 0x08:
                    continue
                self.assertLess(next_state, state_count)
            if "when" in authored[state_index]:
                self.assertLess(trigger_index, state_trigger_count)
                offset, length = struct.unpack_from("<II", data, state_triggers_offset + trigger_index * 8)
                self.assertGreater(length, 0)
                self.assertIn(b"Global(\"TLCHAP\"", data[offset:offset + length])
            else:
                self.assertEqual(trigger_index, 0xFFFFFFFF)

        cast = json.loads((PROJECT / "scene_cast.json").read_text(encoding="utf-8"))
        for area in ("tl0020", "tl0014"):
            alistair = next(person for person in cast[area] if person["name"] == "Alistair")
            self.assertEqual(alistair["dialog"], "ALISTAR")


if __name__ == "__main__":
    unittest.main()
