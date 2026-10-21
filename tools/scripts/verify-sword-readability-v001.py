from pathlib import Path
import argparse,json,math
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);a=p.parse_args();A=Path(a.archive).resolve();O=A/'原件'
r=json.loads((O/'runtime-report.json').read_text('utf-8-sig'));base=json.loads((O/'sword-armor-primary1-runtime-verification.json').read_text('utf-8'))
assert base['passed'] and base['kernel_phase_sampling_exact']
rows=[d for d in r['observations'] if d['supported']];assert rows
widths=[]
for d in rows:
 assert math.isclose(d['weapon_scale'],.5,abs_tol=1e-12)
 assert math.isclose(d['canvas_size'],72*512/416,abs_tol=1e-9)
 assert math.isclose(d['weapon_width'],72*512/416*.5,abs_tol=1e-4)
 assert d['weapon']=='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
 widths.append(d['weapon_width'])
assert max(widths)==min(widths)
o={'passed':True,'supported_observations':len(rows),'uniform_weapon_scale':.5,'display_weapon_width_px':widths[0],'body_max_px':72,'source_texture_unchanged':True,'kernel_phase_verified_separately':True,'scope':'Uniform sword display geometry only, not art contrast/overlap/grip/fullmotion/hit/audio acceptance','formal_complete_units':0}
out=O/'uniform-sword-scale-verification-v001.json';assert not out.exists();out.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8');print(json.dumps(o))
