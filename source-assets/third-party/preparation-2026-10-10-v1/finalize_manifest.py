"""Add verified source-license status and absolute representative file mappings.

This never edits originals, extracted source assets, or the older Kenney manifest.
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parent
manifest_path=ROOT/'acquisition-manifest.json'
records=json.loads(manifest_path.read_text(encoding='utf-8'))
by_id={r['id']:r for r in records}
versions={'kenney-modular-dungeon-kit':'2.1 (package License.txt)','kenney-mini-dungeon':'2.0 (package License.txt)','kenney-animated-characters-protagonists':'1.1 (package License.txt)','kenney-rpg-audio':'no version number in package License.txt','quaternius-universal-animation-library-2-standard':'Standard; upload ID 17958478, archive hash fixed; full product update version not asserted','abstraction-music-loop-bundle-2026-q3':'2026 Q3; upload ID 19538393'}
for rec in records:
    archive=Path(rec['archive_path'])
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual!=rec['sha256'] or archive.stat().st_size!=rec['bytes']:
        raise ValueError(f'Archive checksum/size mismatch: {archive}')
    root=Path(rec['extract_path'])
    licenses=[]
    for rel in rec['license_entries']:
        path=root/rel
        data=path.read_bytes()
        if not re.search(rb'CC[- ]?0|Creative Commons Zero',data,re.I):
            raise ValueError(f'Package CC0 license not found: {path}')
        licenses.append({'archive_member':rel.replace('\\','/'),'absolute_path':str(path),'sha256':hashlib.sha256(data).hexdigest()})
    with zipfile.ZipFile(archive) as z:
        members=[i for i in z.infolist() if not i.is_dir()]
        missing=[i.filename for i in members if not (root/i.filename).is_file()]
        if missing:
            raise FileNotFoundError(f'Missing extracted files: {missing}')
    rec.update(license='CC0 1.0 Universal (package license checked)',license_evidence=licenses,package_version_evidence=versions[rec['id']],status='downloaded_extracted_license_checked_source_audited',all_zip_files_extracted=True,zip_paths_list='archive-file-list.json',extracted_file_checksums='file-checksums-sha256.json',structure_audit='structure-audit.json',current_target_engine='UE5',engine_import_verification='not assessed in source-acquisition audit; see engine integration records')

chosen=[
('player','kenney-mini-dungeon','Models/FBX format/character-human.fbx'),
('enemy','kenney-mini-dungeon','Models/FBX format/character-orc.fbx'),
('weapon','kenney-mini-dungeon','Models/FBX format/weapon-sword.fbx'),
('drop','kenney-mini-dungeon','Models/FBX format/coin.fbx'),
('chest','kenney-mini-dungeon','Models/FBX format/chest.fbx'),
('character-and-props-texture','kenney-mini-dungeon','Models/FBX format/Textures/colormap.png'),
('dungeon-room','kenney-modular-dungeon-kit','Models/FBX format/room-small.fbx'),
('dungeon-floor','kenney-modular-dungeon-kit','Models/FBX format/template-floor.fbx'),
('dungeon-texture','kenney-modular-dungeon-kit','Models/FBX format/Textures/colormap.png'),
('alternative-humanoid-model','kenney-animated-characters-protagonists','Model/characterMedium.fbx'),
('alternative-humanoid-skin','kenney-animated-characters-protagonists','Skins/skaterMaleA.png'),
('alternative-idle','kenney-animated-characters-protagonists','Animations/idle.fbx'),
('alternative-run','kenney-animated-characters-protagonists','Animations/run.fbx'),
('alternative-jump','kenney-animated-characters-protagonists','Animations/jump.fbx'),
('animation-fbx-no-root-motion','quaternius-universal-animation-library-2-standard','Universal Animation Library 2[Standard]/Unity/UAL2_Standard.fbx'),
('animation-fbx-root-motion','quaternius-universal-animation-library-2-standard','Universal Animation Library 2[Standard]/Unity/UAL2_Standard_RM.fbx'),
('animation-glb-no-root-motion','quaternius-universal-animation-library-2-standard','Universal Animation Library 2[Standard]/Unreal-Godot/UAL2_Standard.glb'),
('animation-glb-root-motion','quaternius-universal-animation-library-2-standard','Universal Animation Library 2[Standard]/Unreal-Godot/UAL2_Standard_RM.glb'),
('blender-source-mannequin-no-animations','quaternius-universal-animation-library-2-standard','Universal Animation Library 2[Standard]/Female Mannequin/Mannequin_F.blend'),
('weapon-sound-candidate','kenney-rpg-audio','Audio/drawKnife1.ogg'),
('pickup-sound-candidate','kenney-rpg-audio','Audio/handleCoins.ogg'),
('footstep-sound-candidate','kenney-rpg-audio','Audio/footstep00.ogg'),
('music-loop-candidate-not-auditioned','abstraction-music-loop-bundle-2026-q3','Week 27 - Dusty Memories.ogg'),
]
previous_manifest=ROOT.parent/'kenney/2026-10-10/acquisition-manifest.json'
previous=json.loads(previous_manifest.read_text(encoding='utf-8-sig'))
for rec in previous:
    if hashlib.sha256(Path(rec['archive_path']).read_bytes()).hexdigest().lower()!=rec['sha256'].lower():
        raise ValueError(f'Previously acquired archive changed: {rec["id"]}')
    by_id[rec['id']]=rec
chosen.extend([
 ('existing-ui','kenney-ui-adventure','PNG/Default/button_brown_close.png'),
 ('existing-impact-sound','kenney-impact-sounds','Audio/impactGeneric_light_000.ogg'),
])
reps=[]
for role,identifier,member in chosen:
    rec=by_id[identifier]
    with zipfile.ZipFile(rec['archive_path']) as z:
        info=z.getinfo(member)
    path=Path(rec['extract_path'])/member
    data=path.read_bytes()
    if len(data)!=info.file_size:
        raise ValueError(f'Representative file size mismatch: {path}')
    reps.append({'role':role,'package_id':identifier,'source_page':rec['source_page'],'archive_path':rec['archive_path'],'archive_member':member,'actual_absolute_path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'exists_and_readable_verified':True,'engine_import_status':'not verified by this source audit'})
(ROOT/'representative-files.json').write_text(json.dumps(reps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest_path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'date':'2026-10-10','current_target_engine':'UE5','new_archive_count':len(records),'new_archive_bytes':sum(r['bytes'] for r in records),'preserved_existing_archive_count':len(previous),'preserved_existing_archive_bytes':sum(r['bytes'] for r in previous),'total_archive_bytes':sum(r['bytes'] for r in records+previous),'new_extracted_file_count':sum(r['zip_entries'] for r in records),'new_extracted_bytes':sum(r['uncompressed_bytes'] for r in records),'representative_files_verified':len(reps),'remaining_partials':[str(p) for p in ROOT.rglob('*.partial')],'paid_amount':0,'accounts_logged_in':False,'source_compatibility_scope':'Metadata plus five representative files read by Blender; UE5 compatibility not tested here'}
(ROOT/'acquisition-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
