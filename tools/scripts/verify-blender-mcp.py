"""Exercise the real STDIO MCP -> Blender socket path, preserving every run."""
import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT = Path(__file__).resolve().parents[2]
RUNTIME = PROJECT / "tools" / "runtime" / "blender-mcp"
RUN_STAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
OUTPUT = PROJECT / "source-assets" / "blender-mcp-smoke" / RUN_STAMP
PROMPT = "连接相应的MCP，把所有资源全部准备好。 看看哪方面还有问题，还有需要，我们先提前做好一切准备。"


def text_result(result):
    return "\n".join(item.text for item in result.content if item.type == "text")


async def main():
    OUTPUT.mkdir(parents=True, exist_ok=False)
    server_env = {
        **os.environ,
        "DISABLE_TELEMETRY": "true",
        "BLENDER_MCP_DISABLE_TELEMETRY": "true",
        "BLENDERMCP_NO_UPDATE_CHECK": "1",
        "BLENDER_MCP_SAFE_MODE": "1",
        "BLENDER_HOST": "127.0.0.1",
        "BLENDER_PORT": "9876",
        "BLENDERMCP_ADDONS_DIR": str(RUNTIME / "blender-profile" / "scripts" / "addons"),
    }
    params = StdioServerParameters(
        command=str(RUNTIME / ".venv" / "Scripts" / "mcp-for-blender.exe"),
        args=["--host", "127.0.0.1", "--port", "9876"],
        env=server_env,
    )
    record = {"output": str(OUTPUT), "calls": {}}
    log_path = OUTPUT / "mcp-server.stderr.log"
    with log_path.open("w", encoding="utf-8") as error_log:
        async with stdio_client(params, errlog=error_log) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                init = await session.initialize()
                record["server_info"] = init.serverInfo.model_dump()
                tools = await session.list_tools()
                record["tool_names"] = [tool.name for tool in tools.tools]

                async def call(name, arguments):
                    result = await session.call_tool(name, arguments)
                    payload = text_result(result)
                    record["calls"][name] = payload
                    if result.isError or payload.startswith("Error") or "SandboxViolation" in payload:
                        raise RuntimeError(f"{name} failed: {payload}")
                    return payload

                addon = json.loads(await call("get_addon_status", {"user_prompt": PROMPT}))
                if not addon["up_to_date"] or addon["telemetry_consent"] is not False:
                    raise RuntimeError(f"Unexpected addon status: {addon}")
                await call("get_scene_info", {"user_prompt": PROMPT})
                object_name = "MCP_TransferProbe_" + RUN_STAMP.replace("-", "").replace("_", "")
                blend_path = OUTPUT / "connectivity-probe.blend"
                fbx_path = OUTPUT / "connectivity-probe.fbx"
                code = f'''
import bpy
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
probe = bpy.context.active_object
probe.name = {object_name!r}
probe.dimensions = (1.0, 1.0, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
material = bpy.data.materials.new("MCP_Probe_Slate")
material.diffuse_color = (0.12, 0.24, 0.38, 1.0)
probe.data.materials.append(material)
probe["purpose"] = "Blender MCP to Unreal Engine transfer verification; local diagnostic geometry"
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.wm.save_as_mainfile(filepath={str(blend_path)!r})
print({{"name": probe.name, "dimensions_m": list(probe.dimensions), "blend": {str(blend_path)!r}}})
'''
                await call("execute_blender_code", {"code": code, "user_prompt": PROMPT})
                object_info = await call("get_object_info", {"object_name": object_name, "user_prompt": PROMPT})
                await call("export_scene", {
                    "filepath": str(fbx_path), "format": "fbx", "object_names": [object_name],
                    "selection_only": True, "apply_modifiers": True, "user_prompt": PROMPT,
                })
                data = fbx_path.read_bytes()
                if not data.startswith(b"Kaydara FBX Binary") or len(data) < 1000:
                    raise RuntimeError("Export did not produce a valid FBX binary header.")
                record["fbx"] = {"path": str(fbx_path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                record["blend"] = str(blend_path)
                record["object"] = object_name
                record["success"] = True
    result_path = OUTPUT / "verification.json"
    result_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    (RUNTIME / "logs" / "latest-verification.json").write_text(
        json.dumps({"verification": str(result_path), "fbx": record["fbx"], "blend": record["blend"]}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"success": True, "verification": str(result_path), "fbx": record["fbx"], "blend": record["blend"]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
