---
name: unreal-mcp-orchestrator
description: Operate the UE5.5 and Blender toolchain for F:/Ourgame. Use when opening or building CodexDungeon, querying or modifying its Unreal Editor through MCP, importing prepared assets, or diagnosing this project's Unreal/Blender connection. Routes to the locally verified commands, source provenance, and evidence reports.
---

# CodexDungeon UE5 workflow

Read the project `AGENTS.md`, `README.md`, and `docs/preparation-status-2026-10-10.md` for current scope and evidence. The authoritative engine is **UE5.5.4**, project `F:/Ourgame/UnrealGame/CodexDungeon.uproject`. `Game/` is the historical Unity preparation project.

Read and maintain the root `项目需求台账.md` for each new or changed user requirement. The user designated **F:/Ourgame** on 2026-10-12; E:/codex_game is a preserved pre-migration copy. Weapon, equipment and multiple item systems belong to the long-term scope, with exact types and counts awaiting design. See `docs/project-location-2026-10-12.md` for migrated launch paths and verification boundaries; preserve historical E-source manifests and logs.

The user fixed the game direction on 2026-10-11: Lost Castle 1/2 inspired **2.5D side-view beat-em-up**, single-player first. Read `docs/2.5d-direction-2026-10-11.md`. Use separate ground depth and jump height, fixed camera framing, and a 2D character/layered-scene presentation baseline. Existing Foundation/AssetIntake maps and 3D clips are tool evidence or conversion sources, not accepted final art. Paper2D is bundled and was mounted by the verified editor run; sprites, flipbooks and 2.5D gameplay still require actual validation. Do not count 3D AnimSequences or model preview PNGs as prepared 2D character animations.

## Start and connect

- Run `tools/scripts/Start-ProjectTools.ps1` to start or reuse this project's Blender and Unreal Editor.
- Inspect `tools/scripts/unreal-status.ps1`; a process launch alone does not establish readiness.
- UE bridge listens at **127.0.0.1:55557**; Blender addon at **127.0.0.1:9876**. Preserve loopback binding and check the owning project before managing an existing process.
- Codex global config has `unreal-mcp` and `blender-mcp` STDIO entries. Codex starts these server processes; do not separately daemonize STDIO.
- The current setup exposed the native tools automatically (Blender36 / Unreal30). If a future session lacks newly configured tools, check its MCP connection/loading state; the official Python client can verify the configured launch separately:

```powershell
& 'F:\Ourgame\tools\runtime\unreal-mcp\.venv\Scripts\python.exe' 'F:\Ourgame\tools\scripts\verify-unreal-mcp.py' --global-config
```

Use the returned tool schemas. Read the current level and actor properties before changing objects. Use unique names for diagnostic actors and clean them up. Successful MCP initialization is distinct from a successful UE query. The pinned server exposes 30 tools, but has no arbitrary Python execution or PIE Play / Stop tool; use supported UE Python / editor automation for those operations.

## Build and asset handoff

- Close this project's Editor before rebuilding its plugin / C++ module. `tools/scripts/unreal-build.ps1` selects UE5.5's compiler and defaults to two parallel actions for this 16 GB machine. Read the actual exit code and log.
- Preserve `tools/unreal-mcp` at its pinned commit. Local plugin fixes belong in the project copy and an explicit patch; see `docs/unreal-bootstrap-2026-10-10.md`.
- Keep .blend, generated inputs and original third-party packages under `source-assets/`; import selected runtime assets into `UnrealGame/Content/`.
- UE uses centimetres. Verify exported bounds, axis and transforms with the actual importer. The saved Blender probe is **1×1×2 metres**, expected UE bounds **100×100×200 cm**; do not silently correct a failed measurement in documentation.
- In UE Python, run `tools/scripts/ue-import-prepared-assets.py` for the prepared sample set. `--preflight` in ordinary Python checks sources only. Read `Saved/Bootstrap/asset-import-report.json` for actual classes, saved packages, animations, selected pose gates and bounds. Default runs inspect existing destinations; do not enable replacement without backing up affected assets.
- Read the fresh-project reproduction section of `docs/asset-preparation-2026-10-10.md` before importing these characters again. This project's two Mini Dungeon characters require animation-only 60 FPS sampling and `import_rotation.roll=+90`; mesh rotation stays zero. Actual canonical animation repair and PIE passed. The latest combined fresh mesh+animation importer defaults have only syntax/source preflight validation, so require the documented 32-name, same-Skeleton, root/head pose gates and rendered check before claiming a new import succeeds.
- The independent `ue-diagnose-character-axis.py` repair first validates isolated animations. `CODEX_CHARACTER_AXIS_REPAIR=1` enables repair mode; applying to canonical assets additionally requires `CODEX_CHARACTER_AXIS_APPLY_CANONICAL=1` and `CODEX_CHARACTER_AXIS_BACKUP` pointing to a real, newly preserved backup with hashes. Follow the exact documented steps and clear these environment variables afterward. Never use an Actor tilt to conceal wrong animation axes.
- Mini Dungeon has a simplified skeleton. Use its own verified clips first; UAL2 and standard UE humanoid retargeting require a separate trial. FBX animation stacks are not proof of imported or playable AnimSequences.

## Verify the requested result

Validate the actual Editor or game behavior: objects persist, assets render, selected animation plays, and PIE works where relevant. Record source, run log and scope of proof. Save display media under `F:/Ourgame/过程图稿与视频` before showing it, following that directory's README.

For generation, use the adjacent `asset-gen` Skill and project wrapper. Current free assets do not require paid APIs; first paid generation requires a confirmed cost. For tool versions, complete license gaps and connection details, read `docs/ue5-mcp-evaluation-2026-10-10.md` and `docs/blender-connection-2026-10-10.md`.
