# 石像骑士 UE 单元接入记录

日期：2026-10-15，Asia/Shanghai。状态：实现候选、等待统一构建与运行；助手未验收。仅修改 DungeonFighter.h/.cpp、DungeonGameMode.h/.cpp，本报告新增。冻结的 DungeonStoneKnight 核与 Driver 未修改，未启动 UE、未构建、未提交、未付费生成。

## 真实依据与本轮边界

根线程真实 RED：`test-logs/ue-integration-and-admission-RED.json`，18 项中 14 通过、4 失败。Driver 的 5 项已通过；`CodexDungeon.Content.StoneKnightGameIntegration` 因 InitializeStoneKnight 空实现失败；另 3 项为独立 armor-admission 反例。已读取具体断言，未将纯核 77 项或 Driver 5 项当成 UE 单元接入已通过。

根线程在交接前已修正的三处源码保持：移动意图取消未完成换甲；旧无敌准入成功后才消费近战 hit receipt，枪筛选也排除不可伤目标；普通免费跨房只改位置，不 Reset、不回血、不回专注或清已有状态。

## 接口和权威路径

- `ADungeonFighter::InitializeStoneKnight(uint64 EntityId, double StartTime=0)`：只用于新实体初次配置；拒绝已有 Driver、零 ID、非法时间或已死亡实体。设置 ENM-STN-001，110 HP；甲 45、抗 20、韧 60、移动 185 由冻结 Definition 读取。调用 BeginCombat 启动 12 秒模拟钟兜底；再次初始化及该实体 ResetFighter 均不能重置 HP/CD。非零时刻生成时，调用者传 `GameMode::GetSimulationTime()`。
- `GetStoneKnightDriver()`：只读状态/保存快照入口；Driver 是石骑动作、HP、削韧、苏醒、CD 的唯一权威。`SyncStoneKnightState()` 将位置/HP/死亡/锁向/动作余时和表现名镜像到现有 Actor，禁止 generic AI、generic BeginAttack/ResolveAttack、外部 MoveOnGround 或 StartJump 再推进石骑。
- `GameMode::Tick` 继续使用原有最多 .005 秒步长。新增 double `SimulationTime` 为共同绝对 From/To；等待开始及游戏结束时冻结。每步在运动前后冻结真实 Actor XY、JumpHeight、旧无敌、存活和队伍。玩家/原型身体 18×16、石骑 24×20；中心边界 X[-700,700]、Y[-200,220]。Driver 内查询注册场景碰撞；本关未制作内墙，不能称为真实内墙地图。
- 每个石骑在动作批次只调用一次 `Driver::StepTo(ToTime, Frame)`；Batch.Hits 只加入 PendingDamage，再由原有统一提交调用 ApplyCombatHitInternal。ActiveWindow 不另走 ResolveAttack，因此不会扣第二次。先前已接受的同批命中保留 PreviouslyAccepted 路径，新授予无敌不能吞掉其他已接纳攻击。批次中致死也先提交余下已接纳命中，再冻结下一步。
- 石骑入伤先甲抗结算，再 `ApplyResolvedHit(actual HP loss, legal stagger, instantaneous frame)`；非破韧伤害不取消动作，不授予原型 .18 秒无敌，不做原型 24cm 推位。真破韧的 .4 秒及 1 秒保护、死亡由核决定。伤害事件只改变同一个实体的原有 HP。
- 全房 WakeStarted 权威时刻限制新警告至少相隔 1 秒；真实伤害也须取得许可，未取得时保留 queued。只有 Enemies 中实际接纳实体发生死亡，且其他接纳实体确实全部死亡，才调用 NotifyOtherAcceptedEnemiesCleared；初始零其他敌不触发。
- 死亡先 `ClaimDeathReward()` 一次，再调用旧 OnFighterDied 掉落路径。此处仍为原型金币/药水/斧头，尚未接 D08 正式奖励、真实装备来源或事务凭据。

## 显示与开发入口

石骑 AnimationName 提供 dormant / wake / idle / walk / charge / shield_bash / recovery / hurt / death，锁向与动作显示时间来自 Driver；名字齐备不代表正式素材齐备或验收。当前导入和 HUD 候选图由根线程另行处理。

补齐根线程要求的三个只读玩家展示 getter：`GetVerticalVelocity()`、`IsCurrentPrimaryAirborne()`、`GetLandingVisualAge()`。落地展示 age 初始/Reset 为 .12，真实弹道落地置 0，活体 Motion 最多推进至 .12；没有新增锁输入、回血、取消或判定条件。

`-DungeonStoneKnightPreview` 仅将开发房替换为一只真实 ENM-STN-001，不改变默认原型房、正常开局武器或发甲。可与原有证明旗标组合使用。未修改 DEV-REG01-PACK-v1 或全量目录来源。

`GetRuntimeEntityId()` 仅为内存 QA 身份：石骑使用初始化 ID，原型使用高位标记的 UObject GetUniqueID，调用者必须提供不冲突的 ID。不是 D13 持久身份；磁盘存档、迁移、全代原子提交、加载后输入松开等尚未实现。本轮 Driver Capture/Restore 能力不能充当这些功能的完成证据。

## 待根线程验证

本轮不新增或改写测试。统一构建后应重新运行原 18 项，尤其集成测试的 Dormant → 14.5 物理实伤损 HP10 → 完整 .85 秒警告 → 自动 A1 移动与玩家实伤 → 死亡不重发，以及 3 项 armor-admission 回归。只有新的实际报告可把本记录更新为 GREEN。

尚需真实运行录像、命中边界/体碰撞复核和候选图声审阅。当前只预览单石骑；若将来同批加入多只可移动石骑，需进一步核查彼此连续移动轨迹，现冻结 Bodies 中其他 Driver 的动作阶段移动没有联合求解。全量五敌/Boss、正式掉落、状态、配套道具与磁盘保存不在本轮完成范围。

静态检查：四文件不存在冲突标记，根线程三处修复仍在；冻结核/Driver 的 SHA256 与交接一致。四文件为 Git 未追踪工作文件，git diff 的空输出不被当成改动或编译验证。实际构建和 18 项结果待根线程回填，不宣称通过。

## v002：终局表现与权威冻结分离

2026-10-15 根线程真实执行新测试得到 `test-logs/ue-terminal-RED.json`：19 项中原 18 项全部通过，只有 `CodexDungeon.Content.DeathPresentationAfterTerminalFreeze` 失败；三个失败分别为玩家 death clip、石骑 death clip 和空中死亡落下显示未推进。该报告同时确认 run/Driver 时钟、游标、CD、HP、Focus 和奖励的冻结断言已通过。本轮读取完整失败条目后才修复；未改测试或既有 18 项。

最小修复为 private `ADungeonFighter::AdvanceTerminalPresentation(float DeltaSeconds)`，仅对已死实体加 AnimationTime，并沿原有死亡显示的 360cm/s 下降率把 JumpHeight 显示值收至 0。该函数只写这两个表现字段；不调用 SimulateMotion、SimulateActions、Driver、伤害、输入、落地动作或资源逻辑。GameMode 在 bGameOver 分支调用该函数后直接返回；SimulationTime 和所有未死亡角色都保持原终态。普通游戏循环及冻结核/Driver 未修改。

这不是恢复战斗或离线计时：死亡已提交后只允许尸体显示落下，地面 XY、JumpVelocity、动作 ID、HP/CD/专注、奖励和 Driver 快照保持冻结。等待根线程下一次统一构建及 19 项运行报告，当前源码已更新，不能以此前 18 项 GREEN 代替新版本验证。

## v003 准备：真实事件表现 journal 的 UE RED

2026-10-15 根线程提供独立已验证的 DungeonStoneFeedback.h（25 checks / 0 failures），职责只记录实际核事件、按 EventId 去重、最多64项、不持久化/不推进权威。此次先新增 Fighter 的 `const DungeonStoneFeedback::FJournal& GetStoneFeedback() const` 和私有成员，尚未接 Begin/Observe，保留空 journal 供真实 RED。

新增唯一 UE 测试 `CodexDungeon.Content.StoneFeedbackGameIntegration`，位于 Tests/DungeonStoneFeedbackIntegrationTests.cpp。它由真实 authority Tick 跨过苏醒结束与锁点，实际入伤/破韧/死亡入口产生事件，并从同一个只读 getter 检查 Damaged/WakeStarted/WakeCompleted/AimLocked/PoiseBroken/Died；检查同实体单调ID、HP/clock/奖励未被展示记录多推进。重复实际死亡请求须不多记录；重复Observe单独在只读journal的副本上用实际事件重放，避免暴露给HUD可变接口。这一副本检查不冒充实际世界收到同批两次，核心重复批合同由根独立25项覆盖。

当前总suite为20项，等待根线程统一构建RED；本轮未构建/启动UE，也未擅自接入表现或修改HUD/Probe。动作适配只读计划另存 weapon-actions-adapter-plan.md，16个实际JSON指针已验证，计划本身不实现K/右键/Shift/发射物。

### v003 接线候选与真实 RED

根线程已真实构建并执行20项：`test-logs/ue-stone-feedback-RED.json`，19项通过，唯 StoneFeedbackGameIntegration 失败7条，分别为未记录真实伤害/苏醒/StepTo苏醒结束与锁点/破韧/死亡、没有同实体递增记录以及未初始化journal的重放失败。终局 DeathPresentationAfterTerminalFreeze 在本报告中已 GREEN，v002三个显示断言修复得到实际验证。

读取上述失败后，v003仅补两处：InitializeStoneKnight 对新journal执行一次 Begin(EntityId, Driver.State.NextEventId)；已有 AcceptKnightBatch 在 Accepted 后统一 Observe(Batch.Events, Driver.State.Position)。Fighter::ApplyResolvedHit 和 GameMode::StepTo 已经共用该入口，因此两种真实事件均进入同一成员，不做两次记录。位置取已结束批次的核位置，避免 Actor 尚未 Sync 时误用旧站位。

Observe只影响有界表现journal；失败只输出诊断，不回滚/改变权威状态。没有新增伤害、声音、奖励、随机或时间推进；HUD保留const读取，测试原样不改，根的journal核/Probe/HUD未修改。等待根线程下一次统一20项GREEN；本轮未启动引擎或构建，不把已读19项GREEN当作v003全部通过。
