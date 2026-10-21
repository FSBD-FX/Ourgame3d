# 设备库存纯核实施计划

2026-10-15。范围为D04首个设备闭环；只读来源：`inventory-v1/inventory-rules.json`、`01-交互流程与界面状态.md`、`02-边界案例.md`，D13 `transactions-and-rng.json`、`state-schema.json` 及 `first-batch-v1/content-contract.json` 的 DEV 覆盖。先沿现有独立套件模式实现，不修改 Actor、GameMode、HUD、Driver、Probe 或旧纯核。

1. 固定 owning 数据与事务接口，写关键行为测试和可编译空桩，保留真实 RED。
2. 实现2武器/1甲、当前/备用、稳定实例/地面来源身份。地面来源保留 tombstone，成功操作保留 OperationID 与完整请求/结果；失败不消费身份。
3. Prepare 只返回源/实例/库存版本绑定意图；取消不改权威。Commit 重验同一计划、外层准入与旧物落点，复制候选一次提交；空武器槽拾取激活，满槽要求显式目标，替换备用不激活；手动禁止丢最后武器，免费换入新武器可行。
4. 实例拥有 std::string 与附魔幅度/原q；同步调用时临时构造 Stats 视图并立刻 Validate/Resolve，禁止长期存 string_view。保留实例弹药/CD数据，Q仅切 active、不重建实例。
5. Capture/Restore 校验身份、槽/来源互斥唯一归属、有效属性、版本、来源去重和成功操作记录；用独立 GREEN 验证并写实际日志/指纹。

固定 API：命名空间 `DungeonEquipmentInventory`，`FItem`/`FStoredAffix` 拥有字符串，`FState` 是 owning 内存快照；`FEquipmentInventory(RunId,OwnerId,Starter)`；`RegisterWorldSource`、`PreparePickup(SourceId,Slot=-1)`、`PrepareSwitch()`、`PrepareDrop(Slot)`、`Cancel(Plan)`、`Commit(OperationId,Plan,Context,DropSourceId=0)`、`ResolveStats(Context,ActualHP)`、`Capture/Restore`、只读 `State()`。槽0/1为武器、槽2为甲。外层必须给真实已完成动作/距离/LOS/安全准入，若有旧物还须真实合法落点；bool默认拒绝。

实例ID、SourceID、OperationID是独立Run域稳定uint64，由caller持久分配；本核不使用地址/GetUniqueID、随机或隐式生成。无成功提交的ID可用于纠错重试。Registry始终保留已注册实例，只有装备槽或一个可用地面来源拥有当前实例。

边界：不生成掉落RNG，不改变原45模板池、DEV概率/报价/20金币，不实现快捷物/遗物/钱包，不拥有HP/Focus或动作时钟；实例弹药/CD是外层导入的传递数据，实际射击/装填和资源预算权威仍属于动作核。v2通过合法resolved运行态收据同步这些结果，不重算动作资源。真实接线时须先同批同步动作核最新实例数据再转移，不能拿旧库存快照覆盖战斗结果。D13完整磁盘同代、外层HP截断与输入/时序后续接线，纯核通过不算获取内容已实跑。


## 2026-10-15 运行态桥 v2

获根任务明确授权后，新增 `CommitResolvedWeaponRuntime(Now,InstanceId,ExpectedVersion,Ammo,SkillCooldownDeadline,ReceiptId)`。它只接受当前拥有的武器实例，有限合法弹药、非回退绝对CD、正确实例版本与单调收据ID。失败不改状态或占用ID；同ID同原请求重放原结果，同ID不同请求拒绝。Now是调用者已核实的共同游戏时钟观测，不由库存积分；不能拿它代替WeaponActions的精确时钟检查。CD在观测时已过期合法，保留其绝对值，不清零或刷新。

1. 先新增24个关键行为边界、可编译空桩，69检查/21失败真实RED；实现后69/0。
2. 再自审新增历史运行态结果ActiveSlot的1条独立负例，70/1真实RED，最小补齐历史槽状态校验后70/0。
3. schema显式升到2，旧schema1拒绝，等待外层明确迁移；增加冻结InitialStarter、来源CreatedRevision、运行态before/after及结果日志。按Revision重放来源出生、装备操作和运行态转移，当前registry不能通过合法范围的raw编辑伪造更新。
4. immutable `SpawnItem` 继续用于原来源回调去重；其后拥有时合法变化通过运行态receipt记录。新的落地来源保存落地当刻最新实例完整快照。当前可用地面来源与registry必须完全一致；已消费历史来源允许与当前runtime不同，但内容定义/词条身份不变。

武器动作核的完整导入另见 [weapon-instance-import-plan.md](weapon-instance-import-plan.md)。本阶段只准备纯接口：在同一角色批次复制正常kernel对象作为候选，调用公开方法验证/提交，全部通过才安装两候选；禁止改Capture字段再Restore以绕过合法API。动作完成、范围/LOS、安全准入、实际来源消费和跨模块同代发布仍属于外层接入工作。


### 05:29独立审查修复

D13要求整数弹仓。新增7条回归，77/6 RED→77/0 GREEN；当前Item、来源出生、runtime Before/After统一整数校验，失败不消ID。WeaponActions完整导入及资源记录同步补整数计数，179/8→179/0；ReservedFocus10.05/Focus89.95仍合法。Source05:29再次冻结，v012旧DLL证据仍对应修复前旧头；后续真实Actor接线必须使用新的冻结头构建。
