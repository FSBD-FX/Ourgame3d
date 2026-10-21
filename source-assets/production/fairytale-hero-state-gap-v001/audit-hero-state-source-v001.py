"""Read actual frozen source/content and existing source PNGs; no UE or images emitted."""
from pathlib import Path
import collections,hashlib,json,re
from PIL import Image

ROOT=Path('F:/Ourgame');OUT=Path(__file__).resolve().parent
MANIFEST=ROOT/'source-assets/production/backups/v128-guard-room-176G/compiled-source-manifest.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(name,data):
    p=OUT/name;assert not p.exists(),p;p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def same(p,row):
    got=pin(p);return all(got[k]==row[k] for k in ['bytes','sha256'])

m=read(MANIFEST);rows=[x for x in m['files'] if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/'))]
actual=set(p.relative_to(ROOT).as_posix() for folder in ['UnrealGame/Source','UnrealGame/Content/Production'] for p in (ROOT/folder).rglob('*') if p.is_file())
assert actual=={x['path'] for x in rows}
checks=[]
for turn in range(2):
    bad=[x['path'] for x in rows if not same(ROOT/x['path'],x)];checks.append(dict(pass_number=turn+1,files=len(rows),mismatches=bad));assert not bad,bad
suite=read(ROOT/m['full_suite']['path']);assert same(ROOT/m['full_suite']['path'],m['full_suite'])
assert suite['succeeded']==176 and all(suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
selected=['DungeonHUD.cpp','DungeonHUD.h','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordEquipmentBinding.cpp','DungeonFairytaleSwordEquipmentBinding.h','DungeonFairytaleSwordBodyV001.inl','DungeonFairytaleSwordBodyV002.inl','DungeonFairytaleSwordPrimary2V003.inl','DungeonFairytaleSwordPrimary2ArmorV001.inl','DungeonFairytaleSwordPrimary3V001.inl','DungeonFairytaleSwordPrimary3V002.inl','DungeonFairytaleSwordWalkDataV001.inl','DungeonFairytaleSwordWalkProfile.h','DungeonCandidateAssemblyV007.inl','DungeonPresentationScale.h','DungeonFighter.cpp','DungeonDodge.h','DungeonContentCombat.h','DungeonGameMode.cpp']
references=[];reference_dir=OUT/'source-reference';reference_dir.mkdir(exist_ok=True)
for name in selected:
    p=ROOT/'UnrealGame/Source/CodexDungeon'/name;q=reference_dir/name;assert not q.exists();q.write_bytes(p.read_bytes());references.append(dict(source=pin(p),retained=pin(q)))
write('exact-v128-source-content-pins-v001.json',dict(schema='hero-state-gap-exact-v128-v001',compiled_manifest=pin(MANIFEST),actual_source_files=sum(x['path'].startswith('UnrealGame/Source/') for x in rows),actual_production_files=sum(x['path'].startswith('UnrealGame/Content/Production/') for x in rows),endpoint_checks=checks,original_full176_report=pin(ROOT/m['full_suite']['path']),source_reference=references,files=rows,author_actual_Source_Content_writes=False))

family_manifests=[
 'fairytale-sword-runtime-v002/manifests/import-sword-body-v002.json',
 'fairytale-sword-primary2-runtime-v002/manifests/import-sword-primary2-v002.json',
 'fairytale-sword-primary3-runtime-v001/manifests/import-sword-armor-primary3-v001.json',
 'fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json',
 'fairytale-lgt-readability-v003/primary1-import-v001/import-leather-primary1-v001.json',
 'fairytale-lgt-readability-v003/combo-import-v001/import-leather-primary2-v001.json',
 'fairytale-lgt-readability-v003/combo-import-v001/import-leather-primary3-v001.json',
 'fairytale-lgt-readability-v003/walk-import-candidate-v001/import-walk48-v001.json']
resource=[];bodies=[]
for rel in family_manifests:
    p=ROOT/'source-assets/production'/rel;d=read(p)
    for a in d['assets']:
        src=Path(a['source']);assert same(src,dict(bytes=a['source_bytes'],sha256=a['source_sha256'])),src
        package=a['package_path'];disk=ROOT/'UnrealGame/Content'/(package.removeprefix('/Game/')+'.uasset');assert disk.is_file(),disk
        row=dict(manifest=pin(p),clip=a.get('clip'),component=a.get('component'),frame=a['frame'],source=pin(src),object_path=a['object_path'],actual_disk_uasset=pin(disk))
        with Image.open(src) as im:
            rgba=im.convert('RGBA');assert im.size==(512,512);row.update(source_canvas=list(im.size),actual_alpha_bbox=rgba.getchannel('A').getbbox(),actual_RGBA_sha256=hashlib.sha256(rgba.tobytes()).hexdigest())
        resource.append(row)
        if a.get('component')=='Body' or a.get('clip') in ['Ready','Primary1','Primary2']:bodies.append(row)
assert len(bodies)==28,len(bodies)
write('existing-new-style-reuse-v001.json',dict(schema='existing-new-style-reuse-v001',status='SOURCE_AND_DISK_PRESENCE_ONLY_NOT_VISUAL_ACCEPTANCE',import_manifests=[pin(ROOT/'source-assets/production'/p) for p in family_manifests],resources=resource,whole_body_phases=bodies,whole_body_phase_count=28,already_native_current_families=['Ready4','Walk6','SWD_ground_Primary1/2/3_each6'],new_style_Hurt_Dodge_Death_source_in_these_manifests=0,RGBA_decoded_but_not_viewed=True))

old=ROOT/'source-assets/production/first-unit-animation-v003/import-subset-v005.json';d=read(old);legacy=[]
for a in d['actions']:
    for f in a['frames']:
        src=Path(f['path']);asset=ROOT/f"UnrealGame/Content/Production/FirstBatch/v006/CandidateSprites/Hero/T_hero_{a['action']}_{f['index']:03d}_v006.uasset";assert src.is_file() and asset.is_file()
        legacy.append(dict(action=a['action'],frame=f['index'],manifest_identity=a['actor_identity'],source=pin(src),actual_disk_uasset=pin(asset)))
write('legacy-state-reference-inventory-v001.json',dict(schema='legacy-reference-not-new-style-reuse-v001',manifest=pin(old),logical_frames=len(legacy),unique_source_pngs=len({x['source']['path'] for x in legacy}),identity='EV042_round_enclosed_helmet_little_knight_v003',role='Old actual motion/timing reference only; cannot relabel as new clock-helmet hero',frames=legacy))

scan_roots=[p for p in (ROOT/'source-assets/production').iterdir() if p.is_dir() and p.name.startswith('fairytale-') and p!=OUT]
hits=[]
for folder in scan_roots:
    for p in folder.rglob('*.png'):
        rel=p.relative_to(folder).as_posix()
        if re.search(r'(?:^|[/_-])(hurt|death|dodge|jump|fall|land|air_primary|secondary|reload)(?:[/_.-]|$)',rel,re.I):hits.append(p.as_posix())
write('new-style-state-source-name-search-v001.json',dict(schema='bounded-existing-fairytale-state-name-search-v001',scope=[p.as_posix() for p in scan_roots],matching_png_paths=hits,limits='Filename/path search of current fairytale production families only. Does not prove absent images in arbitrary other folders or unlabelled sheets; no media visually reviewed.',new_images_generated=False))
print(json.dumps(dict(source_files=213,Production_files=1210,two_endpoint_hash_mismatches=0,actual_prior_full176_report_verified=True,new_style_whole_body_phases=28,existing_manifest_resources=len(resource),legacy_logical_frames=len(legacy),bounded_other_state_PNG_name_hits=len(hits),actual_source_content_modified=False),ensure_ascii=False))
