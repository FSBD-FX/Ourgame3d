def write_whole_phase_view(path, maps):
    entries = []
    for item in maps:
        entry = dict(item)
        entry["whole_url"] = quote(os.path.relpath(item["source_whole"]["path"], path.parent).replace("\\", "/"), safe="/")
        entry["crop_url"] = quote(os.path.relpath(item["unscaled_crop"]["path"], path.parent).replace("\\", "/"), safe="/")
        entries.append(entry)
    payload = json.dumps(entries, ensure_ascii=False).replace("<", "\\u003c")
    new(path, '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>实际软皮 P1 原生阶段视图</title>
<style>body{font:15px system-ui;margin:20px;background:#16191c;color:#eee}button{margin:3px;padding:7px}img{display:block;max-width:none}pre{white-space:pre-wrap}section{overflow:auto;border:1px solid #555;margin-top:12px}p{max-width:1000px}</style>
<h1>实际软皮 P1：左右各六阶段</h1><p>仅选择原生 PNG，完整画面1280×720，裁图240×160均无缩放重采样。技术验证不代表美术接受；全动作、音频、完整装备和完整敌人/单位未接受。</p>
<nav id="buttons"></nav><pre id="label"></pre><a id="source">打开原始 PNG</a><section><img id="whole" width="1280" height="720" alt="原生完整画面"></section><h2>原生尺寸局部</h2><img id="crop" width="240" height="160" alt="无缩放裁图">
<script>const entries=''' + payload + ''';const byId=id=>document.getElementById(id);function select(i){const e=entries[i];byId('whole').src=e.whole_url;byId('crop').src=e.crop_url;byId('source').href=e.whole_url;byId('label').textContent=JSON.stringify({facing:e.facing,frame:e.frame,actual_attack_id:e.actual_attack_id,wall_offset_s:e.wall_offset_s,writer_sequence:e.writer_sequence,native_BGRA8_crc32:e.native_BGRA8_crc32,source_sha256:e.source_whole.sha256,crop_sha256:e.unscaled_crop.sha256,actually_viewed:false},null,2);}entries.forEach((e,i)=>{const b=document.createElement('button');b.textContent=(e.facing<0?'左':'右')+' / '+e.frame;b.onclick=()=>select(i);byId('buttons').appendChild(b)});select(0);</script></html>\n''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--expected-automation-count", type=int, default=157)
    args = parser.parse_args()
    archive, snapshot = (ROOT / args.archive).resolve(), (ROOT / args.snapshot).resolve()
    require(archive.is_relative_to(ROOT / "过程图稿与视频") and snapshot.is_relative_to(ROOT / "source-assets/production/backups"), "Archive/snapshot outside authorized project roots")
    original, presentation = archive / "原件", archive / "展示副本"
    require(original.is_dir() and presentation.is_dir(), "Actual capture archive is missing")
    require(not (original / "independent-leather-primary1-verification-v001.json").exists(), "Never overwrite prior postprocess; retain a new version")
    report, index = read(original / "runtime-report.json"), read(archive / "index.json")
    capture_input_pins = [desc(path) for path in [archive / "index.json"] + [original / name for name in
        ("runtime-report.json", "native-lossless-capture.json", "native-frame-pixels.jsonl", "native-async-write-summary.json", "native-pixel-verification.json")]]
    manifest, package_rows, source_audit = verify_sources(snapshot, index, args.expected_automation_count)
    selection, flow_audit = verify_flow(report, index, package_rows)
    movies, pixel_rows, fingerprints, offsets, duration = verify_pixels(original, report)
    # No derived output exists before the complete technical validation above.
    # PNGs, Source/DLL/packages and imported original RGBA are never rewritten.
    maps = []
    for facing in (-1, 1):
        for frame in range(6):
            i = selection[(facing, frame)]
            row = report["observations"][i]
            scale = row["canvas_size"] / 512.0
            root_x = row["grip_screen"][0] - facing * (row["grip"][0] - row["root"][0]) * scale
            root_y = row["grip_screen"][1] - (row["grip"][1] - row["root"][1]) * scale
            left = max(0, min(1040, math.floor(root_x) - 110))
            top = max(0, min(560, math.floor(root_y) - 130))
            destination = presentation / f"leather-primary1-{'left' if facing < 0 else 'right'}-phase-{frame}-{movies[i].name}"
            require(not destination.exists(), "Never overwrite presentation crop")
            with Image.open(movies[i]) as image:
                crop = image.crop((left, top, left + 240, top + 160))
                expected_mode, expected_bytes = crop.mode, crop.tobytes()
                crop.save(destination)
            with Image.open(destination) as crop:
                require(crop.size == (240, 160) and crop.mode == expected_mode and crop.tobytes() == expected_bytes, "Unscaled crop pixel round-trip differs")
            maps.append({"observation_index": i, "writer_sequence": pixel_rows[i]["writer_sequence"], "native_BGRA8_crc32": pixel_rows[i]["native_BGRA8_crc32"],
                "wall_offset_s": offsets[i], "flow_phase": row["flow_phase"], "flow_step": row["flow_step"], "clip": row["clip"], "stage": row["stage"], "frame": frame, "facing": facing,
                "actual_attack_id": row["action_id"], "actual_light_instance_id": row["committed_armor_id"], "draw_stack": row["draw_stack"], "source_whole": desc(movies[i]),
                "unscaled_crop": desc(destination), "crop_rect_xywh_px": [left, top, 240, 160], "crop_resampled": False, "actually_viewed": False})
    whole_view = presentation / "leather-primary1-whole-phase-view-v001.html"
    write_whole_phase_view(whole_view, maps)
    concat = original / "leather-primary1-wall-timed-frames-v001.txt"
    lines = []
    for i, path in enumerate(movies):
        left = 0.0 if i == 0 else offsets[i]
        right = offsets[i + 1] if i + 1 < len(movies) else duration
        require(right > left and "'" not in path.as_posix(), "Invalid concat interval/path")
        lines.extend(["file '" + path.as_posix() + "'", f"duration {right - left:.12f}"])
    lines.append("file '" + movies[-1].as_posix() + "'")
    new(concat, "\n".join(lines) + "\n")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video = presentation / "leather-primary1-trial-silent.mp4"
    require(not video.exists(), "Never overwrite review video")
    encode = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", str(concat),
              "-vf", "fps=30", "-t", f"{duration:.12f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(video)]
    encoded = subprocess.run(encode, capture_output=True, text=True)
    new(original / "leather-primary1-video-encode.log", encoded.stdout + encoded.stderr)
    require(encoded.returncode == 0 and video.is_file() and video.stat().st_size > 0, "Review video encode failed; preserve failed outputs")
    decode = [ffmpeg, "-hide_banner", "-v", "error", "-i", str(video), "-map", "0:v:0", "-an", "-progress", "pipe:1", "-nostats", "-f", "null", os.devnull]
    decoded = subprocess.run(decode, capture_output=True, text=True)
    new(original / "leather-primary1-video-full-decode.log", decoded.stdout + decoded.stderr)
    progress = {}
    for line in decoded.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1); progress[key] = value.strip()
    require(decoded.returncode == 0 and not decoded.stderr.strip() and int(progress.get("frame", "0")) > 0 and progress.get("progress") == "end", "Full review-video decode failed")
    for item in fingerprints + capture_input_pins: same_pin(Path(item["path"]), item)
    _, _, final_source_audit = verify_sources(snapshot, index, args.expected_automation_count)
    require(source_audit == final_source_audit, "Postprocess changed frozen source/DLL/package/original RGBA audit")
    source_audit["endpoint_checks_before_and_after_postprocess"] = 2 * source_audit["source_endpoint_checks"]
    flow_audit.update({"original_PNGs": len(fingerprints), "movie_frames": len(movies), "duration_s": duration,
        "every_movie_observation_FIFO_CRC_bound": True, "native_async_stop_flush_verified": True, "art_review_pending": True})
    new(original / "leather-primary1-source-binding-verification-v001.json", source_audit)
    new(original / "independent-leather-primary1-verification-v001.json", flow_audit)
    new(original / "leather-primary1-selected-source-map-v001.json", {"frames": maps, "whole_phase_view": desc(whole_view), "selection_is_not_art_review": True})
    new(original / "leather-primary1-pixel-FIFO-binding-v001.json", {"movies": [{"file": movies[i].name, "observation_index": i,
        "writer_sequence": row["writer_sequence"], "native_BGRA8_crc32": row["native_BGRA8_crc32"], "wall_offset_s": offsets[i]} for i, row in enumerate(pixel_rows)],
        "whole_PNG_fingerprints_before_and_after_equal": fingerprints, "capture_metadata_pins_before_and_after_equal": capture_input_pins,
        "source_pixels_mutated": False, "event_clock_note": "Use ScreenshotProcessed event offsets, never asynchronous save completion for playback timing."})
    new(original / "leather-primary1-video-receipt-v001.json", {"video": desc(video), "encode_argv": encode, "encode_exit": encoded.returncode,
        "full_decode_argv": decode, "full_decode_exit": decoded.returncode, "decoded_frame_count": int(progress["frame"]), "audio_recorded": False,
        "presentation_policy": "Actual processed-event wall offsets; first frame held from zero, final held to duration; final concat sentinel; CFR30 quantization/duration cap; original clocks/PNGs/positions unchanged.",
        "motion_or_audio_accepted": False})
    provenance = original / "leather-primary1-postprocess-provenance-v001"
    require(not provenance.exists(), "Never overwrite postprocess provenance")
    provenance.mkdir()
    (provenance / "compiled-source-manifest.json").write_bytes((snapshot / "compiled-source-manifest.json").read_bytes())
    (provenance / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    new(archive / "source-version-status-index.json", {"status": "actual_leather_P1_6_both_facings_technical_verified_visual_review_pending", "snapshot": snapshot.as_posix(),
        "runtime_report": desc(original / "runtime-report.json"), "independent_verification": desc(original / "independent-leather-primary1-verification-v001.json"),
        "source_binding": desc(original / "leather-primary1-source-binding-verification-v001.json"), "selected_unscaled_crops": 12, "whole_phase_view": desc(whole_view), "video": desc(video),
        "default_full_bound_flow_claimed": False, "complete_equipment_or_full_motion_accepted": False, "formal_complete_units": 0})
    new(archive / "README.md", "真实软皮轻甲P1-only试装：正常Enter/E/A取消/E提交一次；正常J第一刀，等待实际End+.46和真实Ready，A/D转向，正常J第二个全新Stage0攻击，最后至少3帧真实Ready。左右各6阶段按actualAttackID逐帧绑定新3甲层/旧4body层/独立军剑8层；12张无缩放原生裁图、完整阶段视图和墙钟CFR30静音视频供Root留档后实看。技术通过不等于美术接受，未接受P2/3、完整装备/走跑/受击/死亡、正式来源、存档、音频或完整单位。\n")
    print(json.dumps({"observations": len(report["observations"]), "original_PNGs": len(fingerprints), "snapshot_files": source_audit["snapshot_files"],
        "production_packages": source_audit["production_packages"], "current_full_automation_succeeded": source_audit["current_full_automation_succeeded"],
        "source_mismatches": 0, "operations_committed": 1, "actual_primary1_masks_left_right": [63, 63], "selected_unscaled_crops": len(maps),
        "whole_phase_view": desc(whole_view), "video": desc(video), "art_review_pending": True, "formal_complete_units": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
