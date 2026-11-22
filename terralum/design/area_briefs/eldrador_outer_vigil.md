# Area brief: Eldrador Outer Ward Vigil

**Status:** Implemented adaptation; scene flow and named save/load branch persistence live-reviewed
**Act:** VIII — The Warded Vigil
**Area:** `tl0027`, Eldrador Outer Watch Camp
**Entry:** After the Act VII party reaches the Lower Sanctuary Threshold. The party withdraws to the existing outer ward line; no one crosses the sealed gate.
**Exit:** End at the watch camp with a recorded protocol. The Tear's cause, voice, identity, and outcome remain unknown.

## Story brief

After the party's threshold decision, Queen Vaelthira establishes an observation camp beyond the lower sanctuary's sealed boundary. The player must set how the watchbook relates witness statements to instrument readings. The difficulty is epistemic rather than martial: participants have observations but no explanation, and the pressure to interpret a familiar voice must not be mistaken for evidence about its source.

The recovered codex supports an Eldrador Tear in a lower sanctuary, a familiar voice, Vaelthira's invitation, and the Alsperian party's departure to investigate. It does not support the arrival's exact sequence, a speaking identity, a ward response, or the Tear's resolution. The camp, its ward-scribe, its procedure, and the player choice are **adaptation**. Dialogue must label reports as witness accounts or measurements and must not connect the voice to False Algoreth.

The scene uses four named NPCs: new adaptation character Warden-Scribe Nerys, recurring Queen Vaelthira, Ward-Captain Mereth, and Seraphina Everglow. Nerys asks the player to choose one of two record policies: keep each witness attached to their own words, or separate testimony from measurements during comparison. The choice changes Mereth's and Vaelthira's responses and is recorded in one Act VIII Journal entry. A beat gate prevents the scene from ending before the player speaks with Nerys and makes the choice.

## Beat and state outline

| Beat | Actor / trigger | Player choice | State and visible result | Failure / skip |
|---|---|---|---|---|
| Arrival | Narration on entering `tl0027`; Nerys introduces the outer watchbook | Talk to Nerys and select a record policy | `TLVIGIL=1` keeps witness names with their statements; `TLVIGIL=2` separates the statements from instrument columns | The Continue gate blocks until `TLVIGIL` is 1 or 2. |
| Review | Vaelthira states the adopted policy; Mereth and Seraphina answer the same state | Optional conversations; no second state write | Beat journal entry `TLJRN_VIGIL` records that the outer watch is established and that the source remains unknown | Re-entering does not duplicate the journal event. |
| Close | Seraphina confirms the sealed boundary remains untouched | Continue | Act VIII ends at the exterior camp; neither the player nor NPCs interpret a new pulse as a message | No battle or gate breach is invented to create action. |

## Production scope

- One original painted isometric background with clear open party floor and perimeter tents/ward markers.
- Four visible NPCs, with a distinct painted 2D sprite and portrait for Nerys; reuse approved art for recurring characters.
- Three concise beats, a required choice, conditional NPC responses, one one-time Journal event, Kokoro `af_heart` narration, and the existing cavern loop.
- Data-driven walkable floor with blocked perimeter props; actors and party start connected.
- Rebuild the pack, then review live actor visibility, click-to-talk, both choice paths, narration/music, Journal, and save/load. Live isolated GemRB confirms all four actors appear together, the choice gate blocks Continue, Nerys’s choice advances to Seraphina’s closing beat, and the Journal records the watch policy. A named save/reload preserves the selected branch-specific response and Journal entry; the alternate policy path remains to verify.

## Deferred

No sanctuary interior, battle, new Tear behavior, speaking identity, marriage chronology, Edmon outcome, or later historical claim is part of this slice. Hand-painted walking/attack animation for Nerys and bespoke Eldrador music can follow after the live scene is accepted.
