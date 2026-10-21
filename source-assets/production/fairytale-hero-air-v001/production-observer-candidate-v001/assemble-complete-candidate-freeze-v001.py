"""Package already-frozen NEW observer candidates; no UE or actual-source writes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = Path('F:/Ourgame')
SOURCE_SHA = 'e7b9f44fe53fa2c827d962b359494badf2efbf1ffb8d2e2face8dd2449fa6140'
OLD_CHECKER_SHA = '0883605a2d612fc979d3adb68e3df8191969d288e196db3dd2424efe061a34b6'


def pin(path):
    p = Path(path).resolve()
    data = p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def check(row):
    p = Path(row['path'])
    actual = pin(p if p.is_absolute() else ROOT / p)
    if (actual['bytes'], actual['sha256']) != (row['bytes'], row['sha256']):
        raise ValueError('Frozen member changed: ' + str(row['path']))


def write_new(path, value):
    p = Path(path)
    p.resolve().relative_to(HERE)
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with p.open('xb') as f:
        f.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checker-freeze', required=True)
    parser.add_argument('--checker-sha256', required=True)
    parser.add_argument('--protocol', required=True)
    a = parser.parse_args()
    source_path = HERE / 'HeroAir-production-observer-source-freeze-v001.json'
    old_checker_path = HERE / 'tooling/Air-production-proof-checker-freeze-v001.json'
    checker_path = Path(a.checker_freeze).resolve()
    protocol_path = Path(a.protocol).resolve()
    checker_path.relative_to(HERE)
    protocol_path.relative_to(HERE)
    source_pin, old_checker_pin, checker_pin, protocol_pin = map(pin, (source_path, old_checker_path, checker_path, protocol_path))
    if source_pin['sha256'] != SOURCE_SHA or old_checker_pin['sha256'] != OLD_CHECKER_SHA or checker_pin['sha256'] != a.checker_sha256:
        raise ValueError('Expected immutable source/checker freeze differs')
    freezes = [read(p) for p in (source_path, old_checker_path, checker_path)]
    by_path = {}
    for frozen in freezes:
        rows = frozen.get('members', frozen.get('files'))
        if not isinstance(rows, list) or not rows:
            raise ValueError('Frozen membership absent')
        for row in rows:
            Path(row['path']).resolve().relative_to(HERE)
            if row['path'] in by_path and by_path[row['path']] != row:
                raise ValueError('Overlapping immutable pins conflict')
            by_path[row['path']] = row
    for p in (source_path, old_checker_path, checker_path, protocol_path):
        row = pin(p)
        by_path[row['path']] = row
    for repeat in range(2):
        for row in by_path.values():
            check(row)
    old_result_pin=freezes[1]['accepted_host_result']
    delta_result_pin=freezes[2]['accepted_delta_host_result']
    for row, expected_count in ((old_result_pin,13),(delta_result_pin,10)):
        check(row)
        result=read(row['path'])
        if result['passed'] is not True or result['tests'] != expected_count or result['failures'] != 0 or result['errors'] != 0 or result['sources_unchanged'] is not True:
            raise ValueError('Accepted host result is not exact expected passing version')
    fixture_pin = freezes[1]['synthetic_fixture_provenance']
    check(fixture_pin)
    fixtures = read(fixture_pin['path'])
    for repeat in range(2):
        for row in fixtures['files']:
            check(row)
    baseline_rows = read(HERE / 'immutable-baseline-input-pins-v001.json')
    if isinstance(baseline_rows, dict):
        baseline_rows = baseline_rows.get('files', baseline_rows.get('members', baseline_rows.get('pins')))
    if not isinstance(baseline_rows, list):
        raise ValueError('Immutable baseline list absent')
    for row in baseline_rows:
        check(row)
    protocol = read(protocol_path)
    checker_entry = HERE / protocol['checker_entry']
    if pin(checker_entry)['path'] not in by_path:
        raise ValueError('Current checker entry absent from frozen execution closure')
    review = dict(
        schema='HeroAir-production-observer-independent-host-review-v001',
        created_utc=datetime.now(timezone.utc).isoformat(),
        source_probe_freeze_pin=source_pin,
        old_checker_freeze_pin=old_checker_pin,
        current_checker_freeze_pin=checker_pin,
        current_protocol_pin=protocol_pin,
        unchanged_v001_behavior_13_PASS=old_result_pin,
        current_v002_relative_and_source_chain_10_PASS=delta_result_pin,
        main_native_checker_and_other_algorithm_AST_unchanged=True,
        source_and_both_checker_execution_closures_two_SHA_mismatches=0,
        bulk_synthetic_fixture_pin=fixture_pin,
        bulk_synthetic_fixture_files=fixtures['file_count'],
        bulk_synthetic_fixture_bytes=fixtures['source_bytes'],
        bulk_synthetic_fixture_two_SHA_mismatches=0,
        originals_not_copied_or_deleted=True,
        old_baseline_actual_source_pins_unchanged=True,
        independent_read_paths=['preflight', 'actual49_BGRA_to_RGBA', 'float_quad_single_reflection', '3jump_None6_LGT9_landing_rejump', 'PNG_CRC_FIFO_StopFlush', 'fixed_Dodge_optics', 'main_submix_PCM_duration', 'fresh_PID_pair'],
        old_v001_blocker=dict(function='air_production_contract_v001.frozen',
            actual_reproduced_exception='FileNotFoundError: F:/Ourgame/before-source/DungeonFairytaleSwordAirV001.cpp',
            reason='Production 42-member freeze uses paths relative to its own folder; v001 used F:/Ourgame',
            old_frozen_bytes_preserved=True),
        source_chain_old_before_not_an_after='Production fallback must select existing-source/new-source, never before-source; six current production rows plus three observer rows are legal',
        actual_observer_link_failure_read_only_pin=pin(ROOT/'UnrealGame/Saved/Bootstrap/build-editor-20261019-010618.log'),
        actual_link_failure='Three LNK2019 RHI imports and LNK1120; C++/UHT compilation is not DLL-link success. Root owns NEW explicit RHI Build.cs repair and current CM binding; do not alter frozen observer to hide this failure.',
        unchanged_source_probe_three_files=freezes[0]['source_files'],
        fixed_thresholds=dict(body_min=150,body_median_max=40,body_error_limit=55,body_fraction_min=.60,blade_min=8,blade_median_max=50,blade_error_limit=65,blade_fraction_min=.60),
        actual_UE_started=False,
        actual_Source_Content_E_ledger_writes=0,
        actual_native_GPU_audio_listening_proved=False,
        final_visual_acceptance=False,
        FinalAccepted=False)
    review_path = HERE / 'independent-host-checker-review-v001.json'
    write_new(review_path, review)
    handoff = f'''完整候选仅供 Root 实际准入与验证；本打包脚本没有启动 UE、写 actual Source/Content/E/ledger 或创建批准。

当前源码 freeze：{source_pin['sha256']}（14 members，三个准入 Source），保持旧 baseline h/cpp 原 bytes。
当前独立 checker freeze：{checker_pin['sha256']}。
当前协议：{protocol_path.as_posix()}。
旧 checker v001 freeze {old_checker_pin['sha256']} 原位保留；它不能用于真实 full-production preflight，因为相对42-member闭包从错误根目录解析。

总 freeze 是补充打包索引。Root prereg 的 source_probe_freeze_pin 仍绑定源码 freeze e7b9...，checker_freeze_pin 绑定上方当前 checker，不把总 freeze 冒充实际准入或批准。

Root 先确认实际48 import、Production1419、当前源码和 DLL、逐条完整203GREEN，再准入两个新观察器 Source 与窄 HUD overlay 并真实编译。Production after_files 可列最终6项，observer after_files列最终3项；旧7项准入历史/HUD overlay单独留存，不伪称旧 HUD bytes 仍是当前 CM。

已只读核真实 build-editor-20261019-010618.log 的三项 RHI LNK2019/LNK1120。静态头文件可见不能证明模块链接；旧失败保留，Root负责NEW显式RHI Build.cs补充修复与实际准入记录。必须观察器准入/修复后的当前 DLL 真正链接成功，再以当前源码/同 NativeRHI 全203严格GREEN绑定最终CM，不能以此前Source294通过替代当前296验证。源码 e7b9 和旧静态审查原件均不倒改。

Root 为每侧建立独立实际 prereg 与 archive：root_run_directory = archive根，DungeonContentProofDir = archive/原件；index.json 必须记录真实退出码/PID及对应pins。不得同时启动旧baseline/ContentProbe。启动前49实际原RHI和editor source的98原bin读回全部完成并Flush；之后按真实audio Recording原点→movie/普通输入→最后真实callback Stop→terminal→PNGFlush。

Probe 核心flags：-DungeonHeroAirProductionProofV001 -DungeonFairytaleSwordAirPreview -DungeonFairytaleSwordEquipmentBoundPreview -DungeonContentProof -DungeonFastLosslessCapture -DungeonAsyncLosslessCapture -DungeonHeroAirProductionFacing=-1或1；仅当 Root prereg 明确允许时加 -DungeonHeroAirProductionClearKnightDiagnostic。保持普通variable clock/隐藏UI/rangeoff，不加固定步长、时间/角色/HP/Guard改写。

普通Enter→定向A/D→NoArmor6六相Space→普通E换LGT→LGT9六相Space→原landing[.06f,.12f)普通Space再次跳→第三跳六相→相邻两次普通Ready。左右fresh PID。没有gameplay jumpId，只重算实际H/V的观察序号；NoArmor不计正式20搭配。

PowerShell运行工具（占位符由 Root 换成真实新路径；本脚本没有执行这些未来命令）：
```powershell
$airPython='F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$airCheck='{checker_entry.as_posix()}'
& $airPython -B -X utf8 $airCheck --source-only
& $airPython -B -X utf8 $airCheck --verify-preflight --root-prereg '<Root实际新批准.json>'
& $airPython -B -X utf8 $airCheck --native --root-prereg '<同一实际批准.json>' --archive '<实际archive根>' --output '<NEW独立host结果.json>'
& $airPython -B -X utf8 $airCheck --paircheck --left-prereg '<实际left批准>' --left-archive '<leftarchive>' --right-prereg '<实际right批准>' --right-archive '<rightarchive>' --output '<NEWpair结果.json>'
```

所有 source-pixel 门槛、单次镜像、实际float几何、PNG CRC/FIFO、原PCM时长/非静音门不变。失败原件保留，工具修复走NEW版本。约 {fixtures['source_bytes']:,} bytes 的480份合成fixture仍在原位，按独立provenance两SHA核，未复制到E、未当原生媒体；总freeze只索引其provenance，不自称包含全部fixture payload或全部49源PNG。源49闭包仍由原native-ready e378...、E599/E600与固定输入索引约束。

事实：候选源码静态审查、冻结闭包与主机算法/反例有记录。推理：这些可支持 Root 开始真实编译和原生验证。风险：运行时49纹理、原生动作覆盖/重跳、动态起落与Ready身形衔接、各cue辨识和听感仍由真实录制判定；本候选不声称它们通过。landing J/Shift/真实save_restore/正式20搭配/最终画风仍OPEN。
'''
    handoff_path = HERE / 'COMPLETE-HANDOFF-v001.md'
    with handoff_path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(handoff)
    for p in (review_path, handoff_path, Path(__file__)):
        row=pin(p); by_path[row['path']]=row
    rows = sorted(by_path.values(), key=lambda r:r['path'])
    for repeat in range(2):
        for row in rows:
            check(row)
    output = dict(schema='HeroAir-production-observer-complete-candidate-freeze-v001',
        created_utc=datetime.now(timezone.utc).isoformat(), member_count=len(rows), members=rows,
        source_probe_freeze_pin=source_pin, current_checker_freeze_pin=checker_pin,
        old_checker_freeze_pin=old_checker_pin, current_protocol_pin=protocol_pin,
        bulk_synthetic_fixture_provenance=fixture_pin,
        bulk_fixture_payload_in_members=False, fixture_payload_independently_checked_twice=True,
        verification_passes=2, mismatches=0, actual_UE_started=False,
        actual_Source_Content_E_ledger_writes=0, actual_native_passed=False,
        actual_GPU_bytes_proved=False, audio_listened=False, visual_reviewed=False,
        root_actual_admission_and_runtime_proof_required=True, FinalAccepted=False)
    output_path = HERE / 'HeroAir-production-observer-complete-freeze-v001.json'
    write_new(output_path,output)
    print(json.dumps(dict(freeze=pin(output_path),members=len(rows),two_SHA_mismatches=0,bulk_fixture_files=fixtures['file_count'],bulk_fixture_bytes=fixtures['source_bytes'],UE_started=False,FinalAccepted=False),ensure_ascii=False))


if __name__ == '__main__':
    main()
