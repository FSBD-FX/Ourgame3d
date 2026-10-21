from pathlib import Path
import difflib,hashlib,json
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent
CM=ROOT/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json'
assert hashlib.sha256(CM.read_bytes()).hexdigest()=='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
rel='UnrealGame/Source/CodexDungeon/DungeonHUD.cpp';data=(ROOT/rel).read_bytes();record=next(r for r in json.loads(CM.read_text(encoding='utf-8-sig'))['files'] if r['path']==rel)
assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
result=data;nl=b'\r\n' if b'\r\n' in data else b'\n'
for old,new in [
 ('#include "DungeonGuardMoveProbeV001.h"','#include "DungeonGuardMoveProbeV001.h"\n#include "DungeonHeroAirProbeV001.h"'),
 ('        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardMoveProofV001")))GetWorld()->SpawnActor<ADungeonGuardMoveProbeV001>();',
  '        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProofV001")))GetWorld()->SpawnActor<ADungeonHeroAirProbeV001>();\n        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardMoveProofV001")))GetWorld()->SpawnActor<ADungeonGuardMoveProbeV001>();')]:
    a=old.encode().replace(b'\n',nl);b=new.encode().replace(b'\n',nl);assert result.count(a)==1;result=result.replace(a,b,1)
target=BASE/'existing-source/DungeonHUD.cpp';target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(result)
diff=''.join(difflib.unified_diff(data.decode('utf-8-sig').splitlines(True),result.decode('utf-8-sig').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(BASE/'DungeonHUD.cpp.patch').write_text(diff,encoding='utf-8',newline='')
(BASE/'existing-before-pins.json').write_text(json.dumps({'schema':'HeroAir-baseline-HUD-before-pins-v001','compiled_manifest':str(CM.relative_to(ROOT)).replace('\\','/'),'compiled_manifest_sha256':hashlib.sha256(CM.read_bytes()).hexdigest(),'files':[{'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'candidate':'existing-source/DungeonHUD.cpp','after_bytes':len(result),'after_sha256':hashlib.sha256(result).hexdigest()}]},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'HUD_include_and_exclusive_spawn_only':True,'actual_source_written':False}))
