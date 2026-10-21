# 首单元动作生产与组装准备

开始于2026-10-14，完成来源检查于 **2026-10-15 00:12 Asia/Shanghai**。归档沿用开始日的版本目录，历史副本和 frozen v001 均保留。

事实：EV038 的内置 imagegen 授权共 **24次，已用24、余0**，含一次盾击纠错，已停止全部生成。24张工具输出均保留工具原件、项目raw、归档原件和展示副本，四处SHA256匹配。未调用外部API，host费用未知。asset-gen用于生产流程，generate2dsprite现成processor负责透明处理、分帧和统一缩放；代码没有绘制替代角色。单张生成后均先归档，再逐图view审阅。

实际产生2张身份基准、1张独立军剑、20张成功或明确姿态候选的动作raw，以及1张被拒收的原盾击raw。可供下一步实机检查的 **122张独特动作PNG** = hero68 + stone54，另6张失败盾击帧不计入122。Hero的跳跃连续8格映射jump/fall/land为4/2/2，因此20张raw动作图对应22个逻辑状态候选（hero13/stone9），没有重复计算帧或把静态基准当动作。

| 冻结入口 | 用途与边界 |
|---|---|
| `import-subset-v001.json` | 初批36帧+军剑，可复核旧入口，保留未改 |
| `import-subset-v002.json` | 全122帧逐源SHA、512RGBA8、alpha/corners、逐帧root、22状态映射与phase计划 |
| `assembly-markers-v001.json` | 初30帧idle/walk/三段主攻，保留未改 |
| `assembly-markers-v002.json` | 全68帧hero/13状态手点、原像素近手ROI、候选剑角度；jump/fall/land另保留原家族索引 |
| `source-verification-2026-10-15.json` | 来源、像素、68手点、24原件与归档哈希的实际复核结果，以及两death姿态审阅 |
| `generation-ledger.json` | 每次调用前requested/fullprompt/参考，完成后路径/SHA/状态；cap reached |

推理：这批足够在运行中检查角色、剑和动作映射，尚不足以作为正式分层首单元验收。122帧实际读取均为512×512 RGBA8，有真实透明像素和不透明主体、四角透明，候选无空帧、原始/输出触边或paste clamp。标准grounded动作使用同一角色profile、固定preserve .84，没有逐帧bbox适配缩小人物；hero grounded root为[256,472]。原盾击request14裁盾被拒收，request15纠正后严格门槛通过。默认抠色残边已用现成processor阈值180/260改善；仍测到每帧0–13个洋红相似不透明边像素，最高约0.0218%，不宣称零残边。

两组death保留原站立统计失败，明确`pose_aware_review_required`：hero CV=.0937、anchor std=.0847；stone CV=.0960、anchor std=.0565、对idle面积尺度偏差=.1030。实际六帧均使用同一0.853333像素变换、bbox_fit=false，完整地从站立折叠倒地，头/头盔视觉尺寸随旋转保持；没有独立刚性部件层，未声称测得精确头盔/盾尺寸。最终hero/stone透明轮廓底界分别483/484，contact root估计472；尸体停留、地面接触与衔接仍需运行核查。空气动作的站立CV数值只作诊断，不作为grounded准入，不能因单项数值为true忽略`pose_aware_review_required`。

Air与jump未强行脚底贴地。它们保留center处理的原PNG，由实际可见腰扣作为骨盆代理，按accepted idle腰扣[269,325]到ground[256,472]的固定偏移[-13,147]生成逐帧虚拟root；jump第1/2/7/8接触帧采用实际alpha feet估计。运行应直接消费各帧`root_px`，角色actorZ单独负责全局高度，不再添加第二条图片抛物线。代理点由人工审图，未当作真实骨骼测量。

三段主攻、空中主攻、secondary、stone charge/shield_bash均有绝对phase计划及每phase两帧的映射。军剑三段分别 .17/.12/.31、.15/.12/.27、.22/.12/.32；secondary .20/.10/.38，空中主攻沿第一段。其他状态的`visual_preview_only`不是权威玩法窗口，GIF延时只预览，伤害/无敌/位移不得从GIF推断。jump/fall/land的frame数组保留source_frame_index，markers v002另给本逻辑动作local index。

军剑clean512组件的实测握点[99,256]、刀尖[482,256]均落于实际不透明像素。68只近手均逐个crop审阅并核对alpha，JSON手点是真实可见手位置；剑角度是人工组装建议，因为body图里没有剑，不能伪称源剑角度测量。遮挡是原像素近似手ROI，不是完整near-hand分层。Idle、部分walk与death为张手/松手，闭合握剑缺口仍在。原 .55 组合预览刀尖偏低、primary1击出偏刺；root另有 .40/idle35°/walk30°/第三段角度算术调参候选，本报告不追认这些实机通过。

风险与剩余工作：hero衣服仍烘在body，stone盾/剑仍烘在整身，没有可替换甲或完整near/far层；现有正式atlas schema也不能表达合法全隐藏层。本批未填假透明/复制整身层绕过校验，`formal_content_atlas_validation_passed=false`。握剑自然度、手部精确遮挡、可信横斩/斜切、左右一次镜像、脚滑/循环、跳跃虚拟root与死亡接触，均待运行组装。Stone wake第4帧眼灯回暗保留为可见闪烁候选。没有装备交互新增图，不能声称完整正式首单元交付。

复核命令（只读，不生成、不写引擎）：

```powershell
& 'F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe' -X utf8 -B 'F:\Ourgame\source-assets\production\first-unit-animation-v001\verify-frozen-assets.py'
```

报告和媒体位于 `F:/Ourgame/过程图稿与视频/2026-10-14_首单元动作生产_v001` 的原件/展示副本及index。`reviews/marker-closeups-v001.png`、`remaining-marker-closeups-v002.png`、`pelvis-closeups-v001.png`和`assembly-preview-v001.png`均为已有art的确定性审图资料，不计新生成或runtime帧。本代理未启动UE/Blender、未改UE源码或全局配置、未commit；主线程的导入/运行receipt与验收应另行引用。
