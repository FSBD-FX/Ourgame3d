# Scene 原生低墙与碎碑导入 v001

2026-10-15，Asia/Shanghai。本记录仅核对冻结源、root实际UE导入和当前只读HUD候选接线；未启动UE/UBT，未修改Source、工具、根README、progress或需求台账。source art由assets_prepare制作，root拥有HUD、实际构建/运行、媒体及验收。新HUD/GM正在root统一构建，本文不提前记为运行通过。

## 冻结来源

manifest：`F:/Ourgame/source-assets/production/scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json`，schema=`frozen-scene-exploration-props-v1`、version1、frozen=true，仅`moss_low_wall`与`old_city_stele`两项；SHA256 `a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969`。两张原生生成源由整幅1254方画布等比变为512方画布，不裁切、不bboxfit、不平移重排、不非等比拉伸。来源、原件及F/E副本由art owner保全，具体索引以源目录报告为准。

| 项目 | 苔石低墙 | 旧城碎碑 |
| --- | --- | --- |
| source PNG | `processed/moss-low-wall-512-v001.png` | `processed/old-city-stele-512-v001.png` |
| 字节数 | 125,897 | 121,130 |
| SHA256 | `d8c182b4ee49c2b0120d5581967f0841ff6222131437830bcce96edc97b4314c` | `bce27c174d4146fdf346f04bb1a42d0addac6d85b46e4de16636c40101ced97b` |
| 实际画布/模式 | 512×512、RGBA8 | 512×512、RGBA8 |
| alpha / 四角alpha | [0,255] / [0,0,0,0] | [0,255] / [0,0,0,0] |
| 实际alpha bbox | [14,297,498,413] | [166,123,348,439] |
| 实际可见root | [256,408] | [256,431] |
| root像素RGBA | [31,50,46,255] | [10,22,17,255] |
| 单一uniform scale | 260/478 = 0.5439330543933054 | 0.18 |
| 世界锚点cm | [-900,60]，既有墙近边中点 | [-920,300]，既有调查点 |
| footprint估计四角 | [[31,365],[483,365],[495,410],[17,410]] | [[194,411],[343,420],[316,436],[171,425]] |
| footprint状态 | inferred；hidden_footprint_verified=false | inferred；hidden_footprint_verified=false |

墙的root408是实际不透明前接地点；此前草案中心410已透明，不可改回410。隐藏后边/碑左后底座均无法从源图证实。PNG alpha、bbox和推定脚点不创建或改变碰撞、交互范围或调查状态。

## 源验证与实际UE导入

导入工具 `F:/Ourgame/tools/scripts/ue-import-scene-exploration-props-v001.py` SHA256 `cbcbdecc38b995be6eb826475d33280e4195e882be65fefd4507e632bf046808`。stdlib预检核对实际PNG数据、CRC、root像素、冻结hash与14个独特引用；对原生成工具C路径仅允许manifest精确列出的两份只读原件并核对其raw SHA，其余引用仍受production路径约束。目标目录通过磁盘和AssetRegistry双层拒覆盖；导入不覆盖现存asset，实际属性验证后才保存，失败部分留receipt便于追查。

源预检回执：`F:/Ourgame/UnrealGame/Saved/Bootstrap/scene-exploration-props-v001-source-validation-20261015-045135-7006735.json`，SHA256 `02982424ac7b3b140c9300c0f923fd2901ce36d44784e607146bf06c44101daa`。10项stdlib守卫检查见 `F:/Ourgame/UnrealGame/Saved/Bootstrap/scene-props-tool-guard-probe-20261015-045251-731149/guard-results.json`，SHA256 `6b2939fdd9d9917cb85ac26bf1a31047b835484985e4276a3b9f5a548b897a68`。这些检查未加载UE模块，不能替代UE导入或运行。

root实际commandlet exit0，报告0 error/0 warning。producer独立读取导入回执：`F:/Ourgame/UnrealGame/Saved/Bootstrap/scene-exploration-props-v001-import-20261015-045356-046228.json`，SHA256 `b48cc7d82ddfbc976d7c7401243d78c53b4312620131b9df3d93d3f16c09c15b`；UTC为2026-10-15T04:53:56.046228+00:00。`expected_count=2`、`actual_count=2`、`saved_count=2`、`success=true`，两项`saved=true`，源hash与manifest一致。

仅保存以下两个新Texture2D对象：

- `/Game/Production/SceneExploration/v001/T_scene_moss_low_wall_v001.T_scene_moss_low_wall_v001`
- `/Game/Production/SceneExploration/v001/T_scene_old_city_stele_v001.T_scene_old_city_stele_v001`

回执逐项实际读取的设置均为`TC_EDITOR_ICON`、`TMGS_NO_MIPMAPS`、`TEXTUREGROUP_UI`、`never_stream=true`、`srgb=true`、尺寸512×512。receipt同时保留`runtime_verified=false`、`formal_scene_accepted=false`、`collision_or_interaction_modified=false`、`wall_full_AABB_alignment_verified=false`；actual/saved/success只说明导入和保存完成。

## 当前root HUD组合候选

只读接线为 `Ground(P)=(640+(P.X−CameraX)×0.65,490−P.Y×0.38)`，再由 `Screen` 对整个逻辑坐标乘同一UIScale并加Origin。每个prop先使用各自冻结root与单一uniform scale，整幅512方画布的显示宽高相等，再共同乘UIScale。墙使用`Ground(-900,60)−(256,408)×260/478`作为左上角；碑使用`Ground(-920,300)−(256,431)×0.18`。墙锚是近边(-900,60)，不是AABB中心(-900,110)。

墙碰撞权威仍为共享布局X[-1100,-700]/Y[60,160]，即400×100cm。HUD候选单独在这一真实投影矩形绘石质foundation，逻辑宽260、深38；使用已有floor texture，源 `source-assets/production/room-art-v001/processed/dungeon-floor-tile-512-v001.png` SHA256 `268563d9b2ef74651fee8b978e1e63c18585a0a5068df39b99bc2f119e5a4b16`。原生低墙只作为facade/top overlay，不通过拉伸PNG伪装成精确占满该矩形。

实际源图测得顶部深约45px、前立面高约70px；统一缩放后约24.48与38.08逻辑像素，与期望38深/24高不同。alpha bbox宽约263.26，也略宽于478px前跨度对应的260。源中连续不透明foundation列检查证明无贯穿透明缺口，但不证明运行遮挡或400×100cm完整地基对齐。真实foundation组合、近后边、角色遮挡与碑文可读性仍须新运行审看；两图footprint保持inferred，不把源图后缘补成已验几何。

碑沿用既有调查锚，不增加障碍或扩大80×40交互范围。HUD候选对未知时的整碑与标签进行可见性准入，对记忆状态淡化；调查latch仍由真实E负责。该源码候选未在本文记为运行通过，雕纹也不代表已批准的城徽或可翻译碑文。

## 证据版本与范围

此前严格72 Actor GREEN对应 `FirstRoom-20261015-121909/index.json`/root v034；Scene13 v002实际13/13对应旧v035/v002来源，其runtime-report SHA256为`b09a217635bdd631cb32969d7a8e201b724a0495764c32aaacd5f97c7748155a`。两者均先于本次原生道具与新HUD/GM修正，不倒填为其验收。取消出口后继续探索提示、开始成功后去掉过期“Enter开始”、雾下整碑/标签、root与foundation组合需要后续同版本运行和取消帧检查。

Scene13是定向QA：初始化sim0禁止唯一石骑的新攻击启动，仍保留真实185cm/s追踪；之后玩家正常输入清场、调查与过门，不在运行中写HP、位置或锁状态。普通Scene试玩攻击正常。该录像不是完整AI压力证明，也不覆盖正式D08掉落来源、完整D07路线、D13持久化、美术或音效最终验收。旧QA战利品表现继续作为已知未接正式来源缺项保留，不因换图而宣称补齐。

## 后续主线程v003验证

上述“正在构建/待运行”为导入记录写入时状态。随后root `125830`构建exit0，实际`FirstRoom-20261015-125946/index.json`严格72/72、零warning/error/notRun；root v036快照786文件/61,282,531B，录制DLL SHA256 `95b534b86a8de3df6c5058c3c02d2da6cfef8df6c8ffec12a8959269bfdce2dc`。新增验证归属于v036/Scene13 v003，不改旧v035/v002来源，也不回写冻结素材manifest或导入receipt的历史runtime=false。

producer只读核对F原批 `F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v003` 及E v028实际副本：v003 runtime-report 13/13通过，SHA256 `1e085e86f605140c94baaba839ed522b5e06f6497b67f838aef3add255c65568`；F/E index均为SHA256 `91c4f38629b6ff5b67e533ef46476478b927e9d88462768fe0118a40570831b2`，DLL与v036一致。E目录 `E:/OurGame/Knight/过程图稿与视频/2026-10-15-OurgameUE-原生墙碑探索13项-v028` 的保全索引记录751文件/2,748,361,512B、两遍大小/SHA核验零差；索引SHA256 `bc62f2f66c07d6be719aa732a9aec62180490a84fd708897ddf1a69da9ffe267`。本次未修改任何归档。

739电影原帧加1预热帧全部原生PNG CRC通过；录制墙钟24.650808099657297s、UE主混音24.64s，音画门及全流解码通过。引擎原WAV保留，canonical副本仅修BlockAlign头、PCM完全一致，无音频替换、增益或变速。声画时长门不等于听感、逐sample同步或性能通过。

[主线程运行复核 v003](../runtime-review-scene-exploration-v003.md)记录root实看64/170/182/264，独立8+1帧复核另记。近碑170/182的实际trace包含两张原生Texture路径且surveyRendered=true、visibility/memory1；退回264为visibility0/memory1；新房738仅墙路径且surveyRendered=false、visibility/memory0。由最近捕获完成戳映射trace到原帧，非GPU精确同点；13项流程门本身不独立断言原生纹理，实际路径和原帧属于额外运行证据。

该来源已运行墙root408/260÷478与碑root431/0.18的组合，foundation仍来自真实共享AABB。隐藏后脚点保持inferred，不能把运行调用纹理等同完整AABB精准匹配或全遮挡验收。近距碑身仍部分被角色遮挡，全部碑纹可读及正式美术/声音尚未验收。定向QA只禁新起攻、仍有185cm/s追踪，普通试玩攻击正常；正式D08来源、完整D07、D13等边界不变。
