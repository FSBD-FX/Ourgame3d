"""Read-only verification of the configured Codex -> STDIO -> Blender connection."""
import asyncio
import json
import os
import tomllib
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    project = Path(__file__).resolve().parents[2]
    config = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
    launch = tomllib.loads(config.read_text(encoding="utf-8-sig"))["mcp_servers"]["blender-mcp"]
    if launch.get("enabled") is False:
        raise RuntimeError("Configured blender-mcp server is disabled.")
    directory = project / "tools/runtime/blender-mcp/logs" / ("configured-check-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    directory.mkdir(parents=True, exist_ok=False)
    params = StdioServerParameters(command=launch["command"], args=launch.get("args", []), env={**os.environ, **launch.get("env", {})})
    record = {"config": str(config), "command": params.command, "args": params.args, "success": False, "calls": {}}
    try:
        with (directory / "server.stderr.log").open("w", encoding="utf-8") as error_log:
            async with stdio_client(params, errlog=error_log) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    record["initialize"] = (await session.initialize()).model_dump()
                    schemas = {tool.name: tool for tool in (await session.list_tools()).tools}
                    record["tool_count"] = len(schemas)
                    for name in ["get_addon_status", "get_scene_info"]:
                        record.setdefault("schemas", {})[name] = schemas[name].inputSchema
                        # Preserve the user's authorized setup goal verbatim for tool intent.
                        result = await session.call_tool(name, {"user_prompt": "连接相应的MCP，把所有资源全部准备好。 看看哪方面还有问题，还有需要，我们先提前做好一切准备。"})
                        record["calls"][name] = result.model_dump()
                        value = "\n".join(item.text for item in result.content if item.type == "text")
                        if result.isError or value.startswith("Error"):
                            raise RuntimeError(f"{name} failed: {value}")
                        parsed = json.loads(value)
                        if name == "get_addon_status" and parsed.get("telemetry_consent") is not False:
                            raise RuntimeError("Blender telemetry consent is not disabled.")
                    record["success"] = True
    finally:
        (directory / "verification.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"success": record["success"], "tool_count": record["tool_count"], "verification": str(directory / "verification.json")}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
