# Terralum: Scrolls of Byzantem

This project is a playable campaign prototype for [GemRB](../README.md). GemRB runs Infinity Engine games; it is not a visual editor. The game starts with Algoreth Jon Goren as a wizard seeking the scrolls of Byzantem. Fourteen scene areas now span seven acts, from the early quest to his later, documented reign and the Tear of Chaos. The act cadence takes inspiration from long fantasy RPGs, **not** Baldur's Gate II content or playtime.

## AI and human contributor baseline

Read [GOLD_STANDARD_GAME_DESIGN_PIPELINE.md](GOLD_STANDARD_GAME_DESIGN_PIPELINE.md) before authoring or implementing Terralum content. It defines the canon rules, BG2-informed design principles, production gates, and per-scene acceptance checklist. Use the repo-root [TODO.md](../TODO.md) for current status and [LEARNINGS.md](../LEARNINGS.md) for verified engineering findings. The baseline is also exposed through the `terralum_get_design_standard` MCP tool.

## Story basis

The local campaign archive `C:\Users\goyan\Documents\GolemDungeon - kingdoms - kingdom-alsperia [1203075571572154459].txt` supports the early scroll quest. The user-supplied `TERRALUM_LORE_CODEX.md` supports the later Wizard King, eastern academy, Tear of Chaos, Archives and Eldrador arc. The user clarified that in the early period Queen Alisande was married to King Edmon. The sources do not recover the later transition to Algoreth's reign and marriage, so the game leaves that interval unwritten. See [`lore_notes.md`](lore_notes.md) for provenance and uncertainties. Neither source archive is copied into this repository.

story.json contains fourteen scene introductions and 37 story beats. The areas include Alsperia Market, the library and council; Mistwood Road and its ruined watchpost; Lorian Cavern and its seal gallery; the academy courtyard and vault; the Deep Archives and Index Hall; and Alsperia Skyport and the Aethercraft Hangar. scene_cast.json defines 29 named scene actors; their current sprites reuse the demo's two humanoid templates. Each area spawns its own cast. Talk cycles through local NPCs; choices across eight scenes set flags that affect later dialogue or route text. The three hostile encounters require victory before the story advances. The custom choices and transitions still need live input/save testing, and every area needs its own geometry. This is an expanded playable slice, not a full length RPG campaign.

scene_production_plan.md tracks the BG2-inspired delivery slices. campaign_plan.md maps the seven acts to a longer quest and location plan, with archive facts separated from new material. The preserved story_scrolls_draft.json records the earlier game draft before the codex arrived; it is not the active campaign.

## Build and play

From the repository root:

```powershell
python -m pip install Pillow
python tools/terralum/test_campaign_flow.py
python tools/terralum/test_mcp_authoring.py
python tools/terralum/build_game.py
./build/gemrb/gemrb -c terralum/build/terralum-wsl.cfg
```

The campaign-flow mock checks scene progression and response effects. The MCP test checks JSON-RPC discovery, cast authoring, and campaign-flag registration; neither replaces a live playthrough.

The last command uses the WSL build in this checkout. On Windows with a native GemRB build, use `terralum/build/terralum.cfg`. `terralum/play.ps1` builds and launches through WSL. The assembled pack under `terralum/build/` is ignored by Git.

The voice clips under `terralum/audio/` were rendered locally with Kokoro ONNX using the `af_heart` woman voice. To regenerate them, use the standalone Kokoro Python environment and provide local model and voice files:

```powershell
python tools/terralum/render_audio.py --model path\to\kokoro-v1.0.onnx --voices path\to\voices-v1.0.bin
```

The audio renderer also creates three original looping ambient tracks. It needs `kokoro_onnx`, `numpy`, `soundfile`, and `ffmpeg`. The model files are not included in the repository. Narration plays on chapter entry and through the **Narrate** button. The area song table selects city, woodland, or cavern ambience.

## Author with an AI coder

Run `tools/terralum/mcp_server.py` as a stdio Model Context Protocol server. Its tools inspect the project and per-scene cast, edit story beats, register initialized campaign flags, add or replace NPCs with role, goal, knowledge, voice, and provenance fields, import area art, and rebuild the pack. New NPC dialogue can reference only flags registered at game start. For example:

```json
{
  "mcpServers": {
    "terralum": {
      "command": "python",
      "args": ["D:/CODE/Terralum/gemrb/tools/terralum/mcp_server.py"]
    }
  }
}
```

GemRB and the inherited demo data have their own licenses; consult [`REUSE.toml`](../REUSE.toml) and [`demo/README.md`](../demo/README.md) before distribution. The new backdrop images, narration clips, and generated music are offered as CC0-1.0. The authoring code is GPL-2.0-or-later.
