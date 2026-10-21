# Fighter / Stone owner Schema2 最终独立复核

日期：2026-10-16（Asia/Shanghai）。结论：在当前 BoundPlayer / StoneKnight / StoneBat 本地 owner 合同范围，完整静态复核未发现最终 v009 的新阻塞问题；真实极小位移、原生锚点与枪口原点反例已由 RED 转 GREEN。独立读取 `024633` 实际报告：111 Success，0 warnings/fail/notRun/inProcess；原 103 个完整测试名称全部保留并 Success，新增精确为 Actor5 + World3。完整 Run 聚合安装、磁盘 Continue 和正常输入续玩仍未完成，本报告不为其认证。

本审查只读 Source、合同、测试、实际报告、DLL、冻结快照及本机 UE5.5 原生实现；没有运行 UE/UBT，没有修改 Source/测试/脚本/ledger/图片或旧报告。先完整审了冻结 v006 的 owner 区块、全部私有字段、Snapshot/Context、Bat driver 与五组测试，再对 v007、v009 的窄差异逐项复核。v001 合同保留；v002 是实际证据驱动的合同修正。

## 完整值与候选安装

Snapshot 包含实际稳定 Run/Room/Entity/Kind，body XY、HP/MaxHP、跳跃高度/速度、Facing、Coins、team/AI/death/report，Focus 镜像、受击/无敌/韧性 timers，空中攻击预算、HurtProtectionSource、LastSkillEventId、发射冻结 pose，显示 Attack/Animation/Combo/Moving 等连续值，以及恰一种完整 player 三内核或 Knight/Bat state。legacy window/hit/换甲字段保留其原值；schema2 显式拒绝其正在承担不支持的 legacy 义务，不能静默丢掉有效操作。

Capture 默认读取真实 bound GM：要求完整模拟/伤害批外，检查 Root 平面原生形态与 parent 链，再取真实 GM 的已绑定 EntityId；没有用 GetUniqueID/QA fallback 分配或代替稳定身份。显式 staging Context 仅供调用方提供批准的 saved aggregate，指针只活在调用期间，不进入 payload。Capture 在局部 S 完整校验后才写 Out，拒绝不会留下部分输出。

Restore 先校验 schema、scope、Kind/恰一内核、finite/domain、原生组件链，再在独立 Combat/WA/Dodge 候选中 Restore，或对独立 Knight/Bat 纯状态作严格校验。所有可失败的校验、driver Restore 与 Knight feedback tail seed 都在第 431 行后的实际安装之前。最终安装复制所有数值/数组/完整内核，并重建同步 cache、清单批 cache 与未接受物理输入；没有 ResetFighter、Initialize、BeginCombat、动作重启、重新分配 ID、伤害提交或领取奖励。

Combat.PendingPrimary 与 WA 私有未接受输入被清理，已接受 ComboReady/阶段/expiry、动作 IDs/原期限、terminal PendingEvents 和历史回执保留。StoneFeedback 是合同明确的 transient 输出日志，仅从 saved EntityId/NextEventId seed 尾部，不能重播旧命中、音效或奖励。同步 cache 从各自 saved kernel.Time 重建，不把整个离线时段计入动画。

## 跨 owner 关系与合法历史

验证使用保存的 Equipment/World，不能拿目标 Actor 的 live GM 补齐候选。Equipment owner 在独立对象中完整 Restore；World Context 在本 owner 内核 scope/binding/reference 门之外，仍由调用方负责先运行完整 World owner 校验，不能把轻量 scope 检查描述为整个 World 已获认证。

- 玩家当前 Combat/WA 实例与保存库存 active slot 一致，FocusMirror 精确等于 `float(WA.Budget.Focus)`，MaxHealth 对应解析后的 MaxHP；实际 Pawn.Health 不被 Stats.CurrentHP 覆写，也没有不合理的强相等。
- WA 已导入但换下/丢落的实例对照全部 Inventory.Items 历史，不要求仍在当前槽；未拾取地面物不必在 WA.Instances。ResolvedImport 对照真实 Pickup 和原 Source.SpawnItem 的初始 Ammo/CD；重新拾取既有实例沿原 import 历史，不重置资源。
- Inventory.RuntimeUpdates 与实际发生资源变化的 WA.WeaponRuntimeHistory 双向要求唯一、实例/时间/before/after Ammo/CD 精确匹配；不从最终弹数反推过去是否补弹。Import/Focus 游标与装备 owner 对照，Crit receipts 在对应 Combat/WA 的 action/event/time 域内，已锁定动作与历史窗口/发射要求对应已解析 draw，不再抽随机。
- HurtProtectionSource 要有同 target 的已消费 hit 和实际正损血 direct fact；历史命中目标只要求存在于保存 binding 历史，允许已死亡/旧房间实体。
- 冻结 XBW emission pose 对照完整 WA.Issued 的 EventId/ActionId/Subhit/Instance、时间、Facing、原点与唯一 World projectile；反向要求每个已接受 XBW emission 恰有一个 owner frozen socket。旧发射不会从当前显示/当前自定义 muzzle 重算。

Kind 只支持三种当前正式 owner。Knight/Bat HP 使用 double kernel → float Actor 精确投影，RewardClaimed 与 DeathReported 对照；Bat 精确 combat Z 独立于 float 显示高度。每个 kernel.Time 允许小于等于保存中央时钟，死亡空中玩家仍可保留 WA airborne 预算，GameOver 死亡 Bat 的显示可以落地而 kernel.Z 冻结。没有 StepTo/NotifyLand 去“校准”这些合法终局。

Bat 新显式构造直接使用 saved InitialTime/InitialPosition 初始化 Kernel，随后严格 Restore；不读取或暂时移动 target 到出生位置。旧三参数构造及所有既有 driver 行为保留。Actor body 与 kernel XY 的合法微差使用已存在的本机 UE 默认 FVector::Equals 原生投影谓词，而不是新增容差；两份保存值都保持原数值，安装仍须精确。

## Schema2：实际锚点不能从 Jump/Facing推算

独立读取真实 `023434` targeted Actor5：4 Success、1 Fail、0 warnings/notRun，只有 Atomic 三个错误。报告 SHA `d1bfa19c8cf485ca9d44ef8871a9eb80d125483943396c3cda2b0ee6826a99ed`（5393B）；这是五项定向实测，不是 full111。

三个错误分别是 1e-10 初始 staging body 差没有精确消除、真实 HeightAnchor 相对/世界变换改变、public custom muzzle origin 改变。实际普通 StartJump 加两次中央 Tick，观察到 JumpHeight=`0.00063629908254370093`，而 native anchor relativeZ/worldZ/publicMuzzleHeight=`0.00062999915098771453`，simulation=`1.009999997414468e-06`。源快照/kernel/journal没有被手造；组件可保留上一帧数值，因此 v001 合同将其当纯派生值的假设不成立。

v009 改为 Schema2，新增完整数值 `HeightAnchorRelative`。Capture 第 386 行直接读实际组件 relative transform，测试签名覆盖其 translation/quaternion/scale；Validate 第 145 行在安装前检查。结构域为 finite、normalized quaternion、X/Y=0、Z>=0、identity orientation、scaleX±1/scaleY/Z=1。**没有强制 Z==JumpHeight 或 scaleX==Facing**，所以保留合法原生滞后/terminal 未使用状态。旧 schema1 和未知 schema3 都明确拒绝，不猜缺字段默认值；当前尚未交付磁盘编码/迁移。

Restore 第 480–487 行先原生 NoPhysics 写 body，再 force 更新 Root 世界数值；随后用同一原生 direct/cache/force helper 安装 saved anchor 和原 muzzle。四份本机引擎源码 SHA 均与证据一致：TransformVectorized.h 的 ContainsNaN 实际检查 rotation/translation/scale 中 NaN 或 Infinite；EngineTypes.h 的 NormalizedQuatToRotator cache 保留保存的原 quaternion，随后 RotatorToQuat 取回它；SceneComponent 的 direct setters 写相对分量，非 None teleport 使 ComponentToWorld 绕过二级 UE_SMALL_NUMBER 抑制。没有通过放宽 exact 断言、改变源 Jump 或旧 Sync 来掩盖偏差。

v007→v009 只有 Fighter.cpp、Snapshot.h 和测试三份变化；Fighter.h/BatDriver.h/.cpp 不变。从 Fighter constructor 开始的全部旧 runtime suffix，与初始 Stage0 before 及 v009 before 逐字相同。五个注册名称没有增加或替换；旧 body+1 拒绝、1e-6/1e-10 原生 staging、实际 nativeLag anchor/publicOrigin 的精确断言保留，新 schema/finite/水平位移/scale/rotation 负例走完整 Out/组件/资源/audio 原子检查。新增字段没有进入旧 gameplay Sync 路径。

## 最终实际与冻结绑定

依据 `source-assets/production/backups/2026-10-16_fighter-schema2-world-actual111GREEN-v069/compiled-source-manifest.json`，独立重新读取 **1085 个文件、73,299,914B**，长度/SHA 差异 0。以下关键项同时核对当时 live 文件，差异 0：

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| DungeonFighter.cpp | 98779 | 834aae1d256ff894fd9c656088f96de4cca23b344d7f069790a61050b00132a2 |
| DungeonFighter.h | 10153 | a79c9d5898101093ada0e8eade00b8edb74a9704eebc210e211428f2045c3468 |
| DungeonFighterSnapshot.h | 3680 | 4668cc12f6091729b6aecc54a1c738e1f867b1c63f6eb2afd90375d0797ccf3e |
| DungeonStoneBatDriver.cpp | 21498 | c819ed2a5f1704e7208d2723db2f962af5a7f3496e32634b8692e415f8ea72c4 |
| DungeonStoneBatDriver.h | 1944 | 63674be5e23ce3f7003522c3d510427bf3d5997716ab797edf0047038da87006 |
| DungeonFighterSnapshotTests.cpp | 47423 | 21789d30e819493c920961bd92a2b13ef20523fd3b0849111677820d1b883554 |
| UnrealEditor-CodexDungeon.dll | 3041280 | 2665d1f0058935cd3cc739fbef1851eb4f6f4637d2d6dc8af4628ce983b434de |
| build-editor-20261016-024450.log | 6045 | 99f27882bf3b1a63d290584ac3e56c5ffcdcb2d32217f794cf97d5177d385313 |
| FirstRoom-20261016-024633/index.json | 80040 | c5fb9d8a1c2c8b50858f466364890ccc0b2d6da157714d9f7ac53fc596b71b03 |

合同 v002 SHA `aaf76224149eddf34f6a53de0e74bc717053e728550f080e1110547472f847e8`；原 v001 未覆盖。World .cpp 仍为 `8c4b0a23…`，测试 `850534ce…`，同次 World3 也全部 Success。

独立报告集合比较以 `004750` 的原 103 名称为基准：缺失 0、非 Success 0；新增精确为原定 Actor5/World3，均 0 errors/0 warnings。五组实际覆盖 accepted combo/buffer、保护 dodge/poise、空中左向自定义 XBW emission/装填边界、Knight dormant/wake/locked charge/shield/已领取 death、Bat 非零 birth 与移动/低空/rise/terminal，以及全部同组原子负例与本次原生反例。历史 `022654` 的 111GREEN 保留；它没有被用来冒充后来新增的 `023434` 断言已经通过。

## 进度边界

这些实际测试在 UE 中建立真实 GM/正常公开行动来源，再恢复到独立 staging Actor并回捕获，部分后续动作义务由严格纯内核边界继续验证。它们没有安装整个 live GM 的 Actor map、重建场景/库存/世界事务，未进行新进程正常输入 Continue；staging Actor 尚不能代替最终稳定映射根。默认脚本入口的后续 `v070` 实际结果将另作新增审查，不覆盖本次历史运行。没有观看新视频或试听声音；完整装备/敌人内容仍为 0/15。
