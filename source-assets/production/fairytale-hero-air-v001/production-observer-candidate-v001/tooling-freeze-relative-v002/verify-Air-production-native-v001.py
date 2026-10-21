"""Read-only Air6 source/preflight/native/pair verification. Never launches UE.

Outputs, if requested, are exclusive-create JSON only. Raw PNG/bin/WAV evidence
is never modified. Failed trials retain fixed registration and fixed gates.
"""
from pathlib import Path
import argparse
import json
import math
import sys
import zlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import air_production_contract_v001 as C


def verify_png_fifo(original, r):
    metadata = C.read(original / 'native-lossless-capture.json')
    C.need(metadata['mode'] == 'native_viewport_BGRA8_lossless_PNG_zlib0'
           and all(metadata[k] is False for k in ('pixel_mutations', 'simulation_pacing_changed', 'audio_changed')),
           'Native original capture metadata differs')
    C.need(metadata['async_movie_writer_requested'] is True and metadata['async_movie_writer_active'] is True
           and metadata['prewarm_synchronous'] is True
           and metadata['movie_filename_reservation'] == 'Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue', 'Actual exclusive async writer required')
    rows = [json.loads(line) for line in (original / 'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line]
    names = [x['file'] for x in rows]; movie = [x for x in rows if x['file'].startswith('MovieFrame')]
    C.need(len(set(names)) == len(names) and set(names) == {p.name for p in original.glob('MovieFrame*.png')} | {'prewarm-viewport.png'}, 'Exact original PNG membership/unique FIFO differs')
    C.need(len(movie) == len(r['observations']) > 1 and [x['file'] for x in movie] == sorted(x['file'] for x in movie)
           and [x['writer_sequence'] for x in movie] == list(range(1, len(movie) + 1)), 'Actual one PNG per callback serial FIFO differs')
    timing = r['capture_timing']; start = timing['capture_start_monotonic_s']; stop = timing['capture_stop_monotonic_s']
    for row in rows:
        C.need(Path(row['file']).name == row['file'] and row['saved'] is True, 'Actual preserved PNG receipt required')
        with Image.open(C.file_under(original, row['file'])) as im:
            C.need(im.format == 'PNG' and im.size == (1280, 720) == (row['width'], row['height']), 'Original native1280x720 PNG required')
            rgba = np.asarray(im.convert('RGBA'))
        C.need(np.all(rgba[..., 3] == 255) and zlib.crc32(rgba[..., [2, 1, 0, 3]].tobytes()) & 0xffffffff == row['native_BGRA8_crc32'], 'Original native PNG viewport CRC mismatch')
    for row, offset in zip(movie, timing['frame_wall_offsets_s']):
        C.need(row['async_writer'] is True and row['copy_crc_matches'] is True and row['filename_reserved'] is True
               and row['filename_reservation_mode'] == 'Windows_CreateFileW_CREATE_NEW'
               and row['copied_BGRA8_crc32'] == row['native_BGRA8_crc32'], 'Actual native original copy/reservation receipt differs')
        values = [row[k] for k in ('capture_callback_monotonic_s', 'reservation_completed_monotonic_s', 'enqueued_monotonic_s', 'save_started_monotonic_s', 'save_completed_monotonic_s')]
        C.need(all(C.finite(x) for x in values) and 0 < start <= values[0] <= stop
               and values[0] <= values[1] <= values[2] <= values[3] <= values[4]
               and values[0] <= start + offset + 1e-6 and C.near(row['save_wall_s'], values[4] - values[3], 1e-6), 'Actual async original capture/reserve/enqueue/save timing differs')
    prewarm = next(x for x in rows if x['file'] == 'prewarm-viewport.png')
    C.need(prewarm.get('async_writer', False) is False, 'Prewarm must remain synchronous')
    summary = C.read(original / 'native-async-write-summary.json'); count = len(movie)
    C.need(all(summary[k] is True for k in ('requested', 'active', 'closed', 'flushed', 'success'))
           and all(summary[k] == count for k in ('movie_reserved', 'movie_enqueued', 'movie_saved', 'movie_completed', 'receipts_saved'))
           and all(summary[k] == 0 for k in ('movie_reservation_failed', 'movie_failed', 'rejected', 'pending')), 'Actual async final writer counts differ')
    C.need(r['native_async_capture_writes_flushed'] is True
           and summary['flush_completed_monotonic_s'] >= stop >= start + timing['frame_wall_offsets_s'][-1]
           and summary['last_save_completed_monotonic_s'] <= summary['flush_completed_monotonic_s']
           and C.near(summary['first_capture_callback_monotonic_s'], movie[0]['capture_callback_monotonic_s'], 1e-6)
           and C.near(summary['last_capture_callback_monotonic_s'], movie[-1]['capture_callback_monotonic_s'], 1e-6), 'Final actual callback/audio Stop must precede completed PNG flush')
    return movie


def optical_witnesses(original, r, profile, manifest, movie):
    pixel = C.module(C.DODGE_PIXELS, 'frozen_Dodge_optical_functions', C.DODGE_PIXELS_SHA)
    source_paths = {a['object_path']: a['source'] for a in manifest['assets']}
    source_paths[profile['independent_sword']['object_path']] = profile['independent_sword']['source']['path']
    sources = {}
    for name, path in source_paths.items():
        with Image.open(path) as im: rgba = np.asarray(im, dtype=np.float64) / 255
        rgba[..., :3] = pixel.linear(rgba[..., :3]); sources[name] = rgba
    results = []
    for ordinal in (1, 2, 3):
        for frame in range(6):
            choices = [(i, o) for i, o in enumerate(r['observations']) if o['observed_air_transition_ordinal'] == ordinal and o['physical_visual_key'] == frame]
            C.need(choices, 'Each real jump needs all6 source-pixel witnesses')
            i, o = choices[len(choices) // 2]; d = o['new_air_draw']; slots = d['slots']
            xs, ys = [], []
            for slot in slots:
                for src in ([0, 0], [512, 0], [0, 512], [512, 512]):
                    p = C.project(slot, src); xs.append(p[0]); ys.append(p[1])
            x0 = max(0, math.floor(min(xs)) - 1); x1 = min(1280, math.ceil(max(xs)) + 1)
            y0 = max(0, math.floor(min(ys)) - 1); y1 = min(720, math.ceil(max(ys)) + 1)
            C.need(x1 > x0 and y1 > y0, 'Source-projected native ROI outside viewport')
            yy, xx = np.mgrid[y0:y1, x0:x1]; color = np.zeros((*xx.shape, 3)); alpha = np.zeros(xx.shape); sword = np.zeros(xx.shape)
            tint = np.asarray(d['tint'])
            for slot in slots:
                rgba = pixel.sample(sources[slot['texture']], slot, xx, yy)
                a = np.clip(rgba[..., 3] * tint[3], 0, 1); rgb = rgba[..., :3] * tint[:3]
                color = rgb * a[..., None] + color * (1 - a[..., None]); alpha = a + alpha * (1 - a)
                sword = a if slot['component'] == 8 else sword * (1 - a)
            expected = np.rint(pixel.srgb(color) * 255).astype(np.uint8)
            with Image.open(C.file_under(original, movie[i]['file'])) as im: actual = np.asarray(im.convert('RGB'))[y0:y1, x0:x1]
            error = np.mean(np.abs(actual.astype(float) - expected.astype(float)), axis=-1)
            opaque = (alpha >= .999) & (np.max(expected, axis=-1) >= 32)
            blade = (sword >= .98) & (np.min(expected, axis=-1) >= 45)
            bc, sc, bm, bg, sm, sg = fixed_optical_gate(error, opaque, blade)
            results.append(dict(ordinal=ordinal, frame=frame, file=movie[i]['file'], body_pixels=bc, blade_pixels=sc,
                                body_median=bm, body_fraction_le55=bg, blade_median=sm, blade_fraction_le65=sg))
    return dict(source_registered_witnesses=results, registration_search_used=False, pixels_modified=False,
                inherited_fixed_Dodge_gates=True, FinalAccepted=False)


def fixed_optical_gate(error, opaque, blade):
    bc, sc = int(np.count_nonzero(opaque)), int(np.count_nonzero(blade))
    C.need(bc >= 150 and sc >= 8, 'Fixed original source-pixel body/blade minimum count failed')
    bm, bg = float(np.median(error[opaque])), float(np.mean(error[opaque] <= 55))
    sm, sg = float(np.median(error[blade])), float(np.mean(error[blade] <= 65))
    C.need(all(C.finite(x) for x in (bm, bg, sm, sg)) and bm <= 40 and bg >= .60 and sm <= 50 and sg >= .60,
           'Fixed source-pixel registration error gate failed; never search/relax after failure')
    return bc, sc, bm, bg, sm, sg


def verify_flow(r, manifest, profile, prereg):
    C.need(r['schema'] == C.SCHEMA and r['scenario'] == C.SCENARIO and r['passed'] is True and r['flow_complete'] is True
           and r['failure'] == '' and r['profile_closure'] == C.CLOSURE and r['profile_id'] == profile['profile_id']
           and r['native_ready_freeze_SHA256'] == C.SOURCE_FREEZE_SHA, 'Actual native Air6 successful core flow/source49 receipt required')
    C.need(all(r[k] is False for k in ('final_accepted', 'visual_reviewed', 'audio_listened', 'NoArmor_is_formal20_pair',
                                      'transition_ordinals_are_gameplay_jump_ids', 'player_Guard_HP_position_AI_time_writes')), 'Observer scope cannot claim unrun/final acceptance or gameplay writes')
    C.need(r['additional_scenarios'] == dict(normal_landing_J_priority='OPEN_not_run', normal_landing_Shift_priority='OPEN_not_run', real_save_restore='OPEN_not_run'), 'Unrun J/Shift/save scenarios must remain OPEN')
    C.need(r['requested_facing'] == prereg['requested_facing'] and r['requested_facing'] in (-1, 1), 'Requested physical facing differs')
    for key in ('process_id', 'owner', 'current_room', 'restart_serial', 'weapon_instance', 'weapon_version', 'armor_instance', 'armor_version'): C.uint(r[key], bits=32 if key == 'process_id' else 64)
    C.uint(r['epoch'], zero=True)
    C.need(r['restart_serial'] == '1' and isinstance(r['run'], str) and len(r['run']) == 32 and all(x in '0123456789abcdefABCDEF' for x in r['run']) and int(r['run'], 16) > 0, 'Fresh real run/restart required')
    C.need(r['initial_hp'] == r['capture_final_hp'] > 0, 'Player HP changed; no repair allowed')
    inputs = r['normal_inputs']; downs = [x for x in inputs if x['down']]
    C.need([x['key'] for x in downs] == ['Enter', 'A' if r['requested_facing'] < 0 else 'D', 'SpaceBar', 'E', 'SpaceBar', 'SpaceBar'], 'Exactly ordinary Enter/direction/Space/E/Space/Space required')
    held = set(); previous = -1
    for x in inputs:
        C.need(type(x['down']) is bool and C.finite(x['wall_offset_s']) and previous <= x['wall_offset_s'], 'Actual key input order invalid')
        previous = x['wall_offset_s']; key = x['key']
        C.need(key in ('Enter', 'A', 'D', 'SpaceBar', 'E'), 'Additional/diagnostic input forbidden')
        if x['down']: C.need(key not in held, 'Duplicate key press'); held.add(key)
        else: C.need(key in held, 'Unpaired release'); held.remove(key)
        C.need(all(C.finite(x[k]) for k in ('before_H', 'before_V', 'before_landing_age', 'after_H', 'after_V', 'after_landing_age', 'sim')), 'Raw input before/after physical sample missing')
    C.need(not held, 'Final keys must be released')
    spaces = [x for x in downs if x['key'] == 'SpaceBar']; last_space = spaces[-1]
    C.need(last_space['before_H'] == last_space['before_V'] == 0 and C.f32(.06) <= last_space['before_landing_age'] < C.f32(.12)
           and last_space['after_H'] == 0 and last_space['after_V'] == 630
           and r['normal_rejump_issued_inside_original_landing'] is True
           and r['rejump_input_landing_age'] == last_space['before_landing_age'], 'Actual normal Space missed original landing[.06f,.12f) or did not relaunch')
    diagnostics = r['diagnostic_knight_hits']
    C.need((len(diagnostics) == 1 if prereg['diagnostic_clear_knight'] else len(diagnostics) == 0), 'Knight diagnostic differs from explicit prereg')
    for x in diagnostics:
        C.uint(x['entity']); C.need(x['content'] == 'ENM-STN-001' and x['api'] == 'ADungeonFighter::ApplyCombatHit'
            and x['explicit_cli_authorization'] is True and x['before_hp'] > x['after_hp'] == 0 and x['dead'] is True, 'Only explicit predecessor Knight public hit is allowed')
    obs = r['observations']; offsets = r['capture_timing']['frame_wall_offsets_s']
    C.need(len(obs) == len(offsets) > 18 and all(C.finite(t) for t in offsets)
           and all(b > a for a, b in zip(offsets, offsets[1:])), 'Unique increasing original callbacks required')
    masks = [0, 0, 0]; air_transitions = land_transitions = ready = noarmor = light = landframes = 0
    timing = r['capture_timing']; duration = timing['capture_stop_monotonic_s'] - timing['capture_start_monotonic_s']
    C.need(all(0 <= x['wall_offset_s'] < duration for x in inputs), 'Normal input outside actual audio/movie interval')
    previous_air = False; last_draw = 0; last_sim = -1; last_ready_index = -1; ready_draw_ids = set(); joins = []
    for i, (o, offset) in enumerate(zip(obs, offsets)):
        C.need(o['wall_offset_s'] == offset and o['sim'] >= last_sim and C.finite(o['sim']), 'Original callback simulation clock differs'); last_sim = o['sim']
        for key, want in (('run', r['run']), ('owner', r['owner']), ('current_room', r['current_room']), ('epoch', r['epoch']), ('player_entity', r['owner'])): C.need(o[key] == want, 'Actual callback owner/run/room/epoch differs')
        C.need(o['interface_visible'] is False and o['text_calls'] == 0 and o['range_debug'] is False and o['range_lines'] == 0
               and o['hp'] == r['initial_hp'] and o['dead'] is False and o['native_actor_root_z'] == 0, 'Player/hiddenUI/root state changed')
        C.need(all(o[k] == o['sim'] for k in ('melee_time', 'wa_time', 'dodge_time', 'weapon_world_time')), 'Actual completed subsystem double clocks differ')
        h, v, age = o['jump_height'], o['vertical_velocity'], o['landing_visual_age']; frame = C.selection(h, v, age); air = h > 0 or v > 0
        if air and not previous_air:
            air_transitions += 1
            C.need(1 <= air_transitions <= 3, 'Unexpected extra observed jump')
            trigger = spaces[air_transitions - 1]
            before = obs[i - 1] if i else None
            C.need(before is not None and before['wall_offset_s'] < trigger['wall_offset_s'] <= offset
                   and before['sim'] <= trigger['sim'] <= o['sim']
                   and trigger['before_H'] == trigger['before_V'] == 0
                   and trigger['after_H'] == 0 and trigger['after_V'] == 630, 'Actual ordinary Space input must precede its first native airborne callback')
            if air_transitions == 2:
                equip = next(x for x in downs if x['key'] == 'E')
                first_land5 = next(x for x in obs[:i] if x['observed_air_transition_ordinal'] == 1 and x['physical_visual_key'] == 5)
                C.need(first_land5['wall_offset_s'] < equip['wall_offset_s'] < trigger['wall_offset_s'], 'Normal E must follow first full jump and precede second Space')
        if not air and previous_air: land_transitions += 1
        previous_air = air
        C.need(o['observed_air_transition_ordinal'] == air_transitions and o['transition_ordinal_is_gameplay_jump_id'] is False
               and o['physical_visual_key'] == frame, 'Observed transitions/physical velocity key differ')
        if frame >= 0:
            C.need(1 <= air_transitions <= 3 and o['new_air_query_ok'] is True and o['melee_active'] is False
                   and o['wa_active'] is False, 'Only real nonattack samples can claim Air')
            C.verify_draw(o, frame, profile, manifest, r)
            draw_id = C.uint(o['new_air_draw']['draw_id']); C.need(draw_id > last_draw, 'Actual Air DrawId repeated'); last_draw = draw_id
            masks[air_transitions - 1] |= 1 << frame
            if air_transitions == 1: noarmor += 1
            else: light += 1
            if frame >= 4: landframes += 1
        elif o['phase'] == 9 and air_transitions == land_transitions == 3 and h == v == 0 and age == C.f32(.12):
            d = o['old_draw']
            C.need(o['new_air_draw']['drawn'] is False and d['active'] is True and d['supported'] is True
                   and d['texture_ready'] is True and d['armor_drawn'] is True and d['sword_drawn'] is True
                   and d['clip'] == 'sword_ready_idle' and d['actual_stack'] == o['rendered_player_stack'], 'Ordinary Ready join callback missing')
            C.need(i == last_ready_index + 1 or ready == 0, 'Ready2 callbacks must be adjacent'); last_ready_index = i; ready += 1
            draw_id = C.uint(d['draw_id']); C.need(draw_id > last_draw and draw_id not in ready_draw_ids, 'Ready callback repeats a stale DrawId')
            ready_draw_ids.add(draw_id)
            if ready == 1: C.need(i > 0 and obs[i - 1]['physical_visual_key'] == 5, 'Actual Land5→ordinaryReady adjacency missing')
        if i and obs[i - 1]['physical_visual_key'] == 5 and frame == 0:
            joins.append(dict(kind='Land5_to_Air0', before=i - 1, after=i, ordinal=air_transitions))
    C.need(masks == [63, 63, 63] and [r[k] for k in ('starter_NoArmor_mask', 'light_first_mask', 'light_second_mask')] == masks
           and r['normal_space_inputs'] == len(spaces) == air_transitions == r['air_transitions'] == land_transitions == r['landing_transitions'] == 3, 'All3 native jumps and complete6pose masks required')
    C.need(noarmor == r['starter_NoArmor_frames'] >= 6 and light == r['light_frames'] >= 12
           and landframes == r['landing_frames'] and ready == r['Ready_join_frames'] >= 2,
           'Recomputed actual None/LGT/Landing/Ready coverage differs')
    C.need(len(joins) == 1 and joins[0]['ordinal'] == 3, 'Actual adjacent Land5→Air0 re-jump required')
    return dict(actual6pose_masks=masks, actual_air_transitions=air_transitions, actual_landing_transitions=land_transitions,
                Ready_join_frames=ready, actual_adjacent_rejump=joins[0], NoArmor_is_formal20_pair=False)


def verify_native(archive, prereg_path):
    c, p, manifest, profile, pp, run_directory = C.preflight(prereg_path, __file__)
    archive = c.resolve(archive, within=C.ROOT); C.need(archive == run_directory, 'Archive differs from exact Root prereg run directory')
    original = archive / '原件'; r = C.read(original / 'runtime-report.json'); index = C.read(archive / 'index.json')
    C.need(index['schema'] == 'hero-Air6-production-native-session-v001' and index['exit_code'] == 0
           and index['process_id'] == C.uint(r['process_id'], bits=32) and index['root_prereg_pin'] == c.pin(pp)
           and index['compiled_manifest_pin'] == p['compiled_manifest_pin'] and index['checker_freeze_pin'] == p['checker_freeze_pin']
           and index['source_probe_freeze_pin'] == p['source_probe_freeze_pin'], 'Actual fresh session PID/exit/prereg/source pins differ')
    claim = C.read(original / 'observer-process-claim-v001.json')
    C.need(claim['schema'] == 'hero-air-production-process-claim-v001' and claim['pid'] == int(r['process_id']), 'Native exclusive process claim differs')
    flow = verify_flow(r, manifest, profile, p)
    gpu = C.verify_gpu(original, r, manifest, profile)
    movie = verify_png_fifo(original, r)
    audio = C.module(C.AUDIO_CHECKER, 'frozen_native_mix_audio_checker', C.AUDIO_CHECKER_SHA).audit(original / 'runtime-report.json', require_frame_timing=True)
    optical = optical_witnesses(original, r, profile, manifest, movie)
    return dict(schema='hero-Air6-production-independent-native-v001', passed=True, process_id=int(r['process_id']),
                requested_facing=r['requested_facing'], root_prereg_pin=c.pin(pp), native_report_pin=c.pin(original / 'runtime-report.json'),
                compiled_manifest_pin=p['compiled_manifest_pin'], source_probe_freeze_pin=p['source_probe_freeze_pin'],
                checker_freeze_pin=p['checker_freeze_pin'], flow=flow, actual_GPU_bytes=gpu, native_PNG_CRC_FIFO_verified=True,
                audio=audio, source_pixels=optical, additional_scenarios=r['additional_scenarios'],
                audio_listened=False, visual_reviewed=False, formal20_complete=False, FinalAccepted=False)


def paircheck(left_archive, left_prereg, right_archive, right_prereg):
    left = verify_native(left_archive, left_prereg); right = verify_native(right_archive, right_prereg)
    C.need(left['requested_facing'] == -1 and right['requested_facing'] == 1
           and left['process_id'] != right['process_id'] and Path(left_archive).resolve() != Path(right_archive).resolve()
           and left['root_prereg_pin'] != right['root_prereg_pin'], 'Fresh left/right need separate PID/archive/prereg')
    for key in ('compiled_manifest_pin', 'source_probe_freeze_pin', 'checker_freeze_pin'):
        C.need(left[key] == right[key], 'Pair binds different exact compiled/source/checker inputs')
    return dict(schema='hero-Air6-production-independent-pair-v001', passed=True, left=left, right=right,
                actual_two_fresh_PIDs=True, both6pose_None6_LGT9_rejump_Ready_verified=True,
                additional_J_Shift_save='OPEN_not_run', audio_listened=False, visual_reviewed=False,
                formal20_complete=False, FinalAccepted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--source-only', action='store_true'); modes.add_argument('--verify-preflight', action='store_true')
    modes.add_argument('--native', action='store_true'); modes.add_argument('--paircheck', action='store_true')
    parser.add_argument('--root-prereg'); parser.add_argument('--archive'); parser.add_argument('--left-prereg')
    parser.add_argument('--right-prereg'); parser.add_argument('--left-archive'); parser.add_argument('--right-archive'); parser.add_argument('--output')
    a = parser.parse_args()
    if a.source_only:
        c, m, p, mp, fp, pp = C.source_only()
        result = dict(schema='hero-Air6-source-only-v001', passed=True, source_manifest=mp, source_freeze=fp,
                      profile=pp, source48_RGBA512=True, source49_closed=True, UE_started=False, FinalAccepted=False)
    elif a.verify_preflight:
        C.need(a.root_prereg, 'Root prereg required'); c, p, *_ = C.preflight(a.root_prereg, __file__)
        result = dict(schema='hero-Air6-preflight-v001', passed=True, root_prereg=c.pin(a.root_prereg),
                      full203_strict_GREEN=True, actual_Source_and_Production1419_pins_verified=True,
                      requested_facing=p['requested_facing'], native_run_executed=False, FinalAccepted=False)
    elif a.native:
        C.need(a.root_prereg and a.archive, 'Actual native archive and prereg required')
        result = verify_native(a.archive, a.root_prereg)
    else:
        C.need(a.left_prereg and a.right_prereg and a.left_archive and a.right_archive, 'Both real preregs and archives required')
        result = paircheck(a.left_archive, a.left_prereg, a.right_archive, a.right_prereg)
    if a.output:
        C.import_contract().write_new(a.output, result)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__': main()
