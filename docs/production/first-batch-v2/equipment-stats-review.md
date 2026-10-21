# 装备属性纯核独立审查与修复确认

日期：2026-10-15，Asia/Shanghai。审查者：stats_review。结论：发现的 **P2 吸血双时点缺陷已修复并关闭**；本轮范围内没有其他高置信度阻塞问题。此结论只覆盖纯核，不能作为 Actor 接线、投射物、装备事务或内容单元运行完成的证明。

## 范围与依据

只读审查 `UnrealGame/Source/CodexDungeon/DungeonEquipmentStats.h`、`Tests/DungeonEquipmentStatsStandalone.cpp`，并核对其生成脚本和运行脚本。设计依据为 equipment-v2 的共同规则、属性计算、逐件适配与 JSON，以及 D03 `items-v1/common-rules.json`、D08 `economy-v1/equipment-growth.json`、D09 `progression-v1/talents.json`。

确认以下实现与来源一致：

- 所有有效来源先按同 stat 求和，再加入相应基础值并封顶一次；备用武器验证但不贡献。
- 武器 grade 进入同一伤害百分比预算；防具 grade 按原模板护甲/魔抗生成 flat，不以附魔后的当前值计算。
- 负护甲、魔抗和韧性词条的资格以原模板为准，grade、天赋和其他来源不扩大可抽幅度。例如 LGT001 原护甲14，破损IV只允许13–14，V仍为空。
- 最终最大生命计算后才做一次 `min(previousHP, newMaxHP)`；增加上限不回血，0不复活，存活0.4不截成1。
- 附魔方案检查数量、极性、等级、原模板资格、整数幅度和互斥组；元素共享组，相反词条不能同包。

黄金区间夹具从 `equipment-profiles.json` 已存区间读取，生产函数则从模板、词条与等级计算，未用生产函数生成期望结果。夹具生成器与生产数据冻结器共用脚本，因此 `--check` 只能证明与来源一致；计算规则是否合理仍须审查设计。全部属性 cap 测试引用冻结定义本身，不能单独发现源 cap 被一起改错。首批20种搭配测试覆盖基础属性，不代表全部附魔组合的运行验证。

## P2：吸血率快照与当前治疗属性混用（已关闭）

来源：`docs/design/equipment-v2/enchant-rules.json:161–162` 和 `01-属性体系与计算.md:22,135` 明确要求：吸血率属于攻击锁定快照，治疗效率和最大生命属于实际恢复时的当前接收者。

原实现的 `LifestealAmount` 用同一个 `FResolved` 读取两类属性，无法直接表达这两个时点。最小复现：

1. 发射时 XBW001 带汲血V级5%，防具无治疗加成。
2. 命中时已持无吸血的 SWD001，当前 LGT001 带复原V级25%；当前HP50。
3. 敌人实际损失20HP，攻击和滚动预算分别剩3、6。
4. 正确回复 `20 × 0.05 × 1.25 = 1.25`。原实现传当前属性得到0，传旧攻击属性得到1。

作者最小修复：`DungeonEquipmentStats.h:387` 增加必填 `SnapshotLifestealPct`，当前 `FResolved` 只提供恢复时属性；快照率检查有限且位于0–5，不保留旧单时点 wrapper。原预算、存活与当前HP限制保留。测试 `DungeonEquipmentStatsStandalone.cpp:964–966` 新增上述跨时点用例。

审查者在单独 Temp 目录以 `/EHsc /utf-8 /std:c++17 /W4 /WX` 重新编译原最小复现，使用当前属性与独立5%快照率，实际输出：

```text
both_loadouts_valid=1
snapshot_lifesteal_pct=5 current_lifesteal_pct=0 current_healing_multiplier=1.25
fixed_result=1.25 expected=1.25
RUN_EXIT=0
```

最小复现源及结果保留于 `%TEMP%/OurgameEquipmentStatsReview/20261015-005602-176-fix`；原错误复现保留于同根 `20261015-005223-607`。本次修复复核没有重跑完整套件或 UE。

## 验证证据与指纹

修复前，审查者独立运行完整脚本，16,405断言、0失败，冻结来源 `--check` 通过。此结果没有覆盖双时点缺陷。作者新增真实回归后的原日志已读并核对 SHA256：

| 证据 | 实际结果 | 原日志 SHA256 |
| --- | --- | --- |
| `20261015-005130-634-VERIFY`（审查者修复前复跑） | 编译0；16,405 / 0；退出0 | `9a53f7d156453a3fee578078274638fbbddf29c0f925de768fb1de925aae1603` |
| `20261015-005334-817-RED`（作者） | 编译0；16,406 / 1；退出1 | `d684a6e2fb53853b870a38a81486104b08fabc2f4cbc873625b5148c46416320` |
| `20261015-005418-991-GREEN`（作者） | 编译0；16,406 / 0；退出0 | `9cce121c472c5b1cf392cc3b8bd54ee2e5acefad1f16c52f31042b8df52c7bab` |

上述完整套件原日志目录为 `%TEMP%/OurgameEquipmentStats/<批次>/standalone.log`，全文亦由作者保存在 [equipment-stats-kernel-report.md](equipment-stats-kernel-report.md)。

修复后源文件实际 SHA256：

| 文件 | SHA256 |
| --- | --- |
| `DungeonEquipmentStats.h` | `c33671c5a4fd6cf0c68ede77c473d649692dc9718f7fbd3fb9a1896a26dcb9e7` |
| `Tests/DungeonEquipmentStatsStandalone.cpp` | `275dabc8a56a30b2470237c6b1cdd1147284fa27244b04a69e21c91cbe610aba` |

后续接线仍须在真实攻击锁点保存吸血率，在真实恢复点重算当前治疗属性、读取当前HP，并原子消费实际回复预算。纯核没有实现这些时钟、AttackID预算账本、随机抽样、费用事务、存档或 UI；本次关闭的是接口缺陷，不是这些运行验收项目。

审查者只新增本文件；未修改实现、设计来源或其他 agent 文件，未构建/运行 UE，未生成图像或调用外部 API。
