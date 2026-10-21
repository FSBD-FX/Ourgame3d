"""Root-only deferred standard layout raster preparation; no AI or UE calls.

This file is a candidate. Default mode only verifies inputs. --write-guides writes
new F candidate media; Root must E-retain originals/presentation/index BEFORE View.
It never calls prepare_sprite_run (which would synthesize a new idle anchor).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-guides", action="store_true")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    refs = json.loads((HERE / "reference-pins-v001.json").read_text(encoding="utf-8"))
    for record in refs["files"]:
        actual = pin(Path(record["file"]["path"]))
        if actual != record["file"]:
            raise ValueError("Pinned input changed: " + actual["path"])
    if Path(sys.executable).resolve() != (SKILL / ".venv/Scripts/python.exe").resolve():
        raise ValueError("Use the pinned sprite-gen venv interpreter, never global Python")
    sys.path.insert(0, str(SKILL))
    from sprite_gen.gen.prepare import draw_guide, row_prompt, normalize_states
    request = json.loads((HERE / "sprite-request.json").read_text(encoding="utf-8"))
    if normalize_states(request["states"]) != request["states"]:
        raise ValueError("Standard prepare would change state keys or timing")
    for state, entry in request["states"].items():
        expected = row_prompt(request, state, entry).rstrip() + "\n"
        if (HERE / "prompts" / (state + ".txt")).read_text(encoding="utf-8") != expected:
            raise ValueError("Prompt differs from current numeric SSoT: " + state)
    if not args.write_guides:
        print(json.dumps({"text_inputs_verified": True, "guide_rasters_written": False,
                          "image_generation_called": False, "UE_called": False}))
        return
    if args.out_dir is None:
        raise ValueError("Root must choose a NEW explicit F candidate batch path")
    out = args.out_dir.resolve()
    allowed = (HERE / "process-batches").resolve()
    if not out.is_relative_to(allowed) or out == allowed or out.exists():
        raise ValueError("Choose a NEW child of this candidate/process-batches; never overwrite")
    out.mkdir(parents=True)
    shutil.copyfile(HERE / "sprite-request.json", out / "sprite-request.json")
    for name in ("runtime-timing-annotations-v001.json", "reference-pins-v001.json", "handoff-v001.json"):
        shutil.copyfile(HERE / name, out / name)
    for state, entry in request["states"].items():
        guide = out / "references/layout-guides" / (state + ".png")
        guide.parent.mkdir(parents=True, exist_ok=True)
        draw_guide(guide, state, entry["frames"], request["cell"], motion_phase_guides=False)
        prompt = out / "prompts" / (state + ".txt")
        prompt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / "prompts" / (state + ".txt"), prompt)
        (out / "raw").mkdir(parents=True, exist_ok=True)
        (out / "frames" / state).mkdir(parents=True, exist_ok=True)
    files = [pin(path) for path in sorted(out.rglob("*")) if path.is_file()]
    receipt = {"schema": "hero-state-standard-layout-batch-v001", "files": files,
               "identity_anchor": refs["identity_anchor"], "new_identity_generated": False,
               "layout_only": True, "AI_called": False, "UE_called": False,
               "viewed": False, "E_retention_pending": True, "art_accepted": False}
    (out / "batch-index-v001.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"batch": out.as_posix(), "files": len(files), "E_retention_pending": True,
                      "next": "Root E-retain before any View or attaching refs to generation"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
