# 石像骑士 UE Driver 接入记录

2026-10-14，Asia/Shanghai。范围：新增普通 C++ bridge、5 项 UE 自动化测试；不修改 Fighter/GameMode/HUD 或冻结行为核。Driver 实现已提交工作区供 root 构建；此记录建立时尚未取得实现后的 UE GREEN。纯核77项通过、UE bridge测试和实际游戏运行分别计证，不视为完整敌人制作验收。

## 事实、取舍与边界

当前 Fighter 使用无碰撞 SceneComponent，动态身体不能假借 UE Pawn collider。Driver 因而对本批真实 Actor 的冻结 Start/End XY/高度样本作相对连续几何查询；内墙/物体则调用真实 UWorld box sweep 与 LOS trace。当前原型房间只有中心边界X[-700,700]/Y[-200,220]，root尚未制作内墙；支持场景查询不等于已在主房间放入内墙。

玩家身体沿真实 D02 `/movement/standard_body_half_x_cm`、`/standard_body_half_y_cm` 及 D05 `target-profiles.json#/player_reference`，采用18×16cm半尺寸。石骑24×20来自D05 `/profiles/0`。其它原型身体由调用者显式传入；BodyHalfExtent不得以受击体或画面重叠替代。Owner、其它实体与目标的稳定身份也由root提供，运行期UObject指针不写入核状态。

Driver只调用 `DungeonStoneKnight::FKnightKernel`，没有复制休眠/招式/CD/破韧状态机。它没有Tick，也不扣Actor HP、不SetActorLocation、不调用GameMode奖励或声音。Fighter/GameMode负责同批提交、属性减伤、身体与表现同步；正式视觉/动作/声音、章节派生、奖励来源与磁盘档仍未因此完成。

## 精确接口与接入顺序

文件：`UnrealGame/Source/CodexDungeon/DungeonStoneKnightDriver.h/.cpp`。

~~~cpp
FDungeonStoneKnightDriver(ADungeonFighter* Owner, uint64 EntityId, double StartTime=0.0);
const DungeonStoneKnight::FState& State() const;
DungeonStoneKnight::FState Capture() const;
bool Restore(const DungeonStoneKnight::FState&);
FDungeonKnightBatch StepTo(double Now, const FDungeonKnightFrame&);
FDungeonKnightBatch ApplyResolvedHit(double ActualHPLoss, double LegalStagger, const FDungeonKnightFrame&);
bool BeginCombat();
bool NotifyOtherAcceptedEnemiesCleared();
bool ClaimDeathReward();
DungeonStoneKnight::FSweepResult QuerySweep(const DungeonStoneKnight::FSweepRequest&, const FDungeonKnightFrame&) const;
~~~

- Frame：FromTime/ToTime、Target弱指针、Bodies、CenterBounds、bUseCenterBounds、bCanStartAttack/bCanBeginWake。
- Body：Fighter弱指针、EntityId、Start/End、StartHeight/EndHeight、BodyHalfExtent、bAlive/bCanTakeDamage/bBlocksBody/bSameTeam。
- Batch：Accepted、Events（核原始事件）、Hits。Hit含Target弱指针、AttackId/TargetId、Damage/Stagger、AtTime。

Root在每个实际运动批次前后冻结样本，覆盖完整 `[Frame.FromTime, Frame.ToTime]`；StepTo要求FromTime恰为已存核Time、ToTime恰为Now。步进内按样本线性插值，源动作时间保持绝对double，不改tickrate。root当前采用每批至多.005s的实际模拟步；大渲染帧由root的运动批次拆开，不把帧末位置当过去的位置。

StepTo按核锁点/有效开始/有效结束/恢复结束/苏醒与眩晕边界分割，锁点读取该时点插值目标，休眠和追近先观察区间起点。满足共同规则时每次StepTo最多接受一个新攻击，bCanStartAttack仍须先获得D07全房名额；bCanBeginWake由全房苏醒队列授予。BeginCombat只在真实本房战斗起点调用；NotifyOtherAcceptedEnemiesCleared只能在真实清除其它已接纳敌的事件中调用，不在初始化空集合调用。

StepTo和ApplyResolvedHit返回后，root先检查Accepted，再统一消费Events/Hits、同步State().Position/HP/phase到Owner。Raw Hit须加入已有同批PendingDamage，不能在Sweep callback或事件收集途中直接扣玩家HP；本批旧无敌资格用Body.bCanTakeDamage冻结，新受击产生的无敌不能删掉同批已接受伤害。真实HP损失结算后调用ApplyResolvedHit，休眠可伤与正损失唤醒才不会绕过原核。

Capture/Restore直接委托原核Version=1，Driver不重启/回HP/清CD。返回事件必须消费完后才能在完整批次边界保存；没有第二个待发队列。继续保原时钟，暂停期间不StepTo。ClaimDeathReward只更新核的once凭据，真实交付须与root外层事务同代提交。

## 连续查询与返回命中

QuerySweep全程只读，不能改变核EventID、命中凭据、Actor transform或Health。动态身体用相对XY线段对扩展身体AABB求首接触；从接触边界向外离开/沿边滑动不算新穿透。A1伤害用目标中心投影到锁定轴/垂直轴的连续矩形区间，再裁实际高度容差；不把目标身体半尺寸扩到65×24攻击形状里。有效攻击与身体在同点接触时优先接受合法攻击，然后停止冲锋；无敌/友方/高度或LOS不合法可只发生Body stop，不偷给接触伤害。

静态/动态场景物体调用UWorld::SweepMultiByObjectType，使用Owner身体XY24×20、地面查询薄Z盒；忽略Owner，并把水平阻挡作为Wall，地面法线不当侧墙。LOS使用UWorld::LineTraceTestByObjectType。测试中注册独立WorldStatic box验证真实scene query；当前主房间缺内墙不虚报为墙体内容完成。移动场景物体本身的历史轨迹没有纳入Body样本，本轮只查询场景当前碰撞姿态；复杂移动墙、导航及门边LOS变化需后续专门验证。

A1由原核记录ValidHit，再把原Hit事件映射成Batch.Hits；事件顺序与接触时间不重算，不在query中提交伤害。墙/身体/合法命中后的1.6s恢复和原CD均由冻结核保留。

A2根据核ActiveReceipts冻结窗口，检查本批运动与窗口交集，按原0—90cm、半Y32、高度65及LOS精检，调用核TryMarkMeleeHit后生成Batch.Hits。有效窗采用右开边界，之前已命中目标和重复同钟调用不再生成命中。A2实际命中从Hits消费，不能因为ActiveWindow提示事件又额外扣一次伤害。

## TDD与当前验证状态

根线程已真实执行首轮：`build-editor-20261014-232357.log` exit0；报告副本 `test-logs/ue-stone-driver-RED.json`，总14项中9通过、Driver新增5项全部失败，都是空行为缺失导致的断言失败，不是编译错误。已读取该报告，确认以下5项进入RED：

1. `CodexDungeon.Content.StoneKnightDriver.DormancyAndResolvedDamage`
2. `CodexDungeon.Content.StoneKnightDriver.ChargeQueryHasNoSideEffects`
3. `CodexDungeon.Content.StoneKnightDriver.StaticWallAndBodyStops`
4. `CodexDungeon.Content.StoneKnightDriver.ShieldPoiseResumeAndReward`
5. `CodexDungeon.Content.StoneKnightDriver.MovingTargetContinuousContact`

随后才实现Driver。五项覆盖同实体正伤唤醒、原时钟警告、实际玩家中心与身体碰撞的先后、真实注册墙/友方/旧无敌阻挡、A2去重、破韧/恢复/奖励once，以及目标在两个渲染端点之间穿过有效走廊的连续接触。盟友使用独立真实Actor，不复用玩家指针。

实现后未由本子任务启动Editor/UE构建或运行；待root统一build/headless验证后追加真实GREEN结果。既有纯核独立测试77通过和动作核80通过不能代替这5项UE验证或主房间录屏验收。

另修复独立harness进入UBT的LNK2005：仅自有StoneKnightStandalone加`DUNGEON_STONE_KNIGHT_STANDALONE`守卫，RunStoneKnight加对应/D宏；UBT该TU为空，`stone-green-harness-guard-01.txt`实际77/77通过。冻结核头无修改，旧combat harness未改。

实现源冻结：2026-10-14 23:33:06.2644712 Asia/Shanghai。Driver.h SHA256 `3ad0b14ca173f8de54f7aea3c58a277610d0e4dd5f78c4b1406412bc02456441`；Driver.cpp `2f9bb1f2a708d65ef7bd1f3f00690d1c2ee3266813d8a4e35be5eb57476598e7`；UE测试 `a5933d4085c90da02ace1220ddf79ae02a10cbccae50f2c5d52f5bd6b2395564`。
