"""Deterministic numeric/semantic audit; writes only the two audio-event-map docs.

No playback, audio rendering, engine invocation, or external calls. Stress mixes
exist only as float arrays in memory and are never exported as runtime evidence.
"""

import argparse
import ctypes
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def db(value):
    return round(20 * math.log10(float(value)), 6) if value > 0 else None


def measure(samples, rate):
    squared = samples * samples
    total = squared.sum()
    cumulative = np.cumsum(squared)
    percentiles = {
        str(percent): round(int(np.searchsorted(cumulative, total * percent / 100)) / rate, 6)
        for percent in (1, 10, 50, 90, 99)
    }
    spectrum = np.abs(np.fft.rfft(samples * np.hanning(len(samples)))) ** 2
    frequencies = np.fft.rfftfreq(len(samples), 1 / rate)
    edge = max(1, round(rate / 1000))
    return {
        "duration_s": len(samples) / rate,
        "sample_peak_dbfs": db(np.max(np.abs(samples))),
        "rms_dbfs": db(np.sqrt(np.mean(squared))),
        "clipped_sample_count": int(np.count_nonzero(np.abs(samples) >= 1)),
        "first_sample": float(samples[0]),
        "last_sample": float(samples[-1]),
        "head1ms_peak_linear": float(np.max(np.abs(samples[:edge]))),
        "tail1ms_peak_linear": float(np.max(np.abs(samples[-edge:]))),
        "max_adjacent_sample_delta_linear": float(np.max(np.abs(np.diff(samples)))),
        "raw_end_to_start_delta_linear": float(abs(samples[-1] - samples[0])),
        "energy_centroid_s": float(np.sum(np.arange(len(samples)) * squared) / (rate * total)),
        "cumulative_energy_time_s": percentiles,
        "power_spectral_centroid_hz": float(np.sum(frequencies * spectrum) / spectrum.sum()),
        "dc_mean_linear": float(samples.mean()),
        "analysis_only_not_click_or_loudness_acceptance": True,
    }


def load_ogg(path, decoder_path):
    class Info(ctypes.Structure):
        _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int),
                    ("channels", ctypes.c_int), ("format", ctypes.c_int),
                    ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]
    library = ctypes.CDLL(str(decoder_path))
    library.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(Info)]
    library.sf_open.restype = ctypes.c_void_p
    library.sf_readf_float.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int64]
    library.sf_readf_float.restype = ctypes.c_int64
    library.sf_close.argtypes = [ctypes.c_void_p]
    info = Info()
    handle = library.sf_open(str(path).encode("utf-8"), 0x10, ctypes.byref(info))
    if not handle:
        raise ValueError(f"Cannot decode {path}")
    try:
        buffer = (ctypes.c_float * (info.frames * info.channels))()
        if library.sf_readf_float(handle, buffer, info.frames) != info.frames:
            raise ValueError(f"Incomplete decode {path}")
        original = np.ctypeslib.as_array(buffer).copy().reshape(info.frames, info.channels)
    finally:
        library.sf_close(handle)
    mono = original.mean(axis=1).astype(np.float64)
    converted = np.interp(np.arange(round(len(mono) * 48000 / info.samplerate))
                          * info.samplerate / 48000, np.arange(len(mono)), mono)
    return converted, {
        "original_rate_hz": info.samplerate, "original_channels": info.channels,
        "original_sample_peak_dbfs": db(np.max(np.abs(original))),
        "model_conversion": "in-memory mean stereo to mono and linear interpolation to48kHz; not an exported asset or exact UE resampler",
    }


def stress_mix(name, schedule, arrays, scope):
    count = max(round(start * 48000) + len(arrays[cue]) for cue, start, _ in schedule)
    mixed = np.zeros(count)
    bound = 0.0
    voices = np.zeros(count, dtype=np.int16)
    for cue, start, gain in schedule:
        offset = round(start * 48000)
        source = arrays[cue]
        mixed[offset:offset + len(source)] += source * gain
        voices[offset:offset + len(source)] += 1
        bound += np.max(np.abs(source)) * gain
    return {
        "id": name, "scope": scope,
        "schedule": [{"cue": cue, "start_s": start, "gain": gain} for cue, start, gain in schedule],
        "measured_float_sum_sample_peak_dbfs": db(np.max(np.abs(mixed))),
        "over_fullscale_sample_count": int(np.count_nonzero(np.abs(mixed) >= 1)),
        "maximum_overlapping_finite_voices": int(voices.max()),
        "conservative_all_peaks_sum_dbfs": db(bound),
        "audio_output_created": False, "not_runtime_mix_evidence": True,
    }


def event(event_id, source, cues, when, gain, note, status="candidate_pending_audition"):
    return {"D12_event_id": event_id, "authority_source": source, "candidate_ids_or_paths": cues,
            "emit_when": when, "suggested_linear_gain": gain, "note_zh": note,
            "status": status, "auditioned": False, "runtime_mapping_accepted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    audio_root = root / "source-assets/production/audio-v001"
    manifest_path = audio_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    arrays, rows = {}, []
    for cue in manifest["cues"]:
        path = audio_root / cue["file"]
        if digest(path) != cue["sha256"]:
            raise ValueError(f"Source hash changed: {path}")
        with wave.open(str(path), "rb") as handle:
            if (handle.getnchannels(), handle.getsampwidth(), handle.getframerate()) != (1, 2, 48000):
                raise ValueError(f"Unexpected candidate format: {path}")
            samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype="<i2").astype(np.float64) / 32768
        arrays[cue["id"]] = samples
        rows.append({"id": cue["id"], "path": path.relative_to(root).as_posix(),
                     "sha256": cue["sha256"], "family": cue["family"], **measure(samples, 48000),
                     "auditioned": False, "loop_approved": False,
                     "semantic_loop_policy": "finite authoritative event one-shot only; zero sample boundary is not a sustained-loop contract"})

    cc0_paths = {
        "CC0-GENERIC-IMPACT": "source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactGeneric_light_000.ogg",
        "CC0-STONE-CONTACT": "source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMining_000.ogg",
        "CC0-SOFT-CONTACT": "source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactSoft_medium_000.ogg",
        "CC0-CLOTH": "source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth2.ogg",
        "CC0-PREP": "source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife1.ogg",
    }
    decoder = Path("G:/UE_5.5/Engine/Binaries/ThirdParty/libsndfile/Win64/libsndfile-1.dll")
    contacts = []
    for identifier, relative in cc0_paths.items():
        arrays[identifier], info = load_ogg(root / relative, decoder)
        contacts.append({"id": identifier, "path": relative, "sha256": digest(root / relative),
                         "license": "local_package_CC0", "auditioned": False, **info})
    scenarios = [
        stress_mix("duplicate_heavy_full_gain", [("AUD-GSW-WHOOSH-01", 0, 1)] * 2, arrays,
                   "Exact duplicate event worst case; should be prevented by identity dedupe, not accepted as normal combat."),
        stress_mix("all17_full_gain_same_time", [(cue["id"], 0, 1) for cue in manifest["cues"]], arrays,
                   "Deliberately implausible stress case showing individual headroom is not summing headroom."),
        stress_mix("sword_ground_chain_base", [("AUD-SWD-WHOOSH-01", .17, .25),
                   ("AUD-SWD-WHOOSH-02", .75, .25), ("AUD-SWD-WHOOSH-03", 1.36, .25)], arrays,
                   "v2 unmodified consecutive base timeline; no target contact, no statement of runtime acceptance."),
        stress_mix("spear_secondary_base_three_subhits", [("AUD-SPR-THRUST-01", .18, .25),
                   ("AUD-SPR-THRUST-02", .28, .25), ("AUD-SPR-THRUST-03", .38, .25)], arrays,
                   "The original spear skill has three SubHitIDs inside one AttackID; different from ordinary combo AttackIDs."),
        stress_mix("sword_and_one_generic_contact_current_scalars", [("AUD-SWD-WHOOSH-01", 0, .25),
                   ("CC0-GENERIC-IMPACT", 0, .45)], arrays,
                   "Static-code scalar check using historical source lineage; mono interpolation omits UE pitch/spatial/bus processing and is not actual runtime WAV."),
        stress_mix("wake_sword_two_stone_contacts_budget_scalars", [("AUD-STONE-AWAKE-01", 0, .18),
                   ("AUD-SWD-WHOOSH-01", 0, .25), ("CC0-STONE-CONTACT", 0, .15),
                   ("CC0-STONE-CONTACT", .04, .15)], arrays,
                   "Proposed first-unit numeric density check; not a recommended simultaneous event sequence or exported mix."),
    ]
    sword = [
        event("AUD-WPN-PREP", "DungeonContentCombat::Started", ["CC0-PREP"], "Accepted action starts; once per AttackID", .18,
              "drawKnife1峰值很低且0.400s长；仅材质候选，未确认适合作170/150/220ms前摇，不应盲目抬总线。", "material_candidate_gap"),
        event("AUD-WPN-SWING", "DungeonContentCombat::ActiveWindow", ["AUD-SWD-WHOOSH-01", "AUD-SWD-WHOOSH-02", "AUD-SWD-WHOOSH-03"],
              "Ground combo stage1/2/3 respectively; once per real AttackID/SubhitID", .25,
              "基础时轴击出在0.17/0.75/1.36s；实际使用已接纳最终时轴。空挥也有声，不能由命中或动画帧再发。"),
        event("AUD-WPN-SWING", "WPN-SWD-001 secondary accepted active window", ["AUD-SWD-WHOOSH-02"],
              "One actual secondary active window; unmodified onset0.20s", .25,
              "进身斜斩暂选第二段材料；不加位移/范围/额外伤害，正式技与普攻音色仍待听感区分。"),
        event("AUD-WPN-SWING", "Airborne primary actual first active window", ["AUD-SWD-WHOOSH-01"],
              "One first-stage attack per original airborne allowance", .25,
              "空中不连续接三段，不因落地补播第二次；仍用真实AttackID去重。"),
        event("AUD-DAMAGE-DIRECT", "Accepted effective damage receipt on target", ["CC0-STONE-CONTACT", "CC0-SOFT-CONTACT"],
              "actualDamage>0; choose exactly one target-material main contact", .15,
              "打石骑选石体、软体选软体；同段多目标40ms聚合最多2声，不能合并伤害收据。当前代码通用ImpactLight仍只是原型。"),
        event("AUD-WPN-MISS", "Original attack segment ends with no accepted hits", [], "Optional cosmetic only", 0,
              "建议静音，不能播碎裂/撞击假装命中；退出清理不是落空。", "intentional_optional_silence"),
        event("AUD-WEAPON-SWITCH", "Actual inventory/switch commit", ["CC0-CLOTH"], "Ownership/active weapon change committed", .08,
              "布料是换装材料，尚未定稿鞘/扣音；槽位预览不成功。", "material_candidate_gap"),
    ]
    knight = [
        event("AUD-DORMANT-AWAKE", "DungeonStoneKnight::WakeStarted", ["AUD-STONE-AWAKE-01"], "One actual wake event; warning lasts0.85s", .18,
              "声长0.65s，尾部静段不缩短0.85s可视苏醒；真实受伤/近触/兜底共用同WakeEventID。"),
        event(None, "DungeonStoneKnight::WakeCompleted", [], "Original wake completed", 0,
              "不再播苏醒、攻击或掉落成功。", "intentional_silence"),
        event("AUD-ENEMY-TELL-START", "DungeonStoneKnight::AttackStarted", ["AUD-STONE-ARMOR-SCRAPE-01"],
              "A1/A2 real windup begins", .20,
              "0.32s刮擦仅材质；A1锁点0.45s/A2锁点0.35s，不能把开始音当锁定。", "material_candidate_gap"),
        event("AUD-ENEMY-LOCK", "DungeonStoneKnight::AimLocked", [], "Exactly A1 start+0.45s or A2 start+0.35s", .20,
              "仍缺独立稳定短锁线音，不能用死亡碎裂或刹停冒充；视觉锁线必须可读。", "missing_critical_cue"),
        event(None, "DungeonStoneKnight::ChargeStarted", ["AUD-STONE-ARMOR-SCRAPE-01"], "Actual A1 charge starts at base0.90s; once", .18,
              "可暂用有限运动材料；不能按高频Movement或动画帧重复触发，不声明循环。", "material_candidate_gap"),
        event(None, "DungeonStoneKnight::Movement", [], "Numerous authoritative movement updates", 0,
              "此高频事件禁止默认一条一声。脚步/持续运动另需明确展示钩子。", "intentional_silence_hook_pending"),
        event("AUD-WPN-SWING", "DungeonStoneKnight::ActiveWindow for Shield", ["AUD-STONE-ARMOR-SCRAPE-01"],
              "Actual A2 shield sweep at base0.70s; once", .18,
              "只能作为盾体运动材料，不拿石翼音当盾撞成品；真实玩家命中另走接触声。", "material_candidate_gap"),
        event("AUD-DAMAGE-DIRECT", "DungeonStoneKnight::Hit then accepted player damage receipt", ["CC0-SOFT-CONTACT"],
              "Only effective target damage; target armor may change material selection", .15,
              "撞墙/碰盟友不产生玩家伤害音；轻甲没有新增格挡/反伤。"),
        event(None, "DungeonStoneKnight::ChargeStopped", ["AUD-STONE-CHARGE-BRAKE-01"],
              "One actual early stop or normal end; wall/body/valid-hit facts kept separate", .18,
              "刹停声不是命中或收益；停止先前运动尾声后播，不能同点同时叠整条刮擦和刹停。"),
        event("AUD-RECOVERY-OPEN", "DungeonStoneKnight::RecoveryStarted", [], "Only true recovery starts", 0,
              "可静音；A1完整1.60s/A2完整0.90s反击窗口不受声长影响。", "intentional_optional_silence"),
        event("AUD-DAMAGE-DIRECT", "DungeonStoneKnight::Damaged with accepted effective loss", ["CC0-STONE-CONTACT"],
              "Stone target actualDamage>0; one main contact", .15,
              "不套额外通用ImpactLight，不以每次削韧伪报破韧。"),
        event("AUD-POISE-BREAK", "DungeonStoneKnight::PoiseBroken", ["AUD-STONE-FRACTURE-01"],
              "Actual accepted break, not poise damage during protection", .18,
              "碎裂仅共享材质；死亡和破韧尚未做出稳定区别，完整声包仍有缺口。", "material_candidate_gap"),
        event("AUD-ACTOR-DEATH", "DungeonStoneKnight::Died", ["AUD-STONE-FRACTURE-01"],
              "Authoritative terminal death after same-time damage", .18,
              "同点死亡优先声部并取消破韧尾声，不叠两遍同文件；不等于奖励/清房/Boss胜利。", "material_candidate_gap"),
    ]
    armor = [
        event("AUD-INVENTORY-COMMIT", "D04 actual equip/drop/ownership commit", ["CC0-CLOTH"], "Actual LGT001 equip commit only", .08,
              "行路短衣轻步为常驻属性，保持静音；不能新造proc或换装回资源声。"),
        event("AUD-PLAYER-HURT", "Accepted effective player damage after invulnerability", ["CC0-SOFT-CONTACT"],
              "Actual hurt receipt, not every incoming collision", .15,
              "只有接触材料，没有非语言呼吸成品；若已播主接触则不再叠同一软体声。", "nonverbal_gap_no_duplicate_contact"),
    ]
    budget_rows = [
        ("critical_warning", 2, .20, .53, "highest; reserve source identity; stable distinct cue still missing"),
        ("player_swing", 1, .25, .48, "one per AttackID/Subhit; cosmetics cannot consume combat RNG"),
        ("main_contacts", 2, .15, .90, "40ms similar-material grouping; never merge damage receipts"),
        ("stone_motion", 1, .18, .53, "per actor one; stop/fade previous movement before brake/wake tail"),
        ("hurt_break_death", 1, .18, .53, "per actor terminal death > true poise break > hurt; no duplicate fracture"),
        ("ui_commit", 1, .08, .90, "neutral/equip cosmetic; success only actual receipt"),
    ]
    budget = [{"group": group, "max_voices": count, "max_linear_gain": gain,
               "assumed_max_source_sample_peak": peak, "policy": policy}
              for group, count, gain, peak, policy in budget_rows]
    bound = sum(count * gain * peak for _, count, gain, peak, _ in budget_rows)
    source_files = [manifest_path, Path(__file__),
                    root / "docs/production/first-batch-v2/combo-spec.md",
                    root / "docs/design/presentation-v1/audio-and-assets.json",
                    root / "docs/design/enemies-v1/enemies.json",
                    root / "UnrealGame/Source/CodexDungeon/DungeonFighter.cpp",
                    root / "UnrealGame/Source/CodexDungeon/DungeonStoneKnight.h"]
    report = {
        "schema_version": "1.0", "date": "2026-10-14", "timezone": "Asia/Shanghai",
        "status": "analysis_and_mapping_proposal_only_not_listening_or_runtime_accepted",
        "scope": "17 immutable candidate WAVs, selected existing CC0 materials, in-memory stress sums; no new sound files, UE execution, external API or game code edits",
        "source_refs": [{"path": path.relative_to(root).as_posix(), "sha256": digest(path)} for path in source_files],
        "playback_capability_check": {"native_windows_player": "System.Media.SoundPlayer",
             "actual_local_WAV_Load_completed": True, "Play_or_PlaySync_invoked": False,
             "agent_auditory_observation_tool_available": False, "external_audio_services_used": False,
             "auditioned_files": [], "auditioned_count": 0,
             "note_zh": "本机可以加载播放用WAV，但当前工具不能把本地播放声音返回给代理听辨；未播放/未听过，不能标试听完成。"},
        "candidate_count": len(rows), "all_candidate_hashes_match_manifest": True,
        "numeric_metrics": rows, "selected_CC0_materials": contacts,
        "metrics_limits": {"power_spectral_centroid": "numeric power centroid, not perceived brightness/naturalness",
             "max_adjacent_delta": "noise legitimately has fast internal changes; not a click detector",
             "edge_zero": "finite faded edges only; all17 remain non-looping by event semantics",
             "stress_sum": "deterministic aligned PCM float addition in memory, no limiter, reverb, buses or codec; not actual UE output",
             "sample_peak": "dBFS only; no BS1770 true-peak or LUFS claim"},
        "overlap_scenarios": scenarios,
        "unit_event_maps": {"WPN-SWD-001": sword, "ARM-LGT-001": armor, "ENM-STN-001": knight},
        "unit_only_voice_budget_proposal": {"scope": "one military-sword player plus one stone knight listening slice; music/ambience absent; not a replacement for whole-game D12 caps",
             "groups": budget, "maximum_voices": sum(row[1] for row in budget_rows),
             "conservative_sum_sample_peak_linear": bound, "conservative_sum_sample_peak_dbfs": db(bound),
             "assumptions": "source peaks/gains/concurrency caps actually enforced; no EQ boost, additional actors, music or postmix gain; not true-peak safety or perception acceptance",
             "ducking": "D12 proposed warnings duck music6dB and noncritical combat3dB with20ms attack/180ms release; future audition test required",
             "engine_implemented_or_tested": False},
        "runtime_static_snapshot": {"player_combo": "DungeonFighter ActiveWindow chooses stage-specific SWD/GSW/SPR asset and PlaySound2D gain0.25",
             "contact": "historical generic ImpactLight PlaySound2D gain0.45; pitch1.15 for enemies/0.9 for player; target-material routing not proven complete",
             "lineage": "historical E-root bootstrap report maps SW_ImpactLight to impactGeneric_light_000.ogg; local raw file audited, current UAsset decoding not performed",
             "stone_kernel": "WakeStarted/AimLocked/ChargeStarted/ChargeStopped/etc source events exist in pure kernel; this does not prove live UE actor audio routing",
             "audition_and_runtime_acceptance": False},
        "remaining_gaps": ["stable critical enemy lock cue", "distinct final poise-break versus death signatures",
             "auditioned final preparatory/equip/nonverbal cues", "actual spatial panning and voice-handle lifecycle integration",
             "actual event-dedupe, pause/continue cursor, cancel/death/room-exit lifecycle listening tests",
             "sample-true-peak/output codec/multi-actor mix verification"],
        "lifecycle": ["No replay of already consumed onset on save/resume or low-FPS catch-up.",
             "Motion voices end with real ChargeStopped/death/room cleanup; no loops per Movement update.",
             "Ordinary death does not stop already emitted projectiles; same-time damage resolves before reward/success.",
             "Warning identity may not randomize; cosmetic variants use presentation identity hash, not combat/loot RNG.",
             "All warning audio obeys mute while its visual direction/shape/timing remains readable."],
    }
    output = root / "docs/production/first-batch-v2"
    (output / "audio-event-map.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# 17条候选音效复核与首单元事件映射", "", "日期：2026-10-14。**实际听过0条。** 本轮只有真实源文件读取、确定性波形/频谱分析和内存重叠计算；没有新生成声音、外部API、UE运行或游戏代码改动。以下映射与预算均为待试听提案，不能标完整声包已完成。", "",
          "## 事实、推理与风险", "", "- 事实：17条原件哈希全部匹配audio-v001 manifest，仍为48kHz mono PCM16、无采样削波、首尾0值。Windows System.Media.SoundPlayer已成功Load已有WAV；没有调用Play/PlaySync，当前工具没有本地听感回传能力。", "- 推理：军剑三段可以按真实ActiveWindow分别消费三条短破风；石像苏醒/运动/刹停有材料候选。关键锁线、正式死亡与破韧区别仍没有完整成品，不能只凭17个文件宣布完整单元声音达标。", "- 风险：两条满增益重剑重复播放已能数值超满幅；单条5dB以上余量不代表叠层安全。零首尾只帮助有限one-shot，不证明燃烧或石翼适合循环。内部最大采样跳变主要含有噪声频率，不能当作已听见爆音。", "",
          "## 逐文件数值与语义", "", "原件目录：`source-assets/production/audio-v001`。首尾1ms幅度、频谱质心、能量分位时刻及全部SHA256见JSON。频谱/波形指标不等于音色评价。", "",
          "| 候选 | 时长ms | 采样峰值dBFS | 能量中心ms | 最大相邻采样差 | 循环/用途边界 |", "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        note = "仅有限事件one-shot，不循环"
        if "BURN" in row["id"]: note = "原有燃烧tick短纹理；不当连续火层/新伤害"
        if "FRACTURE" in row["id"]: note = "死亡/破韧共享材料，正式区别仍缺"
        if "WING" in row["id"]: note = "石翼动作，不借用为盾击成品"
        md.append(f'| {row["id"]} | {row["duration_s"] * 1000:.0f} | {row["sample_peak_dbfs"]:.3f} | {row["energy_centroid_s"] * 1000:.1f} | {row["max_adjacent_sample_delta_linear"]:.4f} | {note} |')
    md += ["", "各文件0→0边界没有原始端点台阶，但重复循环会反复出现8/15ms包络及静段，可能形成抽吸/拍动；本轮没有听感证据，17条全部保留`loop_approved=false`。破风能量中心晚于事件起点是包络事实，不能拿破风最响处代替敌人50%锁定信号。", "",
           "## 内存重叠计算", "", "下列均未输出音频文件，不是运行混音。CC0素材按均值转mono/线性插值，仅作近似；UE的pitch、空间、总线与编码未模拟。", "",
           "| 场景 | 浮点和峰值dBFS | 超满幅采样数 | 最大重叠声部 | 所有单峰相加的保守上界dBFS |", "| --- | --- | --- | --- | --- |"]
    for scenario in scenarios:
        md.append(f'| {scenario["id"]} | {scenario["measured_float_sum_sample_peak_dbfs"]:.3f} | {scenario["over_fullscale_sample_count"]} | {scenario["maximum_overlapping_finite_voices"]} | {scenario["conservative_all_peaks_sum_dbfs"]:.3f} |')
    md += ["", "首个重复重剑场景故意模拟去重失效；全17同点是极端压力而不是合法连招。军剑v2连续基础击出时刻为0.17/0.75/1.36s，枪技能子击为0.18/0.28/0.38s；这只是未修饰设计时轴，正式以已接纳最终动作事件为准。", "",
           "## 首个军剑／轻甲／石骑逐事件建议", ""]
    for unit, mappings in report["unit_event_maps"].items():
        md += ["### " + unit, "", "| 权威来源 / D12事件 | 候选 | 建议线性增益上限 | 触发与缺口 |", "| --- | --- | --- | --- |"]
        for row in mappings:
            md.append(f'| {row["authority_source"]} / {row["D12_event_id"] or "新增展示路由待明确"} | '+(", ".join(row["candidate_ids_or_paths"]) or "静音/缺口")+f' | {row["suggested_linear_gain"]:.2f} | {row["emit_when"]}；{row["note_zh"]} |')
        md.append("")
    md += ["候选路径：17条ID对应同名`__v001.wav`；CC0标记对应JSON `selected_CC0_materials`中的精确原路径与hash。它们沿用本地包许可，不把工具许可或原作素材引入项目。", "",
           "## 首单元试听台声部预算提案", "", "只适用于一名军剑玩家+一只石骑、无音乐/环境层的小试听台；不覆盖D12全游戏24非关键世界声/2UI/3音乐层的长期建议。8声上限及以下增益尚未实现或运行验证。", "",
           "| 分组 | 最大声部 | 线性增益上限 | 假定源采样峰值上限 | 策略 |", "| --- | --- | --- | --- | --- |"]
    for row in budget:
        md.append(f'| {row["group"]} | {row["max_voices"]} | {row["max_linear_gain"]:.2f} | {row["assumed_max_source_sample_peak"]:.2f} | {row["policy"]} |')
    md += ["", f'若所有源峰值/增益/并发帽都实际满足，无后级EQ/增益提升，保守同相和上界为{bound:.4f}，即{db(bound):.3f}dBFS。此值只是采样峰值算术，不是dBTP保证；加入其他敌人/音乐/后期处理后不再成立。预警仍应按D12建议对非关键战斗压3dB、音乐压6dB，20ms起/180ms回，最终需试听，不能靠本表宣称可听清。', "",
           "## 当前实现与后续边界", "", "当前Fighter静态源码在真实ActiveWindow选择三段破风，以PlaySound2D/0.25播放；通用受击仍是历史ImpactLight/0.45并有pitch变化，不等于已完成目标材质或石骑声包。历史导入报告把该UAsset溯源到impactGeneric_light_000.ogg，本轮只读了本地原OGG，未解码当前UAsset。纯石骑核已有WakeStarted/AimLocked/ChargeStarted/ChargeStopped等事件，但不证明其UE演员音频适配已经接通。", "",
           "后续先解决独立锁线签名与死亡/破韧区分，再验事件去重、可控运动声部、静音视觉冗余、暂停/恢复游标及取消/死亡/跨房清理。高频Movement不能每条一声；普通死亡不清已发弹；同点死亡/奖励严格沿权威结果。未消费的提示不能提前泄露休眠/future。", "",
           "可重跑分析：", "", "```powershell", "& 'C:/Users/22499/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'F:/Ourgame/tools/scripts/audit-first-content-sfx.py'", "```", "",
           "机器记录：[audio-event-map.json](audio-event-map.json)。重跑只更新本MD/JSON，不产生WAV或改变原始素材。", ""]
    (output / "audio-event-map.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"candidate_count": len(rows), "auditioned": 0,
                      "max_budget_voices": report["unit_only_voice_budget_proposal"]["maximum_voices"],
                      "budget_sample_peak_bound_dbfs": db(bound),
                      "overlap_scenarios": [{"id": item["id"], "peak_dbfs": item["measured_float_sum_sample_peak_dbfs"],
                                             "overfullscale": item["over_fullscale_sample_count"]} for item in scenarios]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
