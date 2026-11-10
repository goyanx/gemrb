#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Exercise every chapter transition without starting the graphical engine."""

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "gemrb" / "GUIScripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "terralum"))


class Control:
    def __init__(self):
        self.frame = {"x": 660, "y": 130, "w": 42, "h": 42}
        self.text = ""
        self.press = None
        self.hotkey = None
        self.disabled = False
        self.visible = True

    def __getattr__(self, name):
        if name in ("SetFlags", "AddAlias", "SetColor", "SetAnimation", "SetBorder"):
            return lambda *args: None
        raise AttributeError(name)

    def GetFrame(self):
        return self.frame

    def SetFrame(self, frame):
        self.frame = frame

    def SetText(self, text):
        self.text = text

    def SetVisible(self, visible):
        self.visible = visible

    def Append(self, text):
        self.text += text

    def OnPress(self, callback):
        self.press = callback

    def SetHotKey(self, *args):
        self.hotkey = args

    def SetDisabled(self, value):
        self.disabled = value


class Window:
    def __init__(self):
        self.controls = {n: Control() for n in (0, 2, 3, 4, 5)}

    def __getattr__(self, name):
        if name in ("SetFlags", "AddAlias"):
            return lambda *args: None
        raise AttributeError(name)

    def GetControl(self, number):
        return self.controls[number]

    def CreateButton(self, number, *frame):
        self.controls[number] = Control()
        return self.controls[number]


window = Window()
events = []
globals_ = {"CHAPTER": 1, "TLCHAP": 0, "TLBEAT": 0, "TLENEMY": 0, "TLENEMY_STALKER": 0,
            "TLENEMY_PROWLER": 0, "TLCAST": 0,
            "TLMARALEAD": 0, "TLLIBRARYCLUE": 0, "TLWATCHPOST": 0, "TLHUNTER": 0,
            "TLGALLERY": 0, "TLCOURT": 0, "TLECHO": 0, "TLECHOPHASE": 0, "TLFALSE_ALGORETH": 0, "TLWARDING": 0, "TLJRN_WARDING": 0, "TLMISTWOODSAFE": 0, "TLMISTWOODVICTORY": 0, "TLARCHIVE": 0, "TLVOYAGE": 0, "TLBRIEFING": 0,
            "TLARCHIVEWARD": 0, "TLDEEP_ARCHIVE_WARDEN": 0, "TLJRN_ARCHIVE_WARD": 0,
            "TLJRN_BYZANTEM": 0, "TLJRN_MISTWOOD": 0, "TLJRN_MISTWOOD_AMBUSH": 0, "TLJRN_HUNTER": 0, "TLJRN_HUNTER_RESOLVED": 0,
            "TLHUNTERTRACK": 0, "TLJRN_TRACKS": 0, "TLTRAVELKIT": 0, "TLJRN_TRAVELKIT": 0, "TLROYALORDER": 0, "TLJRN_ROYALORDER": 0, "TLRIVER": 0, "TLRIVERROUTE": 0, "TLJRN_RIVER": 0,
            "TLWAYSTONE": 0, "TLJRN_WAYSTONE": 0,
            "TLLORIANPURPOSE": 0, "TLLORIAN_GUARDIAN": 0, "TLJRN_LORIAN_PURPOSE": 0,
            "TLJRN_GALLERY_RESOLUTION": 0,
            "TLJRN_SCROLLS": 0, "TLJRN_TEAR": 0,
            "TLJRN_ARCHIVE": 0, "TLARCHIVEQUESTION": 0, "TLJRN_ARCHIVE_QUESTION": 0,
            "TLJRN_ELDRADOR": 0, "TLJRN_VOYAGE": 0, "TLJRN_BRIEFING": 0,
            "TLELDRADOR": 0, "TLSANCTUARY": 0, "TLJRN_ARRIVAL": 0, "TLJRN_SANCTUARY": 0,
            "TLPPELLDOCKET": 0, "TLJRN_PELL_PUBLIC": 0, "TLJRN_PELL_ARCHIVE": 0,
            "TLJRN_COURT_OPEN": 0, "TLJRN_COURT_RESTRICTED": 0}
globals_.update({"TLMARADETAIL": 0, "TLJRN_MARA": 0, "TLFOLLOWPENDING": 0,
                 "TLFOLLOWNPC": 0, "TLFOLLOWCHOICE": 0, "TLWITNESS": 0,
                 "TLORENDOCKET": 0, "TLJRN_COURT_RECORD": 0, "TLRELAY": 0, "TLJRN_RELAY": 0, "TLRETURNMARK": 0, "TLJRN_RETURNMARK": 0})
enemy_dead = False
dead_actors = set()
current_area = "tl0001"
next_actor = 1001
timed_events = []
journal_entries = []
gemrb = types.ModuleType("GemRB")
gemrb.LoadWindow = lambda *args: window
gemrb.GetGameVar = lambda name: globals_[name]
gemrb.SetGlobal = lambda name, context, value: globals_.__setitem__(name, value)
def set_journal_entry(text, section, group=0):
    journal_entries.append({"Text": len(journal_entries) + 1, "GameTime": len(journal_entries) + 1,
                            "Section": section, "Chapter": globals_["CHAPTER"], "Group": group, "value": text})
gemrb.SetJournalEntry = set_journal_entry
gemrb.GetJournalSize = lambda chapter, section: sum(entry["Chapter"] == chapter and entry["Section"] == section for entry in journal_entries)
def get_journal_entry(chapter, index, section):
    matches = [entry for entry in journal_entries if entry["Chapter"] == chapter and entry["Section"] == section]
    return matches[index]
gemrb.GetJournalEntry = get_journal_entry
gemrb.GetString = lambda strref: journal_entries[strref - 1]["value"]
gemrb.SetVar = lambda *args: None
gemrb.LoadMusicPL = lambda name, *args: events.append(("music", name))
def move_to_area(name):
    global current_area
    current_area = name
    events.append(("area", name))
gemrb.MoveToArea = move_to_area
gemrb.GetCurrentArea = lambda: current_area
gemrb.SetTimedEvent = lambda callback, delay: timed_events.append(callback)
gemrb.PlaySound = lambda name, *args: events.append(("voice", name))
def create_creature(*args):
    global next_actor
    next_actor += 1
    events.append(("spawn", args))
    return next_actor
gemrb.CreateCreature = create_creature
gemrb.SetPlayerName = lambda actor, name, *args: events.append(("name", actor, name))
gemrb.SetPlayerDialog = lambda actor, resref: events.append(("dialog", actor, resref))
gemrb.SetPlayerStat = lambda *args: None
gemrb.ExecuteString = lambda action, actor: events.append(("attack", action, actor))
gemrb.GetPlayerStat = lambda actor, stat: 2048 if enemy_dead or actor in dead_actors else 0
gemrb.GamePause = lambda *args: None
gemrb.GameSelectPC = lambda *args: events.append(("select-pc", *args))
gemrb.GameControlSetTargetMode = lambda mode, types=0: events.append(("target-mode", mode, types))
sys.modules["GemRB"] = gemrb
for name, symbol in (("GUICommon", "GetWindowPack"), ("GUIMA", "OpenMapWindow"), ("GUIINV", "OpenInventoryWindow")):
    module = types.ModuleType(name)
    setattr(module, symbol, lambda *args: None)
    sys.modules[name] = module

spec = importlib.util.spec_from_file_location("MessageWindow", SCRIPTS / "terralum" / "MessageWindow.py")
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()

assert window.controls[4].frame["w"] == 100
assert window.controls[10].text == "NARRATE"
assert window.controls[10].hotkey == ("n", 0, True)
assert window.controls[11].text == "CAST"
assert window.controls[11].hotkey == ("c", 0, True)
assert window.controls[16].text == "TALK"
assert window.controls[16].hotkey == ("t", 0, True)
assert window.controls[15].text == "JOURNAL"
assert window.controls[15].hotkey == ("j", 0, True)
assert window.controls[10].disabled is False
window.controls[16].press()
assert events[-2] == ("select-pc", 1, True, 1)
assert events[-1][0:2] == ("target-mode", 1)
assert len(journal_entries) == 1
window.controls[15].press()
assert "Find his route and recover the Scrolls of Byzantem" in window.controls[0].text
assert window.controls[4].text == "CLOSE LOG"
window.controls[15].press()
assert "Archivist Mara" in window.controls[0].text
assert len(journal_entries) == 1
assert "Archivist Mara" in window.controls[0].text
assert len([event for event in events if event[0] == "spawn"]) == len(campaign.Story.cast("tl0001"))
window.controls[11].press()
assert "Dorian's last travel ledger" in window.controls[0].text
window.controls[15].press()
assert "TERRALUM JOURNAL" not in window.controls[0].text
assert "Dorian's last travel ledger" in window.controls[0].text
assert window.controls[12].text == "Ask for the old route"
assert window.controls[12].hotkey == ("1", 0, True)
window.controls[12].press()
assert globals_["TLMARALEAD"] == 1
assert globals_["TLFOLLOWPENDING"] == 1
assert "safe path through the pale stones" in window.controls[0].text
assert "Copy the landmarks for Inessa" == window.controls[12].text
window.controls[4].press()
assert globals_["TLBEAT"] == 0
assert "Finish this conversation before continuing" in window.controls[0].text
window.controls[11].press()
assert "Copy the landmarks for Inessa" == window.controls[12].text
campaign.OnLoad()  # A loaded save recreates the required follow-up from campaign globals.
while timed_events:
    timed_events.pop(0)()
assert globals_["TLFOLLOWPENDING"] == 1
assert "Should I copy the landmarks for Inessa" in window.controls[0].text
window.controls[4].press()
assert "Finish this conversation before continuing" in window.controls[0].text
window.controls[12].press()
assert globals_["TLMARADETAIL"] == 1
assert globals_["TLJRN_MARA"] == 1
assert globals_["TLFOLLOWPENDING"] == 0
assert any("agreed how to handle Dorian's western route ledger" in entry["value"]
           for entry in journal_entries)
chapters = campaign.Story.chapters()
chapter_index_by_area = {chapter["area"]: index for index, chapter in enumerate(chapters)}
assert len(chapters) == 25
assert sum(len(chapter["beats"]) for chapter in chapters) == 63
assert sorted({chapter["act"] for chapter in chapters}) == list(range(1, 8))
for chapter_index, chapter in enumerate(chapters):
    assert globals_["TLCHAP"] == chapter_index
    assert current_area == chapter["area"]
    people = campaign.Story.cast(chapter["area"])
    assert len(people) >= 2
    assert all(all(person.get(field) for field in
                   ("role", "faction", "goal", "knowledge", "voice", "provenance"))
               for person in people)
    assert window.controls[10].disabled is (not bool(chapter["voice"]))
    if chapter_index:
        window.controls[11].press()
        assert people[0]["name"] in window.controls[0].text
        if chapter["area"] == "tl0007":
            assert "copied archive account" in window.controls[0].text
            window.controls[11].press()
            assert "archive copy is aboard" in window.controls[0].text
        if chapter["area"] == "tl0002" and globals_["TLLIBRARYCLUE"] == 1:
            assert "Leora’s copied schedule gives me the patrol turn" in window.controls[0].text
        if chapter["area"] == "tl0006":
            window.controls[11].press()
            window.controls[11].press()
            assert "Archivist Nera" in window.controls[0].text
            assert window.controls[12].text == "Call the Index Warden"
            window.controls[13].press()
            assert globals_["TLARCHIVEWARD"] == 2
            assert "dormant ward intact" in window.controls[0].text
        if people[0].get("choices"):
            selected = people[0]["choices"][0]
            choice_button = window.controls[12]
            assert choice_button.hotkey == ("1", 0, True)
            choice_button.press()
            assert globals_[selected["flag"]] == selected["value"]
            if chapter["area"] == "tl0015":
                window.controls[11].press()
                assert "Follow its short beam" in window.controls[0].text
    beats = chapter["beats"]
    for beat in beats:
        for route in beat.get("routes", []):
            if globals_[route["flag"]] == route["value"]:
                assert route["text"] in window.controls[0].text, (chapter["area"], route, window.controls[0].text)
                break
        if chapter["area"] == "tl0025" and beats.index(beat) == 1:
            window.controls[4].press()
            assert globals_["TLBEAT"] == 1
            assert "Pell is waiting for the route record" in window.controls[0].text
            for _ in range(len(people)):
                window.controls[11].press()
                if "Courier Pell:" in window.controls[0].text:
                    break
            assert "Courier Pell:" in window.controls[0].text
            window.controls[12].press()
            assert "What should I leave for the next travellers?" in window.controls[0].text
            window.controls[12].press()
            assert globals_["TLRETURNMARK"] == 1
            assert globals_["TLJRN_RETURNMARK"] == 1
            assert any("chose how Courier Pell would preserve" in entry["value"] for entry in journal_entries)
        if chapter["area"] == "tl0004" and beats.index(beat) == 1:
            for _ in range(len(people)):
                window.controls[11].press()
                if "Queen Alisande:" in window.controls[0].text:
                    break
            assert "Queen Alisande:" in window.controls[0].text
            assert "pale-stone route marker" in window.controls[0].text
        if chapter["area"] == "tl0024" and beats.index(beat) == 1:
            window.controls[4].press()
            assert globals_["TLBEAT"] == 1
            assert "relay is still unassigned" in window.controls[0].text
            for _ in range(len(people)):
                window.controls[11].press()
                if "Relay Keeper Orla:" in window.controls[0].text:
                    break
            assert "Relay Keeper Orla:" in window.controls[0].text
            window.controls[12].press()
            assert "Will you call the patrol" in window.controls[0].text
            window.controls[12].press()
            assert globals_["TLRELAY"] == 1
            assert globals_["TLJRN_RELAY"] == 1
            assert any("chose whether to call a patrol" in entry["value"] for entry in journal_entries)
        if chapter["area"] == "tl0011" and beats.index(beat) == 1:
            window.controls[4].press()
            assert globals_["TLBEAT"] == 1
            assert "The council docket is unfinished" in window.controls[0].text
            for _ in range(len(people)):
                window.controls[11].press()
                if "Royal Scribe Oren:" in window.controls[0].text:
                    break
            assert "Royal Scribe Oren:" in window.controls[0].text
            window.controls[12].press()
            assert "Should the route and scroll accounts be placed side by side" in window.controls[0].text
            window.controls[12].press()
            assert globals_["TLWITNESS"] == 1
            assert globals_["TLJRN_COURT_RECORD"] == 1
            assert any("chose how Royal Scribe Oren would preserve" in entry["value"]
                       for entry in journal_entries)
        if "encounter" in beat:
            if beat.get("encounter_if") and globals_[beat["encounter_if"]["flag"]] != beat["encounter_if"]["value"]:
                window.controls[4].press()
                assert globals_["TLBEAT"] == beats.index(beat) + 1
                following_beat = beats[beats.index(beat) + 1]
                selected_route = next(route for route in following_beat["routes"]
                                      if globals_[route["flag"]] == route["value"])
                assert selected_route["text"] in window.controls[0].text, (selected_route, window.controls[0].text)
                continue
            if chapter["area"] == "tl0002" and (globals_["TLMARALEAD"] == 1 or globals_["TLLIBRARYCLUE"] == 1 or (globals_["TLTRAVELKIT"] == 1 and globals_["TLHUNTER"] == 1) or (globals_["TLTRAVELKIT"] == 2 and globals_["TLHUNTERTRACK"] == 1)):
                window.controls[4].press()
                assert globals_["TLMISTWOODSAFE"] == 1
                assert globals_["TLBEAT"] == beats.index(beat) + 1
                assert "Dorian's inscription" in window.controls[0].text
                assert "skirts the stalker's ambush" in window.controls[0].text
                continue
            window.controls[4].press()
            assert any(event[:2] == ("attack", "Attack(Player1)") for event in events)
            assert globals_["TLENEMY"] > 1001
            if chapter["area"] == "tl0002":
                spawn = beat["spawn_position"]
                assert (1, "riddler", *spawn) in [event[1] for event in events if event[0] == "spawn"]
            elif chapter["area"] == "tl0003":
                assert beat["encounter_actor_flag"] == "TLLORIAN_GUARDIAN"
                assert globals_["TLENEMY"] == globals_[beat["encounter_actor_flag"]]
                assert [event[1] for event in events if event[0] == "spawn"].count(
                    (1, "riddler", *beat["spawn_position"])) == 1
            window.controls[4].press()
            assert globals_["TLBEAT"] == beats.index(beat)
            enemy_dead = True
            if beat.get("encounter_phases"):
                window.controls[4].press()
                assert globals_["TLBEAT"] == beats.index(beat)
                assert globals_["TLECHOPHASE"] == 1
                assert globals_["TLJRN_TEAR"] == 0
                assert "False Algoreth" in window.controls[0].text, window.controls[0].text
        window.controls[4].press()
        enemy_dead = False
    while timed_events:
        timed_events.pop(0)()
    if chapter_index + 1 < len(chapters):
        assert globals_["TLCAST"] == globals_["TLCHAP"] + 1
        next_cast = campaign.Story.cast(chapters[globals_["TLCHAP"]]["area"])
        assert any(name[0] == "name" and name[2] == next_cast[0]["name"] for name in events)
assert "TO BE CONTINUED" in window.controls[0].text
assert globals_["TLLIBRARYCLUE"] == 1
assert globals_["TLWATCHPOST"] == 1
assert globals_["TLGALLERY"] == 1
assert globals_["TLCOURT"] == 1
assert globals_["TLWITNESS"] == 1
assert globals_["TLJRN_COURT_RECORD"] == 1
assert globals_["TLJRN_COURT_OPEN"] == 1
assert globals_["TLJRN_COURT_RESTRICTED"] == 0
assert globals_["TLECHO"] == 1
assert globals_["TLARCHIVEWARD"] == 2
assert len([event for event in events if event[0] == "area"]) == 24
assert len([event for event in events if event[0] == "voice"]) == 8
assert len([event for event in events if event[0] == "attack"]) == 3, [event for event in events if event[0] == "attack"]
assert len(journal_entries) == 24
assert globals_["TLJRN_WAYSTONE"] == 1
assert any("Three-Cairn Fork" in entry["value"] for entry in journal_entries)
assert globals_["TLJRN_LORIAN_PURPOSE"] == 1
assert any("answered Dorian's question" in entry["value"] for entry in journal_entries)
assert globals_["TLJRN_GALLERY_RESOLUTION"] == 1
assert any("chose whether to name restraint or demand passage" in entry["value"] for entry in journal_entries)
assert globals_["TLJRN_HUNTER_RESOLVED"] == 1
assert any(entry["Section"] == 2 and "Hunter's Camp decision is resolved" in entry["value"]
           for entry in journal_entries)

# Captain Rovan's policy options are one-time, distinct journaled outcomes.
rovan = next(person for person in campaign.Story.cast("tl0011") if person["name"] == "Captain Rovan")
for selected, event_flag, response in (
        (1, "TLJRN_COURT_OPEN", "Rovan will keep the road open"),
        (2, "TLJRN_COURT_RESTRICTED", "Rovan records the court's caution")):
    window = Window()
    events.clear()
    timed_events.clear()
    journal_entries.clear()
    current_area = "tl0011"
    globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
    globals_.update({"TLCHAP": chapter_index_by_area["tl0011"], "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLCOURT": 0, "TLJRN_COURT_OPEN": 0, "TLJRN_COURT_RESTRICTED": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0011"))):
        window.controls[11].press()
        if "Captain Rovan:" in window.controls[0].text:
            break
    assert "Captain Rovan:" in window.controls[0].text
    window.controls[11 + selected].press()
    assert globals_["TLCOURT"] == selected
    assert globals_[event_flag] == 1
    assert sum("western road" in entry["value"] or "scrolls until" in entry["value"]
               for entry in journal_entries) == 1
    assert response in window.controls[0].text
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0011"))):
        window.controls[11].press()
        if "Captain Rovan:" in window.controls[0].text:
            break
    assert window.controls[12].visible is False

# Exercise every remaining response option and its next-beat result.
for chapter_index, choice_index in ((chapter_index_by_area[area], choice) for area, choice in (("tl0001", 1), ("tl0001", 2), ("tl0008", 1), ("tl0017", 1), ("tl0015", 1), ("tl0016", 1), ("tl0009", 1), ("tl0003", 1), ("tl0010", 1), ("tl0011", 1), ("tl0012", 1), ("tl0021", 1), ("tl0013", 1), ("tl0014", 1))):
    chapter = chapters[chapter_index]
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = chapter["area"]
    globals_.update({key: 0 for key in globals_ if key.startswith("TL")})
    globals_.update({"TLCHAP": chapter_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLWAYSTONE": 0,
                     "TLMARALEAD": 0, "TLLIBRARYCLUE": 0, "TLWATCHPOST": 0, "TLHUNTER": 0,
                     "TLGALLERY": 0, "TLCOURT": 0, "TLECHO": 0, "TLWARDING": 0, "TLJRN_WARDING": 0,
                     "TLMISTWOODSAFE": 0, "TLARCHIVE": 0, "TLVOYAGE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[11].press()
    choice = campaign.Story.cast(chapter["area"])[0]["choices"][choice_index]
    button = window.controls[12 + choice_index]
    assert button.hotkey == (str(choice_index + 1), 0, True)
    button.press()
    assert globals_[choice["flag"]] == choice["value"]
    assert choice["reply"] in window.controls[0].text
    if choice.get("followup"):
        window.controls[12].press()
        assert globals_["TLARCHIVEQUESTION"] == 1
        assert globals_["TLJRN_ARCHIVE_QUESTION"] == 1
    else:
        for _ in range(len(campaign.Story.cast(chapter["area"]))):
            window.controls[11].press()
            if f"{campaign.Story.cast(chapter['area'])[0]['name']}:" in window.controls[0].text:
                break
        assert all(not window.controls[index].visible for index in (12, 13, 14))
    if chapter["area"] == "tl0015":
        window.controls[11].press()
        assert "camp should remain concealed" in window.controls[0].text
    if len(chapter["beats"]) > 1:
        window.controls[4].press()
        matching_route = next((route for route in chapter["beats"][1].get("routes", [])
                               if route["flag"] == choice["flag"] and route["value"] == choice["value"]), None)
        if matching_route:
            assert matching_route["text"] in window.controls[0].text, (chapter["area"], matching_route, window.controls[0].text)

# Exercise the two unsafe market outcomes and their actual watchpost actors.
for lead, expect_warden in ((2, True), (3, False)):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0002"
    enemy_dead = False
    globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                     "TLMARALEAD": lead, "TLLIBRARYCLUE": 2, "TLROYALORDER": 0, "TLMISTWOODSAFE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    warden_spawned = any(event[0] == "name" and event[2] == "Edmon's Waywarden" for event in events)
    assert warden_spawned is expect_warden
    window.controls[4].press()
    assert globals_["TLMISTWOODSAFE"] == 0
    assert globals_["TLENEMY"] > 1001
    assert any(event[:2] == ("attack", "Attack(Player1)") for event in events)

# The hunter's lantern independently bypasses the road ambush; leaving it dark does not.
resolved_journal_count = len(journal_entries)
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0002"
enemy_dead = False
dead_actors.clear()
globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 1, "TLTRAVELKIT": 1, "TLMISTWOODSAFE": 0,
                 "TLJRN_HUNTER_RESOLVED": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert globals_["TLMISTWOODSAFE"] == 1
assert "hunters' shuttered lantern" in window.controls[0].text
assert "Dorian's inscription" in window.controls[0].text
assert globals_["TLJRN_HUNTER_RESOLVED"] == 1
assert len(journal_entries) == resolved_journal_count + 1

# Re-entering the resolved beat does not add a duplicate journal record.
window = Window()
events.clear()
timed_events.clear()
globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 2, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
assert len(journal_entries) == resolved_journal_count + 1

# Dorian's purpose question is a required choice; each answer changes the
# Guardian's response and the journal records that the answer was given.
guardian_lines = (
    "You would carry a question through the arch",
    "Knowledge can still open a door",
    "You name a custodian and a return",
)
for purpose_index, guardian_line in enumerate(guardian_lines):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0003"
    enemy_dead = False
    globals_.update({"TLCHAP": chapter_index_by_area["tl0003"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLLORIANPURPOSE": 0, "TLJRN_LORIAN_PURPOSE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Dorian waits for your answer" in window.controls[0].text
    assert len([event for event in events if event[0] == "spawn"]) == len(campaign.Story.cast("tl0003"))
    window.controls[11].press()
    choice = campaign.Story.cast("tl0003")[0]["choices"][purpose_index]
    assert window.controls[12 + purpose_index].text == choice["label"]
    window.controls[12 + purpose_index].press()
    assert globals_["TLLORIANPURPOSE"] == purpose_index + 1
    assert choice["reply"] in window.controls[0].text
    window.controls[11].press()
    assert guardian_line in window.controls[0].text

# The Seal Gallery answer is required to resolve the inscription, adds one
# journal event, and changes Queen Alisande's response on the return to court.
gallery_outcomes = (
    (1, "You left the sealed niches closed in Lorian"),
    (2, "The gallery warning remains unresolved"),
)
for gallery_value, court_line in gallery_outcomes:
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0010"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0010"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLGALLERY": 0, "TLJRN_GALLERY_RESOLUTION": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Speak with the Gallery Keeper" in window.controls[0].text
    window.controls[11].press()
    choice = campaign.Story.cast("tl0010")[0]["choices"][gallery_value - 1]
    window.controls[12 + gallery_value - 1].press()
    assert globals_["TLGALLERY"] == gallery_value
    assert choice["reply"] in window.controls[0].text
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert globals_["TLJRN_GALLERY_RESOLUTION"] == 1
    gallery_route = next(route for route in campaign.Story.chapters()[chapter_index_by_area["tl0010"]]["beats"][1]["routes"]
                         if route["flag"] == "TLGALLERY" and route["value"] == gallery_value)
    assert gallery_route["text"] in window.controls[0].text
    assert any("chose whether to name restraint or demand passage" in entry["value"]
               for entry in journal_entries)

    gallery_journal_count = len(journal_entries)
    window = Window()
    events.clear()
    timed_events.clear()
    globals_.update({"TLCHAP": chapter_index_by_area["tl0010"], "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLGALLERY": gallery_value, "TLJRN_GALLERY_RESOLUTION": 1})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert len(journal_entries) == gallery_journal_count

    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0004"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0004"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLGALLERY": gallery_value, "TLRETURNMARK": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[11].press()
    window.controls[11].press()
    assert court_line in window.controls[0].text

window = Window()
events.clear()
timed_events.clear()
globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 2, "TLMISTWOODSAFE": 0, "TLTRAVELKIT": 2})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert globals_["TLMISTWOODSAFE"] == 0
assert globals_["TLENEMY"] > 1001

# Ranger Ilya's optional creekside investigation preserves concealment and
# bypasses the stalker even when the camp lantern stays dark.
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0015"
enemy_dead = False
globals_.update({"TLCHAP": chapter_index_by_area["tl0015"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 2,
                 "TLHUNTERTRACK": 0, "TLMISTWOODSAFE": 0,
                 "TLJRN_TRACKS": 0, "TLJRN_HUNTER_RESOLVED": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
for _ in range(3):
    window.controls[11].press()
assert "Ranger Ilya" in window.controls[0].text
assert window.controls[12].text == "Read the creekside tracks"
track_journal_count = len(journal_entries)
window.controls[12].press()
assert globals_["TLHUNTERTRACK"] == 1
assert globals_["TLJRN_TRACKS"] == 1
assert len(journal_entries) == track_journal_count + 1
assert "creekside patrol" in journal_entries[-1]["value"]

# Repeating the choice cannot duplicate the journal clue.
for _ in range(3):
    window.controls[11].press()
window.controls[12].press()
assert len(journal_entries) == track_journal_count + 1

window = Window()
events.clear()
timed_events.clear()
current_area = "tl0002"
globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                 "TLMISTWOODSAFE": 0, "TLTRAVELKIT": 2})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert globals_["TLMISTWOODSAFE"] == 1
assert globals_["TLBEAT"] == 2
assert "Ilya's creekside tracks" in window.controls[0].text
assert not any(event[0] == "attack" for event in events)
assert globals_["TLJRN_HUNTER_RESOLVED"] == 1

# The dispatch archive is a required, journaled choice. A copied schedule
# makes Mara's sealed-order route a safe patrol diversion; a sealed schedule
# leaves that route exposed.
for order, expected in ((1, "Leora copies the current watchpost patrol turn"), (2, "leave the dispatch under crown seal")):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0018"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0018"], "TLBEAT": 0, "TLENEMY": 0,
                     "TLCAST": 0, "TLROYALORDER": 0, "TLJRN_ROYALORDER": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Archivist Leora" in window.controls[0].text
    window.controls[11].press()
    window.controls[12 + order - 1].press()
    assert globals_["TLROYALORDER"] == order
    assert globals_["TLJRN_ROYALORDER"] == 0
    assert expected in window.controls[0].text
    journal_count = len(journal_entries)
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert globals_["TLJRN_ROYALORDER"] == 1
    assert len(journal_entries) == journal_count + 1
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0002"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0, "TLMARALEAD": 2, "TLLIBRARYCLUE": 2,
                     "TLROYALORDER": order, "TLTRAVELKIT": 0, "TLHUNTER": 2,
                     "TLHUNTERTRACK": 0, "TLMISTWOODSAFE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[11].press()
    assert ("copied schedule gives me the patrol turn" if order == 1 else
            "schedule stayed sealed") in window.controls[0].text
    window.controls[4].press()
    assert (globals_["TLMISTWOODSAFE"] == 1) is (order == 1)
    assert (globals_["TLENEMY"] == 0) is (order == 1)

# The Royal Stables require a kit choice, journal it once, and make Tavin
# acknowledge both outcomes.
for kit, expected_reply in ((1, "The spare oil is packed"), (2, "The rope and rations are packed")):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0017"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0017"], "TLBEAT": 0, "TLENEMY": 0,
                     "TLCAST": 0, "TLTRAVELKIT": 0, "TLJRN_TRAVELKIT": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Speak with Stablemaster Edda" in window.controls[0].text
    window.controls[11].press()
    window.controls[12 + kit - 1].press()
    assert globals_["TLTRAVELKIT"] == kit
    window.controls[11].press()
    assert expected_reply in window.controls[0].text
    before = len(journal_entries)
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert globals_["TLJRN_TRAVELKIT"] == 1
    assert len(journal_entries) == before + 1
    assert ("shuttered lantern" if kit == 1 else "rope and trail rations") in window.controls[0].text
    window = Window()
    globals_.update({"TLCHAP": chapter_index_by_area["tl0017"], "TLBEAT": 1, "TLENEMY": 0,
                     "TLCAST": 0, "TLTRAVELKIT": kit, "TLJRN_TRAVELKIT": 1})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert len(journal_entries) == before + 1

# The river crossing requires a route decision. The handline only creates a
# quiet route with the expedition rope kit; the exposed ford, or a handline
# attempt without rope, reaches the watched road and its encounter. Eren reports
# the same outcome when he appears again at the Ruined Watchpost.
river_index = chapter_index_by_area["tl0019"]
road_index = chapter_index_by_area["tl0002"]
for kit, crossing_choice, expected_route in ((2, 1, 1), (1, 1, 2), (2, 2, 2)):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0019"
    enemy_dead = False
    globals_.update({"TLCHAP": river_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLTRAVELKIT": kit, "TLRIVER": 0, "TLRIVERROUTE": 0, "TLJRN_RIVER": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Choose how to cross" in window.controls[0].text
    window.controls[11].press()
    window.controls[12 + crossing_choice - 1].press()
    assert globals_["TLRIVER"] == crossing_choice
    window.controls[11].press()
    assert ("rope will bring my cart" if crossing_choice == 1 else "Leave the cart") in window.controls[0].text
    before = len(journal_entries)
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert globals_["TLRIVERROUTE"] == expected_route
    assert globals_["TLJRN_RIVER"] == 1
    assert len(journal_entries) == before + 1
    river_beat = campaign.Story.chapters()[river_index]["beats"][1]
    expected_route_text = next(route["text"] for route in river_beat["routes"]
                               if route["flag"] == "TLRIVERROUTE" and route["value"] == expected_route)
    assert expected_route_text in window.controls[0].text

    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0002"
    globals_.update({"TLCHAP": road_index, "TLBEAT": 1, "TLENEMY": 0,
                     "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                     "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 2,
                     "TLHUNTERTRACK": 0, "TLTRAVELKIT": kit, "TLRIVERROUTE": expected_route,
                     "TLROYALORDER": 0, "TLMISTWOODSAFE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert (globals_["TLMISTWOODSAFE"] == 1) is (expected_route == 1)
    assert (globals_["TLENEMY"] == 0) is (expected_route == 1)

    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0009"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0009"], "TLBEAT": 1,
                     "TLENEMY": 0, "TLCAST": 0, "TLRIVERROUTE": expected_route})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[11].press()
    window.controls[11].press()
    assert ("handline kept the dispatch dry" if expected_route == 1 else
            "exposed ford") in window.controls[0].text

# A dangerous road route now spawns a small authored group. Both actors persist
# by global ID, the party cannot continue while either one stands, and the beat
# resolves only after the entire group is defeated.
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0002"
enemy_dead = False
globals_.update({"TLCHAP": chapter_index_by_area["tl0002"], "TLBEAT": 1, "TLENEMY": 0,
                 "TLENEMY_STALKER": 0, "TLENEMY_PROWLER": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 2,
                 "TLHUNTERTRACK": 0, "TLTRAVELKIT": 0, "TLROYALORDER": 0,
                 "TLRIVERROUTE": 0, "TLMISTWOODSAFE": 0, "TLMISTWOODVICTORY": 0,
                 "TLJRN_MISTWOOD_AMBUSH": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert [event[1] for event in events if event[0] == "spawn"][-2:] == [
    (1, "riddler", 1008, 444), (1, "protagon", 1120, 560)]
assert globals_["TLENEMY_STALKER"] > 1001
assert globals_["TLENEMY_PROWLER"] > globals_["TLENEMY_STALKER"]
assert globals_["TLENEMY"] == globals_["TLENEMY_STALKER"]
assert sum(event[0] == "attack" for event in events) == 2
window.controls[4].press()
assert globals_["TLBEAT"] == 1
assert "Mistwood stalker and Pale-stone prowler" in window.controls[0].text
dead_actors.add(globals_["TLENEMY_STALKER"])
window.controls[4].press()
assert globals_["TLBEAT"] == 1
assert "Defeat Pale-stone prowler to continue" in window.controls[0].text
dead_actors.add(globals_["TLENEMY_PROWLER"])
window.controls[4].press()
assert globals_["TLBEAT"] == 2
assert globals_["TLENEMY_STALKER"] == globals_["TLENEMY_PROWLER"] == globals_["TLENEMY"] == 0
assert globals_["TLMISTWOODVICTORY"] == globals_["TLJRN_MISTWOOD_AMBUSH"] == 1
assert any(entry["value"].startswith("Algoreth and Tessa broke the two-foe ambush")
           for entry in journal_entries)
dead_actors.clear()

# The victory changes Courier Pell's response at the next scene, carrying the
# combat result into the local cast and quest journal.
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0009"
globals_.update({"TLCHAP": chapter_index_by_area["tl0009"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[11].press()
assert "drove both creatures off the road" in window.controls[0].text
ambush_journal_records = sum(entry["value"].startswith("Algoreth and Tessa broke the two-foe ambush")
                             for entry in journal_entries)
window.controls[11].press()
window.controls[11].press()
window.controls[11].press()
assert sum(entry["value"].startswith("Algoreth and Tessa broke the two-foe ambush")
           for entry in journal_entries) == ambush_journal_records

# Both waystone decisions must alter what Tessa says after reaching the watchpost.
watchpost_index = next(index for index, chapter in enumerate(chapters) if chapter["area"] == "tl0009")
for waystone, expected_text in (
        (1, "The reset waystone gave Tessa a clear heading"),
        (2, "With the waystone left turned")):
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0009"
    globals_.update({"TLCHAP": watchpost_index, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLWAYSTONE": waystone, "TLWATCHPOST": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert expected_text in window.controls[0].text

# Exercise every authored player response once, including choices on later NPCs.
choice_count = 0
for chapter_index, chapter in enumerate(chapters):
    people = campaign.Story.cast(chapter["area"])
    for person_index, person in enumerate(people):
        for choice_index, choice in enumerate(person.get("choices", [])):
            window = Window()
            events.clear()
            timed_events.clear()
            current_area = chapter["area"]
            globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
            globals_.update({"TLCHAP": chapter_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0})
            if choice.get("journal"):
                globals_[choice["journal"]["flag"]] = 0
            campaign.OnLoad()
            while timed_events:
                timed_events.pop(0)()
            for _ in range(person_index + 1):
                window.controls[11].press()
            button = window.controls[12 + choice_index]
            assert button.text == choice["label"]
            # GemRB passes the clicked GButton to callbacks with positional
            # parameters. Exercise that runtime behavior to catch closure bugs.
            button.press(button)
            assert globals_[choice["flag"]] == choice["value"]
            assert choice["reply"] in window.controls[0].text
            if choice.get("journal"):
                event = choice["journal"]
                assert globals_[event["flag"]] == 1
                assert any(entry["value"] == event["text"] for entry in journal_entries)
            choice_count += 1
assert choice_count == 46

# Native NPC DLG writes the route flag directly; the scene panel reconciles
# its authored journal event on the next render without duplicating it.
window = Window()
events.clear()
timed_events.clear()
journal_entries.clear()
current_area = "tl0015"
globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
globals_.update({"TLCHAP": chapter_index_by_area["tl0015"], "TLBEAT": 0, "TLENEMY": 0,
                 "TLCAST": 0, "TLTRAVELKIT": 2, "TLHUNTERTRACK": 1, "TLJRN_TRACKS": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
assert globals_["TLJRN_TRACKS"] == 1
assert next(entry for entry in journal_entries if entry["value"].startswith("Hunter Ilya found broken reeds"))["Chapter"] == 2
assert sum(entry["value"] == "Hunter Ilya found broken reeds showing the stalker's creekside patrol. The party can follow the stream to pass beneath its sightline without lighting the camp lantern."
           for entry in journal_entries) == 1

# Selene's second choice is a required follow-up: Ealdrin carries a bounded
# question to Eldrador rather than treating the titleless living record as a witness.
selene = next(person for person in campaign.Story.cast("tl0013") if person["name"] == "Archivist Selene")
selene_followup = selene["choices"][1]["followup"]
for selected, expected, response in (
        (1, "what limits they observed", "Ealdrin has brought a question about the limits"),
        (2, "what the archive record cannot establish", "Ealdrin has brought a question about what the archive cannot establish")):
    window = Window()
    events.clear()
    timed_events.clear()
    journal_entries.clear()
    current_area = "tl0013"
    globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
    globals_.update({"TLCHAP": chapter_index_by_area["tl0013"], "TLBEAT": 0, "TLENEMY": 0,
                     "TLCAST": 0, "TLARCHIVE": 0, "TLARCHIVEQUESTION": 0,
                     "TLJRN_ARCHIVE_QUESTION": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0013"))):
        window.controls[11].press()
        if "Archivist Selene:" in window.controls[0].text:
            break
    assert "Archivist Selene:" in window.controls[0].text
    window.controls[13].press()
    assert globals_["TLARCHIVE"] == 2
    assert globals_["TLFOLLOWPENDING"] == 1
    assert selene_followup["line"] in window.controls[0].text
    campaign.OnLoad()  # The pending question survives GUI script reload.
    while timed_events:
        timed_events.pop(0)()
    assert globals_["TLFOLLOWPENDING"] == 1
    assert selene_followup["line"] in window.controls[0].text
    window.controls[11 + selected].press()
    assert globals_["TLARCHIVEQUESTION"] == selected
    assert globals_["TLFOLLOWPENDING"] == 0
    assert globals_["TLJRN_ARCHIVE_QUESTION"] == 1
    assert any(expected in entry["value"] for entry in journal_entries)
    assert sum("Archivist Selene kept the sealed" in entry["value"] for entry in journal_entries) == 1
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert sum("Archivist Selene kept the sealed" in entry["value"] for entry in journal_entries) == 1

    # The selected question changes Queen Vaelthira's welcome in Eldrador.
    window = Window()
    current_area = "tl0022"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0022"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0022"))):
        window.controls[11].press()
        if "Queen Vaelthira:" in window.controls[0].text:
            break
    assert "Queen Vaelthira:" in window.controls[0].text
    assert response in window.controls[0].text

choice_count += len(selene_followup["choices"])
assert choice_count == 48

# Mara's staged ledger conversation records one shared journal event and carries
# either handling choice into Scholar Inessa's later library dialogue.
mara = campaign.Story.cast("tl0001")[0]
followup = mara["choices"][0]["followup"]
for selected, expected_response in ((1, "separate landmark copy"),
                                    (2, "kept the ledger sealed")):
    window = Window()
    events.clear()
    timed_events.clear()
    journal_entries.clear()
    current_area = "tl0001"
    globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
    globals_.update({"TLCHAP": chapter_index_by_area["tl0001"], "TLBEAT": 0,
                     "TLENEMY": 0, "TLCAST": 0, "TLJRN_MARA": 0,
                     "TLMARADETAIL": 0, "TLMARALEAD": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0001"))):
        window.controls[11].press()
        if "Archivist Mara:" in window.controls[0].text:
            break
    assert "Archivist Mara:" in window.controls[0].text
    window.controls[12].press()
    assert followup["line"] in window.controls[0].text
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert globals_["TLFOLLOWPENDING"] == 1
    assert followup["line"] in window.controls[0].text
    window.controls[13 if selected == 2 else 12].press()
    assert globals_["TLMARADETAIL"] == selected
    assert globals_["TLJRN_MARA"] == 1
    assert globals_["TLFOLLOWPENDING"] == 0
    assert sum("agreed how to handle Dorian's western route ledger" in entry["value"]
               for entry in journal_entries) == 1

    campaign.OnLoad()  # A completed choice remains recorded and does not duplicate its journal entry.
    while timed_events:
        timed_events.pop(0)()
    assert globals_["TLMARADETAIL"] == selected
    assert globals_["TLJRN_MARA"] == 1
    assert sum("agreed how to handle Dorian's western route ledger" in entry["value"]
               for entry in journal_entries) == 1

    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0008"
    globals_.update({"TLCHAP": chapter_index_by_area["tl0008"], "TLBEAT": 0,
                     "TLENEMY": 0, "TLCAST": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0008"))):
        window.controls[11].press()
        if "Scholar Inessa:" in window.controls[0].text:
            break
    assert "Scholar Inessa:" in window.controls[0].text
    assert expected_response in window.controls[0].text, window.controls[0].text

# Include the two nested options in the campaign-wide authored response count.
choice_count += len(followup["choices"])
assert choice_count == 50

# The Act IV council hearing requires the player to choose how Oren preserves
# the evidence; Alisande and the closing record both acknowledge either path.
council_index = chapter_index_by_area["tl0011"]
scribe = next(person for person in campaign.Story.cast("tl0011") if person["name"] == "Royal Scribe Oren")
council_followup = scribe["choices"][0]["followup"]
for selected, expected_response, expected_route in (
        (1, "paired docket keeps the route evidence distinct", "Oren places Dorian's route testimony beside"),
        (2, "separate accounts preserve the limits", "Oren files the route testimony and scroll account separately")):
    window = Window()
    events.clear()
    timed_events.clear()
    journal_entries.clear()
    current_area = "tl0011"
    globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
    globals_.update({"TLCHAP": chapter_index_by_area["tl0011"], "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLWITNESS": 0, "TLORENDOCKET": 0, "TLJRN_COURT_RECORD": 0,
                     "TLFOLLOWPENDING": 0, "TLFOLLOWNPC": 0, "TLFOLLOWCHOICE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert "The council docket is unfinished" in window.controls[0].text
    for _ in range(len(campaign.Story.cast("tl0011"))):
        window.controls[11].press()
        if "Royal Scribe Oren:" in window.controls[0].text:
            break
    assert "Royal Scribe Oren:" in window.controls[0].text
    window.controls[12].press()
    assert council_followup["line"] in window.controls[0].text
    window.controls[13 if selected == 2 else 12].press()
    assert globals_["TLWITNESS"] == selected
    assert globals_["TLJRN_COURT_RECORD"] == 1
    assert sum("chose how Royal Scribe Oren would preserve" in entry["value"]
               for entry in journal_entries) == 1

    campaign.OnLoad()  # Reload preserves the selected evidence treatment and journal event.
    while timed_events:
        timed_events.pop(0)()
    assert globals_["TLWITNESS"] == selected
    assert globals_["TLJRN_COURT_RECORD"] == 1
    assert sum("chose how Royal Scribe Oren would preserve" in entry["value"]
               for entry in journal_entries) == 1
    for _ in range(len(campaign.Story.cast("tl0011"))):
        window.controls[11].press()
        if "Queen Alisande:" in window.controls[0].text:
            break
    assert expected_response in window.controls[0].text
    window.controls[4].press()
    assert expected_route in window.controls[0].text

choice_count += len(council_followup["choices"])
assert choice_count == 52

# Pell's council deposition is optional, gives bounded route testimony, and
# journals the player's decision to publish only the warning or restrict detail.
pell = next(person for person in campaign.Story.cast("tl0011") if person["name"] == "Courier Pell")
for selected, event_flag, expected_response in (
        (1, "TLJRN_PELL_PUBLIC", "My warning is in the public docket"),
        (2, "TLJRN_PELL_ARCHIVE", "The full route stays in the crown file")):
    for witness in (0, 1, 2):
        for court_policy in (1, 2):
            window = Window()
            events.clear()
            timed_events.clear()
            journal_entries.clear()
            current_area = "tl0011"
            globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
            globals_.update({"TLCHAP": chapter_index_by_area["tl0011"], "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                             "TLRETURNMARK": 1, "TLPPELLDOCKET": 0, "TLWITNESS": witness, "TLCOURT": court_policy,
                             "TLORENDOCKET": 0 if witness == 0 else 1,
                             "TLJRN_COURT_RECORD": 0 if witness == 0 else 1,
                             "TLJRN_PELL_PUBLIC": 0, "TLJRN_PELL_ARCHIVE": 0})
            campaign.OnLoad()
            while timed_events:
                timed_events.pop(0)()
            for _ in range(len(campaign.Story.cast("tl0011"))):
                window.controls[11].press()
                if "Courier Pell:" in window.controls[0].text:
                    break
            assert "Courier Pell:" in window.controls[0].text
            window.controls[12 if selected == 1 else 13].press()
            assert globals_["TLPPELLDOCKET"] == selected
            assert globals_[event_flag] == 1
            assert sum(event["value"].startswith("Courier Pell'") for event in journal_entries) == 1
            campaign.OnLoad()
            while timed_events:
                timed_events.pop(0)()
            for _ in range(len(campaign.Story.cast("tl0011"))):
                window.controls[11].press()
                if "Courier Pell:" in window.controls[0].text:
                    break
            assert expected_response in window.controls[0].text
            assert sum(event["value"].startswith("Courier Pell'") for event in journal_entries) == 1
            queen_response = {
                (1, 0): "Pell entered a public warning",
                (1, 1): "Pell's public warning and Oren's paired docket",
                (1, 2): "Pell's warning is public, while Oren filed",
                (2, 0): "Pell kept the route details with the crown",
                (2, 1): "Pell's detailed route stays in the crown file; Oren's paired docket",
                (2, 2): "Pell's detailed route stays in the crown file, and Oren kept",
            }[(selected, witness)]
            campaign.OnLoad()
            while timed_events:
                timed_events.pop(0)()
            for _ in range(len(campaign.Story.cast("tl0011"))):
                window.controls[11].press()
                if "Queen Alisande:" in window.controls[0].text:
                    break
            assert queen_response in window.controls[0].text, (selected, witness, court_policy, window.controls[0].text)
            policy_response = "The road remains open to supervised scholars and travellers." if court_policy == 1 else "Scroll access requires leave from Edmon and me."
            assert policy_response in window.controls[0].text

assert choice_count == 52

# The return to the Mistwood Watchpost reuses the location but changes its
# conversation. Both records persist through a script reload and change court dialogue.
return_index = chapter_index_by_area["tl0025"]
return_followup = campaign.Story.cast("tl0025")[1]["choices"][0]["followup"]
for selected, expected_response, expected_edmon, expected_route in (
        (1, "Pell left the pale-stone route marker", "A public marker guides travellers", "Pell leaves a pale-stone marker"),
        (2, "Pell kept the complete Mistwood route", "The patrol map stays in the crown record", "Pell leaves a brief danger warning")):
    window = Window()
    events.clear()
    timed_events.clear()
    journal_entries.clear()
    current_area = "tl0025"
    globals_.update({key: (1 if key.startswith("TLJRN_") else 0) for key in globals_})
    globals_.update({"TLCHAP": return_index, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLRETURNMARK": 0, "TLJRN_RETURNMARK": 0,
                     "TLFOLLOWPENDING": 0, "TLFOLLOWNPC": 0, "TLFOLLOWCHOICE": 0})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert "Pell is waiting for the route record" in window.controls[0].text
    for _ in range(len(campaign.Story.cast("tl0025"))):
        window.controls[11].press()
        if "Courier Pell:" in window.controls[0].text:
            break
    window.controls[12].press()
    assert return_followup["line"] in window.controls[0].text
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert globals_["TLFOLLOWPENDING"] == 1
    assert return_followup["line"] in window.controls[0].text
    window.controls[11 + selected].press()
    assert globals_["TLRETURNMARK"] == selected
    assert globals_["TLJRN_RETURNMARK"] == 1
    assert sum("chose how Courier Pell would preserve" in entry["value"]
               for entry in journal_entries) == 1
    window.controls[4].press()
    assert expected_route in window.controls[0].text
    for _ in range(len(campaign.Story.cast("tl0025"))):
        window.controls[11].press()
        if "Courier Pell:" in window.controls[0].text:
            break
    assert all(not window.controls[index].visible for index in (12, 13, 14))
    window.controls[4].press()
    assert current_area == "tl0004"
    while timed_events:
        timed_events.pop(0)()
    for _ in range(len(campaign.Story.cast("tl0004"))):
        window.controls[11].press()
        if "Queen Alisande:" in window.controls[0].text:
            break
    assert expected_response in window.controls[0].text
    for _ in range(len(campaign.Story.cast("tl0004"))):
        window.controls[11].press()
        if "King Edmon:" in window.controls[0].text:
            break
    assert expected_edmon in window.controls[0].text

choice_count += len(return_followup["choices"])
assert choice_count == 54

# Act VI's optional archive quest offers a peaceful path and a gated warder
# challenge. Victory records the comparison leaf and changes dialogue in the
# following Index Hall scene without turning the archive clue into a verdict.
archive_index = chapter_index_by_area["tl0006"]
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0006"
enemy_dead = False
globals_.update({"TLCHAP": archive_index, "TLBEAT": 2, "TLENEMY": 0, "TLCAST": 0,
                 "TLARCHIVEWARD": 0, "TLDEEP_ARCHIVE_WARDEN": 0, "TLJRN_ARCHIVE_WARD": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert globals_["TLBEAT"] == 2
assert "speak with Archivist Nera" in window.controls[0].text
for _ in range(3):
    window.controls[11].press()
assert "Archivist Nera" in window.controls[0].text
window.controls[12].press()
assert globals_["TLARCHIVEWARD"] == 1
window.controls[11].press()
assert "called me to witness the missing comparison" in window.controls[0].text
window.controls[4].press()
assert globals_["TLENEMY"] == globals_["TLDEEP_ARCHIVE_WARDEN"] > 1001
assert any(event[:2] == ("attack", "Attack(Player1)") for event in events)
window.controls[4].press()
assert globals_["TLBEAT"] == 2
enemy_dead = True
window.controls[4].press()
assert globals_["TLBEAT"] == 3
assert globals_["TLJRN_ARCHIVE_WARD"] == 1
assert "yielded the missing comparison leaf" in window.controls[0].text
assert any("recovered the comparison leaf without opening the sealed account" in entry["value"]
           for entry in journal_entries)
enemy_dead = False

window = Window()
events.clear()
timed_events.clear()
current_area = "tl0013"
globals_.update({"TLCHAP": chapter_index_by_area["tl0013"], "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[11].press()
assert "called the Index Warden" in window.controls[0].text
window.controls[11].press()
assert "Warden yielded a comparison leaf but no verdict" in window.controls[0].text

# The Act VII chart-room decision is required, journaled, reflected in the next
# beat and spoken differently by Flight Marshal Aven in the hangar.
for briefing, expected_line in (
        (1, "copied account is aboard in a separate case"),
        (2, "Ealdrin carries questions for the warders")):
    chart_index = chapter_index_by_area["tl0020"]
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0020"
    globals_.update({"TLCHAP": chart_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLBRIEFING": 0, "TLJRN_BRIEFING": 0, "TLJRN_ARCHIVE": 1,
                     "TLARCHIVEWARD": 2})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Ealdrin is waiting" in window.controls[0].text
    window.controls[11].press()
    choice = campaign.Story.cast("tl0020")[0]["choices"][briefing - 1]
    window.controls[11 + briefing].press()
    assert globals_["TLBRIEFING"] == briefing
    assert choice["reply"] in window.controls[0].text
    window.controls[4].press()
    assert globals_["TLBEAT"] == 1
    assert globals_["TLJRN_BRIEFING"] == 1
    route = next(route for route in campaign.Story.chapters()[chart_index]["beats"][1]["routes"]
                 if route["value"] == briefing)
    assert route["text"] in window.controls[0].text
    window.controls[4].press()
    assert current_area == "tl0014"
    while timed_events:
        timed_events.pop(0)()
    window.controls[11].press()
    assert expected_line in window.controls[0].text, window.controls[0].text

# The Act V annex decision is mandatory and both rules carry into the vault's
# false-echo approach and final seal narration without changing the outcome.
for warding in (1, 2):
    annex_index = chapter_index_by_area["tl0021"]
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0021"
    enemy_dead = False
    globals_.update({"TLCHAP": annex_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLECHOPHASE": 0, "TLFALSE_ALGORETH": 0,
                     "TLWARDING": 0, "TLJRN_WARDING": 0, "TLJRN_TEAR": 0,
                     "TLECHO": 1})
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    assert globals_["TLBEAT"] == 0
    assert "Celene is waiting" in window.controls[0].text
    window.controls[11].press()
    window.controls[11 + warding].press()
    assert globals_["TLWARDING"] == warding
    window.controls[4].press()
    assert globals_["TLJRN_WARDING"] == 1
    assert any("set a containment rule" in entry["value"] for entry in journal_entries)
    window.controls[4].press()
    assert current_area == "tl0005"
    while timed_events:
        timed_events.pop(0)()
    window.controls[4].press()
    approach = next(route for route in campaign.Story.chapters()[chapter_index_by_area["tl0005"]]["beats"][1]["routes"]
                    if route["flag"] == "TLWARDING" and route["value"] == warding)
    assert approach["text"] in window.controls[0].text
    window.controls[4].press()
    window.controls[4].press()
    assert "Ward Shard" in window.controls[0].text, window.controls[0].text
    enemy_dead = True
    window.controls[4].press()
    assert "False Algoreth" in window.controls[0].text
    assert "Next time, I will have learned" in window.controls[0].text
    assert globals_["TLECHOPHASE"] == 1
    assert globals_["TLJRN_TEAR"] == 0
    window.controls[4].press()
    resolution = next(route for route in campaign.Story.chapters()[chapter_index_by_area["tl0005"]]["beats"][3]["routes"]
                      if route["value"] == warding)
    assert resolution["text"] in window.controls[0].text
    assert "false self remains contained" in resolution["text"]
    assert globals_["TLJRN_TEAR"] == 1
    assert globals_["TLECHOPHASE"] == 0

# The Mistwood Relay choice records one shared journal event for either route
# and preserves the dispatch schedule's limits in Saren's dialogue.
relay_index = chapter_index_by_area["tl0024"]
relay_npc = campaign.Story.cast("tl0024")[1]
relay_followup = relay_npc["choices"][0]["followup"]
for signal in (1, 2):
    for schedule in (1, 2):
        window = Window()
        events.clear()
        timed_events.clear()
        journal_entries.clear()
        current_area = "tl0024"
        globals_.update({"TLCHAP": relay_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                         "TLRELAY": 0, "TLROYALORDER": schedule, "TLJRN_RELAY": 0})
        campaign.OnLoad()
        while timed_events:
            timed_events.pop(0)()
        window.controls[4].press()
        assert globals_["TLBEAT"] == 1
        window.controls[4].press()
        assert "relay is still unassigned" in window.controls[0].text
        window.controls[11].press()
        window.controls[11].press()
        window.controls[12].press()
        assert "Will you call the patrol" in window.controls[0].text
        window.controls[11 + signal].press()
        assert globals_["TLRELAY"] == signal
        assert globals_["TLJRN_RELAY"] == 1
        assert sum(1 for e in journal_entries if "chose whether to call a patrol" in e["value"]) == 1
        window.controls[4].press()
        route = next(route for route in campaign.Story.chapters()[relay_index]["beats"][2]["routes"]
                     if route["value"] == signal)
        assert route["text"] in window.controls[0].text
        window.controls[11].press()
        expected = next(r["line"] for r in campaign.Story.cast("tl0024")[0]["responses"]
                        if r["flag"] == "TLROYALORDER" and r["value"] == schedule)
        assert expected in window.controls[0].text

choice_count += len(relay_followup["choices"])
assert choice_count == 56

# The Act VII Eldrador landing and sanctuary-approach adaptations preserve the
# unresolved Tear while carrying both evidence and protocol choices forward.
for evidence in (1, 2):
    for protocol in (1, 2):
        quay_index = chapter_index_by_area["tl0022"]
        window = Window()
        events.clear()
        timed_events.clear()
        current_area = "tl0022"
        enemy_dead = False
        globals_.update({"TLCHAP": quay_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                         "TLELDRADOR": 0, "TLSANCTUARY": 0,
                         "TLJRN_ARRIVAL": 0, "TLJRN_SANCTUARY": 0})
        campaign.OnLoad()
        while timed_events:
            timed_events.pop(0)()
        window.controls[4].press()
        assert globals_["TLBEAT"] == 0
        assert "Vaelthira is waiting" in window.controls[0].text
        window.controls[11].press()
        window.controls[11 + evidence].press()
        assert globals_["TLELDRADOR"] == evidence
        window.controls[4].press()
        assert globals_["TLJRN_ARRIVAL"] == 1
        evidence_route = next(route for route in campaign.Story.chapters()[quay_index]["beats"][1]["routes"]
                              if route["value"] == evidence)
        assert evidence_route["text"] in window.controls[0].text
        window.controls[4].press()
        assert current_area == "tl0023"
        while timed_events:
            timed_events.pop(0)()
        window.controls[11].press()
        vaelthira_line = next(response["line"] for response in campaign.Story.cast("tl0023")[0]["responses"]
                              if response["flag"] == "TLELDRADOR" and response["value"] == evidence)
        assert vaelthira_line in window.controls[0].text
        for _ in range(3):
            window.controls[11].press()
        protocol_choice = campaign.Story.cast("tl0023")[0]["choices"][protocol - 1]
        window.controls[11 + protocol].press()
        assert globals_["TLSANCTUARY"] == protocol
        assert protocol_choice["reply"] in window.controls[0].text
        window.controls[4].press()
        assert globals_["TLJRN_SANCTUARY"] == 1
        protocol_route = next(route for route in campaign.Story.chapters()[chapter_index_by_area["tl0023"]]["beats"][1]["routes"]
                              if route["value"] == protocol)
        assert protocol_route["text"] in window.controls[0].text
        window.controls[4].press()
        assert "The party has reached the lower sanctuary threshold" in window.controls[0].text
        assert "has not been entered or resolved" in window.controls[0].text

# Alistair is a recurring, lore-grounded engineer. His hangar line reflects the
# combined archive-carrying and voyage-preparation decisions without claiming
# that either choice identifies or resolves Eldrador's Tear.
chart_index = chapter_index_by_area["tl0020"]
window = Window()
events.clear()
timed_events.clear()
current_area = "tl0020"
globals_.update({"TLCHAP": chart_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0})
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
assert len(campaign.Story.cast("tl0020")) == 4
for _ in range(4):
    window.controls[11].press()
assert "magic knights’ armaments" in window.controls[0].text
assert len([event for event in events if event[0] == "spawn"]) == 4
assert [event[2] for event in events if event[0] == "dialog"] == ["ALISTAR"]

hangar_index = chapter_index_by_area["tl0014"]
alistair_lines = {
    (1, 1): "marked account and Aven chose observation",
    (1, 2): "marked account travels separately while Aven prepares a guarded arrival",
    (2, 1): "Ealdrin carries questions for Eldrador’s warders, and Aven chose observation",
    (2, 2): "warder inquiry travels with the instruments aboard a guarded approach",
}
for (briefing, voyage), expected in alistair_lines.items():
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = "tl0014"
    globals_.update({"TLCHAP": hangar_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLBRIEFING": briefing, "TLVOYAGE": voyage})
    campaign = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(campaign)
    campaign.OnLoad()
    while timed_events:
        timed_events.pop(0)()
    assert [event[2] for event in events if event[0] == "dialog"] == ["ALISTAR"]
    for _ in range(3):
        window.controls[11].press()
    assert expected in window.controls[0].text, window.controls[0].text
    assert "cannot tell us what the Eldrador Tear is" not in window.controls[0].text

# False Algoreth answers the player's exact Academy warding and pulse decisions
# before the staged vault fight. Check all four condition combinations.
vault_index = chapter_index_by_area["tl0005"]
false_algoreth = next(person for person in campaign.Story.cast("tl0005")
                      if person["name"] == "False Algoreth")
for warding in (1, 2):
    for echo in (1, 2):
        window = Window()
        events.clear()
        timed_events.clear()
        current_area = "tl0005"
        globals_.update({"TLCHAP": vault_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                         "TLECHOPHASE": 0, "TLFALSE_ALGORETH": 0,
                         "TLWARDING": warding, "TLECHO": echo})
        campaign = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(campaign)
        campaign.OnLoad()
        while timed_events:
            timed_events.pop(0)()
        expected_line = next(response["line"] for response in false_algoreth["responses"]
                             if all(globals_[condition["flag"]] == condition["value"]
                                    for condition in response["when"]))
        for _ in range(len(campaign.Story.cast("tl0005"))):
            window.controls[11].press()
            if expected_line in window.controls[0].text:
                break
        assert expected_line in window.controls[0].text

print(len(chapters), "scenes across seven acts,", sum(len(campaign.Story.cast(chapter["area"])) for chapter in chapters),
      "named scene actors, keyboard controls, authored journal events, four-state NPC response conditions, all 56 response options, three market routes, four encounter gates, twenty-four transitions, and seven voice cues passed")
