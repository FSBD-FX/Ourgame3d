# v013 手动入口候选：LIMITED_WIP

本候选只准备八个既有手动入口与新版 wrapper/core；没有替换实际入口，没有启动 UE，也没有修改 Source、Content、实际 tools、README 或 E 盘。

八个 CMD 各只把调用路径 v012 改为 v013。原 v012 全部游戏开关保留（包括 LeatherReady），唯一新增游戏开关为 `-DungeonFairytaleSwordAirPreview`。它使用正常 Enter / WASD / J / Shift / Space / E / R；不启用 ProductionProof、自动输入、诊断伤害、传统 HUD 或调试攻击范围。

当前固定输入为 CM296 / Production1419 / 严格203全绿：`52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62`，及 queued v003 checker freeze `a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46`。旧 v012 的 Source283 / Production1371 / 200 契约保留作为历史，不冒称其已适配当前输入。

Root 准入索引为 `Root-manual-entry-admit-index-v013.json`。实际 wrapper 目标为 `F:/Ourgame/tools/scripts/launch-guard-room-native-trial-v013.ps1`；wrapper 继续调用本冻结候选目录中的 core。未来 Root 自己写非模板批准至 `F:/Ourgame/source-assets/production/fairytale-hero-air-v001/root-manual-v013/manual-input-v013.json`，填入实际 prereg、独立 pair result、可见审阅 receipt 和本候选 freeze 的完整路径/字节/SHA。

批准范围只可为 `LIMITED_WIP`：实际关键帧已由 Root 审阅后才允许把 `Root_visible_keyframes_reviewed` 与 `manual_trial_allowed` 设为 true。`full_realtime_playback_reviewed=false`、`audio_listened=false`、`FinalAccepted=false`、`known_pose_join_refinement_open=true` 必须如实保留。本候选模板仍 `RootApproved=false`、`is_template=true`，并会在启动前拒绝。Root 还须根据实际轻甲 Air→Ready 新对照独立决定是否批准有限试玩；本候选不授予批准。

事实：v002 原生观察入口没有 LeatherReady 开关，实际回到 v006 灰甲；v013 保留旧手动入口的 LeatherReady，选择 v012 棕甲。推理：这可解释已观察到的颜色突变。风险：不能据此推定肩部体块、起落硬切或动作接续已经修好；需 Root 的实际新原生对照审阅。完整原速观看、试听和正式单元验收仍未完成。

最终 gate 已按 Root 明确选择：Root 准入保留冻结 v003 实际 paircheck 的完整输出。该冻结代码的每个 verify_native 分支会调用完整 C.preflight，涵盖全部历史 source/import/E 闭包；批准记录的 `full_preflight_evidence` 必须为 `frozen_v003_paircheck_each_native_branch`，所选 prereg 必须属于 pair 的一侧，左右都绑定同 CM / source freeze / checker freeze。启动时不重新展开历史 E 闭包，但继续逐一核当前 CM 全部1719成员的 bytes/SHA、Source296与Production1419目录精确成员集、实际 DLL，以及批准/CM/prereg/pair/checker全部成员/候选全部成员 pins。视觉 receipt 的内容解释与批准权威属于 Root 的非模板 checkpoint，本候选只验其固定字节与 SHA。

Root 已测旧全 preflight 单次约40–60秒 CPU；本候选没有重复该昂贵检查，也没有编造新的快检耗时。只验证脚本语法、八入口与旧开关差异、未批准模板拒绝，以及实际旧文件保持原字节；未用伪造批准做正向启动。

Root 实际准入前须重新验证所有 before pins 并保留旧八入口；本目录的候选、验证与原件副本均不等于实际准入或可见结果验收。
