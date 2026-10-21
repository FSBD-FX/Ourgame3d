# EV047 双模型待机观察模式 v001

2026-10-15。此入口是新造型的过渡观察模式，只包含两套各 4 帧的 authored idle。场景仍用旧房间/地面/雾。它没有新造型的行走、攻击、装备适配、状态转换或音效，不能代替完整制作目标；内容单元仍为 0/15。

本次文件实现已交主任务审查，尚未由本实现者运行 UE / UBT、录制或播放动画。6 个 Python 合成合同测试、Python AST、PowerShell语法以及冻结 8 张源图的路径/SHA/RGBA/根点/时序预检已经实际执行通过。合成测试不是运行游戏证据；90 项既有 UE 检查及实际录制由主任务执行。

## 独立入口和隔离

- 只在 `-DungeonFairytaleLookdevPreview` 下进入新 HUD / GameMode 分支；该 flag 关闭时，四份原有文件的旧逻辑逐行保持，仅新增独立分支、字段及 include。
- HUD 只预载新 8 贴图与原房间素材；实际绘制不调用旧 Fighter sprite、Armor/XBW、grip、eye、武器尾迹、音频反馈或文字 HUD，也没有缺图时回旧身份的 fallback。
- GameMode 保持 `bWaitingForStart=true`，停止 Fighter actor tick / AI，并在原有战斗输入、重开及 simulation batch 前返回。A/D 仅修改独立的观察方向；不修改实际 Fighter Facing/位置、武器内核或资源值。
- D：hero 向右、stone 向左；A：hero 向左、stone 向右。镜像依据各自 native facing，而不是旧角色的统一朝向假设。
- 单独 `-DungeonFairytaleLookdevPreview` 可供手动静态位置观察。附加 `-DungeonFairytaleLookdevProof` 才创建新独立 Probe。

新 Probe 录制脚本同时携带 `-DungeonContentProof` / `-DungeonContentProofDir`，只为满足原生截图 helper 原有安装契约。HUD 新入口在旧 ContentProbe 创建位置之前返回，**不创建旧 ADungeonContentProbe，不执行旧29/90 profile**。旧 helper 与旧音画门不修改。

## 造型、时序和比例

冻结输入 manifest：`F:/Ourgame/source-assets/production/fairytale-lookdev-v001/manifests/import-lookdev-v001.json`，SHA-256 `f3cea39ccea3432568ef1e5f37d919f16b3fb083c4a47be22c8783287481b445`。

| | Hero | Stone |
| --- | --- | --- |
| UE 贴图目录 | `/Game/Production/ArtTrials/EV047/v001/HeroCommonIdle/` | `/Game/Production/ArtTrials/EV047/v001/StoneIdle/` |
| 名称 | `T_Fairytale_HeroIdle_000_v001` 至 `003` | `T_Fairytale_StoneIdle_000_v001` 至 `003` |
| 原画布 | 512×512 RGBA | 512×512 RGBA |
| native facing | +1 | −1 |
| 4 帧脚底根点 | [256,464] ×4 | [260,464], [257,464], [264,464], [265,464] |
| 源可见高度 | 416 ×4 | 387,377,401,381；均值386.5 |
| 固定显示画布 | 72×512/416 = 88.61538461538461 | 93.6×512/386.5 = 123.9927554980595 |
| 可见身高目标 | 72 px | 平均93.6 px；平均为 hero 1.3倍 |

每帧 167 ms，周期 668 ms，0..3 循环。显示由独立实时时钟采样，与被冻结的游戏 simulation time 分开。Stone 不逐帧更改 scale 来掩盖源帧高度差；因此“1.3倍”是平均高度关系，不是每帧精确比值。根点来自保全原帧的两足接触测量，不由盾锤的全体 bbox 推定。

在 1280×720 观察视口中，脚线放在 y=540（75%高），hero x=435.2（34%宽）、stone x=819.2（64%宽）。HUD 使用现有 `Ground` 公式的逆投影得到这两个观察锚点的地面坐标，再由正投影绘制；这些不是实际 Fighter 的移动结果。截图观测记录 ground、camera ground center、ground screen、top screen、root、native/观察 facing、flip、canvas size、frame/sample、实际贴图路径和真实 HUD draw serial，便于独立检查。

## 独立真实录制

主任务完成 build、冻结快照和实际 8 纹理导入后，唯一 UE 操作者执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File F:\Ourgame\tools\scripts\verify-fairytale-lookdev.ps1 -Version 1
```

EngineRoot 默认 `G:\UE_5.5`；每次必须使用未占用版本。默认写入 `F:/Ourgame/过程图稿与视频/2026-10-15_暗黑童话双模型待机真实观察_v001/`（日期取实际执行日）。脚本拒绝覆盖旧批次，拒绝与其他 UE 进程并行，也不执行构建/导入。实际展示前仍由主任务完成 E 盘保全并维护版本索引。

Probe 预热2s，保全一张同步 prewarm，然后记录约7.2s。正常按键按 D/A/D 每段约2.4s切方向；另通过 Controller 的正常 key 请求短按 W/S/J/K/E/Q/T/R/Enter/Space/Shift，检验这些输入未推进被冻结的原游戏。Probe 不直接设置观察 Facing，也不写 Fighter / 战斗状态。

原生 PNG 使用未修改的无损 screenshot callback、Windows CREATE_NEW 排他文件预留、深拷贝 CRC、单 FIFO 异步写入和真实 flush。新只读 checker 校验每一张 PNG 的原始 BGRA8 CRC、全名集/唯一名/序号/计数/事件时序、prewarm、停止后队列清空、实际 HUD 双朝向全部4帧及各至少2次真实 3→0采样跨环。索引3→0就是第四帧返回第一帧，不能靠文件名/帧数冒称已经播放并审查循环。

此 profile 明确无录音：`audio_capture_started=false`、`native_async_flush_after_audio_stop=false`，以 `capture_stop_before_flush` 记录实际停止边界。它不把没有发生的 audio stop 写成 true。新 checker 使用相同严格 native 像素/写入合同，并自行核验 silent stop；不调用要求实际录音的旧 combat/native 音频边界检查，更不放宽旧门。

展示 MP4 使用真实原 PNG 的 monotonic 时间戳重采样至30fps，`-an`，全段解码；没有生成补间图、合成波形、源音频替换或所谓试听结果。运行通过后仍标 `motion_reviewed=false`、`new_style_accepted=false`、`formal_complete_units=0`，直到实际连续播放审查单独留证。

只读复查（不启动 UE、不重写报告）示例：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File F:\Ourgame\tools\scripts\verify-fairytale-lookdev.ps1 -InspectArchive 'F:\Ourgame\过程图稿与视频\2026-10-15_暗黑童话双模型待机真实观察_v001'
```

## 文件范围与后续门

新增 Source：`F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleLookdevState.h`、同目录 `DungeonFairytaleLookdevProbe.h/.cpp`。现有四份文件仅增加 opt-in 入口：同目录 `DungeonHUD.h/.cpp`、`DungeonGameMode.h/.cpp`。

新增独立工具：`F:/Ourgame/tools/scripts/verify-fairytale-lookdev.ps1`、同目录 `verify-fairytale-lookdev.py`；合成拒绝测试：`F:/Ourgame/tools/tests/test_fairytale_lookdev_verifier.py`。未编辑旧 ContentProbe、旧截图 helper、旧测试、旧 capture 脚本或冻结 manifest。

实际 build90、原29回归适用范围、原帧/视频生成完整性、F/E保全和连续动态审查由主任务补证。待机观察通过也仍需新行走、攻击/三段连击、受击/死亡等真实动作和装备分层/武器 socket，再进入完整内容单元验收；不能用静态平移当行走，不能混用新 idle 与旧身份的攻击后宣布完成。
