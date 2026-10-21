# Dodge v2 独立只读审查

日期：2026-10-15，Asia/Shanghai。审查者：stats_review。结论：当前冻结版本未发现高置信度、可复现的正确性缺陷。既有独立套件164项与新增审查夹具11项均通过。此结论只覆盖纯核及内存状态合同，不代表 Actor、输入、实际碰撞或伤害流程已经接入。

## 依据与范围

审查 `DungeonDodge.h`、`Tests/DungeonDodgeStandalone.cpp`、`Tests/RunDodge.ps1` 及 [dodge-kernel-report.md](dodge-kernel-report.md)。核对 D02 `docs/design/player-combat-v1/player-combat-rules.json:23–26` 的固定动作/距离、半开无敌、角色共享冷却、受阻不退款及中断规则。

仅新增本审查文档；未修改源码、其他 agent 文件或设计来源，未构建/运行 UE、UBT，未生成图像或调用生成 API。

## 事实与审查判断

| 重点 | 已确认的实现与判断 |
| --- | --- |
| 无敌时间边界 | `DungeonDodge.h:58–60` 使用 `>= Start+.06` 与 `< EndExclusive`，不以 epsilon 扩窗。完成后保留历史区间；真实中断将结束点截到中断时刻。原测试检查 `.06/.20` 与各自 `nextafter`，审查夹具另检查非零起点17.123。 |
| 碰撞截断 | `:157–164` 取墙/身体最早 fraction，同刻墙优先；记录真实接触时间与路程，保留原 `End` 和 `ReadyAt`。零位移和端点碰撞不会缩短动作或退款；碰撞后不再调用移动 sweep 也可等到原结束时刻。 |
| 位置交接准入 | `:133–136` 只在存活 Idle、同一核时间、有限 XY 和新收据 ID 时接纳。成功只更新位置、最后收据及其专域游标；`Time/ReadyAt/NextActionId/NextEventId` 与历史记录不改。失败原子拒绝且不消耗 ID。 |
| 收据去重 | 允许预留跳号，但要求 ID 不小于持久游标，成功推进到 `ID+1`；最大uint64拒绝，防溢出。重复/较旧 ID 在恢复后仍拒绝。下一次动作冻结相应起点收据；无新交接的后续动作沿上次末位置开始，不重复消费旧收据。 |
| 恢复一致性 | `:68–114` 逐项核对可信创建事实、动作/事件游标、动作时轴、位移/碰撞、起点收据 epoch/时间/顺序、最后收据与位置、死亡事实。schema v1 不具备位置凭据，显式拒绝。活动恢复不重发起招。 |

原164项测试使用硬编码规则边界和解析 sweep 夹具，并用完整状态比较检查拒绝不变性；不是只比较生产函数返回给自身的值。它们没有运行真实墙体或运动敌人碰撞。

新增11项审查夹具从非零时刻17.123和非零 XY 创建核，依次执行：起点交接ID7、严格半开边界、fraction=.25受阻、保持原动作/CD结束、CD内交接ID8、恢复/重复ID拒绝、第二次动作使用新起点、第三次无新交接及再次恢复。全部通过；未将该临时夹具加入作者源文件或原164项计数。

## 实际验证

执行命令：

```powershell
& 'F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\RunDodge.ps1' -Phase VERIFY
```

实际日志：

```text
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
NO_EXCEPTIONS_HEADER_COMPILE=true
COMPILE_EXIT=0
CHECKS=164 FAILURES=0
EXIT_CODE=0
```

原日志：`C:/Users/22499/AppData/Local/Temp/OurgameDodge/20261015-020102-455-VERIFY/standalone.log`，SHA256 `6fbe9139add82b057b9c4be912cf66e616735dd1e3f509d1c87ca0ffd4bf5b88`。

审查夹具以 `/EHsc /utf-8 /std:c++17 /W4 /WX` 独立编译，实际 `CHECKS=11 FAILURES=0`、运行退出0。源和结果：`C:/Users/22499/AppData/Local/Temp/OurgameDodgeReview/20261015-020238-151/`。

实际文件指纹与作者冻结报告一致：

| 文件 | SHA256 |
| --- | --- |
| `DungeonDodge.h` | `375ee1aa3d83612a3c686f0b1a6a6d322c97e247ea957c3d7380dcd431fd9ec2` |
| `Tests/DungeonDodgeStandalone.cpp` | `9e298f1cc126ff4a7b2b5685ed15ee3ed03b5e9e9531e4529ad72964422dbc7b` |
| `Tests/RunDodge.ps1` | `be18eb063f8ebb6b78fa2299b47502f484bb9b5255f46ba9f318b15bd1e44e01` |

## 接线边界

`CommitResolvedIdlePosition` 确认外层已经解析的位置事实，本身不验证真实碰撞或授权位移。外层必须先完成合法普通移动/落地/击退，再同刻提交；ID 分配器与核、Actor XY 及 Run 应同批保存。允许旧快照恢复属于整批事务能力，不能仅回退该核来重用旧位置或冷却。

活动状态的未来无敌区间是可被真实中断裁短的承诺；伤害层应按实际接触时间求交，并在中断后重新获取区间。不能以慢帧末布尔值代表整个有效窗。现有独立受伤无敌应取区间并集，DoT等持续状态由外层继续推进。

动作独占/取消事务、Shift edge、实际墙体与活体连续 sweep、普通非破韧伤害、轻甲条件清理及 D13 保存故障恢复均未由本次纯核审查证明。完整动作历史的每步校验/复制成本随历史增加，需在真实长局验证；历史裁剪须先确定世界消费游标和保存合同，不能直接丢弃仍需查询的区间。
