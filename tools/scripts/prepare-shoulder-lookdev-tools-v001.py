"""Create separate opt-in import/capture tools; preserve old chest tools exactly."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
def write(name,text):
 p=root/name;assert not p.exists();p.write_text(text,encoding='utf-8')
source=(root/'ue-import-fairytale-chest-lookdev-v001.py').read_text(encoding='utf-8')
source=source.replace('chest','shoulder').replace('Chest','Shoulder').replace('four','eight').replace('Four','Eight').replace('869','873')
# Only numeric arity literals are changed; native 512 canvas and Source pixels stay exact.
source=source.replace('"sources":4','"sources":8').replace('"expected_count":4','"expected_count":8').replace('==4','==8')
write('ue-import-fairytale-shoulder-lookdev-v001.py',source)
source=(root/'import-fairytale-chest-lookdev-v001.ps1').read_text(encoding='utf-8')
source=source.replace('chest','shoulder').replace('four','eight').replace('Four','Eight').replace('869','873').replace('-ne 4','-ne 8')
write('import-fairytale-shoulder-lookdev-v001.ps1',source)
source=(root/'verify-fairytale-chest-lookdev.ps1').read_text(encoding='utf-8')
source=source.replace('chest','shoulder').replace('Chest','Shoulder').replace('four','eight').replace('Four','Eight').replace('-ne 4','-ne 8')
source=source.replace('暗黑童话胸甲明暗双向真实观察','暗黑童话双肩甲明暗双向真实观察')
source=source.replace("'-DungeonFairytaleShoulderLookdev',","'-DungeonFairytaleChestLookdev','-DungeonFairytaleShoulderLookdev',")
source=source.replace('147 eight-source isolated hero shoulder on/off at light/dark anchors plus original stone4idle; fixed presentation anchors/scale, normal A/D display facing, inert gameplay inputs.',
 '149near4 and150far4 on actual147chest: eight bright/dark/facing/both-on-off combinations plus four isolated-shoulder facing combinations; fixed72px presentation and inert gameplay inputs.')
write('verify-fairytale-shoulder-lookdev.ps1',source)
source=(root/'verify-fairytale-chest-lookdev.py').read_text(encoding='utf-8')
source=source[:source.index('\ndef main():')]
source=source.replace('def validate(report,manifest):','def validate(report,manifest,shoulders):')
source=source.replace("'fairytale_chest_observation_silent_v001'","'fairytale_shoulder_observation_silent_v001'")
source=source.replace('len(rows)==len(offsets)>=300','len(rows)==len(offsets)>=700').replace('11.2<=duration<=12.0','25.2<=duration<=27.0')
source=source.replace('combinations={(dark,chest,side):0 for dark in (False,True) for chest in (False,True) for side in (-1,1)}',
 "combinations={(dark,visible,side,'both'):0 for dark in (False,True) for visible in (False,True) for side in (-1,1)}\n    combinations.update({(False,True,side,only):0 for side in (-1,1) for only in ('near','far')})")
source=source.replace("and row['hero_chest_active'] and not row['hero_walk_active']","and row['hero_chest_active'] and row['hero_shoulder_active'] and not row['hero_walk_active']")
source=source.replace("a['chest_drawn']==row['input_C']","a['chest_drawn']")
source=source.replace("k=(row['hero_dark_position'],row['chest_visible_choice'],side);combinations[k]|=1<<frame",'''require(row['near_shoulder_only']==row['input_N'] and row['far_shoulder_only']==row['input_F'] and not (row['input_N'] and row['input_F']),'Wrong isolated controls')
                for shoulder in ('near','far'):
                    asset=next(v for v in shoulders['assets'] if v['side'].lower()==shoulder and v['frame']==frame)
                    expected_drawn=row['input_C'] and not (row['input_N'] and shoulder=='far') and not (row['input_F'] and shoulder=='near')
                    require(a[shoulder+'_shoulder_ready'] and a[shoulder+'_shoulder_path']==asset['object_path'] and a[shoulder+'_shoulder_drawn']==expected_drawn,'Missing/wrong actual separate shoulder source')
                only='near' if row['input_N'] else 'far' if row['input_F'] else 'both'
                k=(row['hero_dark_position'],row['chest_visible_choice'],side,only);require(k in combinations,'Unexpected display combination');combinations[k]|=1<<frame''')
source=source.replace("else:require(not a['chest_texture_ready'] and not a['chest_drawn'] and not a['chest_path'],'Chest incorrectly applied to monster')",'''else:
                require(not a['chest_texture_ready'] and not a['chest_drawn'] and not a['chest_path'],'Chest incorrectly applied to monster')
                require(all(not a[k] for k in ('near_shoulder_ready','far_shoulder_ready','near_shoulder_drawn','far_shoulder_drawn','near_shoulder_path','far_shoulder_path')),'Shoulders incorrectly applied to monster')''')
source=source.replace('all(v>=1 for v in wraps.values())','all(v>=2 for v in wraps.values())').replace('eight display combinations','twelve display combinations')
source=source.replace("'LeftShift'):","'LeftShift','N','F'):").replace("'eight_combination_masks'","'twelve_combination_masks'")
source+='''
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',default='');p.add_argument('--manifest',required=True);p.add_argument('--preflight-only',action='store_true');args=p.parse_args()
    require(hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA,'Native pixel auditor changed')
    native=load('shoulder_lossless_native_audit',BASE)
    chest=load('shoulder_actual_chest_sources',Path(__file__).with_name('ue_fairytale_chest_lookdev_checks.py'))
    checks=load('shoulder_frozen_sources',Path(__file__).with_name('ue_fairytale_shoulder_lookdev_checks.py'))
    require(Path(args.manifest).resolve()==checks.MANIFEST.resolve(),'Wrong manifest')
    manifest=chest.preflight(require_unused=False);shoulders=checks.preflight(require_unused=False)
    native.validate_manifest(checks.ROOT/'source-assets/production/fairytale-lookdev-v001/manifests/import-lookdev-v001.json')
    if args.preflight_only:print(json.dumps({'source_preflight':True,'source_PNGs':8,'old_packages_unchanged':873}));return
    require(bool(args.archive),'Actual archive required');archive=Path(args.archive).resolve();report_path=archive/'原件/runtime-report.json';report=json.loads(report_path.read_text(encoding='utf-8-sig'))
    print(json.dumps({'schema':'fairytale-shoulder-lookdev-runtime-audit-v1','passed':True,**validate(report,manifest,shoulders),**native.validate_native(archive,report),'manifest_sha256':checks.MANIFEST_SHA,'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'motion_reviewed':False,'runtime_gameplay_identity_installed':False,'formal_complete_units':0},ensure_ascii=False))
if __name__=='__main__':main()
'''
write('verify-fairytale-shoulder-lookdev.py',source)
print(json.dumps({'created':5,'old_tools_modified':False}))
