"""Read-only current-lineage and normal-input locomotion request verifier.

Inherited causal/source/resource/PNG/optical/MainMix gates execute unchanged.
Named request facts and fixed-window signal candidates are separate claims.
No UE launch, media modification, listening, codec or latency acceptance.
"""
from pathlib import Path
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import sys
import wave

sys.dont_write_bytecode = True
ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
OBSERVER = 'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp'
DLL = 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
PREDECESSOR_SHA = '97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5'
CUES = ('HERO_STEP_LIGHT_01', 'HERO_STEP_LIGHT_02', 'HERO_TAKEOFF_LIGHT_01',
        'HERO_LAND_LIGHT_01', 'HERO_LAND_FIRM_01', 'HERO_DODGE_SHORT_01')
CAUSES = ('ground_distance_threshold', 'ground_distance_threshold', 'successful_takeoff',
          'natural_landing', 'natural_landing', 'dodge_started')

def need(ok, why):
    if not ok:
        raise ValueError(why)

def finite(x):
    return type(x) in (int, float) and math.isfinite(x)

def near(a, b, tol=1e-8):
    return finite(a) and finite(b) and abs(a-b) <= tol

def read(path):
    def unique(items):
        result = {}
        for k, v in items:
            need(k not in result, 'Duplicate JSON key: '+k)
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def resolved(path):
    p = Path(path)
    return (p if p.is_absolute() else ROOT/p).resolve()

def pin(path):
    p = resolved(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return dict(path=p.as_posix(), bytes=p.stat().st_size, sha256=h.hexdigest())

def check_pin(row):
    p = resolved(row['path'])
    need(type(row['bytes']) is int and row['bytes'] >= 0 and p.is_file(), 'Pinned member missing: '+str(p))
    actual = pin(p)
    need((actual['bytes'], actual['sha256']) == (row['bytes'], row['sha256']), 'Pinned member changed: '+str(p))
    return p

def same_pin(a, b):
    return resolved(a['path']) == resolved(b['path']) and (a['bytes'], a['sha256']) == (b['bytes'], b['sha256'])

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def dependencies():
    table = read(HERE/'dependencies-v001.json')
    loaded = {row['label']: check_pin(row) for row in table['members']}
    need(len(loaded) == len(table['members']), 'Duplicate dependency labels')
    landing = load_module(loaded['landing_checker'], 'locomotion_frozen_landing')
    legacy, F, C = landing.dependencies()
    signal = load_module(loaded['signal_checker'], 'locomotion_frozen_template_search')
    return loaded, landing, legacy, F, C, signal

def freeze_members(row):
    path = check_pin(row)
    freeze = read(path)
    need(freeze.get('FinalAccepted', False) is False, 'Freeze must not imply final content acceptance')
    members = freeze.get('members', freeze.get('files'))
    need(isinstance(members, list) and members, 'Freeze member list required')
    members = [dict(path=(path.parent/x['relative_path']).as_posix(), bytes=x['bytes'], sha256=x['sha256'])
               if 'relative_path' in x else x for x in members]
    for member in members:
        check_pin(member)
    return freeze, members

def verify_overlay(before, cm, ad, source_members):
    """Pure exact-membership check, independent of mutable previous DLL/build files."""
    need(ad['schema'] == 'Root-hero-locomotion-audio-observer-admission-v001'
         and ad['RootApproved'] is True and ad['is_template'] is False and ad['actual_applied'] is True,
         'Actual Root observer admission required')
    need(ad['actual_source_files'] == 303 and ad['actual_production_files'] == 1425
         and ad['new_source_files'] == 0 and ad['verification_passes'] == 2
         and ad['unrelated_source_tests_content_byte_mismatches'] == 0, 'Wrong bounded source/content admission')
    old = {r['path']: r for r in before['files']}
    now = {r['path']: r for r in cm['files']}
    need(len(old) == len(before['files']) and len(now) == len(cm['files']), 'Duplicate compiled member')
    need(len(ad['before_files']) == len(ad['after_files']) == 1
         and ad['before_files'][0] == old[OBSERVER] and ad['after_files'][0] == now[OBSERVER],
         'Exactly one reviewed observer CPP before/after must match compiled lineage')
    after = ad['after_files'][0]
    need(any(Path(x['path']).name == Path(OBSERVER).name
             and (x['bytes'], x['sha256']) == (after['bytes'], after['sha256']) for x in source_members),
         'Actual observer differs from frozen reviewed projected source')
    for prefix, count in (('UnrealGame/Source/', 303), ('UnrealGame/Content/Production/', 1425)):
        paths = {p for p in now if p.startswith(prefix)}
        previous = {p for p in old if p.startswith(prefix)}
        need(len(paths) == count and paths == previous, 'Source/content exact membership changed: '+prefix)
        for path in paths-{OBSERVER}:
            need(now[path] == old[path], 'Unrelated source/test/content changed: '+path)
    need(now[OBSERVER] != old[OBSERVER], 'The new observation source was not actually compiled')
    tests = lambda rows: {r['path']:(r['bytes'], r['sha256']) for r in rows if '/Source/' in r['path'] and '/Tests/' in r['path']}
    need(tests(cm['files']) == tests(before['files']), 'Frozen 203 test sources changed')
    return dict(actual_source_files=303, actual_production_files=1425, allowed_changed_source=[OBSERVER],
                unrelated_source_tests_content_byte_mismatches=0, old203_test_sources_unchanged=True)

def verify_audio_binding(loaded):
    manifest = read(loaded['import_manifest'])
    recovery = read(loaded['import_recovery'])
    imported = read(check_pin(recovery['import_receipt']))
    readonly = read(check_pin(recovery['fresh_readonly_verification']))
    check_pin(recovery['import_process_receipt']); check_pin(recovery['fresh_readonly_process'])
    need(recovery['actual_import_process_exit_code'] == 1 and recovery['initial_import_clean_exit'] is False
         and recovery['actual_saved_assets'] == 6 and recovery['fresh_readonly_exit_code'] == 0,
         'Preserve actual import exit1 and separate readonly recovery exit0')
    need(imported['manifest_sha256'] == pin(loaded['import_manifest'])['sha256']
         and imported['success'] is True and imported['actual_imported'] == imported['actual_saved'] == 6
         and readonly['passed'] is True and readonly['actual_asset_mutations'] is False
         and readonly['actual_import_operations'] == 0, 'Actual six-source import/readonly binding differs')
    proposal = {r['cue']:r for r in manifest['rows']}
    actual = {r['cue']:r for r in imported['rows']}
    validated = {r['cue']:r for r in readonly['rows']}
    need(set(proposal) == set(actual) == set(validated) == set(CUES)
         and len(manifest['rows']) == len(imported['rows']) == len(readonly['rows']) == 6,
         'Exact six distinct cue source/import bindings required')
    for cue in CUES:
        p, a, v = proposal[cue], actual[cue], validated[cue]
        check_pin(dict(path=p['source_wav'], bytes=p['source_bytes'], sha256=p['source_sha256']))
        check_pin(dict(path=a['saved_uasset'], bytes=a['saved_bytes'], sha256=a['saved_sha256']))
        need(p['object_path'] == a['object_path'] == v['object_path']
             and p['source_sha256'] == a['source_sha256'] == v['source_wav_sha256']
             and a['saved_sha256'] == v['saved_uasset_sha256'] and a['imported'] is True
             and v['complete_source_PCM_byte_equal'] is True
             and v['final_codec'] == 'ADPCM' and v['final_loading'] == 'FORCE_INLINE', 'Cue source/asset payload differs: '+cue)
        need(pin(v['exported_raw_wave'])['sha256'] == v['exported_raw_wave_sha256'] == p['source_sha256'],
             'Readonly raw imported WAV differs: '+cue)
        with wave.open(str(resolved(p['source_wav'])), 'rb') as wav:
            need(wav.getsampwidth() == 2 and wav.getnchannels() == 1 and wav.getframerate() == 48000
                 and wav.getcomptype() == 'NONE', 'Original mono48k PCM16 source required: '+cue)
            payload = wav.readframes(wav.getnframes())
        need(hashlib.sha256(payload).hexdigest() == v['source_pcm_sha256'], 'Complete imported source PCM digest differs: '+cue)
    return proposal

def preflight_context(compiled_manifest, source_admission):
    loaded, landing, legacy, F, C, signal = dependencies()
    cm_path, ad_path = resolved(compiled_manifest), resolved(source_admission)
    cm, ad = read(cm_path), read(ad_path)
    need(cm['source_files'] == 303 and cm['production_files'] == 1425
         and cm['registered_tests'] == cm['passed'] == 203 and cm['failed'] == cm['notRun'] == 0,
         'Actual current Source303/Production1425/full203 required')
    need(same_pin(cm['source_admission_pin'], pin(ad_path)), 'Current CM source admission pin differs')
    need(ad['predecessor_compiled_manifest']['sha256'] == PREDECESSOR_SHA
         and same_pin(ad['predecessor_compiled_manifest'], pin(loaded['predecessor_compiled_manifest'])),
         'Actual 97d4d029 predecessor required')
    source_freeze, source_members = freeze_members(ad['source_candidate_freeze'])
    need(source_freeze['base_compiled_manifest_sha256'] == PREDECESSOR_SHA, 'Source candidate has another predecessor')
    review = check_pin(ad['fresh_source_review'])
    need('Approved' in review.read_text(encoding='utf-8-sig'), 'Fresh independent source review approval missing')
    overlay = verify_overlay(read(loaded['predecessor_compiled_manifest']), cm, ad, source_members)
    C.strict203(read(check_pin(cm['full_suite'])))
    build = read(check_pin(cm['build']))
    need(build['ExitCode'] == 0 and build['Target'] == 'CodexDungeonEditor', 'Actual clean Editor build required')
    log = check_pin(cm['build_log'])
    need(resolved(build['Log']) == log, 'Build receipt differs from compiled build log')
    for row in cm['files']:
        check_pin(row)
    paths = {row['path'] for row in cm['files']}
    need(DLL in paths, 'Current compiled DLL missing')
    for prefix, count in (('UnrealGame/Source/', 303), ('UnrealGame/Content/Production/', 1425)):
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/prefix).rglob('*') if p.is_file()}
        need(actual == {p for p in paths if p.startswith(prefix)} and len(actual) == count,
             'Actual on-disk directory membership differs: '+prefix)
    bindings = verify_audio_binding(loaded)
    return loaded, landing, legacy, F, C, signal, cm, ad, overlay, bindings

def verify_preflight(compiled_manifest, source_admission):
    *_, cm, ad, overlay, bindings = preflight_context(compiled_manifest, source_admission)
    return dict(schema='hero-locomotion-audio-current-independent-preflight-v001', passed=True,
                compiled_manifest_pin=pin(compiled_manifest), source_admission_pin=pin(source_admission),
                source_overlay=overlay, exact_six_source_bindings=list(bindings),
                registered_tests=203, UE_started=False, native_audio_verified=False, FinalAccepted=False)

def decimal(value):
    need(type(value) is str and value.isascii() and value.isdigit()
         and str(int(value)) == value and 0 <= int(value) < 2**64, 'Exact uint64 decimal string required')
    return int(value)

def verify_requests(r, bindings):
    obs, final = r['observations'], r['hero_locomotion_audio']
    need(final['schema'] == 'hero-locomotion-request-observation-v001'
         and final['request_only'] is True and final['audible_or_mix_attribution_proven'] is False
         and final['callback_count'] == len(obs) and final['ring_limit'] == 256
         and final['ring_limit_seen'] is False and final['first_snapshot_truncation_possible'] is False
         and final['sequence_gap_count'] == 0 and decimal(final['sequence_gap_missing_sequence_total']) == 0,
         'Complete first-seen request sequence without truncation/gaps required')
    start = r['capture_timing']['capture_start_monotonic_s']
    stop = r['capture_timing']['capture_stop_monotonic_s']
    requests, scope_changes, last_scope = [], 0, None
    ground_witnesses = []
    for i, o in enumerate(obs):
        a = o['hero_locomotion_audio']; scope = a['current_scope']; w = a['callback_wall_window']
        need(a['schema'] == final['schema'] and a['callback_index'] == i
             and a['request_only'] is True and a['audible_or_mix_attribution_proven'] is False,
             'Actual named request callback index/scope claims differ')
        need(scope == dict(run=o['run'], owner=o['owner'], room=o['current_room'], epoch=o['epoch'], restart=r['restart_serial']),
             'Current request scope borrowed another actual callback owner/run/room/epoch/restart')
        for key in ('owner', 'room', 'epoch', 'restart'):
            decimal(scope[key])
        changed = last_scope is not None and scope != last_scope
        need(a['scope_changed'] is changed, 'Reported scope reset differs from actual callbacks')
        scope_changes += int(changed); last_scope = scope
        lower = start if i == 0 else start+obs[i-1]['wall_offset_s']
        upper = start+o['wall_offset_s']
        need(w['semantics'] == 'first_seen_between_completed_callbacks_not_emission_timestamp'
             and near(w['lower_monotonic_s'], lower) and near(w['upper_monotonic_s'], upper)
             and near(w['lower_offset_s'], lower-start) and near(w['upper_offset_s'], upper-start)
             and start <= lower <= upper < stop, 'First-seen wall window must be actual adjacent completed callbacks')
        need(type(a['ring_snapshot_count']) is int and 0 <= a['ring_snapshot_count'] < 256
             and a['ring_limit'] == 256, 'Actual untruncated ring count differs')
        first, last = decimal(a['ring_first_sequence']), decimal(a['ring_last_sequence'])
        need((a['ring_snapshot_count'] == 0 and first == last == 0)
             or (a['ring_snapshot_count'] > 0 and first > 0 and last-first+1 == a['ring_snapshot_count']),
             'Observed request ring sequence bounds differ')
        need(a['new_request_count'] == len(a['new_requests']), 'New request callback count differs')
        previous_sim = obs[i-1]['sim'] if i else 0.
        for q in a['new_requests']:
            seq = decimal(q['sequence']); source = q['request_scope']
            need(q['request_only'] is True and q['audible_or_mix_attribution_proven'] is False
                 and q['first_seen_callback_index'] == i and q['first_seen_phase'] == o['phase']
                 and q['first_seen_sim_time_s'] == o['sim'] and q['first_seen_current_scope'] == scope
                 and q['first_seen_wall_window'] == w and first <= seq <= last,
                 'Request first-seen callback/phase/window differs')
            need(source['run_available'] is False and source['run'] is None
                 and all(source[k] == scope[k] for k in ('owner', 'room', 'epoch', 'restart'))
                 and q['request_scope_matches_current'] is True, 'Request scope differs or invented event RunGuid')
            need(q['request_wall_time_available'] is False and q['request_monotonic_s'] is None
                 and q['source_interval_available'] is False and q['source_from_time_s'] is None
                 and q['source_to_time_s'] is None and q['source_distance_available'] is False
                 and q['source_distance_cm'] is None, 'Unavailable event wall/interval/distance must remain unavailable')
            need(decimal(q['sequence_gap_before']) == 0 and seq == len(requests)+1,
                 'Request sequence duplicate/gap/replay or capture starts after unseen sequence')
            cue, enum = q['cue'], q['cue_enum']
            need(type(enum) is int and 0 <= enum < 6 and CUES[enum] == cue
                 and q['asset_path'] == bindings[cue]['object_path']
                 and q['source_cause'] == CAUSES[enum]
                 and q['source_cause_basis'] == 'mapped_existing_cue_enum_not_new_gameplay_event',
                 'Actual cue enum/cause/source SoundWave binding differs')
            need(near(q['volume'], .25 if enum < 2 else .32, 1e-7) and q['pitch'] == 1
                 and finite(q['at_time_s']) and finite(q['requested_at_time_s'])
                 and 0 <= q['at_time_s'] <= q['requested_at_time_s'] <= o['sim']
                 and q['requested_at_time_s']-q['at_time_s'] <= .25
                 and (i == 0 or previous_sim < q['requested_at_time_s']),
                 'Request source/dispatch/first-seen simulation interval differs')
            need(len(q['ground_position_at_dispatch']) == 2 and all(finite(v) for v in q['ground_position_at_dispatch']),
                 'Finite actual dispatch ground required')
            step, landing, dodge = enum < 2, enum in (3, 4), enum == 5
            need(q['step_fields_applicable'] is step and q['landing_fields_applicable'] is landing
                 and q['dodge_fields_applicable'] is dodge, 'Typed request fields applicability differs')
            ordinal = decimal(q['step_ordinal']); event = decimal(q['dodge_event_id']); action = decimal(q['dodge_action_id'])
            need(q['event_id_available'] is dodge and q['event_id'] == (q['dodge_event_id'] if dodge else None),
                 'Only actual Dodge has source EventId')
            need((step and ordinal > 0) or (not step and ordinal == 0), 'Step ordinal on wrong cue')
            need((dodge and event > 0 and action > 0) or (not dodge and event == action == 0), 'Dodge IDs on wrong cue')
            need(all(finite(q[k]) and q[k] >= 0 for k in ('fall_speed_cm_s', 'fall_distance_cm'))
                 and (landing or q['fall_speed_cm_s'] == q['fall_distance_cm'] == 0), 'Landing fields on wrong cue')
            requests.append(q)
        need(a['captured_request_prefix_count'] == len(requests), 'Captured request prefix differs')
        g = a['ground_witness']; need(type(g['available']) is bool
             and g['semantics'] == 'actual_completed_callback_motion_not_event_source_interval', 'Ground witness scope differs')
        if g['available']:
            need(all(g[k] == scope[k] for k in ('run', 'owner', 'room'))
                 and all(finite(g[k]) for k in ('from_time_s', 'to_time_s', 'accepted_distance_cm', 'walk_distance_cm'))
                 and 0 <= g['from_time_s'] < g['to_time_s'] <= o['sim']
                 and 0 <= g['walk_distance_cm'] <= g['accepted_distance_cm']+1e-8
                 and len(g['from_xy']) == len(g['to_xy']) == 2
                 and all(finite(v) for v in g['from_xy']+g['to_xy']), 'Actual completed motion witness invalid')
            ground_witnesses.append(dict(callback=i, **g))
    need(final['scope_change_count'] == scope_changes and scope_changes == 0
         and requests == final['captured_requests'] and final['captured_request_count'] == len(requests),
         'Final named request list differs from exact first-seen callback reconstruction')
    counts = Counter(q['cue'] for q in requests)
    need(counts[CUES[2]] == counts[CUES[4]] == counts[CUES[5]] == 1 and counts[CUES[3]] == 0
         and counts[CUES[0]] > 0 and counts[CUES[1]] > 0, 'Exactly one takeoff/natural FirmLand/Dodge and alternating feet required; Light must stay untriggered')
    inputs = r['normal_inputs']; down = [x for x in inputs if x['key'] == 'D' and x['down'] is True]
    up = [x for x in inputs if x['key'] == 'D' and x['down'] is False]
    need(len(down) == len(up) == 2
         and down[0]['sim'] < up[0]['sim'] <= down[1]['sim'] < up[1]['sim'],
         'Real D approach plus separate normal facing pulse required')
    intervals = [(a['sim'], b['sim']) for a, b in zip(down, up)]
    steps = [q for q in requests if q['step_fields_applicable']]
    for n, q in enumerate(steps, 1):
        need(decimal(q['step_ordinal']) == n and q['cue'] == CUES[(n-1)%2]
             and any(lower <= q['at_time_s'] <= upper for lower, upper in intervals),
             'Footstep outside real movement interval, wrong parity or historical backfill')
    need(any(g['grounded'] is True and g['ordinary_eligible'] is True and g['had_move_intent'] is True
             and g['walk_distance_cm'] > 0 for g in ground_witnesses), 'No actual ordinary grounded movement witness')
    takeoff = next(q for q in requests if q['cue'] == CUES[2])
    space = next(x for x in inputs if x['key'] == 'SpaceBar' and x['down'] is True)
    rise = next(o for o in obs[r['ready_callback_index']+1:] if o['jump_height'] > 0)
    need(space['sim'] <= takeoff['at_time_s'] <= rise['sim'], 'Takeoff is not this accepted normal Space rise')
    land_index = r['landing_callback_index']; land = obs[land_index]
    landing = next(q for q in requests if q['cue'] == CUES[4])
    need(obs[land_index-1]['sim'] < landing['at_time_s'] <= land['sim']
         and landing['first_seen_callback_index'] >= land_index
         and (landing['fall_speed_cm_s'] >= 540 or landing['fall_distance_cm'] >= 110),
         'Firm landing does not match the original natural airborne-to-ground transition')
    dodge = next(q for q in requests if q['cue'] == CUES[5]); action = obs[r['first_action_callback_index']]['action']
    need(dodge['at_time_s'] == action['start'] and dodge['dodge_action_id'] == action['id']
         and dodge['dodge_event_id'] == action['start_event_id']
         and dodge['first_seen_callback_index'] >= r['first_action_callback_index'], 'Dodge request differs from actual accepted Started ActionId/EventId/Start')
    return dict(passed=True, captured_request_count=len(requests), cue_counts=dict(counts),
                naturally_covered_cue_types=5, light_landing='UNTRIGGERED', scope_changes=0,
                complete_first_seen_sequence=True, exact_event_ground_distance_reconstructed=False,
                ground_witness_count=len(ground_witnesses), unavailable_event_RunGuid_wall_interval_distance_preserved=True,
                request_only=True, audible_or_mix_attribution_proven=False)

def signal_candidates(r, bindings, signal):
    """Every request uses its own real first-seen callback window; no best-file search."""
    mix_path = r['main_submix_capture']['canonical_wav']
    mix, rate = signal.pcm(mix_path)
    rows = []
    for q in r['hero_locomotion_audio']['captured_requests']:
        source = bindings[q['cue']]; template, source_rate = signal.pcm(source['source_wav'])
        w = q['first_seen_wall_window']
        value = signal.template_search(mix, rate, template, source_rate, w['lower_offset_s'], w['upper_offset_s'])
        rows.append(dict(sequence=q['sequence'], cue=q['cue'], asset_path=q['asset_path'],
                         source_wav_pin=pin(source['source_wav']), first_seen_callback=q['first_seen_callback_index'],
                         callback_window=w, threshold=.75, **value))
    for row in rows:
        if not row.get('search_complete'):
            row['overlapping_candidate_sequences'] = []
            continue
        lo, hi = row['candidate_template_start_s'], row['candidate_template_start_s']+row['template_duration_s']
        row['overlapping_candidate_sequences'] = [x['sequence'] for x in rows if x is not row
             and x.get('search_complete') and lo < x['candidate_template_start_s']+x['template_duration_s']
             and x['candidate_template_start_s'] < hi]
    summary = {cue:dict(requests=sum(x['cue'] == cue for x in rows),
                       strong_candidates=sum(x['cue'] == cue and x.get('strong_template_signal_candidate') is True for x in rows)) for cue in CUES}
    return dict(threshold=.75, window_policy='actual_first_seen_callback_interval_then_original_fixed_-0.10_+0.25s',
                rows=rows, cue_summary=summary, all_observed_requests_have_signal_candidates=all(x.get('strong_template_signal_candidate') is True for x in rows),
                source_run_pcm_time_used=False, SimulationTime_used_as_PCM_time=False, full_file_best_window_search_used=False,
                codec_validated=False, exclusive_cue_attribution=False, auditioned=False, device_latency_measured=False, final_mix_accepted=False)

def verify_session(r, prereg, index, launch, claim, archive, cm_path, ad_path, checker_freeze):
    need(prereg['schema'] == 'Root-hero-locomotion-audio-native-prereg-v001' and prereg['RootApproved'] is True
         and prereg['is_template'] is False and prereg['pre_registered_before_capture'] is True
         and prereg['FinalAccepted'] is False and prereg['requested_action'] == 'Shift'
         and prereg['requested_facing'] == 1 and prereg['diagnostic_clear_knight'] is True
         and prereg['correlation_threshold'] == .75, 'Actual fixed Shift-right prereg required')
    need(resolved(prereg['run_directory']) == archive and ROOT.resolve() in archive.parents,
         'Exact prereg archive required')
    need(same_pin(prereg['compiled_manifest_pin'], pin(cm_path))
         and same_pin(prereg['source_admission_pin'], pin(ad_path))
         and same_pin(prereg['checker_freeze_pin'], pin(checker_freeze))
         and same_pin(prereg['checker_pin'], pin(__file__)), 'Prereg current CM/admission/checker differs')
    need(index['exit_code'] == 0 and str(index['process_id']) == str(launch['process_id']) == r['process_id']
         and claim['schema'] == 'hero-landing-priority-process-claim-v001' and claim['process_id'] == r['process_id'],
         'Actual process PID/normal exit/exclusive claim differs')
    for key in ('compiled_manifest_pin', 'source_admission_pin', 'checker_freeze_pin'):
        need(same_pin(index[key], prereg[key]), 'Session lineage differs: '+key)
    need(same_pin(index['root_prereg_pin'], pin(archive/'preregistration-v001.json'))
         and datetime.fromisoformat(prereg['created_utc'].replace('Z','+00:00'))
         < datetime.fromisoformat(launch['started_utc'].replace('Z','+00:00')), 'Prereg must actually precede native process launch')
    need(launch['schema'] == 'Root-hero-locomotion-audio-native-launch-v001'
         and launch['requested_action'] == 'Shift' and launch['requested_facing'] == 1
         and launch['human_input'] is False and launch['diagnostic_clear_knight'] is True
         and launch['fixed_time_step_requested'] is False, 'Normal queued-input launch scope differs')
    args = launch['arguments']; need(isinstance(args, list) and all(type(x) is str for x in args), 'Exact argv token array required')
    configuration = read(HERE/'dependencies-v001.json')
    launcher = next(x for x in configuration['members'] if x['label'] == 'root_launcher')
    need(same_pin(prereg['launcher_pin'], launcher), 'Preregistered launcher differs from frozen actual Root launcher')
    check_pin(prereg['launcher_pin'])
    expected = configuration['expected_arguments_prefix']+[
        '-DungeonContentProofDir='+str(archive/'原件'), '-abslog='+str(archive/'native-engine.log')]
    need([x.replace('\\','/') for x in args] == [x.replace('\\','/') for x in expected],
         'Exact frozen normal-input launch argv differs; no added/removed arguments')
    required = ('-game', '-d3d11', '-DungeonHeroLandingPriorityProofV001', '-DungeonContentProof',
                '-DungeonFastLosslessCapture', '-DungeonAsyncLosslessCapture', '-DungeonCandidateSprites',
                '-DungeonFairytaleSwordEquipmentBoundPreview', '-DungeonFairytaleLeatherReadyPreview',
                '-DungeonFairytaleLeatherPrimary1Preview', '-DungeonFairytaleLeatherPrimary2Preview',
                '-DungeonFairytaleLeatherPrimary3Preview', '-DungeonFairytaleSwordWalkPreview',
                '-DungeonFairytaleSwordHurtPreview', '-DungeonFairytaleSwordDeathPreview',
                '-DungeonFairytaleSwordDodgePreview', '-DungeonFairytaleSwordAirPreview',
                '-DungeonFairytaleGuardFullPreview', '-DungeonFairytaleGuardStompPreview', '-DungeonFairytaleGuardMoveRigPreview',
                '-DungeonHeroLandingPriorityAction=Shift', '-DungeonHeroLandingPriorityFacing=1', '-DungeonHeroLandingPriorityClearKnightDiagnostic')
    need(all(x in args for x in required) and '/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom' in args
         and '-DungeonContentProofDir='+str(archive/'原件').replace('\\','/') in [x.replace('\\','/') for x in args], 'Required actual gameplay/art/capture flags missing')
    allowed_proofs = {'-DungeonHeroLandingPriorityProofV001', '-DungeonContentProof'}
    need(not any((('Proof' in x and x.startswith('-Dungeon') and not x.startswith('-DungeonContentProofDir=') and x not in allowed_proofs)
                  or x in ('-DungeonShowInterface', '-DungeonCombatRangeDebug', '-DungeonFairytaleLookdevPreview', '-nosound', '-nullrhi')
                  or x.lower().startswith(('-usefixedtimestep', '-fps=', '-benchmark'))) for x in args), 'Other proof/HUD/range/audio/pacing flags cannot share this case')
    need(r['requested_action'] == 'Shift' and r['requested_facing'] == 1 and r['passed'] is True
         and r['flow_complete'] is True and r['failure'] == '' and r['final_accepted'] is False
         and r['visual_reviewed'] is False and r['audio_listened'] is False
         and r['real_save_restore'] == 'OPEN_not_run' and r['player_Guard_HP_position_AI_time_writes'] is False,
         'Bounded actual native claims differ')
    need(all(o['interface_visible'] is False and o['text_calls'] == 0 and o['range_debug'] is False and o['range_lines'] == 0
             and all(o[k] == o['sim'] for k in ('melee_time','wa_time','dodge_time','weapon_world_time'))
             and o['native_actor_root_z'] == 0 for o in r['observations']), 'Actual HUD/range/native actor clocks/root changed')
    duration = r['capture_timing']['capture_stop_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']
    need(all(finite(x['wall_offset_s']) and 0 <= x['wall_offset_s'] < duration for x in r['normal_inputs']), 'Actual normal inputs must be inside recording')
    return dict(explicit_Knight_diagnostic=True, player_Guard_HP_position_AI_time_writes=False, UI_hidden=True, independent_case='Shift_right_only')

def verify_native(archive, compiled_manifest, source_admission):
    loaded, L, legacy, F, C, signal, cm, ad, overlay, bindings = preflight_context(compiled_manifest, source_admission)
    archive = resolved(archive); original = archive/'原件'
    p = read(archive/'preregistration-v001.json')
    checker_freeze = check_pin(p['checker_freeze_pin']); freeze, members = freeze_members(p['checker_freeze_pin'])
    need(any(same_pin(x, pin(__file__)) for x in members)
         and any(same_pin(x, pin(HERE/'dependencies-v001.json')) for x in members), 'Current checker/config absent from selected freeze')
    r = read(original/'runtime-report.json')
    session = verify_session(r, p, read(archive/'index.json'), read(archive/'launch-receipt-v001.json'),
                             read(original/'observer-process-claim-v001.json'), archive, compiled_manifest, source_admission, checker_freeze)
    flow = L.verify_causal(r)
    sources, am, ap = L.sources_for('Shift', legacy, C)
    typed = L.verify_typed_callbacks(r, am, ap, L.read(legacy['import-Dodge32-v001.json']), L.read(legacy['Dodge-runtime-profile-data-v001.json']))
    gpu = L.verify_resources(original, r, sources, am, ap)
    movie = F.verify_png_fifo(original, r)
    audio = C.module(C.AUDIO_CHECKER, 'locomotion_frozen_full_audio', C.AUDIO_CHECKER_SHA).audit(original/'runtime-report.json', require_frame_timing=True)
    pixels = L.optical(original, r, movie, sources, legacy, F, am, ap)
    named = verify_requests(r, bindings)
    candidates = signal_candidates(r, bindings, signal)
    return dict(schema='hero-locomotion-audio-current-independent-native-v001', passed=True,
                compiled_manifest_pin=pin(compiled_manifest), source_admission_pin=pin(source_admission),
                checker_freeze_pin=pin(checker_freeze), root_prereg_pin=pin(archive/'preregistration-v001.json'),
                native_report_pin=pin(original/'runtime-report.json'), session=session, source_overlay=overlay,
                flow=flow, all_typed_callbacks=typed, actual_resources=gpu, native_PNG_FIFO_CRC_verified=True,
                audio=audio, source_pixels=pixels, hero_locomotion_request_chain=named, signal_candidates=candidates,
                structure_and_native_capture_verified=True, all_cue_audio_complete=False,
                visual_reviewed=False, audio_listened=False, formal_complete_units=0, FinalAccepted=False)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preflight', action='store_true'); ap.add_argument('--archive')
    ap.add_argument('--compiled-manifest', required=True); ap.add_argument('--source-admission', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    try:
        need(a.preflight is not bool(a.archive), 'Select --preflight or --archive')
        need(not Path(a.out).exists(), 'Never overwrite any previous verification output')
        value = verify_preflight(a.compiled_manifest, a.source_admission) if a.preflight else verify_native(a.archive, a.compiled_manifest, a.source_admission)
        code = 0
    except (ValueError, KeyError, TypeError, OSError, StopIteration, AssertionError) as e:
        value = dict(passed=False, error=str(e), FinalAccepted=False); code = 3
    if not Path(a.out).exists():
        with Path(a.out).open('x', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(value, ensure_ascii=False)); return code

if __name__ == '__main__':
    raise SystemExit(main())
