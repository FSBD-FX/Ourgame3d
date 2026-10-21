# 首批内容运行基础与首个闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在真实UE工程完成首批内容的可验证动作基础与军剑/轻甲/石像骑士闭环，为剩余内容提供同一接口；这只是持续目标的首阶段，不能据此关闭总目标。

**Architecture:** 可独立测试的C++动作时钟/连招/攻击配置核驱动UE Pawn，HUD及声音只消费权威事件。正式二维资产使用独立图层与绝对动作时间映射；缺素材明确记为待制作，不用原型冒充。首次真实来源与存档接入随后单独展开，保存接口从本阶段预留。

**Tech Stack:** UE5.5.4 C++、MSVC14.38、Python3、Blender MCP、asset-gen。

**Spec:** `F:/Ourgame/docs/production/first-batch-v1/content-contract.json`；`F:/Ourgame/docs/production/first-batch-v2/combo-spec.md`；D02/D03/D05/D12/D13原设计。

## Global Constraints

- 工程F:/Ourgame/UnrealGame/CodexDungeon.uproject；G:/UE_5.5；最多2个编译动作；此项目Editor关闭后再编译。
- 原装备/设计全目录与历史证据保留；当前codex/preparation分支无提交基线，改动前备份源代码及哈希，不建立缺失资产的独立checkout。
- 5武器、4甲、5普通敌、1Boss完整目标不缩减。20种搭配和40朝向只是基础检查，所有适用动作也要验证。
- 正Y向远处/屏幕上方，投影和输入及地面-Y排序一同修正。
- 用户已要求新增近战三段连招；第一段保留旧主攻，v2明确覆盖第二三段及链规则。
- 付费生成须先确认具体花费；缺资源仍可推进代码/工具/声音筛选，不能把完成标准降成占位。
- 交付判据为运行内容和已审阅录像，测试与构建只是分项证据。

## Review Focus

- 低帧率跨过整个有效期仍恰好结算一次，连续有效期不重复命中；表现不能补发攻击。
- 取消/破韧/换装/死亡/离地限制不遗留缓冲或重置资源，普通受击不能偷取消后摇。
- Y朝向迁移须同时检查输入、地面投影与深度顺序，旧证据不可作本轮新证据。
- 正式2D图层缺失、握点错位、镜像两次、脚点抖动必须显式失败，不能回退到通用敌人而标记通过。
- 目标可被重复回调/保存恢复/卡顿时，AttackID、子击及音效均不重复消费。

## Task 1: 可测试动作与三段连招核

**Files:** 新建 `Source/CodexDungeon/DungeonContentCombat.h`、`Tests/DungeonContentCombatStandalone.cpp`、`Tests/RunContentCombat.ps1`（均在UnrealGame下）。

- [ ] 先写可运行失败测试，证明缓冲、恢复、到期、去重、低帧率及三种武器节奏未实现；保存RED日志。
- [ ] 实现纯C++配置/动作核：三种近战9段参数、5武器基础主/技能定义引用、4甲属性；攻击阶段/锁点、ComboStage与单意图缓冲、每段ID/目标去重、可保存状态、非权威展示停帧。
- [ ] 公开轻量接口并交给主线程适配，避免核直接操作UE对象/资产；测试离地一次、普通反馈与中断、无效输入及精确边界。
- [ ] 运行GREEN测试，保存实际结果；核完成不等于游戏接入。

## Task 2: UE首单元控制与真实判定

**Files:** 修改DungeonFighter.h/.cpp、DungeonGameMode.h/.cpp、Tests/DungeonGameplayTests.cpp；后续必要时独立DungeonEnemyController。

- [ ] 用真实隔离UWorld测试证明连续点击不能取消收势、同ID不能二次伤害、非破韧不取消、甲移动/防护、石像休眠/锁线/失手恢复。
- [ ] 将动作核接到正常输入；旧sword/axe原型标记兼容入口，正式内容用稳定模板ID，不混淆旧axe和GSW。
- [ ] 玩家动作基础包含跳跃参数630/1800与一次空中主攻、合法闪避与锁点、武器/防具动作边界。
- [ ] 石像骑士同实体可伤休眠→.85s苏醒→两招，连续冲锋扫掠墙/身体及1.60s失手完整恢复；有限死亡奖励一次。
- [ ] 联合UE自动化和真实图形检查，真实来源/完整存档尚未落地时维持未完成状态。

## Task 3: 动作帧/图层与事件反馈

**Files:** 新建内容presentation模块及资产manifest；修改DungeonHUD；独立source-assets生产目录。根线程负责，避免与Task2共享写。

- [ ] 为绝对动作时间→帧/阶段、固定脚点、握点、单次镜像、缺帧失败、武器-甲适配、下一事件抢断视觉停帧写失败测试。
- [ ] 付费授权后用asset-gen制作风格参考小批，保留全部原件/生成参数/费用上限；先审阅再扩帧，不批量放大坏图。
- [ ] 制作真实对应姿势：idle/walk/跳跃三态/落地/闪避/hurt/death/三连段/技能/换装/各适用动作，保证地面影子和排序不随jump改层。
- [ ] 声音预检→试听→事件挑选→导入与混音；prep/emission/hit/miss/break/death去重，静音低特效设置生效。
- [ ] 逐帧/左右/纵深/四种甲测试；正式风格和动作源未齐时不通过该单元。

## Task 4: 真实来源/保存/其余内容与最终验收

**Files:** 后续从production progress展开分子计划，不在此计划编造已实现接口。

- [ ] 在首单元成功后扩剩余4武器3甲4普通敌及Boss，全部适用招式/状态/转场。
- [ ] 接15既有辅助道具、显式DEV包概率与真实来源、装备属性/附魔/升级、交互UI与输入、活动动作精确保存恢复。
- [ ] 首区有限遭遇与Boss奖励链，不用全发道具测试台替代正常获取。
- [ ] 实跑20搭配/40朝向及全部适用动作、多目标/多段/低帧率/存档中断，保存并审阅带音频短录像。
- [ ] 独立完整审查，逐件八维完成合同全部通过后才调用update_goal complete。
