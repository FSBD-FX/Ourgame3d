"""Run the installed sprite-gen component pipeline with one scale for an entire row.

Chroma removal, connected-component separation, staging, QA and publication remain
owned by the SHA-pinned installed extractor. Only its nonpixel cell-fitting hook
is replaced. No installed skill, old run, artwork shape or timing is edited.
Use the sprite-gen venv, never the project/general Python.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

from PIL import Image

SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")
EXTRACT = SKILL / "sprite_gen/frames/extract.py"
EXTRACT_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fit_components_shared(images, width, height, margin_x, margin_y, native_cell_origins=None):
    """Preserve native inter-pose proportions; never normalize poses separately."""
    require(images and width > 2 * margin_x and height > 2 * margin_y, "Invalid row/canvas")
    crops = []
    for image in images:
        require(image.mode == "RGBA", "Expected native keyed RGBA component")
        bbox = image.getbbox()
        require(bbox is not None, "Empty component cannot become a static fallback")
        crops.append(image.crop(bbox))
    max_width, max_height = max(p.width for p in crops), max(p.height for p in crops)
    ratio = min((width - 2 * margin_x) / max_width,
                (height - 2 * margin_y) / max_height, 1.)
    require(native_cell_origins is None or len(native_cell_origins) == len(crops),
            "Every native-cell registration must match one actual component")
    frames, records = [], []
    for index, sprite in enumerate(crops):
        source_size = list(sprite.size)
        fitted_size = [max(1, round(sprite.width * ratio)), max(1, round(sprite.height * ratio))]
        if ratio != 1.:
            sprite = sprite.resize(tuple(fitted_size), Image.Resampling.LANCZOS)
        bbox = sprite.getbbox()
        require(bbox is not None, "Empty resampled component")
        sprite = sprite.crop(bbox)
        left, top = (width - sprite.width) // 2, height - margin_y - sprite.height
        if native_cell_origins is not None:
            source_x, source_cell_width = native_cell_origins[index]
            left = round(width / 2. + (source_x - source_cell_width / 2.) * ratio)
        require(left >= margin_x and top >= margin_y and left + sprite.width <= width - margin_x,
                "Shared fit exceeds safe area")
        target = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        target.alpha_composite(sprite, (left, top))
        frames.append(target)
        records.append({"frame": index, "source_component_size": source_size,
                        "shared_scale": ratio, "resampled_size": fitted_size,
                        "placement_xy": [left, top], "alpha_bbox_px": list(target.getbbox())})
    return frames, {"policy": "one_raw_component_max_extent_scale_for_entire_row",
                    "scale": ratio, "source_max_extent": [max_width, max_height],
                    "horizontal_registration": "native_source_cell" if native_cell_origins is not None else "bbox_center",
                    "per_frame_scale_normalization": False, "frame_records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    root = Path("F:/Ourgame/source-assets/production").resolve()
    require(run.is_relative_to(root), "Only an explicit project production run is supported")
    frames_dir = run / "frames"
    require(not frames_dir.exists() or (frames_dir.is_dir()
            and not any(p.is_file() for p in frames_dir.rglob("*"))),
            "Preserve prior extraction; choose a new run version")
    request_path = run / "sprite-request.json"
    request = json.loads(request_path.read_text(encoding="utf-8-sig"))
    fit = request["fit"]
    require(fit.get("shared_row_scale") is True and fit.get("pixel_unfake") is False,
            "Explicit nonpixel shared-row-scale contract required")
    require(fit.get("resample") == "lanczos" and fit.get("align_x") == "bbox-center"
            and fit.get("align_y") == "bottom", "Unsupported explicit fitting contract")
    require(hashlib.sha256(EXTRACT.read_bytes()).hexdigest() == EXTRACT_SHA,
            "Installed extractor changed; review its API before using this hook")
    sys.path.insert(0, str(SKILL))
    import sprite_gen.frames.extract as native
    evidence = []
    original_hook, original_argv = native.extract_component_frames, sys.argv

    def shared_hook(strip, count, width, height, margin_x, margin_y, native_fit=None):
        images = native.extract_component_images(strip, count)
        if images is None:
            return None  # Native dispatcher rejects; slot fallback is never enabled.
        origins, source_records = None, []
        if request.get("project_horizontal_registration") == "native_source_cell_x":
            source_frames = request["project_packing"]["frames"]
            require(len(source_frames) == count, "Native source-cell evidence count mismatch")
            origins = []
            for index, source_frame in enumerate(source_frames):
                source = Path(source_frame["source"])
                require(hashlib.sha256(source.read_bytes()).hexdigest() == source_frame["source_sha256"],
                        "Original native source changed")
                raw = Image.open(source)
                keyed = native.remove_chroma_background(raw, (0, 255, 0), 96., 180., 18.,
                    unmix_reach=4, spill_max_fraction=.005)
                component = native.extract_component_images(keyed, 1)[0]
                require(component.tobytes() == images[index].tobytes(),
                        "Source cell must match the actual row component, never a slot fallback")
                source_bbox = keyed.getbbox()
                require(list(raw.size) == source_frame["source_pixel_size"]
                        and [source_bbox[2]-source_bbox[0],source_bbox[3]-source_bbox[1]]
                        == list(component.crop(component.getbbox()).size), "Unexpected source-cell geometry")
                origins.append((source_bbox[0], raw.width))
                source_records.append({"frame":index,"native_source_bbox":list(source_bbox),
                    "native_cell_size":list(raw.size),"row_component_matches_native_cell":True})
        frames, record = fit_components_shared(images, width, height, margin_x, margin_y, origins)
        if source_records:
            record["native_source_cell_records"] = source_records
        require(len(frames) == count, "Native component count changed")
        record["raw_component_RGBA_sha256"] = [hashlib.sha256(p.tobytes()).hexdigest() for p in images]
        evidence.append(record)
        return frames

    try:
        native.extract_component_frames = shared_hook
        sys.argv = [str(EXTRACT), "--run-dir", str(run)]
        code = native.main()
    finally:
        native.extract_component_frames, sys.argv = original_hook, original_argv
    require(code in (None, 0), "Native extractor rejected this run")
    path = run / "frames/frames-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    require(manifest["ok"] is True and manifest["errors"] == manifest["warnings"] == [],
            "Native QA must pass unchanged; no edge/chroma tolerance relaxation")
    require(len(evidence) == len(manifest["rows"]) == len(request["states"]), "Missing native row provenance")
    for row, record in zip(manifest["rows"], evidence):
        require(row["method"] == "components" and row["frames"] == len(record["frame_records"]),
                "Shared fit is only valid after native component extraction")
        row["shared_row_fit"] = record
    manifest["project_fit_extension"] = {"path": str(Path(__file__).resolve()),
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "native_extractor_sha256": EXTRACT_SHA, "artwork_redrawn": False,
        "installed_skill_modified": False, "source_frame_timing_modified": False}
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"shared_row_scale_verified": True, "rows": evidence,
                      "scope": "Deterministic geometric registration only; motion acceptance still requires actual review."}))


if __name__ == "__main__":
    main()
