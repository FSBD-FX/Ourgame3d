# Dodge UE 适配 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox (`- [ ]`) syntax. 本轮仅短计划、接口桩和可编译RED测试；根线程真实RED前禁止实施GREEN。

**Goal:** 正常左右Shift合并fresh输入，沿冻结Dodge v2实现真实移动/直接伤害保护和复合取消；保已有SWD、甲、石骑反馈与终局行为。

**Architecture:** 每角色长期持有一份FDodgeKernel。非dodge合法运动先由外层解析碰撞，再用actor-resolved-position-v1专域单调ID同刻CommitResolvedIdlePosition；活动dodge只镜像该核位置。GameMode按真实接触/动作时刻分段提交，Driver读取冻结的半开保护区间和运动段，不能由一个整批bool猜是否命中。

**Tech Stack / Spec:** UE5.5.4/MSVC14.38/C++17；D02 `/dodge`、`/equipment`、D03 `/use/precommit_cancel`、D04 `/action_policy`、现有combo-spec；[Dodge v2报告](F:/Ourgame/docs/production/first-batch-v2/dodge-kernel-report.md)、[独立复审](F:/Ourgame/docs/production/first-batch-v2/dodge-kernel-review.md)。

## 事实、判断、风险

真实起点：已读取ue-swd-skill-GREEN.json，22/22通过。Dodge纯核164项及复审11场景已报告通过，只覆盖核和内存合同，不能代替UE输入/物理/联合接触。

固定规则：地面、fresh、起招锁八向单位方向/无输入取facing；.4s、最大185cm、462.5cm/s、CD起招+1.2，保护[起招+.06,起招+.20)。受阻保完整动作/CD。Focus、旧hurt无敌、空攻预算仍各按现有唯一权威，dodge不扣/回任何资源、不清DoT、不返空攻。

未破韧正HP损失不取消dodge；真实区间外破韧和死亡才调用核Interrupt，立即重取裁短区间。攻击/技能/Q不能dodge取消；未提交甲/装备或装填只有成功dodge才原子取消，失败不得丢原工作。成功清主攻地面链/未执行缓冲，不能撤已接纳命中或退款。

共同前提：root独立SWD审查提出两个未复现候选——同5ms中早于技能发射的真实破韧可能迟至未来技能前踏/排伤后才提交；末窗批内初始LOS阻挡、稍后解除可能只测首次entry而漏余窗。独立review owner负责新DungeonSkillBoundaryReviewTests.cpp两项，原22项不变。Dodge4项与这两项一起跑真实RED；不能先假定候选已证实或已修好。精确接触/伤害排序是共同GREEN前提，不能只给Dodge添加无敌bool而绕过。

已实际读取[swd-skill-adapter-review.md](F:/Ourgame/docs/production/first-batch-v2/swd-skill-adapter-review.md)：候选A的真实Driver hit已有AtTime，但PendingDamage没有该字段且先消费玩家未来事件；候选B在首次几何entry LOS遮挡后continue，窗末擦除可能丢仍合法余段。该文档将22 GREEN与未覆盖边界分开；本计划沿用该证据限制，不把静态几何算术或测试夹具计划冒充已运行RED。

## Files / Interfaces

未来拥有：DungeonFighter.h/.cpp、DungeonGameMode.h/.cpp；必要的DungeonStoneKnightDriver.h/.cpp；新Tests/DungeonDodgeAdapterTests.cpp及本计划/report。纯Dodge/Combat/Weapon/Stone/Stats核、HUD、Probe和独立review测试不改。

建议入口：`bool TryBeginDodge(FVector2D MoveIntent=ZeroVector,bool FreshPress=true)`；只读`const DungeonDodge::FState& GetDodgeState() const`、`bool IsDodgeInvulnerableAt(double HitTime) const`。RED阶段TryBegin/IsInvulnerable均为空行为；只提供可编译类型和状态，不开始真实动作。

Driver冻结观察新增通用`FDungeonDirectInvulnerabilityInterval{Start,EndExclusive}`、Body的`bUseTimedDamageAdmission=false`与区间列表。默认false保原5项legacy合同；新true必须在几何entry/exit内减去保护区间求最早合法命中，A2首次接触被保护后仍可在余窗命中。受击体扫掠、实体身体阻挡、LOS与保护区间分别处理，不能把未命中当成身体可穿。

## TDD步骤

- [ ] 新4项真实UE测试：`CodexDungeon.Content.DodgeAdapter.FixedMotionAndIdlePositionHandoff`、`.CompositeCancelAndActionExclusion`、`.DirectIntervalsAndResolvedInterrupt`、`.StoneTimedWindowResumesAfterProtection`。我方原22+4=26；独立SWD审查2项另计则总28。新测试使用真实authority Tick/Actor/world wall/body，Driver子场景使用真实UWorld和明确冻结区间输入；该子场景不冒充玩家Shift已经成功。
- [ ] 根线程统一构建并保留新版本RED，确认旧22不退、新4确因缺接线失败；独立review反例按实际结果登记，不能把编译错误/崩溃当业务RED。
- [ ] GREEN先共同时间/位置接口：在真实输入方向采样后、普通运动提交前尝试Shift；成功不多走一段普通移动。所有非dodge合法XY（含落地、技能前踏、许可跨房）在同一核时间提交新位置凭据，成功才推进专域游标；换甲/武器/房间不重建核。只有真正新Run可按创建合同重建。
- [ ] 运动查询以冻结起终/受阻分段轨迹求真实wall/body最早fraction，之后仅镜像核Position；动作被墙/身体截停仍等原End，普通移动不得叠加。真实输入与控制门/复合取消先全部验证再同批提交；失败保持原动作和所有归属。
- [ ] 先只读预览找到本批最早接触/锁点/发射/取消边界，各权威核只推进到已发生边界，同点已接纳全部伤害先提交，再决定后续动作事件。禁止先发未来技能效果、后回填较早破韧；禁止为修时序重置/回滚单核。每次真实中断后重新取得Dodge区间，未来未成立的请求不能成为保护事实。
- [ ] 按真实HitTime联验旧hurt区间与已接受dodge区间的并集。Driver在几何entry/exit及攻击剩余有效窗内查合法子区间；早entry有LOS阻挡时继续评估剩余窗，不只一次entry continue。已有22、独立review2与Dodge4全部实跑；物理左右Shift/八向/无方向、受阻和旧无敌录像由root另验。

最小测试证据：四甲/无甲固定185/0.4；先普通走位后dodge从真实新起点、完成后走位再dodge且CD不洗；墙/身体真实截位；精确半开查询与实际窗口内/外伤害；普通受击继续、真破韧/死亡停止且不激活未来保护；成功/失败换甲取消、primary/skill排他及失败保缓冲；A2保护结束后剩余窗首次命中且不补第二次，完整保护窗零命中。物理键别名只由真实正常输入记录证明，API fresh参数检查不冒充设备证明。

## 验证与停点

本轮不运行UE/UBT。先交根可编译RED；GREEN取得后再统一全部suite和正常输入录制。位置凭据、核历史、实际中断、消费游标将来须同D13世界/资源全代保存，本轮不造磁盘档或迁移。完整历史的长局成本和多运动体联合查询仍需真实实测，不因164纯核通过就关闭目标。

冻结纯核SHA256：375ee1aa3d83612a3c686f0b1a6a6d322c97e247ea957c3d7380dcd431fd9ec2。只读复审结论限定纯核正确性，旧源码与旧测试语义保留。
