# 公共身体与四帧 idle 独立静态复核 v001

2026-10-15。按 `C:/Users/22499/.codex/skills/sprite-gen/SKILL.md` 及 `docs/qa-motion.md` 复核。本审阅实际查看了129公共身体原件、完整idle contact，并另逐张查看 curated/frame-0.png 至 frame-3.png 的512原图。没有生成、修改、缩放、裁切图片，没有改 Source、ledger 或 run/归档索引，未启动 UE/UBT。

Motion标准明确要求“Review motion as motion”，且 loop最后一帧须自然接回第一帧。**本审阅没有真实播放GIF**；读取GIF帧数/时长不算观看循环。因此以下是独立逐帧第二意见，motion gate保持待定，不能称已通过 sprite-gen 或完整idle动作验收。

## 输入与技术证据

原始目录 `F:/Ourgame/source-assets/production/fairytale-hero-v001/`；run为其 `sprite-run-idle-v001`。root已报告129原件F/E v044、130 raw v045、确定性提取/atlas/curated/qa v046完成保全；本审阅在保全后看F原件，没有重新核整个E批。

| 对象 | 本轮重新读取 SHA256 |
| --- | --- |
| raw/129-common-body-idle-base-v001.png | f754ee39487ab6998231b3d80c52c232d5ec4fb8f9f04cceecc49cab797f15ca |
| run/qa/idle-contact.png | 95bfd2131f2563c2b105ed73978df3d9943cb224ff2f6ddcd7c18ab685cfa39f |
| run/qa/idle.gif | 3b842cff1daec4562dc5ec43feedf035211e229d5eef01005c53da63ddaa58b8 |
| curated/frame-0.png | b85d7360b4d6a62c3e347c94fa58f8b339eb1d99052ddd2a666653d61834a7c0 |
| curated/frame-1.png | b933d30012614f910b8de95dd121fbc35451ff7cc082ddefb52a61752add1573 |
| curated/frame-2.png | 15b2a6fe701beb081db581958e3e6130cf7ad3a68ebc792674eaae0b4a06c45f |
| curated/frame-3.png | 39fb47a3aee5e35fe7e19677d5a5714378225044d0b92da316d694c36b4002ee |

contact原尺寸2068×520，工具显示时轻微缩至2048×515，故本审阅补看全部4张原512图，没有只扫缩略图。提取报告实际ok=true、4frames、method=components、errors/warnings空；atlas报告ok=true、4个512单元、2048×512、无errors。四帧提取bbox顶部48、底部464，edge/chroma-adjacent报告均0。它们证明结构/提取，不证明头盔刚性或运动连贯。

request为非pixel_unfake、lanczos、foot-centroid/bottom、ground_frames=true，idle4、fps6、loop=true。manifest时长为167ms×4；只读GIF结构为4帧、160ms×4、无限loop。GIF的厘秒时长量化与runtime manifest有区别，不能用GIF预览时长替代manifest时序。manifest的frame_variant标签为pixel也不代表该手绘角色已变成像素美术。

## 公共身体129

129保持钟盔、琥珀双眼、短身、棕色手套和靴的身份；头到脚完整，朝右三分侧视，躯干为深灰全覆盖内衬，没有胸甲、护肩、披风或武器。作为本轮公共身体身份基准具备明确可用性。root在base-lock-review-v001.md记录的技术门y可理解为继续试制的技术选择，不能扩大成用户终批。

该图仍是单张原始基准，不含公共身体前后分层、武器握点、四甲变装或攻击动作。原件绿色背景是去键输入，不能直接当透明游戏资源。

## 四帧实际静态判断

| 帧 | 身份与手肢 | 呼吸/刚性风险 |
| --- | --- | --- |
| 0 | 钟盔/双眼/深灰内衬/腰带/手套靴一致；双臂双腿完整，空手轮廓清楚。 | 可作此行静态对照姿势。 |
| 1 | 同一身份，无明显增肢、缺肢或断开的手腕/膝。胸腹更鼓、肩手位置上提可见。 | 头盔下沿及眼窗相较0/2/3上提，盔形显得更短、更窄，但盔顶仍近似同高度；有刚性盔体变形或逐帧拟合改变尺寸的风险，不能仅以“在呼吸”消除疑点。 |
| 2 | 衣料、腰带和两手两脚保持一致，身体回近初始状态。 | 盔形回近0；从1返回时是否出现明显跳变须真实播放确认。 |
| 3 | 身份稳定，无明显肢体拓扑破坏，空手与靴形可读。 | 静态外形接近0，具备接回起点的可能，但不等于已经证实4→1循环平滑。 |

胸腹及手臂确有变化，四图不是完全相同的静图复制或整体平移；这仍不足以证明在6fps播放时能读作自然呼吸，也不足以排除只是在抖动。尤其帧1的头盔变化需要作为真实循环审阅的重点。人体关节没有本轮静态可明确判定的严重解剖破坏，但手套遮住手指，不推断每个关节和握持将来都正确。

## 脚底只读辅助测量

在最终curated图的固定ROI y=440..479、alpha≥128，左右各以x256分界读取外框，没有重画或对齐图片：

| 帧 | 左靴ROI bbox | 右靴ROI bbox |
| --- | --- | --- |
| 0 | [162,440,232,464] | [265,440,357,461] |
| 1 | [163,440,232,464] | [264,440,355,461] |
| 2 | [162,440,231,464] | [264,440,356,461] |
| 3 | [162,440,232,464] | [264,440,357,461] |

左右靴分别保持自己的底线，近/远靴底线相差3px且四帧一致，不能误判为一帧突然抬脚。横向外框仍有约1–2px差异；固定ROI外框不是足骨锚点或足底接触追踪，不能据此宣布脚锁或运行中零抖动。技术提取的bottom对齐也会令底线看起来稳定，故需结合真实循环和运行落地检查。

## 本轮结论与下一步

- 公共身体身份：静态可用候选；尚未用户批准。
- 四帧身份/人体拓扑：静态检查未见严重破坏。
- 足底：静态底线稳定，细微横向变化未构成脚锁验收。
- 头盔刚性：帧1存在需要复核的明显变化，不建议忽略。
- 4→1循环/呼吸连贯/是否静态抖动：**待定，未真实播放GIF**。
- sprite-gen motion gate、UE接入、武器甲胄适配及正式单元：未完成。

下一步应以当前实际GIF反复观看帧1前后和4→1衔接，并记录每state motion verdict。若实际循环确认盔体squash、jitter或接缝跳变，应按qa-motion标准重新生成该idle行，不能本地画改、强行重定时或删掉疑点后仍宣称原四帧动作通过。当前静态第二意见不能替代该动态门。
