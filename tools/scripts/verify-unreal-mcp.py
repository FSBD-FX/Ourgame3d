"""Verify STDIO MCP reads, or an explicitly requested reversible actor roundtrip."""
import argparse
import asyncio
import json
import os
import tomllib
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT = Path(__file__).resolve().parents[2]
RUNTIME = PROJECT / "tools" / "runtime" / "unreal-mcp"


async def main(list_only=False, global_config=False, server_name="unreal-mcp", roundtrip=False):
    run_directory = RUNTIME / "logs" / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_directory.mkdir(parents=True, exist_ok=False)
    path = run_directory / "verification.json"
    launch = {
        "command": str(RUNTIME / ".venv" / "Scripts" / "python.exe"),
        "args": [str(PROJECT / "tools" / "scripts" / "run-unreal-mcp.py")],
        "env": {"DISABLE_TELEMETRY": "true", "MCP_DISABLE_TELEMETRY": "true"},
    }
    config_path = None
    if global_config:
        config_path = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
        configuration = tomllib.loads(config_path.read_text(encoding="utf-8-sig"))
        launch = configuration["mcp_servers"][server_name]
        if launch.get("enabled") is False:
            raise RuntimeError(f"Configured MCP server {server_name!r} is disabled.")
    params = StdioServerParameters(
        command=launch["command"],
        args=launch.get("args", []),
        env={**os.environ, **launch.get("env", {})},
    )
    record = {"list_only": list_only, "engine_verified": False}
    record["launch"] = {"config_path": str(config_path) if config_path else None,
                        "server_name": server_name if global_config else None,
                        "command": params.command, "args": params.args}
    with (run_directory / "server.stderr.log").open("w", encoding="utf-8") as error_log:
        async with stdio_client(params, errlog=error_log) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialized = await session.initialize()
                record["server_info"] = initialized.serverInfo.model_dump()
                tool_list = await session.list_tools()
                record["tool_names"] = [tool.name for tool in tool_list.tools]
                record["tools"] = [tool.model_dump() for tool in tool_list.tools]
                if "get_actors_in_level" not in record["tool_names"]:
                    raise RuntimeError("Expected Unreal actor query tool was not registered.")
                if not list_only:
                    result = await session.call_tool("get_actors_in_level", {})
                    record["actor_query"] = result.model_dump()
                    texts = [item.text for item in result.content if item.type == "text"]
                    # MCP 1.5 may serialize list elements as separate content blocks.
                    actors = []
                    for text in texts:
                        value = json.loads(text)
                        actors.extend(value if isinstance(value, list) else [value])
                    actors = [actor for actor in actors if isinstance(actor, dict) and actor.get("name") and actor.get("class")]
                    if result.isError or not actors:
                        raise RuntimeError("No actors returned: UE bridge unavailable or level empty; engine is not verified.")
                    record["actor_count"] = len(actors)
                    actor = next((item for item in actors if item["class"] == "StaticMeshActor"), actors[0])
                    properties = await session.call_tool("get_actor_properties", {"name": actor["name"]})
                    record["actor_properties"] = properties.model_dump()
                    property_text = "\n".join(item.text for item in properties.content if item.type == "text")
                    property_value = json.loads(property_text)
                    if properties.isError or property_value.get("status") != "success":
                        raise RuntimeError(f"Actor properties read failed: {property_text}")
                    record["read_actor"] = actor
                    record["engine_verified"] = True
                    if roundtrip:
                        diagnostic_name = "MCP_Diagnostic_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                        baseline_names = {item["name"] for item in actors}
                        record["diagnostic_name"] = diagnostic_name
                        record["roundtrip_verified"] = False
                        record["roundtrip_calls"] = []
                        created = False

                        async def call_dict(name, arguments):
                            reply = await session.call_tool(name, arguments)
                            record["roundtrip_calls"].append({"tool": name, "arguments": arguments, "result": reply.model_dump()})
                            text = "\n".join(item.text for item in reply.content if item.type == "text")
                            value = json.loads(text)
                            if reply.isError or not isinstance(value, dict) or value.get("status") != "success":
                                raise RuntimeError(f"{name} failed: {text}")
                            return value["result"]

                        try:
                            spawned = await call_dict("spawn_actor", {"name": diagnostic_name, "type": "StaticMeshActor", "location": [0, 0, 5000], "rotation": [0, 0, 0]})
                            created = True
                            if spawned["name"] != diagnostic_name:
                                raise RuntimeError("Spawned actor name did not match diagnostic name.")
                            initial = await call_dict("get_actor_properties", {"name": diagnostic_name})
                            target = {"location": [120.0, 230.0, 340.0], "rotation": [0.0, 45.0, 0.0], "scale": [1.25, 0.75, 1.5]}
                            await call_dict("set_actor_transform", {"name": diagnostic_name, **target})
                            transformed = await call_dict("get_actor_properties", {"name": diagnostic_name})
                            for key, expected in target.items():
                                if any(abs(actual - wanted) > 0.0001 for actual, wanted in zip(transformed[key], expected)):
                                    raise RuntimeError(f"Transform read-back differs for {key}: {transformed[key]}")
                            record["initial_diagnostic"] = initial
                            record["transformed_diagnostic"] = transformed
                            record["roundtrip_verified"] = True
                        except Exception as error:
                            record["roundtrip_error"] = str(error)
                            raise
                        finally:
                            if created:
                                await call_dict("delete_actor", {"name": diagnostic_name})
                                remaining = await session.call_tool("get_actors_in_level", {})
                                record["after_delete"] = remaining.model_dump()
                                after_actors = []
                                for content in remaining.content:
                                    if content.type == "text":
                                        value = json.loads(content.text)
                                        after_actors.extend(value if isinstance(value, list) else [value])
                                after_names = {item["name"] for item in after_actors if isinstance(item, dict) and item.get("name")}
                                record["diagnostic_absent"] = diagnostic_name not in after_names
                                record["original_actor_names_unchanged"] = baseline_names == after_names
                                if not record["diagnostic_absent"] or not record["original_actor_names_unchanged"]:
                                    record["roundtrip_verified"] = False
                                    raise RuntimeError("Actor cleanup did not restore the original actor name set.")
                            path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
                            print(f"Roundtrip evidence: {path}", flush=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"verification": str(path), "tool_count": len(record["tool_names"]), "engine_verified": record["engine_verified"], "roundtrip_verified": record.get("roundtrip_verified")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--global-config", action="store_true")
    parser.add_argument("--server-name", default="unreal-mcp")
    parser.add_argument("--roundtrip", action="store_true")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.list_only, arguments.global_config, arguments.server_name, arguments.roundtrip))
