# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Data-driven Terralum campaign controls on the GemRB message panel."""

import GemRB
import Story
import GUICommon
import GUIMA
import GUIINV
from GUIDefines import *
from ie_stats import IE_EA, ENEMY


def _style(button, width=None):
	if width is not None:
		frame = button.GetFrame()
		frame["w"] = width
		button.SetFrame(frame)
	button.SetFlags(IE_GUI_BUTTON_NO_IMAGE, OP_OR)
	button.SetBorder(0, {"r": 196, "g": 164, "b": 105, "a": 255}, 1, 0)


def OnLoad():
	window = GemRB.LoadWindow(0, GUICommon.GetWindowPack(), WINDOW_BOTTOM | WINDOW_HCENTER)
	window.SetFlags(WF_BORDERLESS, OP_OR)
	window.AddAlias("MSGWIN")
	window.AddAlias("HIDE_CUT", 0)
	message = window.GetControl(0)
	message.SetFlags(IE_GUI_TEXTAREA_AUTOSCROLL | IE_GUI_TEXTAREA_HISTORY)
	message.AddAlias("MsgSys", 0)
	message.AddAlias("MTA", 0)
	message.SetColor(ColorRed, TA_COLOR_OPTIONS)
	message.SetColor(ColorWhite, TA_COLOR_HOVER)

	pause = window.GetControl(2)
	pause.OnPress(lambda: GemRB.GamePause(2, 0))
	pause.SetAnimation("loading", 0, A_ANI_GAMEANIM)
	pause.SetFlags(IE_GUI_BUTTON_PICTURE | IE_GUI_BUTTON_NORMAL, OP_SET)
	map_button = window.GetControl(3)
	map_button.SetText("M")
	map_button.OnPress(GUIMA.OpenMapWindow)
	inventory = window.GetControl(5)
	inventory.SetText("I")
	inventory.OnPress(GUIINV.OpenInventoryWindow)

	action = window.GetControl(4)
	_style(action, 100)
	voice = window.CreateButton(10, 660, 183, 100, 34)
	_style(voice)
	voice.SetText("NARRATE")

	chapters = Story.chapters()
	state = {"enemy": 0}

	def narrate():
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		GemRB.PlaySound(chapter["voice"], "GUI", 0, 0, 4)

	def show():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + beat["speaker"] + ": " + beat["text"] + "\n\n")
		action.SetText(beat["action"].upper() if len(beat["action"]) < 11 else "CONTINUE")

	def advance():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		if "encounter" in beat and not state["enemy"]:
			# The demo humanoid supplies an open-licensed CRE template. The
			# campaign names and hostility are assigned at spawn time.
			state["enemy"] = GemRB.CreateCreature(1, "riddler")
			GemRB.SetPlayerName(state["enemy"], beat["encounter"], 0)
			GemRB.SetPlayerStat(state["enemy"], IE_EA, ENEMY)
			GemRB.ExecuteString("Attack(Player1)", state["enemy"])
			message.Append("\n\nENCOUNTER: " + beat["encounter"] + " emerges. Select it and attack; press Continue after the fight.")
			action.SetText("CONTINUE")
			return
		state["enemy"] = 0
		beat_index += 1
		if beat_index >= len(chapter["beats"]):
			chapter_index += 1
			beat_index = 0
			if chapter_index >= len(chapters):
				message.SetText("[cap]T[/cap]ERRALUM  |  TO BE CONTINUED\n\nThe Aethercraft departs for Eldrador. The fate of its Tear remains unknown.")
				action.SetText("FINISHED")
				action.OnPress(lambda: None)
				return
			GemRB.SetGlobal("TLCHAP", "GLOBAL", chapter_index)
			GemRB.SetGlobal("TLBEAT", "GLOBAL", 0)
			GemRB.SetVar("CHAPTER", chapter_index + 1)
			GemRB.LoadMusicPL(chapters[chapter_index]["music"], 1)
			GemRB.MoveToArea(chapters[chapter_index]["area"])
			show()
			narrate()
			return
		GemRB.SetGlobal("TLBEAT", "GLOBAL", beat_index)
		show()

	action.OnPress(advance)
	voice.OnPress(narrate)
	GemRB.LoadMusicPL(chapters[GemRB.GetGameVar("TLCHAP")]["music"], 1)
	show()
	narrate()


def UpdateControlStatus():
	pass


def ToggleMenuWindow():
	pass
