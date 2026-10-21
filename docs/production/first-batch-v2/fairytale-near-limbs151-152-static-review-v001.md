# Native151／152近护腕护胫保全后静帧复核 v001

2026-10-16。root确认E114实际81files、3,830,284B、两遍size/SHA零差后，才查看本轮派生图。本作者承担本轮输入准备、标准提取和确定性注册；这是制作后的有限静帧复核，不冒充独立于制作作者的第二验收。没有运行UE、导入或图像生成。

实际看过以下8件，公共目录为：

`F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v002/near-limbs-registration-proposed-v001/`

- composite-preview/frame-0.png
- composite-preview/frame-1.png
- composite-preview/frame-2.png
- composite-preview/frame-3.png
- rivet-source-crops/near-bracer-frame-0.png
- rivet-source-crops/near-bracer-frame-3.png
- rivet-source-crops/near-shin-frame-0.png
- rivet-source-crops/near-shin-frame-1.png

原151/152条带及151原创guide此前分别在E111/E113/E110保全后查看；本次没有实际播放GIF或视频。

四帧中的近护腕均位于灰袖前臂，斜向左下，末端靠近棕色腕口但仍能分清甲片和手套。未见明显盖掌、拇指、手指或向手套外伸出不合理尖角。近护胫均位于近腿裤料下段，末端与斜靴口之间仍可见灰布／墨线；未见覆盖棕色靴皮、脚尖、鞋底或改变原足线。甲片宽面、深外沿与147胸片及149/150肩甲的手工灰铁构造协调。新增件在四张中没有明显悬浮、左右错侧或大幅移位。

关键原crop确认A确实来自圆铆钉外圈。近护腕的黑色小点偏离外圈几何中心，因此不用黑点中心替代挂点；护胫的亮色内面也不应当作另一attachment。当前固定ROI深色圆环中心映射、整数平移有可复核依据，保留约±1px feature／量化歧义，不把构造后的A=target当成穿戴零误差。

有限结论：**无静态阻断，可作为root固定72px的真实UE试装候选**。目前看到的是512源图叠合，不是72px游戏截图，不能承诺铆钉、翻边细节在场景中可读。原生护腕前三帧bbox32×28、末帧31×27，护胫30/30/31/31×34；采用每行共同ratio，没有逐帧fit掩盖变化。静图未见明显跳变，不等于4→0循环或刚性运动已通过。

没有实际131语义mask或near-arm／near-hand运行分区，因此不称零碰撞、武器握持遮挡已完成。只有near两件，far护腕／护胫未制作；也不代表完整甲套、walk、攻击、受击、死亡或全动作适配。保留既有149旧B残差历史，不为本次通过而回填旧门。formal仍0/15。

注册证据：[registered-freeze-v001.json](F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v002/near-limbs-registration-proposed-v001/registered-freeze-v001.json)，SHA161bde9b4bb443c735f67db20416ab6f9682073476d7b182b9eb7b70dd27e8df。两行标准QA0errors/0warnings，8件注册cropRGBA逐字节未变、无裁边；这些是几何/编码事实，不能替代上述有限视觉判断或后续运行审阅。
