# 暗黑童话盔甲轮廓试样

EV-048用户明确「保持怪诞方向，增强盔甲和轮廓辨识」。本目录先做一张轻装方向的穿戴参考，保留钟盔/琥珀眼/短比例，增加亮灰胸片、适度肩片、护腕与窄护胫；关节和腰膝保留暗色间隙。

| 内容 | 来源与尺寸 | 目前状态 |
| --- | --- | --- |
| [146穿戴参考](readability-reference-v001/raw/146-compact-armor-readability-reference-v001.png) | 内置image_gen编辑，唯一131idle0参考；1254×1254 RGBA，576701B；未来身体目标72px | 原稿＋展示副本已F/E090先保留两遍SHA零差再root实看；只作造型参考，不是独立甲层/最终sprite，不绑定装备ID，未导入UE。 |

[实际完整提示词](readability-reference-v001/prompts/146-light-armor-readability-reference.txt)、[生成输入](readability-reference-v001/generation-request146-v001.json)、[实际回执](readability-reference-v001/generation-receipt146-v001.json)、[分层与小尺寸检查计划](../../../docs/production/first-batch-v2/fairytale-armor-readability-plan-v001.md)。原131公共身体保持权威，后续再逐独立甲层、朝向与动作制作，不把这张合体参考直接覆盖运行身体。

当前native146/window0072of24剩22/累计170，外部API0，内置费用未知。当前UE运行仍是无甲六相步态观察试样，完整内容0/15。


147四个胸片已实际提取并导入新EV048/v001。源四帧各异，共享60/271比例，原131公共身体不改；整数挂腰后的衣领/U槽差保留为不同特征的未接受约束，没有逐帧放大或重画掩盖。胸片约10.38px高，人物仍72px。约11.2秒实际UE有甲/无甲、左右、亮暗背景观察已F/E095保全；大块可辨，扣件/腰沿细节弱。明暗指背景对比，Draw仍白色tint，不是动态光照验收。

| 新增 | 路径 | 状态 |
| --- | --- | --- |
| 147四胸片 | [提取与原件](independent-idle-components-v001/run-front-idle-v001/manifest.json) | 色键/原生component/共享比例QA通过。 |
| 四帧整数配准 | [实际receipt](independent-idle-components-v001/registration-proposed-v001/registration-receipt-v001.json) | 可观察候选；不是同点双挂接数值验收。 |
| 实际UE观察 | [运行审查](../../../docs/production/first-batch-v2/runtime-review-fairytale-chest-lookdev-v001.md) | 四新Texture2D/旧869不变；空手idle胸片专用试样，未完成肩腕胫/武器/allstate。 |

最新native147/window0073of24剩21/lifetime171，外部API0、费用未知；上段146统计是历史记录。完整内容仍0/15。
