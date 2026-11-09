# Terralum game status and handoff

This is the current work ledger for human and AI contributors. Read [AGENTS.md](AGENTS.md), the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md), and [LEARNINGS.md](LEARNINGS.md) before continuing. Update this file when work changes status. Do not move an item to **Done** based on intent or a passing mock alone; follow the evidence rule below.

## Done

- [x] Researched *Baldur's Gate II*'s documented area pipeline, design guidelines, writing/technical-design collaboration, area density, and QA lessons; captured cited sources in the gold-standard baseline.
- [x] Added `terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md` with canon rules, production gates, scene acceptance criteria, and current-state gaps.
- [x] Added repo-level `AGENTS.md` instructions that direct AI and human game contributors to the baseline and lore notes.
- [x] Exposed the full baseline through the read-only `terralum_get_design_standard` MCP tool.
- [x] Built a 16-scene campaign slice across the seven-act spine, adding the Mistwood Hunter's Camp and Three-Cairn Fork before the road and watchpost. Story provenance and uncertainties are noted in `terralum/lore_notes.md`.
- [x] Added 15 distinct generated backdrops for the 16 scene resources (one is reused), seven act-entry Kokoro narration clips, and three looping ambient music tracks.
- [x] Added 34 named, scene-specific NPC actors across 16 areas; added Talk, Narrate, Continue, and numbered-response keyboard shortcuts alongside visible controls. Current sprites reuse two demo templates.
- [x] Completed structured role, faction, goal, knowledge, voice, and provenance sheets for all 34 NPC cast entries; pack validation now rejects entries missing this design context.
- [x] Added a victory gate to each of the three prototype encounters.
- [x] Fixed the ARE builder counts: it now preserves the demo entrances and clears actor, region, spawn, container, item, and door counts that belonged to the demo.
- [x] Campaign-flow mock reports 16 scene casts, 34 actors, keyboard controls, all 22 authored response options, three market routes, three encounter gates, fifteen area transitions, and seven voice cues.
- [x] Added ten one-time story-beat journal events and an optional persistent Hunter's Camp creekside clue, including the active/resolved camp objective; the Journal panel uses GemRB's persistent journal API.
- [x] Added Ranger Ilya's optional creekside conversation and stateful route around the Mistwood stalker; the dialogue journal event is deduplicated on repeat interaction, and the campaign mock tests the dark-lantern branch through Dorian's inscription.
- [x] Added the Three-Cairn Fork as an adaptation scene with two named waykeepers, a two-outcome marker decision, a journaled route discovery, and changed dialogue at the Ruined Watchpost.
- [x] Authored and connectivity-checked a second custom `SR.BMP` for the Three-Cairn Fork; the player start, both NPCs, three path branches, and blocked stone/terrain footprints are covered by the map check.
- [x] Expanded Act II with a Mistwood Hunter's Camp, two adaptation NPCs, a lantern choice, active and resolved journal events, and a quiet-trail route that can bypass the later stalker ambush.
- [x] Fixed the safe-route skip to continue into Dorian's inscription beat, show route-specific text, and resolve the camp objective once in the journal.
- [x] Authored the Hunter's Camp's first scene-specific `SR.BMP`: a connected clearing and trails, blocked shelter/cart/firepit/rock footprints, and reachable start/NPC positions. The map is declared in `terralum/area_searchmaps.json` and built from GemRB's indexed searchmap template.
- [x] Added Ranger Ilya's optional creekside investigation. Reading the tracks adds a deduplicated journal note and safely bypasses the Mistwood stalker even if the lantern remains dark; the campaign mock covers the dialogue, journal, revisit, route, and encounter outcome.
- [x] Built and launched the WSL GemRB pack with direct startup. The opening scene shows three NPCs beside the player; live startup loaded actors and city ambience with no Python traceback.
- [x] Fork remote `goyanx/gemrb` and branch `terralum-first-slice` are configured; each accepted slice is committed, commented on, and pushed as shown in branch history.

## Ongoing

- [ ] **Scene dialogue slice:** Market, library, watchpost, seal gallery, council, academy courtyard, archive index, and hangar choices set persistent flags with later text outcomes. The logic is mock-tested; live input/save testing remains open. The custom choice UI is not a native GemRB DLG system.
- [ ] **Journal verification:** eleven event flags, including the waystone discovery and optional creekside clue, plus revisit deduplication, pass the script mock; live display and save/load still need direct playtesting.
- [ ] **Playable-scene verification:** the extended pack builds and the opening area starts in live GemRB. Both custom Mistwood maps pass script connectivity checks, but live movement is unverified. The WSLg window input path has not yet been verified. Later-area entry, player movement, actual fights, choice input, save/load, and return entry still need direct playtesting.
- [ ] **Art and geometry:** characters currently reuse the demo's two humanoid sprites. Hunter's Camp and the Three-Cairn Fork now have custom searchmaps, but all 16 areas still inherit the AR0100 WED layout and terrain/height/light files; the other 14 also use its generic searchmap. Both custom maps pass connectivity checks, while actual in-engine movement remains unverified.
- [ ] **Campaign length:** 16 locations and 41 beats form an expanded prototype, not a long-form campaign. Act II now has a side scene about the trail marker; Acts VI and VII have archive-index and hangar preparation locations. Deeper quest arcs remain; see `terralum/campaign_plan.md`.

## To do, in priority order

### P0 — Make one scene a real RPG conversation

- [ ] Playtest the Alsperia Market conversation buttons in live GemRB and confirm choices persist after save/load.
- [ ] Deepen the current one-turn choice scenes with gated topics, multi-step conversations, and journal effects; live-test each branch.
- [x] Give the market quest a readable persistent journal entry; robust failure/skip paths beyond the current route and ambush outcomes remain open.
- [x] Added MCP tools to inspect scene casts, add or replace richly specified NPCs, and register dialogue flags; malformed cast data is rejected before it is written.
- [ ] Test the dialogue and state changes in live GemRB, including save/load and repeat area entry; retain the current mock as a fast logic check.

### P1 — Make every scene coherent and navigable

- [ ] Extend the two custom searchmaps to the remaining 14 areas; replace shared WED geometry, entrances, terrain/height/light maps, and prove party movement in every scene.
- [x] Add a focused searchmap check for dimensions/palette, blocked camp props, and four-way connectivity from the party start to both NPCs and the north/south trails.
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
