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
	voice.SetHotKey("n", 0, True)
	talk = window.CreateButton(11, 545, 183, 100, 34)
	_style(talk)
	talk.SetText("TALK")
	talk.SetHotKey("t", 0, True)
	choice_buttons = []
	for index, x in enumerate((10, 183, 356)):
		button = window.CreateButton(12 + index, x, 183, 160, 34)
		_style(button)
		button.SetVisible(False)
		choice_buttons.append(button)
	journal_button = window.CreateButton(15, 430, 183, 100, 34)
	_style(journal_button)
	journal_button.SetText("JOURNAL")
	journal_button.SetHotKey("j", 0, True)
	journal_state = {"open": False}
	dialogue_state = {"has_choices": False, "must_finish_followup": False, "followup_journal": None}

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
			if person.get("spawn_flag"):
				GemRB.SetGlobal(person["spawn_flag"], "GLOBAL", actor)
		if chapter["area"] == "tl0002" and GemRB.GetGameVar("TLMARALEAD") == 2:
			warden = GemRB.CreateCreature(1, "riddler", 850, 650)
			GemRB.SetPlayerName(warden, "Edmon's Waywarden", 0)
			GemRB.SetPlayerStat(warden, IE_EA, NEUTRAL)
		GemRB.SetGlobal("TLCAST", "GLOBAL", chapter_index + 1)

	def talk_to_scene_npc():
		if dialogue_state["must_finish_followup"]:
			return
		if journal_state["open"]:
			journal_state["open"] = False
			journal_button.SetText("JOURNAL")
			show()
		chapter_index = GemRB.GetGameVar("TLCHAP")
		chapter = chapters[chapter_index]
		people = Story.cast(chapter["area"])
		cast_index["line"] = (cast_index["line"] + 1) % len(people)
		person = people[cast_index["line"]]
		line = person.get("line")
		if chapter["area"] == "tl0002" and person.get("route_lines"):
			line = person["route_lines"].get(str(GemRB.GetGameVar("TLMARALEAD")), line)
		for response in person.get("responses", []):
			if GemRB.GetGameVar(response["flag"]) == response["value"]:
				line = response["line"]
				break
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapters[chapter_index]["title"] + "\n" + chapters[chapter_index]["place"] + "\n\n" + person["name"] + ": " + line + "\n\n")
		show_dialogue_choices(person, person.get("choices", []))

	def show_dialogue_choices(person, choices):
		for index, button in enumerate(choice_buttons):
			button.SetVisible(index < len(choices))
			if index < len(choices):
				choice = choices[index]
				button.SetText(choice["label"])
				button.SetHotKey(str(index + 1), 0, True)
				button.OnPress(lambda choice=choice, person=person: choose_dialogue(person, choice))
		dialogue_state["has_choices"] = bool(choices)
		journal_button.SetVisible(not bool(choices))

	def choose_dialogue(person, choice):
		was_followup = dialogue_state["must_finish_followup"]
		GemRB.SetGlobal(choice["flag"], "GLOBAL", choice["value"])
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		if was_followup:
			record_journal_event(dialogue_state["followup_journal"], chapter["act"])
			dialogue_state["must_finish_followup"] = False
			dialogue_state["followup_journal"] = None
		followup = choice.get("followup")
		if followup:
			dialogue_state["must_finish_followup"] = True
			dialogue_state["followup_journal"] = followup.get("journal")
			message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n" + person["name"] + ": " + followup["line"] + "\n\n")
			show_dialogue_choices(person, followup["choices"])
			return
		record_journal_event(choice.get("journal"), chapter["act"])
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n")
		dialogue_state["has_choices"] = False
		for button in choice_buttons:
			button.SetVisible(False)
		journal_button.SetVisible(True)

	def record_journal_event(event, act):
		if event and not GemRB.GetGameVar(event["flag"]):
			GemRB.SetJournalEntry(event["text"], event["section"], act)
			GemRB.SetGlobal(event["flag"], "GLOBAL", 1)

	def record_journal_entry(chapter, beat):
		record_journal_event(beat.get("journal"), chapter["act"])

	def render_journal():
		entries = []
		section_names = {1: "QUEST", 2: "RESOLVED", 4: "JOURNAL"}
		for act in sorted({chapter["act"] for chapter in chapters}):
			for section, label in section_names.items():
				for index in range(GemRB.GetJournalSize(act, section)):
					entry = GemRB.GetJournalEntry(act, index, section)
					entries.append((entry["GameTime"], act, label, GemRB.GetString(entry["Text"])))
		entries.sort(key=lambda entry: entry[0])
		if not entries:
			return "TERRALUM JOURNAL\n\nNo entries yet. Begin the search in Alsperia."
		lines = ["TERRALUM JOURNAL", ""]
		for _, act, label, text in entries:
			lines.extend((f"ACT {act}  |  {label}", text, ""))
		lines.append("Press J or CLOSE LOG to return to the scene.")
		return "\n".join(lines)

	def toggle_journal():
		if not journal_state["open"] and dialogue_state["has_choices"]:
			return
		journal_state["open"] = not journal_state["open"]
		if journal_state["open"]:
			journal_button.SetText("CLOSE")
			message.SetText(render_journal())
			action.SetText("CLOSE LOG")
			action.OnPress(toggle_journal)
			return
		journal_button.SetText("JOURNAL")
		action.OnPress(advance)
		show()
	def enemy_alive(enemy):
		try:
			return not GemRB.GetPlayerStat(enemy, IE_STATE_ID) & STATE_DEAD
		except RuntimeError:
			# GemRB may remove the actor once its death animation ends.
			return False

	def narrate():
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		if chapter.get("voice"):
			GemRB.PlaySound(chapter["voice"], "GUI", 0, 0, 4)

	def show():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		if chapter["area"] == "tl0019" and beat_index == 1:
			river_route = 1 if (GemRB.GetGameVar("TLTRAVELKIT") == 2
							and GemRB.GetGameVar("TLRIVER") == 1) else 2
			GemRB.SetGlobal("TLRIVERROUTE", "GLOBAL", river_route)
		record_journal_entry(chapter, beat)
		journal_button.SetVisible(True)
		journal_button.SetText("JOURNAL")
		dialogue_state["has_choices"] = False
		for button in choice_buttons:
			button.SetVisible(False)
		beat_text = beat["text"]
		if chapter["area"] == "tl0002" and beat_index == 0:
			lead = GemRB.GetGameVar("TLMARALEAD")
			if lead == 1:
				beat_text = "Mara's ledger marks the pale stones as a safe route around the ruined watchpost."
			elif lead == 2:
				beat_text = "Edmon's waywarden caught up with us. His patrol will draw the stalker away from the road."
			if GemRB.GetGameVar("TLLIBRARYCLUE") == 1:
				if lead == 2:
					beat_text = "Inessa's index confirms the pale stones, and Edmon's waywarden leads the patrol around the watchpost."
				else:
					beat_text = "Inessa's copied rune index confirms the pale stones. We can skirt the ruined watchpost."
		for route in beat.get("routes", []):
			if GemRB.GetGameVar(route["flag"]) == route["value"]:
				beat_text = route["text"]
				break
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + beat["speaker"] + ": " + beat_text + "\n\n")
		action.SetText(beat["action"].upper() if len(beat["action"]) < 11 else "CONTINUE")
		action.OnPress(advance)
		voice.SetDisabled(not chapter.get("voice"))

	def advance():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		beat = chapter["beats"][beat_index]
		if dialogue_state["must_finish_followup"]:
			message.Append("\n\nFinish this conversation before continuing.")
			return
		if chapter["area"] == "tl0003" and beat_index == 0 and not GemRB.GetGameVar("TLLORIANPURPOSE"):
			message.Append("\n\nDorian waits for your answer. Speak with him before approaching the guardian.")
			return
		if chapter["area"] == "tl0010" and beat_index == 0 and not GemRB.GetGameVar("TLGALLERY"):
			message.Append("\n\nThe inscription needs an answer. Speak with the Gallery Keeper before leaving the sealed niches.")
			return
		if chapter["area"] == "tl0018" and beat_index == 0 and not GemRB.GetGameVar("TLROYALORDER"):
			message.Append("\n\nThe dispatch remains to be decided. Speak with Archivist Leora before leaving the archive.")
			return
		if chapter["area"] == "tl0019" and beat_index == 0 and not GemRB.GetGameVar("TLRIVER"):
			message.Append("\n\nEren is still on the far bank. Choose how to cross before leaving the river.")
			return
		if chapter["area"] == "tl0017" and beat_index == 0 and not GemRB.GetGameVar("TLTRAVELKIT"):
			message.Append("\n\nThe horse is ready, but the pack still needs a field kit. Speak with Stablemaster Edda before riding west.")
			return
		if (chapter["area"] == "tl0006" and beat.get("encounter_if")
				and not GemRB.GetGameVar("TLARCHIVEWARD")):
			message.Append("\n\nBefore calling the Index Warden, speak with Archivist Nera and decide what to do with the sealed folio.")
			return
		if chapter["area"] == "tl0020" and beat_index == 0 and not GemRB.GetGameVar("TLBRIEFING"):
			message.Append("\n\nEaldrin is waiting for your decision about which record the expedition will carry.")
			return
		if chapter["area"] == "tl0021" and beat_index == 0 and not GemRB.GetGameVar("TLWARDING"):
			message.Append("\n\nCelene is waiting for your containment rule before the party enters the vault.")
			return
		if chapter["area"] == "tl0022" and beat_index == 0 and not GemRB.GetGameVar("TLELDRADOR"):
			message.Append("\n\nVaelthira is waiting for the party to choose how its first account of the sanctuary will be gathered.")
			return
		if chapter["area"] == "tl0023" and beat_index == 0 and not GemRB.GetGameVar("TLSANCTUARY"):
			message.Append("\n\nMereth is waiting for the party to choose an approach to the sealed threshold.")
			return
		if (chapter["area"] == "tl0002" and beat.get("encounter")
				and (GemRB.GetGameVar("TLMARALEAD") == 1 or GemRB.GetGameVar("TLLIBRARYCLUE") == 1
				     or (GemRB.GetGameVar("TLTRAVELKIT") == 1 and GemRB.GetGameVar("TLHUNTER") == 1)
				     or (GemRB.GetGameVar("TLTRAVELKIT") == 2 and GemRB.GetGameVar("TLHUNTERTRACK") == 1)
				     or (GemRB.GetGameVar("TLMARALEAD") == 2 and GemRB.GetGameVar("TLROYALORDER") == 1)
				     or GemRB.GetGameVar("TLRIVERROUTE") == 1)):
			GemRB.SetGlobal("TLMISTWOODSAFE", "GLOBAL", 1)
			GemRB.SetGlobal("TLBEAT", "GLOBAL", beat_index + 1)
			show()
			return
		encounter_gate = beat.get("encounter_if")
		if encounter_gate and GemRB.GetGameVar(encounter_gate["flag"]) != encounter_gate["value"]:
			GemRB.SetGlobal("TLBEAT", "GLOBAL", beat_index + 1)
			show()
			return
		enemy = GemRB.GetGameVar("TLENEMY")
		group = beat.get("enemies", [])
		if group:
			group_actors = []
			spawned_names = []
			for member in group:
				actor = GemRB.GetGameVar(member["flag"])
				if not actor:
					position = member["position"]
					actor = GemRB.CreateCreature(1, member["creature"], position[0], position[1])
					GemRB.SetGlobal(member["flag"], "GLOBAL", actor)
					GemRB.SetPlayerName(actor, member["name"], 0)
					GemRB.SetPlayerStat(actor, IE_EA, ENEMY)
					GemRB.ExecuteString("Attack(Player1)", actor)
					spawned_names.append(member["name"])
				group_actors.append((member["name"], actor))
			if spawned_names:
				if not enemy:
					GemRB.SetGlobal("TLENEMY", "GLOBAL", group_actors[0][1])
				message.Append("\n\nENCOUNTER: " + " and ".join(spawned_names) + " attack. Defeat them to continue.")
				return
			living = [name for name, actor in group_actors if enemy_alive(actor)]
			if living:
				message.Append("\n\nENCOUNTER: Defeat " + " and ".join(living) + " to continue.")
				return
			for member in group:
				GemRB.SetGlobal(member["flag"], "GLOBAL", 0)
			GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
			GemRB.SetGlobal("TLMISTWOODVICTORY", "GLOBAL", 1)
			record_journal_event(beat.get("victory_journal"), chapter["act"])
			enemy = 0
		if "encounter" in beat and not enemy and not group:
			# A beat may turn a scene NPC hostile; otherwise, use the demo CRE
			# as an open-licensed template for this encounter.
			actor_flag = beat.get("encounter_actor_flag")
			if actor_flag:
				enemy = GemRB.GetGameVar(actor_flag)
				if not enemy:
					message.Append("\n\nThe guardian is absent from the scene. Reload the area before continuing.")
					return
			else:
				spawn = beat.get("spawn_position")
				if spawn:
					enemy = GemRB.CreateCreature(1, "riddler", spawn[0], spawn[1])
				else:
					enemy = GemRB.CreateCreature(1, "riddler")
			GemRB.SetGlobal("TLENEMY", "GLOBAL", enemy)
			if not actor_flag:
				GemRB.SetPlayerName(enemy, beat["encounter"], 0)
			GemRB.SetPlayerStat(enemy, IE_EA, ENEMY)
			GemRB.ExecuteString("Attack(Player1)", enemy)
			message.Append("\n\nENCOUNTER: " + beat["encounter"] + " emerges. Defeat it to continue.")
			action.SetText("CONTINUE")
			return
		if "encounter" in beat and not group and enemy_alive(enemy):
			message.Append("\n\n" + beat["encounter"] + " still stands. Defeat it to continue.")
			return
		if "encounter" in beat and not group and enemy:
			record_journal_event(beat.get("victory_journal"), chapter["act"])
		GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
		beat_index += 1
		if beat_index >= len(chapter["beats"]):
			chapter_index += 1
			beat_index = 0
			if chapter_index >= len(chapters):
				message.SetText("[cap]T[/cap]ERRALUM  |  TO BE CONTINUED\n\nThe party has reached the lower sanctuary threshold. Its inner gate remains sealed; Eldrador's Tear has not been entered or resolved.")
				action.SetText("FINISHED")
				action.OnPress(lambda: None)
				return
			GemRB.SetGlobal("TLCHAP", "GLOBAL", chapter_index)
			GemRB.SetGlobal("TLBEAT", "GLOBAL", 0)
			GemRB.SetVar("CHAPTER", chapters[chapter_index]["act"])
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
	journal_button.OnPress(toggle_journal)
	voice.OnPress(narrate)
	talk.OnPress(talk_to_scene_npc)
	action.SetHotKey(GEM_RETURN, 0, True)
	GemRB.LoadMusicPL(chapters[GemRB.GetGameVar("TLCHAP")]["music"], 1)
	initial_chapter = GemRB.GetGameVar("TLCHAP")
	GemRB.SetTimedEvent(lambda: spawn_cast(initial_chapter), 1)
	show()
	narrate()


def UpdateControlStatus():
	pass


def ToggleMenuWindow():
	pass
