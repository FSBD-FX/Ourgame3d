# 钟盔地牢 · 当前开发页

当前为有限试玩，持续制作目标未完成：正式内容 **0/15**，装备搭配 **0/20**，FinalAccepted=false。
方向：2.5D横版动作地牢，固定侧向视角，地面前后/左右移动与跳跃高度独立；怪诞暗黑童话、小比例钟盔角色，站立基准72px，隐藏HUD文字。

## 启动与操作

开发根：`G:/Ourgame`。最新入口：[钟盔轻甲开发试玩_v148_便携版_v001.cmd](钟盔轻甲开发试玩_v148_便携版_v001.cmd)。
**2026-10-20 G盘已实测：全量恢复SHA、1808编译输入、D3D11全203项零失败/零警告；实际71帧K8/30cm/回待机与81源/GPU读回通过。** 只审阅两张全图，连续观看/听感与完整单元仍待。
Enter开始；WASD地面移动；E靠近轻甲后穿戴（0.50秒）；J普通连招；K军剑副攻；Space跳跃；Shift闪避；R重开本局；关闭窗口退出。
当前开发入口使用QA轻甲来源，不能据此认定正式拾取/合法获得流程完成。独立稳定试玩仍为旧v142快照。

## 已有证据与边界

迁移前基线为 **Source308 / Production1495**；历史D3D11全203项GREEN。对应[编译清单](source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001/compiled-source-manifest.json)保持原SHA，不将迁移算作新增游戏内容。
历史K六案覆盖左右完整、部分、零前踏，成功采集共1006原生帧；首次左侧部分前踏失败259callbacks仍单独保留。各案K0..7合成像素audit通过，详情见[六案例汇总](G:/OurGameArchive/2026-10-20_项目体积与迁移盘点_v001/展示副本/K8六案例进展-v001.md)。
Ready专用光学验证、完整连续观看、听感与设备起声仍待完成；历史采集与有限静图审阅不等于正式验收，也不构成G盘运行验证。

| 当前资产 | 实际状态 | 尚待完成 |
| --- | --- | --- |
| 军剑K8 | 八姿态分层已接入，具上述六案历史实录 | Ready光学边界、连续动作/听感与正式接受 |
| 棕皮轻甲LGT | 当前军剑试样使用独立胸甲/双肩分层与实际穿戴 | 全状态适配、正式获得流程及全部搭配 |
| Air6 | 非攻击六姿态跳跃已接入，有历史实录 | 专属AirJ六姿态攻击、动作接续精修 |
| Guard STN003 | 斧守卫行为及动作试样已有历史制作记录 | 完整单元验收；不计作STN001盾骑士完成 |

## 接下来

G盘迁移与实测已完成，详见[迁移状态](docs/production/first-batch-v2/storage-migration-v150.md)；已生成AirJ专属六姿态request264候选，AJ2留白/握柄/尺度待校准且尚未导入，继续拾取/换装呈现、STN001盾骑士及其余首批内容。
最小历史记录：[v006首次右侧K快照](docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/current308-K8-first-native-limited-review-v006/current-status.json)，只覆盖首案，不替代六案汇总。[旧README详录](README-v148-history.md)保留原相对链接。

过程媒体仅在关键功能、显著视觉变化、重要故障或交付节点留档，优先少量截图与压缩短片；项目必需可编辑源素材保留。选中媒体展示前保存至 `G:/OurGameArchive/日期_主题_版本/`，不覆盖旧版。
关键节点保存后、正常工作汇报前运行 `G:/OurGameArchive/.monitor/check-process-media-size-v001.py --check`。以迁移后压缩归档体积为基线，每新增20GiB仅在正常汇报中提一句，继续制作；不独立打断、不停工、不等确认。执行细则见[容量提示补充v002](G:/OurGameArchive/2026-10-20_关键节点留档与容量提醒_v001/容量提示执行补充-v002.md)。


2026-10-21存储清理：22历史包与4开发包重新核验；最新G工程426文件增量及94项归档索引/关键节点已补存C:/Users/22499/Documents/OurgameSafety/2026-10-21_清理前增量保全_v001。自动目录删除被工具策略拦截，尚未删除，本轮释放0；F约178.49GiB/G约2.24GiB为待清理潜力。详见[清理状态](docs/production/first-batch-v2/storage-cleanup-v151.md)。G当前仅约0.4MB可用；其他聊天knight/game未处理。

2026-10-21容量补充：G经独立复核已恢复约137.20GiB可用，变化来源未核实，非本轮删除成果；实际删除仍为0。最新[清理与保存说明](docs/production/first-batch-v2/storage-cleanup-v152.md)。补充保全已回存G:/OurGameArchive/2026-10-21_清理前增量保全_v001，C独立副本保留。
