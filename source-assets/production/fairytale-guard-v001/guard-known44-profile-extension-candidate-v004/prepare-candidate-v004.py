"""Prepare a new checker variant; never mutate the frozen v003 or actual tools."""
from pathlib import Path
import difflib,hashlib,json,runpy
ROOT=Path('F:/Ourgame').resolve();HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'presentation-full-known44-observer-tooling-candidate-v003/tooling/verify-known44-axecycle-v002.py'
def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,text):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:f.write(text)
def jsonfile(p,j):write(p,json.dumps(j,ensure_ascii=False,indent=2)+'\n')
assert fact(OLD)['sha256']=='df5a0213242cd0187682a7cc9ab781b70ae06750a01cc80d40560f8c3eedbf72'
validator=HERE/'validate-production-extension-v004.py'
text=OLD.read_text(encoding='utf-8-sig')
old_init='HERE=Path(__file__).resolve().parent;CANDIDATE=HERE.parent;WORKSPACE=CANDIDATE.parents[3]'
new_init="HERE=Path(__file__).resolve().parent;WORKSPACE=Path('F:/Ourgame').resolve();CANDIDATE=WORKSPACE/'source-assets/production/fairytale-guard-v001/presentation-full-known44-observer-tooling-candidate-v003'"
old_line=" need({resolve(x['path']).relative_to(WORKSPACE).as_posix() for x in old}|saved=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Old Production+28 native saved packages is not exact compiled set')"
new_line="\n".join([
 " import runpy",
 " extension_validator=HERE/'validate-production-extension-v004.py'",
 " need(sha(extension_validator)=='"+fact(validator)['sha256']+"','Pinned production extension validator differs')",
 " runpy.run_path(str(extension_validator))['validate_production_set']({resolve(x['path']).relative_to(WORKSPACE).as_posix() for x in old}|saved,files,p,WORKSPACE,__file__)",
])
assert text.count(old_init)==text.count(old_line)==1
new=text.replace(old_init,new_init).replace(old_line,new_line)
checker=HERE/'verify-known44-profile-extension-v004.py'
compile(new,str(checker),'exec');compile(validator.read_text(encoding='utf-8'),str(validator),'exec')
write(checker,new)
write(HERE/'checker-v003-to-profile-extension-v004.patch',''.join(difflib.unified_diff(text.splitlines(True),new.splitlines(True),fromfile=OLD.as_posix(),tofile=checker.as_posix())))
cfg=read(ROOT/'source-assets/production/fairytale-hero-state-gap-v001/hurt-runtime-prepared-v002/prepared-v002/import-validator-config-v002.json')
template={'schema':'guard-known44-Root-production-extension-Hurt32-v004','is_template':True,'RootApproved':False,
 'namespace':cfg['namespace'],'baseline_files':1254,'extension_files':32,'final_files':1286,
 'compiled_manifest_sha256':None,
 'profile_source_checker_pin':fact(checker),'extension_validator_pin':fact(validator),
 'baseline_guard_import_receipt_pin':cfg['old_guard_actual_receipt'],'baseline_guard_twoSHA_pin':cfg['old_guard_independent_verification'],
 'Hurt_import_manifest_pin':cfg['import_manifest'],'Hurt_import_validator_config_pin':fact(ROOT/'source-assets/production/fairytale-hero-state-gap-v001/hurt-runtime-prepared-v002/prepared-v002/import-validator-config-v002.json'),
 'Hurt_importer_pin':fact(ROOT/'source-assets/production/fairytale-hero-state-gap-v001/hurt-runtime-prepared-v002/prepared-v002/ue-import-Hurt32-v002.py'),
 'Hurt_actual_native_import_receipt_pin':None,'Hurt_independent_twoSHA_verification_pin':None,
 'actual_preload_finish_receipt':None,'actual_runtime_receipt':None,'FinalAccepted':False}
jsonfile(HERE/'Root-production-extension-Hurt32-TEMPLATE-NOT-APPROVED-v004.json',template)
pins={'schema':'Guard-known44-production-extension-readonly-inputs-v004','frozen_checker':fact(OLD),
 'original_Guard_tooling_freeze':fact(OLD.parent.parent/'known44-AxeCycle-tooling-freeze-v003.json'),
 'Hurt_import_manifest':cfg['import_manifest'],'Hurt_import_validator_config':template['Hurt_import_validator_config_pin'],'Hurt_importer':template['Hurt_importer_pin'],
 'StunIR_shared_checker_pins':fact(HERE.parent/'presentation-full-known44-combat-observer-candidate-v004/independent-profile-input-pins-v003.json'),
 'Death_shared_checker_pins':fact(HERE.parent/'presentation-full-known44-combat-death-candidate-v006/independent-profile-input-pins-v005.json')}
jsonfile(HERE/'read-only-input-pins-v004.json',pins)
write(HERE/'HANDOFF.md','''# Guard known44 approved Production extension candidate v004

Confirmed frozen checker v003 line 100 requires old1226 ∪ actual Guard28.saved to equal all compiled Production (1254). After a real Hurt32 import the exact set becomes 1286, so the old checker rejects it. StunIR v004 and Death v006 call the same pinned source_check function.

The new checker preserves every original Source/compiled-file/disk/build/strict native registry/Guard44/row/alias/scale/Guard28 provenance/twoSHA check. Only its location initialization points back to the unchanged original Guard candidate and the single Production set equality calls a SHA-pinned extension validator. The two-block diff is provided. The original frozen checker, protocol, freezes and runtime actor are untouched. The old candidate_freeze_pin remains the original Guard observer/tooling lock; the NEW Root extension record additionally pins this new checker and helper. source_check(snapshot, prereg) and CLI remain compatible.

Without production_extension_pin the old exact1254 boundary remains. With extras the fresh profile prereg must pin a NEW actual Root approval record (not this template). The record must bind the fresh compiled_manifest_sha256, old Guard receipt/twoSHA proof, exact pre-reviewed Hurt32 manifest/config/importer, actual successful native Hurt32 receipt and independent twoSHA proof. The current template has RootApproved=false, is_template=true and actual Hurt receipts null, so it cannot admit anything.

The gate reuses the pinned Hurt v002 host source/RGBA validator without running main or UE. It verifies all 32 source PNGs and metadata, 512 RGBA, the exact three optional empty FarHand1–3 owners, native Texture2D512/source filename/UI settings/target filenames, actual receipt input binding, host preflight pin, real saved32 and compiled package hashes. It requires exact old1254 ∪ approved32 == compiled Production1286, no overlaps/extras, then rechecks actual disk exact1286 and old1254/new32 byte/SHA twice. It makes no GPU compilation or Hurt runtime claim and changes no Guard source/texture authority.

Root integration after actual Hurt import: retain this candidate; create a new Root approval file from the template with real receipt pins and fresh compiled snapshot SHA; add production_extension_pin to the NEW source/profile prereg; use this new checker for source preflight. For StunIR/Death create NEW independent-profile-input-pins/preregs that point to this checker and retain the original Guard tooling freeze. Do not overwrite old frozen inputs or backdate old preregs. Existing launchers that directly invoke the v003 checker also need a new version targeting the new checker; historical launchers remain intact.

Actual Hurt receipt is pending. Host checks here establish only unchanged old1254 mode and fail-closed missing/pending extension behavior; they do not simulate or fabricate an imported32 pass. Actual native import/preload/runtime receipts remain null.
''')
print(json.dumps({'checker':fact(checker),'validator':fact(validator),'original_checker_unchanged':fact(OLD),'actual_Hurt_native_receipt':None},ensure_ascii=False))
