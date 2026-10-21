# 原生XBW walk Actor/HUD接线计划 v002

> **For agentic workers:** Source保持冻结；本文件只读计划。后续按root明确窗口先冻结真实正常输入RED，再实现、统一编译回归和录像。

**Goal:** 让实际地面行走使用冻结六帧walk身体、相应甲层和该实例-1/0/3组件的真实刚体矩阵，Actor当前口与HUD同样本；既有发射、碰撞和资源合同不变。

**Architecture:** 最小生产改动是owner的`DungeonWeaponPoseSocket.h`、`DungeonFighter.cpp`与root的`DungeonHUD.cpp/.h`。纯helper新增Walk分支和显式ground-walking输入；Actor决定真实呈现上下文、同步当前物理口；HUD只读Pose/Frame加载新walk轨道，不反写组件。本轮没有修改这些文件、UE导入或运行。

**Spec:** root本轮readonly任务，冻结common901e…与armor c14a…。该子集不是全部动作/20搭配/完整服装/足锁或美术最终验收。

## 已核实的事实

- Common：[import-XBW-common-walk-v002.json](F:/Ourgame/source-assets/production/first-batch-XBW-walk-v001/manifests/import-XBW-common-walk-v002.json)，SHA256 `901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab`。six frames、duration .6s/loop、每帧.1s，18个body_far/body_support/body_near PNG；root(256,472)、已烘焙统一body scale .96，显示BodySize仍160，weapon scale固定.48，movespeed_changed=false。

- Armor：[import-XBW-walk-four-armors-v002.json](F:/Ourgame/source-assets/production/first-batch-XBW-walk-v001/manifests/import-XBW-walk-four-armors-v002.json)，SHA256 `c14a031fbd674dadb11f4a4d363f9e65e6bac2b724e39533625f2df24f59cac2`。LGT/MED/HVY/ROB各6帧×far/near，共48甲PNG，复用同18身体轨道。六层为body_far→armor_far→independent_weapon→body_support→armor_near→body_near。该甲合同从旧.94profile按比例.96/.94对原素材作新独立变换，不能在运行时再缩放第二次。

- 本轮实际复算66个body/armor PNG哈希和18个组件源映射；由冻结grip/.48/angle重算的18个virtualEmit与manifest差均<1e-10。最大source support residual为2.8255197372570726px，低于source gate3.129px；这是数值/source证据，不是运行抓握或足锁证明。

- common/armor均runtime_verified=false、footlock_certified=false；两处extended-stride contact proxy及3px测量不确定性仍在原合同。root(256,472)是名义ground origin，不能称每帧脚掌固定无滑移。

- 导入脚本已定义body目标`/Game/Production/FirstBatch/v022/XBWWalk`、`T_XBWWalk_{track}_{frame:03d}_v002`；armor目标`/Game/Production/FirstBatch/v023/XBWArmorWalk`、`T_XBWArmorWalk_ARM_LGT_001_{track}_{frame:03d}_v002`等四甲。**本次只读盘点时两目录均0个uasset**，没有声称已导入；实际导入由root另跑并保receipt。

- 当前[DungeonWeaponPoseSocket.h](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponPoseSocket.h)的EClip只有None/Ready/Primary/Reload。Resolve默认ready按AnimationTime/.15采6帧，仅ground-primary与reload优先覆盖；active skill/air-primary用GroundPoseFallback标出ready替身，没有walk输入或矩阵。

- 当前[DungeonHUD.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:925)的XBW专用入口只允许idle/attack/secondary/reload，排除walk。通用candidate walk按AnimationTime×10取帧，不等于已经使用原生XBW walk轨道。DrawXBWReadyWeapon的Actor-owned分支已经会读Pose.Angle/Grip/ComponentGrip/Emit，可复用这个刚体路径。

## 当前时钟、真实移动和覆盖合同

[DungeonFighter.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1067) SetAnimation在clip改变时AnimationTime=0，同clip累加实际DeltaSeconds；该时间是呈现年龄float。GameMode中央CommitMotion把bMoving设为实际Start/End差，再SimulateActionsTo选walk/idle；`ReadMoveIntent`或按着D本身不证明已移动。堵墙、空中、hurt/dodge/equipment、active primary/skill/reload不能仅因有输入而选walk。正常ground移动速度、真实XY、碰撞和取消仍由既有中央模拟决定，新增pose不得改它们。

GetWeaponPoseSocket的SampleTime使用GameMode实际SimulationTime（无Game时才用WA.Time），动画帧用该次Actor实际AnimationTime。WA.Time管动作权限和截止点，不能替代从walk进入时清零的呈现年龄；也不能按世界绝对Time让第一步从任意帧起。HUD应直接使用同一Pose.Frame/SampleTime，不再自行用另一个FPS或screen lerp修口。

默认当前口由SyncWeaponMuzzleTransform写真实组件：X=(EmitX−256)×160/512/.65、relativeZ=(472−EmitY)×160/512/.70，父height anchor只镜像X一次并加真实JumpHeight。GetWeaponMuzzleOrigin保持真实当前组件XY，默认combat Height仍真实JumpHeight；PresentationHeight单列native手部高度。walking只是当前口的新native几何，不能让ground攻击Height升到90而越过65cm门。

公开直接SetRelativeLocation({24,7,0})仍是合法一般custom覆盖；当前任一外部相对transform与LastAutomatic不同就锁custom。UseAuthoredWeaponPoseSocket恢复自动native矩阵。新walk帧推进不能被当作外部修改而误锁custom，也不得反过来自动覆盖用户custom。

发射快照FindWeaponEmissionPoseSocket在真实pre-spend事件时冻结；World Source/RangeAnchor/PoseSocket不追owner。开始J后实际Primary分支优先，真正发射仍在其ActiveAt用primary frame2与当前实际Actor位置/高度；不能把前一个walk口写进Primary发射。发射后neutral→empty0、真实ReloadCompleted后loaded3、Q往返保同实例、取消不退款均保现history规则。

## 最小文件与接口改动

| Owner / 文件 | 最小改动 | 必须保留 |
| --- | --- | --- |
| 本owner：DungeonWeaponPoseSocket.h | EClip尾部追加Walk（不改旧枚举数值）；Resolve尾部新增默认false的bool GroundWalking参数，保旧四参数调用兼容；ground-primary→reload→合法walk→原Ready/fallback优先级。walk按floor(AnimationTime/.1)%6，取冻结每帧stock/support、每状态角度/.48与现组件坐标 | 不更改WA FState/Version、资源/history、过去/NaN时钟拒绝或Primary/Reload数据 |
| 本owner：DungeonFighter.cpp | ResolveWeaponPoseSocketAt传明确实际ground-walk上下文：AnimationName==walk、bMoving、实际JumpHeight/Velocity==0、WA grounded且无active Action、无hurt/dodge/equipment。复用现current-origin/height/custom同步；必要时在同批SetAnimation之后窄同步组件 | 不写移动、输入、HP/Ammo/Focus、时钟、范围、动画年龄或发射history来适配画面 |
| Root：DungeonHUD.cpp/.h | 允许明确native walk入口；加载v022三body轨道和v023四甲两轨，suffix v002；显示clip标xbw_walk，Frame/SampleTime/instance由同一个Actor Pose；复用Actor-owned weapon矩阵路径和四/六层次序 | 原ready/primary/reload v001路径与参数不动；不把缺track的ready或generic walk当原生walk成功；不反写Actor/socket |
| 目前不需要：Fighter.h / GameMode / WorldProjectiles / WA内核 | 现公开Pose/组件/custom恢复/发射快照API足够；纯helper参数可内部传入 | 若实际RED证明最终Sync顺序不够，先定位最小Fighter时序，不扩碰撞或资源域 |

推荐显式native-walk preview旗标由root掌握；已导入纹理不自动构成运行验收。是否最终并入既有reload body preview由root裁定，不能静默改变旧profile名字或29个必需门。

## 冻结的每帧几何

以下角度为image-clockwise度，Emit为body canvas像素。这里只列审查摘要；实现常量或表必须对应完整manifest，不能把四舍五入表当新的艺术合同。state0与3角度数值相同，但stock/support/emit源Y相差34，因此完整affine translation不同；neutral的角度则另差约4.566度。

| 帧 / 区间s | stock body grip | support body目标 | angle -1 | angle0 /3 | Emit -1 | Emit0 /3 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 / [0.0,0.1) | (229.12, 302.08) | (329.92, 306.88) | -5.17338062035899 | -0.607539667630335 | (400.438961535, 272.592066563) | (405.52103701, 278.608235223) |
| 1 / [0.1,0.2) | (231.04, 298.24) | (332.8, 303.04) | -5.19906227686997 | -0.633221324141312 | (402.345726966, 268.675279321) | (407.430498554, 274.689169441) |
| 2 / [0.2,0.3) | (229.12, 296.32) | (328, 302.08) | -4.56584095272866 | -5.16840135737822e-15 | (400.742001881, 268.650282432) | (405.76, 274.72) |
| 3 / [0.3,0.4) | (236.8, 303.04) | (338.56, 307.84) | -5.19906227686994 | -0.633221324141279 | (408.105726966, 273.475279321) | (413.190498554, 279.489169441) |
| 4 / [0.4,0.5) | (239.68, 297.28) | (338.56, 302.08) | -5.12052475019314 | -0.554683797464487 | (411.026091516, 267.950122365) | (416.10261486, 273.970976725) |
| 5 / [0.5,0.6) | (225.28, 303.04) | (325.12, 307.84) | -5.14720621399654 | -0.581365261267883 | (396.612414618, 273.630333205) | (401.691741199, 279.648822879) |

组件源坐标继续现生命周期：neutral stock(128,253)/support(337,282)/virtualEmit(489,224)；empty0 stock(138,308)/support(344,320)/emit(506,263)；loaded3 stock(138,274)/support(344,286)/emit(506,229)。真实walk只可能-1/0/3，无active reload时不能因装填pose索引显示state1/2。

每态同帧先以stock body grip为锚，R(该态实际angle)×.48变换对应component坐标；Out.Support是真正变换后的support点，不能强填source目标点来假称零残差。读取同角度不等于复用同完整matrix。body .96已在PNG/测量握点中，运行时BodySize160、weapon.48不能再乘.96；nativeEmit是virtual而非不透明像素或combatZ。

## 必须先取得的真实正常输入RED

- [ ] 新Actor组：真实World/Controller/Enter/E取得Ammo1 XBW，正常D/A移动；先证明groundXY有合法位移、AnimationName==walk、AnimationTime确实推进，再要求Pose.Clip==Walk、6帧.1/.6循环、准确neutral矩阵/组件口/镜像。当前生产只能Ready，形成语义RED，不能因未装纹理或fixture初始化失败冒充。

- [ ] 同组或第二组：真实J消耗→autoReload阶段T取消得到empty0，正常AD采walk六帧；真正T完整完成得到loaded3再AD六帧。要求实际ammo/history/ID真实，不能直接注册empty/loaded照片代替真实生命周期。两Facing每态的grip/support/emit按各自18组冻结式独立核，不用Resolve自证Resolve。

- [ ] 转场/覆盖组：移动中正常J，核Primary接纳/实际ActiveAt口与冻结world snapshot；之后走动、转身、Q切回同实例，不改历史Source/RangeAnchor。公开component override24/7在移动中保留、UseAuthored后恢复该次Walk帧而非Ready；同点伤害权限、65 combat gate与420角色range原有83仍保。

- [ ] 反控制：D按住但真实墙挡住无XY进展不伪称walk；正常Jump/Skill/Reload/受击/换装优先，不能以bMoving或输入覆盖动作姿态。断言只读Pose查询不增加Action/Event/资源receipt。新groups数量由root冻结时如实计入（例如加2组就是85），不将现83静默改成85已过。

- [ ] 实际HUD正常输入录像：独立walk profile证明真实XY移动、实际AnimationTime/.1 frame、两Facing的四层无甲/六层四甲、-1/0/3的正确component与current socket，加载的是v022/v023 suffixv002。匹配每次实际draw的sample time，不把walk过程中ready替身或上帧旧甲算mask。保原29/noarmor20任务、预算和失败证据，不改sim/fixedstep/音频。

旧83应该继续作为冻结回归运行，但当前没有“实际走动时必须Walk”的断言，旧GREEN不能证明这项新合同。若旧current-ready假设与新真实walk重叠产生失败，先实读分类，交原test owner明确版本化，不能让GetWeaponMuzzleOrigin暗返历史值或恢复错误ready几何逃避。

## 执行顺序与剩余限制

- [ ] Root完成当前async四甲29实录/归档后再开Source；本owner不运行UE/UBT。
- [ ] Root实际导入18+48，核actual/saved/success receipt，仍runtimefalse。
- [ ] 先加新Clip/API可编译桩及真实正常输入反例，root统一跑有效RED/快照；不先实现几何掩掉RED。
- [ ] 按两owner最小文件分工实现，sourcefreeze→root统一回归旧83+新增实际组。
- [ ] Root做独立正常输入walk录像、F/E保全/CRC/音画/逐向逐态核查；缺足锁/下衣覆盖等原manifest限制仍诚实列出，不用运行接线通过认定正式美术。

该计划不新增碰撞矩形、range锚、launch clearance、Projectile字段或D13 schema，也不修任何未授权美术像素。不能因走路手位更高改combat Height，不能按画面重算已发弹，也不拿角色native0.96重采样去更改实际movespeed或地图接触。

## 本轮只读源码与工具依据

| 文件 | 当前实读SHA256 |
| --- | --- |
| [DungeonWeaponPoseSocket.h](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponPoseSocket.h) | `080734e35f95239c2be0b1a7dc01c0a953812cd8315cb43fad1592e8b2606f59` |
| [DungeonFighter.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp) | `e36cc2915b1367057f32e25054eb6356c37e4569cddc3d619738afaa52df9a60` |
| [DungeonHUD.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp) | `a81276255f8ed08351f9794598a02e8a983f6cf7cb5d3fa6cf65cc9ea9d44a94` |
| [DungeonGameMode.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp) | `930d3ae95684e8f8893b507e394f65daf00beef4fa740c7d2fff1285651bd3e6` |
| [DungeonWorldProjectiles.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.cpp) | `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9` |
| [ue-import-xbw-walk-v002.py](F:/Ourgame/tools/scripts/ue-import-xbw-walk-v002.py) | `0b1fd6292fdffd9f045f2d1ec114f889d61a3468ead9860fef72a18f0d7fcd4f` |
| [ue-import-xbw-armor-walk-v002.py](F:/Ourgame/tools/scripts/ue-import-xbw-armor-walk-v002.py) | `7837dc897df66f87bbb2fb46846b946e0208be56402ffdcaa7e8ef7b02b92680` |
| [ue_xbw_walk_v002_checks.py](F:/Ourgame/tools/scripts/ue_xbw_walk_v002_checks.py) | `abc5d7173800c7a8969821c562074100eccfe16d079c0fcf52a26789b0a289a3` |

本轮交付仅此计划文件；Source、manifest、资源、tests、工具和并行工作均未改。
