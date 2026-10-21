# 实际装备、场景与探索 owner 快照 v001

2026-10-16，F:/Ourgame，UE5.5.4。此记录只覆盖当前已存在 owner 的值捕获、候选校验和独立实例恢复。完整 Actor/Run、磁盘 Continue、正常输入续玩录像尚未完成；首批完整内容仍 0/15，持续目标 active。

## 事实与实际失败

| 构建／实际报告 | 结果 | 已证明的范围 |
| --- | --- | --- |
| 000839／FirstRoom-20261016-001102 | 0/7，通过0、失败7 | 三个真实 owner 的 Capture/Restore 尚为 stub，真实测试先失败。源码及报告冻结 v057。 |
| 002400／002604 尝试 | 引擎退出3，无 index.json | 新测试把 TArray 内自身元素直接 Add，触发数组自引用断言；原崩溃、minidump、源码、DLL、日志留档，不能称为完成的7项结果。 |
| 003051／FirstRoom-20261016-003106 | 5/7，通过5、失败2 | 装备3组和场景历史／精确探索2组通过；探索退化轴和场景非法数值接受仍失败，冻结 v058。 |
| 003809／FirstRoom-20261016-004207 | 4/7，通过4、失败3 | 新增实际换装中无关来源注册的活跃／已提交反例都失败；逐个标签定位了两个场景 NaN，冻结 v059。 |
| 004654／FirstRoom-20261016-004750 | 103/103，零失败／未运行／警告 | 原96名称全部保留，新7含上述真实反例均通过。完整源码／DLL／生产资源冻结v060。 |

实际报告均在 `UnrealGame/Saved/Automation/`，构建／测试日志在 `UnrealGame/Saved/Bootstrap/`。对应完整编译源码、DLL、生产资源及报告分别在 `source-assets/production/backups/2026-10-16_run-owner-snapshot-actual7RED-v057`、`2026-10-16_run-owner-first-production-actual5of7RED-v058`、`2026-10-16_run-owner-rebase-and-numeric-actual4of7RED-v059`。崩溃原件另存 `evidence/run-owner-snapshot-v001/actual-harness-crash-v001`。

003106 的设备3组通过发生在测试局部值复制修订之后：`const auto Duplicate=B.Sources[0]; B.Sources.Add(Duplicate)`。复制来源重复的测试语义、旧断言与3个测试名保留；没有通过删反例绕开断言。

004207 的探索反例：X=[1e20,1e20+16384]、Y=[0,64]，514个记忆值均为.5。有限范围和元素数量检查通过，但64单位轴步在该数量级被浮点舍入折叠。实际引擎接受候选并将当前18个已探索顶点变为514；最大X位置插值实际为0、bits=0000000000000000，finite=1。此实测不支持“实际查询输出NaN”的说法。

004207 的场景逐项标签显示 `layout-survey-nan`、`object-position-nan` 都被接受。单纯 FVector2D 相等／不等比较不足以在该实际构建下拒绝这些位置；交互时间NaN等其他原反例正常拒绝。

004207 的装备反例来自真实 GM：先开始拾取，再注册无关新防具来源，库存 Revision 从2升到3、原 PendingPlan.BaseRevision仍为2。活跃快照被错误拒绝。原截止时间完成拾取后，已提交 Operation.Request 使用新的 BaseRevision，而保存的 PendingPlan仍为原值；该完成快照也被拒绝。恢复必须保留原计划事实，并验证被影响的实例、来源、版本、目标槽和替换物，不应把“任何全局版本变化”当作计划失效。

## 修复与验证边界

根生产 v002 在 `evidence/run-owner-snapshot-v001/root-production-v002` 留有004207前后差异与SHA：探索只在候选构造及形状检查后、安装前要求X/Y每个相邻轴点严格递增；场景在所有6个layout向量及每个object位置的相等比较前逐分量检查有限数值。不重采样、修补、钳制或重写保存值。

装备生产 v002 保留所有受影响字段精确一致；仅允许原BaseRevision到新准备版本之间由无关来源注册造成的版本上升。任何该区间装备操作或Ammo/CD运行更新仍拒绝；原库存Restore已验证完整版本回放。不更改保存的原PendingPlan。装备差异、实际RED报告原件及自审在 `evidence/bound-run-owner-snapshot-v001/equipment/production-rebase-fix-v002`，cpp SHA `0ecc77892bdb13d9d8ed1c10bf74f77de6342cd7a86d46ed2216d2b456379a43`；h及诊断测试保持原SHA。

最终004654构建退出0，004750真实103/103、零失败／未运行／警告。`evidence/run-owner-snapshot-v001/actual103-audit-v001.json` 核实全部原96名称保留，v060共1080文件／72,842,142字节与当前源码、DLL、资源逐项SHA零差。实际报告SHA `f1b31b03e4a1a79e745c0ceec5979bf00cd44ebe1e9e935de491ad623bf6d689`，DLL SHA `b5b2e72b3261244a52968c1f324176205940fd522ebd8512b035a271def708e2`。严格脚本默认数量仅在实际103通过后从96升至103。

独立初审及004207真实诊断保留在 `independent-scene-fog-snapshot-review-v001.md`、`independent-equipment-owner-snapshot-review-v001.md`、`independent-owner-diagnostics-004207-review-v001.md`。最终差异／证据审查单独留档，不覆盖这些发现问题时的版本。

最终独立审查 `independent-owner-three-fixes-final-review-v001.md`，SHA `99a059851c248489ebb3ee14a9b0b0ce8853f07d3c63b98b1b143aedb321c441`：直接读取真实103项、旧96名称及v060两端2160次大小／SHA校验零差；三个局部缺口关闭，未发现新的实质问题。结论仍限定owner层，不升级为Actor/整局Continue。

## 尚未完成

这些 owner 快照仍是完整 D13 的组成部分。尚缺玩家／敌人 Actor 的全部状态与动作时钟、投射物／燃烧和奖励去重、HUD探索状态安装、聚合跨引用验证、完整 canonical payload、语义提交与磁盘发布、暂停重建和新进程正常输入 Continue。不能用 Restart/BeginRun、新初始化、离线追赶或重播历史成功音效代替恢复。

美术140／141是独立经过相试验：141静态近腿经过关系可用，140仍把近腿画成抬起腿。142已另做定向髋／腿遮挡修复，root及独立实看与141的角色可辨交换；上身／靴有生成微漂，所有失败版本保留。F/E原图及透明帧留档，未导入UE、没有完整walk接受，见 [经过相状态v002](fairytale-hero-passing-poses-status-v002.md)。
