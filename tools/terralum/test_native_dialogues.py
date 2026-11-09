#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Check compiled native DLG resources and their dialog.tlk references."""

import json
import os
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
    def test_all_compiled_dialogues_have_valid_reachable_text(self):
        pack = Path(os.environ.get("TERRALUM_GAME_OUTPUT", PROJECT / "build" / "game")).resolve()
        with (pack / "dialog.tlk").open("rb") as stream:
            talk_table = Tlk(stream)
        key_data = (pack / "chitin.key").read_bytes()
        _bif_count, resource_count, _bif_offset, resources_offset = struct.unpack_from("<4I", key_data, 8)
        resources = {struct.unpack_from("<8sHI", key_data, resources_offset + index * 14)[:2]
                     for index in range(resource_count)}
        cast = json.loads((PROJECT / "scene_cast.json").read_text(encoding="utf-8"))
        dialogues = read_native_dialogues()
        bindings = {}
        for area, people in cast.items():
            for person in people:
                if person.get("dialog"):
                    bindings.setdefault(person["dialog"].upper(), []).append((area, person["name"]))
        for resref, dialogue in dialogues.items():
            path = pack / "override" / f"{resref.lower()}.dlg"
            self.assertTrue(path.is_file(), f"missing compiled DLG for {resref}")
            data = path.read_bytes()
            header = struct.unpack_from("<8s11I", data)
            self.assertEqual(header[0], b"DLG V1.0")
            state_count, states_offset, transition_count, transitions_offset = header[1:5]
            state_triggers_offset, state_trigger_count = header[5:7]
            self.assertEqual(state_count, len(dialogue["states"]))
            self.assertIn((resref.lower().encode("ascii").ljust(8, b"\0"), 0x3F3), resources)
            states = [struct.unpack_from("<4I", data, states_offset + i * 16)
                      for i in range(state_count)]
            transitions = [struct.unpack_from("<5I8sI", data, transitions_offset + i * 32)
                           for i in range(transition_count)]
            actions_offset, action_count = header[9:11]
            actions = [struct.unpack_from("<II", data, actions_offset + index * 8)
                       for index in range(action_count)]
            action_scripts = [data[offset:offset + length].decode("ascii") for offset, length in actions]
            for index, (say_ref, first, count, trigger_index) in enumerate(states):
                self.assertEqual(talk_table[say_ref]["string"].decode("utf-8"), dialogue["states"][index]["say"])
                self.assertLessEqual(first + count, transition_count)
                if "when" in dialogue["states"][index]:
                    self.assertLess(trigger_index, state_trigger_count)
                    offset, length = struct.unpack_from("<II", data, state_triggers_offset + trigger_index * 8)
                    condition_text = data[offset:offset + length].decode("ascii")
                    for condition in dialogue["states"][index]["when"]:
                        self.assertIn(f'Global("{condition["flag"]}","GLOBAL",{condition["value"]})',
                                      condition_text)
                for local, transition in enumerate(transitions[first:first + count]):
                    authored_transition = dialogue["states"][index]["transitions"][local]
                    self.assertEqual(talk_table[transition[1]]["string"].decode("utf-8"), authored_transition["text"])
                    if not transition[0] & 0x08:
                        self.assertLess(transition[6], state_count)
                    if "journal" in authored_transition:
                        self.assertTrue(transition[0] & 0x10)
                        self.assertEqual(talk_table[transition[2]]["string"].decode("utf-8"),
                                         authored_transition["journal"])
                    if "set" in authored_transition:
                        self.assertTrue(transition[0] & 0x04)
                        self.assertLess(transition[4], action_count)
                        for write in authored_transition["set"]:
                            self.assertIn(
                                f'SetGlobal("{write["flag"]}","GLOBAL",{write["value"]})',
                                action_scripts[transition[4]],
                            )
        self.assertIn(("tl0001", "King Edmon"), bindings["KINGEDM"])
        self.assertIn(("tl0004", "King Edmon"), bindings["KINGEDM"])
        self.assertIn(("tl0001", "Queen Alisande"), bindings["ALISAND"])
        self.assertIn(("tl0004", "Queen Alisande"), bindings["ALISAND"])
        self.assertIn(("tl0011", "Queen Alisande"), bindings["ALISAND"])
        self.assertEqual(bindings["MARA"], [("tl0001", "Archivist Mara")])
        self.assertEqual(bindings["OREN"], [("tl0011", "Royal Scribe Oren")])
        self.assertEqual(bindings["PELL"], [("tl0011", "Courier Pell")])

    def test_compiled_alistair_dialogue_and_tlk(self):
        pack = Path(os.environ.get("TERRALUM_GAME_OUTPUT", PROJECT / "build" / "game")).resolve()
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
