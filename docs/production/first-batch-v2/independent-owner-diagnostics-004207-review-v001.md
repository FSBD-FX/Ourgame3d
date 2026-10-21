# Owner 快照诊断实测独立复核 v001

审查日期：2026-10-16（Asia/Shanghai）。本报告仅新增审查记录；没有修改 Source、测试、脚本、ledger 或素材，没有启动 UE/UBT。此前两份独立报告保持冻结。这里核实当前 owner 局部恢复，不代表 Actor 聚合恢复、磁盘 Continue 或内容单元完成。

## 事实与版本

实际测试文件是 `UnrealGame/Source/CodexDungeon/Tests/DungeonOwnerSnapshotTests.cpp`，不是消息中曾写的 `DungeonRunOwnerSnapshotTests.cpp`。本次实读 SHA256 为 `48e2335d9b264a443ce21a7903663b99b73663777ff00660c670daad8245d955`，与 `evidence/run-owner-snapshot-v001/root-diagnostic-test-v003/manifest.json` 一致。该测试版本新增 case 标签、独立 object-position NaN 反例，以及 Fog 查询数值/位模式诊断；没有新增测试注册。

本次诊断对应的生产实现仍是：

| 文件 | SHA256 |
| --- | --- |
| DungeonExploration.h | ca742aa38234085a5c2bd85b143c7c6e616fdbc2fd922bb7ea80e3a8b9910021 |
| DungeonSceneObjects.cpp | 5c9924195f807a5ded79caedd13fbc284286f350ad8a8a6369e834d569fb3967 |
| DungeonSceneObjects.h | a6bc7a571889b5a6de29249779deada0391a08904c5c9f3f7faa7d88369ce9f4 |

我只读解析了真实 `UnrealGame/Saved/Automation/FirstRoom-20261016-004207/index.json`，SHA256 `d02c6a0f364f844c20c63a778c3d3ec76b26841dbd8cfefb96b121e25775b6ce`。结果是 4 成功、3 失败、0 warning、0 notRun、0 inProcess；不称全部通过。

| 组 | 实际结果 | 本次关键证据 |
| --- | --- | --- |
| EquipmentInvalidCandidateKeepsOwner | 成功 | 原拒绝候选组通过 |
| EquipmentPendingActionsAndDeepValues | 失败，2 errors | unrelated source registration 后，active 和 completed 两个合法快照都 Restore false |
| EquipmentRuntimeReceiptsCritAndCancellation | 成功 | 当前 receipt/crit/cancel 组通过 |
| ExplorationExactMemoryAndContinuation | 成功 | 正常记忆往返/继续控制通过 |
| ExplorationInvalidRestoreIsAtomic | 失败，4 errors | collapsed axis 被安装，恒定 .5 查询成 0，live 状态及派生 count 改变 |
| SceneCrossReferenceRejectionIsAtomic | 失败，4 errors | layout-survey-nan 和 object-position-nan 都 accepted=1，且没有拒绝诊断 |
| SceneHistoryAndPendingInteraction | 成功 | 正常历史/交互往返控制通过 |

## Scene：事实、推理、最小修复

事实：测试第 143 行只把当前 room 的 `Layout.Survey.X` 改为 quiet NaN；第 144 行另起 Before 副本，只把 `Objects[0].Position.X` 改为 quiet NaN。两者都保留正常 history，因此同时检验本地 layout/对象有效性与 current/history 一致性。真实报告分别记录 `layout-survey-nan accepted=1`、`object-position-nan accepted=1`。`interaction-time-nan accepted=0`，不能说所有 finite 检查失效。

源码路径：`DungeonSceneObjects.cpp:48–50` 的 KnownSceneLayout 依靠 `FVector2D ==` 检查 layout；第 61/64 行依靠 `Position != Layout` 检查对象坐标；第 75 行依靠 `Position !=` 检查 current/history。UE 5.5 本地 `Engine/Source/Runtime/Core/Public/Math/Vector2D.h:956–964` 的这两个运算符只是 `X==V.X && Y==V.Y` 与 `X!=V.X || Y!=V.Y`，没有 finite 门。对普通 IEEE 比较而言 NaN 应不等，但当前实际编译不能据此作恢复契约保证。

实际 `DungeonSceneObjects.cpp.obj.rsp:39` 包含 `/fp:fast`；该响应文件本次 SHA256 `1aea651a0443eb3035e195ea6664ef1f0caa0f8dfbefdd32bfc89014305c7393`。这支持优化语义是可疑机制，尚未做机器码或编译器最小反例归因，不能把它写成已经证明的唯一编译器根因。实际已证明的是 Equality 链没有阻止这两个坏候选安装。

建议最小生产改动：

1. 在 KnownSceneLayout 现有 immutable equality 之前，逐分量检查 Saved.Entry、Exit、ExitHalfExtent、Barrier.Min、Barrier.Max、Survey 的 X/Y 都有限；保留所有原 Id/Version/坐标/Barrier.bIsValid 等比较。
2. 在 ValidSceneRoom 每个 Object.Position 和布局相等比较之前，独立检查 Position.X/Y 有限。不能只校验 layout，因为 object NaN 是独立真实反例；不能只靠 history equality。
3. 使用本地 UE `FMath::IsFinite(double)`。已实读 `GenericPlatformMath.h:577–579`，它采用 BitCast 后的 IEEE exponent 位检查，避免仅把 NaN 保护寄托在浮点相等表达式上。可以在匿名 namespace 放一个局部二维 finite 谓词；不改变 public API，不引入新 schema、修复或替换数据。

覆盖关系：KnownSceneLayout 同时用于 inactive、current 和每个 history room；ValidSceneRoom 用于 current/history。将校验放这里可保护全部这些路径，而不是在最终安装前只抽查 current survey。现有所有验证仍应发生在 `*this=MoveTemp(Candidate)` 前；拒绝时给既有路径的非空 Diagnostic。

风险与测试边界：当前 Scene 原子断言只列举 Run/history 数量/survey count/interaction，并没有逐字段比较 layout 和 position，因此本次坏坐标被安装时这些选择性字段仍能保持真。真实 accepted=1 已足够确认缺口；不能用选定字段断言没有报错来证明 live 完全未变。后续最终复核应至少读到两 case accepted=0 与诊断非空，同时保留合法 pendingSurvey、两种 pendingExit 和历史 roundtrip。没有授权我增加测试或扩大本轮修复。

## Fog：事实、推理、最小修复

事实：测试第 64 行候选 bounds 为 `{1e20,1e20+16384.,0.,64.}`，Memory 为 514 个 `.5`。真实报告记录 `installed=1 query-finite=1 query=0 query-bits=0000000000000000`。恒定 .5 的查询已经错误；原子拒绝也失败，Explored count 从 18 变成 514。此次 C++/UE 实测没有输出 NaN，不能沿用先前 Python double 模型的 NaN 预测作为实际输出。

源码推理：构造器第 46 行通过 Axis 生成每 64 单位的顶点；在这个大原点，多个相邻值舍入到相同 double。Restore 第 80–82 行目前只确认候选 Memory 非空、形状相等、记忆值范围，并未确认实际生成轴严格递增。退化轴没有合法的双线性区间，无需等待查询变成 NaN 才拒绝。

建议在 Restore 生成 Candidate 后、现有非空/shape 门之后、任何 Candidate.Memory 赋值和 `*this` 安装之前，对 Candidate.XVertices 与 Candidate.YVertices 各自逐相邻点验证 `next > previous`。推荐用 `if (!(Axis[I] > Axis[I-1])) return false` 这样的拒绝表达，要求两个轴都成立。现有构造时 finite bounds、维度/分配上限和 Restore 的 memory finite/range 检查保留不动。

这是候选几何验证，不应 clamp、重采样、去重轴、修改保存 bounds、自动 Reveal，也不需要改变原正常构造/游戏流程来使坏数据被接受。Saved.Memory 只有在完整候选验证通过后赋值，Explored 仍从保存值重建。静态源码和本次实测共同支持这个窄修；最终是否真正关闭要等修复 SHA 绑定与同一真实反例通过。

## Equipment 与后续差异审查边界

两个新 Equipment 真实失败与已冻结独立报告的同一个历史 base/current execution base 混用问题一致。本轮我没有重审尚未冻结的 worker 修复，也没有建议篡改捕获的 PendingPlan.BaseRevision。active 和完成后保留原 plan 两个时刻都必须保持真实值通过；其余影响身份、版本、source、slot、drop 和来源一致性的原校验不能借修 rebase 放松。

目前结论是实际反证已定位，生产修复尚待冻结与实测。下一份最终差异审查应绑定新的 Source/test hashes、旧/新小 diff、实际同组报告与旧合法控制；不能将本文件当修复通过证明。也不能据此声称已完成跨 Pawn/Time/Focus/HUD 聚合恢复、磁盘保存/Continue 或玩家可见运行验收。
