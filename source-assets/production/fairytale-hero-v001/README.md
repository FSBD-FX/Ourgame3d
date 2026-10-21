当前最新（2026-10-16）：v008六相已实际导入UE独立HeroCommonWalk目录并完成4.2秒双向静音观察；身体70.44–72px、UI关闭、15独特原帧实看，仍固定锚点/非真实移动或motion接受。EV048保持怪诞方向、补甲与轮廓；146轻装参考另在fairytale-armor-v001，不覆盖131身体。详见[运行复核](../../../docs/production/first-batch-v2/runtime-review-fairytale-walk-lookdev-v001.md)。以下为历史状态。

当前最新（2026-10-16 03:19）：原六相v005统一提取后发现bbox-centering额外横移，v008恢复原1254画布横坐标；六帧裁剪RGBA不变、同次416/1043比例、原83ms×6。v006/v007工具失败保留，无新增生成。F/E087–088保全后已看完整contactsheet并打开循环页；未动态通过/未导入UE，游戏最新仍v054四帧待机。详见[循环来源与边界](../../../docs/production/first-batch-v2/fairytale-walk-source-cycle-status-v001.md)。

当前最新（2026-10-16）：143前伸静态候选；144前跟过低已拒绝；145定向纠错后前跟微小离地可辨，已组件提取／共享fit／atlas／curated，Root与独立实看。完整walk未导入或验收，游戏最新仍v054待机试样。详见[来源、提示词与保全](../../../docs/production/first-batch-v2/fairytale-hero-precontact-poses-status-v001.md)。未来角色可见高度仍72px，本张512px是源画布。

# 卡通暗黑童话公共身体制作 v001

沿EV045/046已确认方向、EV047先试一版及EV040/041自动授权推进。此目录以钟盔/琥珀眼为共同身份，移除烘在躯干上的四甲/披风，准备独立装备分层。131待机四帧已真实导入 UE 的造型预览，角色可见目标高72px；其他新动作与四甲分层尚未完成，不代表完整角色或20搭配。

**2026-10-16经过相试验**：140未画清远腿根，保留失败；141近腿前经过静态可用，142定向编辑140后远腿从近侧站腿后方显露，两相角色现在可辨。各1张512RGBA，仅静态候选，未来可见高72px、未导入，不能称完整walk。142明确绿色键提取在 `sprite-run-passing-far-leg-edit-v002/curated/`；v001漏参数使用错误默认色键已隔离失败，均保留。[来源与实看边界](../../../docs/production/first-batch-v2/fairytale-hero-passing-poses-status-v002.md)。

**后续纠错状态**：135/136六帧行走数值QA通过，但近远肢体未正确交换，均拒绝导入；137远接触/138近接触单姿势可作静态运动参考，均有512RGBA透明帧，未来目标仍可见高72px。139双contact参考生成的六帧0/3改善，但1/4仍重复支撑/后折腿，完整步态继续拒绝导入。[共享缩放与步态实查](../../../docs/production/first-batch-v2/fairytale-shared-scale-and-walk-status-v001.md)。下表为原制作阶段记录；实际131待机运行见[UE试样复核](../../../docs/production/first-batch-v2/fairytale-lookdev-runtime-review-v001.md)。

| 内容 | 来源与制作 | 当前实查 |
| --- | --- | --- |
| 公共身体单张基准 | 内置129由125参考编辑，1254×1254 RGB绿色键；[原稿](raw/129-common-body-idle-base-v001.png) / [完整提示词](prompts/129-common-body-idle-base-v001.txt) | root技术基准门y，非用户终批；头盔/空手/深灰内衬/棕手靴，无甲片披风 |
| 待机原v001 | 内置130，数字4帧合同+layout guide；默认components去键提取、atlas、curated export4张512RGBA | 数值QA过，但第二帧刚性头盔缩形风险，未接运行；[独立复核](../../../docs/production/first-batch-v2/fairytale-common-idle-review-v001.md) |
| 待机纠错v002 | 内置131另生成，旧raw/run不改；同样4张512RGBA，4×167ms manifest | 提取/atlas数值QA过，root与[独立逐帧复核](../../../docs/production/first-batch-v2/fairytale-common-idle-review-v002.md)均看出刚盔改善；完整动作循环/运行审阅尚待；[GIF预览](sprite-run-idle-v002/qa/idle.gif)仅预览，不以GIF厘秒时长替代manifest |

两run均在各自sprite-request.json保存数值合同，prompts/idle.txt由sprite-gen prepare生成；engine77d7af445dc3，pixel_unfake=false，RGB绿色键component提取，不使用槽切fallback，不本地重绘/重定时修动作。curated/为导出帧，frames/不是最终交付入口。后续运行按manifest.frame_layout/durations_ms采样，不能猜旧6帧或沿用旧Root/Grip。

全部展示前F/E保全：v044单张6文件3,396,130B；v045原待机9文件3,777,918B；v046原提取24文件6,074,754B；v047纠错原稿9文件3,779,926B；v048纠错提取24文件5,973,374B。两遍大小/SHA均零差，E根README未改，保全索引保持当时状态，后续审查另写docs。费用未知，外部API0；本轮3次内置调用129–131，权威ledger131、window00611/24剩13、沿既有口径累计155。

## 本轮候选资源补充

| 资源 | 源画布／未来游戏显示 | 路径 | 状态／费用 |
| --- | --- | --- | --- |
| 143近后推蹬／远前伸 | 512RGBA／未来主角可见高72px | sprite-run-precontact-near-push-v001/curated/frame-0.png | 静态候选，未导入；内置费用未知 |
| 145远后推蹬／近前伸 | 512RGBA／未来主角可见高72px | sprite-run-precontact-far-push-v002/curated/frame-0.png | 定向纠错静态候选，未导入；内置费用未知 |
| 六相来源计划 | 6相83ms设计，实际stride/root未定 | walk-six-phase-source-plan-v001/source-plan.json | 仅文本元数据，未拼动画／无新增生成 |

| 完整来源步态基线 | 原138/142/143/137/141/145，83ms×6 | sprite-run-walk-v005；共享比例，bbox横移待纠错；仅来源试样 |
| 原cell横坐标纠错 | 同源无新生成，六裁剪RGBA不变 | sprite-run-walk-v008；headcore跨度1.5px，未导入/未动态通过 |
