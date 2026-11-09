# Terralum game status and handoff

This is the current work ledger for human and AI contributors. Read [AGENTS.md](AGENTS.md), the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md), and [LEARNINGS.md](LEARNINGS.md) before continuing. Update this file when work changes status. Do not move an item to **Done** based on intent or a passing mock alone; follow the evidence rule below.

## Done

- [x] Researched *Baldur's Gate II*'s documented area pipeline, design guidelines, writing/technical-design collaboration, area density, and QA lessons; captured cited sources in the gold-standard baseline.
- [x] Added `terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md` with canon rules, production gates, scene acceptance criteria, and current-state gaps.
- [x] Added repo-level `AGENTS.md` instructions that direct AI and human game contributors to the baseline and lore notes.
- [x] Exposed the full baseline through the read-only `terralum_get_design_standard` MCP tool.
- [x] Built the seven-act prototype: Alsperia opening and court, Mistwood, Lorian, Eastern Academy/Tear, Deep Archives, and the Eldrador expedition departure. Story provenance and uncertainties are noted in `terralum/lore_notes.md`.
- [x] Added seven generated area backdrops, seven chapter narration clips rendered with local Kokoro `af_heart`, and three looping ambient music tracks.
- [x] Added 15 named, scene-specific NPC actors and one Talk line per NPC across seven areas; added the Talk control and timed entry spawning. Current sprites reuse two demo templates.
- [x] Added a victory gate to each of the three prototype encounters.
- [x] Fixed the ARE builder counts: it now preserves the demo entrances and clears actor, region, spawn, container, item, and door counts that belonged to the demo.
- [x] Campaign-flow mock reports seven scene casts, 15 actors, Talk interactions, three encounter gates, six area transitions, and seven voice cues.
- [x] Built and launched the WSL GemRB game pack. The opening screenshot shows three NPCs beside the player; the launch log had no Python error and no stale WED door warning.
- [x] Pushed the current work to `goyanx/gemrb`, branch `terralum-first-slice`; latest relevant commits: `9a4b313`, `857229a`, `46eec88`, `56f31c1`.

## Ongoing

- [ ] **Scene dialogue slice:** scene cast and Talk lines work, but the control cycles a single line per NPC. It is not native GemRB DLG dialogue, has no player response choices, and does not change quests or the world. This is the next implementation slice.
- [ ] **Playable-scene verification:** the campaign-flow script mocks GemRB; the game has only had an opening smoke launch and screenshot. Full live input, later-area entry, actual fights, save/load, and the Talk control still need direct playtesting.
- [ ] **Art and geometry:** characters currently reuse the demo's two humanoid sprites; all seven areas still share the AR0100 template walkmesh and terrain files despite their distinct backdrops.
- [ ] **Campaign length:** seven locations and 23 beats form a short outline, not a long-form campaign. See `terralum/campaign_plan.md` for the intended acts and additional places.

## To do, in priority order

### P0 — Make one scene a real RPG conversation

- [ ] Choose a small scene (Alsperia Market) and implement one native GemRB conversation with about three player options.
- [ ] Make choices set durable quest flags; show different follow-up dialogue based on those flags.
- [ ] Give the quest a readable clue, a meaningful event or reward, a failure/skip path, and a journal entry.
- [ ] Add scene-cast data authoring and validation to the MCP tools so coders can safely create/update NPCs and dialogue.
- [ ] Test the dialogue and state changes in live GemRB, including save/load and repeat area entry; retain the current mock as a fast logic check.

### P1 — Make every scene coherent and navigable

- [ ] Author area-specific walkability, clipping, entrances, and search maps; replace the shared demo geometry and prove party movement through the scene.
- [ ] Replace repeated placeholder NPC models with unique/generated or compatible open-licensed art and portraits. Keep provenance and license records.
- [ ] Place actual interactable clues, containers, doors, and travel links only where they match the new scene geometry.
- [ ] Turn encounters into authored tactical events with clues, sensible placement, AI, balance, victory/failure outcomes, and quest-state effects.
- [ ] Review all 15 NPCs for canonical/adaptation labels, motivation, scene role, and later continuity; add return-state dialogue where appropriate.

### P2 — Expand the campaign

- [ ] Expand each act from a single prototype area into connected subareas, side quests, NPC arcs, puzzles, and battles; follow `campaign_plan.md` without claiming BG2's playtime or copying its content.
- [ ] Build recurring core locations that visibly respond to completed quests.
- [ ] Add companion/party recruitment or another deliberate party system and scripted inter-party/world banter.
- [ ] Extend music and narrator cues as new areas and story beats are authored; verify local Kokoro output remains reproducible.
- [ ] Do not resolve Edmon's fate, the intervening reign/marriage chronology, or Eldrador's Tear without new user-confirmed source material.

### P3 — Release-quality production

- [ ] Run an end-to-end fresh-save playthrough across every area, branch, encounter, return path, and ending transition.
- [ ] Test each scene after save/load and revisit; check for duplicated NPCs, rewards, triggers, or lost quest state.
- [ ] Review build logs, pathfinding, collisions, audio levels/loops, narrator replay, UI input, subtitles, and accessibility controls.
- [ ] Update the status ledger, docs, and changelog; commit, comment on, and push each accepted slice.

## Evidence standard

An automated mock proves only the code paths modeled by that mock. A successful build proves resource assembly, not that a player can use the scene. Use live GemRB evidence for map load, actor presence, UI interaction, pathfinding, actual dialogue, encounters, and audio. Keep unverified items in **Ongoing** or **To do**.
