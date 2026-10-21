# SWD 武器技 Actor/GameMode 接入独立审查

日期：2026-10-15。范围：只读 Fighter/GameMode、WeaponActions 核与已有 UE 测试/报告；本审查没有启动 UE、UBT 或付费 API，没有修改被审查运行源码或原有测试。结论区分源码事实、推理、运行证据。新增两项反例已由根代理统一构建实跑，真实业务 RED 见下文；后续 Explore Probe/capture 工作属于另一个独立任务。

## 现有实际证据

- `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-013502/index.json`：20 成功、2 失败、0 未运行；两失败为 `CodexDungeon.Content.WeaponActionsAdapter.SwordSecondaryRealWindowAndBlockedStep`（11 errors）与 `...SkillRespectsFullRecoveryAndClearsOnlyAcceptedChain`（8 errors）。这是原 stub 的有效 RED，不能拿后来的源码解释成当时通过。
- 只读随后已经落盘的 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-020317/index.json`：22 成功、0 失败、0 未运行，两项技能测试均 Success。此运行由根代理执行；本审查没有重新运行。
- 已有两测试实际覆盖锁点/CD、一次前踏、身体/真实墙截断、椭圆角点、跨批后来进入、一次目标伤害、完整恢复/原链处理、普通非破韧和独立时刻真实破韧。没有覆盖下文两个批内时间/LOS边界。没有依据把22 GREEN解释为所有连续空间与中断时序完成。
- 根代理随后真实运行 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-024913/index.json`，并保留副本 `F:/Ourgame/docs/production/first-batch-v2/test-logs/ue-dodge-skill-boundary-RED.json`：总28项，原22项Success，另4项Dodge未实现桩Fail、本审查2项业务Fail，0未运行。两项所有SETUP均通过，没有把前置故障算作规则RED。报告自身时间字符串为2026.10.14-18.49.38，目录名按本地2026-10-15；保留两种原始时间表示，不误记为两次运行。

## 源码核对结果

| 合同 | 源码依据与结论 | 边界 |
| --- | --- | --- |
| 真正 .08 锁、Start+4.08 CD | `DungeonFighter.cpp:159` 只在 fresh/地面/共同门/同绝对时钟后 TryStart；核 `DungeonWeaponActions.h` 由 .20 windup 的40%定 LockAt，Lock 才设置 instance deadline=LockAt+4；Fighter getter 只读减核当前时间 | 当前只接 SWD，零甲/攻速修正；未来属性样本须按事实拆段 |
| 成功才断链 | Fighter:166成功 TryStart 后才在168清旧 Combat 链；拒绝请求不会先清 buffer | 当前成功时其他活动主攻已被共同门排除；不等于有攻击/技能/Q自由取消权限 |
| .20 前踏用真实合法位置 | GameMode:126 的18×16 box WorldStatic/WorldDynamic sweep、角色边界、活体尺寸连续夹取最早fraction；159先处理ForwardStep，再注册同点ActiveWindow，实际 Delta 写Actor且查询起点加入该真实Delta | 普通 MoveOnGround 的既有穿墙/身体缺口与 StoneDriver 批内分段仍另列 |
| [.20,.30)持续窗与每目标一次 | GameMode:183每个后续批次继续处理 SkillWindows；half-open结束检查；独立 `{ActionId,SubhitId,TargetId}` 领域去重，不混 Combat 主攻receipt | 几何相交采用批内连续起终点；LOS只有第一相交点查询，见候选B |
| 拒绝不消费收据 | target存活/同队/直接无敌、几何、65高度及LOS均在 GameMode:235写receipt前拒绝；旧无敌截至时刻用于裁剪 Begin | 最终伤害是 PendingDamage 批末提交；receipt表示已准入接触，不是最终HP回执。该队列未存 HitTime，见候选A |
| 普通非破韧 / 真破韧 | Fighter:455扣HP后，仅 Broken或死亡分支471调用 WeaponSkills.Interrupt并清窗；普通有效损失保动作；石骑由自身Driver解析削韧/中断；核中断保 instance deadline | 独立调用时刻已被已有测试覆盖；批内早于发射的破韧尚待候选A验证 |
| 当前一个活 Focus 权威 | Fighter:286唯一活SpendFocus/ConsumeAge，635唯一实际恢复；WeaponSkillContext:154把此零成本SWD适配核 FocusRegen=0，没有把内部Budget镜像/花费到Fighter；TryBegin仅SWD | 内部Budget保100但本适配不消费/恢复它。接弩杖/外部Focus前必须迁到共享核唯一权威；不能把本次SWD零成本门当迁移已完成 |

## 候选 A：同一批内的真破韧先后时刻被丢弃

静态证据：`DungeonStoneKnightDriver.h:35` 的真实 hit 含 AtTime；GameMode:99 接 batch 时只将 Attacker/Target/Damage/Stagger 写入无时刻 `FPendingDamage`（GameMode.h:53）。GameMode:293先消费玩家技能事件/前踏/窗口，301才推进石骑，309把 SimulationTime推进到批末，310按插入顺序提交伤害。Fighter:477的真破韧中断只能在这个提交阶段发生。

推理：如果同一实际5ms批内，Driver真实接触时刻早于skill .20发射，但该接触最终造成真实破韧，玩家 .20前踏/技能伤害可能已经先排入并提交；清剩余窗不能追回这个本应被更早中断阻止的发射。已有“在 .10独立ApplyCombatHit后再Tick”的测试没有触发这种先后关系。

最小时间合同：技能 Start=T；先走到 T+.198，再处理到 T+.203；真实Driver接触位于 T+.199，须验证 AtTime < T+.20，玩家旧无敌已结束且此次累计削韧跨真实阈值。期望技能在发射前真实中断，.20没有前踏/发射/对石骑伤害，原锁后CD仍为T+4.08。新测试必须用实际Actor/GM/Driver产生接触；若前置不能可靠满足，明确未证实，不伪造红测试。

状态：已由根代理实际 UE 反例证实业务 RED。真实接触1.550000000000，技能发射1.551000293158，同批[1.549000031315,1.554000031203]。所有SETUP通过、实际13HP/18削韧及Interrupted前置通过；业务失败3条：较早破韧没有阻止未来前踏、玩家位置已改变、石骑HP由110降至87.931030。原锁后CD断言没有失败。不得将下文已公开的前踏路径分段缺口替代成该场景的证据。

## 候选 B：最后有效批内 LOS 从挡到通，没有重查剩余合法段

静态证据：GameMode:229只取椭圆/高度区间的首次 HitTime；234若该时点LOS遮挡就continue整个目标/本批；240批末擦除已结束窗口。后续仍在合法窗内的LOS解除没有在同批重求交。

最小几何：技能前踏后的攻击者原点 `(30,0)`，目标X130；目标在最后批 `[T+.295,T+.300]` 从Y.925合法线性移动到Y0（185cm/s），全程位于145×40前椭圆。真实墙box的XY为X75..85、Y.05..100.05（中心80,50.05，半尺寸5,50）。攻击者及目标身体均与墙不重叠。

在第一次相交点 T+.295，射线穿墙；墙远端X85处射线系数 .55，目标Y低于 `.05/.55≈.0909091` 后LOS解除，即 T+.2995085995以后仍约0.4914ms处于 `[T+.20,T+.30)`合法窗。纯几何算术已实际计算：椭圆最大值约0.476159<1。现有分支只检查 .295 的遮挡，.300擦窗，会漏这一后段。必须用真实Scene/Actor运动补回归，不把算术当UE运行证据。

状态：已由根代理实际 UE 反例证实业务 RED。真实最后批[0.296000137925,0.301000137813]，LOS在0.296838712349前已通，实际窗结束0.300000000000，正常W产生playerY=.662500。全部SETUP通过，唯一业务失败是仍未造成应有32/1.45伤害；随后不重复扣HP断言没有失败。拒绝未消费receipt这点本身正确，问题在于窗口结束前没有再次检查合法剩余区间。

## 已公开或继承的边界，不作为新回归发现

1. **已公开：瞬时前踏与StoneDriver直线批路径。** 玩家技能查询会在 .20加入实际Delta，但传给随后石骑Driver的 Bodies 仅起终点，把瞬时变化摊成直线；且技能查询目标石骑的位置在该Driver本批推进前采样。需统一分段/事件时点路径接口。不能把“endpoint真实”解释成所有批内相对运动已准确。
2. **继承：普通地面移动仍直接SetActorLocation。** 当前Fighter:346..349与永久v002源快照的旧MoveOnGround一致保留“算位置+全局边界clamp+非sweep写位置”；技能期间虽正确用.5移动倍率，普通D/W位移仍未对墙/活体连续截断。独立前踏截断不能保证整个技能期间不穿墙。最小原型：墙中心X50半X5，已接纳技能后持续D；前踏停在中心X27，但后续recovery的普通移动可越过墙。这是既有普通移动缺口，不归罪为新增ForwardStep sweep失败。
3. 真实所有技能发射/伤害/HP/Focus/空攻/位置/receipt的D13完整代持久化、普通Q实例切换、其他四武器技能和弩杖普通攻击均未在本适配完成。运行22项和一段正常K录像不能替代这些验收。

## 审查源码版本

| 文件 | SHA-256 |
| --- | --- |
| DungeonFighter.cpp | `F9BD7B2AA81C5271C9CA99B1904D41DF54C6EB0864BB4E84A313902E67E8CFEA` |
| DungeonFighter.h | `3EE7D4DB1632E1B8B08031AC3594AA77D43FAD7CB99094DF8BD49C6AD3D5B929` |
| DungeonGameMode.cpp | `5F5E7417FDFB824B148AF7AEDF010829AF0CBBA3D522BF81DD4CC3F87E8549D9` |
| DungeonGameMode.h | `09B848462A64E88F52A438FAE1665E43D0361B1E9CFCFB3B4DD7FBB7FC65D7EB` |
| DungeonWeaponActions.h | `574B8090884B4AC2A30693FDE1DBD7367F005A923EDC6891AFFB510BD57B82DB` |
| 原技能AdapterTests.cpp | `D97FC5D9AF5C5A4E2136DDC7E47CD63B1006718F88AB2B76065943BE33506143` |

## 新独立边界回归

已新增 `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonSkillBoundaryReviewTests.cpp`，整文件由 `WITH_DEV_AUTOMATION_TESTS` 包围，恰好2项唯一测试；本代理没有编译或执行它们，根代理已统一构建并执行28项。原22项测试与被审查运行源码均未修改。当前结论是22 GREEN +4 Dodge桩RED +2本审查业务RED；后续修复GREEN仍须重新统一实跑证明。

| 新测试名 | 真实前置与业务断言 |
| --- | --- |
| `CodexDungeon.Content.WeaponSkillBoundaryReview.RealPoiseContactBeforeEmissionSameBatch` | 玩家0/石骑-50，自然近距苏醒后首盾；t≈.8真实1伤害/12削韧，不改private韧性/HP；读实际Shield.ActiveAt，在其前.199起真实skill，在其前.001停止再推进5ms。玩家旧iframe已到期且18盾削韧加12恰跨30。用真实driver Capture/Restore在只读副本执行实际世界query，验证唯一13/18 hit、实际AtTime早于技能发射；实际GameMode随后必须也有同AttackId/TargetId hit、真实13HP损失与存活玩家Interrupted。业务期望：无future前踏、位置不变、石骑不受future技能伤害，原锁后CD保留。 |
| `CodexDungeon.Content.WeaponSkillBoundaryReview.LastWindowBatchLOSBecomesClear` | 真物理墙X75..85/Y[-99.95,.05]、真实休眠石骑130,0、玩家skill实际前踏后30,0。先走至实际ActiveEnd前4ms，实际Controller/UPlayerInput的W变成held，再让GameMode做5ms普通运动。前置要求起点实际ray blocked、终点actualray clear、玩家实际Y .6.. .7且仍X30、窗口确已到期。几何前置证明解除在End前至少1ms；业务要求32/1.45实际伤害且随后无第二次扣HP。 |

A中见证副本只查询世界，不提交UObject/真实Driver/HP；实际GameMode命中与中断仍单独验证。选择盾开窗时玩家在X50前距之内，无论未前踏位置0还是被身体截断后的-8都在90×32内，因此首次接触时刻为实际Shield.ActiveAt，不依赖已公开的瞬时前踏直线路径近似。

B实际测试采用玩家正常W移动而非上文示意中的目标移动，避免控制敌人AI速度/伪造批路径。头less Controller fixture使用Possess、真实UPlayerInput、InputKey及ProcessInputStack刷新held；真实GameMode的UpdatePlayerInput/MoveOnGround产生批内轨迹，未直接写最终位置。按当前265×.5速度，5ms实际预期Y=.6625；墙远X85处光线高度=.45×playerY，LOS在约T+.2968385744解除，到T+.30前还有约3.1614ms有效窗。该算术仅核对fixture，不替代真实物理ray与HP断言。

每个前置断言均标 `SETUP:`，失败立即停止；只有所有相关前置通过后的业务断言失败才计为候选实际RED。若Controller、物理墙或自然首盾前置失败，应修正fixture/明确未证实，不能把setup失败报成规则回归。技能起招是现有API层测试，不冒称正常物理K；B的W动作确实走真实Controller。两项均未直接调用私有伤害/消费函数、拼造命中回调或复写生产相交/LOS算法。

新测试冻结 SHA-256：`4B9E7845205CB8EED62CF1BEDA5364CF3063EB33B60754A9CCA2A16EBE7F0731`。测试编写阶段只执行文本唯一名称/整文件guard及fixture几何算术；以上真实RED来源为根代理随后执行的UE运行。本次报告补证没有修改测试文件，未把静态审查、算术或本代理未做的运行冒充GREEN。
