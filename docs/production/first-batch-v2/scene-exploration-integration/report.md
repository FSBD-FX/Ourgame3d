# EV-042 SceneExplorationPreview：真实场景接线记录

2026-10-15，Asia/Shanghai。producer 独占 GameMode/Fighter/RoomLayout/SceneObjects 与新增生产者 Actor 测试；root 独占 HUD/Probe/脚本及 UE 构建、实际运行和媒体；ranged_review 独占另一新增 Actor 测试文件。共享源码，不回退其他作者。

## 事实、推理、风险

基线是实际 `FirstRoom-20261015-105614/index.json` 的严格 64/64、零 warning/error/notRun 与 root 完整 v030 快照。现有 Bound E 仅调用装备拾取，无真正的场景出口路由；旧 unbound 出口判断为 X>600、HUD 门图在 X665，不能把它作为新布局 X1180 的真实终点。旧 unbound 交互直接修改原型 WeaponId/HP，不可成为 Bound 失败后的第二库存通道。

首轮采用一个无收入调查牌和一个真实石骑，布局同源于 `DungeonRoomLayout::FDescription`：入口(-1180,0)、出口(1180,0)、真实侧龛墙 X[-1100,-700]/Y[60,160]、调查点(-920,300)。入口西侧绕行与主路不需跳跃或支付，物理可达性由实际 Actor 测试和后续正常运行证明。调查不绑定 D08 H01/N03 奖励，不新增经济预算；房间对象仅为当前 Run 内存，不是 D13 持久化。

正式 D04 要求未实现免费回程的出口使用风险确认。本预览计划 E 打开 `NeedsConfirmation`，下一次 fresh Enter 请求提交。装备或满槽选择具有优先权；仅真正 NoTarget 才继续场景路由，Busy/失效目标/LOS/距离/选择层不能悄悄过门。同一输入只消费一次。场景提交安排在中央同点全部伤害/死亡之后，不能通过推进 .005 秒避开伤害。

转房保留当前 Run、玩家、装备实例、Ammo/Focus/HP 与绝对技能 CD；只变 RoomInstanceId 和房间内容。离房清旧世界攻击按现有规则，不额外清玩家附着 DoT。`SpawnRoom` 不应每房调用 `BeginEquipmentRun`。当前未实现完整 D07 有限遇敌图、回程图或经济/存档。

## RED scaffold v001

根任务明确释放 Source 窗口后创建：

- `DungeonSceneObjects.h/.cpp`：只读 DTO、当前房及历史房 registry。对象键为 RunGuid/RoomInstanceId/ObjectId，调查1、出口2；查询不分配任何身份。
- `BeginSceneExplorationPreview()`：真实 IntegrationPreview Run、starter SWD/no armor、唯一旧石骑110HP、两场景对象、Enter 开始门。重复同 Run 调用幂等。
- 共享 `FDescription` 是坐标唯一来源。`ConfirmSceneInteraction` 返回 false；墙碰撞、统一 E 路由、调查事务、换房与 CLI flag 消费尚未实现，保留真实行为 RED。
- 未修改 Fighter、旧64组或独立测试。根任务另加一个独立 XBW pose 组，因此预计总数71=旧64+Scene6+XBW1，以 root 实际 index 为准。

生产者新增三组 `CodexDungeon.Content.SceneExplorationIntegration.*`：

1. `RealLayoutBlocksAndGroundBypass`：真实初始配置与无分配读，正常 W 连续移动须被墙阻挡在 Y44，然后由西口地面绕行。
2. `SurveyRequiresFreshInteractionAndNeverPays`：time0 声明一个近距 LOS 小挡板，合法80×40范围内 E 仍应被挡；正常绕行后 fresh E 一次调查，重复/往返不增加收入、来源或实例。
3. `BoundExitUsesActualAnchorAndKeepsRoomScope`：初始化 time0 将唯一石骑 `bAIEnabled=false`，禁止新起攻，随后正常 SWD 输入真正杀死110HP敌人；该标志仍保留正常追踪移动，详细范围见后续运行记录。旧X665不能过门；真实1180 E打开确认，fresh Enter转入同 Run 新房，旧对象保持原房归属。

测试使用真实 WorldContext/physics、UE World.AddController 注册、Possess/InputKey 和 GameMode Tick。只允许初始化 time0 禁止石骑新起攻或布置声明的 LOS 挡板；后续不写 HP、武器、消耗状态、对象 latch 或玩家位置。这个测试夹具边界不等于生产 AI 已关闭，亦不表示测试敌人停止追踪。

此阶段仅完成可编译候选的静态检查。未运行 UE/UBT，尚无实际新 RED/GREEN，也未声称可玩场景、美术、声音、迷雾墙遮蔽或正式来源通过。

## 实际 RED 与 GREEN 候选

root 实际构建 `114225` exit0；`UnrealGame/Saved/Automation/FirstRoom-20261015-114400/index.json` 实际注册71组，65 Success/6 Fail/0 notRun/0 warning。原64全部成功，独立装备选择优先组作为正控制成功；五个 Scene 墙/LOS调查/出口反例失败，另一个失败为 root 独立 XBW pose 桩。不能把七个新增组都记为失败。root 完整 v031 快照778文件/60,778,796B留存实际 RED 源码与 DLL 后，才释放生产 GREEN。

GREEN 候选保持全部六个 Scene 测试及旧64断言：

- 真实注册 WorldStatic Box，玩家与敌人的现有世界扫掠共用该碰撞；生产唯一石骑 AI 开启，Run allocator 赋身份。
- 调查操作只更新当前 Run/Room/Object 的一次 latch；历史房保调查次数，资源与来源无调查奖励。
- Bound E 依据真实装备目标/选择层优先消费。显示目标在本次输入前刚失效时，该 E 终止；刷新后的目标可在下一输入代接纳新 E，避免永久记住数秒前的自动近物。失效规则同时适用于自动和显式目标。
- E 只打开出口确认，fresh Enter 请求提交；Esc或移动取消，战斗/受击状态通过中央重验使失效确认结束。没有 pending 的 Enter 不开新门，持续按住的 Enter 不跳房。
- 待提交请求进入真实当前时刻的零长度中央批次；全部旧窗、新发射及同点伤害/死亡先处理，再重验和提交，不加 epsilon、不提前换房或回滚状态。
- `DungeonSceneExplorationPreview` CLI 与正常 R 都使用同一初始化，保 Enter 开始门；Scene 的 `SpawnRoom` 只创建房间内容，不创建新 Run。
- 真出口使用(1180,0)与80×40范围；同 Run 的 RoomInstanceId 迁移后出生新布局入口，原装备实例、HP/Ammo/Focus、绝对 CD 和玩家附着 DoT 延续，旧房攻击按既有规则结束。免费出口不额外检查“完整安全”或装备事务 ID 计数。

候选尚待 root 实际构建/71组运行。六组 Actor 证据不包含 Canvas fog 像素、自然旅程全程耗时或额外同点致死反例；同点提交顺序目前为源码接线依据，后续媒体与针对性反例应单列。独立测试的 MoveOnGround 是真实连续扫掠，移动本身不推进完整旅行时间，不能冒称正常键盘录像已验。技术初始化故障未提供事务式回滚保证。原型石骑死亡仍有旧 QA pickup 表现，未绑定正式 D08 装备来源；Bound 路由不会落入旧直接改 WeaponId/HP 的交互分支。

GREEN v001 专属十文件清单为 `evidence/2026-10-15_GREEN-candidate-v001/source-freeze-sha256.json`，SHA256 `eb32d6f9cf59bf09aac650dc6895d82d6e2dd7d33e85eabfc55e3df43ff20be3`。GM.cpp `27cdf83800503d1abdb83556f35a00e8fae4aa8cfeb8e5a2114ac667fb0d3d60`，Fighter.cpp `821346b3d9c1c2549f400c8aedd046ce847cecbf8d733c433a7f12bf6b6c5586`。生产者三组测试仍 `82d9e7c1f7404a07a6949d56e5cc3f43a0b31cbb9335fc15ff2840ce434d3b58`，独立原三组仍 `0f2e58ee40b8b214feeabc699d9198e802afcfb6396ec3f3a014da86bdf8a8fb`，旧含 manual 的生产者文件仍 `95a2d7fc5da51effc04262aace30c97eb162d59d4696d3267f3f6d39e61c61e0`。

独立只读复核发现新输入优先级缺口：当前 Scene pending 层先消费 Enter/E，合法 Shift 检查在其后，可能把同批逃离请求吞成确认或无动作。尚未取得该缺口的实际 RED，不能写成已复现。root 维持当前生产源码冻结，安排 reviewer 在自己的 AdmissionReview 文件新增独立第四组（旧三组不改），使总注册数72，再实际验证 Shift+Enter/Shift+E 后释放窄修。D11 的其它世界键与确认并发仍需各自证据，不能把 Shift 范围扩称完整实时输入层通过。root 的 `115646` 构建失败为其 HUD literal Printf 写法，未运行 UE，不是 Scene 行为失败。

## 实际72 RED与第二候选

root `FirstRoom-20261015-120500/index.json` 实际72组，70 Success/2 Fail；旧64全部成功，原六个 Scene 组中五个成功，root XBW采样组成功。root v032完整快照780文件/60,954,706B保存此源码/DLL后才释放重排。

独立第四组 `LegalDodgeOutranksPendingExitConfirmation`（完整文件 SHA256 `34587bfb8dd0028df8421e8fd6a0d1fab163d5de84662352b4ed6164d2962a6a`）确证四个同时fresh输入对子：Shift+Enter、Shift+E、Space+Enter、J+Enter，八条真实动作/房归属断言失败；当前地面待机/ready状态及两键同一PlayerInput批次前提全部通过。真实先闪避再在未改冷却内发非法Shift的正控制通过，不能把非法Shift当关闭层借口。

另一个失败是生产者墙/绕行组。真实 nearface 阻挡断言已通过，后续正常 waypoint 移动未到；原错误未记录具体轴或起终点，因此此时不能归因于夹具或世界扫掠，更不能换路线、调高容差或声称绕行已过。

v002只改 Fighter 已复现的优先级并增强生产者诊断：Esc先纯取消；移动取消；按现有Dodge→Jump→Skill→Primary→Switch→Reload顺序，仅成功接纳的世界请求关闭Scene层；最后才处理Scene Enter/E。无效世界请求不会自己关闭层，旧64模式保持既有行为。GM的墙/移动生产逻辑未改。

生产者 `MoveAxis` 仅增加失败时 axis/target/initial/lastFrom/lastAfter/delta/dt/stalledSteps/sim 及只读18×16原形状世界扫掠的H.Time/初始穿透/深度/两normal/deltaDotImpact信息；1600步上限、路线、容差和所有断言不变。新生产者测试 SHA256 `efdd634888a0653a6250e4ffd25cb7bbc5ffd019f56ea9b9ef4d62380f0924ea`。Fighter.cpp SHA256 `39495cc9a5a114b10817e70a21352e8f14dd4285c215bcf2fa4e7054936e5b8a`，GM.cpp仍`27cdf83800503d1abdb83556f35a00e8fae4aa8cfeb8e5a2114ac667fb0d3d60`。专属 `evidence/2026-10-15_GREEN-priority-and-waypoint-diagnostic-v002/source-freeze-sha256.json` SHA256 `9917115696542825ab4eadcee1fd1d116e76091ba31faf9282a6da83f60915ea`。

v002停源等待root实际72诊断，未声称全GREEN；其它实时UI/手柄/重绑、多键、箭头导航及同点致死边界不由这四对子覆盖。

## 原生零深墙接触反例与第三候选

实际 `FirstRoom-20261015-121240/index.json`（SHA256 `b5e431a8ce2d344816a7a1de79cd8721035c1c2edba776ffc9d4c68ec255647d`）为71 Success/1 Fail/0 notRun/0 inProcess/0 warning/1 error。输入优先级第四组及非法Shift正控制成功；唯一失败仍是生产者墙后路径。

诊断事实：normal S的Y目标0，实际起点/末点都为(-920.00000001279682,44.000000596418943)，1600步无进展。同样18×16扫掠请求到Y38.700000714883174，原生碰撞返回Time0、startPenetrating=true、PenetrationDepth0、两normal均(0,-1,0)，位移点乘impactNormal为+5.2999998815357685。这是向墙外分离仍被时刻0接触拦停的生产行为，不是不可走路线或坏夹具。root v033完整快照780文件/60,957,294B保留该实际证据后授权修复。

v003限定放行域为真实WorldStatic UBoxComponent、worldQuat严格identity、严格水平轴单位impactNormal，以及Time==0/startPenetrating/depth==0/位移点乘normal>=0。凸轴对齐盒的该面初始接触中，线性离面或沿面移动不进入该面；仍遍历其它hits。向内、正深嵌入、未来碰撞、旋转盒、非盒及不明确normal保持旧保守阻挡。不增加epsilon、不修改碰撞尺寸/布局/角色统计/时钟，不扩到任意mesh或旋转几何。

生产者在原nearface断言后新增实际X -940→-920沿面往返与再次W向内仍止在原Y44的控制，再完整保留原S回0/西口绕行和所有旧阈值。新控制是GREEN验证补充，原121240 RED只证明分离失败，不能倒填成已复现切向失败。

v003 GM.cpp SHA256 `4a03b782b27cbe8c501fee30f80f16f3cbb3d37ccc3f1d81738ee76a825ceb7b`；Fighter.cpp仍`39495cc9a5a114b10817e70a21352e8f14dd4285c215bcf2fa4e7054936e5b8a`；生产者测试`3d1246f5b1ce7d2a1681692c1caa8ebc3bfa69d22e28b1f9c7233da0643a87f9`；独立四组仍`34587bfb8dd0028df8421e8fd6a0d1fab163d5de84662352b4ed6164d2962a6a`；旧64文件保持冻结。专属 `evidence/2026-10-15_GREEN-zero-depth-box-face-v003/source-freeze-sha256.json` SHA256 `d0412cb5ea59675b048f64b748ab53a244a4c3ffddc50a08aded9ac6a2566e3e`。独立只读复核认可这个严格域，尚待root实际72重跑及独立正常输入Scene录像。

## 实际72 GREEN

producer 独立读取 root 实际 `UnrealGame/Saved/Automation/FirstRoom-20261015-121909/index.json`：72 Success/0 Fail/0 notRun/0 inProcess/0 warning/0 error，SHA256 `697c58e7dc0bf3f01a9c1cf64f939e658eed8d4dfdbec513880a7007c9daec02`。GM.cpp与生产者测试逐项重核仍等于v003冻结，原64及独立四组未改。原64、root新增XBW采样1组与Scene七组实际全部成功。

本次运行覆盖：真实物理墙nearface、两向切向往返、再次W向内阻挡、S离墙、原西口地面绕行；近距真LOS拒绝、一次无收入调查与重复/往返；真实SWD清场、旧665拒绝、新1180确认/Esc/freshEnter；同Run实例/实耗Focus/绝对CD/旧房对象历史；四组fresh世界输入竞争以及非法Shift正控制。

这关闭本轮真实Actor接线与两项已复现P2的窄范围。producer未运行UE/UBT，由root统一实际执行；root完整源/DLL/资源v034已冻结781文件/60,963,332B，默认strict脚本据实际结果提升到72。之前v031/v032/v033及对应失败报告全部保留，不倒填新控制或媒体。该阶段记录时root独立Scene13正常输入录像正在运行，其后续结果见下一节，F/E保全/审看另由root记录。Actor自动化不代替Canvas雾像素、正式场景/敌人美术、声音、真实掉落来源、完整D07路线、完整D11输入层或D13持久化。旋转/非盒/正深接触仍保守；同点致死Scene反例、其它多键/手柄/重绑仍需单独实证，不能把72GREEN扩成全域完成。

## Scene13 定向运行与原生道具导入 v001

Scene13 v001前七项通过，接近石骑阶段超时。只读根因核对显示，`bAIEnabled=false` 在 `MakeKnightFrame` 中只关闭 `CanStartAttack`，Target/LOS继续输入纯核；Idle仍以185cm/s追踪。旧录像夹具要求到达实时变化的敌人X−70后停稳0.20s，追踪会在该时间内移动37cm，使接近目标持续漂移。该失败不能称为新冲锋复现，也不能通过固定位置、HP或敌人状态完成录像。reviewer只修改正常输入夹具，进入实际SWD合法命中范围便释放移动并正常J，增加真实敌人坐标/阶段/起攻权限trace，未改变生产追踪行为或13项门槛。

producer已读取 `F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v002/原件/runtime-report.json`：profile为`scene_exploration_normal_inputs`，`passed=true`，13项全部通过；SHA256 `b09a217635bdd631cb32969d7a8e201b724a0495764c32aaacd5f97c7748155a`。这是初始化sim0禁止新起攻、仍有真实185cm/s追踪的定向QA运行，玩家后续正常移动、J、E、Esc、Enter；普通Scene试玩仍开启攻击。该v002结果归属于原v035/v002来源，不覆盖之后的文案、雾下道具/标签、位置与新原生纹理候选。

root随后实际执行原生道具导入，commandlet exit0、0 error/0 warning。producer独立读取并核对 `UnrealGame/Saved/Bootstrap/scene-exploration-props-v001-import-20261015-045356-046228.json`：`expected_count=actual_count=saved_count=2`、`success=true`，回执SHA256 `b48cc7d82ddfbc976d7c7401243d78c53b4312620131b9df3d93d3f16c09c15b`。冻结manifest为 `source-assets/production/scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json`，SHA256 `a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969`；新包位于`/Game/Production/SceneExploration/v001`，仅两张512×512 RGBA Texture2D，不覆盖旧包。

两源PNG、实际设置、root/单一比例与foundation的详细证据见同目录 [native-props-integration-v001.md](native-props-integration-v001.md)。当前只读HUD候选把墙root(256,408)按260/478统一缩放，锚到实际墙近边(-900,60)；碑root(256,431)按0.18统一缩放，锚到调查点(-920,300)。两轴均再乘同一UIScale，未将道具PNG拉伸到碰撞框。墙的共享400×100cm AABB另绘实际260×38逻辑像素石质foundation；源图隐藏后脚点仍为`inferred`，该组合的完整运行对齐尚未验收。

同一后续候选还修正开始成功后的过期“Enter开始”提示，以及取消出口确认后的继续探索提示；死亡/新房最终文案不应被内部取消覆盖。该记录写入时root正在统一构建新HUD/GM候选，尚无其新运行通过证据。导入回执仍明确`runtime_verified=false`、`formal_scene_accepted=false`、`wall_full_AABB_alignment_verified=false`；不得将此前72 Actor GREEN或Scene13 v002倒填为新道具、雾层、取消帧、美术/音效、正式D08来源或D13通过。

## 后续主线程v003验证

后续root构建`build-editor-20261015-125830.log` exit0，实际`FirstRoom-20261015-125946/index.json`严格72 Success/0 Fail/0 notRun，零warning/error；producer已读取该index，SHA256 `8fa0e0bcebeab36c90031f37f9b5f1758282ac085cda89e3ed09991d9c1254dc`。root v036完整快照786文件/61,282,531B，录制DLL SHA256 `95b534b86a8de3df6c5058c3c02d2da6cfef8df6c8ffec12a8959269bfdce2dc`。该结果是新的同版本运行证据，不改写此前v002来源或导入时尚待运行的事实。

producer已读F原批 `F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v003` 的index与runtime-report：13/13通过，无missing/failed；index SHA256 `91c4f38629b6ff5b67e533ef46476478b927e9d88462768fe0118a40570831b2`，runtime-report SHA256 `1e085e86f605140c94baaba839ed522b5e06f6497b67f838aef3add255c65568`。739电影原帧加1预热帧，共740原生PNG逐像素CRC通过；墙钟24.650808099657297s、UE主混音24.64s、差0.010808099657296566s，音画门与全流解码通过。保留引擎原WAV，展示副本只修BlockAlign头且PCM一致；这些门槛不替代听感、逐sample同步或性能验收。

E留档 `E:/OurGame/Knight/过程图稿与视频/2026-10-15-OurgameUE-原生墙碑探索13项-v028` 的`source-size-SHA256.json`记录751文件/2,748,361,512B、两遍核验、大小/SHA零差；该索引SHA256 `bc62f2f66c07d6be719aa732a9aec62180490a84fd708897ddf1a69da9ffe267`。producer另读E实际副本index/runtime-report，其hash与上述F文件分别一致；本次只读既存保全证据，未重新复制或改归档。

详见 [主线程运行复核 v003](../runtime-review-scene-exploration-v003.md)。root已实看MovieFrame64/170/182/264，独立8+1帧复核另记。只读trace映射在近碑170/182记录真实墙、碑两条Texture路径、`survey_whole_prop_rendered=true`、visibility/memory均1；退回264为visibility0/memory1；新房738仅墙路径、surveyRendered=false、visibility/memory均0。纹理路径与原帧是13项之外的补充证据，映射采用最近捕获完成戳，不能冒称GPU逐帧同点。

本次仍为sim0只禁新起攻、保留正常185cm/s追踪的定向QA；普通Scene试玩攻击正常。墙root/单比例与实际共享foundation已在该来源运行，但隐藏后脚仍inferred，不能据此宣称完整AABB图像精确匹配或全遮挡通过。碑近距仍部分被人物遮挡，全部碑纹可读、正式美术/声音及完整内容尚未验收；旧QA战利品未接正式Bound来源、D07/D08/D13等既有边界不变。
