# Terralum: Scrolls of Byzantem

This project is a playable campaign prototype for [GemRB](../README.md). GemRB runs Infinity Engine games; it is not a visual editor. The game starts with Algoreth Jon Goren as a wizard seeking the scrolls of Byzantem. Twenty-five scene areas now span seven acts, from the early quest to his later, documented reign and the unresolved Eldrador Tear. The act cadence takes inspiration from long fantasy RPGs, **not** Baldur's Gate II content or playtime.

## AI and human contributor baseline

Read [GOLD_STANDARD_GAME_DESIGN_PIPELINE.md](GOLD_STANDARD_GAME_DESIGN_PIPELINE.md) before authoring or implementing Terralum content. It defines the canon rules, BG2-informed design principles, production gates, and per-scene acceptance checklist. Use the repo-root [TODO.md](../TODO.md) for current status and [LEARNINGS.md](../LEARNINGS.md) for verified engineering findings. The baseline is also exposed through the `terralum_get_design_standard` MCP tool.

## Story basis

The local campaign archive `C:\Users\goyan\Documents\GolemDungeon - kingdoms - kingdom-alsperia [1203075571572154459].txt` supports the early scroll quest. The user-supplied `TERRALUM_LORE_CODEX.md` supports the later Wizard King, eastern academy, Tear of Chaos, Archives and Eldrador arc. The user clarified that in the early period Queen Alisande was married to King Edmon. The sources do not recover the later transition to Algoreth's reign and marriage, so the game leaves that interval unwritten. See [`lore_notes.md`](lore_notes.md) for provenance and uncertainties. Neither source archive is copied into this repository.

story.json contains twenty-five scene introductions and 63 story beats; story and cast data define thirty-one one-time journal events and 56 authored response options across twenty-one scenes. The opening Market conversation now has two stages: Mara asks whether Inessa should receive a separate copy of the landmarks or the ledger should remain sealed for court review. The decision is journaled once and changes Scholar Inessa's dialogue in the Library. The new Waywarden Relay follows the Ruined Watchpost before the Lorian approach. After Lorian, the campaign revisits the watchpost under its own area resref, with Courier Pell and Waywarden Saren carrying forward patrol and ambush state. Keeper Orla asks whether to call the west patrol or leave the signal dark; Waywarden Saren acknowledges whether Leora's schedule was copied, and the choice is journaled. The areas include Alsperia Market, Library, Royal Dispatch Archive, and Royal Stables; the Mistwood Hunter's Camp, River Crossing, Three-Cairn Fork, Road, Watchpost, and Waywarden Relay; Lorian Cavern and its seal gallery; the return court and council; the academy courtyard, Containment Annex, and vault; the Deep Archives and Index Hall; Alsperia Skyport, the Expedition Chart Room, and the Aethercraft Hangar; and Eldrador's Arrival Quay and Lower Sanctuary Threshold. scene_cast.json defines 62 named scene actors; their current sprites reuse the demo's two humanoid templates. Each area spawns its own cast. Most NPC conversations still use the custom Talk cycle and panel choices; flags affect later dialogue or route text. Alistair’s Chart Room and Hangar actors are bound to a native DLG resource with topic choices and four state-specific Hangar responses; isolated GemRB testing now confirms actor click-to-talk opens Queen Alisande's DLG and one response advances; other DLG actors, branches, and save/load still need playtesting. At the Royal Dispatch Archive, Archivist Leora offers a choice to copy or preserve Edmon’s west-road patrol schedule; the journaled copy makes the Waywarden diversion reliable at the Mistwood ambush. At the Royal Stables, Stablemaster Edda offers a lantern or rope kit; the choice changes which Mistwood bypass is safe and is acknowledged at camp. At Hunter's Camp, Scout Tessa chooses whether to light the lantern, and Ranger Ilya can reveal a creekside path that safely bypasses the ambush while keeping the camp dark. At Mistwood’s river crossing, Maelin and Eren offer a rope handline or an exposed stepping-stone route; only the prepared rope kit makes the downstream stalker bypass safe, and Eren reports the outcome at the watchpost. At the Three-Cairn Fork, Waykeeper Sella and Carver Doma disagree over a storm-turned waystone; the player's choice changes their later account at the watchpost. In Lorian, Algoreth must answer Dorian's question about the scrolls' purpose before facing the Guardian; the journal records his answer and the Guardian responds to it. In the Seal Gallery, the answer to the inscription is required, journaled, and changes Queen Alisande's return-court response. In the academy Containment Annex, Warden Celene offers a measured boundary or purpose rule; the journal records the choice, Magister Vael acknowledges it in the vault, and the selected approach changes the sealing narration while the false self remains contained. The vault battle has two phases: a ward shard reveals the named False Algoreth actor, who responds to both prior warding choices across four combinations. The seal is journaled only after both phases. If the party falls, reload a pre-fight save; live defeat and reload behavior remain unverified. In the Deep Archives, Archivist Nera offers a peaceful or combat route to consult the Index Warden; victory records the recovered comparison leaf, and Selene and Ealdrin respond to the choice in Index Hall. Selene now identifies the source only as a titleless living record with an unknown speaker. If the player keeps the account sealed, a required follow-up asks which bounded question Ealdrin should carry to Eldrador; the answer changes Queen Vaelthira's welcome without turning the record into a witness. In Act IV, Royal Scribe Oren asks Algoreth whether to place Dorian's route testimony beside the scroll account or file them separately; the required choice is journaled and changes Queen Alisande's response without inventing what the scrolls mean. At the Expedition Chart Room, Algoreth chooses whether to carry Selene's marked archive copy or Ealdrin's questions for Eldrador's warders. The required choice is journaled and changes Flight Marshal Aven's hangar dialogue. The Eldrador Landing Quay adds a choice between collecting warder testimony or copying measured seal records; Vaelthira acknowledges it at the Lower Sanctuary Threshold. There, Algoreth chooses whether to approach the outer ring or remain back while Seraphina listens. The endpoint remains before the sealed inner gate, leaving the Tear unresolved. All twenty-five scenes have custom data-authored searchmaps with connected starts, scene casts, encounter positions, routes, and blocked features. The Mistwood ambush spawns two authored foes on connected road positions; the Lorian Guardian waits beside the chest and becomes hostile in place. Live movement still needs verification. All areas still inherit the demo WED geometry. The custom panel's JOURNAL button or `j` shortcut opens saved GemRB journal entries. Only one native DLG path has been live-tested; broader choices, transitions, and save/load still need input testing. This is an expanded playable slice, not a full-length RPG campaign.

scene_production_plan.md tracks the BG2-inspired delivery slices. campaign_plan.md maps the seven acts to a longer quest and location plan, with archive facts separated from new material. The preserved story_scrolls_draft.json records the earlier game draft before the codex arrived; it is not the active campaign.

## Build and play

Native Infinity Engine DLG conversations currently cover Archivist Mara, King Edmon, and Queen Alisande in the opening scene, Royal Scribe Oren in the council, and Alistair in the Chart Room and Hangar. Mara's and Oren's two-stage DLGs set the same campaign globals as the custom panel, write one shared journal entry each, and feed later dialogue by Inessa and Alisande. At the council, Captain Rovan’s one-time open-road/restricted-scroll policy is journaled. Courier Pell offers an optional public-warning or crown-restricted deposition; both interaction surfaces journal the selected record, and Queen Alisande’s later council response combines Pell’s decision with Oren’s paired/separate docket choice. Edmon and Alisande's return-court DLG entry states combine the public/archive route choice with the resolved/open Lorian gallery warning; Alisande’s twelve council responses combine Rovan’s policy, Pell’s deposition, and Oren’s docket outcomes. Other authored NPC choices still use the campaign panel. DLG resources are compiled with `dialog.tlk` strings and checked by `test_native_dialogues.py`; Queen Alisande's actor click-to-talk and one response are verified in isolated GemRB; other NPCs and save/load still need playtesting.

From the repository root:

```powershell
python -m pip install Pillow
python tools/terralum/test_area_searchmaps.py
python tools/terralum/test_campaign_flow.py
python tools/terralum/test_mcp_authoring.py
python tools/terralum/build_game.py
python tools/terralum/test_native_dialogues.py
./build/gemrb/gemrb -c terralum/build/terralum-wsl.cfg
```

The campaign-flow mock checks scene progression and response effects. The MCP test checks JSON-RPC discovery, cast authoring, and campaign-flag registration; neither replaces a live playthrough.

The last command uses the WSL build in this checkout. On Windows with a native GemRB build, use `terralum/build/terralum.cfg`. `terralum/play.ps1` builds and launches through WSL and stops if another GemRB process is already running, preventing ambiguous duplicate game windows. The assembled pack under `terralum/build/` is ignored by Git.

If a running GemRB session has the standard pack open, set `TERRALUM_GAME_OUTPUT` to an isolated output folder before running `build_game.py` and `test_native_dialogues.py`. The builder places the matching Windows and WSL config files next to that pack and leaves the normal launch config untouched.

The voice clips under `terralum/audio/` were rendered locally with Kokoro ONNX using the `af_heart` woman voice. To regenerate them, use the standalone Kokoro Python environment and provide local model and voice files:

```powershell
python tools/terralum/render_audio.py --model path\to\kokoro-v1.0.onnx --voices path\to\voices-v1.0.bin
```

The audio renderer also creates three original looping ambient tracks. It needs `kokoro_onnx`, `numpy`, `soundfile`, and `ffmpeg`. The model files are not included in the repository. Narration plays on chapter entry and through the **Narrate** button. The area song table selects city, woodland, or cavern ambience.

## Author with an AI coder

Run `tools/terralum/mcp_server.py` as a stdio Model Context Protocol server. Its tools inspect the project and per-scene cast, read and upsert native DLG state machines, edit story beats, register initialized campaign flags, set journal events, add or replace NPCs with role, faction, goal, knowledge, voice, and provenance fields, attach journal events to beat advancement or encounter victory, import area art, and rebuild the pack. New NPC dialogue and journal events can reference only flags registered at game start. For example:

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
