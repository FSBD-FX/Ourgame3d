"""Six-phase source-cell X registration inside the component extraction hook.

v006 failed by choosing nonexistent plain twins; v007's affine translation
rounded soft-edge RGB by one. Both are retained. This trial translates during
native component placement instead, before atlas composition. No extra affine
resampling, AI call, redraw, per-frame scaling or changed timing.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from PIL import Image

ROOT = Path("F:/Ourgame")
BASE = ROOT / "source-assets/production/fairytale-hero-v001"
OLD = BASE / "sprite-run-walk-v005"
RUN = BASE / "sprite-run-walk-v008"
SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")


def main():
    assert not RUN.exists(), "Never overwrite a previous trial"
    RUN.mkdir()
    logs = RUN / "project-step-logs"
    logs.mkdir()
    for source in (Path(__file__), ROOT / "tools/scripts/extract-sprite-shared-row-scale.py"):
        shutil.copy2(source, logs / source.name)
    for name in ("raw", "references", "prompts"):
        shutil.copytree(OLD / name, RUN / name)
    shutil.copy2(OLD / "base-source.png", RUN / "base-source.png")
    request = json.loads((OLD / "sprite-request.json").read_text(encoding="utf-8"))
    request["character"]["id"] = "fairytale-hero-walk-native-cell-x-v008"
    request["project_horizontal_registration"] = "native_source_cell_x"
    request["project_registration_limits"] = "Original cell center only; body/feet root unmeasured. Same global scale and bottom registration as v005."
    (RUN / "sprite-request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    steps = [("extract", ROOT / "tools/scripts/extract-sprite-shared-row-scale.py"),
             ("compose", SKILL / "scripts/compose_sprite_atlas.py"),
             ("curated", SKILL / "scripts/export_curated_pngs.py"),
             ("preview", SKILL / "scripts/preview_animation.py"),
             ("gif", SKILL / "scripts/compose_sprite_gif.py")]
    for label, script in steps:
        args = [sys.executable, "-B", "-X", "utf8", str(script), "--run-dir", str(RUN)]
        if label == "gif":
            args += ["--state", "walk"]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        (logs / f"{label}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(label, result.returncode)
        if result.returncode:
            print(result.stdout, result.stderr)
            raise SystemExit(result.returncode)
    manifest = json.loads((RUN / "frames/frames-manifest.json").read_text(encoding="utf-8"))
    assert manifest["ok"] and not manifest["errors"] and not manifest["warnings"]
    fit = manifest["rows"][0]["shared_row_fit"]
    assert fit["horizontal_registration"] == "native_source_cell" and fit["scale"] == 416 / 1043
    records = []
    for index in range(6):
        old = Image.open(OLD / f"frames/walk/frame-{index}.png").convert("RGBA")
        target = Image.open(RUN / f"curated/frame-{index}.png").convert("RGBA")
        a, b = old.getbbox(), target.getbbox()
        assert old.crop(a).tobytes() == target.crop(b).tobytes()
        assert a[1] == b[1] and a[3] == b[3] and b[0] - a[0] == b[2] - a[2]
        assert b[0] >= 48 and b[1] >= 48 and b[2] <= 464 and b[3] <= 464
        assert (RUN / f"frames/walk/frame-{index}.png").read_bytes() == (RUN / f"curated/frame-{index}.png").read_bytes()
        records.append({"frame": index, "native_request": request["project_packing"]["frames"][index]["native_request"],
                        "baseline_bbox": list(a), "registered_bbox": list(b), "dx": b[0] - a[0], "dy": 0,
                        "cropped_RGBA_bytes_unchanged": True, **fit["native_source_cell_records"][index]})
    runtime = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
    assert runtime["animation"]["rows"]["walk"]["durations_ms"] == [83] * 6
    assert len(runtime["frame_layout"]["rows"]["walk"]) == 6
    receipt = {"schema": "native-cell-x-registration-v2", "old_run": str(OLD), "new_run": str(RUN),
               "method": "Installed chroma/component pipeline plus project shared-fit placement hook; no post-affine resample",
               "durations_ms": [83] * 6, "native_generation_calls_added": 0,
               "runtime_imported": False, "motion_accepted": False, "actual_body_or_foot_root_measured": False,
               "records": records}
    (RUN / "source-cell-registration-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
