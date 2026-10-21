"""Read-only source proposal/API boundaries; --against-current only before admit."""
from pathlib import Path
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((HERE/'exact-seams.json').read_text());before=(HERE/m['local_before']).read_bytes();after=(HERE/m['projected_source']).read_bytes()
assert (len(before),sha(before))==(m['source_bytes'],m['source_sha256'])
assert (len(after),sha(after))==(m['result_bytes'],m['result_sha256'])
if '--against-current' in sys.argv:assert Path(m['actual_source']).read_bytes()==before,'Actual before source drift; never overwrite'
nl='\r\n' if m['line_ending']=='CRLF' else '\n';text=before.decode()
for op in m['operations']:
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(a)==1;text=text.replace(a,b,1)
assert text.encode()==after
for op in reversed(m['operations']):
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(b)==1;text=text.replace(b,a,1)
assert text.encode()==before,'Original code byte roundtrip failed'
old=before.decode().replace('\r\n','\n');new=after.decode().replace('\r\n','\n')
# The complete strict capture lambda, all old115/new14 scans and completion gate stay exact.
capture='  IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);'
end='void Observe(ADungeonHeroLandingPriorityProbeV001& Actor)'
assert old[old.index(capture):old.index(end)]==new[new.index(capture):new.index(end)]
added='\n'.join(op['after'].replace(op['before'],'',1) for op in m['operations'])
for name in ('FinishAllCompilation','UpdateResource','FinishCachePlatformData','PlaySound2D','InputKey','StartJump','TryBeginDodge','SetActorLocation','SetGamePaused','Need','BeginStop'):
 assert re.search(r'\b'+name+r'\s*\(',added) is None,('Forbidden additional mutation/control/gate',name)
for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
# Public API declarations used here, read from installed UE5.5 source; not a UE build.
engine=Path('G:/UE_5.5/Engine/Source/Runtime')
for path,needle in (
 ('Engine/Public/TextureCompiler.h','FinishCompilation(TArrayView<UTexture* const> InTextures);'),
 ('Engine/Classes/Engine/Texture.h','bool IsAsyncCacheComplete() const;'),
 ('Engine/Classes/Engine/Texture.h','virtual bool IsCompiling() const override'),
 ('Engine/Public/TextureResource.h','virtual bool IsProxy() const'),
 ('RenderCore/Public/RenderResource.h','bool IsInitialized() const')):
 assert needle in (engine/path).read_text(encoding='utf-8-sig'),path
print(json.dumps(dict(insert_operations=len(m['operations']),exact_original_byte_roundtrip=True,old115_plus14_strict_capture_byte_unchanged=True,api_declarations_verified=5,actual_before_checked='--against-current' in sys.argv,actual_source_written=False,UE_run=False)))
