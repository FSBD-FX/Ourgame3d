# 卡通暗黑童话石像骑士待机制作

本目录使用EV045/046确定的卡通怪诞手绘方向、EV047先试一版及EV040/041自动授权，继续完整首批目标。仅完成待机原稿和候选透明帧，非完整石像敌人。

**最新纠错候选**：134原稿的 v003 逐姿势缩放会错误放大内收盾牌时的躯干，失败提取保留；同原稿 v004 改为共享行缩放，四帧367/365/366/365px，未重画/改时长，也未导入UE。目标平均可见高93.6px对应固定画布约131.027px，尚须可靠根注册/真实循环审查；第2帧被盾遮挡的脚根不视作精确值。[实查与限制](../../../docs/production/first-batch-v2/fairytale-shared-scale-and-walk-status-v001.md)。当前引擎仍显示132的 v002 四帧试样。

| 内容 | 来源 | 状态 |
| --- | --- | --- |
| 身份参考 | [126原图](../art-direction-dark-fairytale-v001/raw/126-EV047-stone-knight-anchor-v001.png) | 完整左向盾锤石骑，助手技术base门y，非用户最终批准 |
| idle4原稿 | [request132](sprite-run-idle-v001/raw/idle.png)、[生成提示词](sprite-run-idle-v001/prompts/idle.txt) | 数字4帧合同/layout guide，青色键，已F/Ev051保全 |
| 初次提取v001 | sprite-run-idle-v001 | 找齐4帧但足心对齐使第0帧抵边，26边缘像素警告；F/Ev052保留，拒绝导入 |
| bbox居中提取v002 | [curated](sprite-run-idle-v002/curated)、[atlas manifest](sprite-run-idle-v002/manifest.json)、[GIF](sprite-run-idle-v002/qa/idle.gif) | 同原稿确定性注册修正，0errors/0warnings；F/Ev053保全，运动与实际UE试装待验 |

[锚点与实际小尺寸参数](runtime-anchor-review-v001.md)记录每帧root、源朝向、可见高和固定画布，避免套旧模型坐标或把画布当身高。此版没有攻击/冲锋/盾击/恢复/休眠/苏醒/受击/死亡等完整状态，不能计入正式单位完成。

sprite-gen77d7af445dc3 component-row，pixel_unfake=false，未槽切fallback或本地重绘/重定时。本次1内置调用132，费用未知，外部API0；权威ledger132，window00612/24剩12、沿既有口径累计156。原件/展示副本/来源索引及失败版不覆盖，E根README未改。

## 实际 UE 观察更新

四张curated v002已真实导入独立EV047目录，并在v054实际双向待机采样和原帧中显示。[实景与复核](../../../docs/production/first-batch-v2/fairytale-lookdev-runtime-review-v001.md)。尺寸/镜像/落脚抽帧无阻断，独立审查指出头肩轮廓改变偏软，重石待机美术门未通过；继续同身份纠错，不宣称完整敌人或最终运动接受。
