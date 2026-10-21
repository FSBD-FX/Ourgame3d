# 三项 owner 快照窄修最终独立复核 v001

日期：2026-10-16（Asia/Shanghai）。结论：在本轮局部 owner 快照范围内，没有发现三个冻结生产差异的新阻塞问题；真实旧反例由 RED 转为 GREEN，原 96 个测试名称全部保留，完整 103/103 无错误、警告或未运行。此前审查与诊断报告不覆盖。本审查只读源码/报告/冻结文件，没有启动 UE/UBT，没有改 Source、测试、脚本或 ledger。

## 差异与契约

### Scene 坐标有限性

`DungeonSceneObjects.cpp` 从原 `5c9924195f807a5ded79caedd13fbc284286f350ad8a8a6369e834d569fb3967` 到最终 `f4e552634988a04ff14e1a846396c64b5081657fb7e3f21085d7678f4a124956`。独立逐行 diff 只有匿名 namespace 的二维 finite helper、KnownSceneLayout 的全部六个布局向量 finite 门，以及 ValidSceneRoom 每个 object.Position 的独立 finite 门。

第 45–47 行使用 FMath::IsFinite 检查每个 double。第 51–53 行覆盖 Entry、Exit、ExitHalfExtent、Barrier.Min/Max、Survey；第 65–66 行覆盖对象坐标。原 schema、精确 immutable layout、Run/history cross-reference、object identity/count、survey 消费次数、pendingSurvey 与确认前后 pendingExit 规则全部保留。inactive/current/history 都沿原入口覆盖；最终整份 Candidate 安装顺序没有移动。没有通过换成容差相等或修补坏坐标让候选通过。

原真实诊断 `004207` 两个 NaN case accepted=1；最终 `004750` 中 `layout-survey-nan`、`object-position-nan` 均 accepted=0，诊断非空的断言通过。交互时间 NaN 仍拒绝，合法历史/交互往返组仍成功。原 Scene 原子测试字段覆盖边界仍按旧报告记录，不将其描述成新增的完整逐字段签名证明。

### Fog 严格递增轴

`DungeonExploration.h` 从原 `ca742aa38234085a5c2bd85b143c7c6e616fdbc2fd922bb7ea80e3a8b9910021` 到最终 `798849e7bb4b410a9d635719b4c764452b83fd2b17e8983e9848420f678e451e`。唯一新增代码是 Restore 第 82–87 行：在 Candidate 构造及非空/shape 门后，对 X/Y 两轴各自要求每个后点严格大于前点。Saved.Memory 赋值、Explored 重建与 live 安装仍在全部验证后。

没有改变正常构造、grid、MemoryAt、Reveal、保存 bounds/schema/数据，也没有去重、clamp、重采样或自动 Reveal。`!(next>previous)` 拒绝重复或逆序间距，位置与本轮真实退化轴反例对应。

原 `004207` 事实是 installed=1、query-finite=1、query=0、bits 全零，恒 .5 被错误插值成 0；不是实测 NaN。最终 `004750` 为 installed=0，坏候选拒绝及 complete memory/bounds/room/derived count 不变断言通过。其后的 query0 来自独立 Probe 未安装坏候选后的原 bounds 外查询，不应读成恢复后仍错插值。正常精确往返/继续 Reveal 组保持通过。

### Equipment 合法注册 rebase

`DungeonEquipmentRuntime.cpp` 从原 `8aaf84ab003c02b7a2ef10e9f100e50e236858c8384ee1f47b858c06b544f93d` 到最终 `0ecc77892bdb13d9d8ed1c10bf74f77de6342cd7a86d46ed2216d2b456379a43`。只读对照冻结 patch `production-rebase-fix-v002/authorized-two-rebase-gates.patch`：新增一个注册区间证明 helper，用于 active 和 committed 两个原来过度比较 BaseRevision 的入口；其他运行方法不变。

第 28–39 行先要求 Original.BaseRevision 不大于 Reprepared.BaseRevision，Action/Slot/SourceId/SourceVersion/InstanceId/InstanceVersion/ReplacedId 全部精确相同；原第 189 行仍要求保存 base 非零且不超库存 revision，原历史 source 创建时刻门仍保留。

Helper 拒绝 `(originalBase,repreparedBase]` 区间内任何 Operation.Result.Revision，也拒绝 `[originalBase,repreparedBase)` 区间内任何 RuntimeUpdate.BaseRevision（该更新产生 revision=base+1）。两个区间端点对应真实 revision 语义。已由 Inventory::Restore 的完整逐 revision replay 先验证过，故剩余中间变化只能是新来源注册，不是任意跳过 stale 保护。完成操作自己的 Result.Revision=repreparedBase+1 位于区间外；完成之后的正常新注册/receipt 也不被错误追溯成准备阶段变化。

Active 第 218 行与 committed 第 232 行共享这个门。没有把原 PendingPlan.BaseRevision 改成新 base；末尾安装仍照保存值复制完整 owner。None action 仍使用原完整相等，affected facts、drop、source、mirror、cursor、crit 与库存 replay 的既有校验没有删除。

真实反例保留为独立 fixture：公开 GM pickup 中点原 base2；注册无关 armor 后库存 rev3、同 ActionId/deadline；active Capture 保留 base2；原 GM 在原 deadline 正常 commit，操作 Request.Base3/Result.Rev4，而完成 Capture 仍保留旧 PendingPlan.Base2。`004207` 两个 Restore 均 false，最终同一测试文件两个时刻的精确 RoundTrip 均通过。没有伪造或规范化输入以适应旧 Restore。

## 测试与冻结证据独立核实

本次直接解析真实报告，而非仅采信 root 的 audit 摘要：

| 证据 | SHA256 | 独立读取结果 |
| --- | --- | --- |
| 原全 96：FirstRoom-20261015-233446/index.json | a0c7c1b26abb991a50b3e7d818bbcc8652cf29208f75e714f2ae976d7db61d3f | 名称基线 96 |
| 新反例 RED：FirstRoom-20261016-004207/index.json | d02c6a0f364f844c20c63a778c3d3ec76b26841dbd8cfefb96b121e25775b6ce | 4/7 成功，三组失败，原因与上述一致 |
| 最终 GREEN：FirstRoom-20261016-004750/index.json | f1b31b03e4a1a79e745c0ceec5979bf00cd44ebe1e9e935de491ad623bf6d689 | 103 成功，0 failed/notRun/inProcess/succeededWithWarnings；逐组 errors/warnings 总计均 0 |

完整名称集合恰好 103 个唯一名称。原 96 名称缺失集合为空；新增集合恰好是 RunOwnerSnapshot 下 EquipmentInvalidCandidateKeepsOwner、EquipmentPendingActionsAndDeepValues、EquipmentRuntimeReceiptsCritAndCancellation、ExplorationExactMemoryAndContinuation、ExplorationInvalidRestoreIsAtomic、SceneCrossReferenceRejectionIsAtomic、SceneHistoryAndPendingInteraction 七项，没有以换名隐藏旧失败。

测试绑定：EquipmentSnapshotTests 最终 `846735a378ef625845dd3ce9dee06ec0450ea55b620eb698011cbde47a01ce7c`；OwnerSnapshotTests 最终 `48e2335d9b264a443ce21a7903663b99b73663777ff00660c670daad8245d955`。最终生产修复没有改变实际 004207 使用的这两份测试。我另对比原 Equipment `538f0b14…`：只新增独立 rebase fixture 和此前已授权的 TArray Duplicate 局部拷贝后 Add；原断言、原 fixture 的 ID/counter 和三个注册均保留。002604 harness crash 依旧单独留档，不被追认成测试通过或 Fog 反证。

`tools/scripts/test-first-room.ps1` 与 v059 逐字对照只有默认 ExpectedTests 从 96 到 103，SHA256 `7828da987221616886b7abeb8049997a13ca1635e0c83e62e411f1584fcb934d`。原失败/notRun/expected 数量门没有改。根记录为实际 full103 后更新默认值；本审没有运行该脚本。

我另行遍历 v060 的全部 manifest 行，分别读取冻结副本和当前 live 的字节数/SHA：1080 files、72,842,142 B，两个方向均 0 mismatch。快照目录 `source-assets/production/backups/2026-10-16_run-owner-three-fixes-actual103GREEN-v060`；manifest SHA256 `0d6ed56663d7f5b2ad34e06d5f45611b2be67413ee0cf34371f542e22e2d70e8`。不是只抽取三条 Source 检查。

关键额外绑定：Runtime.h 未变，`36f01b68e26404a599c76df6ac7726a45f275403bf9c820a0338b8a66e95a88c`；Scene.h 未变，`a6bc7a571889b5a6de29249779deada0391a08904c5c9f3f7faa7d88369ce9f4`；当前/冻结 DLL 都为 `b5b2e72b3261244a52968c1f324176205940fd522ebd8512b035a271def708e2`。实际 build-editor-20261016-004654.log SHA256 `2494510d6f822adbd9f0d740290ec8ec44788762e63e92f117b4c0c40c627c45`，可读到编译、链接及 metadata 完成。root 执行 UE/UBT并报告 build exit0；我只读这些结果。

## 结论边界

此前两个局部报告中的 Fog 退化轴、Equipment 合法中途注册误拒，加上本次实测定位的 Scene 非有限坐标遗漏，在上述冻结代码与真实测试范围内已关闭。没有新增泛化的安全或未来玩法审计范围。这里仍不证明跨 Pawn/Time/Focus/HUD 等完整 Run aggregate、Actor 安装恢复、磁盘保存/Continue、真实试玩画面或新步态通过；正式完整内容单元仍 0。
