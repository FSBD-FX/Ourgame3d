"""Technical assembly of genuine K layer PNGs; no painting or game evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math
from PIL import Image

R = Path('F:/Ourgame')
C = R / 'source-assets/production/fairytale-sword-secondary-v001'
O = C / 'Root-K8-LGT-sword-fit-v001'

def pin(p):
    b = p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())

def checked(p, sha):
    assert pin(p)['sha256'] == sha, p
    return json.loads(p.read_text('utf-8-sig'))

markers_path = C/'Root-K8-binding-decisions-v001/Root-8-markers-v001.json'
markers = checked(markers_path, 'b037b961e6a9731a3f8e51a59e72a133362ac66c39795bfc1567dce3afb66d27')
choice_path = C/'Root-K8-binding-decisions-v001/Root-K5-near-shoulder-choice-v001.json'
choice = checked(choice_path, 'd068f1c3a7d1d42215194bdfdd48dd0268e5d38837b9d77ae127bb25bc929b04')
assert choice['chosen_variant'] == 'A' and choice['RootApproved_for_source_import']
assert pin(Path(choice['chosen_near_shoulder']['path'])) == choice['chosen_near_shoulder']
dependencies = {markers_path: pin(markers_path), choice_path: pin(choice_path)}
for rel, sha in (
    ('request260-body-owner-candidate-v001/four-owner-freeze-v001.json','821b2526704e99846df56d422d645a7148806dad84061d8c4188e34d92bd1b50'),
    ('request260-LGT-fit-candidate-v001/LGT-fit-freeze-v001.json','424549851ac91f5fed65bd742ec9933a912596890feb3bc2bc946fe627c324df'),
    ('K4K5K7-body-owner-candidate-v001/four-owner-freeze-v001.json','f149cd1fc12d0025d5443a16be92d7aec73417d91d824389497d728e6f9ceef0'),
    ('K4K5K7-LGT-fit-candidate-v001/LGT-fit-freeze-v001.json','a686aaec79ad737ca473d79a9a86d8dfac9adc3f73caee3115b2920b90c8b7c1'),
    ('K5-body-owner-correction-v002/four-owner-freeze-v002.json','08185a5d8f0f70b5ecd0b43cdf71dbd0b809a6762a25a5e7756ee3d7b713bfe4'),
):
    p = C/rel
    data = checked(p,sha)
    dependencies[p] = pin(p)
    for row in data['members']:
        q = Path(row['path']) if 'path' in row else p.parent/row['relative_path']
        actual = pin(q)
        assert actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'], q
        dependencies[q] = actual

sword_path = R/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
assert pin(sword_path)['sha256'] == '2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
dependencies[sword_path] = pin(sword_path)
sword = Image.open(sword_path).convert('RGBA')
assert sword.size == (512,512)
owners = ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
assert not O.exists(), 'Never overwrite a prior candidate'
O.mkdir(); (O/'source-render-only').mkdir()
rows=[]
for mark in markers['frames']:
    frame = mark['frame']; source_frame = 0 if frame == 6 else frame
    assert mark['RootApproved_for_first_native_trial'] and mark['Root'] == [256.,464.]
    grip=mark['Grip']; axis=mark['Axis']; assert abs(math.hypot(*axis)-1.) < 1e-12
    paths=[]
    for owner in owners:
        armor=owner in ('ShoulderFar','Chest','ShoulderNear')
        family=('request260-LGT-fit-candidate-v001/armor-layers' if armor else 'request260-body-owner-candidate-v001/body-layers') if source_frame<4 else ('K4K5K7-LGT-fit-candidate-v001/armor-layers' if armor else 'K4K5K7-body-owner-candidate-v001/body-layers')
        if source_frame==5 and not armor: family='K5-body-owner-correction-v002/body-layers'
        p=C/family/owner/f'K{source_frame}.png'
        if source_frame==5 and owner=='ShoulderNear':p=Path(choice['chosen_near_shoulder']['path'])
        assert p in dependencies or owner=='ShoulderNear' and source_frame==5, p
        image=Image.open(p); assert image.mode=='RGBA' and image.size==(512,512)
        dependencies[p]=pin(p); paths.append((owner,p))
    assert Image.open(paths[-1][1]).getpixel(tuple(map(int,grip)))[3]==255
    a,b=axis[0]/.50,axis[1]/.50; d,e=-axis[1]/.50,axis[0]/.50
    gx,gy=grip[0]+256,grip[1]+256
    coefficients=(a,b,99.-a*gx-b*gy,d,e,256.-d*gx-e*gy)
    blade=sword.transform((1024,1024),Image.Transform.AFFINE,coefficients,resample=Image.Resampling.BICUBIC)
    image=Image.new('RGBA',(1024,1024),(0,0,0,0))
    for owner,p in paths:
        if owner=='NearHand':image.alpha_composite(blade)
        image.alpha_composite(Image.open(p),(256,256))
    output=[]
    for direction,render in [('right',image),('left',image.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:
        p=O/'source-render-only'/f'K{frame}-LGT-{direction}-source-fit.png'
        render.save(p,compress_level=6);output.append(pin(p))
    rows.append(dict(frame=frame,source_frame=source_frame,Root=mark['Root'],Grip=grip,Axis=axis,layers=[dict(owner=n,**pin(p)) for n,p in paths],outputs=output))
    for p in dependencies:assert pin(p)==dependencies[p]

assert Image.open(O/'source-render-only/K0-LGT-right-source-fit.png').tobytes()==Image.open(O/'source-render-only/K6-LGT-right-source-fit.png').tobytes()
proof=O/'source-fit-proof-v001.json'
proof.write_text(json.dumps(dict(schema='Root-K8-LGT-genuine-source-assembly-v001',utc=datetime.now(timezone.utc).isoformat(),frames=rows,dependencies=list(dependencies.values()),method='Original RGBA layers alpha-composited in exact eight-slot depth; original independent sword rigid .50 rotation around99,256; 256px uniform canvas padding. Left is complete right pixel flip; not UE continuous UV or actual native evidence.',image_generation_calls=0,art_pixels_painted=False,actual_runtime_imported=False,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(proof=pin(proof),PNGs=16,source_dependency_mismatches=0,actual_runtime_imported=False),ensure_ascii=False))
