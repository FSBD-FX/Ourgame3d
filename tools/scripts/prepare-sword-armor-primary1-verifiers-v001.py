"""New bounded six-phase recording path; preserve old Ready-only verifiers."""
from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
def new(p,s):
 assert not p.exists(),p
 if p.suffix=='.py':compile(s,str(p),'exec')
 p.write_text(s,encoding='utf-8')
s=(T/'verify-sword-armor-ready-v001.py').read_text(encoding='utf-8-sig')
needle='armor_masks={-1:0,1:0}'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
primary_spec=importlib.util.spec_from_file_location('primary_checks',Path(__file__).with_name('ue_sword_armor_primary1_v001_checks.py'))
primary_checks=importlib.util.module_from_spec(primary_spec);primary_spec.loader.exec_module(primary_checks)
primary_manifest=primary_checks.preflight(require_unused=False)
primary_by_phase={(row['component'],row['frame']):row['object_path'] for row in primary_manifest['assets']}
primary_masks={-1:0,1:0}''')
s=s.replace("'actual_imported':34,'armor24_imported':True,'old917_unchanged':True", "'actual_imported':76,'Ready24_imported':True,'Primary42_imported':True,'old941_unchanged':True")
old="""        assert not d['armor_ready'] and not d['armor_drawn'],'Ready armor must never be applied to an attack'
        assert d['draw_stack']==[d['texture'],d['weapon'],d['texture']]"""
assert s.count(old)==1
s=s.replace(old,"""        assert d['armor_ready'] and d['armor_drawn']
        expected=[primary_by_phase[(component,d['frame'])] for component in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground']]+[d['weapon'],primary_by_phase[('NearHand',d['frame'])]]
        assert d['draw_stack']==expected,'Actual Primary1 stack/phase/source mismatch'
        primary_masks[d['facing']]|=1<<d['frame']""")
s=s.replace('assert len(runs)==1','assert primary_masks=={-1:63,1:63},primary_masks\nassert len(runs)==1')
s=s.replace("'old917_packages_unchanged':True", "'old941_packages_unchanged':True,'Primary42_actual_imported':True,'actual_Primary_armor_masks':primary_masks,'Primary_stack_exact':True")
s=s.replace("'scope':'Actual Ready-only chest/shoulder24 render stack and real Enter/A/J. Attack intentionally lacks new armor; fullstate fit, equipment IDs, thumb, fullcombos and audio remain unaccepted'", "'scope':'Actual Ready7/Primary1-eight layer stacks and source-bound both-facing normal Enter/A/J/kernel phases. Matching candidate armor only; real equipment IDs, thumb, allstates/fullcombos, fullmotion and audio remain unaccepted'")
s=s.replace("'sword-armor-runtime-verification.json'","'sword-armor-primary1-runtime-verification.json'")
new(T/'verify-sword-armor-primary1-v001.py',s)
head=(T/'verify-ready-body-pixel-presence-v001.py').read_text(encoding='utf-8-sig')
head=head.replace("d['clip']!='sword_ready_idle'", "d['clip'] not in ['sword_ready_idle','sword_primary_1']")
head=head.replace("'phase':d['frame']", "'clip':d['clip'],'phase':d['frame']")
head=head.replace("{(x['facing'],x['phase']) for x in checks}=={(s,i) for s in [-1,1] for i in range(4)}", "{(x['facing'],x['clip'],x['phase']) for x in checks}=={(s,c,i) for s in [-1,1] for c,n in [('sword_ready_idle',4),('sword_primary_1',6)] for i in range(n)}")
head=head.replace('visible-ready-head-gate-v001.json','visible-ready-primary-head-gate-v001.json').replace('bell-helmet-ready-visible-pixel-gate-v1','bell-helmet-ready-primary-visible-pixel-gate-v1').replace('checked_Ready_observations','checked_supported_observations')
new(T/'verify-ready-primary-body-pixel-presence-v001.py',head)
ps=(T/'verify-sword-armor-ready-v002.ps1').read_text(encoding='utf-8-sig')
ps=ps.replace('[int]$Version=2','[int]$Version=1').replace('verify-sword-armor-ready-v001.py','verify-sword-armor-primary1-v001.py').replace('_钟盔军剑低位胸肩真实按键试装_v','_钟盔军剑首斩穿甲真实按键试装_v').replace("'-DungeonFairytaleSwordArmorReadyPreview'","'-DungeonFairytaleSwordArmorPrimary1Preview'")
ps=ps.replace('verify-ready-body-pixel-presence-v001.py','verify-ready-primary-body-pixel-presence-v001.py')
ps=ps.replace('158Ready/159Primary1 real Enter/A/J with161/162/163 Ready-only armor. No attack armor or actual equipment identity, hit/three-stage/thumb/fullmotion/audio acceptance.','158Ready4/159Primary1six with matching native161/162/163Ready armor and164/165/167Primary1armor. Candidate only; actual equipment identity, hit/three-stage/thumb/fullmotion/audio acceptance remain unfinished.')
new(T/'verify-sword-armor-primary1-v001.ps1',ps)
launch=(T/'launch-fairytale-sword-armor-ready-v001.ps1').read_text(encoding='utf-8-sig')
launch=launch.replace('verify-sword-armor-ready-v001.py','verify-sword-armor-primary1-v001.py').replace('play-fairytale-sword-armor-ready-v001-','play-fairytale-sword-armor-primary1-v001-').replace('-DungeonFairytaleSwordArmorReadyPreview','-DungeonFairytaleSwordArmorPrimary1Preview')
launch=launch.replace('Ready-only chest and shoulders preview started:','Ready and first-cut chest/shoulders preview started:').replace('Imported Ready armor24 trial preflight failed.','Imported matching armor trial preflight failed.')
launch=launch.replace('Chest and shoulders are trial Ready-only layers. They disappear during attack because matching attack armor is unfinished. Other states remain placeholders; real equipment IDs, complete states and combos are unfinished.','Chest and shoulders cover four Ready and six first-cut phases. Other states/second and third combo stages remain placeholders; actual equipment IDs/full motion are unfinished.')
new(T/'launch-fairytale-sword-armor-primary1-v001.ps1',launch)
new(R/'钟盔军剑首斩穿甲试装.cmd','@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\\scripts\\launch-fairytale-sword-armor-primary1-v001.ps1"\r\n')
print('Prepared distinct Primary1 check/capture/launcher tools; no UE invocation or acceptance.')
