# 设备库存纯核制作与验证记录

2026-10-15，Asia/Shanghai。范围为D04首个设备闭环；仅内存纯核，尚未接入 Actor、真实获取或D13磁盘发布。实施计划见 [equipment-inventory-plan.md](equipment-inventory-plan.md)。当前状态：v2合法运行态桥77检查/0失败，原70项均保留；WeaponActions完整实例导入179/0，联合独立纯API夹具10/0。整数弹仓P2已在源码修复并于05:29再次冻结、通知根任务。此前45项与独立恢复7项记录保留为历史。纯核结果不能记为内容单元、Actor获取或D13磁盘已完成。

## 规则事实与方案

两武器槽与一身体甲槽，只有当前武器和身体甲产生属性。空槽默认拾取后激活；满槽必须显式选择，替换备用保持当前，旧物作为原实例完整落地。最后武器禁止手动丢弃，显式免费替换仍可完成。Q只切当前槽，不创建实例、不填弹、不刷新各实例绝对技能CD。

`FItem` 拥有内容ID、附魔ID的 `std::string`、grade、方案/tier、幅度/原q及弹药/技能deadline传递数据。实例表唯一保存当前实例；来源含冻结生成快照与 consumed tombstone，防同一 SourceID 回调生成第二份。实例只属于一个装备槽或一个可用地面来源。稳定 InstanceID、SourceID、OperationID 由caller在相应Run域持久分配，核不使用地址、GetUniqueID或随机。

Prepare返回绑定当前库存/源/实例版本的只读意图，不保留资源预约或改变所有权。Cancel不写状态。Commit先查询已有成功OperationID，同请求返回原结果、不同请求拒绝；新操作再重验版本、选槽、外层真实准入和旧物合法落点。候选副本通过校验后一次安装，失败不消费成功receipt或来源。库存全局Revision是保守乐观锁；任意新源注册也使旧意图过期，不会自动换目标重试。

Stats的 `FInstance` 只在同步调用内部临时构造，string_view引用当前owning实例并立即Validate/Resolve；返回值不保留借用。最终属性仍完全使用冻结Stats的合并、caps和HP候选结果。本核没有HP、Focus或动作时钟权威。

弹匣上限只读复制原v1的12把有弹匣武器元数据；其余合法武器/防具为0。全部45模板资格借用Stats，不缩掉原池。它没有实现射击或装填。v2新增接收已决运行态事实的合法更新接口，战斗实际资源权威仍属于动作核；接线必须先同批同步当前实例数据再转移，不能以这里的旧传递快照覆盖真实射击结果。

## API与外层责任

命名空间 `DungeonEquipmentInventory`；构造 `FEquipmentInventory(RunId,OwnerId,Starter)`，Starter为显式合法武器实例。槽0/1为武器，槽2为甲。

- `RegisterWorldSource(SourceId,Item)`：新源一次注册；同源同冻结结果幂等，同源不同结果冲突，跨源复制同InstanceID拒绝。
- `PreparePickup(SourceId,Slot=-1)` / `PrepareSwitch()` / `PrepareDrop(Slot)`：返回 `FPrepared{Error,Plan}`；显式选槽可免费替换最后武器，默认空槽规则不强迫替换。
- `Cancel(Plan)`：无提交效果。
- `Commit(OperationId,Plan,FCommitContext,DropSourceId=0)`：AdmissionGranted、DropPointGranted默认false；只有真实外层验证后才赋true。
- `ResolveStats(Stats::FContext,ActualHP)`：同步只读计算，不写HP。
- `State()`：只读owning状态；`Capture()/Restore(State)`：内存一致性检查及去重信息往返。

动作0.35/0.50s、受伤/移动/合法闪避取消、同点死亡优先、实际80×40拾取矩形、LOS、安全及落点几何均由外层实现，本核bool不证明这些条件。无钱包/购买价格/商品库存、快捷物、遗物或掉落RNG；不改DEV的SWD起始、0grade/no affix/no armor/20金币，N03装备权重与N04 GSW32/甲28报价仍由既有内容合同指定，本核没有授予全装免费开局。

这里只保留成功操作记录，按本子任务要求失败不消费receipt、可纠正未提交意图后重试。D13完整合同还要求REJECTED/CANCELLED规范请求记录、SHA256规范编码、同代磁盘发布、故障暂停及跨模块同批资源；这些未实现，不能把本内存提交称为D13持久成功。它也不证明全字段协调伪造的快照真实，D13内容完整性是外层职责。

## 当前测试证据

先写可编译空桩及关键行为测试，编译成功后43项中36项真实失败；实现基础闭环后43项全过。两轮编译参数 `/EHsc /utf-8 /std:c++17 /W4 /WX`，无宏翻译单元为空。没有将编译错误当行为RED，没有运行UE/UBT。

| 阶段 | 结果 | 原日志 |
| --- | --- | --- |
| 初始RED | 编译0，43检查/36失败，退出1 | `%TEMP%/OurgameEquipmentInventory/20261015-031733-810-RED/standalone.log` |
| 基础GREEN | 编译0，43检查/0失败，退出0 | `%TEMP%/OurgameEquipmentInventory/20261015-031951-877-GREEN/standalone.log` |

自审Temp最小编译发现：锋利V幅度25但OriginalQ=1/10仍被接受；正确映射应为21，因此应拒绝。另将成功武器拾取操作日志的Slot改成甲槽2，当前Restore仍接受；这是历史请求与目标种类的结构矛盾。原43项没有覆盖，不能把基础GREEN写成已经验证这两个边界。后续真实RED/GREEN将追加在本报告。

上述段落记录基础版发现时的实际缺陷；当前复修已关闭，详情和原始45项日志见末节。

## 只读来源指纹

| 文件 | SHA256 |
| --- | --- |
| `docs/design/inventory-v1/inventory-rules.json` | `7eb6f7da968622a1583b4e63069208513a09e0ef74d12e244c18e20332f08942` |
| `docs/design/save-data-v1/transactions-and-rng.json` | `78272f64a2e727c4ed00aa36d3c21908afa42baa317da2e9c503674cf1cb5b72` |
| `docs/design/save-data-v1/state-schema.json` | `4dc7fb0235b68790cbbda08a25d8d6f1e05e0a18df0bbfb6648430faa31ec4cd` |
| `docs/production/first-batch-v1/content-contract.json` | `860b7f50256085d020cd3a60c2f04e80c0124303cfbe1c5fbfe19da830f0ca56` |
| `docs/design/equipment-v1/weapons.json` | `95757819382832cfa31e6596f3ba90f1e983e83fbd69504da3c99d5ea2a272b4` |

本任务只编辑自己新建的头、Standalone测试/脚本与plan/report文档。未改他人Actor、GM、Driver、HUD、Probe、旧纯核或设计来源。

## 前阶段43项冻结交接（历史）

根任务统一构建需要保持Source稳定，要求先交接释放并行slot，待Actor修复与snapshot后再续补两条真实RED。本核源码自03:19:51基础GREEN后保持冻结。两项自审缺陷未修复，纯库存任务仍有后续工作，不作为完整验收。

| 当前文件/日志 | SHA256 |
| --- | --- |
| `DungeonEquipmentInventory.h` | `de1b144ea861e7cf751fb1409a7b1bcda10c00f788fbb9923bfbc9c0da6ea1f5` |
| `Tests/DungeonEquipmentInventoryStandalone.cpp` | `04584b0ae70d5b6b4864d258251cfde685e6d00385372134a8ec07e2e234c912` |
| `Tests/RunEquipmentInventory.ps1` | `37452a26bb3066e768248fcfdb7492a2ade2656df07bb51d34a46f6f9def5d66` |
| 初始RED原日志 | `30b3f9df1854079941e6cda503d3098a1c3115ae2c1a24d0eacca2d5c4f035be` |
| 基础GREEN原日志 | `33bcd7896122caecd2cd2d714b69b0901d300dd4ee3555d3d34ce7cd3ed820b4` |

以下完整文本保留真实历史结果，后续增加回归不会改写旧计数：

### 初始行为RED

```text
PHASE=RED; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.
DungeonEquipmentInventoryStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentInventoryStandalone.cpp
COMPILE_EXIT=0
FAIL world source registers once
FAIL identical world callback is idempotent
FAIL same source with different result rejected
FAIL same instance cannot appear at another source
FAIL prepare cancel leaves ownership and world source unchanged
FAIL default context cannot commit pickup
FAIL empty weapon pickup activates and consumes source atomically
FAIL pickup preserves independent ammo and cooldown data
FAIL committed replay returns old result without granting again
FAIL new operation cannot pick consumed source
FAIL spawn callback after pickup does not respawn source
FAIL Q switches existing slots without creating instances
FAIL Q roundtrip leaves instance versions and resources unchanged
FAIL OperationID reused for different request rejected before stale validation
FAIL full weapons require explicit destination
FAIL invalid old drop point rejects entire replacement
FAIL replacement of backup drops exact old instance and keeps active
FAIL dropping active switches to other existing weapon
FAIL manual last weapon drop prohibited
FAIL explicit free replacement of last weapon is allowed
FAIL dropped item can be repicked with same stable instance
FAIL registry owns content and affix strings after caller mutation
FAIL armor pickup uses frozen Stats without healing or own HP state
FAIL existing armor needs explicit replacement choice
FAIL armor replacement drops old armor atomically
FAIL manual armor removal preserves old instance on ground
FAIL invalid grade consumes no world source identity
FAIL ammo over original magazine rejected
FAIL nonfinite cooldown rejected
FAIL illegal armor affix on weapon rejected through Stats
FAIL missing original q rejected
FAIL failed source registration can retry same stable IDs
FAIL stale transaction does not consume operation or source
FAIL failed operation ID can retry a freshly validated uncommitted intent
FAIL owning snapshot restores inventory world tombstones and operation results
FAIL restored operation journal still deduplicates successful request
CHECKS=43 FAILURES=36
EXIT_CODE=1
```

### 基础GREEN（未覆盖两项自审缺口）

```text
PHASE=GREEN; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.
DungeonEquipmentInventoryStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentInventoryStandalone.cpp
COMPILE_EXIT=0
CHECKS=43 FAILURES=0
EXIT_CODE=0
```

## 两项自审复修与最终冻结

解冻后先只增加两条关键断言，不改原43项：

1. 锋利V幅度25、原q1/10的数据虽各自非零合法，但按同一q映射当前区间21–25应得到21，故整件拒绝，SourceID和Revision不占用。
2. owning快照中，把成功武器拾取请求Slot改成2（身体甲）必须原子拒绝，保留恢复前库存。

真实RED编译成功，45检查/3失败：两个新断言各失败1；错误接纳q实例还污染来源，导致原“失败来源注册同ID重试”连带失败1。没有将这个原断言删除或改预期。随后最小修复：

- `ValidItem` 逐词条调用冻结 Stats 的 `LegalAffixRange` 与 `MapOriginalQuantile`，要求映射结果等于所存幅度；没有复制映射公式、重新计算原q或修改Stats。
- `ValidState` 对每个历史操作的实例种类与槽种类校验：甲只能槽2，武器只能槽0/1；原有Switch禁止甲槽约束保留。

最终GREEN编译0，45检查/0失败，退出0；owning字符串、实例CD数据和Stats单一属性权威保持。此校验保证所存q与当前幅度一致，不证明其原随机抽样过程或生成seed可信；生成receipt与D13内容完整性仍在外层。

### 两项回归RED原日志

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-034328-031-RED/standalone.log`；SHA256 `b45e46fe0a75caa2750e6fcbf666b2bee0c3114de8a3b782d299528239371e66`。

```text
PHASE=RED; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.
DungeonEquipmentInventoryStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentInventoryStandalone.cpp
COMPILE_EXIT=0
FAIL legal magnitude inconsistent with preserved original q rejected without consuming source
FAIL failed source registration can retry same stable IDs
FAIL historical weapon pickup cannot claim armor destination on restore
CHECKS=45 FAILURES=3
EXIT_CODE=1
```

### 最终GREEN原日志

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-034349-193-GREEN/standalone.log`；SHA256 `45ffe93be76bb7a58fc015919897a7ed36f468acde4853b9dd863a45e8b0c494`。

```text
PHASE=GREEN; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.
DungeonEquipmentInventoryStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentInventoryStandalone.cpp
COMPILE_EXIT=0
CHECKS=45 FAILURES=0
EXIT_CODE=0
```

### 独立恢复负例复核

临时独立C++夹具重新编译当前头，`/EHsc /utf-8 /std:c++17 /W4 /WX`；7检查/0失败、退出0，未运行UE/UBT。源与结果：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventoryReview/20261015-034440-345/`。

覆盖：合法武器和甲设置、合法快照恢复、武器历史目标改甲槽拒绝、甲历史目标改武器槽拒绝、同时改registry与source原q以保持副本一致仍拒绝、拒绝后库存/成功receipt不变。正例还使用LGT001破损III原q7/8，在截短IV区间13–14映射14并保留7/8，确认没有误用当前区间桶中心重造原q。

```text
CHECKS=7 FAILURES=0
RUN_EXIT=0
```

最终冻结指纹（以上43项指纹保留为历史）：

| 文件 | SHA256 |
| --- | --- |
| `DungeonEquipmentInventory.h` | `c41316635d2e41044cca175d61a48e7fec91e6dd33f4be05c0fda88fca34f3c8` |
| `Tests/DungeonEquipmentInventoryStandalone.cpp` | `c329f9f3f4875a33ef45504e0bdeb1913b986069128c1c234b1c7ea048984489` |
| `Tests/RunEquipmentInventory.ps1` | `37452a26bb3066e768248fcfdb7492a2ade2656df07bb51d34a46f6f9def5d66` |

最终源码写入结束于03:43:49，随后只读复核及写本报告；已通知根任务可做统一构建。本阶段没有接Actor、启UE/UBT或增加制作完成计数，首批实际完成仍由根任务按运行验收判定。


## 运行态桥 v2 当前冻结

事实：原地面来源`SpawnItem`是生成/落地当刻的不可变去重请求；装备拥有期间真实射击、装填和技能锁点会改变当前弹药/CD。此前没有合法同步API，不能通过修改Capture快照来接入。新增接口接受动作核已决结果，以独立运行态收据更新拥有武器，而不是把来源出生数据改成当前值。

`CommitResolvedWeaponRuntime(double Now,FId InstanceId,FId ExpectedVersion,double Ammo,double SkillCooldownDeadline,FId ReceiptId)`：

- 只接收当前武器槽0/1拥有的实例；地面、身体甲、未知ID拒绝。检查ammo真实模板上限、CD有限非负且不小于旧绝对值、正确实例Version及有限非回退观测时间。已到期deadline仍合法保存。
- 成功在候选内一次递增实例Version/库存Revision，存完整before/after与结果，NextRuntimeReceiptId推进到已用ID+1；允许显式跳号。失败不改变状态或消费ID；旧同请求收据幂等，改参数拒绝。历史幂等结果是当时结果，不冒充当前Revision。
- schema2显式保存InitialStarter、每个来源CreatedRevision及RuntimeUpdates。Restore核对构造绑定的Run/Owner/Starter，并沿Revision重放来源出生、每次槽操作和每条运行态转移，拒绝缺日志、伪before、当前原始ammo/CD改写、收据游标回退和历史ActiveSlot矛盾。旧schema1直接拒绝，未暗自迁移。
- 内容/词条保持owning string，最终数值只调用Stats；没有新增HP、Focus、动作积分或第二套属性算法。库存Now只记录调用者观测，不证明它等于真实动作核时钟；外层必须在共同批次核实。

来源回调去重与运行变化分离：已消费来源仍匹配其原始SpawnItem，合法运行变化不让它重生或冲突；当前可用来源必须完全匹配最新实例。Drop用最新完整实例创建新的不可变落地来源，重拾沿用原InstanceID与弹药/CD。

先24条新增边界加原45项，真实69/21 RED→69/0 GREEN。追加历史运行态结果ActiveSlot伪改负例，真实70/1 RED→70/0 GREEN：修复为ReplayRuntime核对当刻W.ActiveSlot。没有删旧45断言或用编译失败充当RED。所有轮次MSVC14.38.33130、SDK10.0.19041.0，`/EHsc /utf-8 /std:c++17 /W4 /WX`，无宏TU为空；未启UE/UBT。

### 运行态初始RED

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-050628-313-RED/standalone.log`；1594字节；SHA256 `5fa76b00ba7715948b91469bcbd62ebab65ed93e8eab5ed21054e4e1e424f476`。以下为完整日志文本。

```text
PHASE=RED; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

FAIL resolved owned weapon runtime commits once with persistent receipt

FAIL identical runtime receipt replays without consuming again

FAIL same runtime receipt with changed payload conflicts

FAIL runtime version change invalidates prior equipment plan

FAIL drop snapshots latest runtime rather than original spawn resources

FAIL ground weapon cannot receive an owned runtime update

FAIL repicked same instance accepts resolved reload with preserved cooldown

FAIL runtime receipts ownership chain and resources survive capture restore

FAIL old runtime receipt remains idempotent after restoration and repick

FAIL forged runtime before balance rejected

FAIL missing runtime history cannot preserve edited resources

FAIL runtime receipt cursor rewind rejected

FAIL legacy schema without runtime facts explicitly rejected

FAIL unpicked source cannot be mutated as owned runtime

FAIL nonfinite runtime timestamp rejects atomically

FAIL stale instance version cannot overwrite newer runtime

FAIL overfull ammo and cooldown rollback consume no receipt

FAIL failed receipt retries successfully with legitimate data

FAIL runtime observation timestamp cannot move backwards

FAIL older unused runtime receipt rejected after cursor advancement

FAIL new observed cooldown may already be expired without being reset

CHECKS=69 FAILURES=21

EXIT_CODE=1
```

### 运行态初次GREEN

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-050808-146-GREEN/standalone.log`；271字节；SHA256 `1a7d183ecc6188a1720a32de6b88ef0c1b671bed5c9f43a781bcd3fc3c5ccd1d`。以下为完整日志文本。

```text
PHASE=GREEN; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

CHECKS=69 FAILURES=0

EXIT_CODE=0
```

### 历史ActiveSlot负例RED

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-050838-275-RED/standalone.log`；342字节；SHA256 `4dc6ad64d85df8d455ee3cdb0a293209a12447dbd4b4bff588f35a2b74d52ca1`。以下为完整日志文本。

```text
PHASE=RED; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

FAIL runtime receipt result must preserve actual historical active slot

CHECKS=70 FAILURES=1

EXIT_CODE=1
```

### 最终70项GREEN

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-050848-445-GREEN/standalone.log`；271字节；SHA256 `9207134eed0e0fa8245705d3d4d6cc0a01bf9ed95dc76c6f8489d8000bddfc09`。以下为完整日志文本。

```text
PHASE=GREEN; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

CHECKS=70 FAILURES=0

EXIT_CODE=0
```

### v2初次冻结源码指纹（05:18，半发P2修复前历史）

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| `UnrealGame/Source/CodexDungeon/DungeonEquipmentInventory.h` | 21277 | `4458a90506359c4ebe01df9153add19bf10d63619e8d9fbd261f010f899b8a2e` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentInventoryStandalone.cpp` | 15368 | `25e04e6f610a42db4ea97f289367f899933b58de42a743b2313ee45da0cf8fa0` |
| `UnrealGame/Source/CodexDungeon/Tests/RunEquipmentInventory.ps1` | 2695 | `37452a26bb3066e768248fcfdb7492a2ade2656df07bb51d34a46f6f9def5d66` |


与WeaponActions的独立联合纯API检查10/0见 [weapon-instance-import-report.md](weapon-instance-import-report.md)：实际技能CD合法同步、完整地面武器导入、普通候选复制/提交、Q后原CD保持、Drop/重拾保持实例与资源、两个独立来源/导入receipt幂等、两核Capture/Restore保留Focus和旧事实。该夹具不调用Actor，不代替真实E/Q动作、失败后跨模块回滚或D13磁盘验收。


## 独立审查P2：弹仓必须整数（已修复）

事实：D13 `docs/design/save-data-v1/state-schema.json` 第798–800行明确 `magazine_remaining: nonnegative_integer`。独立审查夹具发现XBW001拾取后`CommitResolvedWeaponRuntime(5,2,2,.5,4,7)`被接受、Revision3→4、NextRuntimeReceiptId1→8，随后同收据纠正为0失败；半发地面来源及快照也被接受。原独立6检查/4失败日志保留如下。原70项测试仅覆盖有限/范围与资源账本，未覆盖整数资格，不据此前GREEN声称该边界已验证。

根任务先将v012旧源码/DLL及运行证据完整冻结；得到可写信号后才修改本两核。v012旧DLL仍有此已知P2，后修工作区不能当成旧DLL源码证据。

修复在本核统一`MagazineCount(Value,Capacity)`为有限、非负、<=真实弹匣、`floor(Value)==Value`：应用于ValidItem（当前Item、来源出生与初始Starter）、运行态提交以及RuntimeUpdates每条BeforeAmmo/Ammo。没有四舍五入、扣半发或改掉落数值，不增加receipt消耗；失败保留原Revision/版本及收据游标，同未成功ID可纠错重试。schema仍2，本次未更改快照结构；旧非法半发状态拒绝。

保留原70项，新增7条关键检查，真实77/6 RED→77/0 GREEN。其中独立负例协调当前Item/来源出生/运行日志为半发；另构造最终弹药与来源出生均整数、仅相邻运行转移的After/Before为半发，确保历史字段也拒绝。正例涵盖同SourceID和receipt纠正后重试、合法完整装填；CD仍允许小数绝对时间。最终Source写入05:29:12，后续只写文档与Temp独立夹具。

### 外部独立原始P2复现（历史6/4）

原件：`C:/Users/22499/AppData/Local/Temp/OurgameInventoryIndependentReview/20261015-052412-059/review.log`；474字节；SHA256 `12d7b8674b8cd2e552799f48b665b2e884bbe06a2384e3280cf1079ee56998c4`。以下为完整日志文本。

```text
inventory-review.cpp

COMPILE_EXIT=0

fractional_runtime_ok=1 revision_before=3 revision_after=4 next_receipt=8

FAIL fractional resolved magazine rejects atomically without ID

corrected_same_receipt_ok=0 error=17

FAIL same receipt retries correct integer observation

fractional_world_source_ok=1

FAIL fractional ground magazine rejects source registration

fractional_snapshot_restore_ok=1

FAIL snapshot carrying half a bolt rejected

CHECKS=6 FAILURES=4

RUN_EXIT=1
```

### 整数弹仓回归RED

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-052822-647-RED/standalone.log`；735字节；SHA256 `19bb5c3463ddedc8f30cea94748f3ca6276b5db87a47dbe04c70181f5b0179a4`。以下为完整日志文本。

```text
PHASE=RED; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

FAIL fractional ground magazine rejects without consuming source identity

FAIL fractional source rejection permits same IDs with integer ammo

FAIL fractional runtime rejects atomically without consuming receipt or revision

FAIL fractional runtime rejection permits corrected same receipt

FAIL coordinated fractional current source and runtime snapshot rejected

FAIL fractional intermediate runtime ledger rejected even when source and current ammo are integer

CHECKS=77 FAILURES=6

EXIT_CODE=1
```

### 整数弹仓最终GREEN

原件：`C:/Users/22499/AppData/Local/Temp/OurgameEquipmentInventory/20261015-052912-297-GREEN/standalone.log`；271字节；SHA256 `13843ddc34347e61dbde8a15179dded81ba5e1a1d6b781d53d44e2cfb9b10666`。以下为完整日志文本。

```text
PHASE=GREEN; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance.

DungeonEquipmentInventoryStandalone.cpp

NO_MACRO_TRANSLATION_UNIT_EMPTY=true

DungeonEquipmentInventoryStandalone.cpp

COMPILE_EXIT=0

CHECKS=77 FAILURES=0

EXIT_CODE=0
```

### 05:29当前冻结指纹

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| `UnrealGame/Source/CodexDungeon/DungeonEquipmentInventory.h` | 21413 | `235284ad0fc7ff955a8814def82b9468f42df514564c97d96e48f3366e55b147` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentInventoryStandalone.cpp` | 16970 | `b2272e7a9bfdeb11abc4b72c9e7b3179280346bcb482326ddcbc47817e16ac30` |
| `UnrealGame/Source/CodexDungeon/Tests/RunEquipmentInventory.ps1` | 2695 | `37452a26bb3066e768248fcfdb7492a2ade2656df07bb51d34a46f6f9def5d66` |


## 05:33 独立修复复核

原审查者asset_sources在新唯一Temp目录复制冻结两头及依赖，独立C++17 `/W4 /WX` 编译0、19检查/0失败、运行0，确认Source哈希与05:29冻结一致。覆盖来源.5拒绝/同ID整数纠错、runtime.5不耗Revision/receipt/同ID纠错、纠错后合法整数快照正例、当前整数但协调历史中间After/Before为.5拒绝、历史来源与首Before为.5拒绝、当前/末After为.5拒绝、WA完整/legacy半发拒绝且同ID纠错、构造/导入出生协调半发快照拒绝；STF真实动作Focus10.05预约和89.95余额仍可恢复。

旧6项原始夹具未改，新夹具明确纠错后的整数快照应接受，未以拒绝合法纠错状态误判通过。源码半发P2关闭；不认证v012旧DLL，也不代表Actor获取或D13磁盘完成。

夹具：`C:/Users/22499/AppData/Local/Temp/OurgameInventoryIndependentReview/20261015-053316-328-fix/inventory-fix-review.cpp`；SHA256 `11126d7080fc951e5997c805fde2e570f58981a0742bec715cc5ab0144235ccd`。日志：`C:/Users/22499/AppData/Local/Temp/OurgameInventoryIndependentReview/20261015-053316-328-fix/review.log`；1267字节；SHA256 `a69d7d0151076407a0e318120928c47e63ce4154c92bf14d685c9a1e461a1f24`。

```text
inventory-fix-review.cpp
COMPILE_EXIT=0
PASS fractional ground source rejects atomically
PASS same rejected source and instance IDs accept corrected integer
PASS SETUP real pickup owns integer bow version2
PASS fractional runtime rejects without revision or receipt use
PASS corrected runtime retries same receipt successfully
PASS SETUP integer reload creates second real runtime receipt
PASS corrected integer snapshot is valid positive control
PASS integer current with coordinated fractional intermediate after-before rejected atomically
PASS coordinated fractional current and last receipt rejected
PASS fractional historical source and first before rejected despite integer current
PASS WA full import half round rejects without identity or receipt use
PASS WA corrected full import retries same receipt
PASS WA legacy half round rejects
PASS WA corrected legacy registration reuses instance ID
PASS WA fractional constructor birth and current snapshot rejects
PASS WA coordinated fractional imported birth and current rejects
PASS SETUP real staff primary starts
PASS fractional Focus reservation 10.05 remains legitimate and restorable
PASS fractional Focus spend 89.95 remains legitimate and restorable
CHECKS=19 FAILURES=0
RUN_EXIT=0
```


补充历史对照：root要求原未修改6项夹具以新冻结头重新编译，实际编译0、6检查/1失败，目录`C:/Users/22499/AppData/Local/Temp/OurgameInventoryIndependentReview/20261015-053418-007-original6-newheader`，log SHA256 `071a273d964ae6d2b1821ed0194c8155092fa257f4d37cd6c65a18965570e287`。唯一失败为原末项要求Restore拒绝K；新修复后K已用同receipt纠正为合法0发，该Restore应成功。未修改旧fixture、未写成6/0，亦不把此失效测试前提写成生产残余缺陷。有效修复验收为上述独立19/19，同时保留原6/4真实RED。
