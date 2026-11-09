# Terralum game status and handoff

This is the current work ledger for human and AI contributors. Read [AGENTS.md](AGENTS.md), the [Gold Standard Game Design Pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md), and [LEARNINGS.md](LEARNINGS.md) before continuing. Update this file when work changes status. Do not move an item to **Done** based on intent or a passing mock alone; follow the evidence rule below.

## Done

- [x] Added lore-grounded Alistair to the Act VII Chart Room and Aethercraft Hangar. The recurring engineer's hangar dialogue reflects all four combinations of the archive-carrying and voyage-preparation choices; the pack and MCP authoring tools now validate multi-flag `when` conditions.
- [x] Added Alistair's native Infinity Engine DLG pilot: chart-room topics and four condition-selected Hangar entries compile to a DLG state machine with appended TLK strings, and spawned actors receive the dialogue resource. MCP tools can read and upsert DLG source. Resource table and string-reference checks pass; direct in-engine click-to-talk remains unverified.
- [x] Researched *Baldur's Gate II*'s documented area pipeline, design guidelines, writing/technical-design collaboration, area density, and QA lessons; captured cited sources in the gold-standard baseline.
- [x] Added `terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md` with canon rules, production gates, scene acceptance criteria, and current-state gaps.
- [x] Added repo-level `AGENTS.md` instructions that direct AI and human game contributors to the baseline and lore notes.
- [x] Exposed the full baseline through the read-only `terralum_get_design_standard` MCP tool.
- [x] Built a 25-scene campaign slice across the seven-act spine, including an Act III return to the Mistwood Watchpost, adding the Royal Dispatch Archive and Royal Stables in Act I, the Mistwood Hunter's Camp and Three-Cairn Fork in Act II, the Academy Containment Annex in Act V, and an Eldrador landing and threshold investigation in Act VII. Story provenance and uncertainties are noted in `terralum/lore_notes.md`.
- [x] Added 23 distinct generated backdrops for 25 scene resources; Deep Archives and the returning Watchpost reuse their existing location art, seven act-entry Kokoro narration clips, and three looping ambient music tracks.
- [x] Added 60 named, scene-specific NPC placements across 25 areas; added Talk, Narrate, Continue, and numbered-response keyboard shortcuts alongside visible controls. Current sprites reuse two demo templates.
- [x] Completed structured role, faction, goal, knowledge, voice, and provenance sheets for all 60 NPC cast entries; pack validation now rejects entries missing this design context.
- [x] Added a victory gate to each of the four prototype encounters.
- [x] Expanded the Mistwood Road gate into a two-foe authored encounter group; each enemy has its own connected spawn point and persistent actor flag, and the campaign mock verifies both attack orders and the group victory gate.
- [x] Made the Mistwood fight's victory persist as a resolved journal event and changed Courier Pell's watchpost response when both road creatures are defeated.
- [x] Added Act VI's optional Deep Archive Warden quest: Archivist Nera can leave the folio sealed or call the Warden, with a connected encounter position, victory journal entry, and Index Hall dialogue that preserves both outcomes.
- [x] Added Act VII's Expedition Chart Room between the Eldrador invitation and the hangar: Ealdrin offers a required choice between Selene's marked account copy and witness notes, records it in the journal, and carries it into Flight Marshal Aven's changed hangar dialogue. Added generated location art, a connected custom searchmap, and three authored NPC placements.
- [x] Added Act V's Eastern Academy Containment Annex between the courtyard and vault. Celene's required form-or-purpose choice is journaled, changes Vael's vault dialogue and the sealing narration, and preserves the established contained-echo outcome. Added generated location concept art, connected custom searchmap, and two authored NPC placements.
- [x] Extended Act VII beyond the Aethercraft departure with the Eldrador Landing Quay and Lower Sanctuary Threshold. Vaelthira offers a choice between witness accounts and measured seal records; the selected evidence changes her threshold dialogue. The party then chooses a cautious outer-ring protocol. Both events are journaled, the scenes have five NPC placements and connected custom maps, and the campaign stops before the Tear is entered or resolved.
- [x] Added an Act III return to the Mistwood Watchpost after Lorian. Courier Pell and Waywarden Saren respond to the earlier patrol and ambush choices; Pell’s required route-record choice changes Queen Alisande’s court dialogue and is written once to the journal. The revisit uses the existing watchpost art and connected map.
- [x] Prevented NPC decision choices from reopening after their shared campaign flag is set, so repeated Talk interactions cannot overwrite a branch while its one-time journal entry remains unchanged. The return-Watchpost flow test revisits Pell after each outcome and confirms the choices stay closed.
- [x] Added the Mistwood Waywarden Relay after the Ruined Watchpost. Orla offers a required patrol-or-silence choice with one shared journal event; Saren uses Leora's dispatch schedule only if the party copied it. Added original concept art and a connected three-approach searchmap.
- [x] Added an Act IV evidence-docket quest with Royal Scribe Oren. A required two-stage conversation decides whether Dorian's route testimony sits beside the scroll account or remains separate; one journal event records the decision, Alisande responds to it, and the player cannot leave the hearing unfinished. Both branches pass the campaign-flow mock; a custom connected `SR.BMP` includes the party start, three council NPCs, and north/south approaches.
- [x] Fixed the ARE builder counts: it now preserves the demo entrances and clears actor, region, spawn, container, item, and door counts that belonged to the demo.
- [x] Campaign-flow mock reports 25 scene casts, 60 actor placements, keyboard controls, all 52 authored response options, three market routes, four encounter gates, five hostile actors across those encounters, twenty-four area transitions, and seven voice cues.
- [x] Expanded the MCP journal authoring tool to cover all 25 scenes and attach journal events to encounter victories; its test covers late-act authoring, victory hooks, and duplicate-flag rejection.
- [x] Added campaign journal entries for story beats and dialogue choices, plus the active/resolved Hunter's Camp objective; entries use GemRB's persistent journal API and are guarded against duplicate records.
- [x] Added Ranger Ilya's optional creekside conversation and stateful route around the Mistwood stalker; the dialogue journal event is deduplicated on repeat interaction, and the campaign mock tests the dark-lantern branch through Dorian's inscription.
- [x] Added the Three-Cairn Fork as an adaptation scene with two named waykeepers, a two-outcome marker decision, a journaled route discovery, and changed dialogue at the Ruined Watchpost.
- [x] Added a required three-option purpose conversation with Dorian in Lorian; it records the answer in the journal and changes the Guardian's response. The campaign mock covers all answers and verifies the player cannot skip the conversation to start the encounter.
- [x] Authored and connectivity-checked a fifth custom `SR.BMP` for Lorian Cavern; the party, Dorian, Guardian, western arch, scroll chest approach, and authored Guardian spawn connect across the plaza.
- [x] Added Mistwood River Crossing between Hunter’s Camp and the Three-Cairn Fork. Fordkeeper Maelin and Courier Eren resolve a handline-or-ford choice; only the rope kit unlocks the quiet stalker bypass, and Eren carries the outcome to the watchpost. The scene has journal state, original art, and a connected searchmap.
- [x] Added the Alsperia Royal Dispatch Archive as an Act I scene with Archivist Leora and Page Nerin, a required copy-or-seal patrol schedule choice, a journal event, a custom connected searchmap, and a reliable Waywarden diversion at Mistwood when the schedule is copied.
- [x] Added Alsperia Royal Stables as an Act I scene with two scene NPCs, a required lantern-or-rope kit choice, a journal event, a custom connected searchmap, and matching kit consequences for later Mistwood bypass routes.
- [x] Made the Seal Gallery inscription a required two-outcome scene event: restraint resolves the warning, while demanding passage leaves it open; both outcomes persist to the journal and change Queen Alisande's return-court response. Added and connectivity-checked a custom `SR.BMP` for the gallery hall and its three approaches.
- [x] Authored and connectivity-checked a second custom `SR.BMP` for the Three-Cairn Fork; the player start, both NPCs, three path branches, and blocked stone/terrain footprints are covered by the map check.
- [x] Authored and connectivity-checked a third custom `SR.BMP` for Mistwood Road; the player start, both scene NPCs, stalker spawn, southern approach, northbound road, and blocked terrain footprints are covered by the map check. The encounter now spawns at its authored world coordinate.
- [x] Authored and connectivity-checked a fourth custom `SR.BMP` for the Ruined Watchpost; the party, Courier Pell, Waywarden Saren, plaza, southern road, north arch, and blocked perimeter ruins are covered by the map check.
- [x] Expanded Act II with a Mistwood Hunter's Camp, two adaptation NPCs, a lantern choice, active and resolved journal events, and a quiet-trail route that can bypass the later stalker ambush.
- [x] Fixed the safe-route skip to continue into Dorian's inscription beat, show route-specific text, and resolve the camp objective once in the journal.
- [x] Authored the Hunter's Camp's first scene-specific `SR.BMP`: a connected clearing and trails, blocked shelter/cart/firepit/rock footprints, and reachable start/NPC positions. The map is declared in `terralum/area_searchmaps.json` and built from GemRB's indexed searchmap template.
- [x] Added Ranger Ilya's optional creekside investigation. Reading the tracks adds a deduplicated journal note and safely bypasses the Mistwood stalker even if the lantern remains dark; the campaign mock covers the dialogue, journal, revisit, route, and encounter outcome.
- [x] Built and launched the WSL GemRB pack with direct startup. The opening scene shows three NPCs beside the player; live startup loaded actors and city ambience with no Python traceback.
- [x] Fork remote `goyanx/gemrb` and branch `terralum-first-slice` are configured; each accepted slice is committed, commented on, and pushed as shown in branch history.

## Ongoing

- [ ] **Scene dialogue slice:** Market, library, Royal Dispatch Archive, Royal Stables, River Crossing, Watchpost and return, Waywarden Relay, Lorian purpose test, seal gallery, Deep Archives, council, academy courtyard, Index Hall, Expedition Chart Room, hangar, Eldrador Landing Quay, and Lower Sanctuary Threshold choices set persistent flags with later text outcomes. Alistair's DLG is a one-NPC native pilot; most other scenes still use the custom panel. Direct click-to-talk, journal integration, branch persistence, and save/load need live testing before broadening the native DLG migration.
- [ ] **Journal verification:** twenty-six event flags, including the Act III return-road record, Act IV evidence docket, academy warding decision, Eldrador evidence/protocol choices, and conditional Mistwood and Deep Archive encounter victories, pass script mocks; live display and save/load still need direct playtesting.
- [ ] **Playable-scene verification:** the extended pack builds and GemRB starts against it. All 25 custom maps pass script connectivity checks, but movement is unverified. The current WSL session has two GemRB processes and the desktop is locked, so no UI input was sent; `terralum/play.ps1` now refuses to add another instance. Later-area entry, player movement, actual fights, choice input, save/load, and return entry still need direct playtesting after unlocking the desktop and closing one session.
- [ ] **Art and geometry:** Characters currently reuse the demo's two humanoid sprites. All 25 named scenes now have custom searchmaps, but every area still inherits the AR0100 WED layout and terrain/height/light files. Actual in-engine movement remains unverified.
- [ ] **Campaign length:** 25 locations and 63 beats form an expanded prototype, not a long-form campaign. Act I/II add trail, courier, route-record, and Waywarden Relay quests; Act III adds a returning Watchpost scene with route-preservation consequences; Act IV now has an evidence docket; Act V adds a warding choice; Act VI adds an optional Index Warden challenge; Act VII covers departure, Eldrador evidence gathering, and a cautious sanctuary approach while leaving the Tear unresolved. Deeper quest arcs remain; see `terralum/campaign_plan.md`.

## To do, in priority order

### P0 — Make one scene a real RPG conversation

- [ ] Playtest the Alsperia Market conversation buttons in live GemRB and confirm choices persist after save/load.
- [x] Added a two-stage Market ledger conversation with a required follow-up choice, one shared journal event, and later Library callbacks for both outcomes; mock-tested both branches.
- [x] Persisted the pending conversation's NPC and topic indexes in campaign globals and restore its required choice when the game script reloads; the flow mock simulates reloads before and after both outcomes.
- [ ] Live-test both Market follow-up branches in GemRB and confirm journal/dialogue state survives an actual save/load. Other one-turn choice scenes still need deeper topics.
- [x] Give the market quest a readable persistent journal entry; robust failure/skip paths beyond the current route and ambush outcomes remain open.
- [x] Added MCP tools to inspect scene casts, add or replace richly specified NPCs, and register dialogue flags; malformed cast data is rejected before it is written.
- [ ] Test the dialogue and state changes in live GemRB, including save/load and repeat area entry; retain the current mock as a fast logic check.

### P1 — Make every scene coherent and navigable

- [x] Added and connectivity-checked custom searchmaps for all 25 scenes, including the Market, Court, Observatory Vault, Skyport, Library, Academy Courtyard, Index Hall, and Hangar.
- [ ] Replace shared WED geometry, entrances, terrain/height/light maps, and prove party movement in every scene.
- [x] Add focused searchmap checks for dimensions/palette, blocked terrain and props, and four-way connectivity from the party start to scene NPCs, encounter spawns, and exits.
- [ ] Replace repeated placeholder NPC models with unique/generated or compatible open-licensed art and portraits. Keep provenance and license records.
- [ ] Place actual interactable clues, containers, doors, and travel links only where they match the new scene geometry.
- [ ] Turn encounters into fully authored tactical events with clues, distinct enemy behavior and art, balance, failure outcomes, and quest-state effects. Mistwood now has a connected two-foe ambush with persistent actor IDs and a group victory gate; live combat and balance remain unverified.
- [ ] Review all 60 cast sheets against live scenes; deepen return-state dialogue and recurring NPC continuity where appropriate.

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
