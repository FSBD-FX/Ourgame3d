# Stage0 fixture correction v001 — explicit armor destination

事实：Root `build-editor-20261016-190617.log` exit0；实际 `FirstRoom-20261016-190734/index.json` 是0 Success／3 Fail／10 errors／0 warnings，其中9个诚实 stub 正控失败，另1个 Transactions 第112行 MED 替换前提失败。原报告和原 Stage0 候选完全保留，不称三组纯 stub RED。

源码依据：`DungeonEquipmentInventory.h:173` 对已有 Armor 的 `PreparePickup(SourceId,-1)` 明确返回 SelectionRequired。`DungeonGameMode.cpp:950–954` 会设置 NeedsSlotSelection／SelectionSlot2，要求 `ConfirmEquipmentSlot(2,true)`。本新测试 helper 第43–46行看见 NeedsSlotSelection 后，在调用参数仍为默认 Slot=-1 时直接返回 false。此前实际 LGT 已提交的断言通过，故 MED 正是已有甲替换；无需增加 neutral tick，也不能跳过公开确认。

最窄修正：只把 MED 替换和后续旧 LGT 重拾的两个 `StartActualPickup` 调用补显式 Slot2。后者在 MED 已装备时也会遇到同一正常选择要求，因此一并修复同一原因。helper、生产 stub、所有期望、原始截止时间、装备／RNG写路径完全不改。通过现有公开 SelectEquipmentSource→TryInteractEquipment→ConfirmEquipmentSlot(2,true) 完成真实正常事务，绝不私写 NeedsSlotSelection 或 Armor。

候选只在本目录；`before/` 保留原 test，`candidate-source/Tests/` 是修正 test，`patch/` 是2行 diff。Root 只准入该 test 后重新编译／执行原3个注册，再以实际结果决定是否获得干净 semantic RED。当前修正没有执行或宣称通过，HUD／Presentation补丁继续后置。测试注册/filter保持不变。
