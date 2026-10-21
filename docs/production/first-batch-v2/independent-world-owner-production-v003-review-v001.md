# World owner v003 独立只读复核

日期：2026-10-16（Asia/Shanghai）。本报告冻结于晚到 burn refresh 反例实测之前。事实结论：`020837` 的 World 三组测试全部 GREEN，原 103 项全部保留并成功；全量仍为 108 Success、3 Fail，不能称完整 111 通过。静态复核另发现一个同范围的晚到刷新缺口，已通知 root 并由 root 加入真实公开流程反例，尚待实际结果。本报告不覆盖此前 stage0 审查。

## 审查范围与冻结依据

本次只读源码、实际 Automation 报告和保全快照，没有运行 UE/UBT，没有修改 Source、测试、脚本、ledger、媒体或历史报告。范围是 schema 1 的单个绑定 player 的 `FDungeonWeaponWorldState` 深值 Capture/Restore；Context 指向已保存并校验的同一 WA 状态。它不是 Actor map 的整局安装，也不包含磁盘 Continue、全局存档容器或 DamageBatch 重新提交。

以 `source-assets/production/backups/2026-10-16_worldGREEN-fighter-projectionRED-v064/compiled-source-manifest.json` 绑定的历史文件为实际运行依据，独立重新读取并计算了以下 SHA：

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| DungeonWorldSnapshot.h | 978 | d3a0e9d2a3117f4ab5a2fad65fad96fbc522a0b8d9439b32bd6671667cd632d7 |
| DungeonWorldSnapshot.cpp v003 | 24503 | 050b5bee71c46919c7e0277329ebb72abf7b68e1b2473b13decab2c3e061592f |
| DungeonWorldSnapshotTests.cpp | 27389 | 82f3513fcac16b95df7fbd3c40172cf43b6ac2904c7ec3be5065a012db434871 |
| UnrealEditor-CodexDungeon.dll | 3010048 | 04fdc18a563355c64f9f4c2062bb72c668c101e9a491593f494dc7dc713a2da6 |
| build-editor-20261016-020807.log | 4258 | be10f4d3e7a37681917822f4e09b95e04024d302588b9795ef596f9307079ecb |
| FirstRoom-20261016-020837/index.json | 83969 | a6c85c95e57acc7ec3c679712732bf21d7dfceeacd090271d275003ffdd5301a |

这些历史文件均与 v064 manifest 的长度、SHA 相符。审查时当前 live World .h/.cpp 仍与此版本相符；live tests/DLL 已因 root 的下一轮合法测试/构建变化而不同，所以没有用后来的 live DLL 代替历史运行绑定。`production-v003/manifest.json` 中的 `uncompiled/unverified` 是生成时的历史状态，不修改它；实际结果以随后独立保存的 `020837` 报告和 DLL 为准。

## 生产约束及六项实际反例修复

原 v001 的 `FKey` 私有别名与引擎全局类型产生实际编译歧义；v002 只改名为 `FWorldKey`。本报告不把这一编译修复当行为验证。v002 随后的实际 `015859`、`020355` 才暴露以下行为缺口；v003 对应关闭了已加入的六类反例。

1. **发射域完整性。** 在现有逐 source 对 WA Issued 的完整事实相等与唯一 ID 门后，v003 第 133 行增加 Sources/Issued 数量相等。它补齐反向关系，拒绝保留 WA.Issued 却删除所有 world 攻击、receipt、burn、journal 并重置 cursor 的候选。没有重新 Step/Initialize WA 或从 live GameMode 补造遗漏内容。
2. **Range stop 的实际截止时刻。** 第 216–218 行要求 Range 事件时刻精确等于原发射时刻加 `(Range-LaunchForwardDistance)/ProjectileSpeed`，保留原 ballistic position/travel、socket/anchor 验证。实际 live projectile 被提前改成 Range stop 的候选在默认与自定义 socket 两个路径均被拒绝；不能用当前一致的 stop journal 抹去仍在飞行的义务。
3. **正伤害 DirectHit 唯一性。** 第 234–236 行按 EventId/TargetId 记录已经出现的正损血事实，拒绝同一消耗 hit receipt 的重复 journal。仍允许真实消耗 receipt 在 float HP 无可表示差值时没有正损血事件。`015859` Invalid 组后续三个 unchanged 失败受先前已安装坏候选污染，不把它们计成三个额外独立生产缺陷。
4. **Burn 必须有应用历史。** 第 249–259 行要求 BurnApplied/Refreshed 具有同源同 target 的正损血 direct fact；第 286 行要求 burn 值域与重建的 application target 域一致。删除 application journal 并重新编号不再能保留可恢复 burn 状态。
5. **正 burn tick 必须落在继承相位。** 第 268–277 行按同 target 当前应用 source、原 expiry 与逐次 `+1` 重建 phase；允许跳过没有正损血事实的 tick，但正 tick 时间必须与继承游标精确相等。`nextafter` 移动实际 tick 不再被接受。
6. **保存的 NextTick 必须与实际应用/刷新/正 tick 一致。** 第 289–295 行对 active status 推进到保存的 world.Time 后精确比对 NextTick；inactive 第 302–305 行只保留已证明 phase 的下界，允许合法死亡/旧房间导致未继续消费义务，不强行追赶到当前房间时间。实际 NextTick 的微小漂移被拒绝。

上述验证仍在最终单次 Candidate 安装之前。没有在拒绝时修改 Out，也没有改为容差、修补数据、重排历史、重抽随机或回放战斗。深值 roundtrip、后续 live tick 不污染 saved/out、候选数组与 source 不别名的原正例仍保留。

## 时间与真实合法状态

Burn journal 按同 target 的 **Sequence** 重建，不要求所有事件的 AtTime 全局递增，这与实际 GameMode 的 damage batch 顺序相符：已接受 damage facts 可以先写完，然后再应用其中较早时刻的 burn refresh。刷新只消费尚未消费的旧 phase，不能因较早 AtTime 将已证明的游标倒退。也不能改成 `latestAppliedAt + integer`，因为 equal refresh 正常继承旧 tick 相位。

`020837` 的三个 World 测试实际运行包含：默认/自定义冻结发射 socket 的真实飞行；真实 ammo 消耗；有限大 float HP 产生消耗 receipt 但零可表示 HP loss；第二把真实 staff 通过 E/确认/Q 流程产生 equal refresh；烧灼到期历史；以及同 Run 清敌、E 打开出口确认、Enter 真正换房。换房正例保留旧房 window、已消费 hit/burn、binding tombstone 与 RoomExit 停止的仍在飞行 staff projectile，同时新敌人获得新身份。不能为了当前房间要求删除旧 source/actor binding 历史。

unknown schema、跨 Run/Owner/Room/Time、缺失 saved WA、非 finite 数据、source/receipt/socket/anchor/cursor/journal 跨引用负例仍在原三组内。测试中的完整 world 签名覆盖全部 owner 数组和元素字段；这是该 owner Out 的原子性证明边界，不外推为整 Actor/Scene/Equipment 聚合安装已完成。

## 尚未关闭：超过旧 expiry 的刷新

**[P2，静态推断，尚未实际 CPP 证实]** v003 第 261 行 Refresh 门校验 Prior.Active、AppliedAt 单调与 DPS，但没有拒绝 `E.AtTime > Prior.ExpiresAt`。`AdvanceBurnPhase` 在旧 expiry 之外停止消费并返回成功，随后第 265 行换成新 expiry，允许一个已过期的 source 在删去 Expired 事实后被伪装成继承旧相位的 Refresh。

可由真实公开流程构造反例的最小方向是：让第一次真实 burn 正常到期，等真实第二 staff 技能 CD 后 K 产生新的 BurnApplied；先证明原状态 Restore 合法，再仅在候选中删去前一个 BurnExpired、将末次 BurnApplied 改为 BurnRefreshed、把 NextTick 改成旧应用的继承 phase、重新编号 journal。其余 emissions、positive hits 和 source 仍来自真实流程。当前 v003 的 replay 路径可能接受该一致但错误的历史，并改变下一次 tick 时刻。

实际 GameMode 按旧 expiry 限制 burn 是否可 refresh；在**恰好等于**旧 expiry 时仍可能在本次 batch 中先 refresh，因此最小修复建议是严格 `>` 门，而不是 `>=`。root 已收到本发现并加入真实 fixture/候选；新的 tests SHA `850534cea7034cba862702f933e6820690f6351187fc77736c31ac74aee51d7f`、31133B 不属于本次 v064 的 `020837` 运行，不能追溯算作已经通过。本报告保持该项未关闭，等待真实 RED/窄修/再次实际报告。

## 实际报告独立核对

`020837`：108 Success、0 SuccessWithWarnings、3 Fail、0 NotRun、0 InProcess。三个 `CodexDungeon.Content.WorldOwnerSnapshot.*` 全部 Success，各 0 errors/0 warnings。以 `004750` 报告的原 103 个完整测试名称作集合比较，缺失 0、状态非 Success 0；新增名称精确为 World 3 + FighterOwner 5，没有替换原测试名称。

剩余三项 Fail 为 FighterOwner 的 PlayerAcceptedActionsAndProtection、KnightActionsHitsAndClaimedDeath、BatBirthAnchorMovedAndTerminalPresentation，分别为 1/1/3 errors，均 0 warnings。它们由独立 Actor owner 工作继续处理，本报告不替其认证。World 三组目前的 GREEN 只证明本轮已运行断言，不消除上述新静态边界，也不构成完整游戏内容单元验收。
