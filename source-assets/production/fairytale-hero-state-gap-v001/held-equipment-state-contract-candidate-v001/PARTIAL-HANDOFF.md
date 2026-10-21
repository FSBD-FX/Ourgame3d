# 218–220 持物/遮挡最小合同（已核实部分，待最终冻结）

事实：13张身体已由Root认可source pose；registration、装备和native均未验收。Dodge0–3近手闭合；Hurt1近手张开，其他Hurt近手闭合/蜷曲但没有实测柄轴；Death0放松张手、Death2–4撑地/贴地。因此空手身体不是已经支持五武器的持握身体。

实际五武器：SWD单手短柄；GSW双手握同一长柄，旧prop主握169,256、副握101,256；SPR两手导杆，旧prop主握137,253、前支撑326,253；XBW后握128,253、前支撑337,282，后续有空弦/已拉无箭/装填及中立历史外观；STF旧manifest明确主握181,251，副握282,251只是optional support。这些是旧prop自身的测量，不是新钟盔身体socket。STF可作为单手候选分支，但长度、灯头重量、肘/杆遮挡均须独立验证，不能直接认证复用SWD。GSW/SPR/XBW三类双手距离/方向各异，不能同套上肢硬贴。

最小首片仍为SWD+None/LGT。Dodge先用现4姿测真握柄接触和本帧NearHand mask，四帧全程握住；若任一闭拳实际不能围柄，再做针对该完整动作行的新native纠错源。Hurt必须全程保留装备。Hurt1不能拿Ready手/mask盖上：优先NEW Hurt4标准row，只纠正pose1握手语义、保留压缩/后仰/回稳关键位；整行重新shared提取/保全/View，比在旧13帧中局部画手更可审。无充分握轴导向之前不调用生成。

Death最小选择为age0即已释放，沿现5张关节collapse身体；单独现有prop从作者化的Death0手旁起点移动至同ground-Y的角色外侧，age.4前后完成一次纯表现落地（时间只是待审美术提案，数值合同未填），后续保持。武器不再声称握在开掌里；不存在新Actor/SourceID/拾取标记/金币/碰撞/伤害/投射物/装填/库存Drop。终点、倾角、地面接触像素、遮挡、连续standing root及release transform全部null，先实测/作者化后填。Death各帧固定canvas88.6153846，不按alpha高度放大。最终持物按已提交实例显示，未装备背包物不额外画。

死亡轨道应由现有AnimationTime与profile直接求值，可跳帧seek而不重播；如果当前合法存续路由接受该dead状态则由已保存相同年龄确定性重建，不新增玩法save字段或改RootV2验证。若从最后活姿动态捕获release矩阵，须另外解决真正可保存的确定性，这不是最小路线。跨攻击/Shift死亡的第一帧位置连续性仍需实机验证，不能预称无跳变。

护甲：当前新LGT采用已准入的紧凑胸/近肩/远肩构造与材料，不因旧design_only“褐色皮衣”文字自动改款；四甲实际旧路由证明不同front/back及ROB近袖需求，但旧圆盔像素不能贴到新钟盔。MED的环甲/开衩、HVY宽胸/大肩/厚胫、ROB长袍/窄袖/下摆需要各自新姿覆盖与前后遮挡；不能缩放LGT算它们。Dodge/Hurt低姿与Death倒地必须按实际胸/臂/盔交叠分片，不预填统一层序。

下一轮最少清单：先1条Hurt4纠错body row；Dodge三件LGT各4相位（胸、近肩、远肩）最多3条row。该4次请求只覆盖首片准备，不等于完整三状态。完整SWD+当前LGT三状态另需Hurt/Death三件各4/5相位：最多9条LGT row、39个组件位，加Hurt4即最多10请求/43位。确实完全被遮的far shoulder应显式author-null，不强画可见片；精确phase-count须先完成visibility表，所以39是上限而非锁定订单。不新增Dodge/Death身体、不重画五个刚性prop，不生成20套整身。其他武器暂仅给可复用下肢/躯干/Death脱手身体的候选，双手上肢新增清单须在第一轮真实握距测量后按家族逐步开单。

后续所有bodyNearGrip、farSupportGrip、handleAxis、weaponScale、handReplayMask、armorAttach、deathRoot/settledTransform均null；已有可见手套表面点只能定位待测区域，不能冒充柄心/骨点。最小可执行次序：真实partition与姿态握点guide→Hurt纠错→全帧source E保全/View→四帧Dodge持物静态合成审→LGT三row→Root正常Shift、poise-break、death及合法存续短片。20格逐格审，None在20之外，当前无任何新三状态装备格通过。
