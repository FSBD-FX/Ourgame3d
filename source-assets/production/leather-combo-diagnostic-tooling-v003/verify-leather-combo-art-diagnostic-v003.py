"""Root-only execution after admission; source preflight or full technical combo verification."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("combo_postprocess", here / "postprocess-leather-combo-art-diagnostic-v003.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic-inputs", required=True)
    parser.add_argument("--archive")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    snapshot = (tool.ROOT / args.diagnostic_inputs).resolve()
    tool.require(snapshot.is_relative_to(tool.ROOT / "source-assets/production/leather-combo-diagnostic-root-input-v002"), "Snapshot outside project backups")
    manifest_path = snapshot
    if args.source_only:
        tool.require(not args.write_receipt, "Source-only preflight cannot create a runtime receipt")
        index = {"source_manifest_SHA256": tool.desc(manifest_path)["sha256"], "snapshot": snapshot.as_posix()}
        _, _, audit = tool.verify_sources(snapshot, index)
        print(json.dumps({"source_preflight_only": True, "actual_native_verified": False, "production_packages": audit["production_packages"], "current_full_automation_succeeded": audit["current_full_automation_succeeded"], "source_mismatches": 0}, indent=2))
        return
    tool.require(args.archive, "Full technical verification requires actual archive")
    archive = (tool.ROOT / args.archive).resolve()
    tool.require(archive.is_relative_to(tool.ROOT / "过程图稿与视频"), "Archive outside retained project originals")
    original = archive / "原件"
    report, index = tool.read(original / "runtime-report.json"), tool.read(archive / "index.json")
    _, packages, audit = tool.verify_sources(snapshot, index)
    selected, flow = tool.verify_flow(report, index, packages)
    movies, receipts, pins, offsets, duration = tool.verify_pixels(original, report)
    result = {"scope": "NONRELEASE_ART_DIAGNOSTIC; native combo flow/pixels only; current fullGREEN false", "current_full_GREEN": False, "current_automation_succeeded": None, "actual_native_technical_verified": True,
        "selected_phase_facing_pairs": len(selected), "movie_frames": len(movies), "original_PNGs": len(pins), "duration_s": duration,
        "production_packages": audit["production_packages"], "current_full_automation_succeeded": audit["current_full_automation_succeeded"],
        "actual_attack_ids_left_right_by_stage": flow["actual_combo_attack_ids_left_right_by_stage"], "actual_ready_left_right": flow["actual_fresh_ready_left_right"],
        "pixel_FIFO_async_stop_flush_verified": True, "art_review_pending": True, "full_motion_accepted": False, "formal_complete_units": 0}
    if args.write_receipt:
        tool.new(original / "independent-leather-combo-preprocess-verification-v001.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
