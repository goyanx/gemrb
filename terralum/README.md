# Terralum: The Shattered Meridian

Terralum is an original, small playable game pack for [GemRB](../README.md). GemRB is the Infinity Engine runtime, not a visual game editor. This first slice reuses the fork's redistributable demo data for character movement, interface, and a second area; it adds an original observatory scene, opening story, and a two-step discovery sequence. It does not contain Baldur's Gate assets.

## Build the game pack

From the repository root:

```powershell
python -m pip install Pillow
python tools/terralum/build_game.py
```

This creates `terralum/build/game` and `terralum/build/terralum.cfg`. The builder uses `demo/` as a data template, converts the generated observatory image into the 450 tiles of `AR0100.TIS`, and updates the game index. The art source and story source are tracked; the assembled data pack is ignored by Git.

## Run

Build GemRB with PNG, OGG, and FreeType support first. The [GemRB build instructions](../INSTALL) cover Windows and Linux. Then launch the engine using the generated config:

```powershell
path\to\gemrb.exe -c terralum\build\terralum.cfg
```

For the WSL build in `build/`, the builder also writes `terralum/build/terralum-wsl.cfg`:

```bash
./build/gemrb/gemrb -c terralum/build/terralum-wsl.cfg
```

Start a new game, move around the courtyard, select **Study** to uncover the route, then **Down** to enter the Hollow. Map and inventory controls come from the GemRB demo.

## Author with an AI coder

`tools/terralum/mcp_server.py` is a local [Model Context Protocol](https://modelcontextprotocol.io/) stdio server. Configure your MCP client to run it with Python from this checkout:

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

It offers `terralum_get_project`, `terralum_update_story`, `terralum_import_area_art`, and `terralum_build_game`. Story changes are stored in [`story.json`](story.json) and read when the game starts. Rebuild after changing the area art or title. To add scenes or rules, edit the GemRB Python scripts in `gemrb/GUIScripts/terralum/` and the builder in `tools/terralum/`.

## Scope of this slice

The observatory art is an AI-generated original image. The collision map and second area's art are inherited from the GemRB demo, so their geometry does not yet match the new scene. The Study and Down actions are command bar interactions; they are not gated by actor proximity. A dedicated area authoring pipeline, dialogue, combat tuning, and additional original assets are the next production steps.

GemRB code is GPL-2.0-or-later. The observatory image is offered as CC0-1.0. The demo template includes assets under several licenses; check [`REUSE.toml`](../REUSE.toml) and [`demo/README.md`](../demo/README.md) before distributing a packaged build.
