"""Read-only candidate checks; never imports Unreal or runs native tests."""
from pathlib import Path
import ast
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent


def pin(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def delimiters(source):
    # Lex only strings, chars and comments. This is a coarse syntax check,
    # explicitly not a C++ parser, compile, native test or acceptance result.
    tokens = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|R"([^ ()\\\t\r\n]{0,16})\([\s\S]*?\)\1"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    source = tokens.sub("", source)
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for char in source:
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            assert stack and stack.pop() == pairs[char], "Mismatched delimiter"
    assert not stack, "Unclosed delimiter"


before = json.loads((OUT / "exact-before-pins-v001.json").read_text(encoding="utf-8-sig"))
baseline = []
design = []
for entry in before["files"]:
    original = Path(entry["path"])
    candidate = OUT / "baseline-source" / original.name
    checked = candidate if candidate.is_file() else original
    assert pin(checked) == {key: entry[key] for key in ("bytes", "sha256")}, checked
    (baseline if candidate.is_file() else design).append(str(checked))

stage = json.loads((OUT / "stage0-freeze-v001.json").read_text(encoding="utf-8-sig"))
for entry in stage["files"]:
    assert pin(Path(entry["path"])) == {key: entry[key] for key in ("bytes", "sha256")}, entry["path"]
for path in (OUT / "new-source").iterdir():
    assert path.read_bytes() == (OUT / "production-source" / path.name).read_bytes(), path

cpp = []
for path in (OUT / "production-source").iterdir():
    delimiters(path.read_text(encoding="utf-8-sig"))
    cpp.append(path.name)
python = []
for path in OUT.glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    python.append(path.name)

print(json.dumps({
    "status": "STATIC_ONLY_NATIVE_UNCOMPILED_UNRUN",
    "baseline_source_pins": len(baseline),
    "design_pins": len(design),
    "frozen_stage0_pins": len(stage["files"]),
    "frozen_test_sha256": pin(OUT / "new-tests/DungeonFirstBatchGuardRoomTests.cpp")["sha256"],
    "new_source_copies_exact": True,
    "coarse_cpp_delimiter_checks": cpp,
    "python_ast_checks": python,
    "actual_Source_read_as_production_input": False,
    "UE_UBT_native_run": False,
}, ensure_ascii=False, indent=2))
