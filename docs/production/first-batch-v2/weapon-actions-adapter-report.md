# SWD001 武器技 UE 适配记录

日期：2026-10-15，Asia/Shanghai。当前为 Task1 可编译 RED 准备：仅接口桩和两项 UE 测试，未实现技能、未接 K/右键或碰撞、未构建/启动 UE、未提交/生成素材。

## 真实起点与范围

根线程的 `test-logs/ue-stone-feedback-GREEN.json` 已读取：20项全部通过，石骑事件journal和终局表现均有实际结果。本轮保留上述代码，不回退之前甲准入/跨房/终局修复。根提供首单元运行16检查通过与源码/DLL冻结备份，相关录制由根负责；该结果不替代新技能验证。

只负责 SWD001（和现有 sword 原型别名）零资源武器技。已有 DungeonWeaponActions 核用于真实技能时间/锁点/CD/事件，三段主攻继续用 Combat 域；Focus 仍由 Fighter 现有路径负责，WeaponSkills 内部资源字段不得扣费/恢复/镜像给 HUD。schema2外部Focus API虽已独立验证，整角色迁移仍在后续任务；本轮不接STF/其他技能、Dodge、掉落/来源/存档，不能登记五武器完整接入。

## 冻结接口（桩）

- `bool TryBeginWeaponSkill(bool FreshPress=true)`：当前返回false，供真实RED；未来只接纳地面、完整先前动作结束、实例CD合法的新按下。
- `const DungeonWeaponActions::FAction& GetWeaponSkillAction() const`：只读技能动作，不暴露另一份角色Focus权威。
- `double GetWeaponSkillCooldownRemaining() const`：当前返回0，未来读实际实例deadline与核当前时间。
- `const DungeonContentCombat::FCombatState& GetMeleeCombatState() const`：只读主攻链/缓冲/当前动作供诊断；测试在技能接纳当刻检查清链，避免.68s技能结束时原.45s续段已自然过期导致假通过。

未来表现名固定 `AnimationName="secondary"`。HUD须读技能Action自己的.20/.10/.38阶段；不能借普通Combat的GetActionProgress猜技能帧。

## 新增真实 UE 反例

文件 `Tests/DungeonWeaponActionsAdapterTests.cpp`，共2项，总suite=22（原20+新2）：

1. `CodexDungeon.Content.WeaponActionsAdapter.SwordSecondaryRealWindowAndBlockedStep`：实际authority/physics world，核对.08锁、4.08CD、.20先前踏最大30，再查145×40前半椭圆；石骑45甲下32名义物理损HP约22.0689655；石骑无原型无敌时同窗不重复扣血；原型后来进入窗可伤；椭圆角落排除；18+24身体在中心距50时截为8cm、不得从虚假30cm站位查伤害；注册WorldStatic墙的前缘45与玩家半宽18截为27cm。零成本不动Fighter已实际消费后剩余50Focus。
2. `CodexDungeon.Content.WeaponActionsAdapter.SkillRespectsFullRecoveryAndClearsOnlyAcceptedChain`：活动主攻后摇拒技能且保原.12s输入缓冲；合法技能立即清链，held失败不清；技能不被jump/switch/主攻/换甲覆盖；.68完整结束、CD仍拒再次技能；普通未破韧正HP损失保动作，真30韧阈值中断且不退已锁CD/不发未来步进。

测试调用真实GameMode.Tick和角色受击/动作入口。物理K/右键别名合并与按住不重发，后续实现时仍须真实输入证明；该测试使用fresh参数只证明意图层边界，不冒充键盘/鼠标设备验收。Dodge不在此次接入，未以不存在的dodge入口假测攻击取消。

先交根线程构建、取得可运行断言RED；然后再最小实现。现测试/桩状态不宣称功能完成或新项通过。旧核/Driver/Feedback/HUD/Probe均未修改。

## Task1 GREEN 候选：真实 RED 后接线

已读取 `test-logs/ue-swd-skill-RED.json`：22项中原20项全部通过，两个新增项分别失败8/11条断言，符合未接纳/未执行技能的缺失。本轮才实现四Actor/GameMode文件，不改测试、纯核、Driver、HUD或Probe。根线程将统一下一次构建/22项；当前未执行引擎或构建，尚未宣称GREEN。

`TryBeginWeaponSkill` 只对SWD001/sword别名在真实权威GameMode当前时刻接受fresh地面请求。需先通过原动作、受击、换甲与CD门；成功后才调用Combat的ExclusiveAction清地面链。拒绝的请求不清链/缓冲。技能使用冻结核原始.20/.10/.38时轴和.08锁点，不改核数据。新增 `GetWeaponSkillTime()` 只读double；AnimationName=secondary、AnimationTime=核Time-Start，Actor的AttackTime/phase也镜像技能剩余完整动作，挡住主攻/jump/switch/甲重叠。普通未破韧伤害不动技能；真实破韧/死亡向技能核传真实中断理由，关闭剩余近战窗，保已锁CD。

每次GameMode动作批次冻结运动前后真实XY/高度与旧无敌截止时刻。ForwardStep实际事件仅消费一次：在该事件时刻对玩家18×16身体做场景WorldStatic/WorldDynamic箱体sweep，并对冻结的真实角色身体连续求交（石骑24×20）；中心边界仍X[-700,700]/Y[-200,220]，阻挡只截短30cm，不改变完整后摇或CD。实际位移提交到Actor后，同点ActiveWindow才开始查询；不根据动画臆造位移。

持续窗沿每批冻结线性轨迹对前向椭圆145×40、最小距离及65cm高度区间求交；保留整个[ActiveAt,WindowEnd)中的后来进入机会，旧无敌截止前不消费receipt。LOS实际查询通过后才加入PendingDamage，与其他已接纳命中同批提交。技能命中key由独立的`FSkillHitReceipt{ActionId,SubhitId,TargetRuntimeID}`类型承担；不复用Combat普通主攻AttackId或MarkContentHit。新技能仅在成功接纳后清已结束旧技能的窗口/receipt；剩余窗口在破韧/死亡时关闭。已排队同点伤害不被后续中断回滚。

前踏是瞬时动作事件；本批技能自己的连续窗使用“原运动轨迹+实际前踏偏移”求解，后续敌Driver收到更新后的真实玩家终点。Driver现有接口仍把一次批内目标路径视为起终点直线，尚无瞬时跳点的分段轨迹接口；若石骑冲锋与玩家前踏在同一个最多.005s区间相交，严格事件时刻的联合接触仍需独立边界复核，不能据此次SWD单元测试称该跨动作联调完成。普通输入移动仍沿已有原型移动路径，本轮没有顺带实现Dodge或全局身体运动适配。

K/右键fresh按下先合并一个bool，成功技能接纳后本批不继续J/E/Q；Space合法跳跃优先且该批不再起技能。保持原有WASD方向；技能仅未锁时允许输入改变朝向，锁后不反向取消或追踪。暂停清缓冲入口同时清两核。仅真实起落通知技能核Grounded以保持时钟合法，不让其新增另一份角色空攻授予权。

技能核Context.FocusRegen=0，SWD定义零Focus/弹药；不读取、花费、恢复、镜像该核Budget到角色。Fighter原Focus/FocusConsumeAge与既有SpendFocus仍是目前唯一活资源路径；schema2纯核只读SHA为`574b8090884b4ac2a30693fde1dbd7367f005a923edc6891affb510bd57b82db`，未修改。切换普通武器和跨房不重构技能核；仅Reset新局按原语义重建。此处只有临时QA实例1及内存命中/事件游标，未接正式获取或D13磁盘存档。

声音仅在经过EventId防重的真实ActiveWindow首次消费时播放既有`SW_AUD_SWD_WHOOSH_03_v001`，音量.25；资产路径已核实存在。持续窗口扫描和HUD绘制不播风切，落空不播金属撞击；命中声音仍由真实受击/journal路径负责，没有新生成或付费API。

待根节点22项GREEN以及真实K/右键 FirstUnitSkill输入记录、正常与身体/墙受阻录像审看。测试文件保持RED版本原样；既有20项、反馈及终态逻辑保留，不把静态阅读代替构建/试玩证据。
