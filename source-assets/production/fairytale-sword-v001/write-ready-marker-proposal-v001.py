"""Freeze source-bound visible-hand estimates; never rewrite extracted images or receipts."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parent; M=R/'ready-measurement-v001'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
e=json.loads((M/'pixel-evidence-v001.json').read_text(encoding='utf-8'))
polys=[
 [[242,256],[264,256],[274,262],[279,270],[278,281],[274,286],[272,297],[266,303],[246,305],[232,301],[225,295],[225,278],[231,267]],
 [[243,256],[265,257],[275,263],[280,271],[279,282],[274,287],[272,297],[266,302],[246,304],[232,300],[225,294],[225,277],[232,266]],
 [[245,259],[265,259],[275,264],[280,272],[279,284],[275,288],[272,299],[266,304],[247,306],[232,302],[225,296],[225,279],[233,268]],
 [[243,256],[264,256],[274,262],[279,270],[279,282],[274,286],[272,297],[266,303],[246,305],[232,301],[225,295],[225,278],[231,267]]]
grips=[[258,282],[258,281],[259,284],[258,282]]
rows=[]
for i,r in enumerate(e['frames']):
 im_path=Path(r['source']['path'])
 assert desc(im_path)==r['source']
 rows.append({'frame':i,'source':r['source'],'near_hand_crop':r['diagnostic_crops'][0],
  'source_root_px':[256,464],'root_basis':{'near_boot':r['near_boot'],'far_boot':r['far_boot'],'two_contact_mean_x':r['dual_visible_contact_center_x'],
   'interpretation':'Use the near sole lower edge y464 and approximately centered two visible boot contacts. Far sole is 3px higher in this fixed3/4 image; do not force both feet onto one source Y.'},
  'grip_candidate_px':grips[i],'grip_uncertainty_px':3,
  'handle_axis_candidate_xy':[0,-1],'axis_uncertainty_degrees':10,
  'axis_evidence':'Visible approximately horizontal curled-finger creases suggest a vertical held cylinder. The hidden cylinder and its directed blade end are not observable; this is a trial alignment estimate, not exact physical ground truth.',
  'visible_fist_replay_polygon_candidate_px':polys[i],
  'polygon_basis':'New manual trace from this retained original source-hand crop, covering the visible fist and black edge while excluding the cuff and belt. No old V007 polygon/root/marker reused. Approximate1-2px boundary; not a certified semantic mask.',
  'closed_finger_crease_visibility':'Four curled-finger bands/creases are readable; no separate far hand overlaps this fist.',
  'thumb_independently_visible':False,'thumb_status':'Cannot independently isolate a thumb crossing the index/middle finger from these source pixels. Do not label thumb anatomy accepted.',
  'occlusion_status':'Only an approximate whole visible near-fist replay polygon is proposed. It does not prove which hidden thumb/finger should cover a later weapon; require actual sword overlay review.'})
out={'schema':'fairytale-sword-ready-source-marker-proposal-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
 'component':'SwordReady','state':'sword_ready_idle','frame_count':4,'durations_ms':[167]*4,'source_native_facing':1,
 'source_canvas_px':[512,512],'shared_row_ratio':0.7111111111111111,'per_frame_scale':False,
 'fixed_display_canvas_at1280x720':72*512/416,'max_visible_height_px':72,
 'visible_body_heights_source_px':[415,416,415,415],'frames':rows,
 'actual_viewed':['run-ready-v001/qa/sword_ready_idle-contact.png']+[f'run-ready-v001/curated/frame-{i}.png' for i in range(4)]+[f'ready-measurement-v001/frame-{i}-near_hand-diagnostic.png' for i in range(4)]+['ready-measurement-v001/frame-0-feet-diagnostic.png'],
 'motion_played':False,'ue_imported':False,'art_accepted':False,'trial_candidate_only':True,'formal_complete_units':0,
 'scope':'Actual visible pixels establish a usable Ready pose candidate and reproducible alignment estimates. Thumb and sword overlay remain open; this is not full action/armor/combat acceptance.'}
p=M/'ready-marker-proposal-v001.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=R/'ready-extraction-v001/actual-static-review-v001.md';assert not review.exists()
review.write_text('''# Native155 Ready: source-bound trial candidate

2026-10-16. Actually viewed all four E127-retained512RGBA frames, their contact sheet, all four E129-retained unscaled near-hand crops and frame0 feet crop. No GIF playback or UE review occurred.

The canonical squat bell helmet, dark cloth and brown gloves/boots remain recognizable. The image-left larger near arm ends in one closed fist across the chest; the far hand is separate at the right. Four subtle drawn poses preserve broadly stable body/helmet volume. Standard shared ratio32/45 gives source body heights415/416/415/415; fixed display canvas88.6153846154 would produce at most72px body height without per-frame scaling. Exact source hashes and proposed markers are in `ready-measurement-v001/ready-marker-proposal-v001.json`.

Visible curled finger creases support a roughly vertical invisible handle. The proposed grip positions are [258,282], [258,281], [259,284], [258,282], with ±3px alignment uncertainty and roughly ±10° axis uncertainty. They are estimates from visible fist pixels, not copied design markers or proof of a hidden handle. Four new approximate visible-fist polygons exclude cuff/belt; they are not certified semantic masks.

The separate thumb across the curled fingers cannot be independently read. Keep thumb anatomy and actual sword/finger occlusion unaccepted. These frames can support a clearly marked Ready alignment trial if root chooses; they cannot support a claim that correct thumb anatomy, continuous idle motion, sword overlay, armor combinations or the complete unit are finished.

Boot-ROI alpha≥128 shows the near sole last pixel y463/lower edge464 and far sole y460/lower edge461 in all four. Their mean contact X is255.75/256/255.5/256.5. A fixed[256,464] root is a reasonable near-ground display pivot; it does not certify both shoes share a source ground depth. No pixels, scale, timing, old markers, root472 or XBW sockets were changed or transplanted.
''',encoding='utf-8')
files=[p,review,Path(__file__).resolve(),R/'primary1-extraction-v001/actual-rejection-review-v001.md']
freeze=M/'review-marker-freeze-v001.json';assert not freeze.exists();freeze.write_text(json.dumps({'file_count':len(files),'total_bytes':sum(x.stat().st_size for x in files),'files':[desc(x) for x in files],'status':'Source-only Ready trial marker estimates + rejected156 evidence; no formal acceptance.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposal':desc(p),'review':desc(review),'freeze':desc(freeze)},ensure_ascii=False))
