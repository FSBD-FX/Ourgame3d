# Equipment Owner Snapshot 独立只读审查 v001

日期：2026-10-16。审查者：clean_frame_review，非实现作者。结论：私有状态的深值捕获、候选隔离、来源bijection、镜像与crit域核对路径整体成立；发现一项**当前GM公开流程可达的合法状态误拒，P2尚未关闭**：无关来源注册抬高库存Revision后，active和completed旧PendingPlan的BaseRevision不能再要求全等。

仅新增本报告。未改Source、测试、脚本、素材、ledger或旧证据，未UE/UBT。范围仅schema1当前bound适配器，没有用未来天赋/路线假设提出阻塞。

## 版本与实际证据

完整阅读Runtime.h/.cpp、三组EquipmentSnapshot tests、作者self-review及当前GM/Fighter/纯Inventory相关公开流程。生产绑定为evidence/bound-run-owner-snapshot-v001/equipment/production-v001：

| 文件 | SHA256 |
|---|---|
| DungeonEquipmentRuntime.h，5215B | 36f01b68e26404a599c76df6ac7726a45f275403bf9c820a0338b8a66e95a88c |
| DungeonEquipmentRuntime.cpp，19415B | 8aaf84ab003c02b7a2ef10e9f100e50e236858c8384ee1f47b858c06b544f93d |
| 原三组tests，24915B | 538f0b14ae0707f6b0f3c2dcb6e801e66d0f2ef043ca3c9fa55133db787b6b2a |

上述生产h/cpp当前与frozen副本相同；原测试在production-v001/frozen/Tests中保留。Stage0实际001102为0/7RED，报告SHA19dfb0abdf060805de0fbeea2bc77ca9e0804a6d5badd9dc1e65eaea4bc6c9dd，不是生产通过证据。

root通知实际002604发生harness crash、没有index.json：UE TArray禁止B.Sources.Add(B.Sources[0])自元素Add。只读diff确认后续测试SHA36ce6d890ae53005d2df26c53f4b65129dcc526f5042c6b21436c9f53efeda48只把该语句改为先const局部copy再Add，原断言未变。这是重复来源坏例的harness窄修，不是放宽候选验证。不能把该次crash称设备三组通过，或称Fog CPP反例已复现。本报告写成时没有完整生产GREEN。

## 深值捕获与整候选安装

Runtime私有事实为View、Sources、Inventory、PendingPlan、PendingDropPosition、PendingHasDrop、CritReceipts，Capture70–75全部包含。FString/TArray、纯Inventory的std::vector/string及嵌套affix/quantile/history是拥有值副本，未把Pawn指针或临时引用伪装成状态。

Restore82先拒绝未知schema/unbound/无inventory；97–103建立独立Candidate并通过纯Inventory::Restore验证完整初始item、版本/revision重放、位置唯一性、来源/operation/runtime receipts。直到241–243才写当前owner的七组字段；所有可能false分支都在此之前。候选的RefreshView/Prepare/Resolve没有改live，也没有调用Crit Observe/Peek或推进cursor。

三组tests的独立fieldwise Signature19–93覆盖外部View每个字段、所有counter、stats、sources、完整纯inventory、计划/drop和crit receipts，避免结构padding；RoundTrip与非法候选nonmutation使用全字段签名，比只比ammo/slot更完整。真实测试夹具通过普通GM交互/明确模拟tick/真实伤害及weapon action取得状态，没有通过friend写入私有Runtime事实来制造通过。

## 已核对的本owner规则

- **Scope与内容：**bound RunGuid/RunAlias/Owner/Room及纯inventory身份一致；Config、failure enum、当前9项开发catalog、非零counter均有门。schema1明确仅安装bound owner，unbound capture不能作为清空当前bound owner的命令。
- **Source bijection：**外部数量与纯source集合相同，逐项匹配ID/instance/version/availability、current item/affix/runtime字段，且拒绝重复SourceId与同room逻辑key；count相等+每项存在+外部唯一性构成双向覆盖。room非零且不来自未来，坐标满足当前实际房间范围。
- **镜像：**在独立Candidate.RefreshView后比Revision/ActiveSlot/receipt和三个slot全字段，stats用当前适配器实际默认FContext与保存的Stats.CurrentHP重新Resolve比较。没有把Pawn当前HP当owner镜像，合法伤害后Pawn95/旧Stats100的取消态可保留；不据未来context工作增加本范围要求。
- **Counter/history：**现有GM成功operation顺序、非alias Instance/Source cursor、纯runtime receipt下一ID都有约束。Import/Focus只有本owner的非零游标，相关WA/Focus历史不在此owner，完整跨域关系留给aggregate，未伪称已验证。
- **Selection/action/drop：**选择层绑定仍可选择的source/kind/slot；active action绑定当前selected/settled/current-room source、ID、时长、计划及replacement；切武器不可生成source/drop。无动作初始化与已接受动作的inactive residue分开，取消保留未花operation和旧plan/drop，完成保留已提交plan，不强制清空它们。旧drop坐标即使PendingHasDrop=false仍可能由实际switch路径保留，当前实现未错误要求此时归零。
- **Crit：**所有已耗draw有逐条receipt，seed/draw/bits/百分比/outcome/time及同域action/event单调唯一性核对；melee与weapon-action的ActionId1可各自存在，不能合并。ResolvedOwnerCritBits只是纯核验，不调用活跃RNG、重抽或增加NextCritDraw。

## P2：无关注册导致合法active/completed计划BaseRevision误拒

**直接位置：Runtime.cpp23–26的SameOwnerPlan，204–205的active比较、218–219的completed比较。**

当前真实流程允许如下操作：

1. BeginEquipmentRun获得Inventory revision1；正常RegisterEquipmentSource(XBW)生成revision2。
2. 正常E启动该source拾取，PendingPlan.BaseRevision=2，A.Active=true，原deadline不变。
3. 中途经同一个公开RegisterEquipmentSource注册无关ARM或另一武器。GM431–459没有Action.Active拒绝，该操作合法升Inventory/View.Revision到3，保留原PendingPlan及预留identity。
4. 立刻Capture。Restore重新PreparePickup得到BaseRevision3；SameOwnerPlan还比较BaseRevision，所以204–205拒绝原始Base2。其余instance/source/version/replaced/slot没有改变。
5. 原GM继续到deadline时，CommitEquipmentAction675–678重新Prepare，但只比较受影响的instance/version/sourceVersion/replaced/slot，不比较旧BaseRevision；684以新Prepared.Plan Base3提交，因此普通动作可以成功。
6. GM721仅把Action.Active设false，未更新R.PendingPlan，仍Base2；Operation.Request由684/纯Inventory.Commit222记录为Base3。完成后Capture再Restore，218对两plan全等也拒绝。因此不能只修active分支。

上述是当前源码与公开API的路径证明，未由本审查者运行UE；root已收到建议补真实countercase。它不是未来掉落系统的假设，也不是要求容忍实例版本/预留槽实际改变的过期计划。无关来源注册只改变全局库存revision，GM现有提交逻辑已经按受影响事实重新确认，不应将该合法基线当损坏snapshot。

建议在原三组内使用独立真实GM夹具：正常拾取中点注册另一source后，对active capture做完整RoundTrip；原GM推进原deadline证明动作完成，再对completed residue完整RoundTrip，保留旧PendingPlan.BaseRevision及drop等所有原字段。新增反例先实际RED、保全源及结果，再窄修。不得把snapshot计划改写为当前revision来使其“通过”。

修正方向是区分“原接受计划的历史base”和“当前/最终Prepare的执行base”：保留有效旧base关系、source创建时序以及受影响identity/version/slot/replacement等既有门，让active和completed两路径与当前GM提交语义一致；future-base或真正改变预留事实的坏例仍拒绝。原三组没有在动作中点注册无关来源，因此原测试即使之后通过也不能自动关闭此反例。

## 接收边界与当前状态

本次没有追加其他假想阻塞。设备owner不包含Pawn/Combat/WA完整状态、捕获模拟时刻、Focus/Import完整receipt域、drop实际重建碰撞和reward/route根事实；这些正是已有aggregate任务。这里的候选验证与深值捕获不构成磁盘Continue，也不会实例化Actor或补做交易。

P2在此版本保持未关闭；root/作者后续授权的测试与修复应另版绑定，不覆盖本报告与原production-v001。正式完整内容单元仍0/15。
