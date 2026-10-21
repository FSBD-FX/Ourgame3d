# 跨房玩家身份与角色快照实测 v001

2026-10-16，Asia/Shanghai。完整目标仍active、0/15；本页仅覆盖快照的跨房绑定纠错，整局聚合、payload、暂停安装与磁盘Continue尚未接通。

事实：原默认111项通过，但新增的真实跨房测试先在 `FirstRoom-20261016-031105/index.json` 得到111成功、1失败、零警告/未运行。正常开始场景、移动和J击杀首房石骑、领取结果，再E/Enter进入第二房后，玩家与新石骑的默认Capture都被错误拒绝。首房二者的Capture与独立staging Restore正例均通过。失败版本已冻结v071，未改写玩家出生绑定、旧敌人墓碑、房清状态或HP来制造换房。

推理与修复：同一Run的玩家稳定身份保留出生房，当前敌人身份属于当前房。Fighter校验只移除玩家出生房必须等于当前房的两个限制，仍拒绝空/未来房、重复ID、错误content/team/kernel/owner及allocator冲突；非玩家自身binding仍强制当前房。新增测试同时核对未来玩家房、错误玩家content及旧房当前敌人被原子拒绝，失败不改变已安装owner或原生发射口。旧111项测试源码和名称均保留。

实际验证：`build-editor-20261016-031531.log`退出0；显式完整 `FirstRoom-20261016-031713/index.json` 和更新默认112后的 `FirstRoom-20261016-031901/index.json` 均112个唯一Success、零警告/失败/未运行。冻结 `source-assets/production/backups/2026-10-16_cross-room-owner-default112GREEN-v072`，1089文件、73,394,914字节；源与冻结两端2178项SHA/大小复核零差。当前DLL SHA256为 `9313b52ba350a28775f61433579a78585d192c1a7a33b1df966d64f46ab5b596`，默认测试脚本为 `7ff916fb2b7ea44ed3389a7d8a2fbde2c04193f36c000f2270c3c40ebd98fb48`。

风险与边界：这是首房到第二房的实际owner保存/独立恢复检查，不是GameMode整局安装或新进程Continue。剩余聚合字段与事务恢复合同见 `run-aggregate-contract-v001.md`；其独立冻结的actualRED补充和修复diff位于本目录 `evidence/run-aggregate-contract-v001/cross-room-production-v001/`。后续必须保留历史绑定，不能通过重建Run或重置奖励/RNG来回避真实恢复。

独立最终审查：`independent-cross-room-owner-review-v001.md`，SHA `bfd962e949de1646fab0255d06c11d06255f149a5c70f48a94148b33ae3c67c5`；独立2178端点复核零差，root已读并核SHA。owner范围没有新增阻断，完整聚合/Continue不在本次结论内。
