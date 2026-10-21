"""Create separate trial verifiers; preserve the prior unarmored recording path."""
from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
def new(p,s):
 assert not p.exists(),p
 if p.suffix=='.py':compile(s,str(p),'exec')
 p.write_text(s,encoding='utf-8')
s=(T/'verify-fairytale-sword-body-v002.py').read_text(encoding='utf-8-sig')
s=s.replace("manifest=checks.preflight(require_unused=False)","""manifest=checks.preflight(require_unused=False)
armor_spec=importlib.util.spec_from_file_location('armor_checks',Path(__file__).with_name('ue_sword_armor_ready_v001_checks.py'))
armor_checks=importlib.util.module_from_spec(armor_spec);armor_spec.loader.exec_module(armor_checks)
armor_manifest=armor_checks.preflight(require_unused=False)
armor_by_phase={(row['component'],row['frame']):row['object_path'] for row in armor_manifest['assets']}
armor_masks={-1:0,1:0}""")
s=s.replace("'actual_imported':10,'old907_unchanged':True", "'actual_imported':34,'armor24_imported':True,'old917_unchanged':True")
s=s.replace("assert not d['weapon'] and len(d['draw_stack'])==1", "assert not d['weapon'] and len(d['draw_stack'])==1 and d['armor_preview'] and not d['armor_drawn'] and not d['armor_ready']")
s=s.replace("assert d['draw_stack']==[d['texture'],d['weapon'],d['texture']]", """assert d['armor_preview']
    if clip=='Ready':
        assert d['armor_ready'] and d['armor_drawn']
        expected=[armor_by_phase[(component,d['frame'])] for component in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear']]+[d['weapon'],armor_by_phase[('NearHand',d['frame'])]]
        assert d['draw_stack']==expected,'Actual Ready stack/phase/source mismatch'
        armor_masks[d['facing']]|=1<<d['frame']
    else:
        assert not d['armor_ready'] and not d['armor_drawn'],'Ready armor must never be applied to an attack'
        assert d['draw_stack']==[d['texture'],d['weapon'],d['texture']]""")
s=s.replace("assert len(runs)==1", "assert armor_masks=={-1:15,1:15},armor_masks\nassert len(runs)==1")
s=s.replace("'old907_packages_unchanged':True", "'old917_packages_unchanged':True,'armor24_actual_imported':True,'actual_armor_masks':armor_masks,'Ready_stack_exact':True,'attack_armor_is_not_faked':True")
s=s.replace("'scope':'Actual normal-input render path only; hit timing, armor, thumb, fullstates/combos and audio remain unaccepted'", "'scope':'Actual Ready-only chest/shoulder24 render stack and real Enter/A/J. Attack intentionally lacks new armor; fullstate fit, equipment IDs, thumb, fullcombos and audio remain unaccepted'")
s=s.replace("'sword-runtime-verification.json'","'sword-armor-runtime-verification.json'")
new(T/'verify-sword-armor-ready-v001.py',s)
ps=(T/'verify-fairytale-sword-body-v002.ps1').read_text(encoding='utf-8-sig')
ps=ps.replace('verify-fairytale-sword-body-v002.py','verify-sword-armor-ready-v001.py').replace('_钟盔军剑低位真实按键双向动作_v','_钟盔军剑低位胸肩真实按键试装_v')
ps=ps.replace("'-DungeonFairytaleSwordBodyV002Preview'","'-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorReadyPreview'")
ps=ps.replace('158Ready/159Primary1 only, real Enter/A/J. No armor/hit/three-stage/thumb or fullmotion acceptance.','158Ready/159Primary1 real Enter/A/J with161/162/163 Ready-only armor. No attack armor or actual equipment identity, hit/three-stage/thumb/fullmotion/audio acceptance.')
new(T/'verify-sword-armor-ready-v001.ps1',ps)
print('Prepared two new verifiers; no capture or old-file edits')
