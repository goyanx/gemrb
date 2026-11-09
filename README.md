# GemRB

[![GitHub build status](https://github.com/gemrb/gemrb/actions/workflows/builder.yml/badge.svg)](https://github.com/gemrb/gemrb/actions/workflows/builder.yml)
[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/k5atpwnihjjiv993?svg=true)](https://ci.appveyor.com/project/lynxlynxlynx/gemrb)
[![Coverity Badge](https://scan.coverity.com/projects/288/badge.svg)](https://scan.coverity.com/projects/gemrb)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=gemrb_gemrb&metric=alert_status)](https://sonarcloud.io/dashboard?id=gemrb_gemrb)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3101/badge)](https://bestpractices.coreinfrastructure.org/projects/3101)

## Introduction

[GemRB](https://gemrb.org) (Game Engine Made with preRendered Background) is a portable open-source
reimplementation of the Infinity Engine that underpinned Baldur's Gate,
Icewind Dale and Planescape: Torment. It sports a cleaner design, greater
extensibility and several innovations.
Would you like to create a game like Baldur's Gate?

## Play Terralum

This fork includes **Terralum: Scrolls of Byzantem**, an original, story-driven Infinity Engine style RPG campaign built on GemRB. Follow Algoreth Jon Goren from the court of Alsperia through the Mistwood, Lorian, the eastern academy, the Deep Archives, and onward to Eldrador. The current prototype spans **25 areas across seven acts**, with local NPCs, branching choices, journaled consequences, encounters, optional narration, and ambient music.

<p align="center">
  <a href="terralum/screenshots/alsperia-market-live.png"><img src="terralum/screenshots/alsperia-market-live.png" alt="Actual GemRB capture of the opening Alsperia Market scene, with the party, three local cast actors, story text, journal, Talk, Continue, and Narrate controls" width="92%"></a>
</p>
<p align="center"><em>Live GemRB campaign capture: the Alsperia Market opening scene with its local cast, story panel, journal control, Talk, Continue, and Kokoro Narrate.</em></p>

<p align="center">
  <a href="terralum/screenshots/alsperia-market-journal-live.png"><img src="terralum/screenshots/alsperia-market-journal-live.png" alt="Live GemRB Journal showing the Alsperia opening quest under Act I" width="44%"></a>
  &nbsp;&nbsp;
  <a href="terralum/screenshots/campaign-locations-concept-art.jpg"><img src="terralum/screenshots/campaign-locations-concept-art.jpg" alt="Generated concept-art montage previewing Terralum campaign locations" width="44%"></a>
</p>
<p align="center"><em>Left: live GemRB Journal with the opening quest recorded under Act I · Right: generated location concept art, a visual target rather than in-game scenery.</em></p>

<p align="center">
  <a href="terralum/screenshots/market-party-detail.png"><img src="terralum/screenshots/market-party-detail.png" alt="Detail crop of the player party and local NPC placements in the Alsperia Market" width="60%"></a>
</p>
<p align="center"><em>Live scene detail: the party and local cast are placed together in the opening market. Scene actors currently reuse the demo's placeholder sprites.</em></p>

**[Campaign guide](terralum/README.md)** · **[Gold Standard pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md)** · **[Campaign plan](terralum/campaign_plan.md)** · **[Current TODO](TODO.md)**

> **Prototype status:** This is an expanding playable slice, not a finished full-length RPG. Its party and scene actors currently reuse demo sprites, and all 25 areas still inherit the demo's WED layout and terrain. The campaign has custom per-area searchmaps, authored cast and dialogue choices, and a growing set of stateful story events. See the [campaign guide](terralum/README.md) for build steps and current verification limits.

To try it out you either need some of the ORIGINAL game's data or you can
get a tiny sneak peek by running the included trivial game demo.

The original game data has to be installed if you want to see anything but
the included trivial demo. On non-windows systems either copy it over from
a windows install, use a compatible installer, WINE or extract it manually
from the CDs using the unshield tool.

Documentation can be found on the [website](https://gemrb.org/Documentation),
in `gemrb/docs/` and the [gemrb.6 man page](https://gemrb.org/Manpage.html).

If you want to help out, start by reading this
list of [options, tips and priorities](https://github.com/gemrb/gemrb/blob/master/CONTRIBUTING.md).

## Terralum: Scrolls of Byzantem

**An original Infinity Engine style RPG campaign, built on GemRB.** In **Terralum: Scrolls of Byzantem**, Algoreth Jon Goren leaves the court of Alsperia to recover the lost scrolls. The trail leads through the Mistwood and Caverns of Lorian, then toward the eastern academy, the Deep Archives, and the mysteries of the Tears.

The playable prototype currently covers **25 scene areas and 63 story beats across seven acts**. Its 62 named scene actors have local dialogue and response choices. Stateful conversations carry across scenes: Mara's ledger handling changes Scholar Inessa's later Library response; Captain Rovan’s Council policy governs open road access or restricted scroll access; Oren’s docket preserves whether route testimony and the scroll account are paired or separate; Pell's optional deposition determines whether the public docket carries only his warning or the crown keeps full route details, later combined with Oren’s paired/separate docket decision in Queen Alisande’s response; and Keeper Orla's Waywarden Relay lets Algoreth decide whether to call the patrol. Saren's dialogue reflects whether the party copied Leora's schedule; both relay outcomes are journaled. After Lorian, the party returns to the watchpost: Pell records whether the route marker is public or held in Edmon's court archive, and King Edmon and Queen Alisande respond to the decision. In Act VII, engineer Alistair's hangar dialogue reacts to both the expedition record and the ship's preparation. The campaign also has ambient music, optional Kokoro narration, and four gated encounters. In Act VI, if the Deep Archives account stays sealed, Algoreth chooses which bounded question Ealdrin carries to Eldrador; Vaelthira’s response changes, while the record’s speaker remains unknown. Act VII continues from the Aethercraft departure into an Eldrador landing and sanctuary-threshold investigation. The party records testimony or ward measurements, then chooses a cautious approach; the game stops before the inner sanctuary is entered, leaving the Tear unresolved as the recovered lore requires. It is an active prototype: campaign content and systems are growing, and the full-length RPG is still ahead.

### Campaign location gallery

Twenty-three distinct generated concept backdrops preview the twenty-five scene areas. The Deep Archives and the returning Mistwood Watchpost reuse their existing location art. They are visual targets for the current prototype. All twenty-five scenes have custom data-authored searchmaps, including the Market, Royal Court, Observatory Vault, Skyport, Library, Academy Courtyard, Index Hall, and Hangar. All twenty-five areas still use the demo's shared WED layout and other terrain resources.

<table>
  <tr>
    <td align="center"><img src="terralum/art/alsperia_market.png" alt="Alsperia Market concept art" width="100%"><br><sub>Alsperia Market</sub></td>
    <td align="center"><img src="terralum/art/alsperia_court.png" alt="Alsperia royal court concept art" width="100%"><br><sub>Royal Court</sub></td>
    <td align="center"><img src="terralum/art/mistwood_road.png" alt="Mistwood Road concept art" width="100%"><br><sub>Mistwood Road</sub></td>
    <td align="center"><img src="terralum/art/mistwood_ruins.png" alt="Mistwood watchpost ruins concept art" width="100%"><br><sub>Mistwood Watchpost</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/lorian_cavern.png" alt="Caverns of Lorian concept art" width="100%"><br><sub>Caverns of Lorian</sub></td>
    <td align="center"><img src="terralum/art/byzantem_arch.png" alt="Byzantem seal gallery concept art" width="100%"><br><sub>Seal Gallery</sub></td>
    <td align="center"><img src="terralum/art/council_chamber.png" alt="Alsperia Council Chamber concept art" width="100%"><br><sub>Council Chamber</sub></td>
    <td align="center"><img src="terralum/art/observatory_courtyard.png" alt="Eastern Academy courtyard concept art" width="100%"><br><sub>Academy Courtyard</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/tear_vault.png" alt="Tear Vault concept art" width="100%"><br><sub>Tear Vault</sub></td>
    <td align="center"><img src="terralum/art/deep_archives.png" alt="Deep Archives concept art" width="100%"><br><sub>Deep Archives</sub></td>
    <td align="center"><img src="terralum/art/archive_index_hall.png" alt="Deep Archive Index Hall concept art" width="100%"><br><sub>Index Hall</sub></td>
    <td align="center"><img src="terralum/art/alsperia_skyport.png" alt="Alsperia Skyport concept art" width="100%"><br><sub>Alsperia Skyport</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/aethercraft_hangar.png" alt="Aethercraft Hangar concept art" width="100%"><br><sub>Aethercraft Hangar</sub></td>
    <td align="center"><img src="terralum/art/mistwood_hunters_camp.png" alt="Mistwood Hunter's Camp concept art" width="100%"><br><sub>Mistwood Hunter's Camp</sub></td>
    <td align="center"><img src="terralum/art/mistwood_waystone_fork.png" alt="Mistwood Three-Cairn Fork concept art" width="100%"><br><sub>Three-Cairn Fork</sub></td>
    <td align="center"><img src="terralum/art/alsperia_royal_stables.png" alt="Alsperia Royal Stables concept art: an open courtyard prepared for a western expedition" width="100%"><br><sub>Royal Stables</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/alsperia_dispatch_archive.png" alt="Alsperia Royal Dispatch Archive concept art: patrol maps and a central route table" width="100%"><br><sub>Dispatch Archive</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/mistwood_river_crossing.png" alt="Mistwood river crossing concept art: a handline above the ford and a damaged footbridge" width="100%"><br><sub>Mistwood River Crossing</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/mistwood_ruins.png" alt="Returning to the Mistwood Watchpost; reuses the existing location concept art" width="100%"><br><sub>Watchpost Return · reused location art</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/mistwood_waywarden_relay.png" alt="Mistwood Waywarden Relay concept art: a covered signal lantern beside the pale-stone road" width="100%"><br><sub>Waywarden Relay</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="terralum/art/expedition_chart_room.png" alt="Alsperia Expedition Chart Room concept art, with harbor windows, an airship, star charts and a clear central floor" width="100%"><br><sub>Expedition Chart Room</sub></td>
    <td align="center"><img src="terralum/art/academy_warding_annex.png" alt="Eastern Academy Containment Annex concept art, a violet Tear held inside a brass measuring ring" width="100%"><br><sub>Containment Annex</sub></td>
    <td align="center"><img src="terralum/art/eldrador_arrival_quay.png" alt="Eldrador cliffside arrival quay with the Aethercraft and an open harbor plaza" width="100%"><br><sub>Eldrador Arrival Quay</sub></td>
    <td align="center"><img src="terralum/art/eldrador_sanctuary_threshold.png" alt="Eldrador lower sanctuary threshold with an intact sealed gate and ward ring" width="100%"><br><sub>Lower Sanctuary Threshold</sub></td>
  </tr>
</table>

### Explore the project

- [Terralum project guide](terralum/README.md) — build, play, audio, and MCP authoring setup.
- [Gold Standard design pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md) — BG2-informed scene and content workflow.
- [Campaign plan](terralum/campaign_plan.md) — seven-act story spine and planned expansion.
- [TODO and handoff](TODO.md) — completed, ongoing, and next work.

Terralum is an in-progress prototype, not a finished or full-length RPG. The current cast reuses demo sprites and all twenty-five areas still inherit the demo WED layout; all twenty-five areas now have custom searchmaps, with structural connectivity checks for each. Archivist Mara, Royal Scribe Oren, King Edmon, Queen Alisande, and Alistair have native DLG resources; the royal couple's return-court dialogue reflects the route record and Lorian gallery decision, and the council response reflects Oren's evidence docket. Most NPC conversations still use the custom choice panel, and direct click/save behavior remains unverified in live GemRB. The project guide and handoff describe current playability and verification gaps.

## Supported platforms

Architectures and platforms that successfully run or ran GemRB:
* Linux x86, x86-64, ppc, mips (s390x builds, but no running info)
* FreeBSD, OpenBSD, NetBSD
* MS Windows
* various Macintosh systems (even pre x86)
* some smart phones (Symbian, Android, other Linux-based, iOS)
* some consoles (OpenPandora, Dingoo)
* some exotic OSes (ReactOS, SyllableOS, Haiku, AmigaOS, AmberElec, ArkOS, UnofficialOS)

If you have something to add to the list or if an entry doesn't work any more, do let us know!

## Requirements

See the INSTALL [file](https://github.com/gemrb/gemrb/blob/master/INSTALL).

## Contacts

There are several ways you can get in touch:
* [Homepage](https://gemrb.org)
* [GemRB forum](https://www.gibberlings3.net/forums/forum/91-gemrb/)
* [IRC channel](https://web.libera.chat/#GemRB), #GemRB on the Libera.Chat IRC network
* [Discord channel](https://discord.gg/64rEVAk) (Gibberlings3 server)
* [Bug tracker](https://github.com/gemrb/gemrb/issues/new/choose)


## Useful links

Original engine research and data manipulation software:
* [IESDP](https://gibberlings3.github.io/iesdp/), documentation for the Infinity Engine file formats and more
* [Near Infinity](https://github.com/NearInfinityBrowser/NearInfinity/wiki), Java viewer and editor for data files
* [DLTCEP](https://www.gibberlings3.net/forums/forum/137-dltcep/), MS Windows viewer and editor for data files
* [iesh](https://github.com/gemrb/iesh), IE python library and shell (for exploring data files)

Tools that can help with data installation:
* [WINE](https://www.winehq.org), Open Source implementation of the Windows API, useful for installing the games
* [Unshield](http://synce.sourceforge.net/synce/unshield.php), extractor for .CAB files created by InstallShield
