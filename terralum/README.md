# Terralum: Scrolls of Byzantem

This project is a playable campaign prototype for [GemRB](../README.md). GemRB runs Infinity Engine games; it is not a visual editor. The game starts with Algoreth Jon Goren as a wizard seeking the scrolls of Byzantem. Twenty-five scene areas now span seven acts, from the early quest to his later, documented reign and the unresolved Eldrador Tear. The act cadence takes inspiration from long fantasy RPGs, **not** Baldur's Gate II content or playtime.

## In-game screenshots

These captures come from isolated GemRB sessions. Mistwood shows the optional Wayfarer report and its Journal entry; the Watchpost capture shows Courier Pell responding to the anonymous warning while leaving the voice unexplained. The Market capture shows Archivist Mara's new portrait beside her dialogue.

| Mistwood choice | Act II Journal | Watchpost callback | NPC portrait |
| --- | --- | --- |
| ![The Lost Wayfarer offers two reporting choices on Mistwood Road](screenshots/mistwood-wayfarer-choice.png) | ![The Act II Journal records the anonymous warning](screenshots/mistwood-wayfarer-journal.png) | ![Courier Pell acknowledges the anonymous warning at the Watchpost](screenshots/ruined-watchpost-pell-callback.png) | ![Archivist Mara's custom portrait appears with her dialogue](screenshots/archivist-mara-dialogue-portrait.png) |

The earlier 38-NPC avatar pass used low-poly Blender figures. That approach looked too much like blocky 3D game characters and is no longer the target art direction. The core recurring cast is now transitioning to hand-painted 2D world sprites. Eleven characters have painted turnaround sources and imported world frames; Mara, Edmon, and Alisande appear in a live Market capture. Remaining cast members and authored movement cycles still need this conversion.

![Live GemRB Market scene with painted Mara, Queen Alisande, and King Edmon sprites and the enlarged Algoreth player character](screenshots/painted-opening-cast.png)

![Painted 2D turnarounds for eleven Terralum characters](art/reference/painted_turnarounds/contact-sheet.png)

The turnaround import tool is documented in [`art/reference/painted_turnarounds/README.md`](art/reference/painted_turnarounds/README.md). The current import fills the four walk slots with the same painted view, so idle rendering is usable but walking is not animation-complete. Review source sheets, then inspect the converted character in a built GemRB scene.

![Market NPCs with distinct green, orange, and teal clothing palettes](screenshots/alsperia-market-npc-palettes.png)

![Market NPCs with individual animated world avatars](screenshots/terralum-cast-avatars-live.png)

![Party movement through the Alsperia Market with the camera following](screenshots/market-party-moved-live.png)

![Contact sheet of all 38 named NPC world avatars](art/world_sprites/cast-contact-sheet.png)

| Scout Tessa at Hunter's Camp | Saren's live schedule dialogue | Relay choice in the Journal |
| --- | --- | --- |
| ![Scout Tessa's new hood and quiver avatar in the Hunter's Camp scene](screenshots/progression-tessa-choice.png) | ![Waywarden Saren's dialogue acknowledges Leora's copied schedule](screenshots/progression-saren-direct-talk.png) | ![The Act II Journal records the patrol call at the Relay](screenshots/progression-relay-journal.png) |

The current procedural pass gives 35 cast members identity-specific costume palettes or visible carried gear, alongside bespoke royal designs for Edmon, Alisande, and Vaelthira. In the live Library, Inessa carries a scroll while Oren wears a distinct scholar coat; Mara's Market sprite uses another field-record variant. Other areas still need an in-game cast review.

![Live Library scene showing distinct Inessa and Oren world avatars](screenshots/supporting-cast-library-live.png)

The latest avatar pass gives Scholar Inessa a scholar's stole and route folio, Scout Tessa a feathered hood and quiver, Waywarden Saren a marshal mantle and relay spear, and the Lost Wayfarer a weather cloak and lantern. Their 9-direction walk and idle BAMs are rebuilt with the game pack; the Library capture shows Inessa loaded in GemRB.

![Scholar Inessa's updated world avatar in the live Library scene](screenshots/inessa-avatar-library-rebuilt.png)

The supporting cast now has eight more named sprite designs: Dorian's silver-bearded seer regalia, Lorian's broad guardian mantle and shield, Ilya's rust trail scarf and quiver, Pell's dispatch tube and courier sash, Fen's hunter hat and fur collar, Sella's waystone charms and marker staff, Doma's stoneworking apron and tools, and Eren's courier pack and rope coil. The generated reference sheets are visual guidance; all eight designs were translated into animated world sprites and included in the rebuilt game pack. Live scene-scale review is still pending.

The latest readability pass gives Scout Tessa a blue-green cloak, rust signal marker, high hood, and dark quiver so she stands apart from other Mistwood travelers. All 36 directional frames were rerendered and the rebuilt pack was opened directly in Mistwood; GemRB shows Tessa's new colors in the scene. The Lost Wayfarer's sprite currently needs a separate live palette investigation before the Mistwood cast review is complete.

![Generated concept sheet guiding Dorian, Lorian, Ilya, and Pell's distinct world-avatar designs](art/reference/supporting-cast-avatar-concepts.png)

![Generated concept sheet guiding Fen, Sella, Doma, and Eren's Mistwood-route avatar designs](art/reference/mistwood-route-cast-concepts.png)

Four generated portrait sheets now provide medium and small GemRB portrait resources for all thirty-eight unique named NPCs across the seven-act cast. These dialogue portraits are separate from the animated world sprites. Portraits are selected by NPC data and appear beside their dialogue. The latest sheet adds distinct portraits for twelve previously unpictured characters.

![Twelve new Terralum NPC portrait concepts for the complete cast](art/character_portraits_sheet_4.png)

The Lost Wayfarer's native actor dialogue now runs in GemRB. This isolated capture shows the private-account outcome recorded in the Act II Journal.

![Mistwood Wayfarer's native dialogue outcome in the Act II Journal](screenshots/wayfarer-native-dialogue-journal.png)

## AI and human contributor baseline

Read [GOLD_STANDARD_GAME_DESIGN_PIPELINE.md](GOLD_STANDARD_GAME_DESIGN_PIPELINE.md) before authoring or implementing Terralum content. It defines the canon rules, BG2-informed design principles, production gates, and per-scene acceptance checklist. Use the repo-root [TODO.md](../TODO.md) for current status and [LEARNINGS.md](../LEARNINGS.md) for verified engineering findings. The baseline is also exposed through the `terralum_get_design_standard` MCP tool.

## Story basis

The local campaign archive `C:\Users\goyan\Documents\GolemDungeon - kingdoms - kingdom-alsperia [1203075571572154459].txt` supports the early scroll quest. The user-supplied `TERRALUM_LORE_CODEX.md` supports the later Wizard King, eastern academy, Tear of Chaos, Archives and Eldrador arc. The user clarified that in the early period Queen Alisande was married to King Edmon. The sources do not recover the later transition to Algoreth's reign and marriage, so the game leaves that interval unwritten. See [`lore_notes.md`](lore_notes.md) for provenance and uncertainties. Neither source archive is copied into this repository.

story.json contains twenty-five scene introductions and 63 story beats; story and cast data define thirty-three one-time journal events and 58 authored response options across twenty-two scenes. The opening Market conversation now has two stages: Mara asks whether Inessa should receive a separate copy of the landmarks or the ledger should remain sealed for court review. The decision is journaled once and changes Scholar Inessa's dialogue in the Library. The new Waywarden Relay follows the Ruined Watchpost before the Lorian approach. After Lorian, the campaign revisits the watchpost under its own area resref, with Courier Pell and Waywarden Saren carrying forward patrol and ambush state. Keeper Orla asks whether to call the west patrol or leave the signal dark; Waywarden Saren acknowledges whether Leora's schedule was copied, and the choice is journaled. The areas include Alsperia Market, Library, Royal Dispatch Archive, and Royal Stables; the Mistwood Hunter's Camp, River Crossing, Three-Cairn Fork, Road, Watchpost, and Waywarden Relay; Lorian Cavern and its seal gallery; the return court and council; the academy courtyard, Containment Annex, and vault; the Deep Archives and Index Hall; Alsperia Skyport, the Expedition Chart Room, and the Aethercraft Hangar; and Eldrador's Arrival Quay and Lower Sanctuary Threshold. scene_cast.json defines 62 named scene actors and binds the 38 unique named identities to generated custom world-sprite sets. The live Market capture confirms Mara, Edmon, and Alisande render with their assigned sprites; a click-to-move check confirms the party can cross the Market courtyard. Review movement and actors in the other areas in GemRB. Each area spawns its own cast. Most NPC conversations still use the custom Talk cycle and panel choices; flags affect later dialogue or route text. Alistair’s Chart Room and Hangar actors are bound to a native DLG resource with topic choices and four state-specific Hangar responses; isolated GemRB testing now confirms actor click-to-talk opens Queen Alisande's DLG and one response advances; other DLG actors, branches, and save/load still need playtesting. At the Royal Dispatch Archive, Archivist Leora offers a choice to copy or preserve Edmon’s west-road patrol schedule; the journaled copy makes the Waywarden diversion reliable at the Mistwood ambush. At the Royal Stables, Stablemaster Edda offers a lantern or rope kit; the choice changes which Mistwood bypass is safe and is acknowledged at camp. At Hunter's Camp, Scout Tessa chooses whether to light the lantern, and Ranger Ilya can reveal a creekside path that safely bypasses the ambush while keeping the camp dark. On Mistwood Road, the Lost Wayfarer lets Algoreth send Pell an anonymous warning about an answering voice or keep the account private; Pell later reflects that choice without explaining the sound. At Mistwood’s river crossing, Maelin and Eren offer a rope handline or an exposed stepping-stone route; only the prepared rope kit makes the downstream stalker bypass safe, and Eren reports the outcome at the watchpost. At the Three-Cairn Fork, Waykeeper Sella and Carver Doma disagree over a storm-turned waystone; the player's choice changes their later account at the watchpost. In Lorian, Algoreth must answer Dorian's question about the scrolls' purpose before facing the Guardian; the journal records his answer and the Guardian responds to it. In the Seal Gallery, the answer to the inscription is required, journaled, and changes Queen Alisande's return-court response. In the academy Containment Annex, Warden Celene offers a measured boundary or purpose rule; the journal records the choice, Magister Vael acknowledges it in the vault, and the selected approach changes the sealing narration while the false self remains contained. The vault battle has two phases: a ward shard reveals the named False Algoreth actor, who responds to both prior warding choices across four combinations. The seal is journaled only after both phases. If the party falls, reload a pre-fight save; live defeat and reload behavior remain unverified. In the Deep Archives, Archivist Nera offers a peaceful or combat route to consult the Index Warden; victory records the recovered comparison leaf, and Selene and Ealdrin respond to the choice in Index Hall. Selene now identifies the source only as a titleless living record with an unknown speaker. If the player keeps the account sealed, a required follow-up asks which bounded question Ealdrin should carry to Eldrador; the answer changes Queen Vaelthira's welcome without turning the record into a witness. In Act IV, Royal Scribe Oren asks Algoreth whether to place Dorian's route testimony beside the scroll account or file them separately; the required choice is journaled and changes Queen Alisande's response without inventing what the scrolls mean. At the Expedition Chart Room, Algoreth chooses whether to carry Selene's marked archive copy or Ealdrin's questions for Eldrador's warders. The required choice is journaled and changes Flight Marshal Aven's hangar dialogue. The Eldrador Landing Quay adds a choice between collecting warder testimony or copying measured seal records; Vaelthira acknowledges it at the Lower Sanctuary Threshold. There, Algoreth chooses whether to approach the outer ring or remain back while Seraphina listens. The endpoint remains before the sealed inner gate, leaving the Tear unresolved. All twenty-five scenes have custom data-authored searchmaps with connected starts, scene casts, encounter positions, routes, and blocked features. The Mistwood ambush spawns two authored foes on connected road positions; the Lorian Guardian waits beside the chest and becomes hostile in place. Click-to-move and camera follow are live-verified in Alsperia Market; movement, collision, and exits still need checks in the other areas. All areas still inherit the demo WED geometry. The custom panel's JOURNAL button or `j` shortcut opens saved GemRB journal entries. Queen Alisande's response and both of Mara's ledger branches have been live-tested in isolated GemRB; the Journal shows the Act I quest and Mara's decision. Broader transitions, other NPCs, and save/load still need input testing. This is an expanded playable slice, not a full-length RPG campaign.

scene_production_plan.md tracks the BG2-inspired delivery slices. campaign_plan.md maps the seven acts to a longer quest and location plan, with archive facts separated from new material. The preserved story_scrolls_draft.json records the earlier game draft before the codex arrived; it is not the active campaign.

## Save and load

The game panel has **SAVE** and **LOAD** controls. SAVE creates a named snapshot based on the current scene. LOAD lists saved games in pages, asks before replacing unsaved progress, and restores the selected game. This uses GemRB's native save-game APIs with a custom in-panel UI because the open demo pack does not include the stock save/load window resources.

![Terralum showing a successful named save in the game panel](screenshots/save-load-saved.png)

![Terralum after loading back into the saved Market scene](screenshots/save-load-restored.png)

## Build and play

Native Infinity Engine DLG conversations currently cover Archivist Mara, King Edmon, and Queen Alisande in the opening scene, the Lost Wayfarer on Mistwood Road, Royal Scribe Oren in the council, and Alistair in the Chart Room and Hangar. The Wayfarer's anonymous-warning and private-account choices use the same campaign and one-time journal flags as the campaign panel; Courier Pell's later callback reads those outcomes. Both native branches and the private branch's Act II Journal entry have been live-verified in an isolated GemRB session. Mara's and Oren's two-stage DLGs likewise set shared campaign globals and journal entries that affect later NPC dialogue. At the council, Captain Rovan’s one-time open-road/restricted-scroll policy is journaled. Courier Pell offers an optional public-warning or crown-restricted deposition; both interaction surfaces journal the selected record, and Queen Alisande’s later council response combines Pell’s decision with Oren’s paired/separate docket choice. Edmon and Alisande's return-court DLG entry states combine the public/archive route choice with the resolved/open Lorian gallery warning; Alisande’s twelve council responses combine Rovan’s policy, Pell’s deposition, and Oren’s docket outcomes. Other authored NPC choices still use the campaign panel. DLG resources are compiled with `dialog.tlk` strings and checked by `test_native_dialogues.py`; Queen Alisande's actor click-to-talk and one response are verified in isolated GemRB. Archivist Mara's two-stage native conversation, both ledger outcomes, and the Act I journal entry are live-verified. Named save creation and loading the saved scene back into GemRB are live-verified; later campaign choices and pending dialogue state still need persistence checks. Other NPCs remain to be tested.

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

### NPC world-avatar pipeline

The preferred art direction for named NPCs is a hand-painted 2D fantasy sprite, with realistic proportions and readable costume details at the game's map scale. Eleven cast members currently have transparent 3×3 turnaround sources and imported directional idle frames in [`art/reference/painted_turnarounds/`](art/reference/painted_turnarounds/README.md). `import_painted_turnaround.py` crops nine views into GemRB's 80×96 frame slots; its current prototype repeats each idle view across the four walk-frame slots, so authored locomotion remains open work.

`build_npc_bams.py` compiles walk, ready, and awake BAMs, and `build_game.py` binds each character through unique CRE resources and `avatars.2da` rows. The remaining cast still uses frames rendered by `render_cast_sprites.py` from procedural Blender models; these are placeholders pending painted sources. Review all visible NPCs in each scene, since changing only the named speaker leaves blocky supporting characters beside the new art. With Blender available, regenerate missing placeholder frames and the contact sheet with:

```powershell
python tools/terralum/render_cast_sprites.py --blender path\to\blender.exe
```

Use `--force` to rerender all characters after changing the model script. Rebuild the pack afterward. The source models are authored in the Blender script; no third-party character meshes are used. The opening cast now has targeted silhouettes: scholars wear trousered coats and carry books, Edmon's royal mantle is crimson and gold, and the queens use distinct crowned gowns. The remaining named cast still needs review in live scenes.

The last command uses the WSL build in this checkout. On Windows with a native GemRB build, use `terralum/build/terralum.cfg`. `terralum/play.ps1` builds and launches through WSL and stops if another GemRB process is already running, preventing ambiguous duplicate game windows. The assembled pack under `terralum/build/` is ignored by Git.

If a running GemRB session has the standard pack open, set `TERRALUM_GAME_OUTPUT` to an isolated output folder before running `build_game.py` and `test_native_dialogues.py`. The builder places the matching Windows and WSL config files next to that pack and leaves the normal launch config untouched.

The twenty-five scene-entry narration clips under `terralum/audio/` were rendered locally with Kokoro ONNX using the `af_heart` woman voice. Narration plays when each scene begins and can be replayed with **NARRATE**. To regenerate them, use the standalone Kokoro Python environment and provide local model and voice files:

```powershell
python tools/terralum/render_audio.py --model path\to\kokoro-v1.0.onnx --voices path\to\voices-v1.0.bin --missing-only
```

The audio renderer also creates three original looping ambient tracks. It needs `kokoro_onnx`, `numpy`, `soundfile`, and `ffmpeg`. The model files are not included in the repository. Use `--missing-only` to add new scene narration without changing existing performances; omit it to regenerate all narration and ambient tracks. Narration plays on scene entry and through the **NARRATE** button. The area song table selects city, woodland, or cavern ambience.

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

GemRB and the inherited demo data have their own licenses; consult [`REUSE.toml`](../REUSE.toml) and [`demo/README.md`](../demo/README.md) before distribution. The generated world sprites, backdrop images, narration clips, and music are offered as CC0-1.0. The authoring code is GPL-2.0-or-later.
