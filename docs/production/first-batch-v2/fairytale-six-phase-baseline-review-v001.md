# 六相步态 v005 基线独立审查

2026-10-16（Asia/Shanghai）。结论：v005 可保留为真实共享比例提取的实验基线；尚不能判定完整动作通过。**支持下一 v006 只做原1254-cell横坐标的统一机械 registration 对照**，因为当前 bbox-center 额外引入的头/身体横移已有直接证据。它不修复原图姿态、纵向体重转移或动作节奏，也不是最终身体/脚根定义。

root 已确认 E087 保全后，本审查实际 view 了 `sprite-run-walk-v005/qa/walk-contact.png` 及全部六张 `curated/frame-0..5.png`。只读原图、源计划、当前 manifests、wrapper 与像素数组，仅新增本报告；没有生成/编辑/拼接图像、提取/导入、播放 GIF/视频、运行 UE 或修改 Source/ledger/旧 run。

## 已核实的提取事实

目录：`F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v005`。

- 原序仍为 request138/142/143/137/141/145，对应 near_contact、near_support_far_pass、near_push_far_reach、far_contact、far_support_near_pass、far_push_near_reach。唯一身份131不变；源计划 SHA `a20838742e3c7df5e08d0753dfa38e6bd490edc2d4de300efd80fe3f3bbb1681`。
- 独立读取实际7524×1254 RGB打包行，并逐cell与原1254×1254源图数组比较，六块全部逐像素相等。原行 SHA `c85246148f129734d327a2cc331dfd3a9ee9e725aff3c374d0e57110c6a6a3b3`。没有把六张旧curated416高图重新当raw。
- `frames/frames-manifest.json` 的 actual shared ratio精确为 `416/1043 = 0.39884947267497606`，source最大范围657×1043，`per_frame_scale_normalization=false`。六frame实际组件尺寸与本次只读原稿测量一致；curated逐份与对应native frames文件字节相同。
- 六帧实际alpha高度为 **416/407/411/410/408/413**，保留原稿不同姿态/尺寸变化，没有再次全部归一化成416。整数输出尺寸有正常round量化，不将其描述为逐帧尺寸拟合。
- native frames QA与atlas QA均0 errors/0 warnings；全部edge/chroma-adjacent计数0，3072×512 atlas含精确六cell。该QA仅证明提取结构，不是motion gate。
- manifest真实时序为83ms×6、loop=true。仅读取GIF元数据见6帧各80ms，这是GIF百分之一秒量化预览，未播放，也不能代替引擎83ms时序或宣称有人看过loop。

## 实际六帧静态衔接

在当前contact与512帧中，近/远髋遮挡及支撑/摆靴角色仍与原合同相容，没有重现失败整行中1/4同一条腿支撑的问题。手套、钟盔、衣靴身份连续，没有额外手臂/腿、整图镜像或装备变化。单帧结构可继续试验，仍不足以据此判断连续走路。

| 相邻段 | 当前静帧观察 | 连续播放需验证 |
| --- | --- | --- |
| 0→1 | 近侧前伸靴收至身体下，far靴清楚离地；头/上身在passing图偏低一些。 | 落脚到支撑是否滑动或突然收腿；合同的轻微上升轨迹尚未由静态确认。 |
| 1→2 | 近臂从侧下中位切到横胸前摆，far腿前伸，near腿向后趾。 | 大手的明显位移会否在12Hz下像快切，能否连续追踪肘/股而非仅看到两张姿态。 |
| 2→3 | 近臂维持前摆峰值附近；前far跟由悬空接收重量，near后趾仍可辨。 | 峰值邻接是否自然接触，还是形成一快一停；前靴角度/鞋底形状变化是否过大。 |
| 3→4 | 支撑换至far，near股/膝前经过；近手回到侧下中位。 | 与1→2相似的大手位移、两半周期不同摆靴幅度是否读成不对称跛行。 |
| 4→5 | near摆靴向右前伸，far后趾留下支撑；前跟间隙小。 | 小比例下悬空是否消失、far膝/后靴是否被误读为腿身份跳换。 |
| 5→0 | near前跟需要落到0接触位，近手都在后侧；衣靴/头部的微小绘制差异可见。 | 原底边registration下头部有横向回跳；鞋跟落地、暖色/纹理/眼形与轮廓重置是否仍明显。 |

5→0的摆臂方向不是逆转或错相；主要问题是几何/位置的连续性仍待动态判断。当前5的盔面略暖、部分袖口/手套/鞋头线形不同于0，这些原稿变化不会被机械X对齐修掉。所有靴底判断仍只是可见轮廓，未锁定任何解剖/双足根或stride。

## bbox-center 横移的直接证据

对当前curated同一色域作只读观测：alpha>=128、y<260、R>80、G>65、R-G>10、G-B>7，取得盔tan core bbox中心X。它不含黑外轮廓，也不是anatomical root；与此前同方法原稿相比，足以判断放置策略是否额外平移。

| frame | 当前alpha bbox | 当前pasteXY | 当前盔core中心X | 原稿全bbox左X |
| --- | --- | --- | ---: | ---: |
| 0 | [125,48,387,464] | [125,48] | 260.5 | 291 |
| 1 | [149,57,362,464] | [149,57] | 257.5 | 358 |
| 2 | [128,53,384,464] | [128,53] | 248 | 329 |
| 3 | [133,54,379,464] | [133,54] | 252 | 332 |
| 4 | [152,56,359,464] | [152,56] | 252 | 378 |
| 5 | [130,51,382,464] | [130,51] | 252 | 320 |

当前盔core中心跨度 **12.5px/512**；原稿对应中心约630/629.5/629/630/629.5/626，仅约4px/1254跨度。当前额外横移主要来自手脚改变全bbox中心，而wrapper把每张component crop独立居中。比如1→2头中心左移9.5px，5→0右跳8.5px；在88.615画布显示约1.64/1.47px。该幅度已是当前实际提取位置，不再只是拼接前估计。

## v006 可以采用的单变量机械对照

可以保留原1254-cell横坐标。每帧都使用同一个映射：

`targetX = 256 + (416/1043) * (rawLocalX - 627)`

即原cell中心627统一映射到输出256，固定offset=`5.9213806327900045`。这是源画布坐标登记，不依据每帧头、脚、bbox中心或人工视觉稳定点追踪；也不宣称627是解剖root。实际crop左X经过此映射再统一round，保留当前shared比例及同一resample方法，其他变量不动。

| frame | v006候选pasteX | 对v005 X差 | 候选盔core中心X（只加上述整数平移） |
| --- | ---: | ---: | ---: |
| 0 | 122 | −3 | 257.5 |
| 1 | 149 | 0 | 257.5 |
| 2 | 137 | +9 | 257 |
| 3 | 138 | +5 | 257 |
| 4 | 157 | +5 | 257 |
| 5 | 134 | +4 | 256 |

按现有实际resampled尺寸，六张候选左右边均在48–464 safe范围内，不需要新缩放或裁切。候选头中心跨度约1.5px，是对同一提取结果进行位置量级预测，**尚未生成/提取/实际观看v006**；不把预测当结果。

为保持可归因，应只改X登记，保留当前bottom Y、六相顺序、83ms时序、原图与key/alpha流程；新run明确写新的registration policy，不能仍标成bbox-center。记录每帧原cell范围、native keyed component在原cell的bbox、shared ratio、整数round、target placement、source/component/output SHA。当前v005记录有尺寸但缺原component位置信息；下一版应从同次native key/组件坐标取真实bbox，不把本报告的近似颜色分类当正式提取receipt。原cell crop还应与native组件hash/数量对应，防止串帧或把相邻cell边缘纳入来源。

这一对照保留原画布已有横向漂移，能去掉提取额外引入的居中漂移；它不能消除原始盔形/上身比例差、摆臂快切、纵向体重轨迹、两半周期抬靴差、脚滑或接缝。若v006仍有这些问题，需按真实播放结果判定，不要继续靠逐帧定位/重时序/改标签把动作稳定成通过。

## 冻结依据与验收边界

| 文件 | SHA256 |
| --- | --- |
| sprite-request.json | 9f33e88fa89a4d46d4acccde72f71bdac1f241e9dca882b77006a975d47ca3e2 |
| frames/frames-manifest.json | e51e7a9a9f10eaf378655423c6bb5b94a8631ab38d7b3aff9d2ab9680350805e |
| manifest.json | e62c6df0b4473224ba04c32c46eb8ecf0da3ca546a3ff931245793939b9fcf02 |
| sprite-sheet-alpha.report.json | 005c51056b470d12d90bb412681cb8943931cba11c9e76587058011096a89b3c |
| qa/walk-contact.png（实际已看） | 7cca62c3163710e4c367d5b1866ac31fd007af5932787b82a50d5ecb035346ef |
| qa/walk.gif（只读元数据，未播放） | d580b45fa79137ae1fafa9f7f58d3b4b8d5308f4caac06743a28f9643c3e6cb6 |

保留v005及其所有raw/run/manifest，不覆盖旧源计划或旧审查。依据sprite-gen motion QA，完整循环、5→0接缝、脚接触/方向/速度、人体关节连续性必须实际播放再判。当前只有静态序列审查，不是motion通过、sprite正式完成、UE运行、左向适配或用户终批；完整内容目标仍0/15。
