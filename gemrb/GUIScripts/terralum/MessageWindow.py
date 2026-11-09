# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Data-driven Terralum campaign controls on the GemRB message panel."""

import GemRB
import Story
import GUICommon
import GUIMA
import GUIINV
from GUIDefines import *
from ie_stats import IE_EA, IE_STATE_ID, STATE_DEAD, ENEMY, NEUTRAL


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
	talk = window.CreateButton(11, 545, 183, 100, 34)
	_style(talk)
	talk.SetText("TALK")
	choice_buttons = []
	for index, x in enumerate((10, 183, 356)):
		button = window.CreateButton(12 + index, x, 183, 160, 34)
		_style(button)
		button.SetVisible(False)
		choice_buttons.append(button)

	chapters = Story.chapters()
	cast_index = {"line": -1}

	def spawn_cast(chapter_index):
		chapter = chapters[chapter_index]
		if GemRB.GetCurrentArea().lower() != chapter["area"]:
			return
		if GemRB.GetGameVar("TLCAST") == chapter_index + 1:
			return
		for person in Story.cast(chapter["area"]):
			actor = GemRB.CreateCreature(1, person["creature"], person["position"][0], person["position"][1])
			GemRB.SetPlayerName(actor, person["name"], 0)
			GemRB.SetPlayerStat(actor, IE_EA, NEUTRAL)
		if chapter["area"] == "tl0002" and GemRB.GetGameVar("TLMARALEAD") == 2:
			warden = GemRB.CreateCreature(1, "riddler", 850, 650)
			GemRB.SetPlayerName(warden, "Edmon's Waywarden", 0)
			GemRB.SetPlayerStat(warden, IE_EA, NEUTRAL)
		GemRB.SetGlobal("TLCAST", "GLOBAL", chapter_index + 1)

	def talk_to_scene_npc():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		people = Story.cast(chapters[chapter_index]["area"])
		cast_index["line"] = (cast_index["line"] + 1) % len(people)
		person = people[cast_index["line"]]
		line = person.get("line")
		if chapter_index == 1 and person.get("route_lines"):
			line = person["route_lines"].get(str(GemRB.GetGameVar("TLMARALEAD")), line)
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapters[chapter_index]["title"] + "\n" + chapters[chapter_index]["place"] + "\n\n" + person["name"] + ": " + line + "\n\n")
		for index, button in enumerate(choice_buttons):
			choices = person.get("choices", [])
			button.SetVisible(index < len(choices))
			if index < len(choices):
				choice = choices[index]
				button.SetText(choice["label"])
				button.OnPress(lambda choice=choice, person=person: choose_dialogue(person, choice))

	def choose_dialogue(person, choice):
		GemRB.SetGlobal(choice["flag"], "GLOBAL", choice["value"])
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n")
		for button in choice_buttons:
			button.SetVisible(False)
	def enemy_alive(enemy):
		try:
			return not GemRB.GetPlayerStat(enemy, IE_STATE_ID) & STATE_DEAD
		except RuntimeError:
			# GemRB may remove the actor once its death animation ends.
			return False

	def narrate():
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		GemRB.PlaySound(chapter["voice"], "GUI", 0, 0, 4)

	def show():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		beat_text = beat["text"]
		if chapter_index == 1 and beat_index == 0:
			lead = GemRB.GetGameVar("TLMARALEAD")
			if lead == 1:
				beat_text = "Mara's ledger marks the pale stones as a safe route around the ruined watchpost."
			elif lead == 2:
				beat_text = "Edmon's waywarden caught up with us. His patrol will draw the stalker away from the road."
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + beat["speaker"] + ": " + beat_text + "\n\n")
		action.SetText(beat["action"].upper() if len(beat["action"]) < 11 else "CONTINUE")

	def advance():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		if chapter_index == 1 and beat.get("encounter") and GemRB.GetGameVar("TLMARALEAD") == 1:
			GemRB.SetGlobal("TLMISTWOODSAFE", "GLOBAL", 1)
			GemRB.SetGlobal("TLBEAT", "GLOBAL", beat_index + 1)
			message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\nFollowing Mara's ledger, the party skirts the stalker's ambush along the pale stones.\n\n")
			return
		enemy = GemRB.GetGameVar("TLENEMY")
		if "encounter" in beat and not enemy:
			# The demo humanoid supplies an open-licensed CRE template. The
			# campaign names and hostility are assigned at spawn time.
			enemy = GemRB.CreateCreature(1, "riddler")
			GemRB.SetGlobal("TLENEMY", "GLOBAL", enemy)
			GemRB.SetPlayerName(enemy, beat["encounter"], 0)
			GemRB.SetPlayerStat(enemy, IE_EA, ENEMY)
			GemRB.ExecuteString("Attack(Player1)", enemy)
			message.Append("\n\nENCOUNTER: " + beat["encounter"] + " emerges. Defeat it to continue.")
			action.SetText("CONTINUE")
			return
		if "encounter" in beat and enemy_alive(enemy):
			message.Append("\n\n" + beat["encounter"] + " still stands. Defeat it to continue.")
			return
		GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
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
			GemRB.SetTimedEvent(lambda: spawn_cast(chapter_index), 1)
			cast_index["line"] = -1
			show()
			narrate()
			return
		GemRB.SetGlobal("TLBEAT", "GLOBAL", beat_index)
		show()

	action.OnPress(advance)
	voice.OnPress(narrate)
	talk.OnPress(talk_to_scene_npc)
	GemRB.LoadMusicPL(chapters[GemRB.GetGameVar("TLCHAP")]["music"], 1)
	initial_chapter = GemRB.GetGameVar("TLCHAP")
	GemRB.SetTimedEvent(lambda: spawn_cast(initial_chapter), 1)
	show()
	narrate()


def UpdateControlStatus():
	pass


def ToggleMenuWindow():
	pass
