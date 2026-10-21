"""Record actual in-progress checkpoint without mislabelling three expected REDs."""
from pathlib import Path
import json
R=Path('F:/Ourgame');p=R/'docs/production/first-batch-v2/progress.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['current_task']='v139守卫跺击闭环制作；新版本Source262已编译，Active/Recovery等待纠错原图批准与导入；原190通过、3个新增指定语义RED已保留'
d['last_fully_green_checkpoint']='v138-HeroDeath190G'
d['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261018-191818.log'
d['current_build_exit_code']=0;d['current_source_uncompiled_changes']=False
d['stomp_v139_work_in_progress']=dict(source_files=262,production_files=1326,source_compiled=True,
    last_test_source_files=260,last_test_report='UnrealGame/Saved/Automation/FirstRoom-20261018-191117/index.json',
    registered_tests=193,old_tests_passed=190,new_expected_semantic_RED=3,all_tests_green=False,
    stage0_snapshot='source-assets/production/backups/v139-Stomp-Stage0-three-semantic-RED-v001',
    overlay_rows_imported=False,native_stomp_complete=False,manual_current_checkpoint_ready=False,
    old44_profile_retained=True,Root_rejected_sources=[224,242,243,244,246,247],
    candidate245='E529 actual transparent review; Root limited source fit approved, no import/native claim',
    Active245_limited_source_fit_approved=True,Recovery_next_candidate=248,last_E_retention=536,
    native_calls_this_turn=6,requested_count=247,formal_complete_units=0)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
readme=R/'README.md';text=readme.read_text(encoding='utf-8-sig')
prefix='2026-10-18 v139制作中：正在补守卫跺击落脚与收招；Source262已编译，Production仍1326。原190项通过，新增3项准确保留“尚未接入”的语义RED，尚非193全绿。旧44配置保留；新的试玩检查点待动作源、导入和完整实景验证后更新。[制作计划](docs/production/first-batch-v2/guard-stomp-v139-plan.md)。\n\n'
if not text.startswith('2026-10-18 v139制作中：'):
    text=text.replace('2026-10-18 当前检查点（EV048，v138）：','2026-10-18 上个已验证检查点（EV048，v138）：',1)
    readme.write_text(prefix+text,encoding='utf-8')
print('Durable working status updated: Source262 compiled; last tested260;190+3RED; no new native/art completion claim.')
