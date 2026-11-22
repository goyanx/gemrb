# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Data-driven Terralum campaign controls on the GemRB message panel."""

import GemRB
import Story
import GUICommon
import GUIMA
import GUIINV
import NPCPalette
from GUIDefines import *
from ie_stats import (IE_EA, IE_STATE_ID, STATE_DEAD, ENEMY, NEUTRAL,
					  IE_HAIR_COLOR, IE_MAJOR_COLOR, IE_MINOR_COLOR,
					  IE_HITPOINTS, IE_MAXHITPOINTS, IE_DAMAGEBONUS, IE_TOHIT)

NPC_PALETTES_BY_NAME = NPCPalette.palettes_by_name(Story.cast_catalog())
PORTRAIT_ALIASES = {
	"Archivist Mara": "MARAAV",
	"King Edmon": "EDMONV",
	"Queen Alisande": "ALISAV",
	"Algoreth": "ALGOVR",
}
_defeat_ui = None


def ShowDefeat():
	"""Show a game-over state using the campaign panel when the demo has no death CHU."""
	if not _defeat_ui:
		return False
	GemRB.GamePause(1, 0)
	ui = _defeat_ui
	ui["message"].SetText("TERRALUM  |  THE PARTY HAS FALLEN\n\nThe road has taken its toll. Load a named save to return to your last safe place.")
	ui["load_state"]["defeated"] = True
	for control in (ui["attack"], ui["cast"], ui["talk"], ui["voice"], ui["journal"], ui["save"], ui["party"], ui["hero"]):
		control.SetVisible(False)
	for button in ui["choices"]:
		button.SetVisible(False)
	ui["action"].SetVisible(False)
	ui["portrait"].SetVisible(False)
	ui["load"].SetVisible(True)
	ui["load"].SetText("LOAD")
	ui["load"].OnPress(ui["open_load"])
	return True


def _style(button, width=None):
	if width is not None:
		frame = button.GetFrame()
		frame["w"] = width
		button.SetFrame(frame)
	button.SetFlags(IE_GUI_BUTTON_NO_IMAGE, OP_OR)
	button.SetBorder(0, {"r": 196, "g": 164, "b": 105, "a": 255}, 1, 0)


def OnLoad():
	global _defeat_ui
	window = GemRB.LoadWindow(0, GUICommon.GetWindowPack(), WINDOW_BOTTOM | WINDOW_HCENTER)
	window.SetFlags(WF_BORDERLESS | IE_GUI_VIEW_IGNORE_EVENTS, OP_OR)
	window.AddAlias("MSGWIN")
	window.AddAlias("HIDE_CUT", 0)
	message = window.GetControl(0)
	message.SetFlags(IE_GUI_TEXTAREA_AUTOSCROLL | IE_GUI_TEXTAREA_HISTORY)
	message.AddAlias("MsgSys", 0)
	message.AddAlias("MTA", 0)
	message.SetColor(ColorRed, TA_COLOR_OPTIONS)
	message.SetColor(ColorWhite, TA_COLOR_HOVER)
	message_frame = message.GetFrame()
	message_frame["x"] += 100
	message_frame["w"] -= 100
	message.SetFrame(message_frame)

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
	voice = window.CreateButton(10, 580, 183, 70, 34)
	_style(voice)
	voice.SetText("NARRATE")
	voice.SetHotKey("n", 0, True)
	cast = window.CreateButton(11, 440, 183, 65, 34)
	_style(cast)
	cast.SetText("CAST")
	cast.SetHotKey("c", 0, True)
	actor_talk = window.CreateButton(16, 510, 183, 65, 34)
	_style(actor_talk)
	actor_talk.SetText("TALK")
	actor_talk.SetHotKey("t", 0, True)
	attack_button = window.CreateButton(20, 183, 183, 150, 34)
	_style(attack_button)
	attack_button.SetText("ATTACK")
	attack_button.SetHotKey("a", 0, True)
	hero_button = window.CreateButton(22, 655, 183, 65, 34)
	_style(hero_button)
	hero_button.SetText("HERO")
	hero_button.SetHotKey("1", 0, True)
	hero_button.SetVisible(False)
	party_button = window.CreateButton(21, 722, 183, 78, 34)
	_style(party_button)
	party_button.SetText("TESSA")
	party_button.SetHotKey("2", 0, True)
	party_button.SetVisible(False)
	save_button = window.CreateButton(18, 10, 183, 78, 34)
	_style(save_button)
	save_button.SetText("SAVE")
	load_button = window.CreateButton(19, 94, 183, 78, 34)
	_style(load_button)
	load_button.SetText("LOAD")
	choice_buttons = []
	for index, x in enumerate((10, 183, 356)):
		button = window.CreateButton(12 + index, x, 183, 160, 34)
		_style(button)
		button.SetVisible(False)
		choice_buttons.append(button)
	journal_button = window.CreateButton(15, 345, 183, 90, 34)
	_style(journal_button)
	journal_button.SetText("JOURNAL")
	journal_button.SetHotKey("j", 0, True)
	portrait_button = window.CreateButton(17, 12, 42, 82, 100)
	portrait_button.SetFlags(IE_GUI_BUTTON_PICTURE | IE_GUI_BUTTON_NORMAL, OP_SET)
	portrait_button.SetBorder(0, {"r": 196, "g": 164, "b": 105, "a": 255}, 1, 0)
	portrait_button.SetVisible(False)
	journal_state = {"open": False}
	dialogue_state = {"has_choices": False, "must_finish_followup": False, "followup_journal": None}
	load_state = {"games": (), "page": 0, "selected": None}
	combat_state = {"original_tohit": {}}

	chapters = Story.chapters()
	cast_index = {"line": -1}

	def set_portrait(person):
		portrait = PORTRAIT_ALIASES.get(person["name"], person.get("portrait")) if person else None
		if portrait:
			portrait_button.SetPicture(portrait + "M")
			portrait_button.SetVisible(True)
		else:
			portrait_button.SetVisible(False)

	def spawn_cast(chapter_index):
		chapter = chapters[chapter_index]
		if GemRB.GetCurrentArea().lower() != chapter["area"]:
			return
		if GemRB.GetGameVar("TLCAST") == chapter_index + 1:
			return
		for person in Story.cast(chapter["area"]):
			actor = GemRB.CreateCreature(1, person.get("avatar_creature", person["creature"]),
									 person["position"][0], person["position"][1])
			GemRB.SetPlayerName(actor, person["name"], 0)
			if person["creature"] in ("protagon", "riddler"):
				palette = NPC_PALETTES_BY_NAME[person["name"]]
				GemRB.SetPlayerStat(actor, IE_HAIR_COLOR, palette[0])
				GemRB.SetPlayerStat(actor, IE_MAJOR_COLOR, palette[1])
				GemRB.SetPlayerStat(actor, IE_MINOR_COLOR, palette[2])
			GemRB.SetPlayerStat(actor, IE_EA, NEUTRAL)
			if person.get("dialog"):
				GemRB.SetPlayerDialog(actor, person["dialog"])
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
		GemRB.GameControlSetTargetMode(TARGET_MODE_NONE)
		if journal_state["open"]:
			journal_state["open"] = False
			journal_button.SetText("JOURNAL")
			show()
		chapter_index = GemRB.GetGameVar("TLCHAP")
		chapter = chapters[chapter_index]
		people = Story.cast(chapter["area"])
		cast_index["line"] = (cast_index["line"] + 1) % len(people)
		person = people[cast_index["line"]]
		set_portrait(person)
		line = person.get("line")
		if chapter["area"] == "tl0002" and person.get("route_lines"):
			line = person["route_lines"].get(str(GemRB.GetGameVar("TLMARALEAD")), line)
		for response in person.get("responses", []):
			conditions = response.get("when")
			if conditions is not None:
				matches = all(GemRB.GetGameVar(condition["flag"]) == condition["value"]
							  for condition in conditions)
			else:
				matches = GemRB.GetGameVar(response["flag"]) == response["value"]
			if matches:
				line = response["line"]
				break
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapters[chapter_index]["title"] + "\n" + chapters[chapter_index]["place"] + "\n\n" + person["name"] + ": " + line + "\n\n")
		choices = person.get("choices", [])
		# The gallery's required seal sequence and final response are authored in
		# the Keeper's native DLG. Do not expose a panel shortcut around the puzzle.
		if chapter["area"] == "tl0010":
			choices = []
		if choices and GemRB.GetGameVar(choices[0]["flag"]):
			choices = []
		show_dialogue_choices(person, choices)

	def begin_actor_talk():
		if dialogue_state["must_finish_followup"]:
			message.Append("\n\nFinish this conversation before speaking with another NPC.")
			return
		if journal_state["open"]:
			journal_state["open"] = False
			journal_button.SetText("JOURNAL")
			show()
		GemRB.GameSelectPC(1, True, SELECT_REPLACE)
		GemRB.GameControlSetTargetMode(TARGET_MODE_TALK, GA_NO_DEAD | GA_NO_ENEMY | GA_NO_HIDDEN)
		message.Append("\n\nChoose a scene NPC to speak with.")

	def begin_actor_attack():
		if dialogue_state["has_choices"] or journal_state["open"]:
			return
		GemRB.GameControlSetTargetMode(TARGET_MODE_ATTACK,
									  GA_NO_DEAD | GA_NO_SELF | GA_NO_HIDDEN | GA_NO_NEUTRAL)
		message.Append("\n\nClick a hostile creature to attack. Clicking open ground only sets a move marker.")

	def select_tessa():
		if GemRB.GetPartySize() > 1:
			GemRB.GameSelectPC(2, True, SELECT_REPLACE)
			message.Append("\n\nScout Tessa selected. Choose ATTACK, then select a target.")

	def select_lead():
		GemRB.GameSelectPC(1, True, SELECT_REPLACE)
		message.Append("\n\nAlgoreth selected. Choose ATTACK, then select a target.")

	def configure_party_controls():
		show_party = GemRB.GetPartySize() > 1
		hero_button.SetVisible(show_party)
		party_button.SetVisible(show_party)

	party_button.OnPress(select_tessa)
	hero_button.OnPress(select_lead)

	def save_game():
		GUICommon.SetSaveDir()
		games = GemRB.GetSaveGames()
		existing_names = {game.GetName() for game in games}
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		place = chapter["place"].replace("/", "-").replace("\\", "-")
		serial = 1
		while "Terralum {:03d} - {}".format(serial, place) in existing_names:
			serial += 1
		save_name = "Terralum {:03d} - {}".format(serial, place)
		result = GemRB.SaveGame(None, save_name, -1, GemRB.GetGamePreview())
		if result == 0:
			saved_text = "TERRALUM  |  GAME SAVED\n\n" + save_name + "\n\nYour party, current area, campaign decisions, and journal have been saved."
			if dialogue_state["must_finish_followup"]:
				saved_text += "\n\nChoose a response to finish the open conversation before continuing."
			message.SetText(saved_text)
		elif result in (3, 7):
			message.SetText("TERRALUM  |  SAVE UNAVAILABLE\n\nYou cannot save during combat or while enemies are close. Finish the encounter, then save from a safe place.")
		else:
			message.SetText("TERRALUM  |  SAVE FAILED\n\nGemRB could not write the save (error {}). Check the game log for details.".format(result))
		action.SetText("CONTINUE")
		action.OnPress(advance)

	def load_game(save):
		GemRB.SetVar("PlayMode", 0)
		GemRB.LoadGame(save)
		GemRB.EnterGame()
		GemRB.HardEndPL()

	def confirm_load(save):
		load_state["selected"] = save
		message.SetText("TERRALUM  |  LOAD SAVED GAME\n\nLoad '" + save.GetName() + "'?\n\nYour current unsaved progress will be replaced.")
		for index, button in enumerate(choice_buttons):
			button.SetVisible(index < 2)
		attack_button.SetVisible(False)
		if load_state["selected"] is not None:
			choice_buttons[0].SetText("LOAD")
			choice_buttons[0].OnPress(lambda _button=None, save=save: (GemRB.QuitGame(), GemRB.SetTimer(lambda: load_game(save), 0, 0)))
			choice_buttons[1].SetText("CANCEL")
			choice_buttons[1].OnPress(show)
		journal_button.SetVisible(False)
		cast.SetVisible(False)
		actor_talk.SetVisible(False)
		voice.SetVisible(False)
		save_button.SetVisible(False)
		load_button.SetVisible(False)
		hero_button.SetVisible(False)
		party_button.SetVisible(False)
		action.SetText("CANCEL")
		action.SetVisible(False)
		action.OnPress(show)

	def show_load_page():
		games = load_state["games"]
		page = load_state["page"]
		start = page * len(choice_buttons)
		page_games = games[start:start + len(choice_buttons)]
		page_count = (len(games) + len(choice_buttons) - 1) // len(choice_buttons)
		message.SetText("TERRALUM  |  SAVED GAMES  |  PAGE {} OF {}\n\nSelect a save to continue from it.".format(page + 1, page_count))
		for index, button in enumerate(choice_buttons):
			button.SetVisible(index < len(page_games))
			if index < len(page_games):
				save = page_games[index]
				button.SetText(save.GetName()[:22])
				button.OnPress(lambda _button=None, save=save: confirm_load(save))
		journal_button.SetVisible(True)
		attack_button.SetVisible(False)
		journal_button.SetText("CANCEL")
		journal_button.OnPress(show)
		cast.SetVisible(page_count > 1)
		cast.SetText("PREV")
		cast.OnPress(lambda: change_load_page(-1))
		actor_talk.SetVisible(False)
		voice.SetVisible(False)
		save_button.SetVisible(False)
		load_button.SetVisible(False)
		hero_button.SetVisible(False)
		party_button.SetVisible(False)
		action.SetText("NEXT")
		action.SetVisible(page_count > 1)
		action.OnPress(lambda: change_load_page(1))

	def change_load_page(direction):
		page_count = (len(load_state["games"]) + len(choice_buttons) - 1) // len(choice_buttons)
		load_state["page"] = (load_state["page"] + direction) % page_count
		show_load_page()

	def restart_game():
		GemRB.QuitGame()
		GemRB.SetNextScript("Start")

	def open_load_window():
		GUICommon.SetSaveDir()
		games = list(GemRB.GetSaveGames())
		if not games:
			if load_state.get("defeated"):
				message.SetText("TERRALUM  |  NO SAFE SAVE FOUND\n\nStart a new journey in Alsperia to try again.")
				action.SetText("RESTART")
				action.OnPress(restart_game)
			else:
				message.SetText("TERRALUM  |  NO SAVED GAMES\n\nPress SAVE to create a named save before loading a game.")
				action.SetText("CONTINUE")
				action.OnPress(advance)
			action.SetVisible(True)
			return
		games.sort(key=lambda game: (game.GetGameDate(), game.GetName()), reverse=True)
		load_state["games"] = tuple(games)
		load_state["page"] = 0
		show_load_page()

	_defeat_ui = {
		"message": message,
		"attack": attack_button,
		"party": party_button,
		"hero": hero_button,
		"cast": cast,
		"talk": actor_talk,
		"voice": voice,
		"journal": journal_button,
		"save": save_button,
		"choices": choice_buttons,
		"action": action,
		"portrait": portrait_button,
		"load": load_button,
		"load_state": load_state,
		"open_load": open_load_window,
	}

	def show_dialogue_choices(person, choices):
		pending_followup = dialogue_state["must_finish_followup"]
		choice_positions = (183, 356, 529) if pending_followup else (10, 183, 356)
		for index, (button, x) in enumerate(zip(choice_buttons, choice_positions)):
			frame = button.GetFrame()
			frame["x"] = x
			button.SetFrame(frame)
			button.SetVisible(index < len(choices))
			if index < len(choices):
				choice = choices[index]
				button.SetText(choice["label"])
				button.SetHotKey(str(index + 1), 0, True)
				button.OnPress(lambda _button=None, choice=choice, person=person: choose_dialogue(person, choice))
		dialogue_state["has_choices"] = bool(choices)
		attack_button.SetVisible(not bool(choices))
		hero_button.SetVisible(not bool(choices) and GemRB.GetPartySize() > 1)
		party_button.SetVisible(not bool(choices) and GemRB.GetPartySize() > 1)
		journal_button.SetVisible(not bool(choices))
		cast.SetVisible(not bool(choices))
		# Keep named saves available during a required second-stage response.
		# Its NPC/choice indexes are persisted in globals and restored by OnLoad.
		save_button.SetVisible(not bool(choices) or pending_followup)
		load_button.SetVisible(not bool(choices) or pending_followup)
		if pending_followup:
			actor_talk.SetVisible(False)
			voice.SetVisible(False)

	def choose_dialogue(person, choice):
		set_portrait(person)
		was_followup = dialogue_state["must_finish_followup"]
		GemRB.SetGlobal(choice["flag"], "GLOBAL", choice["value"])
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		if was_followup:
			record_journal_event(dialogue_state["followup_journal"], chapter["act"])
			dialogue_state["must_finish_followup"] = False
			dialogue_state["followup_journal"] = None
			GemRB.SetGlobal("TLFOLLOWPENDING", "GLOBAL", 0)
			GemRB.SetGlobal("TLFOLLOWNPC", "GLOBAL", 0)
			GemRB.SetGlobal("TLFOLLOWCHOICE", "GLOBAL", 0)
		followup = choice.get("followup")
		if followup:
			dialogue_state["must_finish_followup"] = True
			dialogue_state["followup_journal"] = followup.get("journal")
			people = Story.cast(chapter["area"])
			person_index = next(index for index, person_data in enumerate(people)
							if person_data["name"] == person["name"])
			GemRB.SetGlobal("TLFOLLOWPENDING", "GLOBAL", 1)
			GemRB.SetGlobal("TLFOLLOWNPC", "GLOBAL", person_index)
			GemRB.SetGlobal("TLFOLLOWCHOICE", "GLOBAL", person["choices"].index(choice))
			message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n" + person["name"] + ": " + followup["line"] + "\n\n")
			show_dialogue_choices(person, followup["choices"])
			return
		record_journal_event(choice.get("journal"), chapter["act"])
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n")
		dialogue_state["has_choices"] = False
		for button in choice_buttons:
			button.SetVisible(False)
		attack_button.SetVisible(True)
		journal_button.SetVisible(True)
		cast.SetVisible(True)
		save_button.SetVisible(True)
		load_button.SetVisible(True)
		configure_party_controls()

	def record_journal_event(event, act):
		if event and not GemRB.GetGameVar(event["flag"]):
			GemRB.SetGlobal("CHAPTER", "GLOBAL", act)
			GemRB.SetJournalEntry(event["text"], event["section"], 0)
			GemRB.SetGlobal(event["flag"], "GLOBAL", 1)

	def record_journal_entry(chapter, beat):
		record_journal_event(beat.get("journal"), chapter["act"])

	def reconcile_npc_journal_events(chapter):
		"""Record scene choice events set by a native DLG transition."""
		for person in Story.cast(chapter["area"]):
			for choice in person.get("choices", []):
				if choice.get("journal") and GemRB.GetGameVar(choice["flag"]) == choice["value"]:
					record_journal_event(choice["journal"], chapter["act"])
				followup = choice.get("followup")
				if followup and followup.get("journal"):
					for followup_choice in followup.get("choices", []):
						if GemRB.GetGameVar(followup_choice["flag"]) == followup_choice["value"]:
							record_journal_event(followup["journal"], chapter["act"])

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
			attack_button.SetVisible(False)
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

	def restore_pending_followup():
		if not GemRB.GetGameVar("TLFOLLOWPENDING"):
			return
		chapter = chapters[GemRB.GetGameVar("TLCHAP")]
		if GemRB.GetCurrentArea().lower() != chapter["area"]:
			return
		people = Story.cast(chapter["area"])
		person_index = GemRB.GetGameVar("TLFOLLOWNPC")
		choice_index = GemRB.GetGameVar("TLFOLLOWCHOICE")
		if not (0 <= person_index < len(people)):
			return
		person = people[person_index]
		set_portrait(person)
		choices = person.get("choices", [])
		if not (0 <= choice_index < len(choices)):
			return
		choice = choices[choice_index]
		followup = choice.get("followup")
		if not followup:
			return
		dialogue_state["must_finish_followup"] = True
		dialogue_state["followup_journal"] = followup.get("journal")
		message.SetText("[cap]T[/cap]ERRALUM  |  " + chapter["title"] + "\n" + chapter["place"] + "\n\n" + person["name"] + ": " + choice["reply"] + "\n\n" + person["name"] + ": " + followup["line"] + "\n\n")
		show_dialogue_choices(person, followup["choices"])

	def show():
		chapter_index = GemRB.GetGameVar("TLCHAP")
		beat_index = GemRB.GetGameVar("TLBEAT")
		chapter = chapters[chapter_index]
		# GemRB's AddJournalEntry reads the game-script CHAPTER global; SetVar
		# only updates the separate GUI dictionary and does not select a journal page.
		GemRB.SetGlobal("CHAPTER", "GLOBAL", chapter["act"])
		beat = chapter["beats"][beat_index]
		person = next((person for person in Story.cast(chapter["area"])
					   if person["name"] == beat["speaker"]), None)
		set_portrait(person)
		if chapter["area"] == "tl0019" and beat_index == 1:
			river_route = 1 if (GemRB.GetGameVar("TLTRAVELKIT") == 2
							and GemRB.GetGameVar("TLRIVER") == 1) else 2
			GemRB.SetGlobal("TLRIVERROUTE", "GLOBAL", river_route)
		record_journal_entry(chapter, beat)
		reconcile_npc_journal_events(chapter)
		journal_button.SetVisible(True)
		journal_button.SetText("JOURNAL")
		journal_button.OnPress(toggle_journal)
		dialogue_state["has_choices"] = False
		for button in choice_buttons:
			button.SetVisible(False)
		attack_button.SetVisible(True)
		cast.SetVisible(True)
		configure_party_controls()
		actor_talk.SetVisible(True)
		actor_talk.OnPress(begin_actor_talk)
		voice.SetVisible(True)
		voice.OnPress(narrate)
		save_button.SetVisible(True)
		load_button.SetVisible(True)
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
		action.SetVisible(True)
		action.OnPress(advance)
		voice.SetDisabled(not chapter.get("voice"))

	def begin_group_combat(actors, companion_flag=None, companion_actor=None, party_to_hit=None):
		# Start combat after the one-round delay so a joining companion is in
		# the party before GemRB initializes the active initiative list.
		if party_to_hit is not None:
			for actor in (1, companion_actor):
				if not actor:
					continue
				if actor not in combat_state["original_tohit"]:
					combat_state["original_tohit"][actor] = GemRB.GetPlayerStat(actor, IE_TOHIT)
				if combat_state["original_tohit"][actor] > party_to_hit:
					GemRB.SetPlayerStat(actor, IE_TOHIT, party_to_hit)
		for index, (_name, enemy_actor) in enumerate(actors):
			target = "Player2" if index % 2 and GemRB.GetPartySize() > 1 else "Player1"
			GemRB.ExecuteString("Attack(" + target + ")", enemy_actor)
		if companion_flag:
			GemRB.SetGlobal(companion_flag, "GLOBAL", 1)
		configure_party_controls()

	def restore_combat_stats():
		for actor, to_hit in combat_state["original_tohit"].items():
			GemRB.SetPlayerStat(actor, IE_TOHIT, to_hit)
		combat_state["original_tohit"].clear()

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
		if chapter["area"] == "tl0025" and beat_index == 1 and not GemRB.GetGameVar("TLRETURNMARK"):
			message.Append("\n\nPell is waiting for the route record. Speak with him and decide what the next travellers should learn.")
			return
		if chapter["area"] == "tl0026" and beat_index == 0 and not GemRB.GetGameVar("TLARCHIVETRIAL"):
			message.Append("\n\nThalor is waiting for the three warders' accounts. Hear Vorsath, Elaris, and Thalorix, then return to record your principle.")
			return
		if chapter["area"] == "tl0024" and beat_index == 1 and not GemRB.GetGameVar("TLRELAY"):
			message.Append("\n\nThe relay is still unassigned. Speak with Orla and decide whether to signal the west patrol.")
			return
		if chapter["area"] == "tl0004" and beat_index == 1 and not GemRB.GetGameVar("TLRETURNMARK"):
			message.Append("\n\nCourier Pell’s return report is missing. Speak with Queen Alisande to review the Mistwood record.")
			return
		if chapter["area"] == "tl0011" and beat_index == 1 and not GemRB.GetGameVar("TLWITNESS"):
			message.Append("\n\nThe council docket is unfinished. Speak with Royal Scribe Oren and decide how the route and scroll accounts should be filed.")
			return
		if chapter["area"] == "tl0010" and beat_index == 0 and not GemRB.GetGameVar("TLGALLERY"):
			message.Append("\n\nThe three-mark seal still waits. Speak with the Gallery Keeper, solve its order, and record your answer before leaving the sealed niches.")
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
					hit_points = member.get("hit_points")
					if hit_points:
						GemRB.SetPlayerStat(actor, IE_MAXHITPOINTS, hit_points)
						GemRB.SetPlayerStat(actor, IE_HITPOINTS, hit_points)
					damage_bonus = member.get("damage_bonus")
					if damage_bonus is not None:
						GemRB.SetPlayerStat(actor, IE_DAMAGEBONUS, damage_bonus)
					spawned_names.append(member["name"])
				group_actors.append((member["name"], actor))
			companion = beat.get("companion")
			if companion and not GemRB.GetGameVar(companion["triggered_flag"]):
				actor = GemRB.GetGameVar(companion["actor_flag"])
				if actor:
					GemRB.ExecuteString("JoinParty()", actor)
					GemRB.SetGlobal(companion["triggered_flag"], "GLOBAL", 2)
					GemRB.SetTimedEvent(lambda actors=tuple(group_actors), flag=companion["triggered_flag"],
										ally=actor, to_hit=companion.get("party_to_hit"):
						begin_group_combat(actors, flag, ally, to_hit), 1)
					party_button.SetVisible(True)
					hero_button.SetVisible(True)
					message.Append("\n\n" + companion["join_line"])
				else:
					begin_group_combat(group_actors)
			elif spawned_names:
				begin_group_combat(group_actors)
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
			restore_combat_stats()
			GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
			GemRB.SetGlobal("TLMISTWOODVICTORY", "GLOBAL", 1)
			record_journal_event(beat.get("victory_journal"), chapter["act"])
			enemy = 0
		if "encounter" in beat and not enemy and not group:
			# A beat may turn a scene NPC hostile; otherwise, use the demo CRE
			# as an open-licensed template for this encounter.
			phases = beat.get("encounter_phases", [])
			phase_index = GemRB.GetGameVar("TLECHOPHASE") if phases else 0
			phase = phases[phase_index] if phases else {}
			actor_flag = phase.get("actor_flag", beat.get("encounter_actor_flag"))
			if actor_flag:
				enemy = GemRB.GetGameVar(actor_flag)
				if not enemy:
					message.Append("\n\nThe encounter actor is absent from the scene. Reload the area before continuing.")
					return
			else:
				spawn = phase.get("position", beat.get("spawn_position"))
				if spawn:
					enemy = GemRB.CreateCreature(1, "riddler", spawn[0], spawn[1])
				else:
					enemy = GemRB.CreateCreature(1, "riddler")
			GemRB.SetGlobal("TLENEMY", "GLOBAL", enemy)
			if not actor_flag:
				GemRB.SetPlayerName(enemy, phase.get("name", beat["encounter"]), 0)
			GemRB.SetPlayerStat(enemy, IE_EA, ENEMY)
			GemRB.ExecuteString("Attack(Player1)", enemy)
			encounter_name = phase.get("name", beat["encounter"])
			encounter_text = phase.get("text", encounter_name + " emerges.")
			message.Append("\n\nENCOUNTER: " + encounter_text + " Defeat it to continue.")
			action.SetText("CONTINUE")
			return
		if "encounter" in beat and not group and enemy_alive(enemy):
			phases = beat.get("encounter_phases", [])
			phase_index = GemRB.GetGameVar("TLECHOPHASE") if phases else 0
			encounter_name = phases[phase_index].get("name", beat["encounter"]) if phases else beat["encounter"]
			message.Append("\n\n" + encounter_name + " still stands. Defeat it to continue.")
			return
		if "encounter" in beat and not group and enemy:
			phases = beat.get("encounter_phases", [])
			phase_index = GemRB.GetGameVar("TLECHOPHASE") if phases else 0
			if phases and phase_index + 1 < len(phases):
				phase_index += 1
				phase = phases[phase_index]
				GemRB.SetGlobal("TLECHOPHASE", "GLOBAL", phase_index)
				actor_flag = phase.get("actor_flag")
				if actor_flag:
					enemy = GemRB.GetGameVar(actor_flag)
					if not enemy:
						GemRB.SetGlobal("TLENEMY", "GLOBAL", 0)
						message.Append("\n\nThe next echo is absent from the scene. Reload the area before continuing.")
						return
				else:
					spawn = phase.get("position")
					enemy = GemRB.CreateCreature(1, "riddler", spawn[0], spawn[1])
					GemRB.SetPlayerName(enemy, phase["name"], 0)
				GemRB.SetGlobal("TLENEMY", "GLOBAL", enemy)
				GemRB.SetPlayerStat(enemy, IE_EA, ENEMY)
				GemRB.ExecuteString("Attack(Player1)", enemy)
				message.Append("\n\nENCOUNTER: " + phase["text"] + " Defeat it to continue.")
				action.SetText("CONTINUE")
				return
			else:
				record_journal_event(beat.get("victory_journal"), chapter["act"])
				if phases:
					GemRB.SetGlobal("TLECHOPHASE", "GLOBAL", 0)
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
	attack_button.OnPress(begin_actor_attack)
	journal_button.OnPress(toggle_journal)
	voice.OnPress(narrate)
	cast.OnPress(talk_to_scene_npc)
	actor_talk.OnPress(begin_actor_talk)
	save_button.OnPress(save_game)
	load_button.OnPress(open_load_window)
	action.SetHotKey(GEM_RETURN, 0, True)
	GemRB.LoadMusicPL(chapters[GemRB.GetGameVar("TLCHAP")]["music"], 1)
	initial_chapter = GemRB.GetGameVar("TLCHAP")
	GemRB.SetTimedEvent(lambda: spawn_cast(initial_chapter), 1)
	show()
	restore_pending_followup()
	narrate()


def UpdateControlStatus():
	pass


def ToggleMenuWindow():
	pass
