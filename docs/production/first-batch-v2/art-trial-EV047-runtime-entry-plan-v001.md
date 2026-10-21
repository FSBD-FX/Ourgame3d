# EV-047 新造型进入实际 UE 的只读接入建议 v001

2026-10-15。基于当前 HUD/Fighter、素材导入器和冻结映射的只读定位。本轮未修改 Source、素材、导入脚本或旧索引，未启动 UE/UBT，未生成图片。125/126 仍是待审造型参考，127 尺度失败、128 为改善后的同场概念；本建议不追认它们为已批准资源或完整 sprite。

## 当前实际路径

| 位置 | 当前行为 |
| --- | --- |
| `UnrealGame/Source/CodexDungeon/DungeonHUD.cpp`，BeginPlay / GetCandidateFrame | `DungeonCandidateSprites` 开启候选。hero 的 walk 从 v007/CandidateSprites/Hero 读取，其余 hero 从 v006；stone 所有 clip 从 v002/CandidateSprites/Stone 读取。原型 fallback 是 `/Game/Prototype/FirstRoom/Sprites/Human`、Orc。 |
| 同文件 DrawFighter | 从 Fighter 动画/实际动作时钟选帧，按 ground root 放置 512×512 图；hero root 从 AssemblyV007 取，stone 默认 root 为 (256,472)。额外 Armor/XBW 分层分支可能覆盖选中的基础 Frame。 |
| 同文件 DrawCandidateSword / DrawMeleeTrail | SWD 武器使用 AssemblyV007 的逐帧 Grip、Root、HandPolygon、Angle 和 WeaponVisible。军剑素材是 v002/CandidateComponents/T_military_sword_v002。TuningV002 全局 scale=.40，idle 强制 35°、walk 强制 30°。拖尾也使用同一旧 marker。 |
| `DungeonFighter.cpp`，GetPrimaryPoseFrame | 真实主攻每段按 windup/active/recovery 各两姿势取 0–5；不能把普通帧计时器冒充实际动作时钟。 |
| 同文件 SyncStoneKnightState | Kernel 的 Dormant/Waking/Idle/攻击/Recovery/Stunned/Dead 变为 dormant/wake/idle或walk/charge或shield_bash/recovery/hurt/death。Facing 由真实攻击锁向或玩家位置决定。 |
| `DungeonWeaponPoseSocket.h`、Fighter SyncWeaponMuzzleTransform / ResolveWeaponPoseSocketAt | 当前专属几何只支持 XBW Ready/Primary/Reload，根 (256,472)、512 图，身体画布 120；原始手口数据和组件 .48 对应旧身体。实际物理 muzzle 是世界来源，presentation height 与真实 jump combat height 分开。 |

hero 当前 marker 表有 15 个逻辑 clip：idle6、walk6、primary_1/2/3各6、jump4、fall2、land2、hurt6、death6、dodge6、secondary6、air_primary_1六、equip_weapon6、equip_armor6，总计 80 个逻辑 marker；这不是 80 张独立新动作已完成的声明。

stone 预热目前按每 clip 六图加载，但攻击视觉取帧实际为 windup 0/1、active 2/3；冲锋 active 以 12fps 在 2/3 循环，Recovery 使用另一个 clip 0–5。不能用“导入六张 charge”推断六张均在运行中播放。

## root、120 与实际高度

当前 `DungeonPresentationScale.h` 的 CandidateBodySize=120，同时作用于 hero 与 stone；RelativeScale=.75 用于旧 fallback 和阴影。120 是整张纹理在逻辑 1280×720 画布上的边长，不是角色可见身高，也不是厘米。

实际显示身高约为 `角色主体像素高 / 512 × ActorDisplaySize × UIScale`。Ground 投影为 X×.65、Y×.38，跳跃单独以 JumpHeight×.70 显示。镜像时 root 的 X 变为 512−root.X；只镜像一次。每帧变化的脚部不等于角色位置变化，接触点必须锚定实际 ground。

125/126 是 1254²，不符合现有 512 纹理/marker 约定。必须在保留原件后建立可重放的统一画布转换、脚底 root 和主体高度；不能直接换路径让 1254 图套用 512 坐标。两张原图有低 Alpha 散点，不能以任意非零 Alpha bbox 推 root。独立报告的 Alpha≥128 bbox 高度分别为 987、952，宽度差异很大；同一画布/同一 Size 不会自动产生预期的敌人大 1.3 倍关系。

建议新试样用显式 ActorDisplaySize/主体归一规范，实际运行比较可见身体高度后确定比例。若两种主体归一后高度相同，石骑的显示 Size 可单独调；不能改全局 CandidateBodySize 来连带改变现有 XBW 手口或当前旧版 proof。也不能只把石骑在 512 内放大到盾锤被裁掉。最终必须用实际脚线、主体占屏和武器外伸验证，而不是从整图 128 反推值。

## 必须替换或隔离的旧映射

1. 新版本的 hero/stone 贴图路径及帧数表；Frames 缓存键包含新 style/version，避免同名命中旧图。缺帧应明确诊断，不能悄悄回旧 Human/Orc 或旧造型。
2. 新逐帧 root、握点、手遮挡、剑尖/护手、组件 pivot/scale/angle 与 WeaponVisible；旧 AssemblyV007、TuningV002 的坐标/固定角度均只对旧图有效。125 双手空着，不能用旧多边形在新图上重画出握剑。
3. source native_facing。125 朝右、126 朝左；当前 Facing<0 翻 U 默认源图朝右。准备阶段可统一原始朝向，或 trial renderer 按 Facing/native_facing 决定单次镜像，root 与武器同规；不能改变 AI Facing 来迁就画稿。
4. 新造型支路应隔离旧 ArmorIdle/Walk/P1–3 和 XBW Ready/Primary/Reload 分层。125 已烘甲与披风，旧四甲层不能直接覆上；126 已烘盾锤，也不能叠旧盾锤。新 idle 被旧动作或旧分层覆盖会产生换身份现象。
5. stone 的旧 wake 第 3 帧固定眼睛补光坐标 (295,231) 不能搬到新脸上；hurt/尘土等附着位置也应对新身体重新审阅。地面预警范围来自真实攻击，不能为了贴图好看改碰撞或伤害判定。
6. 若后续接新 XBW 身体，必须同时新做两手、武器组件和 Actor muzzle 几何，不能仅在 HUD 改手口。当前 .48/Root/Grip/Support/Emit 数据及空弹/装填4姿势属于旧形体；保留65真实战斗高度、420 actor range anchor及custom override/历史snapshot规则。首轮 SWD 造型试样无需改这些 XBW 权威路径。

## 分层与动作制作顺序

建议先固定 125/126 的身份、源朝向、512 root 与小尺寸，再建立动作，不把概念全图当动作页。

- 英雄：公共身体/远手、披风或背层、近臂/近手、可换甲层和独立军剑组件。若首轮只用125固定甲合成身体，应明确标记固定外观试样，不称无甲 base 或四甲适配。先完成站立握剑 anchor，再做真实 idle 呼吸、walk 六个步态接触/抬脚姿势，随后 primary_1/2/3各六个真实姿势及手/剑 metadata，再补本试验可触发的 hurt/death/jump/fall/land/dodge/secondary/air/equip。各姿势保持身份与关节长度，动作页的位移不能替代脚步或挥剑动作。
- 石骑：先做可用的待机与步态 anchor，明确盾手、锤手、肩部/苔菇和脚底。可以先逐动作输出合成图，但不能声称内部装备可替换。随后 charge 与 shield_bash 的起势/锁向/发力、独立 recovery 的刹停与回正、hurt/death，按实际需求补 dormant/wake。盾遮近臂时必须真实创作被遮挡关节与转身姿势，不能从126裁出一块盾就推定所有状态完成。

当前 hero walk 六姿势循环使用 10fps，idle 基础分支使用 6fps；旧 Armor idle 支路是每 .15 秒换帧，应为新试样明确选择自身时序，不依赖旧分支偶然覆盖。主攻继续采实际阶段时钟。Stone Charge 的实际 windup .9秒、锁向 .45秒，计划 active .8秒，接触可能提前终止、随后 recovery1.6秒；Shield windup .7秒、锁向 .35秒、active .12秒、recovery .9秒。新动作需跟随真实 AtTime/ActiveEnd/RecoveryEnd，不能把六张等时长 GIF 当最终攻击时序。

## 最小诚实的实际试装阶段

建议增加独立 `DungeonFairytaleLookdevPreview` 或同等含义的新候选开关，不复用并全局替换 DungeonCandidateSprites。名称为建议，尚未实现。可使用新的 `/Game/Production/ArtTrials/EV047/v001` 命名空间；本轮只读检查该磁盘目录尚不存在，实施导入前仍要再查 registry 与 disk。

第一步可以是实际 UE 的站立造型观察：新 Hero/Stone idle anchor、明确足线与单独可调比例、当前真实场景/迷雾。该场景不能让不具备动作的静态人偶以旧 walk/attack 身份活动，不称可玩战斗；常规旧版试玩保持独立可用。外置启动说明准确标记“固定造型观察”，不恢复已移除的 UI 来掩盖限制。

第二步是新 idle/walk 均已创作后的移动试样，只有已经具备新动作的试验操作可启用；需要观察步态、脚锁、左右一次镜像、场景前后遮挡与屏幕占比。第三步才是同身份的 SWD 三段链 + 新石骑真正冲锋/盾击/回正/受击/死亡，使用原战斗内核并录制真实输入。若开放跳跃、闪避、技能和拾取换装，也须补齐相应新 clip；不能让自然可触发操作暗中回旧造型后称为统一风格试玩完成。

阶段限制只作用于明确的造型试验入口，不删除或缩减完整首批目标。新 idle/旧全动作混用最多能作为内部缺陷诊断，不应交付为已完成新造型。单张 idle 的平移不算 walk，整图旋转不算攻击，重复同张不算六姿势，尚未完成 clip 不应在 manifest 宣称 coverage=true。

## 导入与运行门

现有 `tools/scripts/ue-import-content-sprites.py` 使用512×512 RGBA、alpha extrema[0,255]与透明角元数据，导入Texture2D后核尺寸；Texture配置为 TC_EDITOR_ICON、TMGS_NO_MIPMAPS、TEXTUREGROUP_UI、never_stream=true、srgb=true。没有显式指定 TextureFilter，不应假称当前采用 nearest。新试样宜沿用高清手绘的采样约定，实际检查缩小后线条和边缘，不默认改成像素美术滤镜。

新 importer 不直接运行旧固定目录脚本。可借 `ue-import-armor-idle-v001.py` 的真实 PNG chunk CRC/解压/RGBA尺寸/透明角验证，以及 task.imported_object_paths、设置回读、真实保存、registry/disk exactset 方式，建立新冻结manifest和新unused目录。旧sprites importer可重用匹配receipt的existing包且写同名receipt，不能把该行为无条件当作新试样的严格防覆盖策略。

制作完一个真实动作子集后再导入它：保留125/126原件、准备转换脚本/数据、source hash、每帧root/foot/hand/weapon metadata、真实动作引用及未覆盖清单。runtime记录实际Texture路径、Clip/Frame、root、显示Size、Facing、ActionId/阶段时间与分层栈，并审看真实短录像。实际进入新路径、整套同身份转接和有效打击前后的图证不可由成功编译或概念同场图代替。新试样与正在执行的旧版专用音效实录应绑定各自Source/DLL快照。

本建议仅给接入顺序，不代表上述动作已经制作或当前工程已导入 EV-047 新角色。正式首批内容单元仍为 0/15。
