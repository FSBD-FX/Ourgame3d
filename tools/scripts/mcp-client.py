"""Use the official FastMCP client to verify the project's local Unity MCP.

Run with tools/runtime/unity-mcp/Scripts/python.exe. Request files contain a
JSON list of {"resource": uri} or {"tool": name, "arguments": {...}} entries.
Requests share one initialized MCP session. No API keys are required.
"""
import argparse
import asyncio
import json
from pathlib import Path

from fastmcp import Client


def text_or_json(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


async def run(args):
    output = []
    async with Client(args.url, timeout=args.timeout, name="codex-game-readiness") as client:
        if args.inventory or args.describe:
            tools = await client.list_tools()
            resources = await client.list_resources()
            output.append({"tools": [t.name for t in tools], "resources": [str(r.uri) for r in resources]})
            if args.describe:
                output.append({"schemas": [t.model_dump(mode="json") for t in tools if t.name in args.describe]})
        requests = []
        if args.request_file:
            requests.extend(json.loads(Path(args.request_file).read_text(encoding="utf-8-sig")))
        if args.resource:
            requests.append({"resource": args.resource})
        if args.tool:
            requests.append({"tool": args.tool, "arguments": json.loads(args.arguments)})
        for request in requests:
            if "resource" in request:
                result = await client.read_resource(request["resource"])
                output.append({"resource": request["resource"], "contents": [text_or_json(r.text) if hasattr(r, "text") else {"mimeType": r.mimeType, "blob": "omitted"} for r in result]})
            else:
                result = await client.call_tool(request["tool"], request.get("arguments", {}), raise_on_error=False)
                contents = [text_or_json(c.text) if hasattr(c, "text") else {"type": c.type, "binary": "omitted"} for c in result.content]
                output.append({"tool": request["tool"], "is_error": result.is_error, "contents": contents})
    payload = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload + "\n", encoding="utf-8")
        print(json.dumps({"output": str(destination.resolve()), "responses": len(output)}, ensure_ascii=False))
    else:
        print(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8080/mcp")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--inventory", action="store_true")
    parser.add_argument("--describe", nargs="+")
    parser.add_argument("--resource")
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--request-file")
    parser.add_argument("--output")
    asyncio.run(run(parser.parse_args()))
