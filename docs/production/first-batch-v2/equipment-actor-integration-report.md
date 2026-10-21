# 真实装备Actor接入UE验证记录

2026-10-15，Asia/Shanghai。当前真实装备Actor接入切片已取得严格GREEN：第二轮UE构建exit0，38/38 Success、succeededWithWarnings0、failed0、notRun0、inProcess0。新9组和原29均无警告，Tests仍为冻结a13c版本。首次实现的37 Success＋1警告以及更早29 Success＋9 Fail均保留为历史事实。root唯一执行UE/UBT；save_state负责Actor与runtime文件，stats_review仅写新DungeonEquipmentAdapterTests.cpp和本plan/report。首批内容完成数仍0/15，真实来源链与D13磁盘同代尚未完成，正常控制器输入实录待root实际验证。

纯核前置已冻结：Inventory77/0、WeaponActions179/0、Stats原16,406、公开API联合10/0、独立修复审查19/0。它们不能替代真实E/Q、.35/.50时轴、同点损伤或世界源消费。v012旧DLL对应整数弹仓P2修复前源码，不能用当前头解释旧录像。

计划分9个UE组，详见 [equipment-actor-integration-plan.md](equipment-actor-integration-plan.md) 末节。独立测试按正常GameMode/Fighter行为与只读权威状态验证，不编辑任意快照或原29/Explore26测试。空桩真实RED与首版实现实际运行结果见下文，历史“待执行”段落仅记录当时状态。


## 首次UE行为RED待执行（历史，实际结果见末节）

新测试文件：`F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentAdapterTests.cpp`，31591字节，SHA256 `450391f49c6b2d17165244b1e54661789d310ce31eed6e90af4109e687b5a99c`。9组`CodexDungeon.Content.EquipmentAdapter.*`加原29，总预期38。Source已冻结，未本地启UE/UBT。stub应在正常BeginEquipmentRun返回false时产生行为失败，不能把缺符号/编译错误当RED。

已核对边界：same-name不同InstanceID、GSW实际主攻命中与heavy_press时轴、CD经Q/掉落/重拾保留、满槽默认只开层/显式备用替换不激活、失败域ID不耗、石骑Shield同double时刻13伤害读旧无甲/死亡优先、两125max甲替换保120HP且负甲截80/加上限不回、Focus甲边界旧15→新12积分、贴墙移动意图取消、合法/失败dodge区别、两动作域真实锁点单次CritDraw。

root裁定新绑定WA Budget唯一Focus，Fighter镜像，旧QA隔离；本组按该裁定验证Focus连续，而不固守主体旧计划中Fighter唯一权威。预设0时真实Spend50，甲边界1.0/1.5，预期1.25=53.75、1.5=57.5、1.75=60.5、2.0=63.5，LastActualSpend始终0。

集成切片SWD/GSW都是0弹匣，此组只证明0字段完整传递和真实CD不重置；非零弹药/射击装填Actor测试必须待XBW真实接线，不能用本组结果声称已完成。

## 首次stub运行前自审：Dodge测试前提勘误

save_state核对D02与既有真实`DungeonDodgeAdapterTests.cpp`第74行，指出新测试同组误设“闪避耗20Focus、空Focus拒绝”。这是测试前提错误，冻结Dodge本来零资源成本，不改变生产以迎合此断言。root裁定当前正在运行的首次stub RED保留原SHA（所有新组应先在BeginEquipmentRun返回false处失败，不能声称已执行到成本断言），之后连同空指针防护修测试再冻结。

正确失败前置：正常dodge结束但仍在start+1.2冷却内，再开装备动作，重按dodge因真实CD拒绝且不能取消该动作。合法dodge取消装备时Focus保持当前值，零Focus亦不构成额外门槛。仍保合法/失败取消区别和Q禁止dodge取消，组数不变；不弱化旧29或Explore26。


## 首次统一构建未通过（非行为RED）

root实际首轮build失败：本Tests第189行`Stats::EPackage`与UE全局Stats符号歧义；root HUD也有其独立PI宏碰撞，由root处理。该次没有运行38组，不计为业务RED。按root明确解冻窗口，仅修owned Tests本地alias为EquipStats、补Source可用/消费及旧Item空指针guard，同时修已证明错误的Dodge成本前提。

修后同9组加入80×40合法矩形角（归一距离2仍合法，排序不是范围判定）及RestoreFocus边界（满额恢复0不占receipt，正恢复10走一次receipt并同步唯一WA Budget，再真实Spend10回50控制值）。旧29/Explore26、Actor和冻结核均未修改。

别名替换的短暂中间稿5d1b1289误碰首个测试类尾缀，编译前文本复核已修正，未声称该中间稿可编译或有运行结果。当前9个宏声明与RunTest类名逐项匹配，待root统一重build/运行真正RED。

当前测试文件：33598字节，SHA256 `97e31995c3337a5000c95365f8e95db8074d563f0afa9c416389233ecd5b5375`；原31591字节/450391与短暂5d1只作历史，不代表当前源码。


## 实际首次UE行为RED（已核实）

root统一构建`build-editor-20261015-060827.log`真实exit0，随后运行`FirstRoom-20261015-061538`。独立读取原index确认38项：原29全部Success，新增9全部Fail，notRun0、inProcess0、succeededWithWarnings0。测试执行版本为97e31995c3337a5000c95365f8e95db8074d563f0afa9c416389233ecd5b5375；编译成功后才取得以下业务失败，不把之前alias编译错误充作RED。

新增组失败发生在正常BeginEquipmentRun缺行为（返回false）/绑定前置，证明接口尚未接入；没有执行到各组后续时轴、HP、Focus或取消断言，因此本轮RED不声称逐条后置断言已被实际反例触发。LegalAndFailedDodgeAdmission当时setup失败只给generic failed，root明确许可仅补三个TestTrue诊断；当前a4af489011fa89c7a3d531898a05fee0415ec30aaa7bf8542ded941e24449a3f（33832字节）保持同9组/业务预期，供GREEN构建。未根据失败删测试、降低断言、改旧29或改生产闪避成本。

root已给予Actor owner GREEN实现许可。所有权不变：本任务不启UE/UBT、不写Actor/HUD/冻结核；后续继续只读审查公开API和实际结果。源97e当时独立副本尚未由本任务确认留存，等待root核实其原snapshot归档；不从a4af逆改生成一个文件冒充当时原件。

| 新UE组 | 实际状态 | 实际错误条目 |
| --- | --- | --- |
| `CritDrawFollowsRealLocks` | Fail | Expected 'Critical draw fixture bound' to be true. |
| `FailedAdmissionPreservesDomains` | Fail | Expected 'Admission fixture bound' to be true. |
| `FinalHPAndContinuousFocus` | Fail | Expected 'HP/Focus fixture bound' to be true. |
| `InstanceCooldownSurvivesTransfers` | Fail | Expected 'CD transfer fixture bound' to be true. |
| `LegalAndFailedDodgeAdmission` | Fail | Test CodexDungeon.Content.EquipmentAdapter.LegalAndFailedDodgeAdmission failed, but no errors were logged. |
| `RealPickupTimelinesAndStats` | Fail | Expected 'Actual GameMode binds a new equipment run' to be true. |
| `SamePointDamageAndDeathBeforeCommit` | Fail | Expected 'Same-point fixture bound' to be true. |
| `SameTemplateAndBackupReplacement` | Fail | Expected 'Same-template fixture is a real bound run' to be true. |
| `WallBlockedMovementCancels` | Fail | Expected 'Movement cancellation fixture bound' to be true. |

### 原始运行证据指纹

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-060827.log` | 3400 | `b813b9c21203bedfd7bc79ee2dca8f2b11a99ae28dd064d5d93f6d3275ebe50f` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-061538.log` | 197461 | `fae6d39db6d4d3ac09a8298d3cbd6a0e65dcb87ac61b0ae727cb28f517afc29f` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-061538/index.json` | 22409 | `39060a413fbe40e84b8f586be6517a124959709031bb7bdd40b737e2900692b6` |

实际index计数（直接读取，无改写原件）：

```json
{
  "succeeded": 29,
  "succeededWithWarnings": 0,
  "failed": 9,
  "notRun": 0,
  "inProcess": 0
}
```

## 首版Actor实现：38项行为Success，严格门因1警告未通过

root执行`build-editor-20261015-063051.log`构建exit0，随后运行`FirstRoom-20261015-063205`。独立完整读取index确认38项均State Success，其中原29全部无警告；新9中8项无警告，`FailedAdmissionPreservesDomains`有1警告、0错误。计数为succeeded37、succeededWithWarnings1、failed0、notRun0、inProcess0。严格脚本正确未放行，不能称本轮为38/0或clean GREEN。

执行时Tests源为34782字节、SHA256 `871b8b5c4b522914aaa004ac28a9d8d278cbb37a852395802bb711461c892b4d`。相对a4af仅在同一FailedAdmission组增加MaxX外、MaxY外、NaN来源注册拒绝且各域游标不变的断言；这三项先由只读代码审查发现Actor缺少房内边界，再由Actor owner修复并补断言，没有独立执行过该三个断言的RED，不反写成TDD证据。

警告原文位于`first-room-tests-20261015-063205.log:1513`：`UWorld::DestroyActor: World has no context!`。来源是该fixture清障时调用`Wall->Destroy()`，测试UWorld没有注册WorldContext；实际LOS拒绝与清障后同源拾取断言本轮均通过，警告仍按严格标准保留为未通过条件。

按root许可，只将该行改为`Wall->SetActorEnableCollision(false)`：保留真实注册墙体、真实LOS拒绝及清障后同源正常E拾取；直接解除实际碰撞阻挡，世界销毁仍由既有fixture生命周期处理。未屏蔽警告、未改gate、未改旧29或Explore26、未改生产Actor与冻结核。修后Tests为34803字节、SHA256 `a13c1a86a7892f81ade4cfb8025cc5d8587cc3eea10c0b3cccf5bf36bb20c172`，已冻结交root二次统一构建；尚未取得该版本运行结果。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-063051.log` | 4890 | `34871e61c8f9b48d71a548f78ea66068c13c2ec66b7421438a1d04880ce94689` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-063205.log` | 197728 | `a4d3d8932fb3a938f6b280d26ef761ac89a6dc0d216c094f763260d01ca38355` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-063205/index.json` | 18874 | `aa450bfeaab21c923d19646442abcf653f5597d3d33a4c7aa9f569bb88bf0b43` |

## 正常控制器输入proof只读审查

root独占的EquipmentAdapter proof及严格9-name门已逐项对照：C++与PowerShell所需9个唯一名称一致，重复、遗漏、失败均不放行。正常profile只在初始化创建新Run和三个明确QA来源，后续走真实控制器键及公开只读view，不把QA来源写成N03/N04商人掉落或D13同代磁盘闭环。审查没有修改这些root文件。

两项可复现proof问题已由root接受并修源码，尚待实际录制确认：其一，Crit游标起始值应读取实际SetupView，单K锁点验证Before＋1，不能硬编码2；其二，原5cm到点容差与全速方向键在合法50ms帧会振荡。LGT移动速度286.2时每帧14.31cm，目标X=-240的序列可停在-249.27与-234.96往返、两端均大于5cm，导致40秒内不能推进E阶段。root修到点区为24cm，仍在真实80×40拾取矩形内，保留正常键、真实delta和0.2秒站定；三个初始QA源间距120cm，不会因此误选前一个源。没有固定时步或直接写位置消除该问题。源码修复与严格自动化行为通过均不能替代尚待执行的正常输入视频/日志。

## 二次统一运行：真实Actor切片严格GREEN

root执行`build-editor-20261015-063702.log`构建exit0，日志确认重新编译DungeonEquipmentAdapterTests.cpp及DungeonContentProbe.cpp并链接DLL。随后`FirstRoom-20261015-063742/index.json`独立完整核对为38项全State Success，succeeded38、succeededWithWarnings0、failed0、notRun0、inProcess0；新9 EquipmentAdapter逐项warnings0/errors0，原29同样保持通过。本次自动化日志中不再有前轮WorldContext警告，未通过屏蔽日志或降低严格门获得结果。

执行Tests源码再次核对为34803字节、SHA256 `a13c1a86a7892f81ade4cfb8025cc5d8587cc3eea10c0b3cccf5bf36bb20c172`，保持冻结。本任务只读取实际日志/索引并更新owned文档，没有运行UE/UBT或修改任何Source。root报告构建exit0，独立读取构建原件确认五项action全部完成、实际耗时28.03秒；不将本次检索“没有Warning匹配”产生的rg无匹配退出码1写成UE构建退出码。

该GREEN覆盖实际SWD001/GSW001/LGT001的GameMode地面来源、正常Fighter动作、武器.35秒/甲.50秒提交、双武器Q、显式备用替换/原Instance落地再拾、真实技能CD保留、Stats单权威、HP一次截断/不回血、Focus连续、墙挡意图取消、真实同点伤害/死亡优先及锁点Crit游标；各组方法使用公开生产API和只读状态，不靠改Capture伪造库存。测试中的SelectSource、合法QA初始受损HP、QA位置与注册来源仍是明确fixture前置，因此不能把自动化方法调用等同于全控制器输入实录。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-063702.log` | 3409 | `9746b00b5f5064093c85f96f85558a8a60646216a61952a77894261aee77a7a8` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-063742.log` | 196831 | `a4661b2106f23deb840e3a5b35bd554005e95771b26ac7a8c587d9f7eca6c555` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-063742/index.json` | 18872 | `261fb0ff70b6d31790d5833058852c9b9f5ea8624a764f8e0734c2dd62bb1743` |

当前边界继续保留：首批内容完成数0/15不变；非零弹药射击/装填Actor、全5武器4甲目录取得、N03/N04或D08完整真实来源链、D13同代磁盘存取/重载、最终装备图层与完整动作/特效/音效均不能由本切片认证。原Explore26文件与断言未修改，本次38组也不冒充Explore26重新运行。root正在准备单独正常输入profile capture9，只有该独立原始结果出来后才可记录其通过；不结束总goal。
