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

An original fantasy campaign is taking shape inside this GemRB fork. **Terralum: Scrolls of Byzantem** follows Algoreth Jon Goren from the court of Alsperia into a search for the lost scrolls, through the Mistwood and Caverns of Lorian, and onward toward the mysteries of the Tears. Its current prototype spans sixteen scene areas across a seven-act story spine, with a named cast, branching choices, a persistent quest journal, Kokoro narration, ambient music, and gated encounters.

<p align="center">
  <img src="terralum/screenshots/campaign-locations-concept-art.jpg" alt="Six Terralum locations: Alsperia Market, Hunter's Camp, Three-Cairn Fork, Caverns of Lorian, Deep Archives, and Aethercraft Hangar" width="94%">
</p>
<p align="center"><em>Location concept art — visual targets, not in-game screenshots</em></p>

### Running in GemRB

These captures show the opening Alsperia Market scene running in GemRB. The wide view includes the player, three local NPCs, the current story beat, and Talk, Narrate, and Continue controls. The second capture is a closer look at the scene cast.

<p align="center">
  <img src="terralum/screenshots/alsperia-market-npcs.png" alt="Terralum running in GemRB: the Alsperia Market scene with the player and three local NPCs" width="86%">
</p>
<p align="center"><em>Alsperia Market — live GemRB capture</em></p>

<p align="center">
  <img src="terralum/screenshots/market-party-detail.png" alt="Closer gameplay capture of the player and market NPCs" width="62%">
</p>
<p align="center"><em>Market cast — closer view</em></p>

### Scene art

Fifteen distinct generated concept backdrops preview the sixteen scene areas; one backdrop is reused. They are visual targets for the current prototype. The Hunter's Camp, Three-Cairn Fork, and Mistwood Road have custom searchmaps; the Mistwood stalker spawns on the authored road path. All sixteen areas still use the demo's shared WED layout and other terrain resources.

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
    <td align="center"><sub>Sixteen scene areas across seven acts; one backdrop is reused.</sub></td>
  </tr>
</table>

### Explore the project

- [Terralum project guide](terralum/README.md) — build, play, audio, and MCP authoring setup.
- [Gold Standard design pipeline](terralum/GOLD_STANDARD_GAME_DESIGN_PIPELINE.md) — BG2-informed scene and content workflow.
- [Campaign plan](terralum/campaign_plan.md) — seven-act story spine and planned expansion.
- [TODO and handoff](TODO.md) — completed, ongoing, and next work.

Terralum is an in-progress prototype, not a finished or full-length RPG. The current cast reuses demo sprites and all sixteen areas still inherit the demo WED layout; Hunter's Camp, the Three-Cairn Fork, and Mistwood Road have custom searchmaps, while the other thirteen use the generic one. Choices use a custom panel rather than native Infinity Engine DLG resources. The project guide and handoff describe current playability and verification gaps.

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
