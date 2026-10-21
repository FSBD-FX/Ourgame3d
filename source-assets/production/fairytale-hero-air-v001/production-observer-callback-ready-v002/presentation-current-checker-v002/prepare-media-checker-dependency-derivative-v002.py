"""NEW media dependency-only derivative; no actual archive, UE, or View."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
OLD=HERE.parent.parent/'production-observer-candidate-v001/presentation-tooling-v001'
OLD_FREEZE=OLD/'Air-production-presentation-tooling-freeze-v001.json'
OLD_FREEZE_SHA='6a42d8a1722fb5ebbc3d8c26a621c843d12758464e02196e87f6ee5e3c253225'
OLD_SCRIPT_SHA='f84a2f5d16990a82b96074fc42187ebd7af6983d14e6df7d02e2411b9875300e'
OLD_CHECKER_SHA='66f1dd8e0978ea05b89356bb99953a99c282af53bd150fbf7ee6c8bbc8483bfb'
NEW_CHECKER=HERE.parent/'tooling-queued-input-v003/Air-production-proof-checker-freeze-v003.json'
NEW_CHECKER_SHA='a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46'


def pin(p):
    p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p,value):
    if not isinstance(value,(str,bytes)):value=json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    b=value.encode('utf-8') if isinstance(value,str) else value
    with Path(p).open('xb') as f:f.write(b)


def verify(row):
    if pin(row['path'])!=row:raise ValueError('Frozen dependency changed: '+row['path'])


def main():
    if pin(OLD_FREEZE)['sha256']!=OLD_FREEZE_SHA or pin(NEW_CHECKER)['sha256']!=NEW_CHECKER_SHA:raise ValueError('Expected frozen dependency differs')
    old=read(OLD_FREEZE);checker=read(NEW_CHECKER)
    for repeat in range(2):
        for row in old['members']+checker['members']:verify(row)
    src=OLD/'prepare-Air-production-media-v001.py'
    if pin(src)['sha256']!=OLD_SCRIPT_SHA:raise ValueError('Reviewed old media script differs')
    before=src.read_bytes()
    if before.count(OLD_CHECKER_SHA.encode('ascii'))!=1:raise ValueError('Unique dependency literal absent')
    after=before.replace(OLD_CHECKER_SHA.encode('ascii'),NEW_CHECKER_SHA.encode('ascii'),1)
    btree=ast.parse(before.decode('utf-8'));atree=ast.parse(after.decode('utf-8'))
    before_functions={n.name:ast.dump(n,include_attributes=False) for n in btree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    after_functions={n.name:ast.dump(n,include_attributes=False) for n in atree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    if before_functions!=after_functions:raise ValueError('Function scope changed')
    def normalize(tree):
        for n in tree.body:
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHECKER_FREEZE_SHA' for t in n.targets):n.value=ast.Constant('CHECKER_DEPENDENCY_ONLY')
        return ast.dump(tree,include_attributes=False)
    if normalize(btree)!=normalize(atree):raise ValueError('Nondependency AST changed')
    write(HERE/'before-media-source-f84-v001.py',before)
    entry=HERE/'prepare-Air-production-media-v001.py';write(entry,after)
    inputs=dict(schema='HeroAir-production-presentation-current-checker-inputs-v002',
        previous_media_freeze=pin(OLD_FREEZE),previous_media_script=pin(src),current_checker_freeze=pin(NEW_CHECKER),
        current_checker=checker['checker_pin'],current_protocol=checker['protocol_pin'],current_source_probe_freeze=checker['source_probe_freeze_pin'],
        previous_media_algorithms_host_validation='Inherited original 5/5 actual ffmpeg synthetic AV/PTS/PCM/board tests and precise README-only write-order audit in unchanged 6a42 closure. These are host tests, not native or listening proof.',
        old_all_members_two_SHA_verified=True,new_checker_all_members_two_SHA_verified=True,
        original_native_archive_UE_execution=False,actual_E_or_View=False,FinalAccepted=False)
    write(HERE/'dependency-inputs-v002.json',inputs)
    delta=dict(schema='HeroAir-production-presentation-checker-dependency-delta-v002',
        utc=datetime.now(timezone.utc).isoformat(),before_source=pin(HERE/'before-media-source-f84-v001.py'),after_source=pin(entry),
        exactly_one_64byte_SHA_literal_replaced=True,reversible_exact_bytes=after.replace(NEW_CHECKER_SHA.encode('ascii'),OLD_CHECKER_SHA.encode('ascii'),1)==before,
        all_function_AST_identical=True,function_count=len(before_functions),whole_module_AST_identical_except_checker_SHA=True,
        old_checker_freeze_SHA256=OLD_CHECKER_SHA,current_checker_freeze=pin(NEW_CHECKER),
        microsecond_encoder_and_movie_timescale_1000000_unchanged=True,complete_native_PCM_and_AAC_padding_gates_unchanged=True,
        original_PNG_CRC_and_source_binding_unchanged=True,full_frame_VFR_and_copyts_PTS_gate_unchanged=True,
        nonoverlapping_unscaled_board_and_redecoded_exact_RGB_crops_unchanged=True,
        no_UE_or_actual_archive_or_E_View=True,no_repeated_synthetic_AV_generation=True,FinalAccepted=False)
    if not delta['reversible_exact_bytes']:raise ValueError('Replacement not exact reversible')
    write(HERE/'exact-dependency-only-delta-v002.json',delta)
    write(HERE/'HANDOFF.md',f'''NEW presentation dependency-only derivative; source/algorithm original6a42 preserved.

Current actual checker freeze: {NEW_CHECKER.as_posix()}\nSHA256 {NEW_CHECKER_SHA}.
SourceProbeFreeze remains Root prereg's actual be6... candidate/admission/current compiled CM binding. Full native success must come from queued causal v003, never old66f1. Failed oldleft_v001 remains FAILED and cannot pass this media tool.

Only one checker SHA constant changed. All function AST and all other module AST are identical; full-frame microsecondVFR + movie_timescale1e6, original audio origin/firstcallbackoffset, complete engine/canonical PCM copies, full AAC without trimming/replacement, wholeAV decode/count/PTS, fixed AAC padding2048 bound, originalPNG source provenance, sixLGT/eighteenNoneLGTRejump/actualjoins and nonoverlap/exactRGB boards retain original gates. No extra rawPNG/GPU copies. Existing 5/5 synthetic AV verification is inherited via original6a42 closure; no pointless regeneration. This is not native/listening/art acceptance.

```powershell
$airPython='F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$airMedia='{entry.as_posix()}'
& $airPython -B -X utf8 $airMedia --archive '<actual native archive root>' --root-prereg '<actual new prereg.json>' --independent '<actual v003 independent PASS.json>' --validate-only
& $airPython -B -X utf8 $airMedia --archive '<same native archive root>' --root-prereg '<same prereg.json>' --independent '<same independent PASS.json>' --output 'F:/Ourgame/过程图稿与视频/<NEW dated topic side version>'
```

Tool reruns exact frozen v003 native verifier read-only and compares retained independent result before any output. Output is NEW F leaf only. Preserve the complete original native archive and new presentation leaf to E with actual indices/twoSHA before Root View/listening. No E file creation or View here. Index refers full native MovieFrame paths/hashes without claiming self-contained allPNG, and copies selected fullviewport samples/joins, complete engine+canonical WAV and required metadata. Root remains sole actual executor/reviewer; FinalAccepted=false.
''')
    members=[pin(p) for p in sorted(HERE.glob('*')) if p.is_file()]
    for repeat in range(2):
        for row in members:verify(row)
    output=HERE/'Air-production-presentation-tooling-freeze-v002.json'
    write(output,dict(schema='Air-production-presentation-tooling-checker-dependency-freeze-v002',utc=datetime.now(timezone.utc).isoformat(),
        member_count=len(members),members=members,entry=pin(entry),derivative_of=pin(OLD_FREEZE),current_checker_freeze=pin(NEW_CHECKER),
        current_checker=checker['checker_pin'],current_protocol=checker['protocol_pin'],
        old_6a42_immutable=True,source_probe_be6_not_modified=True,exact_dependency_only=True,
        two_SHA_verification_passes=2,mismatches=0,no_new_source_or_native_or_media_execution=True,UE_started=False,View=False,FinalAccepted=False))
    print(json.dumps(dict(freeze=pin(output),members=len(members),entry=pin(entry),current_checker_freeze=pin(NEW_CHECKER),UE_started=False,View=False,FinalAccepted=False)))


if __name__=='__main__':main()
