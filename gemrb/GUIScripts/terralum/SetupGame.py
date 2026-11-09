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
	GemRB.SetGlobal("TLCAST", "GLOBAL", 0)
	GemRB.SetGlobal("TLMARALEAD", "GLOBAL", 0)
	GemRB.SetGlobal("TLLIBRARYCLUE", "GLOBAL", 0)
	GemRB.SetGlobal("TLWATCHPOST", "GLOBAL", 0)
	GemRB.SetGlobal("TLGALLERY", "GLOBAL", 0)
	GemRB.SetGlobal("TLCOURT", "GLOBAL", 0)
	GemRB.SetGlobal("TLECHO", "GLOBAL", 0)
	GemRB.SetGlobal("TLMISTWOODSAFE", "GLOBAL", 0)
	GemRB.EnterGame()
