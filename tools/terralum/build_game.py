#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

"""Assemble the Terralum game pack from GemRB's redistributable demo data."""

import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "demo"
PROJECT = ROOT / "terralum"
OUTPUT = Path(os.environ.get("TERRALUM_GAME_OUTPUT", PROJECT / "build" / "game")).resolve()
CAST_FILE = PROJECT / "scene_cast.json"
NATIVE_DIALOGUE_FILE = PROJECT / "native_dialogues.json"
SEARCHMAP_FILE = PROJECT / "area_searchmaps.json"
AREA_IMAGE = PROJECT / "art" / "observatory_courtyard.png"
SETUP_FILE = ROOT / "gemrb" / "GUIScripts" / "terralum" / "SetupGame.py"
AREAS = {
    "tl0001": "alsperia_market.png",
    "tl0008": "deep_archives.png",
    "tl0017": "alsperia_royal_stables.png",
    "tl0018": "alsperia_dispatch_archive.png",
    "tl0019": "mistwood_river_crossing.png",
    "tl0015": "mistwood_hunters_camp.png",
    "tl0016": "mistwood_waystone_fork.png",
    "tl0002": "mistwood_road.png",
    "tl0009": "mistwood_ruins.png",
    "tl0003": "lorian_cavern.png",
    "tl0010": "byzantem_arch.png",
    "tl0004": "alsperia_court.png",
    "tl0011": "council_chamber.png",
    "tl0005": "tear_vault.png",
    "tl0012": "observatory_courtyard.png",
    "tl0006": "deep_archives.png",
    "tl0013": "archive_index_hall.png",
    "tl0007": "alsperia_skyport.png",
    "tl0020": "expedition_chart_room.png",
    "tl0014": "aethercraft_hangar.png",
    "tl0021": "academy_warding_annex.png",
    "tl0022": "eldrador_arrival_quay.png",
    "tl0023": "eldrador_sanctuary_threshold.png",
    "tl0024": "mistwood_waywarden_relay.png",
    "tl0025": "mistwood_ruins.png",
}
AREA_SONG_INDEX = {
    "tl0001": 1, "tl0002": 3, "tl0003": 2, "tl0004": 1,
    "tl0005": 2, "tl0006": 2, "tl0007": 1, "tl0008": 1,
    "tl0009": 3, "tl0010": 2, "tl0011": 1, "tl0012": 2,
    "tl0013": 2, "tl0014": 1, "tl0015": 3,
    "tl0016": 3, "tl0017": 1, "tl0018": 1, "tl0019": 3, "tl0020": 1,
    "tl0021": 2,
    "tl0022": 1, "tl0023": 2, "tl0024": 3, "tl0025": 3,
}


def read_story():
    story = json.loads((PROJECT / "story.json").read_text(encoding="utf-8"))
    for key in ("title", "hero_default_name"):
        if not isinstance(story.get(key), str) or not story[key].strip():
            raise ValueError(f"story.json: {key} must be nonempty text")
    chapters = story.get("chapters", [])
    if len(chapters) != len(AREAS):
        raise ValueError(f"story.json must define one scene for each of the {len(AREAS)} built areas")
    scene_areas = [chapter.get("area") for chapter in chapters]
    if len(scene_areas) != len(set(scene_areas)) or set(scene_areas) != set(AREAS):
        raise ValueError("story.json must define each built area exactly once")
    journal_flags = set()
    encounter_flags = set()
    setup_text = SETUP_FILE.read_text(encoding="utf-8")
    initialized_flags = set(re.findall(r'GemRB\.SetGlobal\("(TL[A-Z0-9_]+)", "GLOBAL", 0\)', setup_text))
    for chapter in chapters:
        if (chapter.get("area") not in AREAS or not chapter.get("beats")
                or type(chapter.get("act")) is not int or not 1 <= chapter["act"] <= 7):
            raise ValueError("each chapter needs a built area and story beats")
        if not all(beat.get("speaker") and beat.get("text") and beat.get("action") for beat in chapter["beats"]):
            raise ValueError("each story beat needs a speaker, text, and action")
        for beat_index, beat in enumerate(chapter["beats"]):
            enemies = beat.get("enemies")
            if enemies is not None:
                if (not beat.get("encounter") or not isinstance(enemies, list)
                        or not 1 <= len(enemies) <= 3 or beat.get("spawn_position")
                        or beat.get("encounter_actor_flag")):
                    raise ValueError(f"enemy groups for {chapter['area']} need an encounter and one to three members")
                for member in enemies:
                    position = member.get("position") if isinstance(member, dict) else None
                    flag = member.get("flag") if isinstance(member, dict) else None
                    if (not isinstance(member, dict) or not isinstance(member.get("name"), str)
                            or not member["name"].strip() or len(member["name"]) > 120
                            or member.get("creature") not in ("protagon", "riddler")
                            or not isinstance(position, list) or len(position) != 2
                            or any(type(value) is not int or not 0 <= value <= 32767 for value in position)
                            or not isinstance(flag, str) or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", flag)
                            or flag not in initialized_flags or flag in encounter_flags):
                        raise ValueError(f"enemy group member for {chapter['area']} needs a name, supported creature, position, and unique initialized TL flag")
                    encounter_flags.add(flag)
            spawn = beat.get("spawn_position")
            if spawn is not None and (not beat.get("encounter") or not isinstance(spawn, list)
                                      or len(spawn) != 2
                                      or any(type(value) is not int or not 0 <= value <= 32767 for value in spawn)):
                raise ValueError(f"encounter spawn position for {chapter['area']} must be two bounded integers")
            actor_flag = beat.get("encounter_actor_flag")
            if actor_flag is not None and (not beat.get("encounter")
                                           or not isinstance(actor_flag, str)
                                           or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", actor_flag)
                                           or actor_flag not in initialized_flags):
                raise ValueError(f"encounter actor flag for {chapter['area']} must name an initialized TL global")
            phases = beat.get("encounter_phases")
            if phases is not None:
                if (not beat.get("encounter") or not isinstance(phases, list)
                        or not 2 <= len(phases) <= 4 or not beat.get("failure_recovery")):
                    raise ValueError(f"phased encounter for {chapter['area']} needs two to four phases and a recovery path")
                for phase in phases:
                    position = phase.get("position") if isinstance(phase, dict) else None
                    phase_flag = phase.get("actor_flag") if isinstance(phase, dict) else None
                    if (not isinstance(phase, dict) or not isinstance(phase.get("name"), str)
                            or not phase["name"].strip() or not phase.get("text")
                            or (position is not None and (not isinstance(position, list) or len(position) != 2
                                or any(type(value) is not int or not 0 <= value <= 32767 for value in position)))
                            or (phase_flag is not None and (not isinstance(phase_flag, str)
                                or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", phase_flag)
                                or phase_flag not in initialized_flags))):
                        raise ValueError(f"phases for {chapter['area']} need a name, text, optional bounded position, and initialized actor flag")
            encounter_gate = beat.get("encounter_if")
            if encounter_gate is not None and (
                    not beat.get("encounter") or not isinstance(encounter_gate, dict)
                    or not isinstance(encounter_gate.get("flag"), str)
                    or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", encounter_gate["flag"])
                    or encounter_gate["flag"] not in initialized_flags
                    or type(encounter_gate.get("value")) is not int
                    or beat_index + 1 >= len(chapter["beats"])):
                raise ValueError(f"conditional encounter for {chapter['area']} needs an initialized flag, integer value, and following beat")
            if beat.get("victory_journal") is not None and not beat.get("encounter"):
                raise ValueError(f"victory journal event for {chapter['area']} needs an encounter")
            for event_key in ("journal", "victory_journal"):
                event = beat.get(event_key)
                if event is not None:
                    validate_journal_event(event, journal_flags, initialized_flags)
    cast = read_cast()
    read_native_dialogues()
    for chapter in chapters:
        cast_flags = {person.get("spawn_flag") for person in cast[chapter["area"]]}
        for beat in chapter["beats"]:
            actor_flag = beat.get("encounter_actor_flag")
            if actor_flag is not None and actor_flag not in cast_flags:
                raise ValueError(f"encounter actor flag {actor_flag} for {chapter['area']} has no matching scene NPC")
            for phase in beat.get("encounter_phases", []):
                phase_flag = phase.get("actor_flag")
                if phase_flag is not None and phase_flag not in cast_flags:
                    raise ValueError(f"encounter phase actor flag {phase_flag} for {chapter['area']} has no matching scene NPC")
    for area_cast in cast.values():
        for person in area_cast:
            for response in person.get("responses", []):
                conditions = response.get("when")
                if conditions is None:
                    conditions = [{"flag": response["flag"], "value": response["value"]}]
                for condition in conditions:
                    if condition["flag"] not in initialized_flags:
                        raise ValueError(f"dialogue response flag {condition['flag']} must be initialized in SetupGame.py")
            for choice in iter_npc_choices(person.get("choices", [])):
                event = choice.get("journal")
                if event is not None:
                    validate_journal_event(event, journal_flags, initialized_flags)
                followup = choice.get("followup")
                if followup and followup.get("journal"):
                    validate_journal_event(followup["journal"], journal_flags, initialized_flags)
    return story


def iter_npc_choices(choices):
    for choice in choices:
        yield choice
        followup = choice.get("followup")
        if followup:
            yield from followup.get("choices", [])


def validate_journal_event(event, used_flags, initialized_flags):
    if (not isinstance(event, dict) or not isinstance(event.get("flag"), str)
            or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", event["flag"])
            or not isinstance(event.get("text"), str) or not event["text"].strip()
            or len(event["text"]) > 2000 or type(event.get("section")) is not int
            or event["section"] not in (1, 2, 4)):
        raise ValueError("journal events need a unique TL flag, text, and section 1, 2, or 4")
    if event["flag"] in used_flags:
        raise ValueError(f"journal event flag {event['flag']} is used more than once")
    if event["flag"] not in initialized_flags:
        raise ValueError(f"journal event flag {event['flag']} must be initialized in SetupGame.py")
    used_flags.add(event["flag"])


def validate_npc(person, area, require_design=False):
    if not isinstance(person, dict):
        raise ValueError(f"scene cast for {area} contains a non-object NPC")
    limits = {"name": 120, "line": 2000, "role": 300, "faction": 180, "goal": 1000,
              "knowledge": 1000, "voice": 500}
    if (not isinstance(person.get("name"), str) or not person["name"].strip() or len(person["name"]) > 120
            or not isinstance(person.get("line"), str) or not person["line"].strip() or len(person["line"]) > 2000
            or person.get("creature") not in ("protagon", "riddler")):
        raise ValueError(f"scene cast for {area} has an incomplete NPC")
    position = person.get("position")
    if (not isinstance(position, list) or len(position) != 2
            or any(type(value) is not int or not 0 <= value <= 32767 for value in position)):
        raise ValueError(f"scene cast position for {area} must contain two bounded integer coordinates")
    spawn_flag = person.get("spawn_flag")
    if spawn_flag is not None and (not isinstance(spawn_flag, str)
                                   or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", spawn_flag)):
        raise ValueError(f"scene cast spawn flag for {area} must be a TL global name")
    dialog = person.get("dialog")
    if dialog is not None and (not isinstance(dialog, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,8}", dialog)):
        raise ValueError(f"scene cast dialogue resource for {area} must be a resref of at most eight characters")
    choices = person.get("choices", [])
    if (not isinstance(choices, list) or len(choices) > 3
            or any(not validate_choice(choice, allow_followup=True) for choice in choices)):
        raise ValueError(f"scene dialogue choices for {area} must define up to three complete options")
    if choices and len({choice["flag"] for choice in choices}) != 1:
        raise ValueError(f"scene dialogue choices for {area} must share one decision flag")
    responses = person.get("responses", [])
    if not isinstance(responses, list) or len(responses) > 24:
        raise ValueError(f"scene dialogue responses for {area} must define up to 24 entries")
    for response in responses:
        if (not isinstance(response, dict)
                or not isinstance(response.get("line"), str) or not response["line"].strip()
                or len(response["line"]) > 2000):
            raise ValueError(f"scene dialogue responses for {area} need a nonempty line")
        conditions = response.get("when")
        if conditions is not None:
            if ("flag" in response or "value" in response or not isinstance(conditions, list)
                    or not conditions or len(conditions) > 8
                    or any(not isinstance(condition, dict)
                           or not isinstance(condition.get("flag"), str)
                           or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", condition["flag"])
                           or type(condition.get("value")) is not int for condition in conditions)
                    or len({condition["flag"] for condition in conditions}) != len(conditions)):
                raise ValueError(f"scene dialogue response conditions for {area} must use distinct TL flags and integer values")
        elif (not isinstance(response.get("flag"), str)
              or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", response["flag"])
              or type(response.get("value")) is not int):
            raise ValueError(f"scene dialogue responses for {area} must define a flag, value, and line")
    route_lines = person.get("route_lines", {})
    if not isinstance(route_lines, dict) or any(not str(key).isdigit() or not isinstance(value, str) or not value.strip()
                                                for key, value in route_lines.items()):
        raise ValueError(f"scene route lines for {area} must map numeric values to text")
    if require_design:
        for field in ("role", "faction", "goal", "knowledge", "voice"):
            if (not isinstance(person.get(field), str) or not person[field].strip()
                    or len(person[field]) > limits[field]):
                raise ValueError(f"NPC cast entry for {area} needs a nonempty {field}")
        if person.get("provenance") not in ("canon", "user-confirmed", "adaptation", "unresolved"):
            raise ValueError(f"NPC cast entry for {area} needs a recognized provenance label")


def validate_choice(choice, allow_followup=False):
    if (not isinstance(choice, dict)
            or not isinstance(choice.get("label"), str) or not choice["label"].strip() or len(choice["label"]) > 200
            or not isinstance(choice.get("reply"), str) or not choice["reply"].strip() or len(choice["reply"]) > 2000
            or not isinstance(choice.get("flag"), str)
            or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", choice["flag"])
            or type(choice.get("value")) is not int):
        return False
    followup = choice.get("followup")
    if followup is None:
        return True
    journal = followup.get("journal") if isinstance(followup, dict) else None
    journal_valid = (journal is None or (
        isinstance(journal, dict)
        and isinstance(journal.get("flag"), str)
        and re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", journal["flag"])
        and isinstance(journal.get("text"), str)
        and bool(journal["text"].strip())
        and len(journal["text"]) <= 2000
        and type(journal.get("section")) is int
        and journal["section"] in (1, 2, 4)
    ))
    return (allow_followup and isinstance(followup, dict)
            and isinstance(followup.get("line"), str) and followup["line"].strip()
            and len(followup["line"]) <= 2000
            and journal_valid
            and isinstance(followup.get("choices"), list)
            and 1 <= len(followup["choices"]) <= 3
            and len({choice.get("flag") for choice in followup["choices"] if isinstance(choice, dict)}) == 1
            and all(validate_choice(child) for child in followup["choices"]))


def validate_cast(cast):
    if not isinstance(cast, dict):
        raise ValueError("scene_cast.json must contain an object keyed by area")
    if set(cast) != set(AREAS):
        raise ValueError("scene_cast.json must define exactly the built scene areas")
    for area in AREAS:
        people = cast.get(area, [])
        if not isinstance(people, list) or len(people) < 2:
            raise ValueError(f"scene cast for {area} must contain at least two NPCs")
        for person in people:
            validate_npc(person, area, require_design=True)
        names = [person["name"].strip().casefold() for person in people]
        if len(names) != len(set(names)):
            raise ValueError(f"scene cast for {area} must contain unique NPC names")
    return cast


def read_cast():
    return validate_cast(json.loads(CAST_FILE.read_text(encoding="utf-8")))


def validate_native_dialogue(resref, dialogue, initialized_flags):
    if not isinstance(resref, str) or not re.fullmatch(r"[A-Z0-9_]{1,8}", resref):
        raise ValueError("native dialogue resource names must be uppercase resrefs of at most eight characters")
    states = dialogue.get("states") if isinstance(dialogue, dict) else None
    if (not isinstance(states, list) or not states or len(states) > 255
            or not isinstance(states[0], dict) or not states[0].get("when")):
        raise ValueError(f"native dialogue {resref} needs an ordered state list beginning with a conditional entry state")
    reachable = set()
    for state_index, state in enumerate(states):
        if (not isinstance(state, dict) or not isinstance(state.get("say"), str)
                or not state["say"].strip() or len(state["say"]) > 2000):
            raise ValueError(f"native dialogue {resref} state {state_index} needs a nonempty actor line")
        conditions = state.get("when")
        if conditions is not None:
            if (not isinstance(conditions, list) or not conditions or len(conditions) > 8
                    or any(not isinstance(condition, dict)
                           or not isinstance(condition.get("flag"), str)
                           or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", condition["flag"])
                           or condition["flag"] not in initialized_flags
                           or type(condition.get("value")) is not int for condition in conditions)
                    or len({condition["flag"] for condition in conditions}) != len(conditions)):
                raise ValueError(f"native dialogue {resref} state {state_index} has invalid or uninitialized entry conditions")
        transitions = state.get("transitions")
        if not isinstance(transitions, list) or not 1 <= len(transitions) <= 24:
            raise ValueError(f"native dialogue {resref} state {state_index} needs one to twenty-four transitions")
        for transition in transitions:
            if (not isinstance(transition, dict) or not isinstance(transition.get("text"), str)
                    or not transition["text"].strip() or len(transition["text"]) > 1000
                    or ("final" in transition) == ("next" in transition)):
                raise ValueError(f"native dialogue {resref} state {state_index} has an incomplete transition")
            journal = transition.get("journal")
            if journal is not None and (not isinstance(journal, str) or not journal.strip() or len(journal) > 2000):
                raise ValueError(f"native dialogue {resref} state {state_index} has invalid journal text")
            writes = transition.get("set", [])
            if (not isinstance(writes, list) or len(writes) > 8
                    or any(not isinstance(write, dict)
                           or not isinstance(write.get("flag"), str)
                           or not re.fullmatch(r"TL[A-Z][A-Z0-9_]{1,28}", write["flag"])
                           or write["flag"] not in initialized_flags
                           or type(write.get("value")) is not int
                           or not -2147483648 <= write["value"] <= 2147483647
                           for write in writes)):
                raise ValueError(f"native dialogue {resref} state {state_index} has invalid or uninitialized flag writes")
            if "next" in transition:
                if type(transition["next"]) is not int or not 0 <= transition["next"] < len(states):
                    raise ValueError(f"native dialogue {resref} transition points to a missing state")
                reachable.add(transition["next"])
            elif transition["final"] is not True:
                raise ValueError(f"native dialogue {resref} final transitions must set final to true")
    for state_index, state in enumerate(states):
        if "when" not in state and state_index not in reachable:
            raise ValueError(f"native dialogue {resref} unconditioned state {state_index} is unreachable")
    return dialogue


def read_native_dialogues():
    dialogues = json.loads(NATIVE_DIALOGUE_FILE.read_text(encoding="utf-8"))
    if not isinstance(dialogues, dict):
        raise ValueError("native_dialogues.json must contain an object keyed by resource resref")
    setup_text = SETUP_FILE.read_text(encoding="utf-8")
    initialized_flags = set(re.findall(r'GemRB\.SetGlobal\("(TL[A-Z0-9_]+)", "GLOBAL", 0\)', setup_text))
    result = {}
    for resref, dialogue in dialogues.items():
        key = resref.upper()
        if key in result:
            raise ValueError(f"native dialogue resrefs must be unique ignoring case: {resref}")
        result[key] = validate_native_dialogue(key, dialogue, initialized_flags)
    cast = read_cast()
    for area_cast in cast.values():
        for person in area_cast:
            ref = person.get("dialog")
            if ref and ref.upper() not in result:
                raise ValueError(f"NPC {person['name']} references missing native dialogue {ref}")
    return result


def write_native_dialogues(dialogues):
    """Compile authored dialogue state machines and append their TLK strings."""
    if not dialogues:
        return
    tlk_path = OUTPUT / "dialog.tlk"
    converter_path = str(ROOT / "tools" / "tlk_convert")
    sys.path.insert(0, converter_path)
    try:
        from tlk import Tlk

        with tlk_path.open("rb") as source:
            talk_table = Tlk(source)
        strrefs = {}

        def add_text(text):
            if text not in strrefs:
                strrefs[text] = len(talk_table)
                talk_table.append({"flag": 1, "sound_name": b"\0" * 8, "volume": 0, "pitch": 0,
                                   "offset": 0, "length": 0, "string": text.encode("utf-8")})
            return strrefs[text]

        for resref, dialogue in dialogues.items():
            states = dialogue["states"]
            trigger_strings = []
            trigger_indexes = []
            for state in states:
                conditions = state.get("when")
                if conditions is None:
                    trigger_indexes.append(0xFFFFFFFF)
                    continue
                trigger_indexes.append(len(trigger_strings))
                trigger_strings.append(" ".join(
                    f'Global("{condition["flag"]}","GLOBAL",{condition["value"]})'
                    for condition in conditions
                ).encode("ascii") + b"\r\n")

            flat_transitions = []
            action_payloads = []
            state_rows = []
            for state_index, state in enumerate(states):
                first_transition = len(flat_transitions)
                for transition in state["transitions"]:
                    flags = 0x01
                    next_state = 0
                    journal_ref = 0
                    if "journal" in transition:
                        flags |= 0x10
                        journal_ref = add_text(transition["journal"])
                    writes = transition.get("set", [])
                    action_index = 0
                    if writes:
                        flags |= 0x04
                        action_index = len(action_payloads)
                        action_payloads.append("\r\n".join(
                            f'SetGlobal("{write["flag"]}","GLOBAL",{write["value"]})'
                            for write in writes
                        ).encode("ascii") + b"\r\n")
                    if transition.get("final") is True:
                        flags |= 0x08
                    else:
                        next_state = transition["next"]
                    flat_transitions.append((flags, add_text(transition["text"]), journal_ref,
                                             action_index, next_state))
                state_rows.append((add_text(state["say"]), first_transition,
                                   len(state["transitions"]), trigger_indexes[state_index]))

            states_offset = 52
            transitions_offset = states_offset + 16 * len(state_rows)
            state_triggers_offset = transitions_offset + 32 * len(flat_transitions)
            transition_triggers_offset = state_triggers_offset + 8 * len(trigger_strings)
            actions_offset = transition_triggers_offset
            action_data_offset = actions_offset + 8 * len(action_payloads)
            trigger_data_offset = action_data_offset + sum(len(payload) for payload in action_payloads)
            trigger_table = bytearray()
            trigger_data = bytearray()
            for trigger in trigger_strings:
                trigger_table.extend(struct.pack("<II", trigger_data_offset + len(trigger_data), len(trigger)))
                trigger_data.extend(trigger)
            action_table = bytearray()
            action_data = bytearray()
            for payload in action_payloads:
                action_table.extend(struct.pack("<II", action_data_offset + len(action_data), len(payload)))
                action_data.extend(payload)
            header = struct.pack(
                "<8s11I", b"DLG V1.0", len(state_rows), states_offset,
                len(flat_transitions), transitions_offset,
                state_triggers_offset, len(trigger_strings),
                transition_triggers_offset, 0, actions_offset, len(action_payloads), 0,
            )
            state_table = b"".join(struct.pack("<4I", *row) for row in state_rows)
            transition_table = b"".join(
                struct.pack("<5I8sI", flags, text_ref, journal_ref, 0, action_index,
                            b"\0" * 8, next_state)
                for flags, text_ref, journal_ref, action_index, next_state in flat_transitions
            )
            target = OUTPUT / "override" / f"{resref.lower()}.dlg"
            target.write_bytes(header + state_table + transition_table + trigger_table + action_table
                               + action_data + trigger_data)

        with tlk_path.open("wb") as target:
            talk_table.save(target)
    finally:
        sys.path.remove(converter_path)


def read_searchmaps():
    """Load and validate scene-specific walkable and blocked searchmap polygons."""
    specs = json.loads(SEARCHMAP_FILE.read_text(encoding="utf-8"))
    if not isinstance(specs, dict) or not set(specs).issubset(AREAS):
        raise ValueError("area_searchmaps.json keys must name built scene areas")
    for area, spec in specs.items():
        if (not isinstance(spec, dict) or type(spec.get("base_value")) is not int
                or not 0 <= spec["base_value"] <= 15
                or type(spec.get("blocked_value")) is not int or not 0 <= spec["blocked_value"] <= 15):
            raise ValueError(f"searchmap spec for {area} needs base and blocked values from 0 to 15")
        for key in ("walkable", "blocked"):
            polygons = spec.get(key)
            if not isinstance(polygons, list) or not polygons:
                raise ValueError(f"searchmap spec for {area} needs at least one {key} polygon")
            for polygon in polygons:
                if (not isinstance(polygon, list) or len(polygon) < 3
                        or any(not isinstance(point, list) or len(point) != 2
                               or any(type(coord) is not int or coord < 0 for coord in point)
                               for point in polygon)):
                    raise ValueError(f"searchmap {key} polygons for {area} need three or more nonnegative integer points")
    return specs


def write_searchmap(reference_path, spec, target_path=None):
    """Build a paletted GemRB SR map from authored walkable and blocked polygons."""
    with Image.open(reference_path) as reference:
        if reference.mode != "P":
            raise ValueError("GemRB searchmap template must use an indexed palette")
        size = reference.size
        palette = reference.getpalette()
    image = Image.new("P", size, spec["base_value"])
    if palette:
        image.putpalette(palette)
    draw = ImageDraw.Draw(image)
    for polygon in spec["walkable"]:
        if any(x >= size[0] or y >= size[1] for x, y in polygon):
            raise ValueError(f"searchmap polygon exceeds {size[0]}x{size[1]} map bounds")
        draw.polygon([tuple(point) for point in polygon], fill=1)
    for polygon in spec["blocked"]:
        if any(x >= size[0] or y >= size[1] for x, y in polygon):
            raise ValueError(f"searchmap polygon exceeds {size[0]}x{size[1]} map bounds")
        draw.polygon([tuple(point) for point in polygon], fill=spec["blocked_value"])
    if target_path is not None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(target_path)
    return image


def write_tis(image_path, reference_path, target_path):
    """Replace the 25x18 paletted tiles while preserving the demo WED layout."""
    with reference_path.open("rb") as source:
        header = source.read(24)
    signature, count, record_size, offset, tile_size = struct.unpack("<8s4I", header)
    if (signature, count, record_size, offset, tile_size) != (b"TIS V1  ", 450, 5120, 24, 64):
        raise ValueError("The demo AR0100 tileset layout changed")

    with Image.open(image_path) as original:
        image = original.convert("RGB")
    # Center crop preserves the image's proportions before fitting the demo area.
    desired_ratio = 25 / 18
    width, height = image.size
    if width / height > desired_ratio:
        new_width = round(height * desired_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = round(width / desired_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    image = image.resize((1600, 1152), Image.Resampling.LANCZOS)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("wb") as output:
        output.write(header)
        for tile_y in range(18):
            for tile_x in range(25):
                tile = image.crop((tile_x * 64, tile_y * 64, (tile_x + 1) * 64, (tile_y + 1) * 64))
                indexed = tile.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                rgb = indexed.getpalette()[:768]
                # GemRB reads BGRA palette entries; the fourth byte is unused.
                palette = bytearray()
                for index in range(256):
                    red, green, blue = rgb[index * 3:index * 3 + 3]
                    palette.extend((blue, green, red, 0))
                output.write(palette)
                output.write(indexed.tobytes())
    return image


def build():
    story = read_story()
    native_dialogues = read_native_dialogues()
    searchmaps = read_searchmaps()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SOURCE, OUTPUT)
    write_native_dialogues(native_dialogues)
    image = write_tis(AREA_IMAGE, SOURCE / "override" / "ar0100.tis", OUTPUT / "override" / "ar0100.tis")
    image.save(OUTPUT / "override" / "ar0100.png")

    # Keep the demo's walkmesh and entrances until Terralum has authored area
    # geometry. Remove its actors and interactive tutorial objects.
    for area, image_name in AREAS.items():
        upper = area.upper().encode("ascii")
        for suffix in (".are", ".WED", ".mos", "LM.BMP", "SR.BMP", "HT.BMP", "TMP.BMP"):
            if suffix == "SR.BMP" and area in searchmaps:
                continue
            source_name = "ar0100" + suffix if suffix in (".are", ".mos") else "AR0100" + suffix
            data = (SOURCE / "override" / source_name).read_bytes()
            if suffix in (".are", ".WED"):
                data = data.replace(b"AR0100", upper)
            if suffix == ".are":
                data = bytearray(data)
                struct.pack_into("<H", data, 0x58, 0)  # actor count
                struct.pack_into("<H", data, 0x5A, 0)  # region count
                struct.pack_into("<I", data, 0x64, 0)  # spawn count
                struct.pack_into("<H", data, 0x74, 0)  # container count
                struct.pack_into("<H", data, 0x76, 0)  # item count
                struct.pack_into("<I", data, 0xA4, 0)  # door count
                song_offset = struct.unpack_from("<I", data, 0xBC)[0]
                song_index = AREA_SONG_INDEX[area]
                struct.pack_into("<II", data, song_offset, song_index, song_index)
            target_name = area + suffix if suffix in (".are", ".mos") else area.upper() + suffix
            (OUTPUT / "override" / target_name).write_bytes(data)
        if area in searchmaps:
            write_searchmap(SOURCE / "override" / "AR0100SR.BMP", searchmaps[area],
                            OUTPUT / "override" / (area.upper() + "SR.BMP"))
        write_tis(PROJECT / "art" / image_name, SOURCE / "override" / "ar0100.tis", OUTPUT / "override" / (area + ".tis"))

    game = OUTPUT / "override" / "gem-demo.gam"
    game.write_bytes(game.read_bytes().replace(b"AR0100", b"TL0001"))
    for table in ("startare.2da", "mastarea.2da"):
        path = OUTPUT / "override" / table
        path.write_text(path.read_text(encoding="ascii").replace("AR0100", "TL0001"), encoding="ascii")
    startpos = OUTPUT / "override" / "startpos.2da"
    startpos.write_text(startpos.read_text(encoding="ascii").replace("1409    585", "800     585").replace("1035    917", "600     917"), encoding="ascii")
    songs = OUTPUT / "override" / "songlist.2da"
    songs.write_text(songs.read_text(encoding="ascii").replace("mx0100.mus", "tlcity.mus").replace("mx0110.mus", "tlcave.mus")
                     + "3       mistwood        tlwood.mus\n", encoding="ascii")
    actions = OUTPUT / "override" / "action.ids"
    actions.write_text(actions.read_text(encoding="ascii") + "\n3 Attack(O:Target*)\n", encoding="ascii")
    for sound in (PROJECT / "audio").glob("tln*.ogg"):
        shutil.copy2(sound, OUTPUT / "override" / sound.name)
    for music in (PROJECT / "audio" / "music").rglob("*"):
        if music.is_file():
            destination = OUTPUT / "music" / music.relative_to(PROJECT / "audio" / "music")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(music, destination)

    gemrb_ini = OUTPUT / "override" / "gemrb.ini"
    ini_text = gemrb_ini.read_text(encoding="utf-8")
    gemrb_ini.write_text(ini_text.replace("WindowTitle = GemRB demo", f"WindowTitle = {story['title']}"), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_key_file.py"), str(OUTPUT)],
        check=True, capture_output=True, text=True,
    )
    def config_text(path_formatter):
        return (
            f"GameType = terralum\nGamePath = {path_formatter(OUTPUT)}\n"
            f"GemRBPath = {path_formatter(ROOT / 'gemrb')}\n"
            f"PluginsPath = {path_formatter(ROOT / 'build' / 'gemrb' / 'plugins')}\n"
            "Width = 1280\nHeight = 800\nSkipIntroVideos = 0\n"
        )

    default_output = (PROJECT / "build" / "game").resolve()
    config_dir = PROJECT / "build" if OUTPUT == default_output else OUTPUT.parent
    config_name = "terralum.cfg" if OUTPUT == default_output else f"{OUTPUT.name}.cfg"
    config = config_dir / config_name
    config.write_text(config_text(lambda path: path.as_posix()), encoding="utf-8")
    wsl_config = None
    if re.match(r"^[A-Za-z]:", str(ROOT)):
        def wsl_path(path):
            posix = path.as_posix()
            return f"/mnt/{posix[0].lower()}/{posix[3:]}"
        wsl_name = "terralum-wsl.cfg" if OUTPUT == default_output else f"{OUTPUT.name}-wsl.cfg"
        wsl_config = config_dir / wsl_name
        wsl_config.write_text(config_text(wsl_path), encoding="utf-8")
    return {
        "game_path": str(OUTPUT), "config_path": str(config),
        "wsl_config_path": str(wsl_config) if wsl_config else None, "tiles": 450,
        "areas": list(AREAS), "chapters": len(story["chapters"]),
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
