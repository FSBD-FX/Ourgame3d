# 武器技、闪避与共享资源接入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. 本轮仅规划；未授权在此文档交付时改运行源码或执行构建。

**Goal:** 先让 SWD001 的 K/右键武器技和全局 Shift 闪避通过真实角色/碰撞/伤害路径，再让五武器共用单一专注与空中主攻预算；不改既有时轴、取消权或保存规则。

**Architecture:** 保留 DungeonContentCombat 三段主攻核。每玩家一份 DungeonWeaponActions 核管理五件武器实例、技能、弩/杖主攻、专注、装填和共享空攻预算；Fighter 只做输入门、运动和显示镜像，GameMode 在同一权威批次消费事件并提交命中。Dodge 是角色独立动作和 CD，不伪装成武器 Skill，不改石骑状态机。

**Tech Stack:** UE5.5.4 C++、MSVC14.38、现有纯 C++17 核；本轮不构建、不启动引擎、不生成素材。

**Spec:** [D02](F:/Ourgame/docs/design/player-combat-v1/player-combat-rules.json)、[D03](F:/Ourgame/docs/design/items-v1/common-rules.json)、[D04](F:/Ourgame/docs/design/inventory-v1/inventory-rules.json)、[D11](F:/Ourgame/docs/design/ui-input-v1/input-rules.json)、[首批 v1 合同](F:/Ourgame/docs/production/first-batch-v1/content-contract.json)、[连招 v2](F:/Ourgame/docs/production/first-batch-v2/combo-spec.md)、[动作核报告](F:/Ourgame/docs/production/first-batch-v2/weapon-actions-kernel-report.md)。以下新增接口全部是助手实现建议，尚不存在，不代表新玩法规范。

## Global Constraints

- 首批仍为 5 武器、4 甲、5 普通敌、1 Boss；SWD/dodge 只是下一实现切片，不能关闭完整制作目标。
- v1 `/shared_required_systems/actions` 的旧 no_combo 已由 EV-036/combo-spec 对三种近战普通攻击显式覆盖；没有覆盖武器技、空中一次主攻或闪避取消权限。
- 四运行文件当前冻结；本轮只新增本计划。HUD、VFX/SFX、石骑表现 journal、Probe 捕获、equipment stats 由其他负责人处理，不重复实现。
- 时间沿 GameMode double SimulationTime；最多 .005s 步长是现有实现，不是给 D13 新定固定 tickrate。暂停/继续不得推进仿真或离线恢复；终局表现函数只处理已死显示。
- 无新增 stamina、格挡、招架、翻滚伤害、技能无敌、免费装填/换甲治疗或自动连按；动作失败不顺手清原有缓冲/装备归属。

## Review Focus

- 同批 K/右键/Shift/J 必须只接受最高优先级的一个合法主动请求；UI 消费和恢复确认不能穿透。
- Dodge 的 [.06,.20) 无敌边界需按命中真实时刻检查，不能用整 .005s 的一个布尔值盖住区间变化。
- SWD 前踏与同点斩击有严格先后；真实受阻后从实际站位查椭圆，不能播放 30cm 就认为位移成功。
- 新旧两核的局部 ID 都从 1 开始；技能子击与普通三段不能共享无域的命中 key。
- Focus 恢复、外部扣还与空攻预算只能有一份权威；不得用每帧覆盖 Budget 或 Capture→篡改→Restore 充当 API。

## 已核实的事实、推理与缺口

事实：当前 Fighter 只有 J/左键、Space、Q/E 的旧输入分支，没有 K/右键或 Shift；Focus/FocusConsumeAge 与 bAirPrimarySpent 仍是独立权威。WeaponActions 已有五武器逻辑但尚未接 UE。其 `EAction` 只有 None/Primary/Skill/Reload，没有 dodge；`TryStart(Primary)` 明确拒绝 HasCombo，三种近战普通攻击应继续走 Combat。

推理：SWD secondary 和 dodge 均不消耗 Focus，不需要为赶首个切片先制造两份专注恢复。先做排他动作和事件适配；完整五武器预算迁移须在接入 STF 或替换现有 SpendFocus 前完成。

真实缺口：WeaponActions 没有外部专注消耗/恢复入口，Restore 目前把 LastActualSpend 与 Issued 中的真实发射消费交叉验证。既有 `SpendFocus(50)` 不能直接映射到修改 `Budget.Focus/LastActualSpend`，否则快照不合法；D03 专注药恢复也缺入口。必须由该核负责人按 TDD 增加明确资源变更凭据及验证，或在完成前保持旧 Focus 路径并不把 STF 适配标为完成。该缺口不阻止零专注成本 SWD 技/闪避的先行验证。

规范核对：D02 `/attack/ground_jump_or_dodge_cancel=false`、`/dodge/cancels_attack_or_skill=false`。D03 `/use/precommit_cancel` 仅允许道具前提交被合法闪避取消；`/weapon_timing_extension` 只补时间/锁点预算，没有授予攻击前摇 dodge cancel。combo-spec“开始其他独占动作断链”只能在动作已合法接纳后执行，不能反推可取消活动主攻/技能。Q 的 switch_weapon 不可被 dodge 取消（D02 `/equipment/switch_dodge_cancel=false`）；equip_weapon/equip_armor 的未提交动作可被合法 dodge 取消，这两种 .35s 动作不能因时长相同而混用。

## 参数与输入合同

| 项 | 精确接入值及约束 | 真实来源 |
| --- | --- | --- |
| SWD secondary | K/MouseRight fresh press；地面待机或先前完整动作已结束；.20/.10/.38，总 .68s；.08 锁向与快照，CD 到 .08+4=4.08；t=.20 先最大前踏30cm，再由实际新站位查前半椭圆0..145、Y±40；32物理/22削韧，各合法目标一次；零弹药/Focus、无无敌/自动追敌 | equipment-v1/weapons.json `/6/secondary`；ContentCombat definition SWD001 |
| Dodge | 左/右 Shift fresh press；只地面；.40s，最大185cm、462.5cm/s；方向起招固定，八向归一，无方向取 facing；无敌[Start+.06,Start+.20)，CD Start+1.20；碰撞缩短距离不退CD，不受甲/移动/攻速/技能CD修正 | D02 `/dodge`、`/controls/dodge`；D11 `/actions/4` |
| 输入优先级 | dodge→jump→item1→item2→skill→primary→switch→reload→interact；每逻辑步最多一项接纳，held 不重发。装填时 dodge→switch→cancel_reload，取消同点不再接受 primary/skill | D03 `/input_extension`；D11 `/contexts/world_grounded_idle`、`/contexts/world_reload` |
| 甲/资源 | 换甲 .5s，提交前旧甲生效；移动/有效直接或DoT损失/合法dodge取消。失败dodge不取消。Focus100，基础12/s，最后实际消耗后1s；ROB001 当前16/s、1s；换甲不改最后消耗时刻 | D02 `/equipment`；D04 `/action_policy`；ContentCombat armor definition |
| 空中 | 真实起跳清新一轮 token；成功接纳主攻才消费；失败起招不消费、取消/锁失败不退；技能/装填/dodge/换武器非法。落地只更新 Grounded，不重启动作/ID；一次离地不连第二段 | D02 `/jump`；combo-spec；WeaponActions Budget |

## Task 1：SWD 技与共同动作准入

**Files（未来执行时）:** 修改 DungeonFighter.h/.cpp、DungeonGameMode.h/.cpp；新增 `Tests/DungeonWeaponActionsAdapterTests.cpp`。均位于 `F:/Ourgame/UnrealGame/Source/CodexDungeon/`。不修改两个冻结核以绕过合法动作门。

**Interfaces（建议）:** Fighter `bool TryBeginWeaponSkill(bool FreshPress=true)`；`DungeonWeaponActions::FContext WeaponActionContext() const`；`void AdvanceWeaponActionsTo(double Now)`；`void ClearPendingAttackInput()` 扩展为清两个核输入。GameMode `void ConsumeWeaponActionEvents(ADungeonFighter*, const std::vector<DungeonWeaponActions::FEvent>&)`。新增只读技能状态 getter 给 HUD，HUD 不反向发攻击。K/右键的同一动作别名先合并成一个 fresh intent，不能分别调用两次。

- [ ] 写 `SwordSecondaryRealWindowAndBlockedStep`：基础起招 .08 锁/CD4.08；.20 前踏无障碍实际30、真实墙/身体则缩短；仅从实际新位置查椭圆，角落反例不能命中；石骑45甲下单次32实伤约22.0689655，整窗不再重复扣HP。
- [ ] 写 `SkillRespectsFullRecoveryAndClearsOnlyAcceptedChain`：活动主攻/技能不能插 K、Shift、jump、换甲；主攻 .60 完整结束后可开技，清原地面链；技能结束后再主攻从段1开始。未被接纳的技能不清原动作/缓冲。K+右键同批、按住均不多起一次。
- [ ] 根线程统一构建真实 RED，保存独立版本报告；再实现最小接入并统一 GREEN，保持现有19项回归。技能窗口不走旧 ResolveAttack 的普通主攻值或旧 HitAction 去重。

事件消费 key 为 `{OwnerRuntimeID, Domain=weapon-actions-v1, ActionId, SubhitId, TargetID}`；三段普通攻击继续使用 `Domain=melee-combo-v3`。窗口不等一次瞬间点采样：其整个有效区间都可接纳新进入的合法目标，每目标/子击最多一次。ForwardStep 必须先做只读连续扫掠并提交实际位移，再消费同点 ActiveWindow；保持锁定 Facing，移动倍率从对应 definition 读取，不能给技能默认套原型 .2。

## Task 2：全局 Dodge 与独立无敌区间

**Files（未来执行时）:** Fighter/GameMode 四文件、Task1新测试；必要时由石骑 Driver 负责人扩展冻结观察接口及其独立测试。Dodge 无需塞入 WeaponActions::EAction 或改该核技能取消规则。

**Interfaces（建议）:** Fighter `bool TryBeginDodge(FVector2D MoveIntent, bool FreshPress=true)`；`bool IsDodgeInvulnerableAt(double HitTime) const`；只读 `FDungeonDodgeState GetDodgeState() const`。最小状态含 Active、Start/End/ReadyAt、固定单位方向及中断事实；用同一 SimulationTime，身体连续 sweep 遇阻停移，动作仍保留承诺时长；绝不能借调用 MoveOnGround 得到盔甲倍率或穿身体。

- [ ] 写 `DodgeDistanceDirectionAndCost`：四甲/无甲均 .40s 最大185cm，斜向总长185，空方向镜像 facing；身体中心X100且双方半尺寸18+24时最多前移58；Focus与空攻预算不变，受阻仍 CD1.20。空中和活动 primary/skill/switch 请求拒绝。
- [ ] 写 `DodgeIframeHalfOpenAndPoiseInterrupt`：分别用新 fixture 在+.06前、精确+.06、+.20前、精确+.20送实际命中，只有[.06,.20)拒绝直接伤害；旧hurt无敌与dodge取区间并集而非相加；区间外真破韧取消剩余dodge无敌，保原CD及独立hurt区间。既有DoT照常，不授予净化。
- [ ] 写 `LegalDodgeCancelsOnlyUncommittedWork`：换甲 .25s 时合法 dodge 撤 pending、旧甲仍在；CD未好/空中失败不撤甲。装填途中 dodge 丢进度不补弹，取消同点不接J/K；Q切换动作拒绝dodge。不得用“先取消再发现dodge非法”的顺序。
- [ ] 根线程取得 RED 后实现 GREEN，复跑当前19项及Task1测试。现有3项 armor-admission 和 terminal 冻结测试必须继续通过。

连续命中前提需先补齐：当前 FDungeonKnightBody 只有整批 `bCanTakeDamage`，不足以精确表示批内 dodge 无敌开/关。建议冻结 `FDirectInvulnerabilityInterval {double Start, EndExclusive}` 列表（旧hurt与已接纳dodge并集）到 Bodies；Driver 碰撞查询按实际接触时刻/有效窗区间排除不可伤子区间，身体阻挡仍独立成立。A2 初次接触在无敌中但目标仍留在窗内，需在无敌结束后的剩余合法区间再次求交；不能仅否掉第一 entry 就漏整个窗口。关键边界要拆步，但只拆步仍不能把旧布尔值错误套到右端点；禁止epsilon改动[.06,.20)语义。该接口须独立 Driver RED/GREEN 后再冻结，不能在SWD接入时偷改。

## Task 3：把 Focus/空攻迁到唯一核权威

**Files（未来执行时）:** Fighter 四文件与动作适配测试；DungeonWeaponActions.h/其Standalone仅由该核负责人在单独 TDD 修改。equipment stats 的输出结构由其负责人交付后读取，不复制22属性计算。

**Interfaces（已有）:** `RegisterWeapon/EquipCompleted/Instance`、`TryStart/PressReload/StepTo`、`CanAdmitExternalMeleePrimary/RecordAcceptedExternalMeleePrimary`、`NotifyTakeoff/NotifyLand`、`ClearPendingInput/Capture/Restore`。

**缺失接口（建议由核负责人新增）:** `bool TrySpendExternalFocus(double Now,double Amount,uint64 ReceiptId)` 与 `double RestoreExternalFocus(double Now,double Amount,uint64 ReceiptId)`。仅接受当前有限时刻及新凭据；花费须不侵占 ReservedFocus，成功才更新真实消耗时刻；恢复返回实际增加量、封顶100、不重置最后花费。快照版本/凭据校验须同时支持 Issued 发射消费与外部真实消费，不允许只改数值就通过。此接口不自行引入新消耗玩法；用于保留现有 SpendFocus 入口和未来D03已经定义的恢复。

- [ ] 写纯核 `ExternalFocusMutationKeepsReservationsAndRestoreFacts`：真实花费50、等待1秒、恢复45不重置等待；重复Receipt拒绝；缺/伪造花费凭据和倒退时间拒绝且不改活态。取得可编译 RED 后由核负责人补最小 GREEN。
- [ ] 写 UE `SharedFocusSurvivesArmorWeaponRoomAndPause`：Fighter::SpendFocus 只是该核入口封装，Focus字段只镜像；原FocusConsumeAge与SimulateMotion独立恢复移除。换袍前后的分段恢复率只积分一次，换武器/跨房/暂停不回满、不改最后消耗。原跨房反例继续通过。
- [ ] 写 UE `ExternalMeleeUsesOneAirAcceptance`：真实起跳同时通知两核；先共同门检查，再由 Combat 真正接受后同一批 RecordAcceptedExternalMeleePrimary。失败 Press不消费；空中成功后反向取消仍不能再开；落地不重开活动段，下一次真实起跳才清新token。旧Fighter bAirPrimarySpent删除独立授予权，Combat私有token只作镜像/额外拒绝。不通过非法空中Equip来演示跨武器。
- [ ] 根线程取得 RED 后迁移，完整复跑；不能在每次切武器或每帧重新构造 WeaponActions。Q正式切换须 .35s完成才 EquipCompleted，实例Ammo/CD与共享Focus均保持；同模板不同InstanceID也不能被合并。

共同门需排除“别的核/动作”，不能把当前核自己的 Active 当作 Context.CanStart=false，否则会误杀最后 .12s 主攻缓冲。Combat 的 Context 禁活动 WeaponActions/dodge/换甲等；WeaponActions 的 Context 禁活动 Combat/dodge/换甲等，但保留本核自己处理主攻缓冲的机会。每核每个权威时刻最多推进一次，两个 clock 与 GameMode一致；技能/装填阶段也推进闲置 Combat 的绝对时间，不能切回近战后临时补算一大段。

## Task 4：其余技能/投射物与保存批次

**Files（未来执行时）:** GameMode事件适配、独立小型投射物/范围效果模块及测试；D13磁盘层另行承担，不扩写本计划为IO实现。

**Interfaces（建议）:** `FDungeonWeaponEventKey {OwnerID,Domain,ActionId,SubhitId,EventId}`；GameMode `ConsumeWeaponActionEvents` 创建事实实体/范围窗；`FPendingDamage` 增加来源类型、SubhitId、HitTime与已准入事实，避免 STF 魔法误走物理甲。击中/正HP损失结果再交状态模块，表现journal只消费真实发射/命中/状态结果，不轮询HUD相位补发。

- [ ] `FiveWeaponsUseTheirRealEvents`：GSW技能一次68/65；SPR [.18,.22)、[.28,.32)、[.38,.42)分别最近一目标、各12/6；XBW主攻一弹34/12、950cm/s，末弹完整.68结束后才1.10装填；XBW技一弹50/24、1100cm/s，最多两目标，第二直伤和削韧×.6；STF主攻一弹24/8、600cm/s、10Focus且无默认燃烧；火线18/6+固定2/s×3s、24Focus，魔法减伤，直接属性不放大固定burn。
- [ ] `ProjectileAndWindowHaveOneWorldConsumption`：跨过发射点/完整短窗的大步仍消费一次，重复EventId不再建弹或扣伤；实际发射时枪口XY/高度、锁定朝向，无Y追踪/下瞄；墙/中心硬边界/高度65/实体受击体扫掠均生效。MaxTargets=0代表范围内各合法目标一次，不是零目标；没有无限弹丸/宽矩形代替椭圆。
- [ ] `ResumeKeepsWorldAndBudgetSameBatch`：清两个输入缓冲后同批捕获两核、dodge、实例、世界已生成弹/范围、命中receipt/状态next_tick/RNG/消费游标；恢复无重放、无离线恢复、不补回血或空攻。死亡普通敌旧弹规则沿D05，Boss清理沿D06另测。纯核 Capture 通过不等磁盘IO完成。
- [ ] 完成新增 RED→GREEN、现有全部回归及玩家真实K/右键/Shift/弩杖输入录像，才分别登记规则/输入/发射接入。HUD根节点展示与声音不充当碰撞成功证据；正式来源、20装备搭配、手柄重绑与D13完整事务仍各需证据。

WeaponActions::StepTo 的 FContext 在整个传入区间恒定。真实枪口、起落、甲提交、buff截止或关键发射点发生变化时必须拆段并采当时实际样本；不能先推进到慢帧终点，再把所有过去发射都填同一终点枪口。原点策略按 CurrentMuzzle / CurrentActorAfterPriorEvents / GroundProjection 执行，前踏后射线必须读取已提交的新原点。持续窗对进入目标检查与弹体世界消费去重由适配器承担，不能把 Issued 既当已命中又重新遍历扣伤。

## 执行验证与停点

未来根线程先统一编译，再运行 `CodexDungeon.Content.WeaponActionsAdapter` 新测试组保存独立 RED；实现后跑该组及完整 `CodexDungeon.Content` 组。纯核新增验证用现有 `Tests/RunWeaponActions.ps1`，旧Combat/Stone/CombatRules回归仍保留。日志与Automation导出路径每轮取新的日期版本，禁止覆盖先前失败原件。本轮没有执行这些命令或声称任何新项通过。

先交付Task1可玩的SWD技能，再完成Task2（含Driver无敌时间接口验证），Task3为STF等共享资源上线前置，最后Task4；若Task3外部Focus API未完成，不绕过核验证把五武器全部接线。当前石骑 feedback journal 接口由root提供后才能接只读表现事件，本计划不抢改其接口。

## 只读来源冻结

| 文件 | 本轮读取SHA256 |
| --- | --- |
| DungeonWeaponActions.h | 0f6e167fbac7ed44f5908626e5d00a3bb975ce96c3212606d5588b09dd4af76a |
| D02 player-combat-rules.json | ab22cd0f131fa8f025ea16db9d1536028526b35c467aeb0008fe2dca59c413ef |
| 首批v1 content-contract.json | 860b7f50256085d020cd3a60c2f04e80c0124303cfbe1c5fbfe19da830f0ca56 |
| combo-spec.md | 7a630740ccae1e9da7e6effb374f6d63252960f41ed4b998f98a83e0822eea82 |

自查：字段/方法的“已有”与“建议”已分开；引用的 JSON pointer 实际存在；SWD零专注、dodge全局CD/半开无敌、技能不能插后摇、共享空攻与未提交换甲取消无隐性覆盖。运行四文件本轮保持上一冻结版本，未触碰其他负责人文件。
