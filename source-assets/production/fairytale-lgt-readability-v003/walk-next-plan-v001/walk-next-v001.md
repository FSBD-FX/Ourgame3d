# Walk6 下一步候选计划 v001

2026-10-17，只读盘点；未出图、分层、改 Source、导入或运行 UE。**已有公共钟盔 Walk6，尚没有“棕皮 LGT＋SWD 正常行走”的完整素材与玩家运行接入。**不能将旧 CommonWalk 展示证明扩写为持剑、穿新甲或脚锁通过。

## 真正可用的六张身体来源

当前实际导入链为 `F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008` → [冻结导入清单](F:/Ourgame/source-assets/production/fairytale-walk-lookdev-v001/manifests/import-walk-lookdev-v001.json) → [真实导入 receipt](F:/Ourgame/UnrealGame/Saved/Bootstrap/fairytale-walk-lookdev-v001-import-20261015-193357-409584.json)。本轮只读复核六张源 PNG 与六份当前 UAsset，大小／SHA 全相符；actual/saved/expected=6，命名空间 `/Game/Production/ArtTrials/EV047/v002/HeroCommonWalk`，对象名 `T_Fairytale_HeroWalk_000_v002` 至 `_005_v002`。UAsset 均位于 `F:/Ourgame/UnrealGame/Content/Production/ArtTrials/EV047/v002/HeroCommonWalk/`。

| 输出帧 | 原生请求 | 精确512×512 RGBA来源 | 字节 | SHA256 |
|---:|---:|---|---:|---|
| 0 | 138 | [frame-0.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-0.png) | 121979 | `90eb027ee05e289a08aefd613df908c81c450a1f6dd5c14d580ca6e089d415e5` |
| 1 | 142 | [frame-1.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-1.png) | 104942 | `a13aaea3963abc6d4973805524be39710c8ef9395290c3e0d7d844ed7d37594e` |
| 2 | 143 | [frame-2.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-2.png) | 112370 | `016dea34e0a1d858dd2b229ec8b360683633a5679ce5bf293410ec22921ac21b` |
| 3 | 137 | [frame-3.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-3.png) | 114035 | `7ba795bc8876a657b3a9a2adb6843790d52137b43c2b3f4faa1d14e086d51544` |
| 4 | 141 | [frame-4.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-4.png) | 107900 | `f884e69c9653a2a037b9cf366f98fe9b81b2f59a4d8dabeca59217947ac835fd` |
| 5 | 145 | [frame-5.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-5.png) | 118064 | `18364d7b5ea06a1940c91cb204e1e59196194d69d972a123bcbaa956718d2566` |

六相顺序是138／142／143／137／141／145；属于已存在六张独立姿势的来源序列，并非重新生成的一行。[注册回执](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/source-cell-registration-receipt.json)记载共同416/1043缩放与X平移−3／0／+9／+5／+5／+4，六帧原83ms、总498ms。展示 pivot (256,464) 不是实测髋／脚根；头部色区中心也不是骨骼或刚性盔锁。

v002／v003／v004 的 whole-row Walk 曾因相反支撑／经过角色不清被拒；不要选回它们，也不要借旧 round-knight／FirstBatch v007／XBW 行走来源。当前 v008 的原始公共身体身份来源于131；131仅解释历史来源，**新皮甲生成仍只认已经接受的 Ready184／186／187 组件外观**，不得重新用131或179整人当新甲身份。

历史[Walk原生试样审阅](F:/Ourgame/docs/production/first-batch-v2/runtime-review-fairytale-walk-lookdev-v001.md)有真实4.23秒UE lookdev、左右六相／循环、原像素检查；玩法实际冻结、A/D只变展示朝向。它没有证明普通移动、SWD握持、棕皮甲、足底锁定或完整连续步态。导入 receipt 的 runtime_verified=false 是导入时点；后续限定 lookdev 实录另证，二者不可互相倒填。

## 层与部件缺口

本轮扫描全部 `source-assets/production/fairytale*` 家族，没有找到对应 Walk6 的 BodyRest／NearArmWithoutHand／HelmetForeground／NearHand 文件；真实 Walk 导入也仅 whole-body 六件。**Walk 专属四归属层尚不存在。**Ready／P1／P2／P3 四层属于不同姿势，不能直接套用。确定性分区需保留原 Walk 每帧 RGBA，四层重建逐像素相等；归属 mask 不能冒充已经通过的语义保护 mask。

新软皮 Walk Chest／ShoulderNear／ShoulderFar 六相也尚缺，共需18甲层。仅保留同款组件外观身份：[Ready184胸甲](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/chest184-extraction-v001/run-shared-diagnostic-v001/frames/leather_chest_sword_ready/frame-0.png)、[Ready186近肩](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/near186-extraction-v001/run-shared-diagnostic-v001/frames/leather_nearshoulder_sword_ready/frame-0.png)、[Ready187远肩](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/far187-extraction-v001/run-shared-smallcomponent-v002/frames/leather_farshoulder_sword_ready/frame-0.png)。可把90×90／60×44／32×30共同窗口作为初始建议，最终要依实图范围确认；小远肩门逐行声明，不能继承195专属min160为通用门。

Walk 每帧 Root、握点、武器方向、手部前景、肩甲挂点和脚接触窗尚未实测；不要用bbox中心、Ready握点或旧灰甲挂点填入。实际visible A与artist设计B分开；未知保持null，隐藏B明确TRIAL。当前公共身体不是已证实持剑上身，握持不适配时先承认需要局部原生修正，不能靠贴剑遮掩。

## 当前 selector 与最小接入位置

| 当前源位置 | 已核事实／后续最小改动 |
|---|---|
| [Presentation](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp:145) | Supported只有Idle与P1／P2／P3；168–171不支持移动时取Ready0，283不画Sword。未来新增独立StableWalk与Walk clip，不能把占位算完成。 |
| [纹理加载器](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp:59) | GetFairytaleSwordTexture没有Walk分支；独立Walk数据表须有明确6件来源、同帧Root／Grip／Axis，保留已冻Ready与三刀表。 |
| [甲层选择](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp:192) | 新增Walk专属四身体层＋三甲层；层序延续BodyRest→Far→Chest→NearArm→Near→HelmetForeground→独立Sword→NearHand，最终左右整套只镜像一次。 |
| [HUD启动预加载](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:76) | 必须加载全部新Walk六相及实际selected层后再用既有FinishCompilation／render flush；避免重复本轮P2／P3首次懒加载缺图。玩家入口仍HUD:996。 |
| [独立Lookdev选择](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleLookdevState.h:31)、[Lookdev绘制](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:1735) | 当前floor(wall elapsed/.083)%6只是冻结预览，不是普通玩家selector，不能直接挪来当游戏走路时钟。 |
| [真实地面移动](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1144) | bMoving在1162碰撞裁剪前置true，位置实际提交在1194；堵墙也可能为walk。SetAnimation:1659已有动作累计时钟，1781–1782选walk，但这些并不证明真实位移或接地。 |

装备 resolver 只管真实已提交SWD／无甲或LGT实例，不限制Walk；保持它的身份与版本门即可。姿势支持、移动驱动及源marker属于后续独立实现，不必放宽装备白名单。

## 最小下一步

1. 先固定上述 v008 六Body与receipt，Root保全后复核六帧实际手／肩／盔／靴与同款军剑握持。完成 visible landmarks与Walk专属24张四层分区；原Body不重采样、不修色，重建RGBA零差后仍要实看遮挡。
2. 再准备三组新软皮六相component-row：Ready组件只作外观，实际Walk部位／数值guide只作运动几何。当前没有旧Walk同组件行可直接edit，不能拿旧甲／Ready整背心充当Walk肩。先Root实看输入、生成与提取，再测全部新A／B并纯整数试装。
3. 身体与甲试装通过后再接独立Walk marker与正常移动selector。普通移动先有碰撞裁剪后真实位移证据；步幅未测定，498ms只是源预览时长。AnimationTime可供受控候选观察，不能据此宣称脚锁；正式相位应结合真实已完成地面距离，堵墙零位移不空走，换房／安装／恢复不把瞬移计为步行。已有详细[移动接口审计方案](F:/Ourgame/source-assets/production/fairytale-player-motion-v001/README.md)可接续，无需重新摸索。
4. 用正常A/D、W/S斜向、停走／停墙、Idle↔Walk↔三刀、拾取取消与实际提交检查同一装备实例、方向、握点、近远遮挡、原比例与资源首用。保留完整原生观测／CRC／FIFO／flush门及E展示前留档；此阶段继续trial，不接受完整动作／音效／全适配。

范围与成本：最低新增24张确定性身体分区＋18张甲层及6组实测marker，可能仍需持剑手臂原生修正。当前没有冻结步幅、接触窗或新生成成本；本计划没有预留／调用生成，也不把既有六Body的磁盘可用性当成上述任务已经完成。
