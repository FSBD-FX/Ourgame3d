# 非占位玩家移动/装备动作候选 v001

状态：只读核实与可接入方案。未改生产代码，未生成、导入、启动 UE 或验证新的动作运行。源基线、公开接口声明、6份真实导入 receipt 与172项源 PNG/已保存 UAsset 的344次 SHA 核对在 motion-interface-audit-v001.json，全部匹配；导入事实不等于动作验收。

## 事实

当前统一手绘分支支持军剑 Ready4、P1/P2/P3 各6帧；Bound 装备解析仅接无甲与 LGT。不是5武器4甲全状态。DungeonFairytaleSwordPresentation.cpp:133–160 的拾取分支明确 GearPlaceholder=true，播放 Ready0；walk、air、hurt、death、skill 没有本风格完整动作。P2 当前用 V003 标记，Bound P3 用 V002 轴表但继承 V001 图片，不能按旧注释误判未接入。

DungeonFighter.h:24–117 核实19个公开字段/方法；HurtTime、bMoving、JumpVelocity、AdvanceTerminalPresentation 私有。外部测试可读 AnimationName/AnimationTime、GetGroundPosition、GetVerticalVelocity、GetLandingVisualAge、GetMeleeCombatState、GetWeaponActionsState、GetDodgeState 和真实 EquipmentView.Action，不能直接读上述私有成员。

| 状态 | 权威判定/时钟 | 当前缺口 |
|---|---|---|
| 地面普通移动 | 实际碰撞后 GetGroundPosition 位移、grounded、无排他动作 | MoveOnGround:1126 在裁剪前置 bMoving；堵墙也可能是 walk。没有公开“已完成地面位移”DTO |
| run | 没有独立 run/sprint 状态 | 先为现普通速度提供真跑动观感，不能暗加加速机制 |
| SWD P1/P2/P3 | GetPrimaryPoseFrame:677–685，实际 Combat.Time、Start/ActiveStart/ActiveEnd/End，每阶段两帧 | 保持现6帧和 ActionSpeedPct 的实际缩放，不能换100ms展示时钟 |
| 跳/落 | 真实 JumpHeight、GetVerticalVelocity、GetLandingVisualAge | 本分支不靠 literal jump/fall/land 动画名；Ready0不可算空中动作 |
| hurt/death | 真实伤害规则置 AnimationName，SetAnimation 累计/重置 AnimationTime；死亡后专用展示推进 | HitFlash 不等于受击中断；不得为了展示取消合法在行动作 |
| 拾武器/换甲 | EquipmentView.Action 的 Kind/ActionId/OperationId/SourceId/InstanceId/Start/Deadline | .35/.50秒事务；旧装备 held 到真实提交；当前只有 Ready0 占位 |
| Q切武器 | Kind=SwitchWeapon、SourceId=0、真实.35秒，名字同 equip_weapon | 不能仅按动画名误播弯腰捡地面物件 |

名义无加速 SWD 分段分别85/85/60/60/155/155、75/75/60/60/135/135、110/110/60/60/160/160ms；这是现数值解释，不是新增时钟。

## 最小可执行清单

1. 首片先军剑+无甲/新 LGT：一个真6关键位地面循环与一个真4关键位换甲手势。根线程正在制作的新 LGT 来源未冻结进本候选；不得冒用旧图声称新来源已验。
2. 三个逻辑 pose table 在 pose-contract-candidate-v001.json：移动6位（近脚触地/承重远脚过身/抬脚→远脚对应3位）；拾武器4位（撑旧武器/屈膝自由手伸达/回稳/归位）；换甲4位（触旧胸肩/手肘操作绑带/肩膝回稳/归位）。每位须实际身体/关节变化，Ready0平移或重标签不准入。
3. 装备动作按真实事务归一相位0/.25/.5/.75采样，动作取消立即退出；无加速.35/.50仅说明87.5/125ms每位。到Deadline应由真正提交后的 binding 选新皮，不用残留 equip 名决定旧皮。Q 切换另用站立换持姿态，首轮暂不宣称完成。
4. 移动首选已完成地面距离/实际测量步幅决定相位；600ms只可作为候选源预览。265cm/s等速度和各甲属性会变化，按 AnimationTime 固定600ms会滑脚；墙上零位移不前进循环。动作内允许的慢移另明确是否需要步态，首轮不偷扩到攻击/空中。
5. 生成之前测 root/crown、髋膝踝、脚跟/脚尖、肩肘腕、主握点/支持点和每脚接触窗。当前(256,464)是固定展示 pivot，源码明确不是已测脚关节；实际坐标/步幅/新源 SHA 均未知，JSON留 null且标非可导入请求。先定并审核误差阈值，再做像素与运行门；不捏造现有脚锁证明。

## 接口与分层边界

候选新增 FCompletedGroundMotion（目前不存在）：Owner/Run/Room、From/ToTime、From/ToXY、AcceptedDeltaXY、Grounded。仅在碰撞裁剪后真正位置提交点发布；新Run、换房放置、restore/install和teleport只重新播种，不把瞬移计步。初轮可只读真实位置做反例，生产不能跨HUD Draw帧差猜速度。

候选纯解析 FPlayerMotionPose（目前不存在）：Clip、Frame或相邻关键位/Blend、ClockDomain、真实Action/Operation、已提交武器/甲实例、marker集合、有序部件变换。先有可编译声明和真实正常输入 RED，再由 root 决定准入。最小入口是 Fighter MoveOnGround:1146–1158 的真实位移提交，以及 DungeonFairytaleSwordPresentation.cpp:133–160 的 Supported/placeholder 和234–296的投影/层序；binding扩域独立评审，不能只删 LGT 白名单。

现参考层序为 BodyRest→ShoulderFar→Chest→NearArmWithoutHand→ShoulderNear→HelmetForeground（需要时）→独立武器→NearHand。以实际mask/原UV分片，不重新按bbox贴合，不把近远角色随左朝向交换；最终左右只镜像一次，pivot/axis/握点同变换。512源画布、统一尺度、共同根基准；当前72/416源像素到canvas比例不等于物理骨长。

sprite-gen沿已有 component-row/shared_row_scale 管线；当前Ready/P1/P3请求没有 rig/layers，不能称已有骨架。未来数值request必须有真实landmarks/frame_layout，未知值不能假填；上述候选JSON不是有效sprite-request。共享下身步态+真实持械上身profile（SWD单手、GSW重双手、SPR轴杆、XBW枪托/支持手、STF长杖）与4甲材料/附着片，避免20套整身每动作重复；能合并的持械profile须握点实测通过，ROB衣摆/袖和遮挡翻转仍可能需要独有关键帧。

现SWD握点属于HUD手部展示标记，没有投射口。将来扩到XBW时必须保持Actor真实current组件口、公开custom override、每发pre-spend不可变snapshot、真实Jump combatHeight/65门、Actor420 RangeAnchor、launch clearance、弹药/装填生命周期；不能由新画面反写战斗或扩大射程。

## 验证顺序与限界

先决定原生行与真实cutout的小片路线（见 cutout-evaluation-v001.md），再冻结新源/测量；Root先跑新增正常输入语义RED后实现。新增实际门至少含：A/D及W/S斜向位移与停墙；真腿交替/承重脚世界投影稳定；同握点/单镜像/近远遮挡；.50提交前旧甲/末点新甲；移动、受击、死亡取消后旧deadline不变皮/不补交易；Q不会误捡地；换房/恢复不会把放置误当步行。保留旧战斗/来源/保存/音频测试，媒体门单独版本化，旧Ready/P1/P2/P3证据不倒填成新cutout证据。

本候选不包含全部空气状态/技能/20搭配/正式来源D13，也没有新运行或视觉接受结论。当前调用成本与新关节源预算尚未确定，先做小样比较再付费扩产。
