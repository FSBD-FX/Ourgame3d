from pathlib import Path
import hashlib,json,difflib

ROOT=Path('F:/Ourgame')
BASE=Path(__file__).resolve().parent
SRC=ROOT/'UnrealGame/Source/CodexDungeon'
CM=ROOT/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json'
assert hashlib.sha256(CM.read_bytes()).hexdigest()=='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
PINS={r['path']:r for r in json.loads(CM.read_text(encoding='utf-8-sig'))['files']}

def patch(name,edits):
    original=(SRC/name).read_bytes()
    rel='UnrealGame/Source/CodexDungeon/'+name
    assert len(original)==PINS[rel]['bytes'] and hashlib.sha256(original).hexdigest()==PINS[rel]['sha256'],rel
    result=original
    nl=b'\r\n' if b'\r\n' in original else b'\n'
    for old,new in edits:
        a=old.encode().replace(b'\n',nl);b=new.encode().replace(b'\n',nl)
        assert result.count(a)==1,(name,old)
        result=result.replace(a,b,1)
    target=BASE/'existing-source'/name;target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),str(target)
    target.write_bytes(result)
    diff=''.join(difflib.unified_diff(original.decode('utf-8-sig').splitlines(True),result.decode('utf-8-sig').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
    (BASE/(name+'.patch')).write_text(diff,encoding='utf-8',newline='')
    return {'path':rel,'bytes':len(original),'sha256':hashlib.sha256(original).hexdigest(),'candidate':str(target.relative_to(BASE)).replace('\\','/'),'after_bytes':len(result),'after_sha256':hashlib.sha256(result).hexdigest()}

rows=[]
rows.append(patch('DungeonFighter.h',[
 ('#include "DungeonGuardMovePresentation.h"','#include "DungeonGuardMovePresentation.h"\n#include "DungeonHeroAirPresentation.h"'),
 ('    bool QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const;','    bool QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const;\n    // Completed actual hero H/V/landing-age facts only; no new clock/event/save field.\n    bool QueryHeroNonAttackAir(FDungeonHeroAirSample& Out) const;')]))
rows.append(patch('DungeonFighter.cpp',[
 ('bool ADungeonFighter::QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const',
  'bool ADungeonFighter::QueryHeroNonAttackAir(FDungeonHeroAirSample&) const\n{\n    // Stage0 semantic RED seam: leave Out untouched; do not infer from idle/Ready.\n    return false;\n}\n\nbool ADungeonFighter::QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const')]))
rows.append(patch('DungeonHUD.h',[
 ('#include "DungeonFairytaleSwordDodgeDrawState.h"','#include "DungeonFairytaleSwordDodgeDrawState.h"\n#include "DungeonFairytaleSwordAirDrawStateV001.h"'),
 ('    const FDungeonFairytaleSwordDodgeDraw& GetFairytaleSwordDodgeDraw() const { return FairytaleSwordDodgeDraw; }',
  '    const FDungeonFairytaleSwordDodgeDraw& GetFairytaleSwordDodgeDraw() const { return FairytaleSwordDodgeDraw; }\n    const FDungeonFairytaleSwordAirDrawV001& GetFairytaleSwordAirDraw() const { return FairytaleSwordAirDraw; }'),
 ('    FDungeonFairytaleSwordDodgeDraw FairytaleSwordDodgeDraw;',
  '    FDungeonFairytaleSwordDodgeDraw FairytaleSwordDodgeDraw;\n    FDungeonFairytaleSwordAirDrawV001 FairytaleSwordAirDraw; // Stage0 defaults: no Air renderer or submitted slot.')]))
(BASE/'existing-before-pins.json').write_text(json.dumps({'schema':'HeroAir-Stage0-existing-before-pins-v001','compiled_manifest':str(CM.relative_to(ROOT)).replace('\\','/'),'compiled_manifest_sha256':hashlib.sha256(CM.read_bytes()).hexdigest(),'files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'patched_candidates':len(rows),'actual_source_written':False}))
