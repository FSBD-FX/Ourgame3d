# Fighter／武器世界 owner 快照实际验证

2026-10-16。本轮完成绑定玩家、石像骑士、石像蝙蝠及武器世界的本地值快照校验与独立安装。最终构建024450退出0；显式完整024633与默认入口024800均111个唯一测试全部Success，零失败／未运行／警告，原103名称保留。当前首批完整内容仍0/15，整局聚合安装和磁盘Continue尚未接线。

## 实际失败与修复

| 实际运行 | 结果 | 说明 |
| --- | --- | --- |
| 013639 | 103Success、8Fail | 新owner接口Stage0真实失败后才制作生产实现 |
| 015859 | 103Success、1warningSuccess、7Fail | 新生产实现；原生fixture世界生命周期警告及真实校验问题留存 |
| 020355 | 104Success、7Fail、0warning | 生命周期修正；World六类引用／相位反例及Actor诊断达到 |
| 020837 | 108Success、3Fail | World反例窄修通过；Actor真实坐标投影误判被复现 |
| 021659 | 109Success、2Fail | native微小坐标安装与过期后伪刷新两反例 |
| 022145 | 110Success、1Fail | 上述修复后仅custom muzzle精确安装反例 |
| 022654 | 111Success | 当时schema1/已有断言通过，未覆盖随后新增真实anchor遗漏 |
| 023434 | 仅Actor5：4Success、1Fail | 正常两步起跳证明actual anchor独立于JumpHeight；1e-10位置安装也失败，不是full111 |
| 024633、024800 | 各111Success | schema2保存actual anchor、原生精确安装与全部回归／默认入口通过 |

各报告位于UnrealGame/Saved/Automation/FirstRoom-20261016-对应编号，v061–v070分别保存当时真实源码、DLL、资源和报告。015508命名冲突编译失败亦保留，没有给崩溃或无报告的运行伪造结果。默认ExpectedTests仅在实际111GREEN之后103→111；实际显式运行所用旧脚本另保存在evidence/fighter-owner-snapshot-v001/actual-schema2-green-v001/。

## 关键真实状态

Fighter保留完整动作内核、三连击／装填／闪避／保护、出生锚点和时间、terminal合法显示下降与冻结战斗时钟、原始发射socket及回执历史。资源以完整保存的装备事务与WA实例交叉校验，退役／旧房间目标仍可引用；恢复不分配Run内ID、不重播攻击或奖励。独立staging回捕获逐字段比较，实际微小发射口定义和原生world位置也精确保留。

UE原生普通移动可保留与内核稍有差别的body投影；使用本机同版本原生Equals验证这一合法关系，同时保留两边原值。普通组件更新也使真实JumpHeight=.00063629908254370093而actual native anchor/public muzzle height=.00062999915098771453；将anchor视为Jump纯派生的旧假设已被实际反例推翻。schema2保存完整HeightAnchorRelative，不与Jump/Facing强等；schema1缺字段明确拒绝。原生direct/cache/force安装越过已实际复现的两个小差抑制层，旧正常运行／Sync代码逐字保留。

World保存全部projectile/window/hit/burn/binding/event数组与游标，校验双向Issued来源、冻结原点／射程锚、Range截止点、唯一正损血事实、实际burn应用及继承tick相位。消耗命中不一定有正HP损失；零损血tick也推进phase；同强刷新继承旧phase，过期后重烧必须重新应用。真实E/Enter换房保留旧回执、inactive历史和目标tombstone；不要求整个journal按时间全局排序。

## 冻结与边界

最终v070：1085项、73,299,914字节。Root逐项核对源／冻结副本2170次大小与SHA，零差；[完整审计](evidence/world-owner-snapshot-v001/actual-owner-final-default111-audit-v001.json)。[Fighter合同v002](fighter-owner-snapshot-contract-v002.md)、[World独立最终窄审](independent-world-owner-production-v004-final-review-v001.md)及随后Fighter完整独立审查保存审查范围与历史证据。

这是给定批准Context下的owner primitive；Context指针不是payload，也不是已经验证整个Run的证明。尚需暂停状态下的整局交叉校验／原子安装、geometry/Actor map重建、完整payload、真实新进程Continue及正常输入录像。其它敌人／Boss、20装备搭配、全动作／特效／音效和正式来源仍按完整目标推进，不能用本轮测试替代完整内容验收。新美术145也仍是静态源候选，游戏最新画面仍v054待机试样。

[Fighter schema2完整独立审查](independent-fighter-owner-schema2-final-review-v001.md)：SHA5c0a3844ed225d392361eff59eb937b3ae404f8f35103ce861f5960b4fb8e178，覆盖实际023434失败→024633111GREEN、v069全1085项。默认入口v070的独立补充另存，不覆盖历史。

[默认111独立最终绑定](independent-owner-default111-audit-v001.md)：SHA64379d7e95c732aa900647e00ffeff969fbb8d8c4e385b378dee2d3edfd2111b，v070源／冻结两端2170次大小与SHA核对零差，默认024800111Success，旧103保留。
