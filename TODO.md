# Terralum game status and handoff

This is the current work ledger for human and AI contributors. Read [AGENTS.md](AGENTS.md), the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md), and [LEARNINGS.md](LEARNINGS.md) before continuing. Update this file when work changes status. Do not move an item to **Done** based on intent or a passing mock alone; follow the evidence rule below.

## Done

- [x] Researched *Baldur's Gate II*'s documented area pipeline, design guidelines, writing/technical-design collaboration, area density, and QA lessons; captured cited sources in the gold-standard baseline.
- [x] Added `terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md` with canon rules, production gates, scene acceptance criteria, and current-state gaps.
- [x] Added repo-level `AGENTS.md` instructions that direct AI and human game contributors to the baseline and lore notes.
- [x] Exposed the full baseline through the read-only `terralum_get_design_standard` MCP tool.
- [x] Built a 12-scene campaign slice across the seven-act spine: the opening court and library, Mistwood road and watchpost, Lorian cavern and seal gallery, return court and council, academy courtyard and Tear vault, Deep Archives, and the Eldrador expedition departure. Story provenance and uncertainties are noted in `terralum/lore_notes.md`.
- [x] Added generated backdrops for the 12 scene resources (some reuse a previously generated image), seven act-entry Kokoro narration clips, and three looping ambient music tracks.
- [x] Added 25 named, scene-specific NPC actors across 12 areas; added Talk, Narrate, Continue, and numbered-response keyboard shortcuts alongside visible controls. Current sprites reuse two demo templates.
- [x] Added a victory gate to each of the three prototype encounters.
- [x] Fixed the ARE builder counts: it now preserves the demo entrances and clears actor, region, spawn, container, item, and door counts that belonged to the demo.
- [x] Campaign-flow mock reports 12 scene casts, 25 actors, keyboard controls, all 13 authored response options, three market routes, three encounter gates, eleven area transitions, and seven voice cues.
- [x] Built and launched the WSL GemRB pack with direct startup. The opening scene shows three NPCs beside the player; live startup loaded actors and city ambience with no Python traceback.
- [x] Fork remote `goyanx/gemrb` and branch `terralum-first-slice` are configured; each accepted slice is committed, commented on, and pushed as shown in branch history.

## Ongoing

- [ ] **Scene dialogue slice:** Market, library, watchpost, seal gallery, council, and academy courtyard choices set persistent flags with later text outcomes. The logic is mock-tested; live input/save testing remains open. The custom choice UI is not a native GemRB DLG system.
- [ ] **Playable-scene verification:** the extended pack builds and the opening area starts in live GemRB. The WSLg window input path has not yet been verified. Later-area entry, player movement, actual fights, choice input, save/load, and return entry still need direct playtesting.
- [ ] **Art and geometry:** characters currently reuse the demo's two humanoid sprites; all 12 areas still share the AR0100 template walkmesh and terrain files despite their distinct/reused backdrops.
- [ ] **Campaign length:** 12 locations and 33 beats form an expanded prototype, not a long-form campaign. Acts VI and VII still need side locations and quest arcs; see `terralum/campaign_plan.md`.

## To do, in priority order

### P0 — Make one scene a real RPG conversation

- [ ] Playtest the Alsperia Market conversation buttons in live GemRB and confirm choices persist after save/load.
- [ ] Extend branching conversations and durable flag effects to the remaining acts, using the market route choice as the tested pattern.
- [ ] Give the market quest a readable journal entry and robust failure/skip paths beyond the current route and ambush outcomes.
- [ ] Add scene-cast data authoring and validation to the MCP tools so coders can safely create/update NPCs and dialogue.
- [ ] Test the dialogue and state changes in live GemRB, including save/load and repeat area entry; retain the current mock as a fast logic check.

### P1 — Make every scene coherent and navigable

- [ ] Author area-specific walkability, clipping, entrances, and search maps; replace the shared demo geometry and prove party movement through the scene.
- [ ] Replace repeated placeholder NPC models with unique/generated or compatible open-licensed art and portraits. Keep provenance and license records.
- [ ] Place actual interactable clues, containers, doors, and travel links only where they match the new scene geometry.
- [ ] Turn encounters into authored tactical events with clues, sensible placement, AI, balance, victory/failure outcomes, and quest-state effects.
- [ ] Review all 25 NPCs for canonical/adaptation labels, motivation, scene role, and later continuity; add return-state dialogue where appropriate.

### P2 — Expand the campaign

- [ ] Expand Acts VI and VII into connected subareas; deepen all acts with side quests, NPC arcs, puzzles, and authored battles, following `campaign_plan.md` without claiming BG2's playtime or copying its content.
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
