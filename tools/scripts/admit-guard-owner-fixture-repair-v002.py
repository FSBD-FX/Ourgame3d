from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-owner-v002/stage0-fixture-repair-v002';F=B/'fixture-repair-freeze-v002.json';O=R/'docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-fixture-repair-admission-v002';assert not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=json.loads(F.read_text(encoding='utf-8-sig'));assert desc(F)['sha256']=='91a57cc8d2963a51b48f7f77a353733642ae44d00f047d0ea1e517db39ad9615'
for x in v['files']:
 p=Path(x['path']);p=p if p.is_absolute() else B/p;d=desc(p);assert(d['bytes'],d['sha256'])==(x['bytes'],x['sha256'])
patch=B/'fixture-only-v002.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
src=R/'UnrealGame/Source/CodexDungeon/Tests/StoneGuardOwnerFixture_v002.h';before=desc(src);allbefore={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};O.mkdir(parents=True);shutil.copy2(src,O/src.name);assert src.read_bytes()==(O/src.name).read_bytes();subprocess.run(['git','apply',str(patch)],cwd=R,check=True);os.utime(src,None)
assert desc(src)['sha256']=='e1d605a51b8d89e58a63afd5ed2dcab524a6a01ba52380022c8b2e0ef5b77eb9';assert {p for p,d in allbefore.items() if desc(p)!=d}=={src}
(O/'admission.json').write_text(json.dumps(dict(freeze=desc(F),before=before,after=desc(src),only_fixture_changed=True,compiled=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Only fixture corrected; exact source-mtime refreshed; compile required.')
