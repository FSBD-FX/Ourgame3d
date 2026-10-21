# 当前英雄显示缺口：v128 只读审计

事实：实际 v128 的213个 Source 文件与1210个 Production 文件，均按已编译
manifest连续两遍大小/SHA核对零差；原 full176 报告原件核实176成功、零警告/
失败/未运行。这是已有构建证据，本审计没有运行UE、UBT或新测试。19份关键源码
原字节保留在 source-reference，准确版本在 exact-v128-source-content-pins-v001.json。

最关键的前提纠正：启用新军剑 presenter 时，Dodge/Hurt/Death **不会**落到旧
human120。Presentation.cpp:160标记Supported=false，但177–181仍选Ready0，
256固定canvas=72*512/416，258和305的return true拦截旧分支，301只画Body。
所以实际问题是**静态bareReady0遮掉真实动作、无剑无甲**。缺资源时258还会保持
拦截而不画身体。HUD.cpp:1013是入口。原生截图如显示体型/身份差异，须另记
实际视觉现象；不能用猜测替代这条源规则。

| 实际状态／判定 | 新Bound SWD+None/LGT当前画法 | 资源、尺寸与切换规则 |
|---|---|---|
| Ready | 真4帧+独立剑；LGT专层 | EV048/v005 HeroSwordBody Ready000–003_v002；LGT v012胸/双肩；每.167s循环。Presentation:148、177–180 |
| 普通地面Walk | 真6帧距离相位+剑；LGT专层 | EV048/v016 HeroLeatherWalk8组件×6；80 world/.498s为调参循环，非脚锁。Presentation:154–159；WalkData:12–24 |
| 地面SWD P1 | 原生动作6位 | v005 SwordPrimary1_v002整体校验，v007独占身体分片，LGT v013胸/双肩；真实阶段/速度映射。Presentation:139–141、179；Fighter:744 |
| 地面SWD P2 | 原生动作6位 | v009 SwordPrimary2_v002、V003 marker，v010身体分片、LGT v014；Presentation:142–144、190–195 |
| 地面SWD P3 | 原生动作6位 | v011 SwordPrimary3Body+身体分片，Bound V002 marker/axis、LGT v015；Presentation:145–147、187–189 |
| Shift Dodge | **bareReady0；丢甲丢剑** | 原生Dodge仍.40s/185 world，有实际受阻/取消/iframe；Fighter:801–802，Dodge.h:11–15。缺本风格6位动作，6仅为首片建议 |
| Hurt | **bareReady0；丢甲丢剑** | 真poise-break才置hurt/.4s并中断动作；普通HP损失仅HitFlash不应强制Hurt。Fighter:1503–1528。缺真受击与回稳 |
| Death | **站立bareReady0；无尸体姿态** | bDead后实际AnimationTime仍按terminal presentation推进，SimulationTime冻结；Fighter:1799–1805、GameMode:1889–1894。缺倒下与稳定尸体，不能用冻结SimTime采样 |
| Jump/Fall/Land | **被高度投影抬起的Ready0**，落地可能直接恢复Idle | 当前新分支只有JumpHeight投影，没有空中身体pose；旧通道才按垂直速度/landing age选4/2/2。HUD:1121–1129，Presentation:263–270 |
| SWD空中Primary | **bareReady0，无剑攻击姿态** | StartedAirborne使三个ground Primary分支均不成立；Presentation:139–147。缺6位空中攻势 |
| SWD Secondary/K技能 | **bareReady0** | WeaponActions真实发射/前移/伤害继续；新Supported不含技能。Fighter:946–948；缺技能动作，不能以静态Ready代替 |
| 拾武器／换甲 | 明确GearPlaceholder：Ready0+**旧已提交装备** | 仅真正PickupWeapon/PickupArmor、Source/Action/Operation/Instance有效，.35/.50真实事务；提交前不穿目标皮。Presentation:162–175，GameMode:998–1003。缺真实伸手/绑带/回稳手势 |
| Q切武器 | **bareReady0**；并非上述GearPlaceholder | Kind=SwitchWeapon、SourceId=0、.35s；与拾武器虽同名equip_weapon但不能共用地面拾取手势。GameMode:1015–1020，Presentation:165–169 |
| XBW reload／其他武器动作 | 在此全局presenter下**全部bareReady0** | Binding只准SWD；旧XBW分层reload分支被HUD:1013提前return挡住，不能把旧已导入XBW6/4帧算新钟盔覆盖 |

所有新分支画布均88.6153846×UIScale；72是站立身体416个源像素对应的名义显示高，
不保证每个动作的可见bbox恰好72。Root256,464是显示pivot，不是已测物理足点。
左右是同一源镜像一次；不能再互换近远角色或改战斗距离。

| 路由 | 当前资源与尺度 | 事实边界 |
|---|---|---|
| Bound flag+SWD+LGT/None | 上表新资源与bareReady0；canvas88.615 | 仅这些已提交组合能通过Binding.cpp:107–118；仍非全状态 |
| Bound flag+MED/HVY/ROB，或GSW/SPR/XBW/STF | Binding拒绝，仍被同一presenter接管为bareReady0 | 不会自动放回旧“完整20组合”。Presentation:132–137、160、177、301–305 |
| 只启新SwordBody等旧试装flag，无Bound flag | SWD按旧试装条件，其他不支持状态仍bareReady0 | 不能作为真实装备已提交的授权；旧旗标可能启用试装甲。Presentation:134–137、201–213 |
| 不启上述presenter，CandidateSprites启用 | FirstBatch/v006 Hero通用14状态；Walk v007；canvas120 | 旧manifest身份为EV042圆封闭盔小骑士，不是当前钟盔。HUD:633–644、1084–1139、1249；可选旧甲/XBW分层flags另有局部覆盖 |
| 两种presenter都不启 | Prototype/FirstRoom/Sprites/Human；canvas112.5；缺图时程序化图形 | HUD:622–630、1161、1279–1286，PresentationScale.h:7–8；这才是代码明确名为Human的来源 |

20组合=SWD/GSW/SPR/XBW/STF×LGT/MED/HVY/ROB，不含None。新钟盔当前只有
SWD+LGT这一格的部分地面动作；**0/20全状态美术验收**。其余19格不能只删除
Binding白名单便宣称支持：四套甲材质/轮廓与五类握持/动作/装填仍无对应新源。
旧20组合Gameplay/属性/保存测试成功，不证明这20格的当前新角色美术。

可复用：已有新风格Ready4、Walk6、地面P1/P2/P3各6，共28身体相位；相应exclusive
body/hand/helmet分片、LGT胸/双肩及独立军剑可作现有动作资源与身份锚。已实际读取
178条导入manifest源PNG与盘上UAsset，包含28整体身体相位；这不是全部绘制依赖
数量，额外分片另表补齐。来源/尺寸/实际RGBA/SHA见existing-new-style-reuse-v001。
完整当前None/LGT且全Leather flags依赖另补runtime-current-resource-inventory-v002：
加3份独占身体分片manifest后286条，排除66条本路由不画的通用试装甲，得到220条
整体校验／身体分片／LGT纹理依赖，加1独立剑共221。全部实际盘包与v128原pins
匹配；这不把仅校验的whole Body算成同帧实际绘制，也不扩大为20组合。
现fairytale-hero-v001只有idle/walk及步态单相修订。限定搜索fairytale目录只命中两张
Guard死亡参考图，不能冒作Hero死亡。fairytale-player-motion-v001是旧方案，文件自身
明确不含newStyle air/hurt/death/skills；其中Walk“尚未实现”的历史说明已被v127超越，
不能照抄为当前事实。

旧v006确有74逻辑帧/68唯一PNG：Hurt/Dodge/Death各6、jump4/fall2/land2、airPrimary6、
secondary6、equip6等。装备两行共用同6图，其manifest明确EV042圆盔身份，能参考
关键位/时序，不能缩小或改名后算新钟盔。所有74逻辑源/盘包在legacy-state-reference。
未实际审看图片，不能推断它们与新体型的解剖、手握或遮挡契合。

建议先完成SWD+None/LGT的Dodge/Hurt/Death；minimum-art-state-contract-v001.json
给每类6关键位提议，但新源、Root/Grip/Axis、持剑/尸体武器处理均留空待真实供给，
不是可导入sprite request。身体要真实屈伸、压缩、倒下，甲与握点随之变化；既有
Ready/攻击片只有匹配部位可局部复用，不能整张Ready0平移/旋转。重甲/长袍及双手
GSW/轴杆SPR/枪托XBW/长杖STF需各自实测profile；不预设20套整身重复生成，也不
假定同一上肢pose能同时适合五种武器。

可执行下一步：先保留本轮真实Shift原片，运行audit-native-hero-dodge-trace-v001.py
--report <Root已保留的实际runtime-report.json>，脚本只读并以exit1标明Ready0/丢甲
观测，缺真Dodge数据exit2；任何0结果也不代表视觉通过。Root选定上述首片姿态和
来源后，再按真实PNG/marker冻结，先做少量正常输入RED，再接状态专用采样与LGT
分层；保留既有权威动作、命中、装备提交/取消、terminal展示与恢复时钟。随后依次
补空中/技能/拾取/Q，再扩其他武器与四甲。资源未供齐前不交生产修复，不新增Ready0
遮挡问题，也不把旧human/旧圆盔作为合格兜底。

风险：仅改尺寸会让旧体型变小，状态与装备丢失仍在；仅开Binding会把不匹配握持/甲
层混装；用GameOver冻结的SimulationTime做死亡动画会停在首帧。实际视觉仍需Root
E留存后审阅。本审计未生成/查看图、未付费、未导入、未改Source/Content/tools/状态。
