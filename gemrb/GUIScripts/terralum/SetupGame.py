# SPDX-FileCopyrightText: 2012 Contributors to the GemRB project <https://gemrb.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import GemRB
import Start
from GUIDefines import GS_PARTYAI
from ie_stats import IE_STR

def OnLoad():
	# skipping chargen
	GemRB.CreatePlayer ("protagon", 1|0x8000) # exportable
	GemRB.SetPlayerName (1, Start.Name, 0)
	GemRB.SetPlayerSound (1, "male001")
	# set strength, so items can be picked up (currently needed for encumbrance labels)
	GemRB.SetPlayerStat (1, IE_STR, 14)

	GemRB.GameSetScreenFlags (GS_PARTYAI, OP_OR)
	GemRB.SetVar("CHAPTER", 1)
	GemRB.SetVar("TL_CHAPTER", 0)
	GemRB.SetVar("TL_BEAT", 0)
	GemRB.SetGlobal("TLCHAP", "GLOBAL", 0)
	GemRB.SetGlobal("TLBEAT", "GLOBAL", 0)
	GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
	GemRB.SetGlobal("TLENEMY_STALKER", "GLOBAL", 0)
	GemRB.SetGlobal("TLENEMY_PROWLER", "GLOBAL", 0)
	GemRB.SetGlobal("TLMISTWOODVICTORY", "GLOBAL", 0)
	GemRB.SetGlobal("TLCAST", "GLOBAL", 0)
	GemRB.SetGlobal("TLMARALEAD", "GLOBAL", 0)
	GemRB.SetGlobal("TLLIBRARYCLUE", "GLOBAL", 0)
	GemRB.SetGlobal("TLWATCHPOST", "GLOBAL", 0)
	GemRB.SetGlobal("TLGALLERY", "GLOBAL", 0)
	GemRB.SetGlobal("TLCOURT", "GLOBAL", 0)
	GemRB.SetGlobal("TLECHO", "GLOBAL", 0)
	GemRB.SetGlobal("TLMISTWOODSAFE", "GLOBAL", 0)
	GemRB.SetGlobal("TLARCHIVE", "GLOBAL", 0)
	GemRB.SetGlobal("TLVOYAGE", "GLOBAL", 0)
	GemRB.SetGlobal("TLBRIEFING", "GLOBAL", 0)
	GemRB.SetGlobal("TLHUNTER", "GLOBAL", 0)
	GemRB.SetGlobal("TLHUNTERTRACK", "GLOBAL", 0)
	GemRB.SetGlobal("TLWAYSTONE", "GLOBAL", 0)
	GemRB.SetGlobal("TLTRAVELKIT", "GLOBAL", 0)
	GemRB.SetGlobal("TLROYALORDER", "GLOBAL", 0)
	GemRB.SetGlobal("TLRIVER", "GLOBAL", 0)
	GemRB.SetGlobal("TLRIVERROUTE", "GLOBAL", 0)
	GemRB.SetGlobal("TLLORIANPURPOSE", "GLOBAL", 0)
	GemRB.SetGlobal("TLLORIAN_GUARDIAN", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_BYZANTEM", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_MISTWOOD", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_MISTWOOD_AMBUSH", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_HUNTER", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_HUNTER_RESOLVED", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_TRACKS", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_WAYSTONE", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_LORIAN_PURPOSE", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_GALLERY_RESOLUTION", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_TRAVELKIT", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_ROYALORDER", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_RIVER", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_SCROLLS", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_TEAR", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_ARCHIVE", "GLOBAL", 0)
	GemRB.SetGlobal("TLARCHIVEWARD", "GLOBAL", 0)
	GemRB.SetGlobal("TLDEEP_ARCHIVE_WARDEN", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_ARCHIVE_WARD", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_ELDRADOR", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_VOYAGE", "GLOBAL", 0)
	GemRB.SetGlobal("TLJRN_BRIEFING", "GLOBAL", 0)
	GemRB.EnterGame()
