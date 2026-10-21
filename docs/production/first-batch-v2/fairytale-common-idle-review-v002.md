# 公共身体重生 idle v002 独立逐帧复核

2026-10-15。此次审阅实际 `view_image` 查看 request131 的完整 raw/idle.png 与新 curated/frame-0.png 至 frame-3.png 四张512原图，并与本审阅先前实看的v001作对照。只新增本文；未修改旧报告、Source、图片、run、ledger或旧媒体索引，未启动UE/UBT。

依据仍为 `C:/Users/22499/.codex/skills/sprite-gen/docs/qa-motion.md`。**未真实播放GIF**，因此本文只给逐帧二审，motion gate仍待定，不能宣称循环或idle动作验收已完成。

run：`F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002`。root报告131原件/guide/提示词F/E v047保全9文件，新提取/atlas/curated/qa v048保全24文件、5,973,374字节，两遍大小/SHA零差；本审阅未重新核整个E批。

## 实际可见变化

v002延续129公共身体的钟盔、双琥珀眼、深灰全覆盖内衬、棕色手套靴与腰带，四张身份一致。raw为四个完整独立姿态的横行，未见切头、缺脚、外加装备或场景；查看raw时工具将2172×724轻微缩为2048×683，故人体细节以另看的四张原512图为主。

| 帧 | 逐帧判断 |
| --- | --- |
| 0 | 空手闲置姿态完整；盔、肩、肘、手腕与双腿轮廓连贯，可作本行对照。 |
| 1 | 胸腹小幅鼓起、肩手略动可见；相较v001的第二帧，头盔短缩、眼窗突然上提的现象明显减轻，盔体整体更接近其余三张。仍有细小轮廓/位置变化，本文没有做刚体配准，不能宣称逐像素刚性一致。 |
| 2 | 体态回落，头盔与0接近；两臂两腿完整，手套形状未见明显增指/断腕。 |
| 3 | 身份和四肢保持稳定，外形接近起点；具备接回0的静态条件，但尚未真实确认4→1循环接缝。 |

没有发现v001第二帧同程度的盔形突变，静态质量有实质改善。本行确有胸腹与肩手变化，不是四张完全相同图的整体平移。变化也较克制：只有逐帧对照不能判断它在6fps下是否成为自然呼吸，还是单帧脉冲或微抖；实际播放应重点看0→1→2及3→0。没有本轮静态可明确判定的严重解剖破坏，也不因此推断未来握剑、盔甲分层和所有动作均正确。

## 脚底辅助测量

只读固定ROI y=440..479、alpha≥128，以x256分左右，bbox采用左上inclusive/右下exclusive：

| 帧 | 左靴ROI bbox | 右靴ROI bbox |
| --- | --- | --- |
| 0 | [167,440,235,464] | [264,440,355,460] |
| 1 | [169,440,237,464] | [265,440,354,460] |
| 2 | [167,440,235,464] | [264,440,354,460] |
| 3 | [167,440,235,464] | [264,440,354,460] |

各自底线四帧稳定，远近靴4px高度差是持续的透视关系，没有一帧突然跳起。第二帧左靴ROI整体约向右2px，其他水平外框约1–2px变化。bottom/foot-centroid提取对齐本身也有助于此结果，固定ROI不能当足骨锚点追踪；脚锁与UE运行中的亚像素抖动仍未验收。

## 技术结果与边界

读取的frames-manifest实际ok=true、method=components、4frames、errors/warnings均空，每帧edge/chroma-adjacent报告0；atlas报告ok=true、4个512单元、2048×512，无errors。curated导出确有四张。技术绿不代替人体刚性或motion门。

只读GIF结构为4帧、160ms各帧、无限loop；manifest依旧6fps、durations_ms=[167,167,167,167]。这里只核结构，未动态播放；GIF厘秒量化时长不能作为最终runtime时序依据。

| 新文件 | 本轮重新计算SHA256 |
| --- | --- |
| raw/idle.png | 740a2d5fba74670cf3fa11389c62e968e2a91e81d3e078459df48ab32a4995b1 |
| curated/frame-0.png | f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718 |
| curated/frame-1.png | 7bedc3d428f8b1e008d0627d671660b0fd3a68c61c6593872e800d0f19e395a3 |
| curated/frame-2.png | 5d3d6c88289f2aa6347c98869082e551ed2918a86725376af75fbd698f412bbb |
| curated/frame-3.png | c27bfb46301397c627f7346a8890a84358ad1e0465f9fa3cc238e8600cedfe4c |
| qa/idle-contact.png | d720eca9b34139616e6c7d7d6a0f411304ce8e628d3f4fd7bb3e5009edc985ad |
| qa/idle.gif | 0f5154c9af0447b3f92f3ae3b620597106157d43d8f9589f9185da26dab9f420 |
| manifest.json | 8a2e082077c75581064fd014b0b229d6f00e7f14ecb4eaa0238f1ff68932e3e3 |

结论：v002的静态身份、手肢和头盔一致性比v001更适合继续动态复核，尤其旧第二帧的问题已有改善。尚未真实播放GIF，不能将此结论写成motion通过、sprite-gen完成、已导入UE或用户终批。下一步须按qa-motion真实观看循环并记录每state verdict；若仍出现刚体变形、抖动或接缝跳变，按标准重生该行，不通过本地画改或重定时掩盖。正式首批内容单元仍为0/15。
