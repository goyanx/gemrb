# Terralum game status and handoff

This is the current work ledger for human and AI contributors. Read [AGENTS.md](AGENTS.md), the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md), and [LEARNINGS.md](LEARNINGS.md) before continuing. Update this file when work changes status. Do not move an item to **Done** based on intent or a passing mock alone; follow the evidence rule below.

## Done

- [x] Researched *Baldur's Gate II*'s documented area pipeline, design guidelines, writing/technical-design collaboration, area density, and QA lessons; captured cited sources in the gold-standard baseline.
- [x] Added `terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md` with canon rules, production gates, scene acceptance criteria, and current-state gaps.
- [x] Added repo-level `AGENTS.md` instructions that direct AI and human game contributors to the baseline and lore notes.
- [x] Exposed the full baseline through the read-only `terralum_get_design_standard` MCP tool.
- [x] Built a 15-scene campaign slice across the seven-act spine, adding the Mistwood Hunter's Camp before the road and watchpost. Story provenance and uncertainties are noted in `terralum/lore_notes.md`.
- [x] Added generated backdrops for the 15 scene resources (some reuse a previously generated image), seven act-entry Kokoro narration clips, and three looping ambient music tracks.
- [x] Added 31 named, scene-specific NPC actors across 15 areas; added Talk, Narrate, Continue, and numbered-response keyboard shortcuts alongside visible controls. Current sprites reuse two demo templates.
- [x] Completed structured role, faction, goal, knowledge, voice, and provenance sheets for all 31 NPC cast entries; pack validation now rejects entries missing this design context.
- [x] Added a victory gate to each of the three prototype encounters.
- [x] Fixed the ARE builder counts: it now preserves the demo entrances and clears actor, region, spawn, container, item, and door counts that belonged to the demo.
- [x] Campaign-flow mock reports 15 scene casts, 31 actors, keyboard controls, all 19 authored response options, three market routes, three encounter gates, fourteen area transitions, and seven voice cues.
- [x] Added nine one-time journal events across the early scroll quest and later Tear research, including an active and resolved Hunter's Camp objective, with an in-game Journal panel backed by GemRB's persistent journal API.
- [x] Expanded Act II with a Mistwood Hunter's Camp, two adaptation NPCs, a lantern choice, active and resolved journal events, and a quiet-trail route that can bypass the later stalker ambush.
- [x] Fixed the safe-route skip to continue into Dorian's inscription beat, show route-specific text, and resolve the camp objective once in the journal.
- [x] Built and launched the WSL GemRB pack with direct startup. The opening scene shows three NPCs beside the player; live startup loaded actors and city ambience with no Python traceback.
- [x] Fork remote `goyanx/gemrb` and branch `terralum-first-slice` are configured; each accepted slice is committed, commented on, and pushed as shown in branch history.

## Ongoing

- [ ] **Scene dialogue slice:** Market, library, watchpost, seal gallery, council, academy courtyard, archive index, and hangar choices set persistent flags with later text outcomes. The logic is mock-tested; live input/save testing remains open. The custom choice UI is not a native GemRB DLG system.
- [ ] **Journal verification:** the log panel and nine event flags pass the script mock; live display, save/load, and revisit deduplication still need direct playtesting.
- [ ] **Playable-scene verification:** the extended pack builds and the opening area starts in live GemRB. The new Hunter's Camp path has only script-level verification so far. The WSLg window input path has not yet been verified. Later-area entry, player movement, actual fights, choice input, save/load, and return entry still need direct playtesting.
- [ ] **Art and geometry:** characters currently reuse the demo's two humanoid sprites; all 15 areas still share the AR0100 template walkmesh and terrain files despite their distinct/reused backdrops.
- [ ] **Campaign length:** 15 locations and 39 beats form an expanded prototype, not a long-form campaign. The Hunter's Camp adds one optional Mistwood stop; Acts VI and VII have archive-index and hangar preparation locations. Deeper quest arcs remain; see `terralum/campaign_plan.md`.

## To do, in priority order

### P0 — Make one scene a real RPG conversation

- [ ] Playtest the Alsperia Market conversation buttons in live GemRB and confirm choices persist after save/load.
- [ ] Deepen the current one-turn choice scenes with gated topics, multi-step conversations, and journal effects; live-test each branch.
- [x] Give the market quest a readable persistent journal entry; robust failure/skip paths beyond the current route and ambush outcomes remain open.
- [x] Added MCP tools to inspect scene casts, add or replace richly specified NPCs, and register dialogue flags; malformed cast data is rejected before it is written.
- [ ] Test the dialogue and state changes in live GemRB, including save/load and repeat area entry; retain the current mock as a fast logic check.

### P1 — Make every scene coherent and navigable

- [ ] Author area-specific walkability, clipping, entrances, and search maps; replace the shared demo geometry and prove party movement through the scene.
- [ ] Replace repeated placeholder NPC models with unique/generated or compatible open-licensed art and portraits. Keep provenance and license records.
- [ ] Place actual interactable clues, containers, doors, and travel links only where they match the new scene geometry.
- [ ] Turn encounters into authored tactical events with clues, sensible placement, AI, balance, victory/failure outcomes, and quest-state effects.
- [ ] Review the 31 complete cast sheets against live scenes; deepen return-state dialogue and recurring NPC continuity where appropriate.

### P2 — Expand the campaign

- [ ] Deepen all acts with side quests, NPC arcs, puzzles, and authored battles, following `campaign_plan.md` without claiming BG2's playtime or copying its content.
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
