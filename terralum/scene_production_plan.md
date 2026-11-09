# Terralum scene production plan

## Template drawn from Baldur's Gate II

The binding contributor baseline is [GOLD_STANDARD_GAME_DESIGN_PIPELINE.md](GOLD_STANDARD_GAME_DESIGN_PIPELINE.md). This file tracks delivery slices; the gold-standard file defines acceptance gates.

BioWare's postmortem describes a stable engine and content pipeline that let most development time go to authored content. It gives a repeatable area process: designers map and describe an area, concept artists develop the isometric idea, the level is built and dressed, then designers author clipping, lighting, height, and the search map. Its lessons also call out project scope and quality assurance as core constraints. Interviews with BG2 writers and designers describe dialogue authored with variables, technical designers implementing actor spawns, movement, rewards, and event timing, and quest arcs being outlined in beats before implementation. A BG2 retrospective emphasizes putting quests, items, encounters, and people into explorable spaces, and giving companions distinct motives and relationship arcs.

Sources: [BioWare's BG2 postmortem](https://media.gdcvault.com/GD_Mag_Archives/GDM_March_2001.pdf), [David Gaider on Infinity Engine writing and implementation](https://www.shacknews.com/article/103473/beneath-a-starless-sky-pillars-of-eternity-and-the-infinity-engine-era-of-rpgs?page=15), [Kevin Martens on BG2 area content](https://www.insidemacgames.com/historical/news/story.php%3FArticleID=1621.html), [BG2 retrospective](https://www.pcgamer.com/games/rpg/25-years-ago-today-baldurs-gate-2-set-rpgs-on-the-path-to-becoming-the-industry-defining-genre-they-are-today-we-were-putting-all-the-fantasies-that-we-had-into-the-game/).

## Rules for Terralum implementation

1. Keep each area focused on one story purpose and fill it with a named cast, discoverable clues, a quest/event, and a tactical or social encounter.
2. Write an area one-pager and its beat sequence before adding script events. Keep implementation constraints and story choices visible in the same data.
3. Give every recurring NPC a stable identity, role, motivation, voice text, and return beat. Do not turn unresolved lore into asserted history.
4. Make interaction change a durable quest flag, reveal a clue, open a route, or alter an encounter. Avoid dialogue that only relabels the Continue button.
5. Build geometry, walkability, actor placement, and scene art together; the current shared demo walkmesh is a temporary template and must not ship as finished areas.
6. Keep authored content achievable: deliver and playtest one act at a time, then expand only after the area has working pathing, dialogue, events, music, and saves.

## Delivery order

- **Slice A: Present characters in all current scenes.** Add named actors and a local Talk interaction with reusable dialogue data. Verify actors spawn once on initial entry and area transitions.
- **Slice B: Quest and event loop.** Add branching response options, quest flags, journal updates, event triggers, rewards, and battle gates. Each choice must affect a later beat or route.
- **Slice C: Scene fidelity.** Replace shared demo walkmesh, doors, entrances, and tutorial remnants with area-specific collision maps and transitions. Test movement and clicks in all areas.
- **Slice D: Campaign depth.** Expand each act into several connected subareas with side quests and recurring companions, preserving the user's Terralum chronology.
- **Slice E: Production review.** Play the entire campaign from a fresh save, test repeated area entry and save/load, verify Kokoro narration and ambient loops, then commit, comment, and push.

The campaign now has nineteen scene areas. Act I includes the Royal Dispatch Archive, where a copied patrol schedule makes the Waywarden diversion reliable, and the Royal Stables, where Edda and Tavin help Algoreth choose the lantern or rope kit; the choice is journaled and determines which later Mistwood investigation can safely bypass the stalker. The River Crossing now tests whether the Royal Stables rope kit was packed: a handline lets the party bypass the stalker, while the exposed ford keeps the encounter in play. Courier Eren carries the outcome to the Watchpost. The Mistwood Hunter's Camp is a three-NPC side stop with lantern and creekside choices; the Three-Cairn Fork adds a two-NPC waystone decision and changed watchpost dialogue. Mistwood Road has a connected custom searchmap and authored stalker spawn. The Ruined Watchpost has a custom plaza, southern approach, northern arch route, and two NPC placements. These adaptations have script connectivity checks, though their geometry still needs live playtesting. Other location briefs and lore limits are documented in `lore_notes.md` and `campaign_plan.md`; preserve those provenance labels as new scenes are added.
