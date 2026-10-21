# 主角Death5实际接入只读说明 v001

结论：当前主角死亡的游戏终局与展示时钟已存在；启用Fairytale Sword装配时，死亡美术却落到**裸Ready0**并阻止旧Death回退。最小方案是独立Death优先分支＋只读实际terminal-age查询＋精确40层源与复用Sword的纯绘制profile。不能把sim-time当死亡年龄，不能把松手落剑当真实掉落。

本次只读检查actual Source246，与v137-range187G的246项Source pins逐项相同。只新增本文；原debug review freeze仍原字节，本文为其冻结后的独立补充，不冒已包含于旧freeze。未启动UE/UBT、生成/导入/修改资源或View；没有新Death运行验收。

## 事实：真实HP0、时钟与持有关系

| 路径 | 实际函数与行号 | 已存在的行为 |
|---|---|---|
| 致死直伤 | [DungeonFighter.cpp:1448](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1448)，1499、1529–1555 | 先减真实HP；致死必走Death中断Combat/WeaponActions/Dodge，清SkillWindows/世界weapon windows，AnimationName=death、AnimationTime=0；随后bDead=true与OnFighterDied。普通致死可以保留HurtTime=.4；不能要求HurtTime归零才画Death。 |
| 致死DoT | [DungeonFighter.cpp:1501](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1501) | 同样bDead/Death中断、death年龄清零、正式OnFighterDied；不用新的PoiseBreak作为死亡门。 |
| 正式玩家终局 | [DungeonGameMode.cpp:2279](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:2279)，2305–2337 | once门bDeathReported；Bound玩家核真实OwnerId，然后bDeathReported=true、bGameOver=true并return。**玩家分支不调用ResolveDeath、不产生ObjectIds或Pickups**；后面的奖励/掉落仅敌人分支。 |
| terminal推进 | [DungeonGameMode.cpp:1857](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1857)，1889–1894；[DungeonFighter.cpp:1812](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1812) | 下一正常GameMode Tick在bGameOver分支只AdvanceTerminalPresentation后return；死者AnimationTime+=合法DeltaSeconds，JumpHeight以360/s降至0；不推进master/kernel、输入、伤害、资源。致死当前batch仍完成原同点中断/已受理队列排空（GM2024–2051），不能在renderer提前清它。 |
| 非GameOver的旧dead分支 | [DungeonFighter.cpp:1821](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:1821)，1837–1841 | SimulateMotion检测bDead后仅降展示高度并SetAnimation(death)。Bound正式路径由GameMode管理；不额外启用Actor Tick叠加推进（如GM820、1891）。 |
| 身体/库存仍归原Owner | [DungeonGameMode.cpp:976](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:976)，1044–1050；[DungeonEquipmentInventory.h:34](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonEquipmentInventory.h:34) | 受击先CancelEquipmentAction（Fighter1457–1462），这里只取消未完成View.Action/selection。提交后的Weapons[2]/Armor/Items保留；UpdateEquipmentMirrors继续从committed slots投影WeaponId/ArmorId。真实Drop必须PrepareDrop/Commit及合法DropSourceId（Inventory181、205–222）；死亡代码没有自动调用它。 |
| 死者不能捡原币 | [DungeonGameMode.cpp:395](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:395)，422–426、445–451 | 新收币明确拒bDead/HP<=0/bGameOver；敌人已有掉落保持原RunRewards所有者。历史已成功Operation重播是前面的幂等回执分支，不是死者可新收币。 |
| 保存/恢复年龄 | [DungeonFighterSnapshot.h:69](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighterSnapshot.h:69)；[DungeonFighter.cpp:449](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:449)、549、199–205 | AnimationTime随Owner snapshot保存/恢复；dead/kernel预算/GameOver/装备镜像需一致。不得restore时重置Death年龄或重新发死亡事件。既有真实terminal fixture在[DungeonFighterSnapshotTests.cpp:390](F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonFighterSnapshotTests.cpp:390)–401已覆盖空中死亡后Tick(.5)时master/combat/bat时钟冻结、展示下降及RoundTrip；该测试不是Death5纹理验收。 |

RunInstall gate在GM1861/Fighter1814之前返回，因此暂停/准备Continue不能由HUD或wall clock偷推进死亡年龄。致死当帧年龄0，后续展示按实际引擎Delta增加；不补当前帧剩余时间，不手改Tick/SimulationTime。R是已有显式新Run边界（GM1883–1885、2079–2105），视觉释放不触发Restart。

## 事实：HUD为何没有实际Death5装配

入口[DungeonHUD.cpp:1046](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:1046)只要DrawFairytaleSwordBody返回true就退出DrawFighter。该函数[DungeonFairytaleSwordPresentation.cpp:97](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp:97)目前只特判非dead Hurt（104–105）；Primary/Idle/Walk资格在145–166均排除dead。于是死亡时Supported=false、DrawGear=false，但183–186仍把Clip/Frame设为sword_ready_idle/0；209–210不允许ArmorPhase。247–264明确拥有整个主角呈现，资源缺失也returntrue；307画Body，311因!DrawGear直接returntrue，所以无LGT层、无独立Sword，且不会进入旧HUD1168的candidate death选择。旧generic/legacy death分支不等于新Death5已接入。

[DungeonFairytaleSwordEquipmentBinding.cpp:127](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordEquipmentBinding.cpp:127)–146能复用真实世界/Owner/committed view/inventory核对；ValidateCommitted77–124只接受实际SWD及NoArmor/LGT。它没有 blanket dead/GameOver拒绝，inactive历史Action也合法（63–73），适合死者只读皮肤绑定。不要用Ready的!dead/grounded/action-can-start资格替代装备所有权。

## 推理：最小runtime-ready接口及接入位置

以下是**建议接口**，并非本次已实现或获Root试样批准：

```cpp
struct FDungeonDeathPresentationSample {
    bool Active=false;
    float Elapsed=0.f;             // 原Fighter.AnimationTime，非sim差/新timer
    bool DeathReported=false;      // 只读正式once事实
};
bool ADungeonFighter::QueryDeathPresentation(
    FDungeonDeathPresentationSample& Out) const; // 成功一次性赋值，失败Out不变
```

查询限实际玩家（非enemy/stone driver）、bDead&&Health==0、AnimationName==death及有限非负AnimationTime；不要求HurtTime=0、JumpHeight=0、JumpVelocity=0、Melee.Grounded或新可攻击资格。DeathReported可供proof观察正式终局，不制造EventId或分配death owner。死亡年龄复用原保存字段，不加wire/schema。

在Sword总入口内，先识别独立opt-in Death分支，再进入非dead Hurt/正常状态选择；通过真实Binding Resolve确认当前SWD/LGT实例。Death分支应独立Plan/DTO，清本帧旧绘制记录后用本帧事实重建，避免Ready/Hurt/Weapon stack遗留。区分“已占用此呈现分支”和“实际成功Drawn”：匹配Death模式后即使资源不齐也保持显式MissingReason/Drawn=false，不借Ready0/旧灰甲兜底。Alive的既有selector/测试不改。

建议Profile只读承载5帧、40个精确源path/SHA/RGBA及Root typed import/row trial证据，独立Sword复用原资源pin；每帧5 ownBody层（BodyRest/NearArmWithoutHand/HelmetForeground/FarHandForeground/NearHand）＋Chest/ShoulderFar/ShoulderNear三甲层，不用整身作为BodyRest。不新增武器texture或Drop source。整套注册/尺寸/resource resident/无pending GPU初始化先原子预检，再提交任何quad；缺资源fail closed并记录gap。

Death keys按已准备author contract的[0,.2,.4,.6,.8]选择五相；.8起保持frame4直到真实restart/install/restore改变状态，不循环、不在1秒删尸体、不延迟GameOver。Age来自float AnimationTime；边界比较应显式以实际采样数和compiled keys判定，proof记录原age与frame，不将观测年龄四舍五入来救覆盖。

同一row固定身体密度采用既有[DungeonFairytaleSwordBodyV001.inl:18](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordBodyV001.inl:18)的72*512/416画布尺度，塌落帧绝不逐帧按alpha高度归一。作者root/armor translation/剑anchor按独立Root批准的精确数据读取；若导入的是已整数平移好的甲片则runtime不能再叠同一delta。左右镜像统一用x'=512-x、相对root偏移取Facing反射，纹理单次U镜像、旋转角随镜像取反；Sword使用同一个源、现有.50相对身体画布比例（SwordPresentation314–327），不能拿512px或预览padding768px当新的世界尺寸。

准备文件中明确的author提案（当前TrialAllowed=false/FinalAccepted=false，不能据本文开门）：

- body25/LGT15＋复用Sword1；body Root=[242,464]为作者显示root，不冒实测鞋底/物理接触。
- frame0 Sword在身体后段与NearHand前，frame1起IndependentSword在stack最底；release标志只影响quad层序与作者anchor/角度。五帧anchor为[183,311]/[238,408]/[345,442]/[345,442]/[345,442]，角度-20/-8/0/0/0度，.50比例。
- 原手握点/隐藏轴/footlock未测，sourcefit_accepted=false。此处只描述准备接口，Root的新approved profile可替代这些提案；不把source generation或离线整合成功推成真实触柄/no-pop验收。

建议只读DTO包含：OptIn/Active/Supported/AtomicPreflightReady/Drawn/MissingReason、DrawId、SimulationTime、TerminalAge、Frame/LastFrameHeld、真实Owner/Run/restart/装备instance/version、各9slot的精确source/path/quad/pivot/angle/empty属性、实际提交stack；逐Draw绑定terminal age，不要求GameOver后sim严格递增。render-only SwordReleased不得产生Inventory::Drop、Pickups、Scene/RunRewards对象、collision/伤害窗口/音频事件，不能分配OperationId/SourceId或修改WeaponId/ArmorId/Coins。

## 风险与最小验收边界

1. 先做真实GameMode致死integration：direct与DoT都真正HP0/GameOver/一次bDeathReported；后续正常Tick时master/三个玩家kernel/库存Items与slots/奖励对象不变，只有原terminal AnimationTime和展示JumpHeight推进。HurtTime残留、空中死亡与暂停Continue均应保持合法；kernel事件队列不因renderer消费而被删。
2. 用实际Death age验证五相及frame4无限hold、重复查询不改Out以外任何owner；保存/恢复frame2与末相年龄不重播。至少一个真实normal伤害路径捕获，不用写HP/时钟/SetState或public damage冒正常全战。
3. 实际import40后整套resident原子门、source/runtime9slot/层序/两方向root与Sword.50核验；缺一texture/错误Binding/不支持armor明确失败，不能静态Ready遮缺口。旧Alive/Hurt/Walk/三刀行为与旧selector测试保持。
4. 静态代码能证明当前无玩家死亡自动掉落；不能据此宣称新Death5脚锁、甲片透视、松手轨迹/触柄或音色已验收。sourcefit自身保留的late owner、隐藏far肩、剑anchor/遮挡风险仍需Root保全后的实景审看。

## 本次精确来源pins

- v137 compiled manifest：2186 registered files / Source246 / Production1286 / strict187（既有Root快照事实，本次没有重跑UE）。SHA `247c77dca6a5e968946dec9a8c9bcf77bf86d4deb6b2759c125b85ac08ec257a`。
- 准备author contract：[Death220-LGT237-239-five-integer-mounts-and-visual-release-author-contract-v001.json](F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/LGT237-239-Death5-limited-integer-sourcefit-v001/Death220-LGT237-239-five-integer-mounts-and-visual-release-author-contract-v001.json)，65148B SHA `02913295aed0b29b3ca6410939b6053113b7c0dafb848d21c7258eb775aa720f`，TrialAllowed/FinalAccepted/sourcefit_accepted均false。
- `DungeonFighter.cpp`：122242B SHA `818c2c06f4b11d04511f65776a678eaad5f1a2d244ff05b6e6d5bfa1fa1c5a38`。
- `DungeonFighter.h`：12443B SHA `cf84e3781b269e090d9b17544fe85e91726e465f35b7324b561ab98a23f9dbac`。
- `DungeonGameMode.cpp`：151572B SHA `55066ff73a6dd594db4c0631f76656d8166f43a3b4d3512b53df01021038cc6c`。
- `DungeonFairytaleSwordPresentation.cpp`：22622B SHA `092954a95ff43429f5df4306890e725f32532feb96301a59c3b12f18e5b38ad4`。
- `DungeonFairytaleSwordEquipmentBinding.cpp`：9554B SHA `6c167a9da61040ce58333c6824e5c3992de856ba9ceb6f6ed900898c855dfc3a`。
- `DungeonHUD.cpp`：119659B SHA `88ddf5c24bca2259921aa2b9fe6e36aabc665438784e153178d73c751c233f3b`。
- `DungeonFighterSnapshot.h`：4432B SHA `3f3daf9300a85aa00567be7370962f25a849f9c00e81081efe4288112083317d`。
- `DungeonEquipmentInventory.h`：21413B SHA `235284ad0fc7ff955a8814def82b9468f42df514564c97d96e48f3366e55b147`。
- `Tests/DungeonFighterSnapshotTests.cpp`：47423B SHA `21789d30e819493c920961bd92a2b13ef20523fd3b0849111677820d1b883554`。
