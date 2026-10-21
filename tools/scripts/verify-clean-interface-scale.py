"""Read-only EV-043 runtime observations; native pixels and visual review remain separate."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--archive', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
root = Path('F:/Ourgame')
archive = (root / '过程图稿与视频' / a.archive).resolve()
assert archive.parent == root / '过程图稿与视频'
report_path = archive / '原件/runtime-report.json'
report = json.loads(report_path.read_text(encoding='utf-8-sig'))
old_path = root / '过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v003/原件/runtime-report.json'
old = json.loads(old_path.read_text(encoding='utf-8-sig'))
rows = [r for r in report['trace'] if r.get('record_type') == 'scene_normal_input_post_batch_observation']
checks = []
def check(name, passed):
    checks.append(dict(name=name, passed=bool(passed)))

check('original_13_names_unchanged', report['required_check_names'] == old['required_check_names'] and len(report['required_check_names']) == 13)
actual_names = [c['name'] for c in report['checks']]
check('original_13_actually_passed', report['passed'] and len(actual_names) == len(set(actual_names)) == 13
      and sorted(actual_names) == sorted(report['required_check_names']) and all(c['passed'] for c in report['checks']))
check('actual_scene_profile', report['profile'] == 'scene_exploration_normal_inputs' and report['scene_exploration_proof_requested'] is True)
check('observations_exist', len(rows) > 20)
check('interface_off_every_observation', bool(rows) and all(r.get('interface_visible') is False for r in rows))
check('no_text_draws_every_observation', bool(rows) and all(r.get('rendered_text_draw_calls') == 0 for r in rows))
# Zero means not drawn on the last completed HUD pass, never a rendered size.
players = [r for r in rows if r.get('rendered_player_sprite_size', 0) > 0]
knights = [r for r in rows if r.get('rendered_knight_sprite_size', 0) > 0]
check('player_actually_drawn_at120', len(players) > 20 and all(r['rendered_player_sprite_size'] == 120 for r in players))
check('visible_knight_actually_drawn_at120', len(knights) > 5 and all(r['rendered_knight_sprite_size'] == 120 for r in knights))
check('observed_start_confirm_and_transfer_states', any(r.get('waiting_for_start') for r in rows)
      and any(not r.get('waiting_for_start', True) for r in rows)
      and any(r.get('needs_confirmation') for r in rows)
      and len({r.get('room_instance_id') for r in rows}) > 1)
result = dict(scope='Read-only actual observations; no GUI pixels/performance/full units/listening acceptance',
              source_events=['EV-043', 'EV-044'], archive=str(archive),
              runtime_report_sha256=hashlib.sha256(report_path.read_bytes()).hexdigest(),
              historical_13_reference_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(),
              observation_rows=len(rows), rendered_player_rows=len(players), rendered_knight_rows=len(knights),
              old_canvas=160, candidate_canvas=120, relative_scale=.75,
              all_passed=all(c['passed'] for c in checks), checks=checks)
out = (root / a.output).resolve()
assert out.is_relative_to(root / 'docs') and not out.exists()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result['all_passed'] else 1)
