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
globals_ = {"TLCHAP": 0, "TLBEAT": 0, "TLENEMY": 0, "TLCAST": 0, "TLMARALEAD": 0, "TLMISTWOODSAFE": 0}
enemy_dead = False
current_area = "tl0001"
next_actor = 1001
timed_events = []
gemrb = types.ModuleType("GemRB")
gemrb.LoadWindow = lambda *args: window
gemrb.GetGameVar = lambda name: globals_[name]
gemrb.SetGlobal = lambda name, context, value: globals_.__setitem__(name, value)
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
assert window.controls[11].text == "TALK"
assert "Archivist Mara" in window.controls[0].text
assert len([event for event in events if event[0] == "spawn"]) == len(campaign.Story.cast("tl0001"))
window.controls[11].press()
assert "Dorian's last travel ledger" in window.controls[0].text
assert window.controls[12].text == "Ask for the old route"
window.controls[12].press()
assert globals_["TLMARALEAD"] == 1
assert "safe path" in window.controls[0].text
for chapter in range(7):
    assert globals_["TLCHAP"] == chapter
    beats = campaign.Story.chapters()[chapter]["beats"]
    for beat in beats:
        if "encounter" in beat:
            if chapter == 1 and globals_["TLMARALEAD"] == 1:
                window.controls[4].press()
                assert globals_["TLMISTWOODSAFE"] == 1
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
    assert globals_["TLCAST"] == globals_["TLCHAP"] + 1
    current_cast = campaign.Story.cast(campaign.Story.chapters()[globals_["TLCHAP"]]["area"])
    assert any(name[0] == "name" and name[2] == current_cast[0]["name"] for name in events)
    if globals_["TLCHAP"] == 1:
        assert "Mara's ledger marks the pale stones" in window.controls[0].text
        window.controls[11].press()
        assert "skirt the ruined watchpost" in window.controls[0].text
assert "TO BE CONTINUED" in window.controls[0].text
assert len([event for event in events if event[0] == "area"]) == 6
assert len([event for event in events if event[0] == "voice"]) == 7
assert len([event for event in events if event[0] == "attack"]) == 2
print("Seven scene casts,", sum(len(campaign.Story.cast(chapter["area"])) for chapter in campaign.Story.chapters()),
      "named actors, Talk choices and route effects, encounter gates, six area transitions, and seven voice cues passed")
