# Fighter / Stone owner 快照合同 v001

2026-10-16。只读源码合同，尚未实现这些类型或接口，未运行 UE/UBT；装备/Scene/Fog owner 的通过不代表 Actor 或磁盘 Continue 已完成。证据目录为 `evidence/fighter-owner-snapshot-contract-v001/`，保留本次所读源文件及 SHA。

## 事实

- Fighter 没有整体 Capture/Restore。玩家 Combat v3、WA v3、Dodge v2 的纯内核已有 Capture/Restore；Knight v1、Bat v1 同样已有。完整 state 已含动作冻结参数、命中/资源回执、游标与截止时间，不能用“重新开始招式”替代。定位：[Fighter.h:142](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.h:142)、[Combat.h:163](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonContentCombat.h:163)、[WA.h:410](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponActions.h:410)、[Dodge.h:184](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonDodge.h:184)。
- KnightDriver 的 Restore 仅转发 Kernel（[cpp:148](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneKnightDriver.cpp:148)），不更新 Actor；BatDriver 尚无 Restore。Dodge.Restore 强校验原 OwnerId/InitialTime/InitialPosition；Bat.Restore 强校验 EntityId/InitialTime/InitialPosition；Knight 校验 EntityId，但没有 InitialTime 字段。[Dodge.h:70](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonDodge.h:70)、[Bat.h:97](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneBat.h:97)、[Knight.h:82](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneKnight.h:82)。
- 正常 bound 身份来自 GM.WorldEntityIds；GetRuntimeEntityId 的非 bound fallback 包含 GetUniqueID，不能作为跨进程身份。[Fighter.cpp:469](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:469)、[WorldProjectiles.cpp:217](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.cpp:217)。新目标 Actor 在安装前尚未被 live GM 绑定，校验须使用聚合提供的只读身份表，不能先 Admit/消耗 NextEntityId 来“取得正确 ID”。历史 HitReceipts 的 TargetId 可能属于旧房间/已死亡实体，应对照已保存 ActorBindings/历史身份，不能要求目标当前存活。
- InitializeStoneKnight/InitializeStoneBat 是新生入口，含 BeginCombat、初始 HP/高度/计时器重设；ResetFighter 也是重置。[Fighter.cpp:415](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:415)、[436](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:436)、[854](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:854)。恢复不得调用这些入口补“默认值”。

## 建议的最小值结构

以下是可实施的 **新 header 草案**，并非已存在 API。schema1 先明确只支持 BoundPlayer / StoneKnight / StoneBat；原型通用敌人与 unbound legacy 模式应显式拒绝，不能被默认转换为玩家或石像。所有 float 保持原存储精度，JSON 层以后须无损往返；uint64 仍十进制字符串。

```cpp
enum class EDungeonFighterOwnerKind : uint8 { BoundPlayer, StoneKnight, StoneBat };
struct FDungeonFighterEmissionPoseSnapshot {
    uint64 EventId=0, ActionId=0; uint32 SubhitId=0;
    DungeonWeaponPoseSocket::FResolved Pose; // 全值；含发射时冻结世界原点
};
struct FDungeonPlayerKernelSnapshot {
    DungeonContentCombat::FCombatState Combat;
    DungeonWeaponActions::FState WeaponActions;
    DungeonDodge::FState Dodge;
};
struct FDungeonFighterOwnerSnapshot {
    uint32 Schema=1;
    FGuid RunGuid;
    uint64 RoomInstanceId=0, EntityId=0;
    EDungeonFighterOwnerKind Kind;
    FVector2D GroundPosition;
    float Health=0, MaxHealth=0, JumpHeight=0, JumpVelocity=0, Facing=1;
    bool Enemy=false, AIEnabled=false, Dead=false, DeathReported=false;
    int32 Coins=0;
    FString EnemyContentId, WeaponId, ArmorId;
    float FocusMirror=0;

    // 真正参与玩家准入/伤害/运动的 Actor 私有状态
    float InvulnerableTime=0, HurtTime=0, AttackCooldown=0;
    float PoiseAccumulation=0, PoiseDecayDelay=0, PoiseProtection=0;
    bool AirPrimarySpent=false;
    FDungeonWorldWeaponKey HurtProtectionSource;
    uint64 LastSkillEventId=0;
    std::vector<FDungeonFighterEmissionPoseSnapshot> EmissionPoseSockets;

    // 也保留首帧显示连续性；AnimationTime 还输入真实 muzzle pose 求解
    float AttackTime=0, HitFlash=0, AnimationTime=0, LandingVisualAge=0;
    int32 ComboStage=0;
    bool Moving=false;
    FString AnimationName, AttackPhase;
    bool CustomMuzzle=false;
    FTransform CustomMuzzleRelative=FTransform::Identity;
    double BatObservedHeight=90; // 精确战斗高度，不用 float JumpHeight 替代

    // Kind 决定恰有一个存在；三份纯 state 不互相填补
    TOptional<FDungeonPlayerKernelSnapshot> Player;
    TOptional<DungeonStoneKnight::FState> Knight;
    TOptional<DungeonStoneBat::FState> Bat;
};
// Context 是调用期只读聚合视图，不进 payload：批准的 Run/Room/Entity，
// SimulationTime/GameOver、装备 owner、世界攻击/历史实体身份等。
bool CaptureOwnerSnapshot(FDungeonFighterOwnerSnapshot& Out, FString& Why) const;
bool RestoreOwnerSnapshot(const FDungeonFighterOwnerSnapshot& In,
    const FDungeonFighterRestoreContext& Context, FString& Why);
```

字段依据与处理边界：

| 当前字段 | 处理 |
| --- | --- |
| JumpVelocity、InvulnerableTime/HurtTime、PoiseAccumulation/DecayDelay/Protection、bAirPrimarySpent、HurtProtectionSource | 必须保存原值，不能由 HP/阶段猜出；参与 [准入:652](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:652)、[伤害:755](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:755)、[运动:1107](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1107)。 |
| LastSkillEventId / EmissionPoseSockets | 保留消费游标及已发射冻结 socket。游标只需是合法已消费位置，不一概等于 WA.NextEventId−1：终端中断可能被真实 GM gameplay guard 跳过（[GM:1534](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1534)）。Pose 逐条对照 WA.Issued 与世界 emission 身份，历史原点绝不从当前 Actor 重算。 |
| AnimationTime / 当前 muzzle mode | [Fighter.cpp:309](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:309) 把 AnimationTime 传入 pose solver；应保留。有效 CustomMuzzle 还包括“组件相对变换已不同，但 bool 尚未被下一次 Sync 置 true”的情况（284–303）。只保存自定义相对变换的值；自动模式按同版 authored geometry 重建，并在首次 Sync 前建立正确 LastAutomaticMuzzleTransform cache，避免误判为自定义。 |
| WeaponMuzzle/HeightAnchor、Driver.Owner、Controller、RootComponent、GetUniqueID | Actor/组件/弱指针只重建，不入 payload。仅保存数值定义及稳定身份。当前正式平面 Actor XY、Z=0、默认旋转/缩放之外的 QA 变换须明确支持或拒绝，不能默默丢弃。 |
| HitAction / bResolvingContentWindow、BatchSkillStepAt/Delta、bSuppressOrdinaryMovement | 单批临时缓存，不保存；捕获必须在完整批外且非 resolving/suppressed。旧 BatchSkillStep 值可残留，下一批会覆盖；不能为清它而执行模拟。 |
| SkillWindows / SkillHitReceipts | 当前 bound 分支使用 GM.WeaponWorld，跳过这两份 legacy Actor 数组（[GM:1214](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1214)、[1335](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1335)）。schema1 应核它们为空；若要支持 unbound，另加完整旧字段合同，不能无声清空有效窗口。 |
| PendingArmorId/ArmorChangeRemaining、AttackElapsed/bAttackResolved、FocusConsumeAge、bHasAxe | 当前 bound 正式路径不用旧换甲/旧攻击/旧Focus系统；BeginArmorChange 明确拒绝 bound（[526](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:526)）。新 schema 须核无正在进行的 legacy 操作；若支持 legacy，必须追加其完整状态而非借用 Equipment.Action。 |
| LastStoneSyncTime / LastBatSyncTime、StoneFeedback、HUD 音效游标 | 同步 cache 重建到已存 kernel.Time，避免首帧把整个离线间隔加到动画。StoneFeedback 已注明 transient，新的 Journal.Begin(saved EntityId, saved NextEventId) 只 seed 尾部，不重播历史（[Feedback.h:13](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneFeedback.h:13)）。HUD 同理；过去命中/奖励的内核回执仍完整保存。 |

## Restore 顺序与校验

1. **先纯校验**：已知 Schema/Kind、恰一份相应内核、身份在同一 Run/批准实体表、所有数值有限且处于本类型合法区间、朝向 ±1、合法 HP/Coins/坐标。Context 来自待恢复聚合，不能拿 live 当前 Pawn 的身份/装备来替代 saved 根。失败不得改变目标 Actor 位置/组件/内核/资源，也不发音效/事件。
2. **构造独立候选内核再 Restore**：Combat 可按保存 Weapon/Instance 构造；WA 默认构造后直接 Restore 完整 state（其构造第3参数是 Ammo，不是 StartTime，见 [WA.h:331](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponActions.h:331)），不调用 Import/Equip/Press。Dodge 必须用保存 OwnerId、InitialTime、InitialPosition 构造。Knight 使用同 EntityId；Bat 必须使用保存 InitialTime/InitialPosition。不可 StepTo(Now)“校准”、重新抽暴击、补弹或清空历史。
3. **交叉核对**：玩家 Combat/WA 装备实例对应保存库存的当前槽，WA 包含已导入的退役实例是合法的，地面未拾取武器不必已导入 WA。Ammo/CD/预留量、Focus 单一预算、Crit/Import/Focus receipts 对照装备与世界根。FocusMirror == float(WA.Budget.Focus)；Pawn.MaxHealth 对照保存装备解析 MaxHP，Pawn.Health 保持实际值，不能用装备 Stats.CurrentHP 覆写或无条件要求相等。动作互斥只按真实规则核（例如 reload 可由 dodge 正常取消），不把不同 action domain 的同数值 ID 当冲突。
4. **HP/高度投影**：Knight/Bat 的权威是 double Kernel.HP、Phase、Position；Actor.Health 应精确等于 `float(Kernel.HP)`，不要求 double HP 等于已舍入 float。MaxHealth 对照对应 Definition。BatObservedHeight 保留 double Position.Z，正常非终局画面 JumpHeight 是 float 投影。Knight 的 Actor Poise/Hurt 字段当前并非全部由 SyncStoneKnightState 同步，不臆造它们与内核逐字段相等的规则；以 kernel 负责的语义为准。
5. **安装仍由聚合暂停协调**：先验证所有 owner/世界引用，再在暂停的 staging actors 构造并挂接 drivers、组件；全部成功后才替换 live 根和稳定 ID 映射。单个 Actor Restore 成功不等于整个 Run 事务已成功。安装后从保存 state 恢复镜像/显示，清单批 cache 和未接受的物理输入缓冲，seed 反馈尾部；不调用 Reset/Initialize/BeginCombat/ClaimDeathReward/OnFighterDied/Admit 或历史消费函数。Combat.ComboReady/NextComboStage/ComboExpiry 是已存在连段状态，应保留；Combat.PendingPrimary 与 WA 私有 PendingPrimary 属未接受输入，在 Continue 输入代清理（WA.Restore 已清后者，Combat.Restore 不会自动清）。

### BatDriver 最小补口

仅仿照 Knight 增加 `bool Restore(const DungeonStoneBat::FState& S) { return Kernel.Restore(S); }` 还不够：现 [BatDriver.cpp:79](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneBatDriver.cpp:79) 构造把 **Owner 当前 XY,90** 固化为 InitialPosition，已移动 bat 的保存 InitialPosition 与当前 XY 不同。

建议保留原 ctor 行为，另加显式起源 overload（或等价只读 factory）与严格 Restore：

```cpp
FDungeonStoneBatDriver(ADungeonFighter* Owner, uint64 EntityId,
    double InitialTime, DungeonStoneBat::FPoint InitialPosition);
bool Restore(const DungeonStoneBat::FState& Saved); // 仅 Kernel.Restore
```

新 ctor 直接初始化 `Kernel(EntityId,InitialTime,InitialPosition)`，不读/挪动 Actor、不 BeginCombat；聚合按保存起源构造候选后 Restore。不要暂时把目标 Actor 移回出生点、构造后再移到当前点，也不要放宽 Bat.StateValid 的初始锚点相等检查。

## 合法终局与风险

- GameOver 的 [GM:1405](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1405) 只调用 [AdvanceTerminalPresentation:1099](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1099)：AnimationTime 增加，死亡显示 JumpHeight 下落；中央模拟/纯内核不前进。因此已死亡空中玩家/蝙蝠可显示高度0，而冻结 WA.Grounded 仍 false / Bat.Position.Z 仍原值。恢复必须允许这种真实终局；不得为了镜像一致而 LandAt、NotifyLand、StepTo 或改内核高度。
- “dead 时钟都停在死亡点”也不成立：世界仍运行时 Knight.StepTo 的 Dead 分支仍 Advance(Now)（[Knight.h:109](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonStoneKnight.h:109)）；玩家 Fighter.SimulateActionsTo 则 dead 早返（[1174](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1174)），GameOver 后各内核才随整体模拟停止。按每类真实调用链检查各自 Time ≤保存中央时钟，不能统一强推为同一个 Time。
- 死亡 Combat.Interrupt 可留下合法 terminal PendingEvents；完整世界批完成不等于所有纯内核队列为空。保存原事实并禁止历史重播，不用 StepTo 清队列。Kernel 允许 Dead+RewardClaimed=false；是否属于待提交死亡义务，须由聚合奖励根判定。正常已 OnFighterDied 的 Actor 应有同一次 Claim/DeathReported 与实际地面物根；恢复不能擅自补 Claim，当前 owner bool 也不能冒充完整奖励事务日志。
- 上述字段合同仍待真实 RED/GREEN 和视觉证明；它不提供新进程磁盘 Continue，也未制作未来敌人/关卡/账号系统。

## 建议的 5 组实际验收

1. **PlayerAcceptedActionAndProtection**：真实 bound 玩家正常输入/GM.Tick，分别捕获 melee 锁定/连段窗口、dodge 无敌段、跳跃空中攻击与受击/韧性保护状态；克隆到独立 staging actor，继续同输入与边界，比较伤害/命中一次性、运动、剩余保护、原 action IDs/deadlines。确认 fresh Continue 清未接受按键，不清 ComboReady/有效行动。
2. **CrossbowReloadAndEmissionOrigin**：真实左向/空中65/自定义24,7 socket 对照，捕获已射出后和 reload 插箭前后；保留 Ammo/CD/reservation/原发射 socket、装填截止与已导入退役实例，之后成功补弹仅一次。改变新 Actor 位置不得让旧 projectile 改原点；旧声音/粒子不重播。世界弹道由对应聚合同时恢复，不能只靠 Actor 测试宣称全通。
3. **KnightActionHitAndDeathReward**：真实 bound admitted knight 的 dormancy/wake、locked charge、shield 已命中回执和死亡已领取状态表；恢复到新 Actor/同稳定 ID，确认不重启 wake/charge、不重复命中/奖励、double HP→float 镜像一致，原已接受的行动期限继续。
4. **BatInitialAnchorAndTerminal**：非0中央时刻、出生 XY 与捕获 XY 不同的真实 bat，捕获 low/recovery/rising 与实际死亡；新 Actor 保持捕获位置构造，使用保存 InitialTime/InitialPosition 的新 ctor。原 last-damage receipt、PendingLow、低空期限和精确 Z 继续一致；再测 GameOver 后显示落地而 kernel Z 不变的合法终局，不挪 Actor 来满足构造验证。
5. **InvalidOwnerIsAtomic**：从以上真实快照逐项改 unknown schema、kind/内核组合、稳定身份、初始锚点、HP/Dead 镜像、非有限数、发射/命中引用及 action/resource 冲突。每次拒绝后完整目标快照、位置/组件、资源、所有游标与效果请求不变；只读 Capture/验证不可分配实体 ID。错误属于 Actor owner 的先独立拒绝，跨owner错误由同次聚合拒绝；两种测试分别标明。
