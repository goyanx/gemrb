#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Check the MCP scene-cast authoring contract against temporary files."""

import json
import shutil
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "terralum"))

import build_game
import mcp_server


class SceneCastAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.original_cast_path = build_game.CAST_FILE
        self.original_server_cast_path = mcp_server.CAST_FILE
        self.original_setup_path = mcp_server.SETUP_PATH
        self.original_story_path = mcp_server.STORY_PATH
        self.original_native_dialogue_path = build_game.NATIVE_DIALOGUE_FILE
        self.original_server_native_dialogue_path = mcp_server.NATIVE_DIALOGUE_FILE
        self.cast_path = self.temp_path / "scene_cast.json"
        shutil.copy2(self.original_cast_path, self.cast_path)
        self.setup_path = self.temp_path / "SetupGame.py"
        shutil.copy2(self.original_setup_path, self.setup_path)
        self.story_path = self.temp_path / "story.json"
        shutil.copy2(self.original_story_path, self.story_path)
        self.native_dialogue_path = self.temp_path / "native_dialogues.json"
        shutil.copy2(self.original_native_dialogue_path, self.native_dialogue_path)
        build_game.CAST_FILE = self.cast_path
        mcp_server.CAST_FILE = self.cast_path
        mcp_server.SETUP_PATH = self.setup_path
        mcp_server.STORY_PATH = self.story_path
        build_game.NATIVE_DIALOGUE_FILE = self.native_dialogue_path
        mcp_server.NATIVE_DIALOGUE_FILE = self.native_dialogue_path

    def tearDown(self):
        build_game.CAST_FILE = self.original_cast_path
        mcp_server.CAST_FILE = self.original_server_cast_path
        mcp_server.SETUP_PATH = self.original_setup_path
        mcp_server.STORY_PATH = self.original_story_path
        build_game.NATIVE_DIALOGUE_FILE = self.original_native_dialogue_path
        mcp_server.NATIVE_DIALOGUE_FILE = self.original_server_native_dialogue_path
        self.temp_dir.cleanup()

    @staticmethod
    def payload(result):
        return json.loads(result["content"][0]["text"])

    @staticmethod
    def npc(name="Test Wayfinder"):
        return {
            "name": name,
            "role": "Archive guide",
            "faction": "Deep Archives",
            "goal": "Help the party prepare without deciding what the Tear means.",
            "knowledge": "Knows the Index Hall records but has not visited Eldrador.",
            "voice": "Measured and precise, with short practical sentences.",
            "provenance": "adaptation",
            "creature": "riddler",
            "position": [710, 540],
            "line": "The record can guide your questions, but it cannot answer them for you.",
            "choices": [{
                "label": "Copy the record",
                "reply": "A working copy is prepared for the journey.",
                "flag": "TLTEST",
                "value": 1,
            }],
            "responses": [{"flag": "TLTEST", "value": 1,
                           "line": "The working copy is ready."}],
        }

    def test_flag_registration_and_scene_npc_upsert(self):
        original = self.cast_path.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "register campaign flags"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": self.npc()})
        self.assertEqual(self.cast_path.read_text(encoding="utf-8"), original)

        with self.assertRaisesRegex(ValueError, "register the journal event flag"):
            mcp_server.call_tool("terralum_set_journal_event", {
                "chapter": 1, "beat": 1, "flag": "TLTESTJOURNAL",
                "text": "An update for the test journal.", "section": 1,
            })
        journal_flag = self.payload(mcp_server.call_tool("terralum_register_campaign_flag", {
            "flag": "TLTESTJOURNAL",
        }))
        self.assertTrue(journal_flag["registered"])
        journal_event = self.payload(mcp_server.call_tool("terralum_set_journal_event", {
            "chapter": 1, "beat": 1, "flag": "TLTESTJOURNAL",
            "text": "An update for the test journal.", "section": 1,
        }))
        self.assertEqual(journal_event["journal"]["section"], 1)
        saved_story = json.loads(self.story_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_story["chapters"][0]["beats"][0]["journal"]["flag"], "TLTESTJOURNAL")

        last_scene_flag = self.payload(mcp_server.call_tool("terralum_register_campaign_flag", {
            "flag": "TLTESTLASTSCENE",
        }))
        self.assertTrue(last_scene_flag["registered"])
        last_scene_event = self.payload(mcp_server.call_tool("terralum_set_journal_event", {
            "chapter": len(build_game.AREAS), "beat": 1, "flag": "TLTESTLASTSCENE",
            "text": "The final scene authoring bound is reachable.", "section": 4,
        }))
        self.assertEqual(last_scene_event["chapter"], len(build_game.AREAS))
        saved_story = json.loads(self.story_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_story["chapters"][-1]["beats"][0]["journal"]["flag"], "TLTESTLASTSCENE")

        victory_flag = self.payload(mcp_server.call_tool("terralum_register_campaign_flag", {
            "flag": "TLTESTVICTORY",
        }))
        self.assertTrue(victory_flag["registered"])
        road_index = next(i for i, chapter in enumerate(saved_story["chapters"], start=1)
                          if chapter["area"] == "tl0002")
        victory_beat = next(i for i, beat in enumerate(saved_story["chapters"][road_index - 1]["beats"], start=1)
                            if beat.get("encounter"))
        victory_event = self.payload(mcp_server.call_tool("terralum_set_journal_event", {
            "chapter": road_index, "beat": victory_beat, "flag": "TLTESTVICTORY",
            "text": "The encounter was resolved.", "section": 2, "trigger": "victory",
        }))
        self.assertEqual(victory_event["trigger"], "victory")
        saved_story = json.loads(self.story_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_story["chapters"][road_index - 1]["beats"][victory_beat - 1]
                         ["victory_journal"]["flag"], "TLTESTVICTORY")
        with self.assertRaisesRegex(ValueError, "require an encounter"):
            mcp_server.call_tool("terralum_set_journal_event", {
                "chapter": len(build_game.AREAS), "beat": 1, "flag": "TLTESTVICTORY",
                "text": "Invalid victory hook.", "section": 2, "trigger": "victory",
            })
        with self.assertRaisesRegex(ValueError, "unique across story beats"):
            mcp_server.call_tool("terralum_set_journal_event", {
                "chapter": len(build_game.AREAS), "beat": 1, "flag": "TLJRN_ARCHIVE_WARD",
                "text": "Duplicate victory hook.", "section": 2,
            })

        registered = self.payload(mcp_server.call_tool("terralum_register_campaign_flag", {"flag": "TLTEST"}))
        self.assertEqual(registered, {"flag": "TLTEST", "registered": True, "initial_value": 0})
        repeated = self.payload(mcp_server.call_tool("terralum_register_campaign_flag", {"flag": "TLTEST"}))
        self.assertTrue(repeated["already_initialized"])
        self.assertIn('GemRB.SetGlobal("TLTEST", "GLOBAL", 0)', self.setup_path.read_text(encoding="utf-8"))

        added = self.payload(mcp_server.call_tool("terralum_upsert_scene_npc", {
            "area": "tl0001", "npc": self.npc(),
        }))
        self.assertEqual(added["npc_index"], 3)
        scene_cast = self.payload(mcp_server.call_tool("terralum_get_scene_cast", {"area": "tl0001"}))
        self.assertEqual(len(scene_cast["npcs"]), 4)
        with self.assertRaisesRegex(ValueError, "already exists"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": self.npc()})

        replacement = self.npc("Market Wayfinder")
        updated = self.payload(mcp_server.call_tool("terralum_upsert_scene_npc", {
            "area": "tl0001", "npc_index": 3, "npc": replacement,
        }))
        self.assertEqual(updated["npc_index"], 3)
        cast = build_game.read_cast()["tl0001"]
        self.assertEqual(len(cast), 4)
        self.assertEqual(cast[3]["name"], "Market Wayfinder")

    def test_multi_flag_dialogue_response_authoring(self):
        npc = self.npc("Conditional Wayfinder")
        npc["choices"] = []
        npc["responses"] = [{
            "when": [{"flag": "TLBRIEFING", "value": 1}, {"flag": "TLVOYAGE", "value": 2}],
            "line": "The response requires both expedition choices.",
        }]
        added = self.payload(mcp_server.call_tool("terralum_upsert_scene_npc", {
            "area": "tl0001", "npc": npc,
        }))
        self.assertEqual(added["npc"]["responses"][0]["when"][1]["flag"], "TLVOYAGE")

        invalid = self.npc("Unregistered Condition")
        invalid["choices"] = []
        invalid["responses"] = [{
            "when": [{"flag": "TLNOTREGISTERED", "value": 1}],
            "line": "This state cannot be read safely.",
        }]
        with self.assertRaisesRegex(ValueError, "register campaign flags"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {
                "area": "tl0001", "npc": invalid,
            })

    def test_native_dialogue_authoring_and_npc_binding(self):
        dialogue = {
            "states": [
                {"when": [{"flag": "TLCHAP", "value": 18}], "say": "First state.",
                 "transitions": [{"text": "Continue.", "next": 1}]},
                {"say": "Follow-up state.", "transitions": [{"text": "Close.", "final": True}]},
            ]
        }
        authored = self.payload(mcp_server.call_tool("terralum_upsert_native_dialogue", {
            "resref": "TestDlg", "dialogue": dialogue,
        }))
        self.assertEqual(authored["resref"], "TESTDLG")
        self.assertEqual(authored["states"], 2)
        self.assertEqual(build_game.read_native_dialogues()["TESTDLG"], dialogue)
        fetched = self.payload(mcp_server.call_tool("terralum_get_native_dialogue", {"resref": "testdlg"}))
        self.assertEqual(fetched["dialogue"], dialogue)

        invalid = json.loads(json.dumps(dialogue))
        invalid["states"][0]["when"][0]["flag"] = "TLNOTREGISTERED"
        with self.assertRaisesRegex(ValueError, "uninitialized entry conditions"):
            mcp_server.call_tool("terralum_upsert_native_dialogue", {
                "resref": "BADDLG", "dialogue": invalid,
            })

    def test_design_metadata_and_area_cast_invariants_are_required(self):
        npc = self.npc()
        del npc["goal"]
        with self.assertRaisesRegex(ValueError, "needs a nonempty goal"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": npc})
        npc = self.npc()
        del npc["faction"]
        with self.assertRaisesRegex(ValueError, "needs a nonempty faction"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": npc})
        with self.assertRaisesRegex(ValueError, "Unknown area"):
            mcp_server.call_tool("terralum_get_scene_cast", {"area": "tl9999"})
        listed = mcp_server.handle({"id": 1, "method": "tools/list"})["result"]["tools"]
        names = {tool["name"] for tool in listed}
        self.assertTrue({"terralum_get_scene_cast", "terralum_upsert_scene_npc",
                         "terralum_register_campaign_flag"}.issubset(names))
        set_journal_schema = next(tool["inputSchema"] for tool in mcp_server.TOOLS
                                  if tool["name"] == "terralum_set_journal_event")
        update_beat_schema = next(tool["inputSchema"] for tool in mcp_server.TOOLS
                                  if tool["name"] == "terralum_update_beat")
        self.assertEqual(set_journal_schema["properties"]["chapter"]["maximum"], len(build_game.AREAS))
        self.assertEqual(update_beat_schema["properties"]["chapter"]["maximum"], len(build_game.AREAS))
        self.assertEqual(set_journal_schema["properties"]["trigger"]["enum"], ["advance", "victory"])

    def test_staged_choice_requires_registered_nested_flags_and_valid_journal(self):
        npc = self.npc("Staged Market Archivist")
        npc["choices"][0]["followup"] = {
            "line": "Should the landmarks travel ahead of the sealed ledger?",
            "journal": {"flag": "TLSTAGEDJOURNAL", "section": 4,
                        "text": "The party chose how Mara will share Dorian's western route ledger."},
            "choices": [{"label": "Copy the landmarks", "reply": "Mara makes a copy.",
                         "flag": "TLSTAGED", "value": 1}],
        }
        original = self.cast_path.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "register campaign flags"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": npc})
        self.assertEqual(self.cast_path.read_text(encoding="utf-8"), original)

        for flag in ("TLTEST", "TLSTAGED", "TLSTAGEDJOURNAL"):
            mcp_server.call_tool("terralum_register_campaign_flag", {"flag": flag})
        added = self.payload(mcp_server.call_tool("terralum_upsert_scene_npc", {
            "area": "tl0001", "npc": npc,
        }))
        self.assertEqual(added["npc"]["choices"][0]["followup"]["journal"]["flag"], "TLSTAGEDJOURNAL")

        invalid = self.npc("Invalid Staged Archivist")
        invalid["choices"][0]["followup"] = {
            "line": "A valid question.",
            "journal": {"flag": "TLBADJOURNAL", "section": 3, "text": "Invalid section."},
            "choices": [{"label": "Seal", "reply": "Done.", "flag": "TLSTAGED", "value": 1}],
        }
        with self.assertRaisesRegex(ValueError, "complete options"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": invalid})
        self.assertEqual(len(build_game.read_cast()["tl0001"]), 4)

    def test_stdio_server_lists_and_calls_scene_tools(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                "name": "terralum_get_scene_cast", "arguments": {"area": "tl0015"},
            }},
        ]
        process = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "terralum" / "mcp_server.py")],
            input="\n".join(json.dumps(request) for request in requests) + "\n",
            capture_output=True, text=True, check=True,
        )
        replies = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual([reply["id"] for reply in replies], [1, 2, 3])
        tool_names = {tool["name"] for tool in replies[1]["result"]["tools"]}
        self.assertIn("terralum_upsert_scene_npc", tool_names)
        self.assertIn("terralum_set_journal_event", tool_names)
        self.assertEqual(replies[2]["result"]["content"][0]["type"], "text")
        self.assertIn("Hunter Fen", replies[2]["result"]["content"][0]["text"])
        self.assertNotIn("error", replies[2])


if __name__ == "__main__":
    unittest.main()
