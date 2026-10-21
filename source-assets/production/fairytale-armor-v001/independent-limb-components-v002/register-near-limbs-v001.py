"""Measure actual rivet outline and integer-translate original component RGBA; no art edits."""
from pathlib import Path
import datetime, hashlib, json, math, sys
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
sys.path.insert(0,str(SG))
import sprite_gen.frames.extract as native
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002')
OLD=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v001')
CHEST=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front')
OUT=ROOT/'near-limbs-registration-proposed-v001'
assert not OUT.exists(), 'Never overwrite proposed geometry'
OUT.mkdir()
for folder in ['armor-near-bracer','armor-near-shin','composite-preview','rivet-source-crops']:(OUT/folder).mkdir()
def desc(p):
    p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
    assert not p.exists(),p
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def components(mask):
    seen=np.zeros(mask.shape,bool);result=[]
    for y,x in zip(*np.where(mask)):
        if seen[y,x]:continue
        queue=[(int(y),int(x))];seen[y,x]=True;pts=[]
        while queue:
            cy,cx=queue.pop();pts.append((cx,cy))
            for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
                ny,nx=cy+dy,cx+dx
                if 0<=ny<mask.shape[0] and 0<=nx<mask.shape[1] and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;queue.append((ny,nx))
        if len(pts)>8:
            xx=[p[0] for p in pts];yy=[p[1] for p in pts]
            result.append({'count':len(pts),'bbox':[min(xx),min(yy),max(xx)+1,max(yy)+1]})
    return result

entries=[];registered={}
for key,roi_fraction in [('near-bracer',(.18,.23,.47,.68)),('near-shin',(.10,.12,.43,.48))]:
    row=json.loads((ROOT/f'handoffs/{key}-native-input-v001.json').read_text(encoding='utf-8'))['rows'][0]
    run=Path(row['run_dir']);manifest=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'))
    assert manifest['ok'] and manifest['errors']==manifest['warnings']==[]
    fit=manifest['rows'][0]['shared_row_fit']
    raw=Path(row['raw_output_path'])
    keyed=native.remove_chroma_background(Image.open(raw),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
    pieces=native.extract_component_images(keyed,4)
    assert len(pieces)==4
    registered[key]=[]
    frames=[]
    for i,piece in enumerate(pieces):
        assert hashlib.sha256(piece.tobytes()).hexdigest()==fit['raw_component_RGBA_sha256'][i]
        a=np.array(piece.convert('RGBA'));h,w=a.shape[:2]
        x0,y0,x1,y1=[int(v*n) for v,n in zip(roi_fraction,[w,h,w,h])]
        roi=a[y0:y1,x0:x1];dark=(roi[:,:,:3].mean(axis=2)<60.)&(roi[:,:,3]>=250)
        candidates=[]
        for c in components(dark):
            l,t,r,b=c['bbox'];cw,ch=r-l,b-t
            if l==0 or t==0 or r==dark.shape[1] or b==dark.shape[0]:continue
            if not(.10*w<=min(cw,ch) and max(cw,ch)<=.30*w and .70<=cw/ch<=1.30):continue
            candidates.append({**c,'bbox_component_px':[l+x0,t+y0,r+x0,b+y0]})
        assert len(candidates)==1,(key,i,candidates)
        ring=candidates[0];l,t,r,b=ring['bbox_component_px']
        center=[(l+r-1)/2.,(t+b-1)/2.]
        record=fit['frame_records'][i];px,py=record['placement_xy'];fw,fh=record['resampled_size']
        mapped=[px+(center[0]+.5)*fw/w-.5,py+(center[1]+.5)*fh/h-.5]
        measured=[int(math.floor(v+.5)) for v in mapped]
        target=row['target_mounts'][i]['A'];shift=[target[j]-measured[j] for j in range(2)]
        source=run/f'curated/frame-{i}.png';im=Image.open(source).convert('RGBA');bbox=im.getbbox()
        assert im.getpixel(tuple(measured))[3]>=250
        assert 0<=bbox[0]+shift[0]<bbox[2]+shift[0]<=512 and 0<=bbox[1]+shift[1]<bbox[3]+shift[1]<=512
        layer=Image.new('RGBA',(512,512),(0,0,0,0));layer.paste(im,tuple(shift))
        assert im.crop(bbox).tobytes()==layer.crop(layer.getbbox()).tobytes(),'CroppedRGBA changed'
        dest=OUT/f'armor-{key}/frame-{i}.png';layer.save(dest);registered[key].append(layer)
        crop=OUT/f'rivet-source-crops/{key}-frame-{i}.png';piece.crop((max(0,l-5),max(0,t-5),min(w,r+5),min(h,b+5))).save(crop)
        frames.append({'frame':i,'source':desc(source),'native_component_size_px':[w,h],
                       'native_component_RGBA_sha256':hashlib.sha256(piece.tobytes()).hexdigest(),
                       'rivet_roi_component_px':[x0,y0,x1,y1],'dark_ring_candidates':candidates,
                       'actual_ring_center_component_px':center,'mapped_ring_center_frame_px':mapped,
                       'A_measured_integer_px':measured,'A_target_body_design_px':target,'integer_translation_px':shift,
                       'quantization_error_px':[measured[j]-mapped[j] for j in range(2)],
                       'confidence':'Actual isolated connected round outline, not the deliberately off-center dark dot or external plate bbox; integer quantization <=0.5px, semantic center ambiguity about1px.',
                       'registered':desc(dest),'registered_alpha_bbox_px':list(layer.getbbox()),
                       'cropped_RGBA_byte_identical':True,'clipped':False,'rivet_diagnostic_crop':desc(crop)})
    entries.append({'component':row['component'],'raw':desc(raw),'frames_manifest':desc(run/'frames/frames-manifest.json'),
                    'shared_scale':fit['scale'],'QA_errors':manifest['errors'],'QA_warnings':manifest['warnings'],
                    'durations_ms':[167]*4,'frames':frames})

composites=[]
for i in range(4):
    body=CANON/f'curated/frame-{i}.png';far=OLD/f'far150-registration-proposed-v001/armor-far/frame-{i}.png'
    chest=CHEST/f'frame-{i}.png';near=OLD/f'near149-registration-proposed-v001/armor-near/frame-{i}.png'
    base=Image.open(body).convert('RGBA')
    for p in [far,chest,near]:base=Image.alpha_composite(base,Image.open(p).convert('RGBA'))
    prior=OLD/f'far150-registration-proposed-v001/composite-preview/frame-{i}.png'
    assert base.tobytes()==Image.open(prior).convert('RGBA').tobytes(),'Existing full-set assembly changed'
    current=Image.alpha_composite(base,registered['near-bracer'][i]);current=Image.alpha_composite(current,registered['near-shin'][i])
    dest=OUT/f'composite-preview/frame-{i}.png';current.save(dest)
    composites.append({'frame':i,'prior_full_set':desc(prior),'body':desc(body),'far_shoulder':desc(far),
                        'chest':desc(chest),'near_shoulder':desc(near),'new_composite':desc(dest),
                        'layer_order':['whole131','far150','chest147','near149','near_bracer151','near_shin152']})
write(OUT/'registration-receipt-v001.json',{'schema':'fairytale-near-limb-integer-rivet-registration-v1',
      'created_local':datetime.datetime.now().astimezone().isoformat(),
      'algorithm':'Re-use pinned native chroma/component extraction and verify every rawRGBA hash against shared-fit manifest. Inside fixed per-component relative ROI find threshold luma<60 opaque connected dark round outline; reject ROI-touching or nonround/small features. Unique rivet ring bbox midpoint maps through actual integer Lanczos output dimensions; round-half-up then pure integer translation to fixed body garment-design A. No point selected based on body fit.',
      'feature':'Actual round rivet OUTLINE center, not potentially off-center black dot; no B residual or whole-plate center fallback.',
      'native_extractor_sha256':'f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539',
      'new_outputs_viewed':False,'registration_visual_status':'Proposed; machine feature localization pending post-E visual check.',
      'entries':entries,'composites':composites,'actual_semantic_mask_exists':False,
      'zero_collision_accepted':False,'motion_accepted':False,'runtime_imported':False,'formal_complete_units':0})
files=sorted(p for p in OUT.rglob('*') if p.is_file())+[Path(__file__)]
freeze=OUT/'registered-freeze-v001.json'
write(freeze,{'schema':'fairytale-near-limb-proposed-registration-freeze-v1',
              'created_local':datetime.datetime.now().astimezone().isoformat(),'file_count':len(files),
              'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],
              'viewed_before_root_retention':False,'accepted':False})
print(json.dumps({'freeze':desc(freeze),'files':len(files),'bytes':sum(p.stat().st_size for p in files),
      'components':[{'component':e['component'],'A':[f['A_measured_integer_px'] for f in e['frames']],
                     'translations':[f['integer_translation_px'] for f in e['frames']]} for e in entries]},ensure_ascii=False))
