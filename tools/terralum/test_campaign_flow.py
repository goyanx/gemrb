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

    def __getattr__(self, name):
        if name in ("SetFlags", "AddAlias", "SetColor", "SetAnimation", "SetBorder", "SetVisible"):
            return lambda *args: None
        raise AttributeError(name)

    def GetFrame(self):
        return self.frame

    def SetFrame(self, frame):
        self.frame = frame

    def SetText(self, text):
        self.text = text

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
globals_ = {"TLCHAP": 0, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
            "TLMARALEAD": 0, "TLLIBRARYCLUE": 0, "TLWATCHPOST": 0, "TLHUNTER": 0,
            "TLGALLERY": 0, "TLCOURT": 0, "TLECHO": 0, "TLMISTWOODSAFE": 0, "TLARCHIVE": 0, "TLVOYAGE": 0,
            "TLJRN_BYZANTEM": 0, "TLJRN_MISTWOOD": 0, "TLJRN_HUNTER": 0, "TLJRN_HUNTER_RESOLVED": 0,
            "TLHUNTERTRACK": 0, "TLJRN_TRACKS": 0,
            "TLWAYSTONE": 0, "TLJRN_WAYSTONE": 0,
            "TLJRN_SCROLLS": 0, "TLJRN_TEAR": 0,
            "TLJRN_ARCHIVE": 0, "TLJRN_ELDRADOR": 0, "TLJRN_VOYAGE": 0}
enemy_dead = False
current_area = "tl0001"
next_actor = 1001
timed_events = []
journal_entries = []
gemrb = types.ModuleType("GemRB")
gemrb.LoadWindow = lambda *args: window
gemrb.GetGameVar = lambda name: globals_[name]
gemrb.SetGlobal = lambda name, context, value: globals_.__setitem__(name, value)
def set_journal_entry(text, section, chapter):
    journal_entries.append({"Text": len(journal_entries) + 1, "GameTime": len(journal_entries) + 1,
                            "Section": section, "Chapter": chapter, "value": text})
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
gemrb.SetPlayerStat = lambda *args: None
gemrb.ExecuteString = lambda action, actor: events.append(("attack", action, actor))
gemrb.GetPlayerStat = lambda actor, stat: 2048 if enemy_dead else 0
gemrb.GamePause = lambda *args: None
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
assert window.controls[11].text == "TALK"
assert window.controls[11].hotkey == ("t", 0, True)
assert window.controls[15].text == "JOURNAL"
assert window.controls[15].hotkey == ("j", 0, True)
assert window.controls[10].disabled is False
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
assert "safe path" in window.controls[0].text
chapters = campaign.Story.chapters()
assert len(chapters) == 16
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
            assert "Inessa's copied rune index" in window.controls[0].text
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
        if "encounter" in beat:
            if chapter["area"] == "tl0002" and (globals_["TLMARALEAD"] == 1 or globals_["TLLIBRARYCLUE"] == 1 or globals_["TLHUNTER"] == 1):
                window.controls[4].press()
                assert globals_["TLMISTWOODSAFE"] == 1
                assert globals_["TLBEAT"] == beats.index(beat) + 1
                assert "Dorian's inscription" in window.controls[0].text
                assert "skirts the stalker's ambush" in window.controls[0].text
                continue
            window.controls[4].press()
            assert any(event[:2] == ("attack", "Attack(Player1)") for event in events)
            assert globals_["TLENEMY"] > 1001
            window.controls[4].press()
            assert globals_["TLBEAT"] == beats.index(beat)
            enemy_dead = True
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
assert globals_["TLECHO"] == 1
assert len([event for event in events if event[0] == "area"]) == 15
assert len([event for event in events if event[0] == "voice"]) == 7
assert len([event for event in events if event[0] == "attack"]) == 2
assert len(journal_entries) == 10
assert globals_["TLJRN_WAYSTONE"] == 1
assert any("Three-Cairn Fork" in entry["value"] for entry in journal_entries)
assert globals_["TLJRN_HUNTER_RESOLVED"] == 1
assert any(entry["Section"] == 2 and "Hunter's Camp decision is resolved" in entry["value"]
           for entry in journal_entries)

# Exercise every remaining response option and its next-beat result.
for chapter_index, choice_index in ((0, 1), (0, 2), (1, 1), (2, 1), (3, 1), (5, 1), (7, 1), (9, 1), (10, 1), (13, 1), (15, 1)):
    chapter = chapters[chapter_index]
    window = Window()
    events.clear()
    timed_events.clear()
    current_area = chapter["area"]
    globals_.update({"TLCHAP": chapter_index, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
                     "TLWAYSTONE": 0,
                     "TLMARALEAD": 0, "TLLIBRARYCLUE": 0, "TLWATCHPOST": 0, "TLHUNTER": 0,
                     "TLGALLERY": 0, "TLCOURT": 0, "TLECHO": 0, "TLMISTWOODSAFE": 0, "TLARCHIVE": 0, "TLVOYAGE": 0})
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
    globals_.update({"TLCHAP": 4, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                     "TLMARALEAD": lead, "TLLIBRARYCLUE": 2, "TLMISTWOODSAFE": 0})
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
globals_.update({"TLCHAP": 4, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 1, "TLMISTWOODSAFE": 0,
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
globals_.update({"TLCHAP": 4, "TLBEAT": 2, "TLENEMY": 0, "TLCAST": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
assert len(journal_entries) == resolved_journal_count + 1

window = Window()
events.clear()
timed_events.clear()
globals_.update({"TLCHAP": 4, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                 "TLMARALEAD": 3, "TLLIBRARYCLUE": 2, "TLHUNTER": 2, "TLMISTWOODSAFE": 0})
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
globals_.update({"TLCHAP": 2, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0,
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
globals_.update({"TLCHAP": 4, "TLBEAT": 1, "TLENEMY": 0, "TLCAST": 0,
                 "TLMISTWOODSAFE": 0})
campaign.OnLoad()
while timed_events:
    timed_events.pop(0)()
window.controls[4].press()
assert globals_["TLMISTWOODSAFE"] == 1
assert globals_["TLBEAT"] == 2
assert "Ilya's creekside tracks" in window.controls[0].text
assert not any(event[0] == "attack" for event in events)
assert globals_["TLJRN_HUNTER_RESOLVED"] == 1

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
            button.press()
            assert globals_[choice["flag"]] == choice["value"]
            assert choice["reply"] in window.controls[0].text
            if choice.get("journal"):
                event = choice["journal"]
                assert globals_[event["flag"]] == 1
                assert any(entry["value"] == event["text"] for entry in journal_entries)
            choice_count += 1
assert choice_count == 22
print(len(chapters), "scenes across seven acts,", sum(len(campaign.Story.cast(chapter["area"])) for chapter in chapters),
      "named scene actors, keyboard controls, eleven authored journal events, all 22 response options, three market routes, encounter gates, fifteen transitions, and seven voice cues passed")
