"""Candidate-only source/patch preparation. Never writes an actual project path."""
from pathlib import Path
import hashlib, json, difflib, re, datetime

HERE = Path(__file__).resolve().parent
ROOT = Path('F:/Ourgame')
BASE = ROOT / 'source-assets/production/backups/v140-Dodge196G/compiled-source-manifest.json'
ART = ROOT / 'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/Move7-profile-preparation-v001/GuardMove7-runtime-profile-candidate-v001.json'
FINAL = HERE / 'Move7-stage0-freeze-v001.json'
assert not FINAL.exists(), 'Frozen Stage0 is immutable; create a new candidate version instead.'

def pin(path):
    data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

def put(path, data):
    assert path.resolve().is_relative_to(HERE)
    assert not path.exists(), f'Candidate output already exists: {path}'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def dump(path, obj):
    put(path, (json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode())

baseline = json.loads(BASE.read_text(encoding='utf-8'))
assert pin(BASE)['sha256'] == 'c3bae7da14020ededd624bb2bc9469f322d60ff3189dda4b9e0f865eb1fa2778'
old_sources = [f for f in baseline['files'] if f['path'].startswith('UnrealGame/Source/')]
assert len(old_sources) == 273
passes = []
for pass_id in (1,2):
    mismatch=[]
    for frozen in old_sources:
        actual=pin(ROOT/frozen['path'])
        if any(actual[k] != frozen[k] for k in ('bytes','sha256')):
            mismatch.append(dict(expected=frozen, actual=actual))
    assert not mismatch, mismatch
    passes.append(dict(pass_id=pass_id, source_count=273, differences=0))

# All exact source hashes and all18 point/RGBA values come from the frozen art
# profile as an independent test oracle, not from the future C++ Profile().
profile=json.loads(ART.read_text(encoding='utf-8'))
assert pin(ART)['sha256']=='03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51'
sources=profile['source7']
quoted=lambda value:'TEXT('+json.dumps(value)+')'
lines=[]
for name,field in [('ExpectedPNG','source'),('ExpectedRGBA','RGBA_sha256'),('ExpectedPaths','texture_object_path')]:
    values=[s[field]['sha256'] if field=='source' else s[field] for s in sources]
    lines.append(' const TCHAR* '+name+'[]={'+','.join(map(quoted,values))+'};')
markers=[(name,value) for s in sources for name,value in s['artist_surface_markers'].items()]
assert len(markers)==18
lines.append(' const TCHAR* ExpectedMarkerNames[]={'+','.join(quoted(name) for name,_ in markers)+'};')
lines.append(' const FVector2D ExpectedPoints[]={'+','.join('FVector2D('+','.join(map(str,v['xy']))+')' for _,v in markers)+'};')
lines.append(' const FColor ExpectedColors[]={'+','.join('FColor('+','.join(map(str,v['actual_RGBA']))+')' for _,v in markers)+'};')
lines += [' int32 MarkerIndex=0;for(int32 Index=0;Index<7;++Index)',
 ' {const auto& S=P.Sources[Index];TestTrue(TEXT("Every exact component identity, path and original PNG/RGBA hash remains frozen"),S.Component==M::EComponent(Index)&&S.TexturePath==ExpectedPaths[Index]&&S.SourceSHA256==ExpectedPNG[Index]&&S.SourceRGBASHA256==ExpectedRGBA[Index]);',
 ' for(const auto& A:S.Markers){TestTrue(TEXT("Every artist18 source name, opaque RGBA and exact surface coordinate remains frozen"),A.Name==ExpectedMarkerNames[MarkerIndex]&&A.Point==ExpectedPoints[MarkerIndex]&&A.SurfaceRGBA==ExpectedColors[MarkerIndex]);++MarkerIndex;}}']
testpath=HERE/'new/Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp'
tests=testpath.read_text(encoding='utf-8')
assert tests.count('// EXACT_SOURCE_ORACLE_INSERTED_HERE')==1
tests=tests.replace(' // EXACT_SOURCE_ORACLE_INSERTED_HERE','\n'.join(lines))
testpath.write_text(tests,encoding='utf-8',newline='\n')

replacements={}
def narrow(filename, transforms):
    source=ROOT/'UnrealGame/Source/CodexDungeon'/filename
    old=source.read_bytes();new=old
    newline=b'\r\n' if b'\r\n' in old else b'\n'
    for before,after in transforms:
        before=before.replace(b'\n',newline);after=after.replace(b'\n',newline)
        assert new.count(before)==1,(filename,before)
        new=new.replace(before,after)
    assert new!=old
    put(HERE/'before'/filename,old)
    put(HERE/'replacements'/filename,new)
    diff=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),
        fromfile='a/UnrealGame/Source/CodexDungeon/'+filename,tofile='b/UnrealGame/Source/CodexDungeon/'+filename))
    put(HERE/'patches'/(filename+'.patch'),diff.encode())
    replacements[filename]=dict(actual_path=source.as_posix(), before=pin(HERE/'before'/filename), after=pin(HERE/'replacements'/filename), patch=pin(HERE/'patches'/(filename+'.patch')))

narrow('DungeonFighter.h',[
 (b'#include "DungeonDodgePresentation.h"\n',b'#include "DungeonDodgePresentation.h"\n#include "DungeonGuardMovePresentation.h"\n'),
 (b'    bool QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const;\n',b'    bool QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const;\n    // Actual Guard-only completed Move facts; read-only and atomic.\n    bool QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const;\n')])
narrow('DungeonFighter.cpp',[
 (b'bool ADungeonFighter::QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const\n',b'bool ADungeonFighter::QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const\n{\n    (void)Out; // Stage0 semantic RED: no fabricated witness or caller mutation.\n    return false;\n}\n\nbool ADungeonFighter::QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const\n')])
narrow('DungeonHUD.h',[
 (b'#include "DungeonFairytaleGuardFullDrawStateV003.h"\n',b'#include "DungeonFairytaleGuardFullDrawStateV003.h"\n#include "DungeonFairytaleGuardMoveDrawStateV001.h"\n'),
 (b'    bool IsFairytaleGuardStompPreviewEnabled() const { return bUseFairytaleGuardStompPreview; }\n',b'    bool IsFairytaleGuardStompPreviewEnabled() const { return bUseFairytaleGuardStompPreview; }\n    const TArray<FDungeonFairytaleGuardMoveRigDrawV001>& GetFairytaleGuardMoveRigDraws() const { return FairytaleGuardMoveRigDraws; }\n    bool IsFairytaleGuardMoveRigPreviewEnabled() const { return bUseFairytaleGuardMoveRigPreview; }\n'),
 (b'    bool bUseFairytaleGuardStompPreview=false;\n',b'    bool bUseFairytaleGuardStompPreview=false;\n    bool bUseFairytaleGuardMoveRigPreview=false;\n    uint64 FairytaleGuardMoveRigDrawSerial=0;\n    TArray<FDungeonFairytaleGuardMoveRigDrawV001> FairytaleGuardMoveRigDraws;\n')])

names=re.findall(r'"(CodexDungeon\.Content\.FairytaleGuardMoveRigV001\.[^"]+)"',tests)
assert names==['CodexDungeon.Content.FairytaleGuardMoveRigV001.RealCompletedGuardOwnerAndAcceptedPath',
 'CodexDungeon.Content.FairytaleGuardMoveRigV001.FixedSurfaceRigSingleMirrorAndFiniteBounds',
 'CodexDungeon.Content.FairytaleGuardMoveRigV001.AtomicSevenResourcesAndLegacyIsolation']
assert tests.count('TARGET Stage0 RED:')==3
new_files=sorted((HERE/'new').rglob('*'))
new_files=[p for p in new_files if p.is_file()]
assert len(new_files)==5
for path in new_files:
    assert not (ROOT/'UnrealGame/Source/CodexDungeon'/path.relative_to(HERE/'new')).exists()
dump(HERE/'exact-beforepins-v001.json',dict(baseline=pin(BASE),source_verification_passes=passes,
    all_old_sources=old_sources,modified_existing=replacements,original_196_test_sources_byte_identical=True))
all_files=sorted(p for p in HERE.rglob('*') if p.is_file() and p!=FINAL)
manifest=dict(schema='Guard-Move7-Stage0-stub-and-semantic-tests-freeze-v001',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    candidate_only=True,production_implementation_allowed=False,UE_build_run_performed=False,semantic_RED_observed=False,
    required_actual_result=dict(registered=199,old_passes=196,new_failures=3,errors_per_new_group=1,expected_error_prefix='TARGET Stage0 RED:'),
    baseline=pin(BASE),baseline_sources=273,added_sources=5,expected_stage0_sources=278,existing_source_mutations=3,
    tests=names,new_sources=[dict(candidate=pin(p),actual_path=(ROOT/'UnrealGame/Source/CodexDungeon'/p.relative_to(HERE/'new')).as_posix()) for p in new_files],
    existing_replacements=replacements,profile=pin(ART),source_verification_passes=passes,
    boundaries=['No actual Source/Content/tools/ledger/E mutation','No UE launch/build/commit','No HUD.cpp or gameplay implementation',
     'No history sweep cause reconstruction; BlockKnown=false','No renderer or actual GPU-residency claim from pure metadata tests',
     'Actual UE semantic RED is a required separate Root step','Original18 opaque markers are surface registrations, not bones or alpha-core sole points'],
    files=[pin(p) for p in all_files])
dump(FINAL,manifest)
for pass_id in (1,2):
    for frozen in manifest['files']:
        assert pin(Path(frozen['path']))==frozen
print(json.dumps(dict(freeze=pin(FINAL),files=len(manifest['files']),new_sources=5,changed_existing=3,tests=names,old_source_passes=passes),ensure_ascii=False,indent=2))
