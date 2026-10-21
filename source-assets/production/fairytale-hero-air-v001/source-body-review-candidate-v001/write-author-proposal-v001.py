"""Author JSON only. No image decoding, masks, raster edits or game writes."""
from pathlib import Path
import datetime, hashlib, json, math

R = Path('F:/Ourgame')
C = Path(__file__).resolve().parent
S = R / 'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/extraction-v001/run-Air6-shared-HD-v001'
M = R / '过程图稿与视频/2026-10-18_钟盔非攻击跳跃六相切帧审阅_v001'
E = Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-本项目E584-钟盔非攻击跳跃六相切帧审阅-v001/E-retention-index-v001.json')

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    p = Path(p); return dict(path=p.as_posix(), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def new(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')

retained = read(E)
assert retained['verification_passes'] == 2 and retained['source_and_member_hash_mismatches'] == 0
assert Path(retained['source_archive']).resolve() == M.resolve()
source_rows = read(S / 'frames/frames-manifest.json')['rows'][0]['frame_records']
before = [pin(S / f'frames/jump_nonattack/frame-{i}.png') for i in range(6)]
for i, source in enumerate(before):
    copy = pin(M / f'展示副本/frame-{i}.png')
    assert (source['bytes'], source['sha256']) == (copy['bytes'], copy['sha256'])
    assert any(x['member'] == f'展示副本/frame-{i}.png' and x['bytes'] == source['bytes'] and x['sha256'] == source['sha256'] for x in retained['files'])

# Hand-authored rough visible contours from actual original512 Views. Root must
# inspect/rasterize/refine separately. These are NOT bone/socket/alpha masks.
polygons = [
 {
  'NearHand': [[156,227],[175,229],[194,240],[192,255],[183,270],[178,284],[166,295],[148,296],[134,288],[125,276],[126,262],[136,248],[147,241]],
  'NearArmWithoutHand': [[179,220],[199,212],[220,211],[238,215],[247,224],[240,239],[218,247],[194,248],[178,237],[166,229]],
  'HelmetForeground': [[292,58],[329,58],[344,86],[324,101],[339,110],[362,123],[378,146],[382,170],[391,177],[391,197],[375,198],[376,225],[375,238],[369,252],[344,255],[302,243],[258,227],[224,213],[197,199],[197,185],[212,175],[221,153],[223,141],[236,132],[259,116],[286,108],[292,97]],
  'FarHandForeground': [[317,286],[335,283],[354,282],[369,287],[382,298],[387,315],[384,328],[372,333],[359,328],[350,326],[335,323],[321,313],[311,300]]
 },
 {
  'NearHand': [[148,283],[168,280],[187,291],[195,307],[193,322],[183,337],[166,344],[151,339],[141,329],[139,314],[143,298]],
  'NearArmWithoutHand': [[173,272],[190,265],[211,266],[228,276],[230,289],[211,299],[191,302],[179,294],[164,288]],
  'HelmetForeground': [[246,110],[272,102],[289,128],[276,140],[292,146],[316,153],[337,168],[348,190],[352,210],[361,210],[360,226],[352,227],[353,252],[351,269],[344,281],[313,285],[279,274],[241,264],[207,253],[177,249],[175,238],[189,230],[194,212],[194,203],[201,196],[216,173],[239,158],[258,150],[256,143]],
  'FarHandForeground': [[309,312],[326,309],[341,308],[354,313],[369,323],[374,338],[369,351],[356,356],[345,352],[331,352],[319,345],[307,334],[303,322]]
 },
 {
  'NearHand': [[150,321],[170,318],[189,328],[198,343],[197,356],[187,369],[174,377],[157,375],[146,367],[141,355],[143,341]],
  'NearArmWithoutHand': [[167,313],[186,303],[205,302],[222,310],[225,321],[213,334],[195,342],[181,335],[163,328]],
  'HelmetForeground': [[231,155],[256,146],[276,172],[263,182],[273,187],[297,192],[320,201],[339,218],[347,239],[354,244],[354,260],[348,261],[349,286],[347,303],[336,313],[308,315],[272,310],[234,301],[205,291],[176,288],[168,280],[178,270],[185,252],[185,245],[199,233],[214,211],[240,199],[250,191],[246,182]],
  'FarHandForeground': [[302,331],[319,326],[336,328],[350,335],[363,341],[371,354],[368,367],[355,374],[341,373],[327,368],[314,365],[301,354],[295,343]]
 },
 {
  'NearHand': [[146,229],[165,229],[184,241],[184,255],[172,269],[169,284],[155,298],[138,298],[124,289],[116,278],[117,264],[127,250]],
  'NearArmWithoutHand': [[164,232],[179,222],[197,214],[215,212],[230,216],[240,227],[237,242],[218,249],[190,249],[182,244]],
  'HelmetForeground': [[272,60],[307,58],[323,86],[308,99],[323,106],[345,116],[362,135],[373,159],[376,175],[385,180],[383,197],[367,197],[367,221],[365,233],[355,245],[327,247],[291,237],[254,224],[219,211],[190,198],[189,186],[206,174],[214,151],[215,141],[230,132],[252,116],[278,107],[284,98]],
  'FarHandForeground': [[322,282],[340,281],[355,282],[367,286],[382,285],[394,296],[398,311],[390,325],[377,330],[366,326],[348,324],[334,320],[323,310],[315,297]]
 },
 {
  'NearHand': [[135,303],[154,303],[175,314],[174,330],[164,342],[168,352],[161,366],[147,374],[130,371],[119,362],[116,347],[120,333],[123,315]],
  'NearArmWithoutHand': [[146,291],[166,283],[189,287],[209,295],[214,309],[202,323],[180,332],[164,320],[146,311],[130,305]],
  'HelmetForeground': [[275,146],[302,143],[318,169],[309,184],[320,191],[339,207],[351,230],[358,252],[365,259],[366,274],[360,279],[359,303],[363,315],[356,334],[342,340],[312,331],[281,319],[249,303],[218,291],[187,281],[172,271],[176,261],[189,249],[194,232],[199,220],[220,202],[248,190],[274,186],[281,175]],
  'FarHandForeground': [[317,337],[335,336],[350,340],[367,344],[383,350],[393,361],[397,373],[390,377],[383,369],[380,380],[374,385],[365,377],[359,372],[354,380],[344,378],[337,370],[325,368],[316,359],[312,348]]
 },
 {
  'NearHand': [[181,272],[203,272],[216,280],[220,294],[233,309],[235,323],[226,334],[212,337],[200,334],[191,330],[180,322],[173,310],[166,292],[169,280]],
  'NearArmWithoutHand': [[196,228],[208,226],[227,228],[235,243],[229,262],[215,286],[202,283],[181,275],[168,273],[171,254],[181,238]],
  'HelmetForeground': [[249,54],[277,48],[294,73],[282,86],[296,91],[315,100],[334,115],[345,135],[349,154],[361,159],[361,176],[350,177],[351,203],[350,219],[340,233],[309,235],[274,229],[239,218],[205,210],[180,203],[178,192],[188,181],[193,158],[197,149],[210,137],[226,116],[250,103],[261,92],[259,84]],
  'FarHandForeground': [[312,306],[325,307],[336,318],[346,326],[358,334],[367,345],[373,355],[369,366],[362,363],[358,351],[353,356],[348,362],[342,354],[337,346],[332,344],[322,339],[311,329],[307,317]]
 }
]
grips = [[151,269],[168,318],[167,351],[140,278],[143,351],[209,311]]
far_centers = [[355,311],[346,334],[340,351],[366,309],[361,361],[346,343]]
poses = ['RiseEarly','RiseLate','Apex','Fall','LandingImpact','LandingSettle']
axes = [[1/math.sqrt(1.04),.2/math.sqrt(1.04)] for _ in range(5)] + [[.94,-.341]]
frames = []
for i, owners in enumerate(polygons):
    bbox = source_rows[i]['bbox']
    owners = dict(owners)
    owners['BodyRest'] = [[bbox[0],bbox[1]],[bbox[2],bbox[1]],[bbox[2],bbox[3]],[bbox[0],bbox[3]]]
    frames.append(dict(frame=i,pose_label=poses[i],source=before[i],source_alpha_bbox=bbox,root_source_artist=[256,464],grip_source_artist=grips[i],axis_artist_directed=axes[i],far_hand_visible_center_artist=far_centers[i],near_hand_role='screen-left larger glove, not screen-right far hand',artist_visible_polygon_by_owner=owners,BodyRest_polygon_semantics='Bounding envelope ONLY; actual owner is remaining original source alpha after four priority owners. Not a precise torso outline.',near_hand_polygon_semantics='Visible brown near glove/cuff; no hidden fingers/wrist or bone estimation',author_point_uncertainty_source_px=6,Root_approved=False,source_fit_viewed=False,actual_weapon_contact_measured=False,physical_root_or_socket_measured=False))

proposal = dict(schema='Air253-six-source-five-body-owner-and-author-marker-proposal-v001',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_only=True,generation_request_id=253,source=pin(S/'frames/frames-manifest.json'),actual_View_evidence='Original512 frame0..5 plus retained contact; sole accepted Ready158 identity also viewed after E581 receipt/source SHA check',retention_E584=pin(E),reference_ready=pin(R/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'),body_owners=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground'],exclusive_pixel_priority=['NearHand','FarHandForeground','HelmetForeground','NearArmWithoutHand','BodyRest'],partition_rule='Root later intersects rough polygons with unchanged original alpha, assigns one source owner per nonzero-alpha pixel with declared priority, preserves original RGBA, puts all remainder in BodyRest; overlap0 and exact reconstruction must be separately checked.',suggested_LGT_stack=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','FarHandForeground','NearHand'],shared_body_scale=dict(source_canvas=512,standing_extent=416,display_standing_height=72,source_to_display=72/416,per_frame_scale_normalized=False,per_frame_geometry_warp=False),Root_semantics='Fixed display registration at current extracted exclusive bbox bottom464. It is a transparent virtual reference, NOT observed floor/foot/hip. Actual game H projection remains separate.',Grip_semantics='Artist intended future near-hand hilt point, manually estimated from visible glove; no weapon/hilt exists in these six sources, so actual contact is UNKNOWN.',Axis_semantics='Artist trial direction only: frames0..4 forward/down11.31deg to reduce helmet crossing; frame5 returns existing Ready direction near-19.94deg. Root must inspect actual independent SWD0.50 fit and dynamic31deg terminal rotation before approval.',fixed_weapon_scale_proposal=.5,masks_rasterized=False,body_layers_created=False,source_pixels_read_for_masking=False,images_generated_or_edited=False,actual_Source_Content_UE_changed=False,runtime_imported=False,runtime_trial_allowed=False,physical_sockets_measured=False,footlock=False,FinalAccepted=False,formal_complete_units=0,frames=frames)
new(C/'Air253-five-bodyparts-author-proposal-v001.json',proposal)

# Coordinate-only sanity: no image decoding or rasterization.
def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def strict_intersection(a,b,c,d):
    return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0
geometry=[]
for frame in frames:
    for owner, polygon in frame['artist_visible_polygon_by_owner'].items():
        assert len(polygon)>=3 and len(set(map(tuple,polygon)))==len(polygon)
        assert all(len(p)==2 and all(type(x)is int and 0<=x<=512 for x in p)for p in polygon)
        area=sum(polygon[i][0]*polygon[(i+1)%len(polygon)][1]-polygon[(i+1)%len(polygon)][0]*polygon[i][1]for i in range(len(polygon)))/2
        assert abs(area)>1
        crossings=[]
        for i in range(len(polygon)):
            for j in range(i+1,len(polygon)):
                if j==i+1 or(i==0 and j==len(polygon)-1):continue
                if strict_intersection(polygon[i],polygon[(i+1)%len(polygon)],polygon[j],polygon[(j+1)%len(polygon)]):crossings.append([i,j])
        assert not crossings,(frame['frame'],owner,crossings)
        geometry.append(dict(frame=frame['frame'],owner=owner,vertices=len(polygon),signed_area=area,strict_self_intersections=0))
assert before==[pin(S/f'frames/jump_nonattack/frame-{i}.png')for i in range(6)]
new(C/'coordinate-only-sanity-and-source-unchanged-v001.json',dict(schema='Air253-author-coordinate-only-sanity-v001',passed=True,polygons_checked=len(geometry),geometry=geometry,source_six_SHA_passes=2,source_six_unchanged=True,source_image_decoded_or_rasterized=False,masks_created=False,exact_partition_reconstruction_not_yet_checked=True,Grip_alpha_or_hilt_not_yet_checked=True,visual_reviewed_source_frames=6,source_fit_or_native_reviewed=False,FinalAccepted=False))
print(json.dumps(dict(proposal=pin(C/'Air253-five-bodyparts-author-proposal-v001.json'),polygons=len(geometry),source_six_unchanged=True,source_pixels_changed=False,masks_created=False),ensure_ascii=False))
