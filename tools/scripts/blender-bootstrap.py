"""Enable the pinned MCP addon in the project's isolated Blender profile."""
import json
import os
from pathlib import Path

import addon_utils
import bpy


RUNTIME = Path(__file__).resolve().parents[1] / "runtime" / "blender-mcp"
EXPECTED_PROFILE = (RUNTIME / "blender-profile").resolve()
configured_profile = Path(os.environ.get("BLENDER_USER_RESOURCES", "")).resolve()
if configured_profile != EXPECTED_PROFILE:
    raise RuntimeError("Use start-blender-mcp.ps1 so existing Blender preferences stay isolated.")

addon_utils.enable("blender_mcp", default_set=True, persistent=True)
addon = bpy.context.preferences.addons.get("blender_mcp")
if addon is None:
    raise RuntimeError("The pinned blender_mcp addon could not be enabled.")
addon.preferences.telemetry_consent = False
scene = bpy.context.scene
scene.blendermcp_port = 9876
scene.blendermcp_auto_start_server = True
for integration in ("polyhaven", "hyper3d", "hunyuan3d", "sketchfab", "tripo", "polypizza"):
    setattr(scene, f"blendermcp_use_{integration}", False)

# Only this project profile is written; never the normal AppData profile.
bpy.ops.wm.save_userpref()
bpy.ops.blendermcp.start_server()
server = bpy.types.blendermcp_server
if not server.running or server.host not in ("localhost", "127.0.0.1"):
    raise RuntimeError("The local Blender MCP socket did not start safely.")
status = {
    "blender_version": bpy.app.version_string,
    "blender_binary": bpy.app.binary_path,
    "process_id": os.getpid(),
    "addon_enabled": "blender_mcp" in bpy.context.preferences.addons,
    "profile": str(EXPECTED_PROFILE),
    "socket_host": server.host,
    "socket_port": server.port,
    "telemetry_consent": addon.preferences.telemetry_consent,
    "disable_telemetry": os.environ.get("DISABLE_TELEMETRY"),
    "no_update_check": os.environ.get("BLENDERMCP_NO_UPDATE_CHECK"),
}
(RUNTIME / "logs").mkdir(exist_ok=True)
(RUNTIME / "logs" / "blender-startup-status.json").write_text(
    json.dumps(status, indent=2), encoding="utf-8"
)
print("CODEX_GAME_BLENDER_READY " + json.dumps(status), flush=True)
