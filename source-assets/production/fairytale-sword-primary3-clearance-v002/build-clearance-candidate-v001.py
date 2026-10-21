"""Numerical source-RGBA forecast and UNAPPLIED text only. Never writes images/UE Source."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent
BASE=ROOT/'source-assets/production/fairytale-sword-primary3-runtime-v001'
SNAPSHOT=ROOT/'source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116'
WEAPON=ROOT/'source-assets/production/first-unit-animation-v001/processed/military-sword-component/clean.png'
MARKERS=BASE/'data/primary3-marker-candidate-v001.json'
EXPECTED_MARKER='5ebe10d89f9ab5847acf613bc96f656e45631e525e7c2918d08d1c531b89f60a'
EXPECTED_WEAPON='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
EXPECTED_INLINE='6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054'
AXES={1:[-.5,-.8660254037844386],3:[.9135454576426009,.4067366430758002]}
SCREEN_PER_BODY_SOURCE=72/416

def desc(path):
    data=path.read_bytes();return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def new(path,value):
    with path.open('x',encoding='utf-8') as stream:
        stream.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def dilate_numeric(mask,radius):
    padded=np.pad(mask,radius);result=np.zeros_like(mask)
    for row in range(2*radius+1):
        for col in range(2*radius+1):result|=padded[row:row+512,col:col+512]
    return result

def main():
    assert desc(MARKERS)['sha256']==EXPECTED_MARKER and desc(WEAPON)['sha256']==EXPECTED_WEAPON
    marker_doc=load(MARKERS);markers=marker_doc['markers']
    assert len(markers)==6 and [m['frame'] for m in markers]==list(range(6))
    assert [m['display_root'] for m in markers]==[[256,464]]*6
    assert [markers[i]['grip_candidate_px'] for i in (1,3)]==[[194,191],[331,360]]
    assert [markers[i]['grip_uncertainty_source_px'] for i in (1,3)]==[3,3]
    assert marker_doc['sword_scale']==.5 and marker_doc['independent_sword_grip']==[99,256]
    assert marker_doc['durations_ms']==[110,110,60,60,160,160]
    snapshot=load(SNAPSHOT/'compiled-source-manifest.json')
    indexed={row['path']:row for row in snapshot['files']}
    source_names=['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordPrimary3V001.inl','DungeonContentCombat.h']
    pins=[]
    for name in source_names:
        rel='UnrealGame/Source/CodexDungeon/'+name;actual=desc(ROOT/rel)
        assert actual['bytes']==indexed[rel]['bytes'] and actual['sha256']==indexed[rel]['sha256']
        assert (ROOT/rel).read_bytes()==(SNAPSHOT/rel).read_bytes();pins.append(actual)
    original_inline=ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary3V001.inl'
    assert desc(original_inline)['sha256']==EXPECTED_INLINE
    package_rel='UnrealGame/Content/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.uasset'
    package=desc(ROOT/package_rel)
    assert package['bytes']==indexed[package_rel]['bytes'] and package['sha256']==indexed[package_rel]['sha256']
    receipt_path=ROOT/'UnrealGame/Saved/Bootstrap/content-sprites-v002-import.json'
    receipt=load(receipt_path);matches=[row for row in receipt['assets'] if row.get('action')=='military_sword']
    assert receipt['success'] and len(matches)==1
    imported=matches[0]
    assert Path(imported['source'])==WEAPON and imported['source_sha256']==EXPECTED_WEAPON
    assert imported['asset']=='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002'
    assert imported['grip_px']==[99,256] and imported['imported_size']==[512,512]
    assert hashlib.md5(WEAPON.read_bytes()).hexdigest()=='007d1bf45485d555262fcfbb2cd3123b'
    weapon=np.asarray(Image.open(WEAPON).convert('RGBA'))
    assert weapon.shape==(512,512,4)
    wy,wx=np.nonzero(weapon[:,:,3]>0);alpha=weapon[wy,wx,3].astype(float)
    dx=(wx+.5-99)*.5;dy=(wy+.5-256)*.5
    proof_path=ROOT/'source-assets/production/fairytale-sword-primary3-body-partition-v001/proof-v001.json'
    proof=load(proof_path)
    arrays={};refs={}
    for frame in (1,3):
        arrays[frame]={};refs[frame]={}
        for component in ('HelmetForeground','NearHand'):
            path=BASE/f'textures/{component}/frame-{frame}.png'
            p=[x['file'] for x in proof['frames'][frame]['layers'] if x['owner']==component][0]
            original=Path(p['path']);assert desc(original)==p and path.read_bytes()==original.read_bytes()
            refs[frame][component]=desc(path);arrays[frame][component]=np.asarray(Image.open(path).convert('RGBA'))

    def sample(frame,axis,grip_delta=(0,0),with_samples=False):
        angle=math.atan2(axis[1],axis[0]);co,si=math.cos(angle),math.sin(angle)
        grip=np.array(markers[frame]['grip_candidate_px'])+np.array(grip_delta)
        px=grip[0]+co*dx-si*dy;py=grip[1]+si*dx+co*dy
        ix=np.floor(px).astype(int);iy=np.floor(py).astype(int)
        inside=(ix>=0)&(ix<512)&(iy>=0)&(iy<512)
        helm=np.zeros(len(px),dtype=float);hand=np.zeros(len(px),dtype=float)
        helm[inside]=arrays[frame]['HelmetForeground'][iy[inside],ix[inside],3]
        hand[inside]=arrays[frame]['NearHand'][iy[inside],ix[inside],3]
        remaining=alpha*(1-hand/255.)
        core_before=(alpha>=128)&(helm>=128)
        core=(remaining>=128)&(helm>=128)
        any_visible=(remaining>0)&(helm>0)
        margin=464-float(py.max())
        # Full unit source-pixel-cell support, a stronger geometric bound than centers.
        half_cell_support=.25*(abs(co)+abs(si))
        core_margin=464-float(py[alpha>=128].max())
        row={'axis':axis,'angle_degrees':math.degrees(angle),'source_pixel_center_count':len(px),
            'helmet_core_overlap_before_NearHand':int(core_before.sum()),
            'helmet_core_overlap_after_NearHand':int(core.sum()),
            'helmet_any_alpha_overlap_after_NearHand':int(any_visible.sum()),
            'after_hand_core_sample_area_screen_px2_only':float(core.sum()*(.5*SCREEN_PER_BODY_SOURCE)**2),
            'ground_margin_positive_above_464':{'all_alpha_pixel_centers_body_source_px':margin,
                'all_alpha_pixel_centers_screen_px':margin*SCREEN_PER_BODY_SOURCE,
                'core_alpha128_pixel_centers_body_source_px':core_margin,
                'core_alpha128_pixel_centers_screen_px':core_margin*SCREEN_PER_BODY_SOURCE,
                'full_source_pixel_cells_body_source_px':margin-half_cell_support,
                'full_source_pixel_cells_screen_px':(margin-half_cell_support)*SCREEN_PER_BODY_SOURCE},
            'body_source_projected_bounds_centers':[float(px.min()),float(py.min()),float(px.max()),float(py.max())],
            'per_facing':[]}
        for facing in (1,-1):
            fx=256+facing*(px-256)
            mirror_angle=angle*facing
            native_x=256+facing*(grip[0]-256)+math.cos(mirror_angle)*(facing*dx)-math.sin(mirror_angle)*dy
            native_y=grip[1]+math.sin(mirror_angle)*(facing*dx)+math.cos(mirror_angle)*dy
            algebra_error=max(float(np.max(np.abs(native_x-fx))),float(np.max(np.abs(native_y-py))))
            assert algebra_error<1e-12  # Numerical model algebra only, not a gameplay tolerance.
            mx=np.floor(native_x).astype(int);my=np.floor(native_y).astype(int)
            valid=(mx>=0)&(mx<512)&(my>=0)&(my<512)
            hm=arrays[frame]['HelmetForeground'][:,:,3]
            nm=arrays[frame]['NearHand'][:,:,3]
            if facing<0:hm=hm[:,::-1];nm=nm[:,::-1]
            mirrored_helmet=np.zeros(len(px));mirrored_hand=np.zeros(len(px))
            mirrored_helmet[valid]=hm[my[valid],mx[valid]]
            mirrored_hand[valid]=nm[my[valid],mx[valid]]
            visible_alpha=alpha*(1-mirrored_hand/255.)
            row['per_facing'].append({'facing':facing,'directed_screen_rotation_degrees':math.degrees(angle)*facing,
                'projected_body_coordinate_bounds_centers':[float(fx.min()),float(py.min()),float(fx.max()),float(py.max())],
                'signed_ground_margin_screen_px':margin*SCREEN_PER_BODY_SOURCE,
                'helmet_core_overlap_after_NearHand':int(((visible_alpha>=128)&(mirrored_helmet>=128)).sum()),
                'helmet_any_alpha_overlap_after_NearHand':int(((visible_alpha>0)&(mirrored_helmet>0)).sum()),
                'independently_composed_mirror_transform_error_body_source_px':algebra_error,
                'mirror_note':'Algebraic single reflection and reflected-mask lookup; not two GPU measurements.'})
        if with_samples:
            def details(mask):
                result=[]
                for k in np.flatnonzero(mask):
                    result.append({'weapon_source_texel_index':[int(wx[k]),int(wy[k])],
                        'weapon_source_RGBA':weapon[wy[k],wx[k]].tolist(),
                        'transformed_body_source_pixel_center':[float(px[k]),float(py[k])],
                        'reference_body_texel_index':[int(ix[k]),int(iy[k])],
                        'HelmetForeground_RGBA':arrays[frame]['HelmetForeground'][iy[k],ix[k]].tolist(),
                        'NearHand_RGBA':arrays[frame]['NearHand'][iy[k],ix[k]].tolist(),
                        'remaining_sword_alpha_255_scale':float(remaining[k])})
                return result
            row['overlap_core_source_samples_after_hand']=details(core)
            row['overlap_all_alpha_source_samples_after_hand']=details(any_visible)
        return row

    comparisons=[]
    for frame in (1,3):
        variants={}
        for name,axis in [('old',markers[frame]['directed_blade_axis_DESIGN']),('candidate',AXES[frame])]:
            nominal=sample(frame,axis,with_samples=True)
            sensitivity=[]
            for offset_x in (-3,0,3):
                for offset_y in (-3,0,3):
                    metric=sample(frame,axis,(offset_x,offset_y))
                    sensitivity.append({'hypothetical_grip_offset_not_installed':[offset_x,offset_y],
                        'core_overlap':metric['helmet_core_overlap_after_NearHand'],
                        'any_overlap':metric['helmet_any_alpha_overlap_after_NearHand'],
                        'signed_full_pixel_cell_ground_margin_screen_px':metric['ground_margin_positive_above_464']['full_source_pixel_cells_screen_px']})
            nominal['grip_uncertainty_9_sample_sensitivity']=sensitivity
            nominal['sampled_worst_core_overlap']=max(x['core_overlap'] for x in sensitivity)
            nominal['sampled_worst_all_alpha_overlap']=max(x['any_overlap'] for x in sensitivity)
            nominal['sampled_min_full_cell_ground_margin_screen_px']=min(x['signed_full_pixel_cell_ground_margin_screen_px'] for x in sensitivity)
            nominal['minus_1screenpixel_UNMEASURED_raster_budget']=nominal['sampled_min_full_cell_ground_margin_screen_px']-1.
            variants[name]=nominal
        helmet=arrays[frame]['HelmetForeground'][:,:,3]>=128
        hand=arrays[frame]['NearHand'][:,:,3]>=128
        adjacent=int((hand&dilate_numeric(helmet,1)).sum())
        comparisons.append({'frame':frame,'grip_unchanged':markers[frame]['grip_candidate_px'],
            'actual_handle_center':None,'actual_blade_axis':None,'layers':refs[frame],
            'axis_change_degrees':variants['candidate']['angle_degrees']-variants['old']['angle_degrees'],
            'fixed_NearHand_core_pixels_8adjacent_HelmetForeground_core':adjacent,
            'painted_fist_helmet_adjacency_changed_by_axis':False,'variants':variants})
    search=[]
    for angle in range(-150,-99):
        axis=[math.cos(math.radians(angle)),math.sin(math.radians(angle))]
        metric=sample(1,axis)
        search.append({'angle_degrees':angle,'core_overlap_after_hand':metric['helmet_core_overlap_after_NearHand'],
            'all_alpha_overlap_after_hand':metric['helmet_any_alpha_overlap_after_NearHand']})
    candidate_markers=[]
    for frame,m in enumerate(markers):
        row=dict(m);row['directed_blade_axis_DESIGN']=AXES.get(frame,m['directed_blade_axis_DESIGN'])
        row['axis_changed_from_V001']=frame in AXES;candidate_markers.append(row)
    changed=[i for i,(old,new_marker) in enumerate(zip(markers,candidate_markers)) if old['directed_blade_axis_DESIGN']!=new_marker['directed_blade_axis_DESIGN']]
    assert changed==[1,3]
    for old,new_marker in zip(markers,candidate_markers):
        assert {k:v for k,v in old.items() if k!='directed_blade_axis_DESIGN'}=={k:v for k,v in new_marker.items() if k not in ('directed_blade_axis_DESIGN','axis_changed_from_V001')}
    prediction={'schema':'native175-primary3-axis-only-clearance-CPU-v002','candidate_only':True,'Source_applied':False,
        'snapshot_reference':desc(SNAPSHOT/'compiled-source-manifest.json'),'actual_v116_source_pins':pins,
        'original_marker':desc(MARKERS),'actual_weapon_clean':desc(WEAPON),
        'weapon_source_MD5':'007d1bf45485d555262fcfbb2cd3123b','Root_reported_current_importData_MD5_matches':True,
        'current_uasset_matches_v116':package,'historical_actual_import_receipt':desc(receipt_path),
        'historical_weapon_import_row':imported,'body_partition_reference':desc(proof_path),
        'method':{'input':'Every nonzero-alpha original512 sword texel center, including alpha1 tails; nearest floor lookup of actual imported original512 helmet/hand sourceRGBA.',
            'transform_body_source':'Grip + Rotation(atan2(axis.y,axis.x))*0.5*((weapon_texel_index+0.5)-[99,256])',
            'facing':'x=256+Facing*(x_right-256), y unchanged; source helmet/hand mask reflected by the same single operation.',
            'layer_order':'HelmetForeground then Sword then NearHand; remaining sword alpha=wAlpha*(1-handAlpha/255).',
            'core_sample':'remaining sword alpha>=128 and actual helmet alpha>=128; any sample:both>0.',
            'ground_reference':'fixed displayRoot.y464; positive margin means projected sword is above this baseline, not physics-ground proof.',
            'source_to_screen':SCREEN_PER_BODY_SOURCE,'screen_context':'1280x720 native capture, UIScale1; bodyCanvas72*512/416, independentSword.50.',
            'source_pixel_cells':'Centers + rotation-projected half unit-cell support; no image resampling or mask output.',
            'sensitivity':'Nine hypothetical±3source palm perturbations only assess measurement sensitivity, never change candidate palm.',
            'raster_budget':'1screen pixel subtracted as an UNMEASURED design allowance. Not a proven engine filtering/error bound.',
            'not_GPU':'No viewport raster/filter/depth/translucency/sampling reproduced; source sample counts are not rendered pixels.'},
        'comparisons':comparisons,'bounded_phase1_integer_angle_scan':search,
        'bounded_scan_not_global_impossibility_proof':True,
        'unchanged':{'palm':True,'root':[256,464],'body_canvas':72*512/416,'body_max_px':72,'sword_scale':.5,
            'weapon_source_grip':[99,256],'durations_ms':[110,110,60,60,160,160],'body_armor_textures_andRGBA':True,
            'other_phase_axes':[0,2,4,5],'old_flags_and_V001':True,'combat_damage_range_clock_input':True},
        'semantic_grasp_or_helmet_clearance_complete':False,'GPU_clearance_accepted':False,'fullmotion_accepted':False,'formal_complete_units':0}
    new(OUT/'cpu-axis-comparison-v001.json',prediction)
    new(OUT/'primary3-marker-axis-candidate-v002.json',{'schema':'native175-primary3-axis-only-marker-candidate-v002',
        'original_marker':desc(MARKERS),'changed_frames':[1,3],'markers':candidate_markers,'durations_ms':marker_doc['durations_ms'],
        'actual_handle_center':None,'actual_blade_axis':None,'axis_authority':'Root-approved numerical trial only; GPU and grasp not accepted.',
        'sword_scale':.5,'independent_sword_grip':[99,256],'body_max_px':72,'Source_applied':False,'formal_complete_units':0})
    inline='''#pragma once
#include "DungeonFairytaleSwordPrimary3V001.inl"

// UNAPPLIED axis-only Root Bound-mode trial; keep V001 and all old flags unchanged.
// CPU nominal phase1 residual3core/17AA samples, +/-3source worst47core.
// Fixed original NearHand/Helmet86adjacent core hand pixels remain unchanged.
// Phase3 alpha-support center gap~4.19screenpx at UIScale1 is CPU, not GPU proof.
// All palms/roots/polygons/textures/72px/.50/timing are inherited exactly.
namespace DungeonFairytaleSwordPrimary3V002
{
using FMarker = DungeonFairytaleSwordPrimary3V001::FMarker;
inline int32 Count(const FString& Clip)
{ return DungeonFairytaleSwordPrimary3V001::Count(Clip); }
inline const FMarker* Find(const FString& Clip,int32 Frame)
{
    if(Clip!=TEXT("sword_primary_3") || Frame<0 || Frame>=Count(Clip))return nullptr;
    static const TArray<FMarker> Markers=[]()
    {
        TArray<FMarker> Values;Values.Reserve(6);
        for(int32 SampleIndex=0;SampleIndex<6;++SampleIndex)
        {
            const FMarker* Base=DungeonFairytaleSwordPrimary3V001::Find(TEXT("sword_primary_3"),SampleIndex);
            if(!Base)return TArray<FMarker>();
            Values.Add(*Base);
        }
        Values[1].Axis=FVector2D(-.5,-.8660254037844386);
        Values[3].Axis=FVector2D(.9135454576426009,.4067366430758002);
        return Values;
    }();
    return Markers.IsValidIndex(Frame)?&Markers[Frame]:nullptr;
}
inline UTexture2D* GetTexture(const FString& Component,int32 Frame,
    TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{ return DungeonFairytaleSwordPrimary3V001::GetTexture(Component,Frame,Cache); }
} // namespace DungeonFairytaleSwordPrimary3V002
'''
    new(OUT/'DungeonFairytaleSwordPrimary3V002.inl',inline)
    for pin in pins:assert desc(Path(pin['path']))==pin
    assert desc(MARKERS)['sha256']==EXPECTED_MARKER and desc(WEAPON)['sha256']==EXPECTED_WEAPON
    print(json.dumps({'changed_frames':changed,'core_helmet_old_new':[comparisons[0]['variants'][x]['helmet_core_overlap_after_NearHand'] for x in ('old','candidate')],
        'any_helmet_old_new':[comparisons[0]['variants'][x]['helmet_any_alpha_overlap_after_NearHand'] for x in ('old','candidate')],
        'candidate_phase1_uncertainty_max_core':comparisons[0]['variants']['candidate']['sampled_worst_core_overlap'],
        'fixed_hand_helm_adjacency':comparisons[0]['fixed_NearHand_core_pixels_8adjacent_HelmetForeground_core'],
        'phase3_center_ground_screen_old_new':[comparisons[1]['variants'][x]['ground_margin_positive_above_464']['all_alpha_pixel_centers_screen_px'] for x in ('old','candidate')],
        'phase3_cell_ground_screen_old_new':[comparisons[1]['variants'][x]['ground_margin_positive_above_464']['full_source_pixel_cells_screen_px'] for x in ('old','candidate')],
        'phase3_candidate_9sample_min_minus1budget':comparisons[1]['variants']['candidate']['minus_1screenpixel_UNMEASURED_raster_budget'],
        'images_created_or_edited':0,'Source_applied':False},indent=2))

if __name__=='__main__':main()
