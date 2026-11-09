# Terralum development learnings

This file records verified implementation findings and mistakes that should inform future work. Pair it with [TODO.md](TODO.md), [AGENTS.md](AGENTS.md), and the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md). Add a note when a new bug or workflow finding changes how contributors should build the game.

## Engine and architecture

- **GemRB is an engine/runtime, not a visual game editor.** Terralum content is assembled from Infinity Engine resources, Python GUI scripts, and game data. Use resource editors or authoring tools for area formats; use GemRB to play and verify.
- **Prefer content over engine changes for scene work.** The existing game already loads a custom chapter UI. NPCs, area transitions, music, and timed callbacks can be implemented with game resources and GUIScripts.
- **Use current local APIs as the authority.** Read the matching GemRB Python scripts/docs or local C++ API implementation before relying on a remembered Infinity Engine call. Similar engine forks can differ.

## Area resources and build errors

- **ARE headers use mixed-width counts.** In the demo area header, actor count is a 16-bit value at `0x58`, region count at `0x5A`, and spawn count is a 32-bit value at `0x64`. The field at `0x6C` is the 32-bit entrance count, not spawn count. Writing zero there silently removes entrances. Verify field offsets against the local importer and binary template before patching.
- **ARE doors must agree with WED doors.** Leaving a demo ARE door while replacing or clearing its WED counterpart causes GemRB's `Found door without WED entry!` error. Clear both sides or author a matching door; do not just rename the area resref.
- **A cloned area is not a finished scene.** The current seven backdrops reuse AR0100's walkmesh, terrain/search maps, entrances, and other geometry assumptions. It may load but art, collision, props, and routes can disagree. Make geometry and actor positions area-specific before calling a scene accepted.
- **The build pack is generated.** `terralum/build/game` is output, not source of truth. Edit `terralum/` and `gemrb/GUIScripts/terralum/`, then run `tools/terralum/build_game.py`; a rebuild removes and recreates the pack.
- **Validate content before assembling.** Build validation should check story shape, every scene's cast, known creature templates, coordinates, and referenced resources so a broken content file fails early.

## Runtime timing and NPCs

- **The message-window startup can run before a current area exists.** Calling `GemRB.ExploreArea(True)` or `GemRB.CreateCreature(...)` immediately from `MessageWindow.OnLoad` produced `RuntimeError: No current area!`. Defer area-dependent work with `GemRB.SetTimedEvent(callback, 1)` and verify the target area in the callback.
- **Make area-entry callbacks idempotent.** Save a durable scene/cast flag or inspect existing actors so area reloads and saves do not duplicate NPCs or rewards. Test both fresh entry and revisit.
- **`CreateCreature` can place a CRE at a world coordinate.** `SetPlayerName` can give the actor a display name and `SetPlayerStat(actor, IE_EA, NEUTRAL)` can make a prototype actor neutral. The current implementation uses two demo CREs, so distinct names and lines do not make their repeated silhouettes visually unique.
- **A text-panel line is not native Infinity Engine dialogue.** The current Talk control cycles lines in the campaign panel. It does not provide DLG choices, conditions, interjections, or durable quest consequences. Do not claim branching dialogue until the engine shows and persists those effects.
- **A purpose-built choice panel can prove branching quest logic before the DLG toolchain exists.** The market scene now offers three Talk responses, records a global route flag, and changes the Mistwood encounter and dialogue. This is a real stateful prototype, but still requires live button/save testing and should not be described as native DLG support.
- **Use log evidence after a live launch.** Search `GemRB.log` for `Python/ERROR`, `Traceback`, resource lookup failures, area import errors, and audio imports. A script-level mock cannot expose missing area resources or a callback firing at the wrong time.

## Testing and production workflow

- **Keep mock and live checks separate.** `tools/terralum/test_campaign_flow.py` replaces GemRB with a small test double. It verifies the modeled progression and callback contract only. It does not prove UI input, pathfinding, actor visibility, actual combat, area resources, save/load, or sound output.
- **Capture screenshots from the actual game window.** Prior WSLg automation clicks did not reliably reach the controls. Treat an image as visual evidence of the shown frame only; do not assume a button works from its appearance.
- **Rebuild after changing story/audio/resource source.** The running process keeps loaded resources. Stop it, rebuild the ignored game pack, relaunch, then inspect the new log and screen.
- **Keep lore and invention distinct.** The lore codex is a partial reconstruction and the user has corrected the early relationship: Alisande was married to Edmon, Alsperia's original king. The later chronicle names Algoreth as Wizard King with Alisande as wife/co-ruler, while the transition remains undocumented. Adaptation NPCs and dialogue must not invent missing history.
- **Use production scope gates.** BG2's postmortem describes how a stable engine/content pipeline helped focus work on content, while its team also recognized oversized scope and QA difficulty. Complete and playtest a small act slice before filling every planned area with more content.

## Tooling and portability

- **Kokoro assets are generated locally.** The ONNX model and voice files are not committed. The renderer needs explicit local model/voice paths plus `kokoro_onnx`, `numpy`, `soundfile`, and `ffmpeg`; clips can be consumed by the game without shipping the model.
- **The AI authoring server is intentionally narrow.** `terralum_get_design_standard` returns the contributor baseline; current edit tools cover campaign title, hero name, linear beats, area art, and builds. It does not yet safely author branching dialogue or NPC cast records.
- **Check status and push evidence.** The repo's approved workflow includes committing and pushing fork changes, with a GitHub commit comment. Confirm the branch and clean status before reporting completion.
