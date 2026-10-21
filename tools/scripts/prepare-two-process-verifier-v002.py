from pathlib import Path
import hashlib,importlib.util,json
R=Path('F:/Ourgame');T=R/'tools/scripts';E=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/two-process-verifier-correction-v002'
assert not E.exists();E.mkdir()
p=T/'verify-run-pristine-two-process-v001.py';q=T/'verify-run-pristine-two-process-v002.py';assert not q.exists()
s=p.read_text(encoding='utf-8')
anchor='def f64(bits):'
assert s.count(anchor)==1
helper='''def codec_guid(value):
    require(isinstance(value, dict) and set(value) == {"A", "B", "C", "D"}, "Not canonical native FGuid words")
    words = [uint(value[key]) for key in ("A", "B", "C", "D")]
    require(all(word <= 0xffffffff for word in words), "FGuid uint32 overflow")
    return guid("".join(f"{word:08x}" for word in words))


'''
s=s.replace(anchor,helper+anchor)
old='guid(envelope["runGuid"]) == guid(saved["RunGuid"])';new='guid(envelope["runGuid"]) == codec_guid(saved["RunGuid"])'
assert s.count(old)==1;s=s.replace(old,new);q.write_text(s,encoding='utf-8')
p=T/'verify-run-pristine-two-process-v001.ps1';qps=T/'verify-run-pristine-two-process-v002.ps1';assert not qps.exists()
s=p.read_text(encoding='utf-8');assert s.count('verify-run-pristine-two-process-v001.py')==1
qps.write_text(s.replace('verify-run-pristine-two-process-v001.py','verify-run-pristine-two-process-v002.py'),encoding='utf-8')
spec=importlib.util.spec_from_file_location('native_guid_verifier',q);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
session=R/'UnrealGame/Saved/RunPristineProofs/20261016-163146-native-two-process-v001'
doc=json.loads((session/'source/source-codec.json').read_text(encoding='utf-8'))
profile=json.loads((session/'two-process-session.json').read_text(encoding='utf-8'))
bundlepath=Path(profile['profiles_directory'])/profile['profile_id']/'slot-A.bundle.json'
bundle=json.loads(bundlepath.read_text(encoding='utf-8'))
assert mod.codec_guid(doc['snapshot']['RunGuid'])==mod.guid(bundle['payload']['runGuid'])
cases=[{}, {'A':'0','B':'0','C':'0','D':'0'}, {'A':'4294967296','B':'1','C':'1','D':'1'},
       {'A':True,'B':'1','C':'1','D':'1'}, {'A':'01','B':'1','C':'1','D':'1'},
       {'A':'1','B':'1','C':'1','D':'1','E':'1'}]
for bad in cases:
    try: mod.codec_guid(bad)
    except ValueError: pass
    else: raise AssertionError('Malformed native FGuid accepted: '+str(bad))
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(E/'correction-check-v002.json').write_text(json.dumps({'old_session_preserved_failed':session.as_posix(),
    'actual_failure':'Both native roles exited0, original verifier raised AttributeError on native FGuid {A,B,C,D}. This was verifier schema error, not a game semantic RED.',
    'local_native_source':'DungeonRunSnapshotCodec.cpp Fields(FGuid&) writes four canonical uint32 word strings; native ToString Digits concatenates A/B/C/D in that order.',
    'actual_source_guid_matches_published_envelope':True,'malformed_guid_cases_rejected':len(cases),
    'new_verifier':desc(q),'new_coordinator':desc(qps),'Source_DLL_changed':False,'next':'Fresh version2 session/profile, no reuse or fallback',
    'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_verifier':desc(q),'new_coordinator':desc(qps),'actual_guid_match':True,'malformed_rejected':len(cases)},ensure_ascii=False))
