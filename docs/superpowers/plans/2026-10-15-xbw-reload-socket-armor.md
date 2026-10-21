# 猎弩装填、发射口与四甲接续制作

本轮接续完整15单元目标，不能把本轮子集当完整目标。前轮分类为progress：v036源码/资源、实际72测试、新Scene13实录及13独特原帧复核均改变了权威状态。现FirstBatch616/Room3/Scene2，Reload16和Bat27冻结未导入，猎弩射击仍缺pose3实采/世界发射口/四甲适配。

1. root核验冻结Reload16的实际PNG、哈希、矩阵、四关键姿态与半开归一时间；编写非覆写UE导入器。图片不提交弹药。
2. root新增实际Reload采样边界测试与先失败stub；producer/独立review新增真实Actor发射口反例。所有Source/test先freeze，root唯一运行UE/UBT、max2；取得真实RED，再实现并取得原72与新增组全部GREEN。
3. producer将发射口归属Actor、每次真实subhit取当前位置/高度/朝向，presentation与combat高度分别命名和验证。root HUD读同一个契约，禁止屏幕位置反写Actor。不能简单抬combat高度使地面对地失效。
4. root接入Reload16，正常动作四阶段同步body/weapon，成功装填后的loaded与实际发射后的empty仅由真实instance/ammo/accepted action决定；取消、切换、死亡不凭插箭画面补弹。现有Ready/Primary历史证据保留，另profile真实录制。
5. 唯一美术owner继续四甲猎弩原生适配，先Primary6再Reload4，逐姿势冻结合同，来源/计数/F-E保留。未就绪层明确未完成，不能把军剑甲姿势拉伸成弩适配。
6. root实际导入/运行、保存失败版与编译快照，F/E两遍SHA后才看录像原帧；更新README、资产表、需求台账与progress，正式完整数以完整合同为准。

Ruling: 本轮首先完成猎弩当前真实缺口，Bat27保持冻结待后续接入——避免同时修改两种动作渲染/战斗域导致证据混淆；代价是其他敌人美术仍需后续制作，完整范围不变。

Ruling: 显示离手的高度不自动等于战斗受击高度——现65cm判定语义必须保持，世界presentation高度可独立携带但不得干预伤害/去重/资源/排序；错误时将表现为命中或镜像偏移，需独立真实Actor反例与运行图证。

Ruling: 复用已有分工owner——美术单写者与已熟悉Actor边界的producer/reviewer保持责任，root独占HUD/Probe/UE；所有人不得撤销其他人的工作。

范围边界：本轮不是D13/正式来源/15辅助物品或全状态20搭配完成声明；这些继续属于原目标，不能在本轮通过后关闭goal。
