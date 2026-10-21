"""Prepare exact48 import inputs after Root approval. Never launches Unreal.

--validate-source-only is read-only and needs no approval. Normal preparation
requires an existing pinned Root approval; this tool never manufactures one.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
from air48_import_contract_v001 import (
    ROOT, E_ROOT, NAMESPACE, OLD_COUNT, NEW_COUNT, FINAL_COUNT, SCOPE_FALSE,
    need, read, resolve, pin, write_new, load_prepared, baseline,
    validate_approval, verify_approval_retention, verify_old, exact_membership, load_import)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-manifest', required=True)
    p.add_argument('--source-freeze', required=True)
    p.add_argument('--source-approval')
    p.add_argument('--old-snapshot')
    p.add_argument('--output-dir')
    p.add_argument('--validate-source-only', action='store_true')
    a = p.parse_args()
    manifest_pin, freeze_pin = pin(a.source_manifest), pin(a.source_freeze)
    prepared, assets = load_prepared(manifest_pin, freeze_pin)
    if a.validate_source_only:
        need(not a.output_dir, 'Source validation writes no outputs; omit output-dir')
        print(json.dumps(dict(success=True, source_manifest=manifest_pin, candidate_freeze=freeze_pin,
                              source48_RGBA512_decoded=True, existing_sword_RGBA512_decoded=True,
                              actual_E_ZIPmember_twoSHA_verified=True, outputs_written=False,
                              UE_started=False, native_imported=False, TrialAllowed=False, FinalAccepted=False)))
        return
    need(a.source_approval and a.old_snapshot and a.output_dir,
         'Root source approval, authoritative old snapshot and NEW output-dir required')
    approval_pin = pin(resolve(a.source_approval, within=ROOT))
    approval = read(a.source_approval)
    validate_approval(approval, manifest_pin, freeze_pin, prepared['source_closure_digest'])
    verify_approval_retention(approval, prepared, manifest_pin, freeze_pin)
    old_pin = pin(a.old_snapshot)
    old = baseline(old_pin)
    if 'old_compiled_snapshot' in approval:
        need(approval['old_compiled_snapshot'] == old_pin, 'Approval baseline pin differs')
    m = dict(schema='Root-Air48-native-import-v001', namespace=NAMESPACE, replace_existing=False,
             expected_old_count=OLD_COUNT, expected_new_count=NEW_COUNT, expected_final_count=FINAL_COUNT,
             source_manifest=manifest_pin, candidate_freeze=freeze_pin, Root_source_approval=approval_pin,
             source_closure_digest=prepared['source_closure_digest'], old_compiled_snapshot=old_pin,
             old_production_files=old, assets=assets, **{k: False for k in SCOPE_FALSE})
    for repeat in range(2):
        verify_old(old)
        exact_membership(m, False)
    namespace_dir = ROOT / 'UnrealGame/Content' / NAMESPACE[6:]
    need(not namespace_dir.exists() and all(not Path(x['saved_path']).exists() for x in assets),
         'New namespace/packages must not exist')
    output = resolve(a.output_dir, within=ROOT / 'source-assets/production')
    need(not output.exists(), 'NEW preparation output directory required; preserve any earlier failure')
    # All mutable outputs stay outside the frozen media/native-ready candidate.
    source_dir = Path(manifest_pin['path']).parent
    need(not output.is_relative_to(source_dir), 'Do not write inside frozen source candidate')
    output.mkdir(parents=True, exist_ok=False)
    host = dict(schema='Air48-host-source-validation-v001', utc=datetime.now(timezone.utc).isoformat(),
                success=True, source_manifest=manifest_pin, candidate_freeze=freeze_pin,
                Root_source_approval=approval_pin, source_closure_digest=prepared['source_closure_digest'],
                contract=pin(Path(__file__).with_name('air48_import_contract_v001.py')), preparer=pin(__file__),
                source48_RGBA512_decoded=True, existing_sword_source_RGBA512_decoded=True,
                actual_E_ZIPmember_twoSHA_verified=True, old1371_exact_membership_twoSHA_verified=True,
                UE_started=False, native_imported=False, **{k: False for k in SCOPE_FALSE})
    m['host_source_validation'] = write_new(output / 'host-source-validation.json', host)
    import_pin = write_new(output / 'import-manifest.json', m)
    load_import(import_pin['path'])
    print(json.dumps(dict(success=True, manifest=import_pin, host_source_validation=m['host_source_validation'],
                          actual_imports=0, expected_final_count=FINAL_COUNT, UE_started=False,
                          TrialAllowed=False, FinalAccepted=False)))


if __name__ == '__main__':
    main()
