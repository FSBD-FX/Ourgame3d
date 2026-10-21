"""Candidate-only native171 + native172/173/174 integer registration; never UE/import.
Default admission produces no derived images. Root reviews retained outputs before use.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent
FAMILY=ROOT/'source-assets/production/fairytale-armor-sword-primary2-v001'
PART=ROOT/'source-assets/production/fairytale-sword-primary2-body-partition-v001'
BODY_RUNTIME=ROOT/'source-assets/production/fairytale-sword-primary2-runtime-v002/axis1-correction-v001'
HANDOFF=FAMILY/'primary2-macro-native-handoff-approved-v002.json'
HANDOFF_SHA='0342bbf095edec2d5d973bc28ed33f54a141827bf4c5d126238d9124043d5148'
STACK=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
OWNERS=['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']
MAP={'Chest':'Chest','NearShoulder':'ShoulderNear','FarShoulder':'ShoulderFar'}
NAMESPACE='/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor'
DURATIONS=[75,75,60,60,135,135]

def require(ok,why):
    if not ok:raise ValueError(why)
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def fact(p):
    p=Path(p).resolve();b=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def verify(f):require(fact(f['path'])==f,'Pinned source changed: '+f['path'])
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rgba(p):
    with Image.open(p) as im:
        require(im.mode=='RGBA' and im.size==(512,512),'Exact512RGBA required: '+str(p))
        return np.asarray(im).copy()
def translate(a,dx,dy):
    require(type(dx) is int and type(dy) is int,'Only integer translation')
    yy,xx=np.nonzero(np.any(a!=0,axis=2))
    require(len(xx)>0 and np.all((xx+dx>=0)&(xx+dx<512)&(yy+dy>=0)&(yy+dy<512)),'Any nonzero RGBA clipping rejected')
    b=np.zeros_like(a);x0,x1=max(0,-dx),min(512,512-dx);y0,y1=max(0,-dy),min(512,512-dy)
    b[y0+dy:y1+dy,x0+dx:x1+dx]=a[y0:y1,x0:x1]
    return b
def save(p,a):
    require(not p.exists(),'No overwrite '+str(p));p.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(a).save(p);require(np.array_equal(rgba(p),a),'PNG readback changed RGBA')

def admit(input_path):
    require(Path(sys.executable).resolve()==Path('C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe').resolve(),'Sprite-gen dedicated Python required')
    require(fact(HANDOFF)['sha256']==HANDOFF_SHA,'Approved design changed')
    data=load(input_path)
    require(data['schema']=='primary2-armor-physical-feature-registration-input-v1','Wrong registration input schema')
    verify(data['measurement']);verify(data['measurement_freeze'])
    measurement=load(data['measurement']['path'])
    require(measurement['schema']=='native171-primary2-armor-physical-feature-measurement-v001' and len(measurement['rows'])==18,'Actual independent18 measurement required')
    measured={(r['component'],r['frame']):r for r in measurement['rows']}
    for f in load(data['measurement_freeze']['path'])['files']:verify(f)
    handoff=load(HANDOFF);hrows={r['component']:r for r in handoff['rows']}
    require(len(data['rows'])==18 and {(r['component'],r['frame']) for r in data['rows']}=={(c,i) for c in MAP for i in range(6)},'Exact18 distinct physical features required')
    protected=[fact(HANDOFF),data['measurement'],data['measurement_freeze'],fact(input_path)]
    for component in MAP:
        ep=FAMILY/(component.lower()+'-extraction-v001/extraction-receipt-v001.json');e=load(ep)
        require(e['component']==component and e['shape_pipeline_passed'] and e['failure'] is None and e['request_exact_unchanged'],'Only actual standard extraction GREEN')
        require(e['metadata']['QA_errors']==e['metadata']['QA_warnings']==[] and e['metadata']['shared_row_fit']['per_frame_scale_normalization'] is False,'Unchanged sharedrow strictQA required')
        protected.append(fact(ep))
        for f in [e['raw'],e['native_receipt'],e['approved_handoff'],e['metadata']['frames_manifest'],e['metadata']['atlas_report']]:
            verify(f);protected.append(f)
        for r in [x for x in data['rows'] if x['component']==component]:
            i=r['frame'];verify(r['source']);require(r['source']==e['frames'][i]['source'],'Measured feature/source extraction mismatch')
            mr=measured[(component,i)]
            require(r['physical_measurement_row']==mr and r['source']==mr['source'] and r['actual_component_A']==mr['actual_component_A'] and r['feature_kind']==mr['feature_kind'] and r['uncertainty_source_px']==mr['uncertainty_source_px'] and r['source_RGBA_at_A']==mr['rgba_at_selected_A'] and mr['bbox_center_used'] is False,'Registration must exactly retain independent physical feature, not substitute a nearby valid pixel')
            A=r['actual_component_A'];require(isinstance(A,list) and len(A)==2 and all(type(n) is int and 0<=n<512 for n in A),'Actual physical feature A remains unmeasured')
            require(r['whole_component_bbox_used_as_A'] is False and r['uncertainty_source_px']>0,'Feature provenance/uncertainty required')
            a=rgba(r['source']['path']);require(a[A[1],A[0],3]>0 and a[A[1],A[0]].tolist()==r['source_RGBA_at_A'],'Physical feature RGBA changed')
            for sample in mr['local_cross_rgba']+mr['manual_feature_rim_evidence']:
                xy=sample.get('source_point',sample.get('point'));require(a[xy[1],xy[0]].tolist()==sample['rgba'],'Physical feature cross/rim RGBA changed')
            mount=hrows[component]['mount_candidates'][i];visible=mount['visible_cloth_design_A'];hidden=mount['hidden_trial_design_A']
            target=visible['point'] if visible['point'] is not None else hidden['point']
            require(r['body_target']==target and r['body_target_is_measured_bone'] is False,'Body target must exactly retain approved DESIGN/TRIAL')
            require(r['visible_cloth_design_A']==visible and r['hidden_trial_design_A']==hidden,'Do not fill hidden measurement or silently move design')
            dx,dy=target[0]-A[0],target[1]-A[1]
            require(r['integer_translation_xy']==[dx,dy],'Integer offset must be derived from exact feature/approved target')
            require(np.array_equal(translate(translate(a,dx,dy),-dx,-dy),a),'Read-only preflight detects clipping or irreversible RGBA translation')
            protected.append(r['source'])
    bp=load(PART/'proof-v001.json');pf=load(PART/'partition-freeze-v001.json')
    require(fact(PART/'partition-freeze-v001.json')['sha256']=='1966472a46553844aeee4e718ffdfd92c569c0f8242138a641d5df2e319e0d01','Body partition freeze changed')
    for f in pf['files']:verify(f)
    require(bp['all_source_RGBA_reconstructions_byte_exact'] and bp['all_premultiplied_alpha_composites_exact'],'Body pixel reconstruction missing')
    protected.extend([fact(PART/'proof-v001.json'),fact(PART/'partition-freeze-v001.json')])
    marker=BODY_RUNTIME/'data/primary2-marker-candidate-v002.json';inline=BODY_RUNTIME/'data/DungeonFairytaleSwordPrimary2V003.inl'
    require(fact(marker)['sha256']=='98517472416f187d50bb1d16cef484a8dad04e31e70e22d9c73b643b7c65e855','Current171 marker changed')
    require(fact(inline)['sha256']=='b2f769bcd7c92d8531a8faa9a10b9a6345e077b44f3f019f0c7de8639c34dc44','Current171 V003 inline changed')
    markers=load(marker)
    require(markers['durations_ms']==DURATIONS and markers['display_pivot_px']==[256,464] and markers['sword_scale']==.50,'Current171 display/timing/weapon contract changed')
    require(len(bp['frames'])==len(markers['markers'])==6 and all(f['source']==markers['markers'][i]['source'] and f['frame']==i for i,f in enumerate(bp['frames'])),'Body partition is not current171 V003 exact source')
    for f in bp['frames']:
        original=rgba(f['source']['path']);yy,xx=np.nonzero(original[:,:,3])
        require(len(yy)>0 and int(yy.max()-yy.min()+1)<=416,'Original body exceeds unchanged72px/416 display contract')
    protected.extend([fact(marker),fact(inline)])
    require(not (ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor').exists(),'Unused namespace collision')
    return data,bp,protected,marker,inline

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=OUT/'registration-input-v001.json');p.add_argument('--execute',action='store_true');a=p.parse_args()
    data,bp,protected,marker,inline=admit(a.input)
    if not a.execute:
        print(json.dumps({'executed':False,'physical_features':18,'body_layers':24,'namespace':NAMESPACE,'marker':fact(marker)}));return 0
    require(not (OUT/'textures').exists() and not (OUT/'candidate-import-v001.json').exists(),'No overwrite or retry of outputs')
    values=[{} for _ in range(6)];textures=[];registration=[]
    for r in data['rows']:
        c=MAP[r['component']];i=r['frame'];source=rgba(r['source']['path']);A=r['actual_component_A'];B=r['body_target'];dx,dy=B[0]-A[0],B[1]-A[1]
        registered=translate(source,dx,dy);require(np.array_equal(translate(registered,-dx,-dy),source),'Reverse translation RGBA not exact')
        dest=OUT/f'textures/{c}/frame-{i}.png';save(dest,registered);values[i][c]=registered
        textures.append({'component':c,'frame':i,'source':fact(dest)})
        registration.append({**r,'runtime_component':c,'integer_translation_xy':[dx,dy],'registered':fact(dest),'nonzero_RGBA_clipped':0,'reverse_translation_RGBA_exact':True,'rescale_rotate_warp_repaint':False})
    for f in bp['frames']:
        i=f['frame']
        for layer in f['layers']:
            c=layer['owner'];require(c in OWNERS,'Unknown body owner');verify(layer['file']);src=Path(layer['file']['path']);dest=OUT/f'textures/{c}/frame-{i}.png'
            require(not dest.exists(),'No overwrite');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);require(dest.read_bytes()==src.read_bytes(),'Original body PNG bytes changed')
            values[i][c]=rgba(dest);textures.append({'component':c,'frame':i,'source':fact(dest)});protected.append(layer['file'])
    require(len(textures)==42 and len({(x['component'],x['frame']) for x in textures})==42,'Exact42 texture set required')
    require(len({x['source']['sha256'] for x in textures})==42,'42 distinct candidate PNG sources required; no clone workaround')
    textures.sort(key=lambda x:(STACK.index(x['component']),x['frame']))
    assemblies=[]
    for i,layers in enumerate(values):
        require(set(layers)==set(STACK),'Complete same-frame layer set required')
        original=rgba(bp['frames'][i]['source']['path']);reconstructed=np.sum(np.stack([layers[c] for c in OWNERS]),axis=0,dtype=np.uint16)
        require(np.array_equal(reconstructed,original.astype(np.uint16)),'Original whole171 RGBA not reconstructed exactly')
        result=Image.new('RGBA',(512,512),(0,0,0,0))
        for c in STACK:result=Image.alpha_composite(result,Image.fromarray(layers[c]))
        dest=OUT/f'assemblies/frame-{i}-armor-no-sword.png';save(dest,np.asarray(result).copy())
        overlaps=[{'armor':c,'body_owner':o,'alpha_overlap_pixels_diagnostic_only':int(np.count_nonzero((layers[c][:,:,3]>0)&(layers[o][:,:,3]>0)))} for c in ['Chest','ShoulderNear','ShoulderFar'] for o in OWNERS]
        assemblies.append({'frame':i,'source':fact(dest),'sword_present':False,'grip_or_helmet_fit_accepted':False,'overlap_diagnostics':overlaps})
    candidate={'schema':'fairytale-primary2-armor42-integer-candidate-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'textures':textures,'texture_count':42,'frame_count':6,'durations_ms':DURATIONS,'source_canvas':[512,512],'native_facing':1,'display_canvas':72*512/416,'hero_visible_height_limit':72,'display_root':[256,464],'static_stack_without_sword':STACK,'runtime_sword_between':['HelmetForeground','NearHand'],'marker':fact(marker),'marker_inl':fact(inline),'registration':registration,'assemblies':assemblies,'new_outputs_explicitly_viewed':False,'import_permitted':False,'visual_fit_or_motion_accepted':False,'formal_complete_units':0}
    write(OUT/'candidate-import-v001.json',candidate)
    for f in protected:verify(f)
    excluded={'manifests','import-tool-version-used'}
    files=[fact(q) for q in sorted(OUT.rglob('*')) if q.is_file() and q.name not in {'delivery-freeze-v001.json','preimport-freeze-v001.json'} and not (set(q.relative_to(OUT).parts)&excluded)]
    write(OUT/'delivery-freeze-v001.json',{'schema':'primary2-armor42-candidate-freeze-v1','files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),'protected_source_files':protected,'protected_source_mismatches':[],'new_outputs_explicitly_viewed':False,'UE_imported':False,'accepted':False,'formal_complete_units':0})
    print(json.dumps({'candidate':fact(OUT/'candidate-import-v001.json'),'freeze':fact(OUT/'delivery-freeze-v001.json'),'textures':42,'new_outputs_viewed':False}));return 0

if __name__=='__main__':raise SystemExit(main())
