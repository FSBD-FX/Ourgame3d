"""Read an actual retained room-flow report; no UE, images or state mutation."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
report=Path(a.report).resolve();d=json.loads(report.read_text(encoding='utf-8-sig'))
rows=[(i,x) for i,x in enumerate(d.get('observations',[])) if x.get('native_dodge_phase')==1]
result=dict(schema='actual-hero-dodge-trace-gap-audit-v001',actual_report=report.as_posix(),actual_dodge_frames=len(rows),visual_reviewed=False,Source_modified=False,frame_evidence=[])
for i,x in rows:
    result['frame_evidence'].append(dict(index=i,sim=x.get('sim'),hero_clip=x.get('hero_clip'),action_pose_supported=x.get('hero_action_pose_supported'),LGT_drawn=x.get('LGT_drawn'),texture=x.get('actual_rendered_player_texture'),stack=x.get('actual_rendered_player_stack'),canvas=x.get('hero_canvas_size'),rendered_size=x.get('rendered_player_size')))
gap=[x for _,x in rows if x.get('hero_clip')=='sword_ready_idle' and x.get('hero_action_pose_supported') is False and x.get('LGT_drawn') is False]
result.update(status='MISSING_ACTUAL_DODGE_DATA' if not rows else 'ACTUAL_DODGE_READY0_GEAR_LOSS_OBSERVED' if gap else 'ACTUAL_TRACE_REQUIRES_STATE_AND_VISUAL_REVIEW',bare_Ready0_gear_loss_frames=len(gap),all_state_art_accepted=False)
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(2 if not rows else 1 if gap else 0)
