# Scene / Fog Owner Snapshot 独立只读审查 v001

日期：2026-10-16。审查者：clean_frame_review，非本实现作者。结论：Scene 的合法历史/交互状态、整候选拒绝后一次安装路径未发现阻塞；Fog 的正常形状/值/计数路径成立，但有一项**P2 浮点坐标轴退化反例，尚未关闭**。生产版本当时未实际编译/运行，本报告不宣称103 GREEN或Actor磁盘Continue。

仅新增此报告。没有改 Source/测试/脚本、素材、ledger或旧证据，没有UE/UBT。没有审查尚在写入的Equipment实现。

## 审查绑定与实际证据

已完整阅读新FState及Restore、SceneObjectsSnapshot及Restore、四个OwnerSnapshot tests，并只读查阅既有GM真实交互顺序、HUD探索入口与不可变DungeonRoomLayout。

首次读取时，root-production-v001/manifest.json的四份工作文件字节/hash均匹配：

| 文件 | SHA256 |
|---|---|
| DungeonExploration.h，4202B | ca742aa38234085a5c2bd85b143c7c6e616fdbc2fd922bb7ea80e3a8b9910021 |
| DungeonSceneObjects.cpp，7102B | 5c9924195f807a5ded79caedd13fbc284286f350ad8a8a6369e834d569fb3967 |
| DungeonSceneObjects.h，2110B | a6bc7a571889b5a6de29249779deada0391a08904c5c9f3f7faa7d88369ce9f4 |
| Tests/DungeonOwnerSnapshotTests.cpp，8903B | 786c96f63d37022a74561c4ff1247363deb6b9a638e73bbb77cbd8ce4a04ddbb |

实际Stage0报告FirstRoom-20261016-001102/index.json，SHA19dfb0abdf060805de0fbeea2bc77ca9e0804a6d5badd9dc1e65eaea4bc6c9dd，为0 Success/7 Fail/0 warnings/0 notRun，其中四项Scene/Fog测试均Fail。这证明既有空实现RED，不是本生产候选已经通过的证据。

本审查发出P2后，root已另行冻结fog-axis-counterexample-test-v001，并通知测试新SHA前缀b231e5；Fog生产仍ca742aa未修，等待真实CPP新7执行。**这份后来测试不与上表旧测试版本混称，也未在本报告冒称已经跑过。**

## Scene：合法状态与拒绝边界

SceneObjects.cpp82–85 Capture返回拥有值副本。Restore90–132先验证全部候选；133–135才构建Candidate并一次MoveTemp安装。所有返回false路径都在任何私有CurrentRoom/Rooms/Interaction写入之前，Diagnostic是外部诊断输出，清它不等于改变live owner。

- **Inactive owner：**Reset/默认对象的CurrentRoom.Active=false、无Run/Room/Object/历史、默认已知Layout、无活动Interaction均可恢复，不创建房间。Inactive且只有合法LastFailure观察值亦可保留；未知enum、非有限/负AtTime或活动残留被拒绝。
- **历史survey：**每个历史entry必须key==RoomInstanceId、Active、同Run、有不可变已知Layout和两个固定对象。survey只能count0/false或count1/true；exit不可携带survey事实。current必须存在于history且逐对象事实一致，避免加载current与较旧history拼接。MarkSurvey会同步当前历史，正常BeginRoom/返回历史房保留已消费事实。
- **Pending survey：**要求当前Room/Object对应未消费Survey，NeedsConfirmation=false、LastFailure=None；保留原AtTime，不在Restore中调查或触发奖励。既有GM的CommitSceneInteraction先CancelSceneInteraction清pending（397），然后MarkSurvey（400），所以拒绝“仍pending且surveyed=true”不会误挡合法提交后的状态。
- **Pending exit：**NeedsConfirmation=true确认前与false已确认/待语义提交都允许；不把后者当空闲，不自动确认或NextRoom。GM366会设置false并保留Pending、AtTime及bSceneCommitRequested；测试明确覆盖确认前/后两个owner值状态。
- **已取消/失败观察：**Pending=false时Kind/Room/Object/AtTime及NeedsConfirmation不得残留live intent，合法LastFailure可保留。GM Cancel及失败分支形成的状态相容。

KnownSceneLayout45–50对已知ID/version/Entry/Exit/Extent/Barrier有效性/Min/Max/Survey作全等检查；对象数量、顺序、kind、ID、Room、坐标与survey一致性亦验证。未知schema、Run/Room交叉引用、current/history不一致、非法对象和非有限布局坐标会在安装前被拒绝。本Owner不承担尚未提供的玩家位置、EquipmentRun或完整世界聚合交叉验证，不能凭这层验证宣称所有Run引用已闭合。

四组中的SceneHistoryAndPendingInteraction使用现有BeginRoom/MarkSurvey及public Interaction值构造合法owner状态，并检历史消费、pending survey、exit确认前后和正常回访；不是正常键盘输入或真实世界恢复录像。SceneCrossReferenceRejectionIsAtomic有有效控制、未知schema/Run/room/layout/object/enum/time坏例及inactive控制。其nonmutation断言只逐项比较部分Run/history计数/survey/confirmation字段，未递归全比所有对象/布局；本次全状态原子判断还有源码“所有验证完成后才安装”的支持，不能称测试已经逐字段证明了所有内容。

## Fog：正常候选与计数

FState拥有Schema、Bounds、RoomId、std::vector<double> Memory。Restore78–85先要求Schema1、RoomId>0，以Saved.Bounds重建Candidate网格，并检查非空、精确Memory大小及每个值finite且在[0,1]。完整复制Saved.Memory，不重新Reveal、不夹紧保存值、不使用墙钟；Explored计数从Value>0导出，再一次move安装。拒绝正常坏例时live bounds/room/memory/count均在安装前保持。

构造器38–47验证bounds有限且正尺寸、width/height有限、浮点转整数前的分配限额和总顶点限额；非64整倍的尾格仍由Max形成。四个tests中的Fog部分覆盖真实Reveal的逐double值、双线性查询及下一次Reveal等价、大小增减、非法值、未知schema/Room、NaN/退化/巨大宽度bounds，以及拒绝后Memory和派生count不变。

## P2：有限bounds仍可生成重复轴，Restore接受后插值退化

**位置：DungeonExploration.h27–30、37–47、58–65、78–85。**现有候选只看分配尺寸与保存值；没有验证重建后的X/YVertices严格递增。

具体候选：Schema1、RoomId9、Bounds={MinX=1e20,MaxX=1e20+16384,MinY=0,MaxY=64}，Memory514项，每项0.5。四个bound和width/height都是finite；XCells256、YCells1，总顶点257×2=514，远低于MaxVertices。该候选绕过目前的大小与有限值门。

本次只读普通Python以同一IEEE双精度算式Min+i*64核对：X轴257项中有255个相邻重复区间；最后两顶点同为MaxX。MemoryAt({MaxX,0})经Cell的右边界分支选最后cell，分子=0、分母=0。按源码常规double语义预期TX及插值为NaN，std::clamp不能把NaN修成合法[0,1]。**这是源码/普通double模型反例，尚未实际运行CPP或UE；真实接受/NaN须由root新测试确认。**

风险：损坏但每项“finite、形状正确”的保存候选可能安装一个无法合法插值的fog owner，违反恢复后仍是有限可查询网格的约定。当前实际±1350等小坐标不会触发它；这不使接受畸形外来bounds合理。原Bad.MaxX=1e100测试检测巨大宽度/分配限额，未覆盖巨大平移、小尺寸、分配很小的情形。

最小修正方向是在候选安装前要求每个轴相邻点严格递增且差值有效；可在构造器统一拒绝退化网格，使普通创建/Restore遵循同一门。拒绝而非夹紧坐标、重采样或改Saved.Memory。保留原始反例测试与live完整nonmutation断言，再由root实际新7复现RED和窄修后回归。本报告在root执行前保留此发现**未关闭**。

## Owner与Continue边界

Scene快照不含GM的bSceneCommitRequested、SceneEncounterEntityId、world actor、reward/route事实；Fog纯FState不含HUD的ExplorationOwner、run-restart/reset序号及相机状态。HUD UpdateRoomView236–245仍按owner/room/restart重新创建并Reveal。未来聚合必须保留相应事实/绑定、从已验证bounds重建而不意外重置记忆，并按既有Task3语义处理已确认exit的提交身份；这里没有接Actor/GM/HUD Restore或磁盘Continue。该缺失属于计划已列的聚合工作，本次不升级为额外owner缺陷。

未改变玩法、设计范围或正式完成数。此报告只评上表版本与四项owner测试，formal complete units仍0/15；后续实际生产结果应另留版本证据。
