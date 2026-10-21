# Weapon-world owner Stage0 独立复核 v001

日期：2026-10-16（Asia/Shanghai）。范围是新 WorldSnapshot 的类型/上下文、三组真实流程测试与现有生产来源规则。**这是 Stage0 审查，生产 Capture/Restore 尚为桩；没有实际通过结果。** 我仅只读源码/冻结 manifest 并新增本文，没有启动 UE/UBT 或修改 Source、脚本、测试、ledger。

## 版本事实

| 冻结文件 | SHA256 | 状态 |
| --- | --- | --- |
| DungeonWorldSnapshot.h，978 B | d3a0e9d2a3117f4ab5a2fad65fad96fbc522a0b8d9439b32bd6671667cd632d7 | Stage0/v002 不变 |
| DungeonWorldSnapshot.cpp，409 B | 33279231ae085cd4a66c6b11b1a76d7e6d1ebd37f8624a54ce46019a969188e2 | Capture 返回默认值，Restore 返回 false，明确 pending actual RED |
| Tests/DungeonWorldSnapshotTests.cpp，原 15,522 B | ec603c37b86523cbb60c5d3e85d9bf6087e8f3fc45340db4ab9211f1a0822752 | evidence/world-owner-snapshot-v001/stage0 |
| 同测试，v002 18,458 B | 8098722168ede113963dec2de594b90a5be09a05b84f307be28e69c074c6f56f | stage0-v002；同三组新增真实 zero-loss、equal-refresh 控制 |

实际读取的既有来源：WorldProjectiles.h `06a874893c7521417759a00a4d0213d0b81ff85f4bc258abc2ddc94c71f1908a`；WorldProjectiles.cpp `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9`；WeaponActions.h `e8d6d2366c26b87eecc14b660b8020b31a4e7c674c7256479a536ba8d2b91586`；WeaponPoseSocket.h `722d6fae382704b36e6c0e105fb63cdb25d66eacc53cd5722b0431bf41ba6848`。Fighter worker 同时编辑其他独占文件，本审未对未冻结 Fighter 实现作结论。

## 类型与上下文

Snapshot 是 Schema1 与完整 FDungeonWeaponWorldState 的值封装，后者含 Run/room/time、entity/event 游标、历史 ActorBindings、Projectiles、Windows、HitReceipts、Burns、Events。没有以 UObject 地址替代 stable key；这些状态字段和其中 FEvent/FAction/FResolved 均是可按值复制的数据。

RestoreContext 提供批准的 RunGuid、当前 RoomInstanceId、OwnerId、SimulationTime 和保存玩家完整 WeaponActions::FState 的 const 指针。这足以让当前单个 bound 玩家 world 来源与原 Issued 发射事件核对，不需要在恢复时重新发射或重新求当前 muzzle。指针仅用于同步验证、不得保存到 Out；其对象必须在调用期间存活。注释要求它是已经验证的保存 owner 状态，不能把新 actor 的默认 kernel 当来源。

这不是最终 aggregate 上下文：WorldEntityIds weak actor map、PendingDamage/batch admission、实体重建以及跨 owner 安装仍应由 aggregate 处理。旧 actor 死亡/销毁不能使历史 ActorBinding 自动无效。未来实现应验证 context 与 candidate 的批准边界匹配，并以纯 kernel 既有 Restore 或明确的 validated-only 调用合同保证 PlayerActions 可信；当前 const 指针类型本身不证明数据已验证。

## 三组测试是否有实质验证力

三组注册名保持固定：LiveFlightFrozenSocketsAndDeepValues、BurnTickPhaseReceiptsAndStoppedHistory、CrossReferenceAndNumericRejectionIsAtomic，均在 `CodexDungeon.Content.WorldOwnerSnapshot` 下。

Fixture 真正创建 Game world、GameMode、玩家与 controller；调用公开 BeginEquipmentRun/RegisterEquipmentSource，经 E 输入和真实装备 deadline 进入武器，然后 J/K 和 GameMode Tick 产生实际 World 事实。其 capture 输入来自 GetWeaponWorldState，而非手造 projectile/receipt/burn。不能把这类无图形自动化 world fixture 称为用户已看到的游戏运行画面。

FWorldProof 逐字段编码所有当前 World 字段、数组、FEvent/FAction/FResolved，FString 按值序列化，不散列 struct padding 或指针。我与这几份当前类型逐字段核对，没有发现遗漏成员。RoundTrip 检查独立 Out、旧 source/冻结 socket/range/cursor/history 精确值、下一 ballistic 查询相同，以及后续 live Tick 不改变已捕获值；坏候选使用完整 proof 对比 Out，而不是只对比几个外层标记。这比只检查返回 bool 更有价值。

默认与 custom socket 两分支确实经过公开组件偏移设置，未把旧 source 追随当前 actor。Burn 组正常 K 火线与 HP 损失产生状态，随后跨过首跳，检查原 NextTickAt 和 expiry/history。Invalid 组先有真实已消费命中，再检 schema/Run/游标/重复binding/缺target/source及position/pose NaN、range anchor、launch allowance、stop reason、receipt、journal sequence/kind 的完整原子拒绝。

v002 新控制也符合真实来源：NoLoss 在有限大 float HP 的独立目标上正常 J，允许伤害舍入后 HP 不变，但仍有实际 consumed receipt、没有正损失 journal。Refresh 使用第二个 STF 实例的公开注册/目标选择/槽确认/切换，绕过第一个实例已锁 cooldown，而非改写 cooldown 或 Burn；第二次实际技能将 source/AppliedAt 更新、保留旧 tick phase，显式断言不是 new AppliedAt+1。两项都没有手造 receipt、burn 或 journal。

但此时没有收到实际 Stage0 引擎结果。且桩 Restore 的第一 positive control 会提前返回：v002 Flight 第 128 行、Burn 第 162 行、Invalid 第 197 行。因此第一次 stub RED 即使三组都失败，也不证明后面的 zero-loss/refresh/negative 流程已经执行。实现后的真实 full regression 才能确认这些控制实际到达并通过，不能提前追认。

## 生产验证必须遵循的现有语义

1. **原发射是历史事实。** ConsumeBoundWeaponEvents 第 285–315 行把真实 FEvent、emission-time pose、actor range anchor 与 launch allowance 固定到 world。来源应匹配保存 WA.Issued 的完整 key/payload，不重新根据当前 Action、当前位置或当前贴图大小计算旧发射。历史 Source.Action.Active 是发射时快照，不要求与当前已经完成的 action 一样。
2. **消费 receipt 不等于正 HP 损失 journal。** Projectile receipt 第 372–374 行、window receipt 在 GM 第 1358 行先记录消费；GM 第 1143–1159 行仅 Loss>0 时追加 DirectHitCommitted/BurnTickCommitted，并对正直伤申请 burn。不能要求每个 receipt 必有正损失 journal，也不能用一次当前 HP 查询重放旧伤害。v002 zero-loss 专门保护这一点。
3. **Burn refresh 不重置跳伤相位。** 第 395–400 行刷新时保留旧 NextTickAt，只更新 key/Dps/AppliedAt/ExpiresAt。NextTickAt 不能硬要求 latest AppliedAt+1 或 latest AppliedAt 的整数偏移；第 411–415 行按原 phase 逐次加 1，expiry 时 NextTickAt 可大于 ExpiresAt。v002 refresh 控制针对这个合法状态。
4. **换房保留历史。** ClearWorldRoomAttacks 第 437–448 行停旧 projectile 并追加 RoomExit，置 window/burn inactive，不删除数组。GM NextRoom 第 1672–1679 行随后更新 current room。旧 keys、旧 target bindings、inactive attacks/status 不能被强制改成当前 room 或因 actor 不再活着而拒绝。该 clear 函数本身不为每个 inactive window/burn 追加新的终止 journal，不能仅凭 inactive 就规定统一终止事件。
5. **Sequence 与时间排序分开。** AppendWeaponWorldEvent 第 249–251 行确保追加 Sequence 连续；per-projectile traversal 可以晚追加较早 contact.AtTime，所以不能强制所有 journal.AtTime 全局递增。每个事实仍应有限、在批准时间内，与自身 source/window/burn 语义一致。
6. **有限性要显式校验。** 当前项目实际 `/fp:fast` 下曾有 Scene NaN 被 equality 漏过的真实反证。World 的 source/origin/pose/position/time 等每个 double 应先有 finite 门，再作关系比较。不能只依靠 `saved==known`。同时不能把 actor 中心 bounds 机械套给所有发射位置：作者 socket 可在边缘 actor 外部，QueryContact 第 135–136 行会合法地在 source 点产生 HardBounds 停止历史。

## 已告知 root 的覆盖边界与最小公开换房路径

原三组没有 refresh、零损失消费、旧 room history 的正控制；root 已将前两项加进冻结 v002，并表示实现前在同组补真实换房控制。Context 本身的 null/actions/错 Owner/room/time 目前也没有独立负例；这是覆盖边界，不据此把尚未写的生产逻辑判错。

公开换房需要从初始独立 fixture 就 BeginSceneExplorationPreview，不能在已经生成 World 事实后调用它——Setup 会 Begin 新 Run 并清 World。正常 Enter 启动、沿 Y0 移动、公开注册/拾取 STF、K 产生火/消费，再切 SWD 用 J 真正打死骑士；复用现有 SceneIntegration 的 KillKnightNormally/MoveAxis。到 Layout.Exit 后释放移动，等待装备/WA/Combat/dodge 全 idle，E 打开确认、fresh Enter 提交，断言同 Run/room+1 与旧 histories 保留。

如需实际 RoomExit 停止仍飞的 projectile，在出口换回 STF，先向左轻脉冲并释放，再 J；普通 STF ActiveAt=Start+.22、End=Start+.67，Range360/Speed600 到 Start+.82，idle 后约 .15s 内可 E/Enter，向左可避开出口右边界。XBW 普通弹的射程结束 Start+.16+420/950≈Start+.602，早于 End=.68，不适合等 idle 后测仍飞弹。该步骤是依据源码的建议，**我没有实跑**；需要真实前置 active 断言及 engine 报告后才可认定这个控制成立。

Stage0 接口与这三组的核心设计可继续推进，没有发现需改动既有 gameplay 的前提。生产实现仍须 actual RED 后进行，再绑定新的 Source/test SHA 和真实旧 103+新 8 全量结果。本文不证明 aggregate、Actor 安装、磁盘 Continue、新进程恢复或完整内容单元完成；正式单元仍 0。
