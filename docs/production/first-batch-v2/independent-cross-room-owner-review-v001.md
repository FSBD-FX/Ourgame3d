# 跨房间 owner 绑定窄修独立审查 v001

2026-10-16（Asia/Shanghai）。结论：当前 Schema2 owner 范围未发现这两处条件修复的新阻塞问题。真实换房后的 player/新knight Capture 误拒已由 RED 转 GREEN；默认入口实际112/112成功，原111名称和40份原测试cpp均保留。本结果修正合法 player 出生房绑定的解释，不是 GM 聚合恢复或磁盘 Continue 已完成。

本次只读 Source、测试、实际报告、DLL、冻结 manifest；没有运行 UE/UBT，没有修改 Source/测试/脚本/ledger/资产或既有审查。实际证据目录为 `F:/Ourgame/docs/production/first-batch-v2/evidence/run-aggregate-contract-v001/cross-room-production-v001/`。

## 实际根因与两处条件

真实Scene流程保持同一Run、同一个Player Entity1；World.ActorBindings 的player项保留出生Room1。换到Room2时旧Knight Entity2成为历史tombstone，新Knight Entity3绑定Room2。这是正常输入J真正击杀/领取奖励/清房、E打开确认、Enter提交出口的结果，没有改HP、room-clear、稳定map或binding来伪造跨房状态。

原 Fighter validator 第120行要求全局player binding属于current，且第125行又要求被恢复Actor自己的binding属于当前snapshot房间。因此Room2玩家自己被拒绝；即使新Knight有正确Room2项，也因全局player仍记录Room1而被连带拒绝。

完整cpp diff只有以下两项条件及对应注释/诊断：

1. `HasPlayerBinding` 对 `EntityId==Equipment.OwnerId && ContentId=="player"` 成立，不再要求其出生room等于current。**前面的非零房间、room不大于current、唯一EntityId、Content非空以及敌方allocator范围门完全保留。** 它允许同Run内合法既往出生房，不允许未来房间。
2. 被恢复Actor自己的binding房间，仅对非player仍要求 `Binding.RoomInstanceId==Snapshot.RoomInstanceId`。Kind暂时改成player不能绕过后续校验：S.EntityId仍必须是Equipment.OwnerId，Enemy必须false，恰有Player variant，binding.Content必须player；否则明确拒绝。StoneKnight/Bat/未知Kind不会获得player例外，当前敌人的历史房binding仍拒绝。

Snapshot/Context 的Run/Room/Entity相等、Equipment/World当前scope、Schema2、完整内核、finite/资源/pose/actual-anchor等原门均未改变。没有改player出生binding本身，没有归一化World历史或改正常runtime Sync；constructor起整个原Fighter runtime suffix与修前逐字相同。字段布局不变，不升级schema或伪迁移旧档。

## 新测试的真实来源与拒绝边界

唯一新增注册 `CodexDungeon.Content.RunAggregate.CrossRoomOwners`。它先通过Room1 player/knight默认真实GM Capture和独立staging Restore，再正常移动/J击杀/领取、移动到出口、E确认前检查、Enter真实换房；确认同Run/同Player、单一出生binding、旧knight历史项和新knight当前项，然后独立尝试Room2 player与Room2新knight两个观测，不短路掩盖第二个错误。

每个成功owner用显式批准的saved Equipment/World Context恢复到独立Actor，完整字段签名（含actual HeightAnchor）回捕获相等；只清未接受输入，没有重置已接受义务。新增同组负例分别篡改候选Context里的future-player-room、wrong-player-content；对Room2敌人再篡改为past-room binding。每次均要求拒绝、非空诊断、在原正确Context下回捕获完整owner/原生muzzle不变。测试末尾保留Run/room/revision/crit cursor/world IDs/journal cursor/ActionAudio cursor/pickup count不变检查。

这些负例对准本次放宽点，不以完整World validator先拒绝来掩盖Actor自己的门。当前Knight跨房路径已实测；Bat共享非player房间条件的静态结论不描述成新增Bat跨房实测。selected外部cursor/count检查也不冒充完整GM对象图事务证明。

## RED→GREEN实际报告

- `031105`：111 Success、1 Fail、0 warnings/notRun/inProcess；原111全部Success。新CrossRoomOwners仅两error：Room2 player Entity1和Room2 knight Entity3默认Capture都失败，诊断为缺current-room binding。Room1两个正对照captured=1。报告82725B、SHA `2941900786915d2494b9c242b5184d14e917a4eee2a1370610983a09ff665d1c`。v071冻结的Fighter旧SHA `834aae1d…`、新增原测试 `26ad2c8f…`、DLL `e604a880…` 与报告逐项长度/SHA匹配，原件保留。
- `031713`：实际完整112/112，0 errors/warnings/fail/notRun/inProcess；新case的Room1/Room2四个owner均captured=1。报告81768B、SHA `5c0bde2a82cefb2e659485fe5f3514a560020db886fc760c681b7ed10db7d739`。原111名称完整保留且全部Success，新增精确只有CrossRoomOwners。
- 默认入口 `031901`：再次实际112/112、112唯一完整名称、0 errors/warnings/fail/notRun/inProcess。不是仅靠ExpectedTests改数通过；旧111同样全部Success。

## v072最终文件绑定

`F:/Ourgame/source-assets/production/backups/2026-10-16_cross-room-owner-default112GREEN-v072/compiled-source-manifest.json`。独立重读 **1089文件、73,394,914B**，对frozen和当前对应文件逐项长度/SHA，共2178文件端点检查，差异0。原v070中Tests目录49份源文件（40cpp+9其他）SHA全部相同，没有改写旧111测试实现。

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| DungeonFighter.cpp | 98927 | aa7f70fb718e115e599d212c40887e6893b5dffe6d4992c7c0831e41a760d385 |
| DungeonRunAggregateTests.cpp | 23738 | f3c08b42b44f9e5b0efefee13d4b6c3835bb90270cd2caceb131677867152448 |
| UnrealEditor-CodexDungeon.dll | 3094528 | 9313b52ba350a28775f61433579a78585d192c1a7a33b1df966d64f46ab5b596 |
| build-editor-20261016-031531.log | 4294 | d07c7aebe47f2c3084ccc5d972be1918754d936c268ee719abfe298ad17c768b |
| FirstRoom-20261016-031901/index.json | 81763 | 9e0127602c85285b080057611599cd67458164ac0751cffef27d14fcff483f8c |
| tools/scripts/test-first-room.ps1 | 1589 | 7ff916fb2b7ea44ed3389a7d8a2fbde2c04193f36c000f2270c3c40ebd98fb48 |

独立脚本diff只把默认ExpectedTests111改112，原非零进程/缺报告/failed/notRun/成功数量门原样保留。Fighter原生数值修复、World恢复规则与所有旧测试并未为新增case退让；艺术工具的独立变化不属于本次Actor逻辑。

## 进度边界

测试名的RunAggregate前缀表示为未来聚合提供跨房owner反例，不表示已经有aggregate编码器、paused Actor map整体安装或新进程正常Continue。它验证真实正常换房来源的owner可以捕获并独立恢复；没有把staging Actor绑定进live GM、恢复磁盘档或实际播放游戏证明。完整装备/敌人内容仍0/15；本审查没有观看动画/视频或试听声音。
