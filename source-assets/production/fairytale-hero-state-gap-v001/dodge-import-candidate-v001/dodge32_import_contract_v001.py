"""Exact Dodge32 host contract. No Unreal import or writes at module load."""
from pathlib import Path
import hashlib,json,re

HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame').resolve()
NAMESPACE='/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge'
COMPONENTS=('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground','ShoulderFar','Chest','ShoulderNear')
BODY_COMPONENTS=set(COMPONENTS[:5])

def need(value,reason):
    if not value:raise ValueError(reason)

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def resolve(path,root=ROOT):
    p=Path(path);return (p if p.is_absolute() else root/p).resolve()

def pin(path):
    p=Path(path).resolve();b=p.read_bytes()
    return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def check(value,root=ROOT):
    p=resolve(value['path'],root);actual=pin(p)
    need((actual['bytes'],actual['sha256'])==(value['bytes'],value['sha256']),'Pin changed: '+str(p))
    return p

def validate_layout(m,root=ROOT):
    need(m['schema']=='Root-Dodge32-native-import-v001','Wrong Dodge32 manifest schema')
    need((m['expected_old_count'],m['expected_new_count'],m['expected_final_count'])==(1332,32,1364),'Exact1332+32=1364 required')
    need(m['namespace']==NAMESPACE and m['replace_existing'] is False,'Exact unused Dodge namespace/no replacement required')
    assets=m['assets'];need(len(assets)==32,'Exactly32 assets required')
    need({(x['component'],x['frame']) for x in assets}=={(c,f) for c in COMPONENTS for f in range(4)},'Exact eight components times four phases required')
    need(len({x['object_path'] for x in assets})==32 and len({x['saved_path'] for x in assets})==32,'Duplicate object or package')
    for x in assets:
        need(type(x['frame']) is int,'Integer phase required')
        name=f'T_Fairytale_Dodge_{x["component"]}_{x["frame"]:03d}_v001';package=NAMESPACE+'/'+name
        need((x['name'],x['package_path'],x['object_path'],x['destination_path'])==(name,package,package+'.'+name,NAMESPACE),'Destination identity changed')
        target=resolve(root/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset'),root)
        need(resolve(x['saved_path'],root)==target,'Saved path substituted outside exact new package')

def validate_receipt_assets(m,receipt,root=ROOT):
    validate_layout(m,root)
    actual=receipt['assets'];need(len(actual)==32,'Receipt must have32 assets')
    indexed={(x['component'],x['frame']):x for x in actual}
    need(len(indexed)==32,'Duplicate receipt identity')
    expected={(x['component'],x['frame']):x for x in m['assets']}
    need(set(indexed)==set(expected),'Receipt phase identity changed')
    enum_names={'compression_settings':('TextureCompressionSettings','TC_EDITOR_ICON'),
        'mip_gen_settings':('TextureMipGenSettings','TMGS_NO_MIPMAPS'),
        'lod_group':('TextureGroup','TEXTUREGROUP_UI'),'filter':('TextureFilter','TF_BILINEAR')}
    for key,x in expected.items():
        a=indexed[key]
        need(a['source']==x['source'] and a['actual_object_path']==x['object_path'],'Receipt source/object substituted')
        need(a['actual_class']=='Texture2D' and a['actual_dimensions']==[512,512],'Actual Texture2D512 readback required')
        names=a['actual_import_filenames']
        need(len(names)==1 and resolve(names[0],root)==resolve(x['source']['path'],root),'Actual source import provenance changed')
        need(resolve(a['saved']['path'],root)==resolve(x['saved_path'],root),'Saved receipt path changed')
        need(type(a['saved']['bytes']) is int and a['saved']['bytes']>0 and re.fullmatch('[0-9a-f]{64}',a['saved']['sha256']),'Invalid saved package pin')
        settings=a['actual_settings'];need(set(settings)==set(enum_names)|{'never_stream','srgb'},'Missing/extra texture readback setting')
        need(settings['never_stream']==settings['srgb']=='True','UI never-stream/sRGB readback differs')
        for field,(enum,member) in enum_names.items():
            need(re.fullmatch(r'<'+enum+r'\.'+member+r': [0-9]+>',settings[field]) is not None,'Texture setting differs: '+field)

def verify_old(old,root=ROOT):
    need(len(old)==1332 and len({x['path'] for x in old})==1332,'Exact1332 distinct old pins required')
    for x in old:
        need(x['path'].startswith('UnrealGame/Content/Production/'),'Unexpected old package path')
        check(x,root)

def exact_membership(m,after,root=ROOT):
    expected={resolve(x['path'],root) for x in m['old_production_files']}
    if after:expected|={resolve(x['saved_path'],root) for x in m['assets']}
    actual={p.resolve() for p in (root/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
    need(actual==expected and len(actual)==(1364 if after else 1332),'Production membership differs from exact old1332'+('+new32' if after else ''))

def load_sources(root=ROOT,decode_rgba=True):
    """Read exact frozen prepared sources; body20 E502, armor12 E510."""
    if decode_rgba:from PIL import Image
    inputs=read(HERE/'input-pins-v001.json')
    for value in inputs['files'].values():check(value,root)
    prepared=read(check(inputs['files']['prepared_manifest'],root))
    freeze=read(check(inputs['files']['prepared_freeze'],root))
    for value in freeze['files']:check(value,root)
    review=read(check(inputs['files']['Root_after_E510_review'],root))
    need(review['Dodge_source_freeze']==inputs['files']['prepared_freeze'] and review['source_preparation_only'] is True,'Wrong Root E510 preparation record')
    need(review['TrialAllowed'] is False and review['FinalAccepted'] is False,'Preparation must not assert runtime acceptance')
    for value in review['actually_viewed_standalone_plates']:check(value,root)
    need(prepared['schema']=='frozen-Dodge32-scoped-native-import-prepared-v001' and prepared['asset_count']==32,'Wrong prepared source manifest')
    need(prepared['import_permitted_for_Root_scoped_preparation'] is True and prepared['FinalAccepted'] is False and prepared['replace_existing'] is False,'Limited source preparation scope changed')
    permission=read(check(prepared['Root_preparation_permission'],root))
    need(permission['accepted_for_limited_preparation_only'] is True and permission['TrialAllowed'] is False and permission['FinalAccepted'] is False,'Source permission exceeds preparation scope')
    need(permission['source_closure_digest']==prepared['source_closure_digest']==freeze['source_closure_digest'],'Source closure changed')
    e510_path=check(review['E510_actual_retention'],root);e510=read(e510_path)
    e502_path=check(permission['E502'],root);e502=read(e502_path)
    for e in [e502,e510]:need(e['verification_passes']==2 and e['source_and_target_hash_mismatches']==0,'Retained E two-SHA index failed')
    assets=[]
    for x in prepared['assets']:
        source=dict(path=resolve(x['source'],root).as_posix(),bytes=x['source_bytes'],sha256=x['source_sha256']);p=check(source,root)
        need(x['source_mode']=='RGBA' and x['source_canvas']==[512,512] and x['known_optional_empty'] is False,'All32 nonempty source slots required')
        if decode_rgba:
            with Image.open(p) as image:
                need(image.mode=='RGBA' and image.size==(512,512) and image.getchannel('A').getbbox() is not None,'Nonempty RGBA512 source required')
                need(hashlib.sha256(image.tobytes()).hexdigest()==x['source_RGBA_sha256'],'Decoded RGBA changed: '+str(p))
        ep,ej=(e502_path,e502) if x['component'] in BODY_COMPONENTS else (e510_path,e510)
        matches=[z for z in ej['files'] if (z['sha256'],z['bytes'])==(source['sha256'],source['bytes'])]
        need(bool(matches),'Exact source missing from required E502/E510 retention')
        retained=(ep.parent/matches[0]['retained_relative']).resolve()
        need(retained.is_relative_to(ep.parent),'Retained path escapes E batch')
        for repeat in range(2):need((pin(retained)['bytes'],pin(retained)['sha256'])==(source['bytes'],source['sha256']),'Retained source bytes changed')
        package=x['package_path'];saved=root/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset')
        assets.append(dict(component=x['component'],frame=x['frame'],native_source_ids=x['native_source_ids'],name=x['name'],source=source,
            source_RGBA_sha256=x['source_RGBA_sha256'],destination_path=NAMESPACE,package_path=package,object_path=x['object_path'],
            saved_path=saved.as_posix(),retained_E=pin(retained),E_retention_index=pin(ep)))
    validate_layout(dict(schema='Root-Dodge32-native-import-v001',expected_old_count=1332,expected_new_count=32,
        expected_final_count=1364,namespace=NAMESPACE,replace_existing=False,assets=assets),root)
    closure=hashlib.sha256(json.dumps([dict(component=x['component'],frame=x['frame'],source_sha256=x['source']['sha256'],
        source_RGBA_sha256=x['source_RGBA_sha256'],object_path=x['object_path']) for x in assets],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(closure==prepared['source_closure_digest'],'Actual32 source closure differs')
    return assets,inputs,review,prepared

def load_manifest(path,root=ROOT,decode_rgba=True):
    m=read(path);validate_layout(m,root)
    assets,inputs,review,prepared=load_sources(root,decode_rgba)
    need(m['assets']==assets,'Root manifest differs from exact frozen source/E32')
    need(m['source_manifest']==inputs['files']['prepared_manifest'] and m['candidate_freeze']==inputs['files']['prepared_freeze'],'Prepared-source provenance changed')
    need(m['Root_source_review']==inputs['files']['Root_after_E510_review'],'Wrong Root source review')
    need(m['source32_RGBA512_host_verified'] is True,'Host RGBA32 preparation gate missing')
    trial=read(check(m['root_trial_registration'],root))
    need(trial['schema']=='Root-Dodge32-limited-import-trial-v001' and trial['RootApproved'] is True and trial['is_template'] is False,'Explicit Root limited import approval missing')
    need(trial['limited_import_approved'] is True and trial['approval_method']=='Root CLI --approve-limited-import','Missing import-only CLI approval')
    need(trial['source_manifest']==m['source_manifest'] and trial['candidate_freeze']==m['candidate_freeze'] and trial['Root_source_review']==m['Root_source_review'],'Limited approval binds different source')
    need(trial['TrialAllowed'] is False and trial['FinalAccepted'] is False and m['FinalAccepted'] is False,'Import scope cannot grant runtime/final approval')
    old_snapshot=read(check(m['old_compiled_snapshot'],root))
    old=[x for x in old_snapshot['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
    need(old_snapshot['production_files']==1332 and old==m['old_production_files'],'Wrong1332 baseline snapshot')
    return m
