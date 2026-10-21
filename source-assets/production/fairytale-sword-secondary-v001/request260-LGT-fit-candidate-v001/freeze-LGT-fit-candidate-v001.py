import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FREEZE=HERE/'LGT-fit-freeze-v001.json'
def absolute_pin(p):
 b=p.read_bytes();return {'path':p.resolve().as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
 members=[]
 for p in sorted(HERE.rglob('*')):
  if p.is_file() and p!=FREEZE:
   assert p.is_relative_to(HERE)
   r=absolute_pin(p);r['relative_path']=p.relative_to(HERE).as_posix();del r['path'];members.append(r)
 dependencies=json.loads((HERE/'LGT-source-inputs-v001.json').read_text())['dependencies']
 for _ in range(2):
  for r in members:
   p=HERE/r['relative_path'];actual=absolute_pin(p);assert actual['bytes']==r['bytes'] and actual['sha256']==r['sha256']
  for r in dependencies:assert absolute_pin(Path(r['path']))==r
 d={'schema':'request260-LGT-integer-fit-candidate-freeze-v001','members':members,'dependencies':dependencies,'verification_passes':2,'twoSHA_mismatches':0,'armor_layer_count':12,'diagnostic_source_order_no_sword_assemblies':4,'source_RGBA_inverse_translation_all_exact':True,'all_nonzero_RGBA_clipped_pixels':0,'images_viewed':False,'Root_F_E_retention_required_before_View':True,'wear_fit_accepted':False,'semantic_accepted':False,'runtime_imported':False,'FinalAccepted':False}
 with FREEZE.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 r=absolute_pin(FREEZE);print(json.dumps({'freeze':r,'members':len(members),'dependencies':len(dependencies),'twoSHA_mismatches':0}))
if __name__=='__main__':main()
