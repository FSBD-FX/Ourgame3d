"""Make an X-only registered six-pose trial through sprite-gen curation.

Uses the pinned installed extraction plus the existing shared-row fit. All
artwork, order and numeric durations remain unchanged. Native1254 source-cell
center is the registration basis, not a claimed body or foot root.
Run with sprite-gen's own virtual environment.
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
RUN = BASE / "sprite-run-walk-v007"
SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not RUN.exists(), "Keep every prior trial; choose a new run version"
    assert sha(SKILL / "sprite_gen/frames/extract.py") == "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
    sys.path.insert(0, str(SKILL))
    from sprite_gen.frames import extract as native
    from sprite_gen.curate.curation import write_curation_atomic

    RUN.mkdir()
    logs = RUN / "project-step-logs"
    logs.mkdir()
    shutil.copy2(Path(__file__), logs / Path(__file__).name)
    for name in ("raw", "references", "prompts"):
        shutil.copytree(OLD / name, RUN / name)
    shutil.copy2(OLD / "base-source.png", RUN / "base-source.png")
    request = json.loads((OLD / "sprite-request.json").read_text(encoding="utf-8"))
    request["character"]["id"] = "fairytale-hero-walk-source-cell-registration-v007"
    request["project_registration"] = {
        "basis": "native1254 source cell X center627 -> output256; same global416/1043 scale; bottom placement retained",
        "actual_body_or_foot_root": None,
        "per_frame_resize": False, "reorder": False, "retime": False,
    }
    assert request["states"]["walk"]["durations_ms"] == [83] * 6
    (RUN / "sprite-request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def step(label, arguments):
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", *arguments], cwd=ROOT,
                                capture_output=True, text=True, encoding="utf-8")
        (logs / f"{label}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(label, result.returncode)
        if result.returncode:
            print(result.stdout, result.stderr)
            raise SystemExit(result.returncode)

    step("extract", [str(ROOT / "tools/scripts/extract-sprite-shared-row-scale.py"), "--run-dir", str(RUN)])
    manifest = json.loads((RUN / "frames/frames-manifest.json").read_text(encoding="utf-8"))
    assert manifest["ok"] and not manifest["errors"] and not manifest["warnings"]
    fit = manifest["rows"][0]["shared_row_fit"]
    ratio = fit["scale"]
    assert ratio == 416 / 1043
    records, transforms = [], {}
    for index, entry in enumerate(request["project_packing"]["frames"]):
        raw = Path(entry["source"])
        assert sha(raw) == entry["source_sha256"]
        keyed = native.remove_chroma_background(Image.open(raw), (0, 255, 0), 96., 180., 18.,
                                                unmix_reach=4, spill_max_fraction=.005)
        component = native.extract_component_images(keyed, 1)[0]
        assert hashlib.sha256(component.tobytes()).hexdigest() == fit["raw_component_RGBA_sha256"][index]
        bbox = keyed.getbbox()
        assert [bbox[2] - bbox[0], bbox[3] - bbox[1]] == fit["frame_records"][index]["source_component_size"]
        left = round(256 + (bbox[0] - 627) * ratio)
        dx = left - fit["frame_records"][index]["placement_xy"][0]
        transforms[str(index)] = {"dx": dx, "dy": 0, "scale": 1., "rotate": 0, "flipX": 0}
        records.append({"frame": index, "native_request": entry["native_request"],
                        "native_cell": [1254, 1254], "native_alpha_bbox": list(bbox),
                        "shared_scale": ratio, "baseline_xy": fit["frame_records"][index]["placement_xy"],
                        "source_cell_left": left, "translation_dx": dx, "translation_dy": 0})

    # No plain twins exist in a nonpixel extraction. Leave the variant selector
    # absent: canonical frames remain the exact nonpixel output. Setting false
    # selects nonexistent *.plain.png in this installed composer (v006 failed).
    write_curation_atomic(RUN, {"version": 1, "kind": "sprite-gen-curation", "states": {
        "walk": {"selected": list(range(6)), "order": list(range(6)), "transforms": transforms}}})
    for label, script in (("compose", "compose_sprite_atlas.py"), ("curated", "export_curated_pngs.py"),
                          ("preview", "preview_animation.py"), ("gif", "compose_sprite_gif.py")):
        args = [str(SKILL / "scripts" / script), "--run-dir", str(RUN)]
        if label == "gif":
            args += ["--state", "walk"]
        step(label, args)

    for index, record in enumerate(records):
        source = Image.open(RUN / f"frames/walk/frame-{index}.png").convert("RGBA")
        target = Image.open(RUN / f"curated/frame-{index}.png").convert("RGBA")
        a, b = source.getbbox(), target.getbbox()
        assert source.crop(a).tobytes() == target.crop(b).tobytes()
        assert [b[j] - a[j] for j in range(4)] == [record["translation_dx"], 0, record["translation_dx"], 0]
        assert b[0] >= 48 and b[1] >= 48 and b[2] <= 464 and b[3] <= 464
        record.update(curated_alpha_bbox=list(b), cropped_RGBA_bytes_unchanged=True)
    runtime = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
    assert runtime["animation"]["rows"]["walk"]["durations_ms"] == [83] * 6
    assert len(runtime["frame_layout"]["rows"]["walk"]) == 6
    receipt = {"schema": "native-cell-x-registration-v1", "old_run": str(OLD), "new_run": str(RUN),
               "method": "Installed shared component extraction + pipeline curation integerX translations only",
               "durations_ms": [83] * 6, "native_generation_calls_added": 0,
               "runtime_imported": False, "motion_accepted": False,
               "actual_body_or_foot_root_measured": False, "records": records}
    (RUN / "source-cell-registration-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
