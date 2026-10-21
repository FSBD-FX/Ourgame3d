# Common Hero 六帧 Walk：生成前设计 v002

状态：**仅数字合同、布局 guide、提示词已准备；尚未生成 walk raw，未提取、未进 UE、未通过 motion/art gate。** walk 为 sprite-gen 标注的 experimental locomotion。没有生成或改绘最终人物像素，也没有修改旧 idle、Source 或 ledger。

唯一身份基准是 [idle v002 curated frame-0](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png)，512×512 RGBA，SHA-256 `f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718`，实读 alpha bbox `[146,48,367,464]`、高度416。本轮已实际 view 此帧。它是已确认的技术身份锚点，不能借此宣称用户最终批准画风或 walk 动作。

本 run 的 `base-source.png` 是该 curated 单帧的**逐字节副本**；这里的文件名来自 prepare 工具，内容不是旧129 base。后续 native 仅附此单帧和 `references/layout-guides/walk.png`，不重新附129、整条 idle、概念场景或单张峰值 walk 姿态。单峰值会诱导六格重复同一条腿的接触相。

## 合同和生成入口

- 数字制作请求：[walk-request-spec-v002.json](F:/Ourgame/source-assets/production/fairytale-hero-v001/walk-request-spec-v002.json)。
- 姿态/身份来源/步幅与风险记录：[numeric-walk-request-v002.json](F:/Ourgame/source-assets/production/fairytale-hero-v001/numeric-walk-request-v002.json)。
- 实际 pipeline 请求：本 run `sprite-request.json`；实际 native prompt 必须读取本 run `prompts/walk.txt`，不能另外手抄帧数和动作要求。
- 固定6格、512×512、每边48安全边距，guide为3072×512。guide是 sprite-gen 确定性技术布局，不是人物资产。
- 单右向3/4视角，native facing=+1；左向计划运行时镜像，不另外生一条左 walk。不改变锚点的钟盔、眼睛、深灰便服和棕色手套/靴子。空手、无盔甲、无披风、无装备。
- 默认 components 分割，RGB绿色 `#00FF00` chroma，`pixel_unfake=false`。这是手绘HD风格，不伪装成像素画。`lanczos/bbox-center/bottom/shared_row_scale=true` 是显式确定性提取合同；没有 slot fallback。必须使用 project-only shared wrapper，不能用默认逐pose fit 替代。

prepare 工具会明确丢弃传入顶层 `chroma`；本次已在新 run 请求中补入同一份 `rgb/unmix_reach=4/spill_max_fraction=.005` 合同。未修改 skill 工具或旧 run。六帧不受该 skill 的八帧 motion-phase-stick guide 特性支持，因此此 guide只负责六槽/边距，六个相位的责任由数字合同及自动生成 action prompt 承担；不能把空布局格说成已经画出行走动作。

## 六个不同步态相位

near/far 指当前视角的近侧/远侧肢体；不要中途交换肢体身份。整个人保持朝右，手臂与同侧腿反相摆动。

| 源索引 | 相位 | 落足/摆动责任 |
| --- | --- | --- |
| 0 | 近足前接触 | 近脚前方脚跟接地、远脚后方脚尖离地前支撑；近臂后、远臂前。 |
| 1 | 近足承重、远足通过 | 近足掌承重向身后相对移动，远膝弯曲从髋下向前通过，远靴离地。 |
| 2 | 近足后蹬、远足前伸 | 近足后方脚尖支撑/脚跟抬起；远脚前伸准备下一落足，不能两脚都飞起。 |
| 3 | 远足前接触 | 与0相反的腿负责前脚跟接触；近脚在后脚尖支撑，近臂前、远臂后。不是把整个人翻面。 |
| 4 | 远足承重、近足通过 | 远足掌承重，近膝弯曲向前通过，近靴离地；与1相反的支撑腿。 |
| 5 | 远足后蹬、近足前伸 | 远脚后方脚尖支撑，近脚前伸进入下一0的脚跟接触；5→0不得重置、瞬移或多补一个idle格。 |

钟盔保持同一金属刚体形状：高度、宽度、帽顶、铆钉、面罩开口和两眼形状不变。可随躯干整体小幅上下移动，设计上限约6源像素；该值是设计容限，不是已有帧测量。主要运动来自髋、膝、踝、足接触和反相手臂，不能把静态人物平移/上下晃动作为 walk 成功。

## 根点、尺寸和提取风险

`[256,464]` 仅为512画布中的预期骨盆地面投影与落足基线，**不是已生成 walk 的实测 root**。真正的6个 root、支撑/摆动足接触点、头盔 bbox、身体高度和 limb landmark 全部待 raw→components→curated 后量测。

步态的支撑足会交换，不能把每帧最低20%alpha的重心直接当固定角色骨盆根点；否则抬脚/前后伸腿会让整个人横向晃动。本次先选 bbox-center 进行普通确定性放置，之后必须检查骨盆/腰带中心与脚线。bbox-center也不等于天然稳定 root，手臂外伸可能改变 bbox；应记录真实根点供运行时使用，而非重新绘像素。

v002解决的是旧普通 `fit_to_cell` 按每pose完整bbox单独缩放造成的几何变形风险：本新合同要求整条row计算一次固定ratio，再对所有native keyed components使用同一个ratio，保持腿/手/头盔之间原有相对尺寸。此变化不生成、不重绘原稿，也不调整帧时间。它仍不能修复原画中的头盔软变或解剖错误；此类问题须重生该行。最终仍使用固定显示Canvas，不逐帧缩放。

现 idle 的固定显示画布为 `72×512/416 = 88.61538461538461`。walk目标保持同一角色视觉尺度，不能仅用每帧全身bbox高强行归一成72px；弯膝/步态本来可以改变身高。是否可以沿用同一固定Canvas，需实际比较头盔尺寸和全身比例后再锁定。

左向镜像需使用 `flip = desiredFacing != nativeFacing`，横根点转换为 `512-rootX`，不直接套旧剑/弩的 socket 或 eye 补丁。左右的支撑足/手臂都须观看，镜像技术通过不等于两种方向动作已验收。

## 步幅与未来实际移动时钟

源码只读依据：`F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:573` 的普通无甲基础速度为265 world/s；装备绑定时读 `Stats.MoveSpeed`。`F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonEquipmentStats.h:355` 计算 `265×IdleMoveMultiplier×MovementConstraint`；不能把带甲/附魔后的速度都固定为265。碰撞、墙/身体裁剪会在 `DungeonFighter.cpp:624` 之后缩短实际位移。

本行设12fps，compose预期产生83ms×6=498ms。设计名义步幅为 **132 world/cycle、22 world/phase**；265基础速度对应周期约.498113s、相位速率约12.04545fps，和83ms预览接近。按当前水平投影.65，名义全周期地面前进85.8显示像素；每相位约14.3像素。132只是生成前的节奏初值，不能作为已经测得的脚步步幅。

未来游戏 walk phase 推荐由“实际解析后平面位移累计/已量测步幅”推进，使用真实 `GetGroundPosition()` 差值或等价已接受运动记录，不使用相机移动、按键保持时间、请求但被墙阻挡的位移或现idle lookdev wallclock。这样停下/堵墙/暂停时不会继续踏步，装备改变速度时也能保持位移与步频关系。本轮没有改接 GameMode；现新idle lookdev仍固定位置、冻结游戏时钟。

新 raw 通过逐帧/循环审查后，还需在固定相机的实际移动实录中量测同一只脚的接触区间及姿态切换，比较其世界落足漂移。接触由脚跟→足掌→脚尖滚动时不能把不同接触点误算成同一个钉死地面点。六帧本身是稀疏采样，连续移动期间每个持帧会有步进/滑动风险；不能宣称精确脚底锁定已经解决。

GIF以厘秒存时间，83ms可能显示为80ms。GIF只供动态观感复核；实际UE使用 manifest durations/位移时钟，不能根据GIF估计引擎已按83ms采样。若循环姿态本身不成立则重生整条 walk，不通过本地GIF重定时掩盖断接。

## 下一步门与未覆盖边界

root是唯一 native 图像生成者；生成前使用本 run 的单帧身份副本+六槽guide，prompt读取 `prompts/walk.txt`。本准备者不调用图像工具，也没有为尚不存在的 raw、六帧或atlas编造SHA。新图和展示副本仍须由root完成F/E保全再展示。

生成后必须按components提取、curated/atlas输出合同处理。自动检查需覆盖6帧、非空、边缘/绿边、尺寸，逐帧确认近/远腿和手肘、膝/踝/手指没有多/少/长短突变，钟盔没有再短缩。实际播放多个0→5→0循环、双向/实际72px大小及移动地面上的步频，并交独立复核。没有真实播放则 `motion gate=pending`，联系图/自动报告不能替代。

这条只做空手 common body。武器、防具分层、far/near遮挡、武器socket，以及起步/停止/急转/受击/攻击/跳跃等衔接均未完成。尤其停止在六个不同相位、撞墙和反向时的idle接续须另审；不能因已有新walk就恢复旧身份的攻击或声称完整制作完成。纯Y纵深移动也不是新的front/back方向行走已完成。

## v002提取扩展与v001留存

v001全部保留；v002身份单帧、guide、六相action和12fps语义不变，只添加 `fit.shared_row_scale=true` 并指定 project-only wrapper `F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py`（冻结SHA `31a4e3f10f4b0bbf3e9dd51c591e860c5c23f0cfa342cc0a86a498cd7de2b3bb`）。该wrapper复用SHA-pinned native色键/组件/QA，行scale由所有组件最大宽/高共同计算；bbox-center/bottom只是放置，不能冒充真实人体/脚底根。root仍须量每帧root与接触点。

后续root唯一提取命令（本准备者未运行）：

```powershell
& C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe -X utf8 -B F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py --run-dir F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v002
```
