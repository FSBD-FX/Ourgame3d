# 三近战三段普通链独立代码审查

日期：2026-10-14，Asia/Shanghai。审查范围：已实现的 SWD001/GSW001/SPR001 普通三段链、UE Fighter/GameMode/HUD 适配与 ContentProbe。依据 AGENTS.md、combo-spec.md、kernel-report.md 和下列源码快照。**只读静态审查；没有启动 UE、运行游戏或执行测试，没有修改玩法源码、导入资产或付费生成。** 下面给出可执行的复现夹具及按代码得到的结果，不能当作已完成实机复现。

结论：已实现范围仍有四项运行路径错误和一项核恢复校验错误。未接完整AI、附魔、音频、正式图像或磁盘保存等已登记后续工作，不计入本次缺陷。根已在审查过程中补了枪的“本次查询最近目标”分支；问题 R1 针对补丁后仍存在的整段目标数错误。

## R1 · [P1] 枪只限制每次查询最近一人，整个 AttackID 仍可击中第二人

**位置**：`UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:151–163`；`DungeonFighter.cpp:82–90`；`DungeonContentCombat.h:120`。

现在每次 ResolveAttack 重新找最近的存活合法目标，但没有“本段已选/已命中唯一目标”的事实。核 TryMarkHit 仅限制同 AttackID/SubhitID/TargetID 重复，允许同 AttackID 命中不同 TargetID。Fighter 在 ActiveWindow 事件中 Resolve 一次，随后处于有效期还会再 Resolve。

**复现**：

1. 玩家装 WPN-SPR-001，重置到(-170,0)，朝右；关闭两个靶的AI，靶A在(-90,0)、HP=21，靶B在(10,0)、HP=1000。二者高度0、无受伤无敌。
2. 发第一段，从核时间0推进到0.12（枪有效期[0.11,0.18)）。
3. 首次 Resolve 选A并造成21伤害使其死亡。随后同次 AdvanceContentAction 的第二次 Resolve 忽略已死A、选B，再造成21。
4. 实际代码得到A死亡、B=979，且两次属于同一个 AttackID。预期B保持1000：普通枪刺只处理路径最近一个目标。即使A不死，其+24cm击退也可能使另一靶成为下一次查询的最近者，发生同类串靶。

**修正边界**：选中/命中目标限制要成为本 AttackID/SubhitID 的持久事实，不能靠每帧重查最近者和按目标去重代替；如近靶死亡或移开，本段不能转而穿透后排。

**QA假阳性**：`DungeonContentProbe.cpp:52–56,126` 只摆一个合法靶，其余放在600及偏纵深处；名为 `spear_nearest_target_three_hits_total_63` 的检查只看0号靶总HP，所以当前错误也能全绿。需加入同时合法两靶、近靶死亡/击退、远靶未受伤断言。

## R2 · [P1] 跨有效窗事件使用帧初位置/高度，移动攻击随帧率漏命中

**位置**：`DungeonFighter.cpp:70–90`、`104–113`、`384–396`。

AdvanceContentAction 先把核推进整个 Delta，再消费历史 ActiveWindow；CanContentHit 却读取此刻 Actor 位置和 JumpHeight。玩家地面移动与跳跃积分在之后才执行。代码既未把位置/高度推进到 Event.AtTime，也没有在[AtTime,WindowEnd)做相对运动检查。有效窗过去后若当前Phase已是Recovery，也不会再补合法区间查询。核本身会返回窗口，不代表适配层保住了该窗口的真实命中。

**复现（10 FPS，不需要目标移动）**：

1. 玩家军剑第一段在(0,0)朝右起攻，静止靶在(150,0)，关闭AI；起攻后持续按D，以 Delta=0.10 调用正常Tick。
2. 第一次Tick至t=.10尚未出击，玩家移动到X=13.25（265×.5×.10）。
3. 第二次Tick把核推进到t=.20，产生t=.17的窗口；两次Resolve都使用移动前X=13.25，距靶136.75>135，因此不命中；随后才移动到X=26.5。
4. 第三次Tick到t=.30时已过有效期结束.29，没有新窗且Phase为Recovery，未结算伤害。
5. 连续运动在t=.17应处X=22.525，距靶127.475，整个有效期有合法命中；60 FPS下也会正常打中。相同输入路径却因10 FPS漏掉这一击。

空中高度同样在窗口结算之后更新，跨起跳/落地的大步会用旧高度检查65cm差值；缓冲后一次Step跨多个段时，多个历史窗也共享一套帧初空间，不能据此回补真实过去命中。

**修正边界**：仿真要在动作/运动/落地关键边界分段，或保存并检查实际区间内的相对轨迹；不能仅按事件数量补调 Resolve，也不能拿帧末/帧初坐标替代历史几何。

**QA局限**：standalone 的 `low_frame_step_across_entire_active_window_does_not_lose_hit_opportunity` 只断言核返回一次窗口；ContentProbe靶与玩家都静止攻击，均看不见这个适配错误。

## R3 · [P2] 所有普通伤害都被当作破韧，直接清动作与连段

**位置**：`DungeonFighter.cpp:230–243`；合同：combo-spec.md“普通未破韧受击只有反馈，不凭播放hurt取消本段”。

ApplyCombatHit 没有破韧条件或类型，任何正伤害都设 AttackTime=0 并调用 Combat.Interrupt(PoiseBreak)。因此该适配无法保留普通受击中的活动段、后摇和已接受缓冲。

**复现**：军剑或重剑起攻后，选一个仍存活且无无敌的玩家时点，调用 `ApplyCombatHit(1.f,nullptr)` 表示未达破韧的普通伤害。当前立刻中断核、清地面链与缓冲；下一次攻击回第一段。预期只有受击表现/伤害，原动作完整继续；只有真正破韧或死亡才中断。

旧Source.zip的原型本来也在每次受伤时清AttackTime，但把这条旧占位行为映射成新核的PoiseBreak违背本次连段规则，不能因旧实现如此就视为新规则已经适配。

**修正边界**：普通伤害反馈与真实破韧/死亡事件分开；不要无条件调用核中断。现有standalone `ordinary_hit_feedback_has_no_kernel_interrupt` 只调用ClearPendingInput，没有调用UE ApplyCombatHit，因此无法验证适配层。

## R4 · [P1] E捡斧绕过活动动作限制，回切剑会复活被冻结的旧攻击

**位置**：`DungeonGameMode.cpp:251–255`；`DungeonFighter.cpp:26–29,288–293,384,404–416`；核拒绝条件：`DungeonContentCombat.h:116,119`。

旧拾取路径直接把WeaponId改为axe，没有通过核的ChangeWeapon/活动动作拒绝；IsContentMelee随之变false，核从此不再推进，外部AttackTime却走旧斧逻辑继续倒计时。等外部AttackTime归零，Q回剑会调用Interrupt(SwitchWeapon)，但仍Active的核拒绝这个中断；调用者忽略返回值，依然换WeaponId。下一帧旧剑动作从被冻结的核时间接着推进。

**复现**：

1. 在玩家身边放原型axe拾取物，关闭敌人AI。用sword起第一段，在t=.10（未到.17有效窗）按E捡斧。
2. 等旧AttackTime倒计时完成，并等待靶受伤无敌结束；此期间不要按J。核时间仍停在原剑t=.10、Action.Active=true。
3. 按Q切回剑，下一帧核越过原剑.17有效点，产生原AttackID窗口，可能再造成26剑伤害，尽管没有新的攻击输入。
4. 即使目标不在范围，HUD也会重新出现原连段与动作，说明旧动作被恢复。

**修正边界**：所有能改变WeaponId/实例的路径都走相同的已接受换装事务；活动primary下不能靠E直接替换。拒绝的Interrupt/ChangeWeapon不能继续改外部武器。核与外部AttackTime不能被不同模式各自推进。

这是新核与保留旧拾取路径组合出的状态回归；没有要求本次补完整背包或真实来源系统。

## R5 · [P2] Restore接受可篡改的排队窗口快照，绕过已冻结伤害

**位置**：`DungeonContentCombat.h:89,122`；消费端：`DungeonFighter.cpp:82–84,186–189`。

ValidState 对 PendingEvents 只检查基本ID/枚举/时间与Action的AttackID/Stage，没有联验窗口事件是否为已发窗、是否已经消费、事件Action是否符合原冻结快照，也不验证事件Action各数值。Restore因此可以接受一个将旧窗口重新排队且Damage不同的状态，StepTo返回它后，适配直接以Event.Action作为伤害快照。

**纯核调用复现（由当前条件静态推导，未执行编译）**：

```cpp
using namespace DungeonContentCombat;
FCombatKernel k;
k.PressPrimary(0);
k.StepTo(.20);              // 原Locked/ActiveWindow已返回并被调用者消费
auto s = k.Capture();       // Action.Damage仍为26，PendingEvents为空
const auto w = s.IssuedWindows.back();
FCombatEvent e;
e.EventId = w.EventId;       // 小于NextEventId，且PendingEvents内不重复
e.AttackId = w.AttackId;
e.Stage = s.Action.Stage;
e.Kind = EEventKind::ActiveWindow;
e.AtTime = w.Start;
e.WindowEnd = w.End;
e.Action = s.Action;
e.Action.Damage = 999;      // 与冻结Action.Damage不一致
s.PendingEvents.push_back(e);
FCombatKernel r;
bool accepted = r.Restore(s); // 当前为true；应拒绝不一致候选
auto events = r.StepTo(s.Time); // 当前返回含999伤害的伪窗口
```

IssuedWindows证据仍存在，所以后续对尚无HitReceipt的新靶调用TryMarkHit会成功；适配GetAttackDamage读取HitAction.Damage，错误窗口能够实际绕过冻结伤害。即使不改伤害，只重新排队已返回窗口，也会重播已消费挥击声。

**修正边界**：恢复校验必须联验事件种类/时间/窗口receipt/消费游标和不可变动作快照，拒绝不一致Event.Action；继续保持失败不改变现核。这里审查的是已经实现并声称校验快照的Restore，非要求立即补磁盘存档。

## 核与探针的其余边界

静态读取中，核的末0.12s单槽缓冲、完整后摇后接段、0.45s精确到期、锁后朝向冻结、NotifyLand不取消动作/不退离地token，以及ClearPendingInput仅清未执行意图，符合所读调用合同，未另列功能缺陷。Capture保留内部缓冲而正式暂停先Clear的区别已明确记录；尚未接磁盘/UI暂停适配属于已登记后续工作。

ContentProbe对空中部分只检查跳高和向上输入（112–113行），没有断言空中AttackID数量、第二次空攻拒绝或落地后原后摇。其报告scope中的“one air primary”应按实际断言范围理解，不能用该绿灯认证整个UE空攻合同。这是证据覆盖限制，未凑成第六条实现缺陷。

HUD正Y向上与降groundY排序已改，读取动作进度作为占位显示不产生判定；正式画面与完整声音不在本次通过声明中。

## 审查快照

源码在协作中仍可能更新；下列哈希描述本次阅读的版本，问题修复后需针对新版本复测，不将本报告当作后续代码的自动结论。Source.zip仅以只读流比较旧实现，没有解压覆盖工程。GameMode哈希对应已加入nearest分支的版本。

| 文件（项目根相对） | SHA-256 |
| --- | --- |
| `UnrealGame/Source/CodexDungeon/DungeonContentCombat.h` | `11d88c9e6f599d4ff2e7929e1775053975e9474f355004d8790db8a02a44deec` |
| `UnrealGame/Source/CodexDungeon/DungeonFighter.h` | `94cf9e398bb618c7aa76eb3086095daa821b7f773b5ce46c76db2d962294c4ed` |
| `UnrealGame/Source/CodexDungeon/DungeonFighter.cpp` | `744d34baed0d2b7ea19af40e2402f2f855f76400eeb9b32b90cb88662c61ee57` |
| `UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp` | `b44c322d85670fcaf273872dc2aaad05cd5b22fbb813760bbed99086bbf31efd` |
| `UnrealGame/Source/CodexDungeon/DungeonHUD.cpp` | `30fc35c7420f00f8721468e660a6562a595e64d4f50149373fdae24ac092744b` |
| `UnrealGame/Source/CodexDungeon/DungeonContentProbe.h` | `aed89e1c3b0bbd49cbb0082a642b045e0ecf7a8f568a4051287a0c79a27e99d4` |
| `UnrealGame/Source/CodexDungeon/DungeonContentProbe.cpp` | `39e3be86b98ef4ba4f3fe4f83a542588e449fd2b65c8c1c3089cb5c79b04605f` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonContentCombatStandalone.cpp` | `033ca2e821d4892fd8dd6ac684e6bc14a2c877585fe02aae504a838a16840006` |

本报告只写入 `docs/production/first-batch-v2/combat-review.md`。未修改任何被审源码或其他参与者文件；未启动UE、未生成资产、未运行验证，因此不声明上述修复或实机验收已完成。


---

## 复审追加：原五项修复与统一模拟路径

同日复审；仍未由本审查者启动UE、构建或运行测试。下表是对修复代码的独立静态复核，运行结论应以root随后统一构建、测试和录屏为准。原报告保留作为先前版本证据，不能把旧行号直接用于新源码。

| 原项 | 当前代码处理 | 复审结论 |
| --- | --- | --- |
| R1 枪整段串靶 | Fighter::MarkContentHit遍历本AttackID的任意Subhit0 receipt，已有一次尝试即拒绝其他目标；GameMode仍只查询最近合法靶 | 原死亡/击退换靶路径静态已堵住。新增UE源中包含近靶死亡而远靶100HP的回归，避免旧单靶QA假阳性 |
| R2 整帧历史窗错采样 | GameMode::Tick以≤.005s统一推进所有actor Motion→Actions→伤害批次；生产player/enemy自身Tick关闭 | 原10FPS整帧漏判路径已替换；不能据此批准完整连续碰撞。已新增真实GameMode.Tick的慢帧空中/地面对照测试，待root执行 |
| R3 普通受伤强制断链 | 玩家累计30韧性并衰减/保护；只有Broken或死亡才Interrupt，普通未破韧伤害保Action | 原普通1伤直接断链静态已修；已有真实ApplyCombatHit的UE断言覆盖，完整防具/AI仍是后续范围 |
| R4 捡斧冻结后复活旧剑 | TryInteract要求地面且CanStartAttack；SwitchWeapon检查Interrupt返回后才改变WeaponId | 原活动primary时E捡斧路径被拒绝，Q不再忽略拒绝；未要求本轮补完整背包 |
| R5 伪排队窗/冻结伤害 | ValidActionData、事件语义/时间/receipt联验；随后给窗口receipt保存FrozenAction并将内存Version升3 | 当前与历史独立窗口均有冻结快照比较，原999与历史27伤路径静态已修；仅读取owner的80/80日志，不冒称由本审查者重跑 |

本轮复审曾在75检查版发现一个残余：新Action已开始时，队列只剩上一AttackID窗口，缺上一Locked可比较，在合法区间内改26→27仍会被接受。已反馈owner；最新 `FWindowReceipt::FrozenAction` 与receipt/event的SameAttackFacts比较堵住这一条，新增5项回归及旧Version2拒绝测试见 `combat-green-review-05.txt` 的 `SUMMARY checks=80 failed=0`。这份日志支持纯核测试结果，不代表UE保存已落地。

### 新发现 N1 · [P1] 同批新生无敌仍会吞掉后续已到期伤害

发现时位置：`DungeonGameMode.cpp:56–61`、`DungeonFighter.cpp:238–249`。排队解决了actor结算先后干扰，但提交队列仍逐条调用ApplyCombatHit；第一条授予0.65秒无敌，下一条同批伤害又按InvulnerableTime拒绝，尚未使用批次开始时的旧无敌资格。

可复现夹具：玩家无旧无敌，三个AI关闭的普通敌在(80,0)/(80,±2)，各同时BeginAttack，原13伤均在.46秒到期。真实GameMode.Tick(.47)后，100HP对照应为61，20HP应死亡并通知authority结算。发现版本会分别停在87/7。旧无敌在.46仍覆盖时，则三条都应拒绝，不能为修复同批伤害而一律绕过无敌。

root已接受并计划“入队检查旧资格、提交accepted hit仅忽略同批新生无敌”的修复。此处记录发现版本及测试目标，不把计划或正在进行的构建标成通过。

### 新增可执行UE回归夹具

独立owned文件：`UnrealGame/Source/CodexDungeon/Tests/DungeonDamageBatchTests.cpp`。注册3个测试，由root统一build/run：

1. `CodexDungeon.Content.DamageBatch.AllDueHitsResolve`：真实GameMode.Tick(.47)，先100HP→61精确计三发，再20HP→0/死亡/authority bGameOver。20HP例单独只能证明至少两发，因此保留100HP正控。
2. `CodexDungeon.Content.DamageBatch.PreexistingIframesStillBlock`：用真实ApplyCombatHit建立0.65秒旧无敌并确认第二次伤害被挡，再保留该区间将公开HP设20；.47Tick中三发均被挡，存活且不结束局。
3. `CodexDungeon.Content.DamageBatch.LowFpsAirWindowUsesMotionTime`：StartJump+军剑空攻，一次.60秒慢render Tick跨越[.17,.29)窗口，窗口期间高度>65，地面靶应100HP；同路径地面正控应74HP，防止“不发窗/假authority”也使空中用例全绿。

夹具不直接Spawn一个无authority关系的GameMode：先CreateWorld并挂UGameInstance，再 `World.SetGameMode(FURL game=/Script/CodexDungeon.DungeonGameMode)`，由World记录真正AuthorityGameMode，断言GetAuthGameMode返回该实例。API依据是本地UE源码 `World.cpp:5196` 的SetGameMode→`GameInstance.cpp:1490` 的CreateGameModeForURL；显式native game选项加载类后不依赖WorldContext的PIE/map前缀fallback。测试关闭音频/物理/AI系统，明确仅调用生产统一Tick，避免直接Player.Tick/手工Resolve掩盖GameMode路径。

任何世界创建/SetGameMode/演员或攻击未成功的setup错误都会报告并失败，不能当作成功复现N1。此审查者没有执行这3个测试；root尚在统一构建/运行时，不提前声明RED或GREEN。

### QA与声明边界

原5个UE测试的源码主要直接Player.Tick、手工Resolve或ApplyCombatHit，不足以单独认证新增的GameMode统一小步与伤害批次路径。新增3项专门补这个空白。ContentProbe仍只用一个合法枪靶，空中部分仍只看跳高/方向；新的针对性自动化可以补充其证据，但不把旧录屏scope扩大为整套低FPS/输入/保存验收。

核的80检查、UE测试、真实录屏分别归档。≤.005s离散处理解决整render帧取错姿态的问题，不是完整连续碰撞、正式防具或完整AI的已完成声明。内存Version3不表示磁盘存档已完成；暂停时ClearPendingInput与外层事件消费/提交仍按原合同。

### 复审快照

| 文件（项目根相对） | SHA-256 |
| --- | --- |
| `UnrealGame/Source/CodexDungeon/DungeonContentCombat.h` | `0becdef858554b311a1bd284585f6b16bc64a420cf7ec49dce30616a9e53d6a5` |
| `UnrealGame/Source/CodexDungeon/DungeonFighter.cpp` | `0b0c411aa8c4298093df910e47486664a1bb21b960627cdc0c8e92b39e3c001f` |
| `UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp` | `d7ba7588bab49c1055fcd71ef7dc02a5f896792d3b861ea84da28d1fa145f8c4` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonContentCombatStandalone.cpp` | `4871515b5837c3ae082b2480761069720b54804ac0eab3c4a05baf579c8fd064` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonDamageBatchTests.cpp` | `3f5db0ef64e229fc01af5ef7221155fac5e871cb0d68c8cab999c2a4a39d9b88` |

追加工作只涉及本报告和新DungeonDamageBatchTests.cpp；没有修改root/owner源码，未启动UE/生成付费资产。


