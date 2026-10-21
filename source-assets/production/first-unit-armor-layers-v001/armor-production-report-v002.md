# 圆盔角色真实甲层生产记录 v002

2026-10-15，单一视觉写入者 `/root/assets_prepare`。此版追加说明，不覆盖已留档的 v001。规范源为 `F:/Ourgame`，原生后端为 `image_gen.imagegen`；外部 API 调用 0，内置费用未知。

唯一账为 `F:/Ourgame/source-assets/production/first-unit-animation-v003/generation-ledger.json`。EV039 后累计 **71请求**，此前 EV038 另24，历史累计95。窗口3仍为 **23/24，余1**，尚未结束或重置。P2/P3袖层修订新增生成调用 **0**。本次核对窗口49–71的23原件、92份F/E原件及展示副本、23份工具C盘原件，SHA全部一致。证据为 `reviews/armor-production-source-checkpoint-v002.json`。

## 已冻结候选合同

| 合同 | 实际512 RGBA纹理范围 | SHA256 |
|---|---|---|
| `manifests/import-armor-idle-v001.json` | 60：共同far/near12，四甲front/back48 | `f0cd3c72a1fe0b7ac3ad7416ddde44a0f89dd6f0d5ddc25320aec3c184769ab3` |
| `manifests/import-armor-primary1-four-v002.json` | 36：共同body12，四甲front24；相对轻甲旧合同仅新增18 | `6369db09edb37e08256ef2fe22763846adb2802efc4ea8bdf8ad30a4a8b8ca70` |
| `manifests/import-armor-walk-four-v001.json` | 36：共同body12，四甲front24 | `fd02fa5de2eb23efba31a0c60167bcaf7482a91666959caf2001949fffae3e58` |
| `manifests/import-armor-primary2-four-v001.json` | 36：旧partial；原件和合同保留 | `1372c8ea3cb5a113dc9e8315a7b5cf51ebafe50359d96d42878a3c70891fa46e` |
| `manifests/import-armor-primary3-four-v001.json` | 36：旧partial；原件和合同保留 | `e97f2958f624e8d27c0942931e48a293c5bee6b33ebfd42148956dfd3f288497` |
| `manifests/import-armor-primary2-four-sleeves-v002.json` | 42：新共同body12、ROB front/near12、复用其他三甲front18；本版本新增24 | `04d9dce4c7d1aff12bea9873681c9e759e9032544ca37c7abd33f01939fbb225` |
| `manifests/import-armor-primary3-four-sleeves-v002.json` | 42：新共同body12、ROB front/near12、复用其他三甲front18；本版本新增24 | `3f1dc1ea892ea82535263f0ad170a39cee62af3d892e422dd2628f99b6db4c5c` |

最新五个clip合同引用 **216条独特身体/甲PNG路径**；包含保留的旧P2/P3版本时共252。这个计数排除军剑、raw整图、诊断图、mask和其他动作源；新分区不是新动作，不将历史版本叠加成更多可用帧。五个clip为idle、walk、P1、P2、P3，各六姿势；四甲共120个衣装姿势样本，仍是候选表面，不是四套全状态成品。

## 袖层修订的事实与接口

旧共同 `body_near` 的宽选区在若干姿势包含较长前臂，顶层会把原金色上臂盖回已有灰袖。P2新版将共同整身重新分为far与真实distal拳/短腕near：两层重构后的RGBA与旧共同整身**逐字节一致**，没有改人物姿势、握点、脚根、缩放或全局平移。P3也作同样重新分区；其共同底臂仍来自原native67来源，不冒称都是旧人物原始前臂。

ROB袖片仅选择原生66/P2与71/P3同坐标的实际灰袖、袖口和蓝灰布腕像素。可见RGBA与来源逐字节一致，front与near不重叠；没有画皮肤、补造隐藏袖子、重画手或局部缩放。P2通过手区、实际衣袖轮廓与领口桥修订，解除金色上臂顶层冲突。旧多边形的head/belt区域包含少量真实衣装，因此本次单独记录实际拳/短腕选区和衣装来源，不把宽多边形等同于精确解剖边界。

新版绘序必须显式为：

`body_far → armor_front → 独立Sword → armor_near → body_near`

ROB六帧的 `armor_near` 均必需；缺层时应拒绝/停用该新版外观，不能静默丢弃后声称长袖已显示。其他三甲此槽为明确null，保留原partial front。`armor_back`仍为null，无隐藏后背像素不造空文件冒充。无需修改旧v2四层验证器；新合同为独立v2近袖轨道合同。左右方向仍先组装右向，围绕共同root镜像一次。

P2阶段 `.15/.12/.27`，P3 `.22/.12/.32`，各2/2/2帧，沿用旧绝对时轴；Sword比例 `.4`、原握点/角度不变。六帧每帧root、grip、手层bbox、真实alpha和hash在合同中逐项提供。

## 真实来源缺口与审查范围

- P2源pose0本身有袖口到布腕间的小裸肤缝，未补造布料。P3源在多个姿势有更明显裸肤段，尤其抬手pose1；它不存在完整覆腕长袖，**P3新合同不宣称全覆盖长袖**。这属于源素材衣装形状缺口，未来若纠正须制作新来源，不能靠选区伪造。
- P2早期袖选区v001–v006及P3早期partial均保留。v003旧腕区过宽，v004过宽手包络曾选中手后袍摆，v005仍被旧near和宽腰区盖回；v006收紧共同near，v007补实际来源领口桥。全部纠正只改选区及层顺序，不追加生成。
- 袖修订各核验42实PNG、168份F/E副本、真实alpha/角点/hash，0错误。四甲各六帧右向与一次镜像左向，共八张静态组装图已逐张查看。该审查证明候选可供接线，不证明动作衔接、全20搭配、命中可读性或运行无穿插。
- walk六帧继续沿原belt proxy根。伸步帧支撑不明确、bob不足的限制不变，不新增footlock或无滑步结论。
- idle、P1、walk的旧合同仍为保守partial；P2/P3的新袖轨道也没有使所有甲层完整。jump/fall/land、dodge、hurt、death、secondary、air-primary和装备交互等适用状态仍待共同body与四甲真表面制作。
- 原74张圆盔身体、80逻辑marker、旧源/冻结合同未覆盖。没有整身角色伪装成甲层，没有把整衣variant冒作语义分离层。

## 留档与引擎边界

本次源、处理、mask、合同、静态审阅图及失败版本均在 `source-assets/production/first-unit-armor-layers-v001/`。F/E主题分别为 `F:/Ourgame/过程图稿与视频/2026-10-15_圆盔四甲组件路线_v001` 与 `E:/OurGame/Knight/过程图稿与视频/2026-10-15_圆盔四甲组件路线_v001`；每次view前已留四份并维护index。保留C盘工具原件。

本写入者没有启动UE、UBT或修改Actor/HUD/工程。主线程已报告旧partial P2/P3实际36/36导入和双向三段连招运行录像；其证据归旧合同，不倒填新袖层。新袖层等待独立版本/flag接入ArmorNear后实机检查。所有合同仍标 `runtime_verified=false`、`complete_armor=false`，当前仅为静态源候选交付。
