"""Preserve this compiled visual slice before parallel Actor work resumes."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path("F:/Ourgame")
DEST = ROOT / "source-assets/production/backups/2026-10-15_armor-layer-preview-compiled-v016"
if DEST.exists():
    raise RuntimeError("Never overwrite a prior compiled snapshot")
paths = []
for directory in ("UnrealGame/Source", "UnrealGame/Config", "UnrealGame/Content/Production"):
    paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file())
paths.extend(ROOT / p for p in (
    "UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll",
    "UnrealGame/Saved/Automation/FirstRoom-20261015-072535/index.json",
    "tools/scripts/ue-import-armor-idle-v001.py",
    "tools/scripts/ue-import-armor-primary1-four-v002.py",
    "tools/scripts/verify-content-combat.ps1",
    "tools/scripts/verify-native-capture-pixels.py",
    "tools/scripts/retain-ue-process-media.py",
    "source-assets/production/first-unit-armor-layers-v001/manifests/import-armor-idle-v001.json",
    "source-assets/production/first-unit-armor-layers-v001/manifests/import-armor-primary1-four-v002.json",
))
paths.extend((ROOT / "UnrealGame/Saved/Bootstrap").glob("armor-primary1-four-v002-import-*.json"))
paths.extend((ROOT / "UnrealGame/Saved/Bootstrap").glob("armor-idle-v001-import*.json"))
rows = []
for source in sorted(set(paths)):
    relative = source.relative_to(ROOT)
    target = DEST / relative
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"Snapshot mismatch: {source}")
    rows.append({"path": relative.as_posix(), "bytes": source.stat().st_size, "sha256": digest})
report = {
    "snapshot": DEST.as_posix(), "files": rows,
    "copied_files": len(rows), "bytes": sum(row["bytes"] for row in rows),
    "status": "compiled visual preview; ranged actual RED13 remains; not all-tests-GREEN or full-content acceptance",
    "ranged_red_report": "UnrealGame/Saved/Automation/FirstRoom-20261015-072535/index.json",
    "historical_old38_passed_in_red_run": True, "formal_complete_units": 0,
}
(DEST / "compiled-source-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "files"}, ensure_ascii=False))
