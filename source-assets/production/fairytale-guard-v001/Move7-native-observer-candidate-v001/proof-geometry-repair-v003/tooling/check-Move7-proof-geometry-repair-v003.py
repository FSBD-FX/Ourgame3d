"""JSON-only actual replay and exact AST delta; never PNG, UE, Source or E writes."""
from pathlib import Path
import argparse, ast, copy, hashlib, json, math, runpy, sys
import numpy as np
import move7_native_contract_v001 as a

def need(value, reason):
    if not value: raise ValueError(reason)

def tree(path): return ast.parse(Path(path).read_text(encoding='utf-8-sig'))
def dump(node): return ast.dump(node, include_attributes=False)
def fn(t, name): return next(x for x in t.body if isinstance(x, ast.FunctionDef) and x.name == name)
def reject(call):
    try: call()
    except (ValueError, AssertionError, KeyError, TypeError): return
    raise AssertionError('Invalid geometry fixture was accepted')

def check(archive, observer_receipt):
    before = a.CONTRACT_FIX / 'tooling'
    after = a.D / 'tooling'
    old = tree(before / 'verify-Move7-native-v001.py')
    new = tree(after / 'verify-Move7-native-v001.py')
    for name in [x.name for x in old.body if isinstance(x, ast.FunctionDef) and x.name not in ['near', 'verify']]:
        need(dump(fn(old, name)) == dump(fn(new, name)), 'Unrelated native geometry/threshold function changed: ' + name)
    old_near, new_near = fn(old, 'near').body[0].value, fn(new, 'near').body[0].value
    need(isinstance(old_near, ast.BoolOp) and isinstance(new_near, ast.BoolOp) and len(old_near.values) == 5 and len(new_near.values) == 7 and [dump(x) for x in old_near.values[2:]] == [dump(x) for x in new_near.values[4:]], 'Finite checks, absolute error or original tolerance changed')
    expected_prefix = ast.parse('isinstance(a,numbers.Real) and not isinstance(a,bool) and isinstance(b,numbers.Real) and not isinstance(b,bool)', mode='eval').body.values
    need([dump(x) for x in new_near.values[:4]] == [dump(x) for x in expected_prefix], 'Numerical repair is broader than Real scalars with bool rejected')
    native = copy.deepcopy(fn(new, 'verify')); removed_session = 0; removed_metadata = 0
    for statement in list(native.body):
        if isinstance(statement, ast.Expr) and 'Native session supplemental numerical type repair binding differs' in dump(statement):
            native.body.remove(statement); removed_session += 1
    class RemoveSupplemental(ast.NodeTransformer):
        def visit_Call(self, node):
            nonlocal removed_metadata
            if isinstance(node.func, ast.Name) and node.func.id == 'dict':
                for keyword in list(node.keywords):
                    if keyword.arg in ['proof_geometry_repair_freeze_pin', 'proof_geometry_repair_checker_pin']:
                        node.keywords.remove(keyword); removed_metadata += 1
            return self.generic_visit(node)
    native = RemoveSupplemental().visit(native)
    need(removed_session == 1 and removed_metadata == 2 and dump(native) == dump(fn(old, 'verify')), 'Native oracle differs beyond supplemental metadata and unchanged near() calls')
    old_contract, new_contract = tree(before / 'move7_native_contract_v001.py'), tree(after / 'move7_native_contract_v001.py')
    for name in [x.name for x in old_contract.body if isinstance(x, ast.FunctionDef) and x.name != 'preflight']:
        need(dump(fn(old_contract, name)) == dump(fn(new_contract, name)), 'Old files closure/five Source chain or gate changed: ' + name)
    preflight = copy.deepcopy(fn(new_contract, 'preflight')); removed = 0
    for statement in list(preflight.body):
        if 'PROOF_GEOMETRY_REPAIR_FREEZE' in dump(statement):
            preflight.body.remove(statement); removed += 1
    class OldCheckerName(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == 'OLD_CHECKER':
                return ast.copy_location(ast.parse("D/'tooling/verify-Move7-native-v001.py'", mode='eval').body, node)
            return node
    preflight = OldCheckerName().visit(preflight)
    need(removed == 2 and dump(preflight) == dump(fn(old_contract, 'preflight')), 'Preflight changed beyond explicit supplemental freeze/checker and fixed old checker lineage')
    old_fill, new_fill = tree(before / 'fill-Move7-native-prereg-v001.py'), tree(after / 'fill-Move7-native-prereg-v001.py')
    removed = 0
    for node in ast.walk(new_fill):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'update':
            for keyword in list(node.keywords):
                if keyword.arg in ['proof_geometry_repair_freeze_pin', 'proof_geometry_repair_checker_pin']:
                    node.keywords.remove(keyword); removed += 1
    new_fill = OldCheckerName().visit(new_fill)
    need(removed == 2 and dump(old_fill) == dump(new_fill), 'Root fill changed beyond fixed old lineage and supplemental pins')
    for name in ['verify-Move7-source-pixels-v001.py', 'verify-Move7-native-pixels-v001.py', 'test-Move7-contract-v001.py']:
        need((before / name).read_bytes() == (after / name).read_bytes(), 'CRC/FIFO/stop-flush/optics/original host gates must remain byte identical: ' + name)
    # The launcher is text because it is PowerShell; exact inverse leaves all
    # input flags, capture timing, failure preservation and execution unchanged.
    launcher = (after / 'capture-Move7-native-v001.ps1').read_text(encoding='utf-8')
    old_launcher = (before / 'capture-Move7-native-v001.ps1').read_text(encoding='utf-8')
    launcher = launcher.replace("\n$contractFix=Join-Path $candidate 'tool-contract-fix-v002'", '')
    inverse_new = "tool_contract_fix_freeze_sha256=(Get-FileHash -LiteralPath (Join-Path $contractFix 'Move7-tool-contract-fix-freeze-v002.json') -Algorithm SHA256).Hash.ToLowerInvariant();tool_contract_fix_checker_sha256=(Get-FileHash -LiteralPath (Join-Path $contractFix 'tooling/verify-Move7-native-v001.py') -Algorithm SHA256).Hash.ToLowerInvariant();proof_geometry_repair_freeze_sha256=(Get-FileHash -LiteralPath (Join-Path $derivative 'Move7-proof-geometry-repair-freeze-v003.json') -Algorithm SHA256).Hash.ToLowerInvariant();proof_geometry_repair_checker_sha256=(Get-FileHash -LiteralPath $checker -Algorithm SHA256).Hash.ToLowerInvariant();"
    inverse_old = "tool_contract_fix_freeze_sha256=(Get-FileHash -LiteralPath (Join-Path $derivative 'Move7-tool-contract-fix-freeze-v002.json') -Algorithm SHA256).Hash.ToLowerInvariant();tool_contract_fix_checker_sha256=(Get-FileHash -LiteralPath $checker -Algorithm SHA256).Hash.ToLowerInvariant();"
    need(launcher.count(inverse_new) == 1 and launcher.replace(inverse_new, inverse_old) == old_launcher, 'Launcher changed beyond supplemental immutable lineage pins')
    api = runpy.run_path(str(after / 'verify-Move7-native-v001.py'))
    old_api = runpy.run_path(str(before / 'verify-Move7-native-v001.py'))
    near = api['near']; negatives = 0; positives = 0
    for left, right, tolerance in [(0, np.float64(0), 0), (np.float64(12.5), 12.5, 0), (np.int64(2), 2, 0), (0., np.float64(1e-8), 1e-8), (np.float64(-1e-8), 0., 1e-8)]:
        need(near(left, right, tolerance), 'Finite real scalar at original tolerance rejected'); positives += 1
    for left, right, tolerance in [(False, 0, 0), (0, False, 0), (True, 1, 0), (1, True, 0), (np.bool_(False), 0, 0), (0, np.bool_(False), 0), (math.nan, 0., 1), (0., np.float64(math.nan), 1), (math.inf, 0., 1), (0., np.float64(math.inf), 1), (-math.inf, 0., 1), (0., np.float64(-math.inf), 1), (0., np.nextafter(np.float64(1e-8), np.float64(math.inf)), 1e-8), (np.float64(1e-6), 0., 1e-8), (1+0j, 1, 0), ('1', 1, 0)]:
        need(not near(left, right, tolerance), 'Bool/nonfinite/nonreal/outside original tolerance accepted'); negatives += 1
    need(not old_api['near'](220, np.float64(220), 0) and near(220, np.float64(220), 0), 'Original exact np.float64 misrejection not reproduced')
    report_path = archive / '原件/runtime-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8-sig'))
    need(report['passed'] and report['flow_complete'], 'Diagnosis must bind real completed native report')
    fixed = a.read(a.C / 'read-only-input-pins-v001.json')['inputs']
    profile = a.read(a.pin(fixed['prepared_profile']))
    solver = runpy.run_path(str(a.pin(fixed['host_solver'])))['ReferenceSolver'](a.pin(fixed['prepared_profile']), a.PROFILE_SHA)
    total = 0.; totals = {}; events = {e['event']: e for e in report['guard_original_events']}
    for event in report['guard_original_events']:
        if event['kind'] == 7:
            total += math.dist(event['from'], event['to']); totals[event['event']] = total
    real = [(i, o) for i, o in enumerate(report['observations']) if o.get('move_query_ok')]
    first_i, first_o = real[0]
    def replay(o, implementation=api):
        return implementation['verify_rig'](o, report, profile, solver, events[o['move_query']['movement_event']], totals[o['move_query']['movement_event']])
    reject(lambda: replay(first_o, old_api))
    for _, observation in real:
        replay(observation)
    geometry_negatives = 0
    for field, delta in [('source_pivot', 1e-7), ('source_rotation_radians', 1e-6), ('art_anchor_from_ground', 1e-5), ('screen_anchor', 1e-5)]:
        bad = copy.deepcopy(first_o); value = bad['rig_draw']['planned_parts'][0][field]
        if isinstance(value, list): value[0] += delta
        else: bad['rig_draw']['planned_parts'][0][field] += delta
        reject(lambda: replay(bad)); geometry_negatives += 1
    bad = copy.deepcopy(first_o); bad['rig_draw']['submitted_parts'][0]['submitted'] = False; reject(lambda: replay(bad)); geometry_negatives += 1
    bad = copy.deepcopy(first_o); bad['move_query']['block_known'] = True; reject(lambda: replay(bad)); geometry_negatives += 1
    template = a.read(a.C / 'Root-Move7-native-prereg-TEMPLATE-v001.json')
    template['source_extension_chain'][-1]['receipt_pin'] = a.fact(observer_receipt)
    base = a.read(a.pin(fixed['base_compiled_manifest']))
    expected = a.source_chain(template, base)
    actual = a.keyed([a.fact(p) for p in (a.ROOT / 'UnrealGame/Source').rglob('*') if p.is_file()])
    need(actual == expected and len(expected) == 283, 'Current actual Source differs from five exact admissions')
    return dict(schema='Move7-proof-geometry-repair-host-review-v003', passed=True, actual_failed_native_report=a.fact(report_path), first_actual_observation=first_i, original_builtin_only_np_float64_misrejection_reproduced=True, actual_Move_observations_replayed=len(real), actual_seven_part_geometry_replays=len(real)*7, actual_verify_rig_pass=True, finite_real_type_positive_cases=positives, bool_nonfinite_nonreal_original_threshold_negative_cases=negatives, mutated_geometry_and_resource_negative_cases=geometry_negatives, original_abs_tol_and_math_isfinite_AST_unchanged=True, native_oracle_AST_unchanged_except_near_and_supplemental_pins=True, old_files_and_five_Source_chain_AST_unchanged=True, actual_five_receipt_Source_count=len(actual), optics_CRC_FIFO_stop_flush_byte_identical=True, launcher_exact_inverse_delta_verified=True, actual_complete_native_checker_run=False, native_session_v001_rewritten=False, PNG_read=False, UE_started=False, View=False, Source_written=False, FinalAccepted=False)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--archive', required=True); p.add_argument('--observer-admission', required=True); p.add_argument('--output')
    args = p.parse_args()
    result = check(a.path(args.archive), a.path(args.observer_admission))
    if args.output:
        with a.path(args.output).open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(result, ensure_ascii=False))
