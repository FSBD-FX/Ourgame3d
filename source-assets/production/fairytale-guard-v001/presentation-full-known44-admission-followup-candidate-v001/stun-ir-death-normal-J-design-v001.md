# 后续 StunIR／Death：正常 J 观察模式草案

本文件仅方案，implemented=false、UE_run=false。冻AxeCycle v001入口仍只支持AxeCycle，不能把本草案写进已有native成功。建议NEW actor/工具版本使用相互独立fresh process场景`StunIR`与`Death`，旧partial与首AxeCycle验收语义保持。

## 可复用事实

复用真实房间URL、Enter/E同LGT来源与提交、Knight/Bat公开诊断清除、formal slot2 Guard出生、44resident预检、WASD身体外侧路线及CRC/FIFO捕获。Guard不允许public damage、spawn、teleport、kernel控制、HP/time/poise/stat/RNG改写。正常J通过controller `InputKey`脉冲，读取`PlayerFighter->GetMeleeCombatState()`；连招尾窗复用WalkProbe逻辑：actual A.Active、Stage<2、尚未queue该AttackId、SimulationTime≥ActiveEnd且≥End-.10时按J，不能直接PressPrimary。必要躲避只能正常WASD/Shift输入，记录真实Dodge回执；不直接调用TryBeginDodge。

军剑基础削韧16/14/18，一链48不足Guard85。默认无词缀两链六个实际命中合计96，仅在实际间隔未触发1s延迟后20/s衰减且未受ProtectionUntil限制时才可能破韧。每刀锁定后的Stagger/Damage/Range、真实Crit决策、Guard ReceivedHits/PoiseAccum才是判断依据，不能按六次J宣称break。实际默认SWD Grade0/no affix，5%基础Crit仍可能发生；不锁死最终HP或击杀刀数。

现被动AxeCycle侧点150超出军剑前两刀135中心射程：`CanContentHit`按中心ForwardEllipse，未额外扩Guard40半身宽。新模式用正常移动目标约side*125、Y对齐并保留安全余量；射程资格按本刀真实FrozenAction与真实双方位置独立重算，不能把150处空挥计命中。仍在ExtremelyClose70外，可引导实际Axe而非私设攻击类型。

## StunIR 模式

先真实J积累poise，记录每个玩家IssuedWindow/HitReceipt `(AttackId,SubhitId,TargetId)`、Guard ReceivedHit `(ReceiptId,AtTime,ActualHPLoss,Stagger)`、所有Damaged/PoiseBroken/AttackInterrupted及每draw真实时钟。普通正伤只允许MaterialHit/tint，未到85不得切Stunned。

尝试让最终实际破韧命中落在某次真实Axe早Windup内（观察调度，不改clock），pin该Guard AttackStarted的完整原FAction/OccupiedUntil。以真实PoiseBroken为成功触发，不强定第6刀；要求非致死且`Broken.AtTime+.4 == StunUntil < original OccupiedUntil`。若生存、hit或剩余窗前提未成立，明确本场景RED并停止，不重置Guard或把更晚break当原cycle。正常准备战斗是否能稳定实现该时序，尚待原生诊断；无直接伤害捷径。

Stun4必须同一个PoiseBroken EventId、原`[Broken.AtTime,StunUntil)`，0/.1/.2/.3。InterruptedRecovery4必须同一个原被打断AttackId且只在正剩余`[StunUntil,original OccupiedUntil)`，frame=floor(4*(Sample-StunUntil)/(OccupiedUntil-StunUntil))，无固定400ms。原窗结束即failfast缺帧。

现SelectFull委托旧selector的IR，**IR.SourceEventId合法为0**（旧Finish未传event）；不能误套AxeRecovery必须RecoveryStarted EventId的oracle。独立核原AttackInterrupted、PoiseBroken，以及实际StunUntil处RecoveryStarted(EndTime=原OccupiedUntil)证明来源。Stunned.SourceEventId必须是真PoiseBroken ID。break若在原Active前，未issued Window，不能要求一定存在closure；已issued才要求该窗原closure。打断后不得新增同AttackId ActiveWindow/Hit，原窗口与原deadline不改；新攻击只可按真实IdleReadyAt/Cooldown开始。画面只宣称Stun4/IR4和实际material反馈，未覆盖行仍gap。

## Death 模式

新fresh process沿真实J命中继续至Guard实际HP0，保留所有Crit、受伤、躲避和必要失败，不能预置低HP/补85或public杀Guard。death pin唯一Died.EventId/AtTime/Entity及触发原玩家HitReceipt；原Died优先于共享边界未issued Active；碰撞/伤害资格即时关闭，不能等动画结束。

读实际 `DungeonFairytaleGuardFullDrawV003` 的DeathAge/TerminalPresentation/DeathAfterglow：6帧起点0/.1/.2/.35/.55/.75，总art1s，余辉仅前100ms，末帧hold；MaterialHit在.22s后清。没有手动Tick/改AnimationTime。若bGameOver使kernel停钟，仅接受现有central terminal AnimationTime的明确TerminalPresentation；否则依据实际S.Time-Died.AtTime。原生是否持续绘制死Guard满1s须实跑确认。

正式结算使用既有`SettleFirstBatchGuardDeath`自动路径：它读唯一原Died.AtTime，之后ClaimStoneGuardDeathEligibility/RewardClaimed由GameMode自己调用。观察器只读`IsStoneGuardDeathObserved/IsStoneGuardDeathSettled`、`CaptureRunRewardsSnapshot()`、`QueryFirstBatchGuardRoom()`、Pickups，不调用Claim/OnFighterDied/TryCollectRunReward来冒正常流程。核一次Died、一次claim、一个Guard9coin source/object、slot2.Dead/CoinObjectId、RoomClear时间；先前Knight/Bat各7/4属于诊断前置而非正常全战。

Death6完成后用WASD走向真实Guard coin Object.Position；GameMode automatic收币需生存、地面、同Run/Owner/Room、LOS、|dx|≤60/|dy|≤30。记录Coin Object/Source/CollectionOperation、BeforeCoins→AfterCoins恰增该ResolvedAmount，不能硬宣称钱包必40（前两堆可能没拾）。可观察稍后数帧确保无重复死亡/奖励/金币，不延长至无用90s。终局不必进门/恢复存档；这与现有Save回归无关。

风险／替代：StunIR的真实六刀准备跨越敌人Windup/Active，受伤会中断英雄连招；先做短的普通J receipt/poise观测诊断，按真实回执调整正常输入时机。若SWD方案无法稳定在原占用窗内非致死破韧，保持RED；可另经Root同意用合法公开装备来源+真实E换GSW（基础42/36/48，首两刀78仍不足85），但会失去当前军剑棕皮视觉范围，不能静默替换。Death多刀战斗的原始PNG成本高于单斧23s，实际用本场景有界deadline与完成即停；按原生files/offsets核成本，不预报固定时长或全行完成。
