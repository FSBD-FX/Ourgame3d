"""Restore the pinned external plugin locally; never overwrite modified files."""
from pathlib import Path
import hashlib
import json
import os
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    spec = json.loads((root / "docs/github/external-plugin-files.json").read_text(encoding="utf-8"))
    target = root / "UnrealGame/Plugins/UnrealMCP"
    missing = []
    for item in spec["files"]:
        destination = target / item["path"]
        if destination.exists():
            if digest(destination.read_bytes()) != item["sha256"]:
                raise RuntimeError("Existing plugin file was modified: " + item["path"])
        else:
            missing.append(item)
    if not missing:
        print("Pinned UnrealMCP plugin already matches all source hashes.")
        return
    cache = root / "tools/runtime/github-restore" / ("unreal-mcp-" + spec["commit"][:12])
    environment = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")

    def git(*arguments):
        return subprocess.run(["git", *arguments], env=environment, check=True,
                              text=True, stdout=subprocess.PIPE).stdout.strip()

    if not (cache / ".git").exists():
        cache.mkdir(parents=True, exist_ok=False)
        git("init", str(cache))
        git("-C", str(cache), "remote", "add", "origin", spec["repository"])
    origin = git("-C", str(cache), "remote", "get-url", "origin")
    if origin != spec["repository"]:
        raise RuntimeError("Dependency checkout has an unexpected origin.")
    git("-C", str(cache), "config", "core.autocrlf", "false")
    git("-C", str(cache), "fetch", "--depth=1", "origin", spec["commit"])
    git("-C", str(cache), "checkout", "--detach", spec["commit"])
    if git("-C", str(cache), "rev-parse", "HEAD") != spec["commit"]:
        raise RuntimeError("Dependency commit mismatch.")
    prepared = []
    for item in missing:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("Invalid dependency member path.")
        data = (cache / spec["plugin_path"] / relative).read_bytes()
        if item["path"] == "Source/UnrealMCP/Private/MCPServerRunnable.cpp":
            data = data.replace(b"\r\n", b"\n")
            replacements = [
                (b'#include "HAL/PlatformTime.h"', b'#include "HAL/PlatformTime.h"\n#include "Containers/StringConv.h"'),
                (b"uint8 Buffer[8192];", b"uint8 Buffer[BufferSize + 1];"),
                (b"ClientSocket->Recv(Buffer, sizeof(Buffer), BytesRead)", b"ClientSocket->Recv(Buffer, BufferSize, BytesRead)"),
                (b"if (!ClientSocket->Send((uint8*)TCHAR_TO_UTF8(*Response), Response.Len(), BytesSent))", b"FTCHARToUTF8 Utf8Response(*Response);\n                                if (!ClientSocket->Send(reinterpret_cast<const uint8*>(Utf8Response.Get()), Utf8Response.Length(), BytesSent))"),
                (b"uint8 Buffer[MaxBufferSize];", b"uint8 Buffer[MaxBufferSize + 1];"),
                (b"if (!Client->Send((uint8*)TCHAR_TO_UTF8(*Response), Response.Len(), BytesSent))", b"FTCHARToUTF8 Utf8Response(*Response);\n    if (!Client->Send(reinterpret_cast<const uint8*>(Utf8Response.Get()), Utf8Response.Length(), BytesSent))"),
            ]
            for before, after in replacements:
                if data.count(before) != 1:
                    raise RuntimeError("Pinned local fix no longer applies.")
                data = data.replace(before, after, 1)
        variants = [data]
        if b"\0" not in data:
            lf = data.replace(b"\r\n", b"\n")
            variants.extend([lf, lf.replace(b"\n", b"\r\n"),
                             lf.rstrip(b"\n") + b"\n",
                             (lf.rstrip(b"\n") + b"\n").replace(b"\n", b"\r\n")])
        matched = next((candidate for candidate in variants
                        if len(candidate) == item["bytes"] and digest(candidate) == item["sha256"]), None)
        if matched is None:
            raise RuntimeError("Restored plugin differs from the pinned project file: " + item["path"])
        prepared.append((target / relative, matched))
    # All members pass before any plugin source is installed.
    for destination, data in prepared:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
    print("Restored", len(prepared), "external plugin files with exact project SHA256 hashes.")


if __name__ == "__main__":
    main()
