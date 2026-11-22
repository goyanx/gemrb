# Painted 2D world sprite turnarounds

These generated transparent turnarounds establish the corrected world-character art direction: painted 2D fantasy illustrations with realistic proportions and readable silhouettes, instead of the earlier low-poly Blender figures.

| Character | Runtime sprite asset | Sheet |
| --- | --- | --- |
| Archivist Mara | `mara00` | `mara.png` |
| King Edmon | `edmon0` | `edmon.png` |
| Queen Alisande | `queen_alisande` | `alisande.png` |
| Scout Tessa | `tessa0` | `tessa.png` |
| Scholar Inessa | `inessa` | `inessa.png` |
| Waywarden Saren | `saren0` | `saren.png` |
| Lost Wayfarer | `wayfar` | `wayfarer.png` |
| Dorian the Seer | `dorian` | `dorian.png` |
| Royal Scribe Oren | `oren00` | `oren.png` |
| Courier Pell | `pell00` | `pell.png` |
| Courier Eren | `eren00` | `eren.png` |
| Algoreth Jon Goren (player) | `TLPG` | `algoreth.png`; directional staff attacks in `algoreth_attack.png` |
| Mistwood Stalker (encounter enemy) | `mistalk` | `mistwood_stalker.png` |
| Pale-Stone Prowler (encounter enemy) | `paleprow` | `pale_stone_prowler.png` |

The Stalker and Prowler also have directional attack turnarounds in `mistwood_stalker_attack.png` and `pale_stone_prowler_attack.png`. Import their attack poses with `python tools/terralum/import_painted_turnaround.py <sheet> <asset> --attack`. The BAM builder uses these frames for all nine mirrored-human melee attack resources, with an idle/strike/recovery sequence per direction.

Convert a sheet into GemRB's nine directional 80x96 frame slots with:

```powershell
python tools/terralum/import_painted_turnaround.py terralum/art/reference/painted_turnarounds/mara.png mara00
```

The initial import duplicates each direction into four walk slots. It provides painted idle views, not hand-painted locomotion; the repeated walk frames are a prototype limitation and must be replaced with authored motion before final acceptance. Always inspect the built BAM in a live scene for palette, transparency, scale, facing, and ground anchoring.
