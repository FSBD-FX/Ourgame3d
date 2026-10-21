# 角色级闪避纯核 v2（外层已解析位置交接）

日期：2026-10-15。状态：独立 C++17 RED→GREEN，164 项检查通过，含原 113 项回归；新增外层已解析的 idle XY 位置交接和持久去重。未接入 UE 角色、Shift、身体碰撞或伤害流程，不能记为游戏闪避已完成。Probe、录音和 capture 脚本保持冻结，本任务未运行 UE、编辑器或 UBT。

## 规则事实与实现判断

权威来源：`F:/Ourgame/玩家角色与战斗规则设计.md` 第 4 节及 `docs/design/player-combat-v1/player-combat-rules.json` 的 dodge；`F:/Ourgame/道具与状态系统设计.md` 第 4 节；`F:/Ourgame/docs/production/first-batch-v2/weapon-actions-adapter-plan.md` Task 2。

- Fresh Shift、地面且外层合法独占上下文才可起招；D03 只扩充未提交道具/遗物的复合取消许可，没有增加攻击、武器技或 Q 的反向取消权。
- 动作 0.40s、最多 185cm、462.5cm/s；输入归一化并在起招固定，无输入取 facing。核没有甲/攻速/移动/技能 CD 参数，不走普通移动倍率。
- 所有武器共用这个角色核的 `ReadyAt=Start+1.20`。受阻可以零位移，仍保留动作和 CD；没有提前起攻、退款或改方向接口。
- 直接接触无敌严格 `[Start+.06, Start+.20)`。无 epsilon 延长。真实区间外破韧可终止动作；死亡可以在任何阶段终止。中断立即裁掉余下闪避无敌，不改本次 CD。
- Focus、空攻预算、已有 DoT/状态和独立受伤无敌均不属于此核。核不提供净化、回血、补弹、额外受伤无敌或自由取消。

这些规则能独立计算，不代表外层合法上下文、复合取消、连续命中和实际状态已完成接线。

## 交付接口

文件：

- `F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonDodge.h`
- `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonDodgeStandalone.cpp`
- `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/RunDodge.ps1`

命名空间 `DungeonDodge`，`FDodgeKernel(OwnerId, InitialTime, InitialPosition)`。初始身份、时钟和位置是可信创建事实；无效构造不能开始/推进。只读 `State()` 返回当前绝对时间、位置、Idle/Dodging/Dead、全局 CD 和完整动作凭据。

| 方法 | 合同 |
| --- | --- |
| `TryStart(Now, FContext)` | Now 必须等于核当前时间；FreshPress/Grounded/CanStart 默认均 false，外层必须显式授权。成功才发 Started，提交固定方向、动作和 CD。失败原状态不变。 |
| `CommitResolvedIdlePosition(Now, Position, ReceiptId)` | bool 返回；Now 必须等于核当前时间，仅 Idle 存活，XY 坐标有限，ReceiptId 为专域持久严格递增新 ID。确认外层已合法解析的位置事实，保留 Time/ReadyAt/动作事件游标/历史无敌/死亡事实。失败不占 ID。 |
| `StepTo(Now, Sweep)` | 绝对时钟只能向前。活跃未受阻位移必须取得只读 sweep；已受阻、闲置、死亡或同刻无移动可省略。一次长步最多完成当前动作，不自动重复起招。 |
| `Interrupt(Now, PoiseBreak/Death)` | Now 必须等于当前核时间；外层只能在已解析真实破韧/死亡后调用。受保护的直接接触不能作为 PoiseBreak 提交。无其他理由/自由取消权限。死亡事实仅发一次。 |
| `IsDirectInvulnerableAt(HitTime)` | 精确半开查询，保留历史；活动动作未来的窗口是会被真实中断裁短的时间承诺。 |
| `DirectInvulnerabilityIntervals()` | 返回每动作的 `[Start, EndExclusive)`，早于+.06中断则不返回空区间；中断后重新读取才得到实际裁短结果。 |
| `Capture()/Restore(State)` | schema v2 完整状态，包含最后位置凭据、去重游标及每 dodge 起点凭据；同 Owner/可信创建事实。旧 schema v1 缺凭据显式拒绝，无隐式迁移。恢复合法活动动作不重发 Started，后续完成沿原事件游标继续；坏状态原子拒绝。允许同版本合法旧快照恢复供未来同批事务，未实现磁盘 IO。 |

事件只含成功产生的 Started、Blocked、Completed、Interrupted、Died；包含 OwnerId、ActionId、EventId、真实时间和当时位置。Died 为角色事实，ActionId=0；活动死亡另发该 dodge 的 Interrupted。重复 StepTo 不重复结束事件。

### 只读 sweep

请求包含 From/To、FromTime/ToTime、ActionId 和角色身体半尺寸 X18/Y16。外层返回 `Accepted`、HitWall/HitBody 及各自 `[0,1]` fraction；没有该碰撞时 fraction 必须为 1。选最早 fraction，同刻墙优先；命中 fraction=1 仍记录真实端点受阻。核只提交自己的 Position，不修改 UObject。死尸是否不阻挡、墙/身体几何和场景权威由外层负责。

移动按起点与绝对累计路程计算，避免逐帧相加漂移。遇阻记录实际接触时刻与累计路程，后续停移而不缩短 End。查询拒绝、缺查询、NaN/Inf、越界/矛盾 fraction、倒时均不改变时间/位置/CD/凭据，不返回半套事件。启用 C++ 异常的独立构建也拒绝抛异常的 query；UE 无异常模式要求 query 本身不抛异常，头文件已在该模式编译核验。

Restore 核对版本/身份、有限时刻/坐标、创建事实、连续 ActionId/EventId、单位方向、固定 End/ReadyAt、动作互斥与时间一致性、合法终止原因、受阻时间/路程/凭据、历史起点与位置连续性、死亡时间/事实及游标。v2 还核对起点位置凭据的动作 epoch/时刻/单调 ID/坐标，当前最后凭据与去重游标、活动/死亡状态的一致性。坐标/浮点路程重建允许数值误差检查；无敌边界始终原样严格比较，没有 epsilon。

### idle 已解析位置交接与保存域

外层先用实际动作/碰撞规则解析普通移动、跳跃落地或击退后的 XY，再在同一 SimulationTime 调用 `CommitResolvedIdlePosition`。核不会驱动 UObject、执行普通移动、改变 Grounded/Z、授权穿墙或授予免费传送。接纳只表示外层已解析位置成为核后续 dodge 的起点；外层必须保留其原有合法移动准入和 sweep。

- ID 域为 `actor-resolved-position-v1`，按当前 Run＋Owner 独立、单调、持久；与 dodge ActionId/EventId、武器/伤害/Focus 凭据分开。Run 身份由外层 D13 同批约束，核身份检查为 OwnerId 与可信创建事实。
- `NextPositionReceiptId` 初值 1，成功接受 `ReceiptId >= NextPositionReceiptId` 且 ID 不能为 uint64 最大值；允许预留跳号，成功后游标为 ID+1。低于游标的任何 ID 均拒绝。失败保留游标，调用方可重试同一未成功的新 ID。
- ID 分配器须同核/Actor XY/Run 同批保存；换甲、切武器、房间、暂停/继续不能清游标。恢复后不能用临时局部计数从 1 重来。合法旧快照恢复只有在整个权威批次一起回到同代时才安全。
- 当前 idle 提交只覆盖 `LastPositionReceipt {Id,AfterActionId,AtTime,Position}`，无每 tick 位置 vector；下一次 dodge 冻结当时起点 receipt。动作之间没有新提交则沿上次 dodge 的实际末位置开始。历史每 dodge 至多保留一个起点 receipt，用于恢复起点链条与 ID 顺序。
- 凭据提供去重和结构一致性校验；真实外层碰撞/落点解析仍需 Actor 集成实证，D13 负责完整代/内容完整性。所有字段协调伪造的状态不能仅靠一枚无签名内存 receipt 证明真实性。

## 实际 RED→GREEN 证据

MSVC 14.38.33130、Windows SDK 10.0.19041.0；`/std:c++17 /W4 /WX /EHsc`。脚本每次在 TEMP 新建时间戳目录，保留日志，不覆盖前次；finally 恢复调用前 INCLUDE/LIB。

| 阶段 | 实际结果 | 保存日志 |
| --- | --- | --- |
| 空实现有效 RED | compile 0，78 checks / 43 failures，进程 exit 1；空凭据后的破坏测试跳过 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-010246-900-RED/standalone.log` |
| 默认上下文拒绝 RED | compile 0，111 checks / 6 failures（默认错误接纳导致同组后续连带失败），exit 1 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-010752-459-RED/standalone.log` |
| 闲置死亡错误归属 RED | compile 0，113 checks / 1 failure，exit 1 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-010948-337-RED/standalone.log` |
| 最终 GREEN | compile 0，113 checks / 0 failures，exit 0；无宏 TU 为空、无异常头文件 compile 均通过 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-010958-071-GREEN/standalone.log` |
| 冻结复核 VERIFY | compile 0，113 checks / 0 failures，exit 0；宏与无异常两项仍通过 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-011152-946-VERIFY/standalone.log` |
| idle 位置交接 RED | compile 0，原113回归仍过，总164 checks / 28 failures，exit 1 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-013941-011-RED/standalone.log` |
| v2 位置交接 GREEN | compile 0，164 checks / 0 failures，exit 0；宏与无异常两项通过 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-014030-576-GREEN/standalone.log` |
| v2 冻结 VERIFY | compile 0，164 checks / 0 failures，exit 0；宏与无异常两项通过 | `C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-014250-395-VERIFY/standalone.log` |

测试整个翻译单元由 `DUNGEON_DODGE_STANDALONE` 包围；只有自己的 RunDodge.ps1 启用，UE/UBT 默认看不到 main 或测试静态对象。最初测试草稿曾因空记录索引越界退出，修复防护后的有效 RED 才计入以上证据，未将崩溃充作规则 RED。

覆盖：八向及无输入 facing、巨大有限输入归一化、同刻/分帧/长步、完整时长与 CD 边界、精确+.06/+.20与 nextafter、早期破韧不激活未来无敌、尾段破韧、窗口内死亡裁短、闲置死亡/重复死亡、X100/身体18+24→最大58cm、墙零位移/端点/双碰撞最早值、坏输入/坏 query 原子拒绝、活动/受阻/中断/死亡/多动作恢复、缺失/伪造凭据与状态一致性。

新增51项：已解析 XY 后从真实新起点闪避、CD内提交不退款、历史无敌保留、事件/动作游标不变、100次idle提交压缩为一枚最后凭据、严格单调/跳号/重复/较旧 ID、失败不占 ID、NaN/Inf/倒时/未来时间、活动 dodge/死亡拒绝、落点与真实破韧后击退提交、内存恢复后的去重、位置/凭据/时刻/epoch/游标矛盾与旧 schema 拒绝。这里验证外层位置事实的核交接，不声称已运行 UE 普通移动或跳跃。

解析 sweep 是本地几何夹具，不是 UE 碰撞验收；Focus/DoT 不在本核中，未伪造 Actor 资源不变的运行证据。

## 未来 Actor 接线前提与风险

1. 外层共同门必须排除空中、活动主攻/技能/Q、硬直、死亡和正在 dodge；只对成功核准入的复合请求取消未提交旧工作。若外层取消失败，须同批回滚核准入，不允许先取消再发现 CD 不好。输入 edge/每逻辑步一项/Shift 别名合并由输入层负责。
2. 已实现 `CommitResolvedIdlePosition`。未来 Actor 在非 dodge 时先解析真实合法 XY，再同刻提交专域凭据；活动 dodge 期间由核位置镜像到 Actor，保持唯一移动权威。Z/落地与移动权限仍由外层提供，不能每次重建核或伪改 Restore 刷 CD。Actor 接线及实际走路/落地/击退验证未实现。
3. 同一角色用一个长期核，不因武器/甲/房间/暂停更换而重建；时间与其他核使用同一 SimulationTime。先推进到实际接触时刻，再解析伤害/破韧/死亡；不能推进到慢帧尾再回填更早中断。
4. 旧独立受伤无敌与本核区间取并集。Driver 当前整批布尔伤害门不足以完成区间合同；需按实际接触时刻及有效窗剩余区间重求交，尤其 A2 首次接触落在无敌中而后续仍在攻击窗内的情况。收到实际中断必须重新冻结后续区间，不拿旧未来承诺当已发生保护。
5. 成功起招清指定轻甲 buff/站立计时、普通非破韧伤害继续动作、DoT 持续、未提交装填/换装归属原子保留均在 Actor/状态模块，尚未实现运行验收。
6. 当前保留完整动作历史，快照和每步校验/复制成本随次数增长；未来只可在世界消费游标与保存合同明确后安全压缩，不能擅删仍供历史接触/恢复使用的凭据。
7. D13 须与角色/动作/Focus/空攻/伤害区间/输入清理/世界消费游标同批保存。这里是内存 Capture/Restore，不是保存文件、跨房、故障恢复或实际游戏验收。

## 源码冻结 SHA-256

| 文件 | SHA-256 |
| --- | --- |
| DungeonDodge.h | `375EE1AA3D83612A3C686F0B1A6A6D322C97E247EA957C3D7380DCD431FD9EC2` |
| DungeonDodgeStandalone.cpp | `9E298F1CC126FF4A7B2B5685ED15EE3ED03B5E9E9531E4529AD72964422DBC7B` |
| RunDodge.ps1 | `BE18EB063F8EBB6B78FA2299B47502F484BB9B5255F46BA9F318B15BD1E44E01` |

所有本次编辑仅以上三个新文件与本报告；未改 Actor/GameMode/HUD/Driver、UE 测试、WeaponActions/Stats、Probe/capture 或总账。

v1 先前冻结头 SHA-256 `B937EF48E12DC2B5751819760EA7F876BEFC469F55DB6F655FBD11261F423379`，113项当时通过；该版本未含外层位置交接。本报告保留其 RED/GREEN 日志作为历史证据，当前 schema/源码以 v2 冻结为准。
