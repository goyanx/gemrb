# Terralum Gold Standard Game Design Pipeline

**Status:** Project baseline for every human or AI contributor working on Terralum.

**Purpose:** Deliver a coherent, playable, lore-faithful Infinity Engine campaign with the area density, character presence, authored dialogue, and eventful exploration that made *Baldur's Gate II: Shadows of Amn* a useful production model. This is a production standard, not a claim that the current prototype already meets it.

## 1. How to use this standard

Read this file before changing story content, scene data, scripts, art, or area resources. Treat it as the project's acceptance criteria. If a task cannot meet a criterion, record the gap in the area brief and describe the next step; do not mark the scene complete. The current implementation status is in [README.md](README.md), the lore boundaries are in [lore_notes.md](lore_notes.md), and the seven-act roadmap is in [campaign_plan.md](campaign_plan.md).

AI contributors must:

- Inspect current files and lore before drafting. Do not assume summaries are complete.
- Separate source-backed canon, user corrections, and proposed adaptation in briefs and content data.
- Work in the established GemRB pipeline. Do not expand engine features when authored resources and scripts can deliver the scene.
- Keep changes reviewable: small content slices, explicit file lists, a build, focused checks, and a playthrough of the affected path.
- Never contact or invoke Demerzel. Do not send messages to people or services unless the user has authorized that action.

## 2. What the BG2 research supports

This baseline adapts the documented process and lessons from BG2; it does not copy its story, characters, text, assets, or setting.

- BioWare described keeping a stable engine and a familiar content pipeline so most of the 20-month project could focus on content. Their area pipeline ran from area map and description, through isometric concept and asset production, dressing and lighting, clipping and search maps, creatures/items/traps/triggers, and finally scripting. They also described written design standards and prioritized feature lists as important discipline.
- BG2's published level guidelines emphasized player agency, visible consequences, chapter goals, reusable core locations that change over time, and areas with distinct art and exploration value. Their writing guidance favored concise NPC dialogue and a small set of clear player choices. These were guidelines that changed during production, not rigid laws.
- BG2's writing and design accounts describe outlining a quest's beats with the wider team, expanding the beats into detail, and coordinating narrative with gameplay and art. Technical designers implemented the triggers, actors, movement, rewards, and scene timing. The team also acknowledged that content scope could grow out of control and that late QA was difficult; early testing and scope control are therefore required here.
- Contemporary reporting describes BG2 areas as dense with quests, items, encounters, and people to talk to, and companions with individual motives and arcs.

Sources: [BioWare's BG2 postmortem](https://media.gdcvault.com/GD_Mag_Archives/GDM_March_2001.pdf), [David Gaider on Infinity Engine writing and implementation](https://www.shacknews.com/article/103473/beneath-a-starless-sky-pillars-of-eternity-and-the-infinity-engine-era-of-rpgs?page=15), [Kevin Martens on area content](https://www.insidemacgames.com/historical/news/story.php%3FArticleID=1621.html), and [PC Gamer's BG2 retrospective](https://www.pcgamer.com/games/rpg/25-years-ago-today-baldurs-gate-2-set-rpgs-on-the-path-to-becoming-the-industry-defining-genre-they-are-today-we-were-putting-all-the-fantasies-that-we-had-into-the-game/).

## 3. Canon and narrative control

1. **Use a source hierarchy.** Direct user clarification and original user-authored material take precedence. The user's lore codex is a valuable but explicitly partial reconstruction. Existing game prose and AI-generated proposals are not evidence of canon.
2. **Mark provenance.** Every new major plot point or NPC belongs in one of these categories: `canon`, `user-confirmed`, `adaptation`, or `unresolved`. Keep those labels in planning data, not in player-facing dialogue.
3. **Keep uncertainty intact.** Do not fill gaps with invented deaths, marriages, dates, kinship, motives, or outcomes. In particular, Edmon's fate and the transition from his reign to Algoreth's later rule remain unwritten in available sources. The early period has Queen Alisande married to King Edmon, the original king; the later recovered chronicle describes Alisande as Algoreth's wife and co-ruler. Keep those eras distinct.
4. **Make the player the actor.** Algoreth's choices, investigation, and actions must drive the outcome. NPCs can advise, oppose, ask, or react; they must not resolve the central conflict while the player watches.
5. **Preserve the established boundaries.** Do not merge Terralum with separate Demerzel/Synthia continuities. Do not turn uncertain recovered details into settled fact.

## 4. Content pipeline: one playable area at a time

The following gates are mandatory, in order. Changes can overlap when dependencies are clear, but an area is not complete until every gate has evidence.

### Gate A — Story brief

Write a one-page brief containing:

- Act, quest, area name, entry point, exit points, and estimated play time.
- What the player wants on entry, the obstacle, the turning point, and the result on exit.
- What is canon, what is adaptation, and what must stay unresolved.
- How this scene advances the act and what state it changes.
- Intended player feelings and the moment of discovery or decision.
- Scope: required content, optional content, and explicitly deferred work.

**Pass:** The player goal is concrete, the story outcome follows from player action, and no unresolved lore is silently settled.

### Gate B — Quest and event outline

Break the scene into ordered beats before writing dialogue. For every beat, record actor, trigger, player options, condition, state change, visible result, failure/skip case, and next beat. Map the state in a small table or diagram. Use flags with one owner and clear meanings; set each once, define reset behavior, and avoid ambiguous overloaded variables.

**Pass:** A designer can explain how the scene starts, advances, branches, rewards, and ends without reading implementation code. Every branch rejoins or intentionally leads to a different quest state. No choice is cosmetic.

### Gate C — NPC design and cast

Each area must contain at least two authored, named NPCs unless the brief explains why isolation is the intended experience. The cast sheet records:

| Field | Required content |
|---|---|
| Identity | Stable name, role, faction, canon/adaptation status |
| Presence | Area, start position, schedule/arrival/departure, sprite/portrait |
| Goal | What this NPC wants in this scene |
| Knowledge | What they know, what they misunderstand, and what they will reveal |
| Voice | Distinct diction and emotional stance, without relying on caricatured accent |
| Interaction | Dialogue resource, entry condition, choices, consequences, exit |
| Continuity | Quest flags touched, later return, changed relationship or world state |

Recurring characters need a clear reason to return and a changed line when the world state changes. Background NPCs should have a few useful lines, but do not give every passerby a large quest. Distinct names without distinct motivations or actions do not count as authored NPCs.

**Pass:** NPCs exist as visible actors in the correct area, their names are observable in play, at least one can be spoken to, their lines are contextual, and no actor overlaps the party, blocks a route, or silently respawns on reload.

### Gate D — Dialogue and player choices

- Use short NPC turns. Aim for one or two concise lines before a player response.
- Offer about three meaningful responses when a decision belongs to the player. Fewer are fine when the moment is simple; more require a clear reason.
- Give each response an observable effect: information, relationship change, quest state, route, reward, encounter disposition, or a deliberate refusal.
- Write speaker, condition, response, action, and resulting state together. Dialogue and implementation must describe the same event.
- Never put required information in an optional line with no fallback. Give the player another route to discover essential facts.
- Do not use a linear text panel as a substitute for interactive dialogue when the design calls for a conversation.

**Pass:** Every choice was tested at least once; restricted choices appear only when their conditions hold; prior choices can produce a changed response.

### Gate E — Area concept and production design

Before generating or building final art, produce an area map and written description, then an isometric concept. Mark:

- Walkable surfaces, walls, height changes, occlusion, entrances, exits, and camera composition.
- Party arrival and NPC positions, combat staging, interactable props, clues, cover, and hazards.
- Lighting, palette, time/weather, ambient audio, and visual story focal points.
- Route lengths, sightlines, scale, and navigation landmarks.
- Search map, clipping/walkmesh, height, light map, and region/door geometry.

Build and dress the environment to make the intended route readable. The art, walkmesh, actor positions, entrances, and interactive regions must describe the same place. Reusing a template is acceptable for a prototype; it is not a release-ready area.

**Pass:** The player can navigate from entry to exit; blocked areas match the art; NPCs and props are reachable and legible; no inherited tutorial geometry or trigger remains by accident.

### Gate F — Encounter, clue, and reward implementation

For every encounter or puzzle, specify the player-facing clue, expected tactics, difficulty target, party assumptions, failure state, victory state, and quest effect. Provide a noncombat route when it fits the characters and scene. Rewards should arrive at the moment promised and be recorded in the journal or world state. Persistent story events must survive save/load without duplication.

**Pass:** The encounter is winnable with the expected party, loss cannot softlock the campaign, and victory or resolution visibly changes the scene or quest.

### Gate G — Script and resource integration

- Keep narrative and NPC data in explicit, validated resources; keep event scripts small and named for their scene or quest.
- Use stable script names and resource references. Document global flags and their owners in the quest brief.
- Make area-entry events idempotent: reloading or revisiting does not duplicate NPCs, rewards, ambushes, or dialogue effects.
- Keep scripts compatible with the GemRB API shipped by the repository. Do not guess an API call; verify against local scripts/docs/source or a working demo.
- Add clear logging for a failed resource lookup or event precondition during development.

**Pass:** The game pack builds from source, all referenced resources resolve, and the game log contains no new Python/resource errors on the scene path.

### Gate H — Audio, narration, and accessibility

Use the established local Kokoro woman narrator for chapter narration when the machine's local model is available. Keep narration text in the story source and generated audio reproducible. Ambient tracks should loop without clicks, sit below dialogue, and change with place or dramatic state. Every essential voiced line remains readable on screen; provide pause, replay, and subtitle behavior.

**Pass:** Narration and loops play in the built game, scene changes select the right music, and audio does not obscure combat or NPC dialogue.

### Gate I — Playtest and acceptance

Run a focused test after each scene change and a fresh-save campaign pass before calling a complete act. Check:

- Entry, party placement, each NPC, each response, each event, each exit, and return path.
- Quest-state changes, encounter success/failure, rewards, and visible consequences.
- Save, load, revisit, and duplicate-spawn behavior.
- Movement/pathfinding, collisions, triggers, map notes, lighting, audio, narration, and UI input.
- Game logs, build output, and the content checks relevant to the changed resources.

Record the test path and result next to the scene's status. A mocked script test proves state logic only; it does not prove the live area, controls, actor placement, or audio work. Mark acceptance only when both resource checks and a live GemRB playthrough support it.

## 5. Scope and release discipline

BG2's postmortem warns that abundant content can balloon scope and make QA difficult. Terralum should grow by accepted slices, not by counting unimplemented locations. Each release slice has:

1. A fixed list of areas, quests, NPCs, and features.
2. A playable critical path and a stated deferred-content list.
3. A content owner/reviewer and a bug list for each quest.
4. A stop condition: no new side content enters the slice after acceptance testing starts unless a blocker requires it.
5. A commit that includes source, resource manifest, review notes, test evidence, and a pushed fork update when requested by the user.

Use a simple status per area/quest: `brief`, `outlined`, `writing`, `building`, `playtest`, `accepted`. Only a live tester moves a quest from `playtest` to `accepted`.

## 6. Scene acceptance checklist

Copy this list into each area review:

- [ ] Lore sources and uncertainty reviewed; adaptation content labeled.
- [ ] Brief and beat outline approved against the act goal.
- [ ] Named NPC cast present, motivated, visible, and interactable.
- [ ] Dialogue choices have conditions and durable consequences.
- [ ] Clues and quest progression have readable fallback routes.
- [ ] Area art, collision, height, lighting, entrances, and interactables agree.
- [ ] Encounter/puzzle has clue, balance assumptions, failure case, resolution, and reward.
- [ ] NPCs, quest states, and rewards persist correctly across save/load and return.
- [ ] Narration, subtitles, ambient music, and replay/pause controls work.
- [ ] Build/resource checks pass and the live GemRB playthrough is recorded.
- [ ] Deferred issues are listed; no remaining issue is hidden by a green mock test.

## 7. Current campaign status

The prototype has 14 scene areas across seven acts, 37 story beats, 29 named scene actors, seven one-time persistent journal events, generated backdrops, seven act-entry Kokoro clips, and looping ambience. Eight scenes now contain response choices that set campaign flags and alter later scene text or the Mistwood route; campaign-flow mocks cover the 14 scene transitions and journal entries. The live WSL GemRB build starts in Alsperia Market and spawns its local cast, but UI input and save/load persistence remain unverified. The cast still reuses two demo sprites, all areas share one demo walkmesh, the choice system is custom rather than native DLG, and the scenes have not passed a full interactive playthrough. These are explicit production gaps, not accepted deviations from this baseline.
