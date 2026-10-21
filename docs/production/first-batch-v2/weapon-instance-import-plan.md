# 武器完整实例导入纯核计划

2026-10-15，Asia/Shanghai。根任务明确授予本子任务独占WeaponActions头、Standalone、对应Run脚本与本plan/report。保留此前148项行为覆盖，支持库存即将接入的合法实例转移；不修改Actor/GM/HUD/Probe/设计来源，不启UE/UBT。

已核实：`RegisterWeapon(Weapon,Id,Ammo)`固定从CD0出生，无法代表地面武器携带的绝对CD。通过修改任意Capture快照重建kernel会丢Focus、现行动作、已发事件与旧收据；不能作为获取接口。

选定API：`FImportResult ImportResolvedWeapon(double Now,const FInstance& Imported,uint64 ReceiptId)`。FInstance含Weapon、InstanceId、Ammo、ReservedAmmo、CooldownDeadline；完整导入只接受ReservedAmmo0、合法模板弹匣/绝对CD、新ID、Now恰等于核时钟，收据成功一次、同原请求幂等、失败不耗ID。导入仅注册，实际装备动作完成后由外层调用既有EquipCompleted；已注册ID不能覆盖，重拾同一已有实例应复用它。

1. 先加20条必要边界和可编译空桩，真实168/15 RED；schema期望从2显式更新3，其余原148断言保留。
2. 以独立注册来源账本记录初始/legacy/import出生事实和import收据。保持旧Focus账本、动作及事件游标，不重置任何角色预算。
3. 记录真实SkillLock、正弹耗Emission、ReloadCompleted的before/after事实，Capture/Restore从出生数据重放当前Ammo/CD；用既有Issued/Pending/当前动作反查已锁技能及弹耗凭据。
4. 实现后168/0；再加一个已知旧零弹耗技能换武器后删lock日志/清CD负例，169/1真实RED，最小补齐已知locked技能的lock凭据检查后169/0。
5. 冻结Source哈希并通知根构建；文档留完整真实日志。独立Temp夹具验证库存与动作核公开API组合，不改任何生产Source。

schema明确升到3，旧schema2拒绝，等待显式迁移；没有把历史字段默认值伪装成同一格式。只验证内存语义一致性，不实现D13磁盘同代、可信生成RNG、SHA规范请求、跨Actor来源消费或全部45把武器动作。当前动作核仍按原首批定义支持SWD/GSW/SPR/XBW/STF；库存可验证原45模板不代表动作/视觉内容齐备。


### 05:29整数弹仓资格修复

独立审查确认D13弹仓为非负整数；保留原169，新增10条真实179/8 RED→179/0 GREEN。统一约束Ammo、合法ReservedAmmo、immutable出生与运行Before/After，不对Focus或CD整数化。修复后当前头冻结并以独立联合10/0验证；详细指纹/日志见report。v012旧DLL属于修复前版本，不与当前Source混称。
