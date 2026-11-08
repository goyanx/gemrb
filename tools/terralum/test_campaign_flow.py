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
        if name in ("SetFlags", "AddAlias", "SetColor", "SetAnimation", "SetBorder"):
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
globals_ = {"TLCHAP": 0, "TLBEAT": 0}
gemrb = types.ModuleType("GemRB")
gemrb.LoadWindow = lambda *args: window
gemrb.GetGameVar = lambda name: globals_[name]
gemrb.SetGlobal = lambda name, context, value: globals_.__setitem__(name, value)
gemrb.SetVar = lambda *args: None
gemrb.LoadMusicPL = lambda name, *args: events.append(("music", name))
gemrb.MoveToArea = lambda name: events.append(("area", name))
gemrb.PlaySound = lambda name, *args: events.append(("voice", name))
gemrb.CreateCreature = lambda *args: 1001
gemrb.SetPlayerName = lambda *args: None
gemrb.SetPlayerStat = lambda *args: None
gemrb.ExecuteString = lambda action, actor: events.append(("attack", action, actor))
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

assert window.controls[4].frame["w"] == 100
assert window.controls[10].text == "NARRATE"
assert "Archivist Mara" in window.controls[0].text
for chapter in range(7):
    assert globals_["TLCHAP"] == chapter
    beats = campaign.Story.chapters()[chapter]["beats"]
    for beat in beats:
        if "encounter" in beat:
            window.controls[4].press()
            assert ("attack", "Attack(Player1)", 1001) in events
        window.controls[4].press()
assert "TO BE CONTINUED" in window.controls[0].text
assert len([event for event in events if event[0] == "area"]) == 6
assert len([event for event in events if event[0] == "voice"]) == 7
print("Seven chapters,", sum(len(chapter["beats"]) for chapter in campaign.Story.chapters()),
      "beats, three encounters, six area transitions, and seven voice cues passed")
