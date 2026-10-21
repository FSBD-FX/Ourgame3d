# 首批装备与敌人音频预检 v1

核查日期：2026-10-14，Asia/Shanghai。范围：本地源文件、许可文本、整文件解码和数值波形检查。未试听、未生成或转换音频、未启动 Editor、未调用付费 API，未修改 UE 资产/代码/台账。**本文件不是 DONE-FEEDBACK 验收。**

## 事实、推理与风险

- 事实：205/205 OGG 完整解码，205 个原文件哈希均匹配 D12。181 个单独音效只有179个唯一哈希；另有23个音乐和1个合集预览。预览不作游戏单个音效。三份本地许可明确 CC0/允许商用，见下表。
- 推理：现有音效可作为布料、金属、石体、脚步与接触材料；不足以直接交付五武器、四甲、五敌和一Boss的完整声包。共列15单元、10武器动作、14敌招和全部40个D12共享事件候选，所有候选均待试听与派生剪辑。
- 风险：22个单独音效（加合集预览共23个文件）解码采样峰值≥0dBFS；不能直接等增益叠层。所有181个单独音效都是双声道，不能直接当作已验收空间单声道素材。波形数值不证明听感、响度标准或无缝循环。

## 解码与许可

解码器：`G:/UE_5.5/Engine/Binaries/ThirdParty/libsndfile/Win64/libsndfile-1.dll`，实际返回 `libsndfile-1.2.2`；通过既有 Python 的 ctypes 调用 sf_open / sf_readf_float 到内存，核对预期帧数、EOF、错误码和有限采样。未安装依赖；ffmpeg/ffprobe 不在 PATH，两个已查 Python 环境均无 soundfile 模块。DLL 可解码不代表新建了 UE SoundWave 或复核了打包播放。

| 来源 | 本地许可证据 | 当前边界 |
| --- | --- | --- |
| Impact Sounds | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/License.txt`；SHA256 `b49aa9c56b04528b95913de13e506a0f7c5e807b9925db9bfef86af1f91120db` | Kenney Impact Sounds (1.0) local package CC0; commercial use and optional attribution explicit |
| RPG Audio | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/License.txt`；SHA256 `5735dfd72cb64cbbceda4ebc00c380c41ca680edb82ff153aa7c9ab97614c539` | Kenney RPG Audio local package CC0; commercial use and optional attribution explicit |
| Abstraction Music | `source-assets/third-party/preparation-2026-10-10-v1/abstraction-music-loop-bundle-2026-q3/extracted/_LICENSE.txt`；SHA256 `d02e059adb401d50167b2e04d12ef9236fbcef0b4e3b7157bd5ebfab8a82b8f4` | Abstraction Music Loop Bundle local _LICENSE.txt CC0 includes contained music; does not cover all Patreon or website content |

## 数值发现与处理边界

- 音效采样率：130个44.1kHz、51个48kHz；单文件约0.106–1.741s。RMS跨度 -44.679 至 -11.6 dBFS，不能仅按峰值或文件名统一增益。
- `chop.ogg` +0.487 dBFS、`knifeSlice2.ogg` +0.633 dBFS、`metalLatch.ogg` +1.615 dBFS 为解码采样峰值。可能含有损编码超幅，不能由此断言原录音削波。未来派生副本先预衰减、再修边/混音；最终还需真实峰值与响度计及试听。
- `drawKnife1.ogg` 峰值−24.284、RMS−44.679 dBFS，明显比多数碰撞轻；应判断是否需要使用，避免为了它整体抬高总线。
- `dropLeather.ogg` 平均左右声道后 RMS 损失5.74dB，相关系数−0.468156；本轮未列为优先候选，后续需单独决定声道/重混方案。
- 77文件首采样、41文件尾采样绝对值超过0.01（约−40dBFS），仅触发起音/尾截/接缝复听；不是已证实爆音。保留瞬态，派生时用适当短淡化，不能盲裁至伤害窗口。
- 精确重复：`footstep_carpet_001/002.ogg` 与 `003/004.ogg` 各一组哈希相同；不能算四个不同take。
- 23音乐均为44.1kHz双声道，未确认任何分轨或环点。Week33 HUMAN RIGHTS 的 last→first 最大差0.369481，先复听接缝；差小也不等于无缝。当前REG01/Boss均不指派曲目。
- `sample_peak_dbfs`是采样峰值、`rms_dbfs`是全采样RMS；均非LUFS或dBTP。全部文件的帧数/时长/声道/哈希/风险见JSON。

## 候选材料库（项目根 F:/Ourgame）

下表每个路径均真实存在且完整解码。素材名只作为候选依据，**不代表已听到所需音色**。2–3个文件也不代表已通过take差异验收。

| 材料库 | 原始路径 |
| --- | --- |
| cloth | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth1.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth2.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth3.ogg` |
| draw | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife1.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife2.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife3.ogg` |
| swing_material_only | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/knifeSlice.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/knifeSlice2.ogg` |
| metal_light | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_light_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_light_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_light_002.ogg` |
| metal_heavy | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_heavy_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_heavy_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_heavy_002.ogg` |
| plate | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_heavy_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_heavy_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_heavy_002.ogg` |
| stone | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMining_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMining_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMining_002.ogg` |
| soft | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactSoft_medium_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactSoft_medium_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactSoft_medium_002.ogg` |
| wood | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactWood_heavy_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactWood_heavy_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactWood_heavy_002.ogg` |
| click | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalClick.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalLatch.ogg` |
| bell | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactBell_heavy_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactBell_heavy_001.ogg` |
| glass | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactGlass_light_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactGlass_light_001.ogg` |
| small | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactGeneric_light_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactGeneric_light_001.ogg` |
| coin | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleCoins.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleCoins2.ogg` |
| concrete | `source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/footstep_concrete_000.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/footstep_concrete_001.ogg`<br>`source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/footstep_concrete_002.ogg` |
| leather | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather2.ogg` |
| creak | `source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak1.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak2.ogg`<br>`source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak3.ogg` |

命中按 `contact_material_candidates` 选择单一主接触，石体/软体/金属/木体/机械/虚体分开；没有目标材质证据时，不因攻击者是石像就给玩家播石体命中。

## 逐单元与逐招候选

以下秒数来自未修饰的原始设计基础时轴，只用于选材长度预检。正式播放严格跟随已接纳动作的最终权威时轴及既有攻速/属性锁定规则，不能以这些固定秒数重新控制判定或硬播音频。

### WPN-SWD-001 尺衡军剑

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-WPN-PREP | drawKnife1.ogg, drawKnife2.ogg, drawKnife3.ogg | provisional_candidate；材料需按前摇剪辑；不得拉长原动作。 |
| AUD-WPN-SWING | knifeSlice.ogg, knifeSlice2.ogg | material_only_gap；未确认纯破风；完整0.57–0.60s切片不直接用于0.10s间隔三刺。 |
| AUD-DAMAGE-DIRECT | — | provisional_candidate；所有有效命中按contact_material_candidates选择一主声。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选静音。 |
| AUD-WEAPON-SWITCH | drawKnife1.ogg, drawKnife2.ogg, drawKnife3.ogg | provisional_candidate； |

| 动作 | 破风/释放起点（接纳后秒） | 前摇/有效/后摇（秒） |
| --- | --- | --- |
| 尺衡军剑主攻 | [0.17] | 0.17/0.12/0.31 |
| 进身斜斩 | [0.2] | 0.2/0.1/0.38 |

接触仍以真实有效伤害收据为准；一段挥动只有一个主破风，三刺按真实SubHitID分段，不能在低帧率补播未真实发生的旧事件。

### WPN-GSW-001 裂碑重剑

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-WPN-PREP | cloth1.ogg, cloth2.ogg, cloth3.ogg | provisional_candidate；材料需按前摇剪辑；不得拉长原动作。 |
| AUD-WPN-SWING | knifeSlice.ogg, knifeSlice2.ogg | material_only_gap；未确认纯破风；完整0.57–0.60s切片不直接用于0.10s间隔三刺。 |
| AUD-DAMAGE-DIRECT | — | provisional_candidate；所有有效命中按contact_material_candidates选择一主声。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选静音。 |
| AUD-WEAPON-SWITCH | drawKnife1.ogg, drawKnife2.ogg, drawKnife3.ogg | provisional_candidate； |

| 动作 | 破风/释放起点（接纳后秒） | 前摇/有效/后摇（秒） |
| --- | --- | --- |
| 裂碑重剑主攻 | [0.45] | 0.45/0.14/0.6 |
| 落碑重压 | [0.68] | 0.68/0.16/0.85 |

接触仍以真实有效伤害收据为准；一段挥动只有一个主破风，三刺按真实SubHitID分段，不能在低帧率补播未真实发生的旧事件。

### WPN-SPR-001 疾雨短枪

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-WPN-PREP | cloth1.ogg, cloth2.ogg, cloth3.ogg | provisional_candidate；材料需按前摇剪辑；不得拉长原动作。 |
| AUD-WPN-SWING | knifeSlice.ogg, knifeSlice2.ogg | material_only_gap；未确认纯破风；完整0.57–0.60s切片不直接用于0.10s间隔三刺。 |
| AUD-DAMAGE-DIRECT | — | provisional_candidate；所有有效命中按contact_material_candidates选择一主声。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选静音。 |
| AUD-WEAPON-SWITCH | handleSmallLeather.ogg, handleSmallLeather2.ogg | provisional_candidate； |

| 动作 | 破风/释放起点（接纳后秒） | 前摇/有效/后摇（秒） |
| --- | --- | --- |
| 疾雨短枪主攻 | [0.11] | 0.11/0.07/0.24 |
| 迅雷三刺 | [0.18, 0.28, 0.38] | 0.18/0.27/0.36 |

接触仍以真实有效伤害收据为准；一段挥动只有一个主破风，三刺按真实SubHitID分段，不能在低帧率补播未真实发生的旧事件。

### WPN-XBW-001 栓机猎弩

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-WPN-PREP | creak1.ogg, creak2.ogg, creak3.ogg | provisional_candidate；材料需按前摇剪辑；不得拉长原动作。 |
| AUD-DAMAGE-DIRECT | — | provisional_candidate；所有有效命中按contact_material_candidates选择一主声。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选静音。 |
| AUD-WEAPON-SWITCH | handleSmallLeather.ogg, handleSmallLeather2.ogg | provisional_candidate； |
| AUD-WPN-RELEASE | metalClick.ogg, metalLatch.ogg, impactGlass_light_000.ogg, impactGlass_light_001.ogg | material_only_gap；按弩/法杖实际释放分支；这里没有可信弩弦或火球成品，不把点击声标为已解决。 |
| AUD-WPN-EMPTY | metalClick.ogg | edit_then_audition；仅新合法请求因弹匣0被拒一次；完整文件0.446s，应试听/剪成短机械点。 |
| AUD-RELOAD-START | creak1.ogg, creak2.ogg, creak3.ogg, handleSmallLeather.ogg, handleSmallLeather2.ogg | material_only_gap；只能作拉杆/握持材料，不代表真正弩弦；一次实际装填起始。 |
| AUD-RELOAD-COMMIT | metalLatch.ogg | edit_then_audition；只在真实补弹提交；+1.615dBFS解码采样峰值必须先留增益余量。 |
| AUD-RELOAD-CANCEL | — | intentional_optional_silence；可选静音；若未来加止机短点须区别补弹完成。 |

| 动作 | 破风/释放起点（接纳后秒） | 前摇/有效/后摇（秒） |
| --- | --- | --- |
| 栓机猎弩主攻 | [0.16] | 0.16/0.04/0.48 |
| 贯甲弩矢 | [0.55] | 0.55/0.05/0.55 |

接触仍以真实有效伤害收据为准；一段挥动只有一个主破风，三刺按真实SubHitID分段，不能在低帧率补播未真实发生的旧事件。

### WPN-STF-001 余烬灯杖

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-WPN-PREP | cloth1.ogg, cloth2.ogg, cloth3.ogg | provisional_candidate；材料需按前摇剪辑；不得拉长原动作。 |
| AUD-DAMAGE-DIRECT | — | provisional_candidate；所有有效命中按contact_material_candidates选择一主声。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选静音。 |
| AUD-WEAPON-SWITCH | handleSmallLeather.ogg, handleSmallLeather2.ogg | provisional_candidate； |
| AUD-WPN-RELEASE | impactGlass_light_000.ogg, impactGlass_light_001.ogg, impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；主攻火球与技能一次地面火线需不同释放/消散；现成文件只是素材，未有火焰成品。 |
| AUD-FOCUS-LOW | — | missing；不足反馈缺口。 |
| AUD-DAMAGE-DOT | — | missing；仅技能真实燃烧tick；主攻火球不默认施加燃烧。 |

| 动作 | 破风/释放起点（接纳后秒） | 前摇/有效/后摇（秒） |
| --- | --- | --- |
| 余烬灯杖主攻 | [0.22] | 0.22/0.05/0.4 |
| 铺炭火线 | [0.45] | 0.45/0.12/0.45 |

接触仍以真实有效伤害收据为准；一段挥动只有一个主破风，三刺按真实SubHitID分段，不能在低帧率补播未真实发生的旧事件。

### ARM-LGT-001 行路短衣

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-INVENTORY-COMMIT | cloth1.ogg, cloth2.ogg, cloth3.ogg | provisional_candidate；只真实换装提交一次；不为常驻属性发循环技能声。 |
| AUD-DAMAGE-DIRECT | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | provisional_candidate；只真实有效受击材质，不能冒充格挡/反伤或新增减伤。 |
| 未定义展示钩子（不是新增AUD事件） | footstep_concrete_000.ogg, footstep_concrete_001.ogg, footstep_concrete_002.ogg | source_hook_definition_required；步点候选；40事件表未定义脚步钩子，须补实际落脚事件与速度/暂停约束后才能接入。 |

常驻特性保持静音；不增加轻步触发、板甲格挡、换袍回专注或新的恢复循环声。

### ARM-MED-001 巡路环甲

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-INVENTORY-COMMIT | impactMetal_light_000.ogg, impactMetal_light_001.ogg, impactMetal_light_002.ogg | provisional_candidate；只真实换装提交一次；不为常驻属性发循环技能声。 |
| AUD-DAMAGE-DIRECT | impactMetal_light_000.ogg, impactMetal_light_001.ogg, impactMetal_light_002.ogg | provisional_candidate；只真实有效受击材质，不能冒充格挡/反伤或新增减伤。 |
| 未定义展示钩子（不是新增AUD事件） | footstep_concrete_000.ogg, footstep_concrete_001.ogg, footstep_concrete_002.ogg | source_hook_definition_required；步点候选；40事件表未定义脚步钩子，须补实际落脚事件与速度/暂停约束后才能接入。 |

常驻特性保持静音；不增加轻步触发、板甲格挡、换袍回专注或新的恢复循环声。

### ARM-HVY-001 门栓板甲

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-INVENTORY-COMMIT | impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | provisional_candidate；只真实换装提交一次；不为常驻属性发循环技能声。 |
| AUD-DAMAGE-DIRECT | impactMetal_light_000.ogg, impactMetal_light_001.ogg, impactMetal_light_002.ogg | provisional_candidate；只真实有效受击材质，不能冒充格挡/反伤或新增减伤。 |
| 未定义展示钩子（不是新增AUD事件） | footstep_concrete_000.ogg, footstep_concrete_001.ogg, footstep_concrete_002.ogg | source_hook_definition_required；步点候选；40事件表未定义脚步钩子，须补实际落脚事件与速度/暂停约束后才能接入。 |

常驻特性保持静音；不增加轻步触发、板甲格挡、换袍回专注或新的恢复循环声。

### ARM-ROB-001 灰烛法袍

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-INVENTORY-COMMIT | cloth1.ogg, cloth2.ogg, cloth3.ogg | provisional_candidate；只真实换装提交一次；不为常驻属性发循环技能声。 |
| AUD-DAMAGE-DIRECT | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | provisional_candidate；只真实有效受击材质，不能冒充格挡/反伤或新增减伤。 |
| 未定义展示钩子（不是新增AUD事件） | footstep_concrete_000.ogg, footstep_concrete_001.ogg, footstep_concrete_002.ogg | source_hook_definition_required；步点候选；40事件表未定义脚步钩子，须补实际落脚事件与速度/暂停约束后才能接入。 |

常驻特性保持静音；不增加轻步触发、板甲格挡、换袍回专注或新的恢复循环声。

### ENM-STN-001 沉石骑士

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；按真实物化事件。 |
| AUD-DORMANT-AWAKE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | edit_then_audition；近触/受伤/兜底同一WakeEventID一次。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| ENM-STN-001-A1 盾锋冲阵 | 衣料/石裂材料 → 0.45s锁点；稳定专属签名未制作 | 冲锋展示钩子待定义；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.9s | 后摇1.6s；有效伤害才接触；恢复提示可静音 |
| ENM-STN-001-A2 盾沿横撞 | 衣料/石裂材料 → 0.35s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.7s | 后摇0.9s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

### ENM-STN-002 灰翼石蝠

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；按真实物化事件。 |
| AUD-DORMANT-AWAKE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | edit_then_audition；近触/受伤/兜底同一WakeEventID一次。 |
| 未定义展示钩子（不是新增AUD事件） | cloth1.ogg, cloth2.ogg, cloth3.ogg, impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；没有石翼扑动成品；真实低位/抬升/落翼的钩子与声包待做，不用飞行声暗示可命中高度。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| ENM-STN-002-A1 低掠啄击 | 衣料/石裂材料 → 0.4s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.8s | 后摇2.1s；有效伤害才接触；恢复提示可静音 |
| ENM-STN-002-A2 落翼横拍 | 衣料/石裂材料 → 0.4s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.8s | 后摇2.1s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

### ENM-STN-003 裂岩守卫

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；按真实物化事件。 |
| AUD-DORMANT-AWAKE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | edit_then_audition；近触/受伤/兜底同一WakeEventID一次。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| ENM-STN-003-A1 石斧横抡 | 衣料/石裂材料 → 0.5s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点1.0s | 后摇1.4s；有效伤害才接触；恢复提示可静音 |
| ENM-STN-003-A2 裂地顿足 | 衣料/石裂材料 → 0.45s锁点；稳定专属签名未制作 | AUD-WPN-RELEASE；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.9s | 后摇1.5s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

### ENM-STN-004 石纹哨像

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；按真实物化事件。 |
| AUD-DORMANT-AWAKE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | edit_then_audition；近触/受伤/兜底同一WakeEventID一次。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| ENM-STN-004-A1 刻纹石矢 | 衣料/石裂材料 → 0.425s锁点；稳定专属签名未制作 | AUD-WPN-RELEASE；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.85s | 后摇0.95s；有效伤害才接触；恢复提示可静音 |
| ENM-STN-004-A2 碎纹掌击 | 衣料/石裂材料 → 0.325s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点0.65s | 后摇0.95s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

### ENM-GOB-001 碎刃哥布林

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | edit_then_audition；按真实物化事件。 |
| 未定义展示钩子（不是新增AUD事件） | — | missing；没有哥布林非语言喉音；可自录或本地合成，但当前均未制作。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| ENM-GOB-001-A1 碎刃捅刺 | 衣料/石裂材料 → 0.275s锁点；稳定专属签名未制作 | AUD-WPN-SWING；knifeSlice.ogg, knifeSlice2.ogg；起点0.55s | 后摇0.6s；有效伤害才接触；恢复提示可静音 |
| ENM-GOB-001-A2 掷路石 | 衣料/石裂材料 → 0.4s锁点；稳定专属签名未制作 | AUD-WPN-RELEASE；impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg；起点0.8s | 后摇0.7s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

### BOS-STN-001 裂冠石像统领

| 事件或槽位 | 材料候选 | 状态 / 缺口 |
| --- | --- | --- |
| AUD-DAMAGE-DIRECT | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | provisional_candidate；实际有效命中唯一主声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；另做区别普通命中的短版本，保护期不伪报。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；需要生物非语言/石体解体终结层；不等于掉落或Boss胜利。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；仅D07已接纳实体/槽位；不泄露future。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；按真实物化事件。 |
| AUD-BOSS-PHASE | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg, impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；原1.2s真实相位提示；材料未证明可分辨。 |
| AUD-BOSS-SUCCESS | — | missing；缺专用胜利短收束，必须等同点结算后玩家存活。 |

| 招式 | 0s前摇 / 锁定秒 | 实际执行候选 | 恢复与命中 |
| --- | --- | --- | --- |
| BOS-STN-001-A1 裂冠冲阵 | 衣料/石裂材料 → 0.6s锁点；稳定专属签名未制作 | 冲锋展示钩子待定义；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点1.2s | 后摇2.2s；有效伤害才接触；恢复提示可静音 |
| BOS-STN-001-A2 破盾横斩 | 衣料/石裂材料 → 0.7s锁点；稳定专属签名未制作 | AUD-WPN-SWING；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点1.4s | 后摇1.9s；有效伤害才接触；恢复提示可静音 |
| BOS-STN-001-A3 震殿跺足 | 衣料/石裂材料 → 1.0s锁点；稳定专属签名未制作 | AUD-WPN-RELEASE；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点2.0s | 后摇2.1s；有效伤害才接触；恢复提示可静音 |
| BOS-STN-001-A4 冠盾踏印 | 衣料/石裂材料 → 0.9s锁点；稳定专属签名未制作 | AUD-WPN-RELEASE；impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg；起点1.8s | 后摇2.1s；有效伤害才接触；恢复提示可静音 |

完整逐招候选路径与壁撞/盟友阻弹的无伤钩子缺口见JSON。矿石原文件0.805–0.937s不能整条充作多数短前摇音，否则会遮住50%锁定；需先制短起音与独立锁点。

## 全部40个D12事件覆盖

| 事件 | 候选材料（原路径见上表/JSON） | 预检结论 |
| --- | --- | --- |
| AUD-WPN-PREP | drawKnife1.ogg, drawKnife2.ogg, drawKnife3.ogg, cloth1.ogg, cloth2.ogg, cloth3.ogg | reuse_candidate；随实际接纳攻击进入前摇一次；drawKnife1 很轻，不能为听见它把总线无限抬高。 |
| AUD-WPN-SWING | knifeSlice.ogg, knifeSlice2.ogg | material_only_gap；刀切文件仅作材料候选；纯空气破风未确认，挥空不可播肉体/石体命中。 |
| AUD-WPN-RELEASE | metalClick.ogg, metalLatch.ogg, impactGlass_light_000.ogg, impactGlass_light_001.ogg | material_only_gap；按弩/法杖实际释放分支；这里没有可信弩弦或火球成品，不把点击声标为已解决。 |
| AUD-WPN-MISS | — | intentional_optional_silence；可选，建议先静音；不可用命中声冒充，清理也不是落空。 |
| AUD-WPN-EMPTY | metalClick.ogg | edit_then_audition；仅新合法请求因弹匣0被拒一次；完整文件0.446s，应试听/剪成短机械点。 |
| AUD-RELOAD-START | creak1.ogg, creak2.ogg, creak3.ogg, handleSmallLeather.ogg, handleSmallLeather2.ogg | material_only_gap；只能作拉杆/握持材料，不代表真正弩弦；一次实际装填起始。 |
| AUD-RELOAD-COMMIT | metalLatch.ogg | edit_then_audition；只在真实补弹提交；+1.615dBFS解码采样峰值必须先留增益余量。 |
| AUD-RELOAD-CANCEL | — | intentional_optional_silence；可选静音；若未来加止机短点须区别补弹完成。 |
| AUD-FOCUS-LOW | — | missing；缺专注不足短低脉冲；可本地合成，不能产生新资源或CD。 |
| AUD-WEAPON-SWITCH | drawKnife1.ogg, drawKnife2.ogg, drawKnife3.ogg, handleSmallLeather.ogg, handleSmallLeather2.ogg | reuse_candidate；真实切换提交；预览槽位不播。 |
| AUD-DAMAGE-DIRECT | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg, impactMetal_light_000.ogg, impactMetal_light_001.ogg, impactMetal_light_002.ogg, impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactWood_heavy_000.ogg, impactWood_heavy_001.ogg, impactWood_heavy_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg, impactGlass_light_000.ogg, impactGlass_light_001.ogg | reuse_candidate；按目标材质择一个主接触；同一受击不再叠另一通用命中主声。 |
| AUD-DAMAGE-DOT | — | missing；缺燃烧短状态/tick素材；不把STF直伤音重复当DoT。 |
| AUD-PLAYER-HURT | impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | material_only_gap；仅肉体接触材料；没有玩家非语言呼吸/受创成品，不冒充已配人声。 |
| AUD-POISE-BREAK | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactPlate_heavy_000.ogg, impactPlate_heavy_001.ogg, impactPlate_heavy_002.ogg | edit_then_audition；材质破裂候选；需和普通命中区分，仅真实破韧事件，不在保护期每次削韧播。 |
| AUD-ACTOR-DEATH | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, impactSoft_medium_000.ogg, impactSoft_medium_001.ogg, impactSoft_medium_002.ogg | material_only_gap；只一次解体/倒地；Boss死亡不等于成功，仍缺生物死亡非语言声。 |
| AUD-ENEMY-TELL-START | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | material_only_gap；仅石纹/拉伸材料；完整挖矿音约0.805–0.937s会盖过一些锁定点，须分离短起音并试听。 |
| AUD-ENEMY-LOCK | metalClick.ogg | material_only_gap；0.446s机械点仅占位；14招还缺经试听可区分、短促且稳定的锁线签名。 |
| AUD-RECOVERY-OPEN | — | intentional_optional_silence；可选静音优先；真后摇开始才提示，不暗示场上其他攻击消失。 |
| AUD-SPAWN-WARN | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg | material_only_gap；材料候选；与原1.2s预告同点，须区别锁线/Boss相位。 |
| AUD-SPAWN-EMERGE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | edit_then_audition；实际物化后一次，不能在位置重验失败时提前播。 |
| AUD-DORMANT-AWAKE | impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg, creak1.ogg, creak2.ogg, creak3.ogg | edit_then_audition；既有休眠实体真实苏醒一次；不是为future槽先播。 |
| AUD-ITEM-START | handleSmallLeather.ogg, handleSmallLeather2.ogg, metalClick.ogg, metalLatch.ogg | material_only_gap；瓶塞/陷阱仅材料，未治疗未提交不播完成。 |
| AUD-ITEM-COMMIT | impactGlass_light_000.ogg, impactGlass_light_001.ogg, metalClick.ogg, metalLatch.ogg | material_only_gap；15配套道具仍需专属疗剂/爆弹/火焰/陷阱；玻璃音不自动等于饮药。 |
| AUD-ITEM-CANCEL | — | intentional_optional_silence；可选静音，不伪装成治疗或退款。 |
| AUD-INVENTORY-COMMIT | cloth1.ogg, cloth2.ogg, cloth3.ogg, handleSmallLeather.ogg, handleSmallLeather2.ogg, impactMetal_light_000.ogg, impactMetal_light_001.ogg, impactMetal_light_002.ogg | reuse_candidate；换装按材质一次；dropLeather普通平均单声道丢5.74dB，暂不列首选。 |
| AUD-CURRENCY-CREDIT | handleCoins.ogg, handleCoins2.ogg | material_only_gap；金币候选；永久碎片缺独立签名，批量入账合并。 |
| AUD-TRANSACTION-COMMIT | — | missing；缺服务专属短确认；必须区别UI按键与真正扣款/交付。 |
| AUD-TRANSACTION-FAIL | — | missing；缺中性失败短点；未知提交走恢复记录，不发未扣款暗示。 |
| AUD-RANDOM-REVEAL | — | missing；缺金币/物品/空奖/附魔可辨结果短声；不可拿同一币声覆盖所有结果。 |
| AUD-SOURCE-CLAIM | handleSmallLeather.ogg, handleSmallLeather2.ogg | material_only_gap；仅物件拿取材料；缺领取专属短标记，不第二次播货币/强化。 |
| AUD-ROOM-CLEAR | — | missing；缺短收束；波清不是房清，不提前宣告安全。 |
| AUD-ROUTE-COMMIT | doorOpen_1.ogg, doorOpen_2.ogg, doorClose_1.ogg | reuse_candidate；真实转房门声候选，不是DoT净化。 |
| AUD-BOSS-PHASE | impactBell_heavy_000.ogg, impactBell_heavy_001.ogg, impactMining_000.ogg, impactMining_001.ogg, impactMining_002.ogg | material_only_gap；石钟/冠裂材料；需为原1.2s可伤可控相位制作短标记，不提早播放阈值队列。 |
| AUD-BOSS-SUCCESS | — | missing；缺独立成功短收束；只接受canonical success，双死不能胜利。 |
| AUD-RUN-END | — | missing；缺失败/胜利/主动结束三种短收束；回看不重复。 |
| AUD-ACCOUNT-GROWTH | — | missing；缺购买/研究/退款可辨短确认；只读和坏凭据不成功。 |
| AUD-UI-NAV | impactGeneric_light_000.ogg, impactGeneric_light_001.ogg | material_only_gap；现有是冲击短点，仅占位；需降增益/修包络、限频，不能抢危险预告。 |
| AUD-UI-CONFIRM | — | missing；缺中性按键确认，不共用扣款/领奖成功。 |
| AUD-UI-BACK | — | missing；缺中性返回；不替代闪避声。 |
| AUD-NPC-NONVERBAL | — | missing_optional；未找到可靠非语言人声；文本优先，不伪造已有中文配音。 |

## 必须补的声包与免费制作路线

| 缺口 | 内容 | 下一步（本轮均未制作） |
| --- | --- | --- |
| GAP-WHOOSH | 没有经试听确认的纯空气剑/枪破风；knifeSlice仅材料，三刺需0.10s间隔可辨短起音。 | 用本地噪声+带通+短包络合成，或安全自录挥动物件；GSW宽厚、SWD短均衡、SPR窄刺分别制2–3take；不把肉体接触混进挥空。 |
| GAP-CRITICAL-UI | 14敌招的短前摇/50%锁定签名、破韧、相位、出生，以及UI/交易/房清/成功/失败/永久碎片等独立短反馈未完成。 | 用现有CC0金属/石体/钟声剪辑并辅以本地振荡器短脉冲；关键警报固定身份不随机变调；逐招和视觉实测后定稿；不从未试听音乐裁切成奖励声。 |
| GAP-XBW-MAGIC | 没有可信弩弦/弩矢短啸；creak/metalLatch只是机械材料，法术谐波亦未完成。 | 用短衰减正弦/滤波噪声作弩弦与空气层，叠低增益现有CC0机括；本地处理即可，不需要付费API。 |
| GAP-FIRE | 没有火球、一次火线及燃烧tick/状态层的明确成品。 | 本地滤波噪声、包络与稀疏颗粒合成；火线一次释放，DoT按实际tick，余焰不能发持续伤害暗示；禁止无界循环。 |
| GAP-STONE-MOTION | 没有石盾拖擦/冠裂/石翼/巨大石体整套运动与解体声；impactMining只是候选颗粒。 | 剪辑/叠加现有CC0石体与板材素材，保起音、修边、控制低频与尾长；声音体积不通过抬总音量实现。 |
| GAP-NONVERBAL | 玩家/哥布林受创、死亡、NPC非语言声未找到可靠现成文件；没有中文对白声库。 | 可先保留接触/视觉反馈；未来由自愿本人安全自录非语言声或本地合成非语言生物声并记录作者/许可，不能把已有素材标作已配音。 |
| GAP-MOVEMENT-HOOK | 40个D12事件未显式定义实际脚步/落地、冲锋起动/运动尾声、无伤墙/盟友阻弹等音频钩子。 | 后续先明确来自实际动作/阻挡收据的展示钩子与生命周期；本预检保留event_id=null，不悄悄新增玩法或借有效伤害事件伪报命中。 |
| GAP-SUPPORT | 首批15配套道具的喝药/治疗、爆弹/燃油、陷阱等成品声包未完成。 | 现有衣料/机括/玻璃仅材料；后续逐实际提交/投放/触发收据制作；本地合成及CC0派生可无API费用。 |
| GAP-MUSIC | 23音乐未试听，未确认REG01/石像Boss曲风、分轨、相位层或无缝环点。 | 先试听少量现有CC0循环；无需按名字认定曲风；若无合适曲可本地制作原创稀疏鼓/石钟素材，仍需节拍与环点验收。 |

“免费”指不需要付费素材/API，不代表没有录制、剪辑、试听、混音和接入工时；本轮不承诺工时。现有CC0材料可以在保留原件/许可/哈希后制作派生副本，本地合成亦不必引入付费服务。

## 接入前验收

1. 先试听SWD+LGT+STN001的少量候选，完成短破风、石盾起音/锁点与有效命中声；批准样张后再批量制其他声包。
2. 派生源保留48kHz/24bit PCM WAV与剪辑链；OGG转WAV不恢复损失，也不证明原始24bit。空间音效经L/R/mono复听后再导出单声道。
3. 按实际AcceptedAttackID/SubHitID/收据触发；前摇/锁线/有效窗/补弹/奖励必须由原事件决定，音频不延长动作或制造收益。没有定义的展示钩子先补合同，不能偷借伤害事件。
4. UE导入后验证暂停/继续游标、取消/死亡/跨房清理、旧弹保留、同点双死无成功声；最终在正常输入的实际混音和打包播放中试听。
5. 警报也服从用户静音，所有必要提示仍有可读视觉；不能用声音掩盖缺失的地面形状/锁线/反击窗口。

预检机器记录：[audio-preflight.json](audio-preflight.json)。仅本MD与该JSON是本子任务产物；没有将候选登记为最终声包或改变总账。
