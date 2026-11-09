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
        self.cast_path = self.temp_path / "scene_cast.json"
        shutil.copy2(self.original_cast_path, self.cast_path)
        self.setup_path = self.temp_path / "SetupGame.py"
        shutil.copy2(self.original_setup_path, self.setup_path)
        build_game.CAST_FILE = self.cast_path
        mcp_server.CAST_FILE = self.cast_path
        mcp_server.SETUP_PATH = self.setup_path

    def tearDown(self):
        build_game.CAST_FILE = self.original_cast_path
        mcp_server.CAST_FILE = self.original_server_cast_path
        mcp_server.SETUP_PATH = self.original_setup_path
        self.temp_dir.cleanup()

    @staticmethod
    def payload(result):
        return json.loads(result["content"][0]["text"])

    @staticmethod
    def npc(name="Test Wayfinder"):
        return {
            "name": name,
            "role": "Archive guide",
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

    def test_design_metadata_and_area_cast_invariants_are_required(self):
        npc = self.npc()
        del npc["goal"]
        with self.assertRaisesRegex(ValueError, "needs a nonempty goal"):
            mcp_server.call_tool("terralum_upsert_scene_npc", {"area": "tl0001", "npc": npc})
        with self.assertRaisesRegex(ValueError, "Unknown area"):
            mcp_server.call_tool("terralum_get_scene_cast", {"area": "tl9999"})
        listed = mcp_server.handle({"id": 1, "method": "tools/list"})["result"]["tools"]
        names = {tool["name"] for tool in listed}
        self.assertTrue({"terralum_get_scene_cast", "terralum_upsert_scene_npc",
                         "terralum_register_campaign_flag"}.issubset(names))

    def test_stdio_server_lists_and_calls_scene_tools(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                "name": "terralum_get_scene_cast", "arguments": {"area": "tl0013"},
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
        self.assertEqual(replies[2]["result"]["content"][0]["type"], "text")
        self.assertNotIn("error", replies[2])


if __name__ == "__main__":
    unittest.main()
