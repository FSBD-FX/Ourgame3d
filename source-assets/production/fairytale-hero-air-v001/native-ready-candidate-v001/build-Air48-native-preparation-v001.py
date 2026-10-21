"""Prepare48 byte-identical source textures + existing sword49 and typed data.
Does not import, run UE, change actual source, or claim resident/native acceptance.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import shutil
import zipfile

import numpy as np
from PIL import Image

ROOT = Path('F:/Ourgame')
OUT = Path(__file__).resolve().parent
FIT = OUT.parent/'source-full49-fit-candidate-v001'
FIT_CONTRACT = FIT/'Air253-nine-layer-integer-armor-and-SWD-limited-fit-candidate-v001.json'
FIT_FREEZE = FIT/'Air253-nine-layer-integer-fit-freeze-v001.json'
E_INDEX = Path('E:/OurGame/Knight/过程图稿与视频/2026-10-19-本项目E599-钟盔Air253九层棕皮甲军剑试装-v001/E-retention-index-v001.json')
TYPE_HEADER = ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordAirV001.h'
MEDIA = ROOT/'过程图稿与视频/2026-10-19_钟盔Air253四十八源纹理与四十九纹理原生准备_v001'
NAMESPACE = '/Game/Production/ArtTrials/EV048/v020/HeroLeatherAir6'
PROFILE_ID = 'EV048-v020-HeroLeatherAir6-v001'
LAYER_ORDER = ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand']
SLOT_ORDER = ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','FarHandForeground','NearHand']
POSES = ['RiseEarly','RiseLate','Apex','Fall','LandingImpact','LandingSettle']
SWORD_OBJECT = '/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'


def pin(p):
    p=Path(p); data=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(rel,value):
    p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return p


def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    with Path(src).open('rb') as rf,dst.open('xb') as wf:
        shutil.copyfileobj(rf,wf)
    assert pin(src)['sha256']==pin(dst)['sha256']
    return dst


def facts(path):
    with Image.open(path) as im:
        im.load(); assert im.mode=='RGBA' and im.size==(512,512)
        a=np.asarray(im)
    ys,xs=np.where(a[:,:,3]>0)
    assert len(xs)>0
    return {'source_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'source_mode':'RGBA','source_canvas':[512,512],
            'source_alpha_nonzero_pixels':int(len(xs)),'source_alpha128_pixels':int(np.count_nonzero(a[:,:,3]>=128)),
            'source_alpha255_pixels':int(np.count_nonzero(a[:,:,3]==255)),
            'source_alpha_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}


def numbers(xy):
    return ','.join(format(float(v),'.17g') for v in xy)


def run():
    assert set(p.name for p in OUT.iterdir())=={Path(__file__).name} and not MEDIA.exists()
    assert not (ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v020/HeroLeatherAir6').exists(), 'New import namespace already exists; stop and retain.'
    assert pin(FIT_CONTRACT)['sha256']=='e534ebd3682310c3b7742075b6fffe76c5f53f33d9d5b81de7bea49b102734a9'
    assert pin(FIT_FREEZE)['sha256']=='6bc92ada3e0c293b4a83bf47df7c15b9bd2f1294ff231c77e8c6a9166329d7cd'
    fc,freeze,ei=read(FIT_CONTRACT),read(FIT_FREEZE),read(E_INDEX)
    assert ei['verification_passes']==2 and ei['source_and_member_hash_mismatches']==0
    assert len(fc['frames'])==6 and fc['nine_layer_stack']==SLOT_ORDER
    for _ in range(2):
        assert [pin(r['path']) for r in freeze['members']]==freeze['members']
    packet=Path(ei['packet']['path']); assert pin(packet)==ei['packet']
    source_inputs=[FIT_CONTRACT,FIT_FREEZE,E_INDEX,TYPE_HEADER,packet]
    source_input_pins=[pin(p) for p in source_inputs]
    for src,rel in [(FIT_CONTRACT,'source-fullfit-contract.json'),(FIT_FREEZE,'source-fullfit-freeze.json'),
                    (E_INDEX,'E599-real-ZIP-retention-index.json'),(TYPE_HEADER,'actual-typed-interface-DungeonFairytaleSwordAirV001.h')]:
        copy(src,OUT/'inputs'/rel)
    prefix='原件/六相九层整数试装候选完整包/'
    e_by_member={r['member']:r for r in ei['files']}
    assets,frames,artist_rows=[],[],[]
    e_checks=[]
    with zipfile.ZipFile(packet) as z:
        assert z.testzip() is None

        def retained(source,relative):
            member=prefix+relative
            record=e_by_member[member]
            expected=pin(source)
            assert record['bytes']==expected['bytes'] and record['sha256']==expected['sha256']
            for n in range(2):
                data=z.read(member)
                assert data==Path(source).read_bytes() and len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
            e_checks.append({'source':expected,'E_member':member,'two_SHA_byte_equal':True})
            return {'E_index':pin(E_INDEX),'E_packet':ei['packet'],'E_member':member,
                    'E_member_bytes':record['bytes'],'E_member_sha256':record['sha256'],
                    'current_twoSHA_byte_equal':True,'individual_E_PNG_path':None,
                    'storage':'ZIP member in real E599 packet, not a loose E file.'}

        for i,row in enumerate(fc['frames']):
            frame_assets=[]
            for component in LAYER_ORDER:
                is_body=component in row['body_layers_v002_byte_identical']
                origin=Path(row['body_layers_v002_byte_identical'][component]['path'] if is_body else row['armor'][component]['placed']['path'])
                relative=f'{"body-layers" if is_body else "armor-layers"}/{component}/frame-{i}.png'
                retention=retained(origin,relative)
                name=f'T_Fairytale_Air_{component}_{i:03d}_v001'
                source=copy(origin,OUT/'sources48'/f'{name}.png')
                source_inputs.append(origin);source_input_pins.append(pin(origin))
                source_facts=facts(source)
                r={'component':component,'family':'body_source_partition' if is_body else 'armor_source_integer_translated',
                   'frame':i,'pose':POSES[i],'source':source.as_posix(),'source_filename':source.name,
                   'source_bytes':source.stat().st_size,'source_sha256':pin(source)['sha256'],**source_facts,
                   'source_origin':pin(origin),'native_source_ids':[253] if is_body else [],
                   'armor_generation_request_id':None,'known_optional_empty':False,'empty_reason':None,
                   'retention':retention,'name':name,'package_path':NAMESPACE+'/'+name,
                   'object_path':NAMESPACE+'/'+name+'.'+name,'expected_object_class':'Texture2D'}
                assets.append(r);frame_assets.append(r)
            frame={'frame':i,'pose':POSES[i],'pose_enum_value':i+1,'Root':row['Root']['xy'],'Grip':row['Grip_xy'],
                   'AxisArtist':row['axis_final_author'],'angle_author_degrees':row['angle_final_author_degrees'],
                   'Layers':[{key:a[key] for key in ['component','object_path','source_sha256','source_RGBA_sha256','source_alpha_nonzero_pixels','known_optional_empty']} for a in frame_assets],
                   'SlotOrder':SLOT_ORDER,'ExpectedNonemptyDrawCount':9}
            frames.append(frame)
            original=np.asarray(Image.open(row['source']['path']).convert('RGBA'))
            gx,gy=row['Grip_xy']
            artist_rows.append({'frame':i,'pose':POSES[i],'Root':row['Root'],'belt':row['author_belt_reference'],
                                'Grip_xy':row['Grip_xy'],'actual_Grip_source_RGBA':original[gy,gx].tolist(),
                                'Grip_author_uncertainty_source_px':6,'AxisArtist':row['axis_final_author'],
                                'Axis_author_degrees':row['angle_final_author_degrees'],
                                'v002_original_axis':row['axis_v002_original_author'],'explicit_parent_override':row['parent_author_override'],
                                'armor_A_B_and_residual_results':{role:{k:row['armor'][role][k] for k in ['author_A_B','author_point_meanings','translation_integer_xy','transformed_source_minus_body_author_point_residual_xy','author_point_residual_distances_source_px']} for role in ['Chest','ShoulderNear','ShoulderFar']},
                                'physical_bone_handle_socket_or_footlock':False,'native_art_accepted':False})
        sword_origin=FIT/'source-copied/military-sword-clean-v001.png'
        sword_retention=retained(sword_origin,'source-copied/military-sword-clean-v001.png')
        sword_source=copy(sword_origin,OUT/'existing-sword-source49/military-sword-clean-v001.png')
        source_inputs.append(sword_origin);source_input_pins.append(pin(sword_origin))
        sword={'source':pin(sword_source),'source_origin':pin(sword_origin),**facts(sword_source),'object_path':SWORD_OBJECT,
               'source_grip_xy':[99,256],'native_blade_axis':[1,0],'weapon_scale':.5,
               'retention':sword_retention,'import_new':False,'reuses_existing_object':True}
    assert len(assets)==48 and len({a['source'] for a in assets})==48 and len({a['object_path'] for a in assets})==48
    assert len({a['object_path'] for a in assets}|{sword['object_path']})==49
    artist_path=write('Air6-actual-author-points-and-armor-results-v001.json',{'schema':'Air6-actual-author-points-and-armor-results-v001','source_fullfit':pin(FIT_CONTRACT),'frames':artist_rows,'actual_physical_points':False,'FinalAccepted':False})
    descriptor={'schema':'Air49-exact-source-typed-profile-closure-v001','ProfileId':PROFILE_ID,'namespace':NAMESPACE,
                'CanvasSource':512,'StandingExtent':416.,'StandingDisplay':72.,'HeightProjection':.70,'WeaponScale':.5,'ComponentGrip':[99,256],
                'Frames':frames,'assets48':assets,'existing_sword49':sword,'source_fullfit_contract':pin(FIT_CONTRACT),
                'source_fullfit_freeze':pin(FIT_FREEZE),'artist_points':pin(artist_path),'actual_typed_header':pin(TYPE_HEADER),
                'digest_rule':'SHA256 exact UTF8 canonical JSON bytes: sort_keys=True,separators=(comma,colon),ensure_ascii=False,no trailing newline; digest is outside descriptor.'}
    canonical=json.dumps(descriptor,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    closure_path=OUT/'Air49-source-closure-canonical-v001.json'
    with closure_path.open('xb') as f:f.write(canonical)
    closure_digest=hashlib.sha256(canonical).hexdigest()
    assert pin(closure_path)['sha256']==closure_digest
    manifest=write('import-Air48-v001.json',{'schema':'frozen-Air48-scoped-native-import-prepared-v001','profile_id':PROFILE_ID,'namespace':NAMESPACE,
                   'asset_count':48,'assets':assets,'existing_sword':sword,'unique_mandatory_texture_total':49,
                   'source_closure_digest':closure_digest,'source_closure':pin(closure_path),'source_closure_descriptor':pin(closure_path),
                   'source_closure_algorithm':'SHA256 exact UTF8 descriptor bytes: sort_keys=True,separators=(comma,colon),ensure_ascii=False,no trailing newline; manifest stores digest outside descriptor.',
                   'source_fullfit':pin(FIT_CONTRACT),'Root_actual_import_approval_pin':None,
                   'E599_retention_index':pin(E_INDEX),'native_imported':False,'GPU_ready':False,'FinalAccepted':False})
    profile=write('Air-runtime-profile-data-v001.json',{'schema':'Air-sixpose-eight-source-layer-artistprofile-prepared-v001',
                 'profile_id':PROFILE_ID,'namespace':NAMESPACE,'import_manifest':pin(manifest),'source_closure_digest':closure_digest,
                 'source_closure':pin(closure_path),'SourceClosureVerified':True,'SourceClosureVerified_scope':'Exact retained source bytes/author preparation only; not import, GPU, native or final art acceptance.',
                 'canvas_source_px':[512,512],'standing_height_source_px':416,'standing_display_height_px':72.,'height_projection':.70,
                 'source_to_display_scale':72./416.,'weapon_scale':.5,'component_grip':[99,256],'independent_sword':sword,
                 'native_facing':1,'Frames':frames,'actual_author_points':pin(artist_path),
                 'selection_authority':'Actual QueryHeroNonAttackAir sample and Select: H>0 OR V>0; >315,(90,315],[-90,90],<-90; landing H=V=0 age[0,.06),[.06,.12). No authored animation clock/durations.',
                 'facing_geometry':'All layers use current actual facing; common actor X reflection after full independent sword rigid matrix. Do not swap NearFar semantics.',
                 'virtual_Root_outside_canvas_allowed':True,'Root_apex_y530_clamped':False,
                 'atomic_preload':'All48+existingSword49 exact Texture2D512/cache resident checks before any of9 slots; no flattened whole, SWDbaked, optional empty, partial or source fallback.',
                 'native_imported':False,'actual_GPU_resident_receipt':None,'TrialAllowed':False,'FinalAccepted':False})
    lines=['// Generated NEW candidate from exact E599 ZIP bytes and author profile; no native/GPU acceptance.',
           '// Include inside DungeonFairytaleSwordAirV001 anonymous namespace; no extra namespace.',
           'FProfile BuildProfileData()', '{', ' FProfile P;',f' P.ProfileId=TEXT("{PROFILE_ID}");',
           f' P.SourceClosureSHA256=TEXT("{closure_digest}");',' P.SourceClosureVerified=true; // Exact source preparation only.',
           ' P.CanvasSource=512;P.StandingExtent=416.;P.StandingDisplay=72.;P.HeightProjection=.70;P.WeaponScale=.5;',
           ' P.ComponentGrip={99.,256.};',f' P.SwordTexturePath=TEXT("{SWORD_OBJECT}");',f' P.SwordSourceSHA256=TEXT("{sword["source"]["sha256"]}");']
    for frame in frames:
        lines+=[' {',f'  auto& F=P.Frames[{frame["frame"]}];F.Frame={frame["frame"]};F.Pose=EPose::{frame["pose"]};',
                f'  F.Root={{{numbers(frame["Root"])}}};F.Grip={{{numbers(frame["Grip"])}}};F.AxisArtist={{{numbers(frame["AxisArtist"])}}};',
                '  F.ExpectedNonemptyDrawCount=9;']
        for j,a in enumerate(frame['Layers']):
            lines.append(f'  F.Layers[{j}]={{EComponent::{a["component"]},TEXT("{a["object_path"]}"),TEXT("{a["source_sha256"]}"),TEXT("{a["source_RGBA_sha256"]}"),{a["source_alpha_nonzero_pixels"]}u,false}};')
        lines += ['  F.SlotOrder={'+','.join('EComponent::'+o for o in SLOT_ORDER)+'};',' }']
    lines+=[' return P;','}','']
    inl=write('new-source/DungeonFairytaleSwordAirDataV001.inl','\n'.join(lines))
    assert len([l for l in lines if 'F.Layers[' in l])==48 and len([l for l in lines if 'F.SlotOrder=' in l])==6
    for _ in range(2):
        assert [pin(p) for p in source_inputs]==source_input_pins
        for a in assets:
            assert pin(a['source'])['sha256']==a['source_sha256'] and facts(a['source'])['source_RGBA_sha256']==a['source_RGBA_sha256']
    proof=write('Air48-preparation-host-proof-v001.json',{'schema':'Air48-preparation-host-proof-v001','actual_E599_ZIP_CRC_all_members_PASS':True,
                'actual_E599_member_twoSHA_byte_equal_checks':e_checks,'all48_source_copies_byte_equal':True,
                'all48_are512_RGBA_nonempty':True,'all48_unique_new_object_paths':True,'resident49_includes_existing_sword':True,
                'no_flattened_whole_or_SWDbaked_in_sources48':True,'Layers_order':LAYER_ORDER,'SlotOrder':SLOT_ORDER,
                'six_pose_enum_values':[1,2,3,4,5,6],'all_draw_counts':9,'canonical_closure_exact_UTF8_SHA256':closure_digest,
                'actual_typed_interface':pin(TYPE_HEADER),'typed_data_candidate':pin(inl),'source_inputs_two_SHA_unchanged':True,
                'source_inputs':source_input_pins,'CPlusPlus_compiled':False,'UE_calls':0,'actual_imports':0,'GPU_acceptance':False,'FinalAccepted':False})
    write('HANDOFF.md','''仅NEW native-ready候选：6×8=48个真实身体/甲PNG直接复制E599原ZIP已保全bytes，旧军剑为第49个resident（复用既有object path），没有flattenedwhole或SWDbaked导入。manifest source指NEW sources48，retention只记真实E599 ZIP packet/member/index及逐字节两SHA结果，不虚构E单独PNG路径。旧军剑原PNG仅供源闭包核验，不新导入。

typed Data.inl只供Root准入production的匿名namespace BuildProfileData seam，不另namespace。48源Layers固定顺序与9个SlotOrder分别明确；六相Root/Grip/Axis为实际作者合同，Apex虚拟RootY530不clamp。Land4只有NEW作者Axis覆盖回[1,.2]，最终4→5约−31.24898°；所有source fit/原甲A/B点/残差可追溯到E599源合同。

闭包SHA为明确canonical descriptor exact UTF8字节；包含49源事实、Typed frames/常量/slot、源fit及作者点pin。SourceClosureVerified只表示原源准备核验，非import/GPU/native/美术验收。Root独占actual import、Source准入、UE/native/E试听和动态判断；本候选没有C++编译或UE运行。准备F媒体只复制已经保全的源/演示，没有新图生成，保留原件/展示/版本索引。
''')
    members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    for _ in range(2):assert [pin(r['path']) for r in members]==members
    prepared_freeze=write('Air48-native-ready-freeze-v001.json',{'schema':'Air48-native-ready-freeze-v001','member_count':len(members),'members':members,
                          'two_SHA_verification_passes':2,'mismatches':0,'source_closure_digest':closure_digest,'host_proof':pin(proof),
                          'typed_data':pin(inl),'native_imports':0,'native_accepted':False,'FinalAccepted':False})
    for p in sorted(OUT.rglob('*')):
        if p.is_file():copy(p,MEDIA/'原件/四十八源四十九纹理准备完整包'/p.relative_to(OUT))
    # Copies of Root-reviewed E599 presentation, not newly generated media or acceptance.
    for p in sorted((FIT/'presentation').glob('*.png')):copy(p,MEDIA/'展示副本/E599已保全试装参考'/p.name)
    media_files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]
    for _ in range(2):assert [pin(r['path']) for r in media_files]==media_files
    with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump({'date':'2026-10-19','topic':'钟盔Air253四十八源纹理与四十九纹理原生准备','version':'v001',
                   'status':'Prepared exact source49 and typed Data; no actual import/native acceptance. Presentation is byte copy of E599 reviewed finite-fit reference.',
                   'candidate':OUT.as_posix(),'manifest':pin(manifest),'profile':pin(profile),'freeze':pin(prepared_freeze),
                   'new_visuals_generated':False,'presentation_View_in_this_batch':False,'actual_imports':0,'FinalAccepted':False,
                   'two_SHA_verification_passes':2,'mismatches':0,'files':media_files},f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'manifest':pin(manifest),'profile':pin(profile),'data_inl':pin(inl),'freeze':pin(prepared_freeze),
                      'source_closure_digest':closure_digest,'F_media':MEDIA.as_posix(),'F_files':len(media_files)+1,
                      'F_bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'actual_imports':0,'UE_calls':0},ensure_ascii=False,indent=2))


if __name__=='__main__':run()
