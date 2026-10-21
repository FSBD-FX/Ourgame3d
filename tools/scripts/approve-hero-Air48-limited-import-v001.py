"""Root verifies actual prepared48/ZIP/source closure and authorizes import only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
from PIL import Image
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/native-ready-candidate-v001';O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/Root-Air48-limited-import-v001';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(x,base=R):
 p=Path(x['path']);p=p if p.is_absolute() else base/p;assert (p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),p;return p
freeze=C/'Air48-native-ready-freeze-v001.json';manifest=C/'import-Air48-v001.json';closure=C/'Air49-source-closure-canonical-v001.json';data=C/'new-source/DungeonFairytaleSwordAirDataV001.inl'
assert pin(freeze)['sha256']=='e3786b74ac2292479780368531a99ebc097ec8df3c70629d8168a39ff75dfea7'
assert pin(manifest)['sha256']=='1cd238d89d6e897616e12ce74066d25203614afd3e006059c0bcb0643fc5f32c'
assert pin(closure)['sha256']=='5df0479bd1689b8adeb525255e748db13288839bbc1b8523f7ec012f404bdaec'
assert pin(data)['sha256']=='a0b179e2132674e0bad302809802ff2a68b5e9d486909762fdb322213a896191'
for _ in range(2):
 for x in read(freeze)['members']:check(x,C)
m=read(manifest);ns='/Game/Production/ArtTrials/EV048/v020/HeroLeatherAir6';assert m['namespace']==ns and m['asset_count']==48 and len(m['assets'])==48
components=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand'];assert [(x['frame'],x['component']) for x in m['assets']]==[(f,c) for f in range(6) for c in components]
assert len({x['source'] for x in m['assets']})==len({x['object_path'] for x in m['assets']})==48
assert not (R/'UnrealGame/Content/Production/ArtTrials/EV048/v020').exists()
packet=None;z=None
try:
 for x in m['assets']:
  p=Path(x['source']);assert p.is_relative_to(C/'sources48') and pin(p)['sha256']==x['source_sha256'] and p.stat().st_size==x['source_bytes'] and not x['known_optional_empty']
  im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512) and hashlib.sha256(im.tobytes()).hexdigest()==x['source_RGBA_sha256'];used=sum(v>0 for v in im.getchannel('A').getdata());assert used==x['source_alpha_nonzero_pixels']>0
  assert p.read_bytes()==check(x['source_origin']).read_bytes()
  retained=x['retention'];ep=check(retained['E_packet']);check(retained['E_index'])
  if packet is None:packet=ep;z=zipfile.ZipFile(ep);assert z.testzip() is None
  assert ep==packet;member=z.read(retained['E_member']);assert len(member)==retained['E_member_bytes'] and hashlib.sha256(member).hexdigest()==retained['E_member_sha256']==x['source_sha256'] and member==p.read_bytes()
finally:
 if z:z.close()
for f in range(6):
 assert f'F.Frame={f};' in data.read_text(encoding='utf-8')
assert 'F.Root={244,530};' in data.read_text(encoding='utf-8') and 'P.SourceClosureVerified=true;' in data.read_text(encoding='utf-8')
cm=R/'source-assets/production/backups/v142-HeroAir6-Baseline292-200G3R-v001/compiled-source-manifest.json';assert pin(cm)['sha256']=='4f55684c044c1b5fde8edf0a1b7f378d22e16e9a87b7407ee878c6552e2fb85d'
for x in read(cm)['files']:
 if x['path'].startswith('UnrealGame/Source/') or x['path'].startswith('UnrealGame/Content/Production/'):check(x)
O.mkdir(parents=True)
approval=dict(schema='Root-Air48-limited-source-import-approval-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,limited_import_approved=True,is_template=False,source_manifest=pin(manifest),candidate_freeze=pin(freeze),source_closure=pin(closure),source_closure_digest=pin(closure)['sha256'],namespace=ns,expected_old_count=1371,expected_new_count=48,expected_final_count=1419,old_compiled_snapshot=pin(cm),actual_prepared48_RGBA_and_E599_bytes_verified=True,typed_data=pin(data),E600_actual_retention=pin(Path('E:/OurGame/Knight/过程图稿与视频/2026-10-19-本项目E600-钟盔Air253四十八源原生准备-v001/E-retention-index-v001.json')),Root_viewed_source_fit='E599 full6, torso4x, display72; E596 complete helmet and rejected Land4=25deg boot overlap preserved. FinalLand4[1,.2] is explicit artist override.',remaining_risks=['Apex jerkin hem and tucked knees','hard takeoff/landing pose changes and original Ready join','artist roots/grips/axes are not measured bones/feet/hilt','actual49GPU/None6-LGT9/left-right pixels and native priorities/restore still unverified'],approval_scope='Only exact new48 Texture2D files in unused namespace; no new sword/whole texture, gameplay change or final acceptance.',TrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
p=O/'Root-source-approval-v001.json';p.write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(success=True,approval=pin(p),new48_host_verified=True,actual_import_started=False),ensure_ascii=False))
