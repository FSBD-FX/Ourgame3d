from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;BIND=HERE.parent/'UE-import-binding-candidate-v001';SRC=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon');sha=lambda b:hashlib.sha256(b).hexdigest()
freeze=BIND/'candidate-freeze-v001.json';assert sha(freeze.read_bytes())=='eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9'
members={r['path']:r for r in json.loads(freeze.read_text(encoding='utf-8'))['members']}
for rel in ['source/expected-two-frame-draws-v001.json','import/import-manifest-v001.json']:
 p=BIND/rel;b=p.read_bytes();m=members[str(p).replace('\\','/')];assert sha(b)==m['sha256'] and len(b)==m['bytes'];(HERE/'before'/p.name).write_bytes(b)
contract=json.loads((BIND/'source/expected-two-frame-draws-v001.json').read_text(encoding='utf-8'));manifest=json.loads((BIND/'import/import-manifest-v001.json').read_text(encoding='utf-8'));assets=manifest['assets'];assert len(assets)==14
expected={p for f in contract['frames'] for i,p in enumerate(f['draw_stack']) if i!=6};assert {r['object_path'] for r in assets}==expected
for row in assets:
 p=Path(row['source']['path']);b=p.read_bytes();assert len(b)==row['source']['bytes'] and sha(b)==row['source']['sha256']
def literal(s):return 'TEXT('+json.dumps(s,ensure_ascii=False)+')'
rows=[]
for r in assets:rows.append(' {'+str(r['frame'])+','+','.join([literal(r['component']),literal(r['object_path']),literal(r['source']['path']),str(r['source']['bytes'])+'ULL',literal(r['source']['sha256'])])+'},')
helper='''// Request258 immutable contract only; no loading, simulation or input.
bool Bridge258ObservationEnabled()
{
 FString RequestedAction;
 return FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytalePrimary1Bridge258Preview"))
  &&FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityAction="),RequestedAction)&&RequestedAction==TEXT("J");
}
struct FBridge258SourcePin{int32 Frame;const TCHAR* Component;const TCHAR* ObjectPath;const TCHAR* SourcePNG;uint64 SourceBytes;const TCHAR* SourceSHA256;};
const FBridge258SourcePin Bridge258SourcePins[]={
'''+ '\n'.join(rows)+'\n};\n'
(HERE/'fragments/helper.inc').write_text(helper,encoding='utf-8')
original=(SRC/'DungeonHeroLandingPriorityProbeV001.cpp').read_bytes();assert sha(original)=='e73bb9df5e3b95d1dcf16152e945f0efeb90ffc4c522a89b3c6a2d06cc71a422';(HERE/'before/DungeonHeroLandingPriorityProbeV001.cpp').write_bytes(original)
(HERE/'before/DungeonFairytaleSwordDrawState.h').write_bytes((SRC/'DungeonFairytaleSwordDrawState.h').read_bytes())
text=original.decode('utf-8').replace('\r\n','\n');brown=text[text.index('bool Brown('):text.index('JO DodgeDraw(')]
(HERE/'tests/brown-under-test.inc').write_text(brown,encoding='utf-8');(HERE/'tests/readback-under-test.inc').write_text('// Missing new opt-in readback for RED.\n',encoding='utf-8')
(HERE/'reports/source-contract-pins.json').write_text(json.dumps({'binding_freeze_sha256':sha(freeze.read_bytes()),'expected_draw_contract_sha256':sha((BIND/'source/expected-two-frame-draws-v001.json').read_bytes()),'source_png_count':len(assets),'source_png_total_bytes':sum(r['source']['bytes'] for r in assets),'baseline_probe_sha256':sha(original),'all_14_source_png_sha_size_match':True,'images_generated_or_viewed':0},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'contract_verified':True,'new_objects':14,'source_png_hashes':14,'baseline_probe_sha256':sha(original),'images_viewed':0}))
