# 裂岩守卫 Move：2D 腿部 rig 可行性候选

结论：可行，但这是新的动画、渲染和取证模式。建议停止同类整身条带重试，先做两个相反触地的 rig 小样，再决定完整六相。当前没有制作 rig、生成组件或准入运行。

## 事实

221、223 六格和226双关键姿态都未完成物理近/远腿交换；223另有斧头原稿裁边。技术透明QA通过不等于动作通过。当前截取的 Guard presenter要求恰好一个整身层；HUD已有带pivot的旋转纹理四边形，但没有Guard腿骨层级或IK。现有Move选择器已按真实Movement回执累计路径并取128world相位。

sprite-gen的 `compose-layers` 只做整数平移与alpha遮罩，不做旋转、缩放或IK；不能把该命令的rig字段冒称骨骼动画。asset-gen的rig/retarget说明属于外部3D GLB服务，不适用于本候选，也未授权调用。

## 资产和遮挡成本

| 最少资产 | 内容 | 明确artist源标记 |
|---|---|---|
| BodyRest+固定斧 | 头盔、躯干、前景骨盆遮挡边、双臂闭拳和完整同一重斧；不画腿 | root、crown、near/far髋挂点 |
| Near大腿/小腿/脚 | 前景侧三段腿链，需opaque接缝覆盖区 | hip/knee；knee/ankle；ankle/heel/toe |
| Far大腿/小腿/脚 | 独立后景侧阴影/透视，不能偷偷镜像Near替代 | 同上 |

最少7张透明源组件、18个显式artist标记、6个limb变换骨。必要时再加两个膝盖遮挡帽；不要提前无依据加层。现整身Ready的旧腿、近髋和斧柄尾部相互遮挡，矩形裁切不能保证可用BodyRest，更不能补造隐藏像素。较稳妥的源计划是1次BodyRest、1次Near三件kit、1次Far三件kit，共3次拟定首轮调用；这不是次数或费用保证。内置收费与窗口由Root ledger决定，不能拿外部3D价表当内置价格。没有本管线实测工时，不承诺小时或天数。

## 真正 rig 的范围

用 `Root / BodyRest / NearThigh→NearShin→NearFoot / FarThigh→FarShin→FarFoot` 层级，所有源pivot、固定长度与固定scale在实际组件留档审图后作者明确设计。它们是2D制作轴，不是假称恢复了原人物隐藏骨骼。Far链先画、Near链再画、BodyRest及骨盆前缘/固定斧最后画，保留近腿前景遮挡；两手与斧继续整体烘在BodyRest，不新增手柄rig。

相位仍来自真实已接受碰撞移动路径 `distance mod128`；0近腿触地、3远腿触地，中间各经过承重和摆腿。64world接触边界若落在一条Movement线段中，按距离比例插值真实From→To位置建立该脚的world支撑锚。支撑期固定该锚，再投影回实际Ground；不得移动actor来救画面、按速度乘时间伪造步幅或用draw次数生脚步。纯X的32world半步投影20.8px，真实Y对齐也必须纳入。组件腿长与髋高度必须能覆盖目标，不得伸缩骨长或偷偷改128/160。

若要求连续足底支撑，优先实时rig插值/双段IK。离线rig烘六张透明图可减少HUD改动，但必须标为RigDerived，保留组件、rig和姿态来源；不得冒成AI生成六帧或写入由SG extractor独占的frames目录，而且六张保持图并不能证明连续足锁。

## 集成边界与风险

Move需新的LegRig模式和组件pin/变换/接触锚回执；当前恰好一层的Guard门不能直接放7层，更不能伪造NativeSourceId。7个texture提交相对1个整身提交增加渲染、遮挡和observer工作，需真实敌群/双向/转向/阻挡测试。脚步仍由已有64world接受距离消费者一次发出，渲染不得加伤害或重复音效。

所有非Move状态继续整身源动作。这个方案不会修复已经登记的WU→Active约29.7px上身跳变，或Active1→Rec0约10.46px进一步下压；这些攻击衔接风险独立保留。厚石板关节的缝隙、双黑边、转动后透视与折纸感是主要美术风险，必须先在100.8px实际显示尺度检查两个相反触地小样。

后续第一步仅是Root决定是否采用、批准组件源计划并做隔离contact小样。当前没有新组件、最终像素、骨骼实现、API调用、Source/Content/tools/ledger/UE修改。
