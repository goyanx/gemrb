# Terralum: Scrolls of Byzantem

This project is a playable campaign prototype for [GemRB](../README.md). GemRB runs Infinity Engine games; it is not a visual editor. The game starts with Algoreth Jon Goren as a wizard seeking the scrolls of Byzantem. Seven chapters move from that early quest to his later, documented reign and the Tear of Chaos. This is a chapter structure inspired by long fantasy RPGs, **not** Baldur's Gate II playtime or content.

## Story basis

The local campaign archive `C:\Users\goyan\Documents\GolemDungeon - kingdoms - kingdom-alsperia [1203075571572154459].txt` supports the early scroll quest. The user-supplied `TERRALUM_LORE_CODEX.md` supports the later Wizard King, eastern academy, Tear of Chaos, Archives and Eldrador arc. The user clarified that in the early period Queen Alisande was married to King Edmon. The sources do not recover the later transition to Algoreth's reign and marriage, so the game leaves that interval unwritten. See [`lore_notes.md`](lore_notes.md) for provenance and uncertainties. Neither source archive is copied into this repository.

`story.json` contains seven chapter introductions and 23 dialogue beats. The seven playable locations are Alsperia Market, Mistwood Road, Lorian Cavern, Alsperia Court, Old Observatory Vault, Deep Archives, and Alsperia Skyport. They use original generated backdrops and the open demo's geometry template. Three hostile encounters currently spawn demo humanoids; their art, combat balance, and victory gates need further work. Dialogue is linear, with no branching choices yet. The chapter count is a pacing outline, not a full length RPG campaign.

[`campaign_plan.md`](campaign_plan.md) maps the seven acts to a longer quest and location plan, with archive facts separated from new material. The preserved [`story_scrolls_draft.json`](story_scrolls_draft.json) records the earlier game draft before the codex arrived; it is not the active campaign.

## Build and play

From the repository root:

```powershell
python -m pip install Pillow
python tools/terralum/build_game.py
./build/gemrb/gemrb -c terralum/build/terralum-wsl.cfg
```

The last command uses the WSL build in this checkout. On Windows with a native GemRB build, use `terralum/build/terralum.cfg`. `terralum/play.ps1` builds and launches through WSL. The assembled pack under `terralum/build/` is ignored by Git.

The voice clips under `terralum/audio/` were rendered locally with Kokoro ONNX using the `af_heart` woman voice. To regenerate them, use the standalone Kokoro Python environment and provide local model and voice files:

```powershell
python tools/terralum/render_audio.py --model path\to\kokoro-v1.0.onnx --voices path\to\voices-v1.0.bin
```

The audio renderer also creates three original looping ambient tracks. It needs `kokoro_onnx`, `numpy`, `soundfile`, and `ffmpeg`. The model files are not included in the repository. Narration plays on chapter entry and through the **Narrate** button. The area song table selects city, woodland, or cavern ambience.

## Author with an AI coder

Run `tools/terralum/mcp_server.py` as a stdio Model Context Protocol server. Its tools inspect the project, edit the title or hero name, edit a chapter beat, import art for one of the seven areas, and rebuild the pack. For example:

```json
{
  "mcpServers": {
    "terralum": {
      "command": "python",
      "args": ["D:/CODE/Terralum/gemrb/tools/terralum/mcp_server.py"]
    }
  }
}
```

GemRB and the inherited demo data have their own licenses; consult [`REUSE.toml`](../REUSE.toml) and [`demo/README.md`](../demo/README.md) before distribution. The new backdrop images, narration clips, and generated music are offered as CC0-1.0. The authoring code is GPL-2.0-or-later.
