"""Read-only native Move7 inputs; NEW F review media. No engine, E writes or View."""
from pathlib import Path
import argparse, hashlib, json, math, runpy, shutil, struct, subprocess, sys
from PIL import Image, ImageDraw

ROOT = Path('F:/Ourgame').resolve()
C = Path(__file__).resolve().parent.parent
PROOF_NAME = 'Move7-independent-native-verification-v001.json'
JOINS = ['Move7_to_native_Windup', 'native_Recovery_to_Ready_stop']

def need(value, reason):
    if not value:
        raise ValueError(reason)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pin(path):
    path = Path(path).resolve()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return dict(path=path.as_posix(), bytes=path.stat().st_size, sha256=h.hexdigest())

def checked(row, base=ROOT):
    need(set(row) == {'path', 'bytes', 'sha256'}, 'Exact three-field pin required')
    path = Path(row['path'])
    path = (path if path.is_absolute() else base / path).resolve()
    actual = pin(path)
    need((actual['bytes'], actual['sha256']) == (row['bytes'], row['sha256']), 'Pinned input changed: ' + str(path))
    return path

def dump_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def copy_verified(source, target):
    source, target = Path(source), Path(target)
    need(not target.exists(), 'Never overwrite a retained file')
    before = pin(source)
    shutil.copy2(source, target)
    after = pin(target)
    need((before['bytes'], before['sha256']) == (after['bytes'], after['sha256']), 'Copy size/SHA differs')
    return dict(source=before, copy=after)

def dependencies():
    for row in read(C / 'Move7-native-media-freeze-v001.json')['files']:
        checked(row, C)
    contract = read(C / 'media-input-contract-v001.json')
    for key in ['official_checker', 'old_tool_contract_fix_checker', 'tool_contract_fix_freeze', 'proof_geometry_repair_freeze', 'original_observer_freeze', 'VFR_reference_helper', 'VFR_reference_freeze']:
        checked(contract[key])
    for name in ['tool_contract_fix_freeze', 'proof_geometry_repair_freeze', 'original_observer_freeze']:
        p = checked(contract[name])
        for row in read(p)['files']:
            checked(row, p.parent)
    return contract

def actual_inputs(archive, contract, retention=None):
    original = archive / '原件'
    report_path, proof_path = original / 'runtime-report.json', original / PROOF_NAME
    report, proof, session = read(report_path), read(proof_path), read(archive / 'index.json')
    need(report['schema'] == 'guard-Move7-native-observer-v001' and report['scenario'] == 'NormalWASDLeadActualGuardMove128CombatReady' and report['passed'] is True and report['flow_complete'] is True, 'Terminal original native Move7 PASS required')
    need(proof['schema'] == 'guard-Move7-independent-native-v001' and proof['passed'] is True and proof['native_report_pin'] == pin(report_path), 'Exact retained independent native PASS required')
    need(session['schema'] == 'guard-Move7-native-session-v001' and session['exit_code'] == 0 and session['native_reported_passed'] is True and session['independent_passed'] is True and session['process_id'] == int(report['process_id']) == proof['process_id'], 'Actual session/PID/exit/native/independent PASS required')
    side = report['requested_approach_side']
    need(side in [-1, 1] and type(side) is int and side == report['actual_approach_side'] == proof['actual_facing'] == session['requested_approach_side'], 'Actual side differs')
    need(session['candidate_freeze_sha256'] == contract['original_observer_freeze']['sha256'] and session['tool_contract_fix_freeze_sha256'] == contract['tool_contract_fix_freeze']['sha256'] and session['tool_contract_fix_checker_sha256'] == contract['old_tool_contract_fix_checker']['sha256'], 'Session is not the pinned original derivative tool milestone')
    need(proof['tool_contract_fix_freeze_pin'] == contract['tool_contract_fix_freeze'] and proof['tool_contract_fix_checker_pin'] == contract['old_tool_contract_fix_checker'], 'Independent original derivative binding differs')
    need(session['proof_geometry_repair_freeze_sha256'] == contract['proof_geometry_repair_freeze']['sha256'] and session['proof_geometry_repair_checker_sha256'] == contract['official_checker']['sha256'] and proof['proof_geometry_repair_freeze_pin'] == contract['proof_geometry_repair_freeze'] and proof['proof_geometry_repair_checker_pin'] == contract['official_checker'], 'Supplemental proof geometry repair lineage differs')
    snapshot, prereg = Path(session['snapshot']).resolve(), Path(session['root_prereg']).resolve()
    manifest = snapshot / 'compiled-source-manifest.json'
    need(pin(manifest)['sha256'] == session['snapshot_manifest_sha256'] and pin(prereg)['sha256'] == session['root_prereg_sha256'], 'Actual snapshot/prereg changed')
    p = read(prereg)
    need(p['compiled_manifest_pin'] == pin(manifest) and p['approach_side'] == side, 'Actual prereg belongs to another snapshot/side')
    checker = checked(contract['official_checker'])
    rerun = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(checker), '--snapshot', str(snapshot), '--root-prereg', str(prereg), '--archive', str(archive)], capture_output=True, text=True, encoding='utf-8')
    need(rerun.returncode == 0, 'Readonly official checker rejected inputs: ' + rerun.stderr)
    need(json.loads(rerun.stdout) == proof, 'Exact readonly official rerun differs from retained independent receipt')
    need(proof['complete7GPU_and_submitted_floatquads'] and proof['original_clock_and_source_projection'] and proof['native_PNG_CRC_FIFO_verified'] and proof['accepted_cycle_distance'] >= 128 and proof['six_distance_window_mask'] == report['distance_window_mask'] == 63, 'Real seven resources/128 distance/six windows/CRC gates absent')
    need(report['silent_video'] and not report['audio_recorded'] and not report['visual_reviewed'] and not proof['audio_recorded'] and not proof['visual_reviewed'] and not proof['FinalAccepted'] and not proof['footlock'] and report['formal_complete_units'] == 0, 'Only silent bounded unaccepted Move trial is allowed')
    optics = proof['optical_source_projection']
    need(optics['passed'] and not optics['registration_search_used'] and not optics['actual_pixels_modified'], 'Fixed source projection PASS required')
    rows = [json.loads(line) for line in (original / 'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line]
    movie = [row for row in rows if row['file'].startswith('MovieFrame')]
    frames = [original / row['file'] for row in movie]
    need(frames and len({f.name for f in frames}) == len(frames) and [f.name for f in frames] == sorted(f.name for f in frames) and {f.name for f in frames} == {f.name for f in original.glob('MovieFrame*.png')}, 'Original movie frame membership/order differs')
    observations = report['observations']
    timing = report['capture_timing']
    offsets = timing['frame_wall_offsets_s']
    duration = timing['capture_stop_monotonic_s'] - timing['capture_start_monotonic_s']
    need(len(frames) == len(observations) == len(offsets) and all(math.isfinite(t) for t in offsets) and all(b > a for a, b in zip(offsets, offsets[1:])) and duration > offsets[-1] >= offsets[0] >= 0 and not timing['use_fixed_time_step'] and all(o['wall_offset_s'] == t for o, t in zip(observations, offsets)), 'One original callback/PNG and real monotonic wall timeline required')
    witnesses = optics['source_registered_native_witnesses']
    need(len(witnesses) == 6 and {w['distance_window'] for w in witnesses} == set(range(6)), 'Six distance windows are not six raster frames')
    samples = []
    for window in range(6):
        ws = [w for w in witnesses if w['distance_window'] == window]
        need(len(ws) == 1, 'Duplicate/missing distance window witness')
        w = ws[0]
        i = w['observation']
        need(type(i) is int and 0 <= i < len(frames) and frames[i].name == w['original_PNG'], 'Witness original callback PNG differs')
        o, d = observations[i], observations[i]['rig_draw']
        need(o['visual_kind'] == 'Move7' and o['move_query_ok'] and d['drawn'] and d['draw_id'] == w['DrawId'] and o['move_query']['movement_event'] == w['MovementEventId'] and d['accepted_distance'] == w['accepted_distance'] and int(d['cycle_position'] / (128 / 6)) == window and len(d['submitted_parts']) == 7 and all(q['submitted'] for q in d['submitted_parts']), 'Witness cannot be replaced by a different draw/distance/quad')
        samples.append(dict(distance_window=window, observation=i, independent_optical_witness=w))
    joins = report['actual_adjacent_joins']
    need(joins == proof['actual_adjacent_joins'] and [j['kind'] for j in joins] == JOINS, 'Exact two original adjacent joins required')
    for j in joins:
        i, k = j['from_observation'], j['to_observation']
        need(type(i) is type(k) is int and 0 <= i < k < len(frames) and k == i + 1, 'A join must be strictly adjacent original callbacks')
        before, after = observations[i], observations[k]
        if j['kind'] == JOINS[0]:
            need(before['visual_kind'] == 'Move7' and before['rig_draw']['drawn'] and after['visual_kind'] in ['AxeWindup', 'StompWindup'] and after['full_draw']['frame'] == 0 and after['full_draw']['attack'] == report['battle_attack'], 'Actual Move7 to first natural Windup0 differs')
        else:
            need(before['visual_kind'] in ['AxeRecovery', 'StompRecovery'] and before['full_draw']['frame'] == 3 and before['full_draw']['attack'] == after['full_draw']['attack'] == report['battle_attack'] and after['visual_kind'] == 'Ready' and after['full_draw']['drawn'] and not after['move_query_ok'], 'Actual same-Aid Recovery3 to stationary Ready differs')
    retention_binding = dict(provided=False, status='ROOT_E_NATIVE_ARCHIVE_RETENTION_PENDING', full_native_PNGs_remain_in_F_archive=True)
    if retention:
        record = read(retention)
        need(record['schema'] == 'native-media-exact-original-zip-retention-v001' and Path(record['source_archive']).resolve() == archive and record['verification_passes'] == 2 and record['source_and_member_hash_mismatches'] == 0 and record['status'] == 'EXACT_ORIGINALS_AND_PRESENTATION_RETAINED_BEFORE_REVIEW' and not record['source_deleted'] and not record['reencoded_originals'], 'Root retention record must bind this exact native archive and two zero-mismatch passes')
        members = {x['member']: x for x in record['files']}
        need(len(members) == record['file_count'], 'Root retained member manifest differs')
        for frame in frames:
            row = members['原件/' + frame.name]
            actual = pin(frame)
            need(Path(row['source']).resolve() == frame.resolve() and (row['bytes'], row['sha256']) == (actual['bytes'], actual['sha256']), 'Original movie source differs from Root retained member record')
        retention_binding = dict(provided=True, Root_retention_record=pin(retention), Root_E_packet=record['packet'], Root_record_source_and_member_verification_passes=2, Root_record_zero_mismatches=True, actual_F_movie_sources_match_Root_record=True, E_ZIP_rehashed_or_members_reread_by_media_helper=False, full_native_PNGs_remain_in_F_archive=True)
    bindings = dict(native_archive=archive.as_posix(), native_report=pin(report_path), independent=pin(proof_path), session=pin(archive / 'index.json'), official_checker=pin(checker), old_tool_contract_fix_checker=contract['old_tool_contract_fix_checker'], tool_contract_fix_freeze=contract['tool_contract_fix_freeze'], proof_geometry_repair_freeze=contract['proof_geometry_repair_freeze'], original_observer_freeze=contract['original_observer_freeze'], root_prereg=pin(prereg), compiled_manifest=pin(manifest), readonly_official_rerun_passed=True, full_source_archive_retention=retention_binding)
    return dict(archive=archive, report=report, proof=proof, frames=frames, offsets=offsets, duration=duration, samples=samples, joins=joins, bindings=bindings, prereg=prereg, manifest=manifest, retention=retention)

def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]

def ground(o):
    if o['visual_kind'] == 'Move7':
        return [f32(640 + (o['guard_ground'][0] - o['camera_ground'][0]) * f32(.65)), f32(490 - o['guard_ground'][1] * f32(.38))]
    return o['full_draw']['ground_screen']

def quad_corners(q):
    need(q['draw_scale'] == 1 and not q['scale_position'], 'Only actual native unit-scale canvas quads are supported')
    x, y = q['top']; w, h = q['size']; px, py = x + q['pivot'][0] * w, y + q['pivot'][1] * h
    angle = math.radians(q['rotation']); co, si = math.cos(angle), math.sin(angle)
    return [(px + co * (x + u * w - px) - si * (y + v * h - py), py + si * (x + u * w - px) + co * (y + v * h - py)) for u, v in [(0, 0), (0, 1), (1, 0), (1, 1)]]

def actual_crop_bounds(o):
    if o['visual_kind'] == 'Move7':
        quads = [x['quad'] for x in o['rig_draw']['submitted_parts']]
    else:
        need(o['full_draw']['drawn'] and o['full_draw']['quad_submitted'], 'Ordinary joined source was not submitted')
        quads = [o['full_draw']]
    points = [p for q in quads for p in quad_corners(q)]
    gx, gy = map(math.floor, ground(o))
    return [math.floor(min(p[0] for p in points)) - gx - 8, math.floor(min(p[1] for p in points)) - gy - 8, math.ceil(max(p[0] for p in points)) - gx + 8, math.ceil(max(p[1] for p in points)) - gy + 8]

def contact(path, items, columns, label):
    sizes = []
    for item in items:
        with Image.open(item['path']) as im:
            sizes.append(im.size)
    width = max(s[0] for s in sizes)
    height = max(s[1] for s in sizes)
    board = Image.new('RGB', (columns * width, math.ceil(len(items) / columns) * (height + 24)), (26, 29, 34))
    draw = ImageDraw.Draw(board)
    for i, item in enumerate(items):
        x, y = (i % columns) * width, (i // columns) * (height + 24)
        draw.text((x + 5, y + 5), label(item), fill='white')
        with Image.open(item['path']) as im:
            rgb = im.convert('RGB'); board.paste(rgb, (x, y + 24))
            need(board.crop((x, y + 24, x + rgb.width, y + 24 + rgb.height)).tobytes() == rgb.tobytes(), 'Contact altered source RGB pixels')
    board.save(path)

def prepare(output, data):
    raw, show = output / '原件', output / '展示副本'
    raw.mkdir(); show.mkdir()
    frames, offsets, report = data['frames'], data['offsets'], data['report']
    obs = report['observations']
    video, last, timing, decoded = runpy.run_path(str(C / 'tooling/retained-microsecond-VFR-Move7-v001.py'))['encode_vfr'](show, frames, offsets, data['duration'])
    # Originals stay in the complete independently retained native archive.
    # Every frame is pinned here; only review witnesses/joins are copied again.
    sources = [dict(observation=i, native_original=pin(f), wall_offset_s=t, decoded_video_PTS_s=int(decoded[i][2]) / 1.e6, simulation_time=o['sim'], callback_phase=o['phase'], visual_kind=o.get('visual_kind'), original_RGB_frame_copied_to_this_media=False, review_copies=[]) for i, (f, t, o) in enumerate(zip(frames, offsets, obs))]
    def copy_native(i, name):
        copied = copy_verified(frames[i], raw / name)
        with Image.open(raw / name) as im:
            need(im.format == 'PNG' and im.size == (1280, 720), 'Original viewport PNG dimensions differ')
        sources[i]['original_RGB_frame_copied_to_this_media'] = True
        sources[i]['review_copies'].append(copied['copy'])
        return dict(observation=i, **copied, wall_offset_s=offsets[i], simulation_time=obs[i]['sim'], guard_time=obs[i].get('guard_time'), visual_kind=obs[i].get('visual_kind'), actual_rig_draw=obs[i].get('rig_draw'), actual_full_draw=obs[i].get('full_draw'), resized=False, RGB_pixels_edited=False)
    samples = []
    for s in data['samples']:
        row = copy_native(s['observation'], f'Move7-distance-window-{s["distance_window"]}-UNSCALED-native-v001.png')
        row.update(distance_window=s['distance_window'], independent_optical_witness=s['independent_optical_witness'])
        samples.append(row)
    joins = []
    for edge in data['joins']:
        pair = [copy_native(edge[key], f'JOIN-{edge["kind"]}-{key}-UNSCALED-native-v001.png') for key in ['from_observation', 'to_observation']]
        joins.append(dict(**edge, pair=pair, original_adjacent_callbacks=True, intervening_native_frames=0, wall_delta_s=offsets[edge['to_observation']] - offsets[edge['from_observation']], retimed=False, interpolated=False))
    selected = samples + [x for j in joins for x in j['pair']]
    bounds = [actual_crop_bounds(obs[x['observation']]) for x in selected]
    common = [min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds)]
    def crop(item, name):
        origin = list(map(math.floor, ground(obs[item['observation']])))
        box = [origin[0] + common[0], origin[1] + common[1], origin[0] + common[2], origin[1] + common[3]]
        need(0 <= box[0] < box[2] <= 1280 and 0 <= box[1] < box[3] <= 720, 'Fixed native pixel crop would clip original viewport')
        with Image.open(item['copy']['path']) as im:
            cut = im.convert('RGB').crop(box)
        path = show / name; cut.save(path)
        with Image.open(path) as back:
            need(back.convert('RGB').tobytes() == cut.tobytes(), 'Saved crop RGB differs from original exact pixel crop')
        return dict(path=path.as_posix(), crop=pin(path), observation=item['observation'], source=item['source'], source_pixel_crop_box=box, common_integer_ground_relative_box=common, integer_ground_origin=origin, RGB_bytes_sha256=hashlib.sha256(cut.tobytes()).hexdigest(), resized=False, RGB_pixels_edited=False)
    crops = [crop(s, f'Move7-distance-window-{s["distance_window"]}-NATIVE-PIXEL-CROP-v001.png') for s in samples]
    for s, c in zip(samples, crops): c['distance_window'] = s['distance_window']
    contact(show / 'Move7-six-distance-windows-NATIVE-PIXEL-CROP-v001.png', crops, 3, lambda x: f'distance window {x["distance_window"]} | obs{x["observation"]}')
    contact(show / 'Move7-six-distance-windows-FULL-unscaled-v001.png', [dict(path=s['copy']['path'], observation=s['observation'], distance_window=s['distance_window']) for s in samples], 3, lambda x: f'distance window {x["distance_window"]} | obs{x["observation"]}')
    for edge in joins:
        edge['crops'] = [crop(s, f'JOIN-{edge["kind"]}-{i}-NATIVE-PIXEL-CROP-v001.png') for i, s in enumerate(edge['pair'])]
        contact(show / f'JOIN-{edge["kind"]}-NATIVE-PIXEL-CROP-pair-v001.png', edge['crops'], 2, lambda x: f'original adjacent obs{x["observation"]}')
        contact(show / f'JOIN-{edge["kind"]}-FULL-unscaled-pair-v001.png', [dict(path=s['copy']['path'], observation=s['observation']) for s in edge['pair']], 2, lambda x: f'original adjacent obs{x["observation"]}')
    final_copy = copy_native(len(frames) - 1, 'native-final-UNSCALED-v001.png')
    final = dict(native_original=pin(frames[-1]), native_copy=final_copy, decoded_final=pin(last), native_frame_index=len(frames) - 1, decoded_frame_index=len(frames) - 1, decode_count_equals_native=True, source_and_decoded_are_separate=True, lossy_video_pixel_equality_not_claimed=True, visual_reviewed=False)
    dump_new(raw / 'decoded-final-source-association-v001.json', final)
    metadata = []
    for source, name in [(data['archive'] / '原件/runtime-report.json', 'runtime-report.json'), (data['archive'] / ('原件/' + PROOF_NAME), PROOF_NAME), (data['archive'] / '原件/native-frame-pixels.jsonl', 'native-frame-pixels.jsonl'), (data['archive'] / 'index.json', 'native-session-index-readonly-copy.json'), (data['prereg'], 'Root-native-prereg-readonly-copy.json'), (data['manifest'], 'compiled-source-manifest-readonly-copy.json')]:
        metadata.append(copy_verified(source, raw / name))
    if data['retention']:
        metadata.append(copy_verified(data['retention'], raw / 'Root-native-archive-retention-record-readonly-copy.json'))
    index = dict(schema='Guard-Move7-native-review-media-source-version-status-v001', status='ACTUAL_NATIVE_INDEPENDENT_PASS_ROOT_E_AND_VISUAL_REVIEW_PENDING', native_bindings=data['bindings'], media_candidate=pin(C / 'Move7-native-media-freeze-v001.json'), actual_side=report['actual_approach_side'], process_id=int(report['process_id']), video=pin(video), native_frame_count=len(frames), complete_native_source_manifest=sources, source_manifest_scope='Every original MovieFrame pinned; full PNG sequence remains in original F native archive and Root E archive. This review directory copies selected originals only.', all_native_PNGs_copied_to_this_media=False, samples=samples, sample_semantics='six real accepted-distance windows, not six raster animation frames', required_sample_count=6, actual_adjacent_joins=joins, required_join_count=2, crops=crops, original_metadata_copies=metadata, presentation_frame_retention=timing, final_frame=final, native_originals_modified=False, all_original_frames_encoded_once=True, native_callback_wall_pacing_preserved=True, simulation_or_Guard_clock_used_for_video=False, video_silent=True, audio_recorded=False, visual_reviewed=False, Hurt_Stun_native_covered=False, historical_block_cause_verified=False, footlock=False, FinalAccepted=False, formal_complete_units=0, E_before_view_required=True)
    (output / 'README.md').write_text('Move7真实原生单侧试样。完整电影PNG序列保留在native_bindings.native_archive及Root独立E原archive保全；本审阅目录只复制六个真实接受距离窗口、两组严格相邻回调和末帧的选定原PNG，绝不冒称自包含全部PNG。完整微秒VFR读取每一个原MovieFrame，按真实callback单调墙钟编码一次，逐帧全解码校验帧数及PTS；仿真/Guard时钟不用于视频编码。七个实际提交组件的源/floatquad由独立检查器复核；六窗口不是六张生成动画帧。原幅1280×720和固定整数ground相对crop均不缩放/重绘，contact标签只在原像素矩形之外。两组接续是Move7→首个自然Windup0、同Aid Recovery3→静止Ready相邻原回调，没有补帧、拼攻击或改时序。完整静音视频有损展示，源PNG与解码末帧分别索引。普通Hurt/Stun、足锁/隐藏socket、音色和最终接受都不在本次证明范围。Root完成E双SHA保全后才能View/播放。\n', encoding='utf-8')
    index['output_files_before_index'] = [pin(p) for folder in [raw, show] for p in sorted(folder.iterdir()) if p.is_file()] + [pin(output / 'README.md')]
    return index

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    parser.add_argument('--output')
    parser.add_argument('--native-retention-receipt')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    archive = Path(args.archive).resolve()
    retention = Path(args.native_retention_receipt).resolve() if args.native_retention_receipt else None
    data = actual_inputs(archive, dependencies(), retention)
    if args.validate_only:
        print(json.dumps(dict(actual_native_and_independent_verified=True, native_frames=len(data['frames']), six_real_distance_windows=6, actual_adjacent_joins=2, media_written=False, UE_started=False, View=False, FinalAccepted=False)))
        return
    need(args.output, 'NEW absolute F dated output leaf required')
    output = Path(args.output)
    need(output.is_absolute(), 'Absolute output required')
    output = output.resolve()
    need(output.is_relative_to(ROOT / '过程图稿与视频') and not output.exists() and output.parent.is_dir(), 'Unused dated topic leaf under existing F media parent required')
    need(output != archive and archive not in output.parents and output not in archive.parents, 'Output must be separate from readonly native archive')
    output.mkdir()
    status = dict(schema='Guard-Move7-native-media-preparation-status-v001', status='PREPARING_UNVIEWED_ROOT_E_REQUIRED', native_archive=archive.as_posix(), media_candidate=pin(C / 'Move7-native-media-freeze-v001.json'), native_originals_modified=False, UE_started=False, View=False, FinalAccepted=False)
    try:
        index = prepare(output, data)
        dump_new(output / 'source-version-status-index.json', index)
        status.update(status=index['status'], source_version_status_index=pin(output / 'source-version-status-index.json'), video=index['video'], native_frames=index['native_frame_count'], decoded_frames=index['presentation_frame_retention']['decoded_frames'])
    except Exception as error:
        status.update(status='FAILED_PRESERVED', failure=str(error))
        raise
    finally:
        dump_new(output / 'media-preparation-status-v001.json', status)
    print(json.dumps(status, ensure_ascii=False))

if __name__ == '__main__':
    main()
