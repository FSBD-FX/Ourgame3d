# Death40 原生接入计划

目标：钟盔／军剑／棕皮轻甲在真实致死后保留装备，按已有terminal展示时钟播放Death五相并停留末相。视觉放剑独立绘制；不改变库存、真实世界掉落、存档业务、伤害、kernel或sim时钟。

当前实际基线：v137-range187G，Source246／Production1286／严格187通过；默认范围线清理三次原生通过。当前Fairytale装配在dead时使用裸Ready0，且阻止外层旧death回退；terminal age本身已存在。Death40候选源已审但未导入，不属于实际当前构建。

唯一源包：`Death40-native-ready-author-candidate-v002/native-ready-author-freeze-v002.json`，SHA5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c。25自身body使用v005边界，15甲使用覆盖控制v003，不混用v001/v004；实际匹配E505。独立军剑统一.50，采用清楚离掌release-v002的作者位姿。Root/隐藏骨轴/物理落点没有测量依据，不改称实测。

1. Root核源freeze、40文件尺寸/alpha/hash和E505两端；核v019 objectpath没有占用。先准备只含40源的实际导入manifest与独立receipt检查，保持原1286不变。
2. 先加入有意义的Stage0语义检查并实际RED：致死优先于残留Hurt/Ready/Jump；真实terminal age在sim停止后继续、五个半开区间及.8+末相；缺少任一纹理不得半套绘制，dead HitFlash残值不能永久染红。测试观察Plan和实际actor/binding行为，不能只比常量列表或纹理数量。
3. 实现只读Death查询和独立五相计划/DTO，复用committed装备Binding。由已有terminal AnimationTime驱动；不新增播放timer、不推进sim或改物品归属。Death优先于旧Hurt/bareReady回退；unsupported组合仍保持原可识别回退。
4. 导入实际40、核原1286+40＝1326；41个资源（40+复用Sword）原子预加载，九槽完整渲染。一次镜像、整数source配准不重复应用；phase0与1–4的剑层级不同。Death基材白色，避免terminal时HitFlash不递减导致全程红色。
5. 实际编译、Stage0 GREEN、完整注册回归；新实际snapshot及精确生产扩展profile冻结，旧v137手动入口暂保持可用到新checkpoint就绪，不能让旧freeze替新Source背书。
6. 新原生observer通过正常E提交装备并由Guard实际连续攻击致死，记录HP0、同真实AttackId、GameOver一次、原sim停止及terminal age推进、Death0–4/末相hold、41resident/9slots/实际quad/PNG CRC/固定源投影。左右各一次；不向hero/Guard注入公开诊断伤害。
7. 源/原生/媒体先F原件+展示+索引，再E双size/SHA核对；Root审实际关键帧、Hurt或Ready→Death0、Death4停留和完整短录像，声音另验。正常死亡不制造地面拾取物；R/恢复规则仍走原系统。

边界：正式完整0/15、完整搭配0/20保持到整单元验收；这次只是SWD/LGT Death有限状态接入。Dodge胸衣配准缺口独立继续，避免未接受源进入Production。任何新RED或源偏差保留原件并按实际原因修复，不改阈值凑通过。

代码依据：`combat-range-debug-runtime-debug-review-v001/death-integration-readonly-note-v001.md`（c8492f8b…6fa2446b8），具体指向Fighter1812、GM1889及SwordPresentation97/145/183/247/307/311。实施前读当前实际文件并按新diff更新行号。
