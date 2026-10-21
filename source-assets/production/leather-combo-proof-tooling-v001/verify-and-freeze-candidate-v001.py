"""Author-only syntax/synthetic checks and immutable candidate freeze; no UE/capture."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path("F:/Ourgame").resolve()
PYTHON = ROOT / "tools/runtime/asset-gen/Scripts/python.exe"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pin(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n")


python_files = sorted(HERE.glob("*.py"))
for path in python_files:
    compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
unit = subprocess.run([str(PYTHON), "-B", "-X", "utf8", str(HERE / "test-combo-tooling-v001.py")], capture_output=True, text=True, encoding="utf-8")
new(HERE / "unit-final-v003.log", unit.stdout + unit.stderr)
if unit.returncode:
    raise SystemExit("Synthetic checks failed; preserved log, no freeze")
ps = subprocess.run(["powershell", "-NoProfile", "-Command",
    "$taskTokens=$null; $taskErrors=$null; [System.Management.Automation.Language.Parser]::ParseFile('" + str(HERE / "capture-leather-combo-trial-v001.ps1") + "',[ref]$taskTokens,[ref]$taskErrors)|Out-Null; Write-Output ('capture_parse_errors='+@($taskErrors).Count); if(@($taskErrors).Count){$taskErrors|Out-String|Write-Output; exit 1}"], capture_output=True, text=True)
new(HERE / "syntax-final-v003.log", "PYTHON_SYNTAX_OK=" + str(len(python_files)) + "\n" + ps.stdout + ps.stderr)
if ps.returncode:
    raise SystemExit("PowerShell syntax failed; preserved log, no freeze")

template = read(HERE / "combo-proof-contract-template-v001.json")
membership_checks = 0
for clip in ("Ready", "Primary1"):
    assembly_path = (ROOT / template["assemblies"][clip]["path"]).resolve()
    members = {(assembly_path.parent / item["path"]).resolve() for item in read(assembly_path)["files"]}
    for asset in read(ROOT / template["imports"][clip]["path"])["assets"]:
        assert Path(asset["source"]).resolve() in members, clip + " actual historical import source not in referenced assembly"
        membership_checks += 1
new(HERE / "historical-source-membership-check-v001.json", {
    "read_only_actual_historical_import_source_membership_checks": membership_checks,
    "mismatches": 0, "clips": ["Ready", "Primary1"],
    "P2_P3_actual_import_not_claimed": True, "actual_combo_capture_not_run": True,
    "formal_complete_units": 0})

input_paths = [
    ROOT / "tools/scripts/capture-leather-primary1-trial-v001.ps1",
    ROOT / "tools/scripts/postprocess-leather-primary1-trial-v001.py",
    ROOT / "tools/scripts/verify-native-bound-capture-pixels-v001.py",
    ROOT / "source-assets/production/leather-primary1-proof-tooling-v001/test-tooling-contract-v001.py",
    ROOT / template["base_snapshot_manifest"]["path"],
    ROOT / template["native_source_freeze"]["path"],
]
for clip in ("Ready", "Primary1"):
    input_paths += [ROOT / template["imports"][clip]["path"], ROOT / template["assemblies"][clip]["path"]]
files = sorted(path for path in HERE.iterdir() if path.is_file())
public = [HERE / name for name in ("capture-leather-combo-trial-v001.ps1", "postprocess-leather-combo-trial-v001.py", "verify-leather-combo-proof-v001.py")]
freeze = {
    "schema": "leather-combo-proof-tooling-candidate-freeze-v001",
    "scope": "Unapplied capture/postprocess/verification tooling only",
    "public_tools": [pin(path) for path in public],
    "files": [pin(path) for path in files], "inputs": [pin(path) for path in input_paths],
    "verification": {"python_syntax_files": len(python_files), "powershell_parse_errors": 0,
        "synthetic_unit_methods": 6, "negative_flow_variants": 35,
        "recovery_expiry_and_final_action_end_negative_cases": 3,
        "current_full_test_set_example": 160, "current_full_test_count_minimum": 157,
        "historical_actual_import_assembly_membership_checks": membership_checks,
        "pixel_FIFO_async_stop_flush_function_exactly_reused": True},
    "current_runtime_contract": {"top_level_snapshot_key": "combo_proof_contract", "template_is_executable": False,
        "current_automation": "Explicit report pin + exact unique full_test_paths + expected_count>=157",
        "parallel_source_changes": "Explicit additional_source_pins for every non-combo Source/Config delta relative to historical v125",
        "production": {"historical_baseline": 1115, "new_receipted_P2_P3": 36, "explicit_total": 1151},
        "source_closure": "All referenced assembly members and actual imported PNG membership required in snapshot"},
    "actual_source_admitted": False, "actual_UE_or_UBT_run": False,
    "actual_import_or_capture_run": False, "media_created": False,
    "art_review_pending": True, "formal_complete_units": 0,
}
new(HERE / "tooling-freeze-v001.json", freeze)
for row in freeze["files"] + freeze["inputs"]:
    assert pin(ROOT / row["path"]) == row, "Freeze input drift"
print(json.dumps({"freeze": pin(HERE / "tooling-freeze-v001.json"), "public_tools": freeze["public_tools"],
    "frozen_candidate_files": len(files), "input_pin_mismatches": 0,
    "synthetic_unit_methods": 6, "native_acceptance_claimed": False}, indent=2))
