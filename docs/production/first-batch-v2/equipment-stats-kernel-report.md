# 装备属性纯核验证记录

日期：2026-10-15，Asia/Shanghai。范围仅 C++17 属性核与独立测试；不启动 UE、不执行引擎构建、不生成图像。

## 事实、判断与边界

来源是装备 v2 的 22 属性、36 词条、45 原模板及 I–V 合法区间；D03 规定同类合并封顶与快照时机；D08 定义 grade0–3；D09 定义九天赋快照。原模板资格不能因强化、其他来源或当前负词改变。首批九件需要完整计算，同时保留全45模板，不改旧池资格。

计算顺序：当前武器/甲附魔 + 已验证其他来源 + 当前实例强化 + 当前 Run 天赋，同 stat 求和一次；加入基础值后按对应属性范围封顶一次；计算派生倍率/防护/移动上限；最后仅 `currentHP=min(previousHP,newFinalMaxHP)`。备用武器不贡献。

风险边界：本核不做随机抽样、费用/购买提交、附魔设施、天赋购买、状态触发计时、AttackID/伤害快照、治疗/元素预算账本、存档或 Actor/HUD 接线。源模板单次攻击字段不是三段连招的新定义，运行适配应使用既有动作核的真实分段再乘本核结果，不能替换动作时轴。

## 执行计划

1. 冻结只读来源哈希、45 模板/36 词条/22 上限/九天赋数据，独立测试夹具直接读取来源已列出的逐模板合法区间。
2. 先写可编译接口桩与真实断言，运行 RED 并保留编译成功、断言失败的原日志。
3. 实现原模板资格、完整 package 校验、一次合并/封顶、grade/天赋与最终 HP；运行 GREEN。
4. 核对全部 45×36×5 资格格、首批 5×4 装备组合、上下限/非法输入/不治疗边界，记录可复现命令和真实验证范围。

状态：纯属性核独立验证通过；未做 UE 接线或运行验收。

## 实际结果与覆盖

- 先发生一次编码编译失败（未计为行为 RED），在本测试脚本加 `/utf-8` 后，首次行为 RED 编译成功：186 条断言，176 失败，退出1。
- 首轮 GREEN：8,412 条断言、0失败。补充治疗时实际 HP 的回归先编译失败（接口尚未扩展），补可编译桩后真实 RED：8,417 条、1失败；实现后 GREEN：8,417 条、0失败。
- 最终 VERIFY（2026-10-15 00:46:20 本地）：**16,405 条断言、0失败、编译退出0、测试退出0**。覆盖新增闭区间上下端点和越界，编译参数 `/EHsc /utf-8 /std:c++17 /W4 /WX`。
- 45×36×5 = **8,100 资格格**全部与来源已列出的区间匹配；807 个逐模板词条记录、3,994 个非空等级区间，各测最小/最大合法值和上下越界。45×5 =225 模板等级格分别存在 beneficial / mixed / cursed 完整组合；元素共组、相反词条互斥、包数量与极性单独检查。
- 首批 SWD001 / GSW001 / SPR001 / XBW001 / STF001 × LGT001 / MED001 / HVY001 / ROB001 的20种基础搭配通过；其余36模板仅只读属性/资格支持，不宣称有完整战斗内容或正式素材。
- 同类一次合并封顶、grade按原值化flat、全部22上下限、九天赋完整/部分/非法快照、备用武器休眠、条件基值替换、装填/专注家族限制、HP不治疗/不复活/不截到1、实际治疗时HP、量化升级原q及非法输入通过。
- 运行脚本先真实 `cl /EP /P /U...` 预处理，**未定义 opt-in 宏时输出空文件**，随后才带宏编译测试。这仅是独立编译安全验证；没有执行UE/UBT。
- Python AST有效；冻结工具 `--check` 通过；profile 的 source_catalogue_sha256 与原始 v1 JSON匹配，45个 base_definition 与 v1 原记录逐对象完全相等。没有写设计来源文件。

## 交接接口

头文件：`UnrealGame/Source/CodexDungeon/DungeonEquipmentStats.h`，命名空间 `DungeonEquipmentStats`，只依赖C++17标准库。

```cpp
FLoadout L;
L.Weapon = FInstance{"WPN-SWD-001", 3, {}};
L.Armor  = FInstance{"ARM-LGT-001", 0, {}};
L.Context.TalentRanks = {3,3,3,4,3,2,3,3,3}; // VIT GRD MED ATK BRK CRT MOV FOC RLD
L.PreviousHP = 88; // 提交前实际HP，不能填旧上限或预先截过的HP
FResolved R = Resolve(L);
if (R.Ok()) { /* 外部事务提交一次新属性和 R.CurrentHP */ }
```

- `FInstance`：原模板ID、grade0–3、一个 `FEnchant`。`FEnchant{EPackage::Mixed,5,{{"AFF-P-001",25},{"AFF-P-002",20},{"AFF-N-016",15}}}`；None必须tier0/空词条。
- `FindTemplate` / `FindAffix`：全45/36只读定义，未知返回nullptr；没有静默替代/重抽。
- `LegalAffixRange(templateID,affixID,tier)`：只读原始定义资格；返回正整数闭区间，空区间为Min0/Max-1。优先用ID重载，不把当前实例的派生护甲填入 `FTemplate`。`ValidateInstance` / `ValidateEnchant`拒绝非法package/等级/极性/组/幅度。未按全局cap删除合法词条。
- `FContext.Other`：调用者已验证适用来源的当前道具/遗物/状态 **同stat贡献**，百分数12代表12%，不是0.12；本核不认识这些来源的触发资格。九天赋是当前Run已冻结快照，校验rank与前置，不读取实时账号购买。
- `RawBonus`：所有有效贡献及grade、天赋的未封顶和，**不含**基础crit5、原甲护甲/魔抗、原甲poise及角色base30。`Final`：crit / armor / ward / poise四项含基础值并封顶；其余项为封顶贡献幅度。不能把 `Final.ArmorFlat` 再加原甲一次。
- `FResolved`：直接伤害/削韧倍率、完整动作时间倍率、射程外边界倍率、crit最终概率/倍率、技能CD倍率、实际装填秒数、主攻/武器技专注成本、最终防护/韧性/最大HP/当前HP/移动/恢复与治疗/易伤倍率。元素幅度在 `Final`；没有元素触发实现。
- `ArmorConditionalActive`只表示外部已验证原甲条件成立；LGT002/003的1.12/1.14、ROB003的20/s是替换基值。条件计时/取消/冷却由调用方维护。本冻结工具对来源trait数字作校验，但没有把文字规则变成触发器。
- `MovementConstraint`是外部已有动作、空中、受伤、寒缓等限制的乘积，作用在idle派生cap后；不会修改跳跃物理、闪避距离或无敌。
- `OriginalQuantile` / `MapOriginalQuantile`只计算原整数桶中心分位数与合法新等级映射，保留原q由实例/事务层负责；无RNG、抽词、收费或升级提交。空下一档返回nullopt，调用方必须在收费前检查。
- `HealingAmount(R, baseHP, actualHP, sourceBudget)` 与 `LifestealAmount(currentRecipient, snapshotLifestealPct, eligibleDirectHPLoss, attackRemaining, rollingRemaining, actualHP)` 只返回本次合法量；必须在实际治疗点读取当前治疗倍率/最大HP和 actualHP，不用攻击40%快照的旧治疗值。吸血预算上限3/6在效率后应用，预算实际消费由调用方原子完成；本核不持有或推进任何预算。

## 已核对的数值与动作接线边界

- KNF+3(15%)、P001V25%、ATK4(8%)得到48%，不是相乘；再有其他15%时raw63、cap50、12基础段变18。
- LGT001原甲14，grade3贡献2.1，GRD3贡献6，最终22.1；N008仍只有IV13–14，V为空。HVY001原85、grade3为12.75、guard6、P014V25，最终128.75。
- HP原100，VIT3贡献12%、N011V减少20%，最终92；旧实际88保持88，不能中途先截成80；加上限不回HP，死者0与存活0.4原样保留。
- full talents unarmored：最大HP112、护甲/魔抗6、短刀直接伤害12.96、削韧6.36、crit7%、移速272.95、恢复13.08/s。天赋各rank只贡献一次。
- 攻速仅输出 `ActionTimeScale=1/(1+bonus/100)`。D03所有动作时间、子段和正有效窗至少0.02s应由动作核统一处理；此模块不新建时轴，不用reload缩后摇，不刷新现存CD。
- 伤害适配只用于武器直接分段：原段×距离因子×目标比例×DamageMultiplier，再crit/目标当时减伤/易伤各一次；不能放大道具固定伤害、燃烧或shock，不能重复乘穿透次目标0.6。
- 源profile的 SPR001 skill未列min_range字段，其历史默认0；当前首批动作核明确min45。本核保留源原文/哈希，仅用于原模板资格，输出外边界倍率；不会用历史单招原稿覆盖当前三段或技能形状。当前所有资格格结果不受此差异影响。
- 快照时机仍由D03动作核控制：起攻锁完整时轴，40%锁攻击伤害/资源/crit；命中时读取目标当前防护/易伤；治疗时读取当前治疗属性。此核没有模拟上述时钟。

## 复现命令

```powershell
& 'F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe' -X utf8 -B 'F:\Ourgame\tools\scripts\prepare-equipment-stats.py' --check
& 'F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\RunEquipmentStats.ps1' -Phase VERIFY
```

测试编译产物与原日志在 `%TEMP%\OurgameEquipmentStats\<timestamp>-<phase>`，每次新目录不覆盖。若明确更新冻结源，可运行生成工具不带`--check`，它只更新本头文件数据块与本测试黄金夹具块；先独立审查规则变化，不将数据再生成当作行为验收。

## 来源与实现指纹

下表为本轮实际文件SHA256；来源均只读，未执行会写设计JSON的build_design_catalog.py。

| 来源 | SHA256 |
|---|---|
| `docs/design/equipment-v2/00-属性附魔共同规则.md` | `12278ea720388723cbbc15408bc166e7ffe542aa4f3fe03ca455ad2f52974a17` |
| `docs/design/equipment-v2/01-属性体系与计算.md` | `fe4027c4a177c7b4125ef0ea9dd8f27342c4b0a8fa573b34776008fb8e43811c` |
| `docs/design/equipment-v2/04-逐件附魔适配与示例.md` | `ee6c5701d3a377c5fc9149b97497ad9235f9664ffffdaa87ca87e5563056edb7` |
| `docs/design/equipment-v2/stat-definitions.json` | `2f8c3fe15aa2dc940f867be118b948e80ae9ae4c654bc70580021ade79d37bc9` |
| `docs/design/equipment-v2/affixes.json` | `e6e3737cb15e64f0782dae0f0652dbac80ebaabf9ee9d97c46bd3e439402c75e` |
| `docs/design/equipment-v2/equipment-profiles.json` | `1cace928f0f08c3f9afb3e093e1070785f59cd50a6210882a45d8d1b7597f85a` |
| `docs/design/equipment-v2/enchant-rules.json` | `520214b7b3b8195f769f7a77c7ecc40baca2039746f7bc73cbe49b4445756a55` |
| `docs/design/equipment-v1/weapons.json` | `95757819382832cfa31e6596f3ba90f1e983e83fbd69504da3c99d5ea2a272b4` |
| `docs/design/equipment-v1/armor.json` | `9407e458aef80b9f0d8f0e958b089e7b7a6f4180aef41b7b7df97534fe780e9d` |
| `docs/design/items-v1/common-rules.json` | `b5815a10f313b7364b1dde66b0eac9f703104ea260d4e4470094cffe31652e99` |
| `docs/design/economy-v1/equipment-growth.json` | `4002351b1de27128f1a1db27020cdec8f46ab776bfc285be34742cbee23eedb9` |
| `docs/design/progression-v1/talents.json` | `67f12dc215a628d94c41efa2a92e9a3929785036cab86d4cd11ec8dc958fb2f5` |

| 本轮实现文件 | SHA256 |
|---|---|
| `UnrealGame/Source/CodexDungeon/DungeonEquipmentStats.h` | `741ec843098b9cc08755af0842194173cf30af37c7e0801b076f4726bc01926f` |
| `UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentStatsStandalone.cpp` | `949bd50e5a25baa66139e9f09c5a2142c649eda78540b3aa1554e2c35054960d` |
| `UnrealGame/Source/CodexDungeon/Tests/RunEquipmentStats.ps1` | `e2bc4ccd55818ca15cf22205b5410f940dc8a4c675016bfaa1ad09f7be521157` |
| `tools/scripts/prepare-equipment-stats.py` | `a82dbc6dbc19a835974af03e28ff0d12b65d99b3dda3fbb0296a26adbdbe6d0c` |

## 原始日志留存

以下为每次原日志完整文本副本，连同原文件路径、字节数和SHA256保留在本受管报告中；编译失败与行为RED分别标明，不隐藏中间错误。Temp原件亦保留。本轮只写指定五个源/文档文件。

### 20261015-003814-235-RED

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-003814-235-RED\standalone.log`；491 bytes；SHA256 `1e2443e39873c73ea9f30de3c82af6685fd341b04ccab4b7e9955af89808ac02`。

```text
PHASE=RED; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\../DungeonEquipmentStats.h(1): error C2220: 以下警告被视为错误
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\../DungeonEquipmentStats.h(1): warning C4819: 该文件包含不能在当前代码页(936)中表示的字符。请将该文件保存为 Unicode 格式以防止数据丢失
COMPILE_EXIT=2
EXIT_CODE=2
```

### 20261015-003825-035-RED

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-003825-035-RED\standalone.log`；8101 bytes；SHA256 `6b4aa0f92831f0346b4d41103ff29c4e4591a908a32d39bc5156ee921d7f6d65`。

```text
PHASE=RED; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
FAIL original template lookup WPN-KNF-001
RANGE_MISMATCH WPN-KNF-001 AFF-P-001 tier=1
RANGE_MISMATCH WPN-KNF-001 AFF-P-001 tier=2
RANGE_MISMATCH WPN-KNF-001 AFF-P-001 tier=3
RANGE_MISMATCH WPN-KNF-001 AFF-P-001 tier=4
RANGE_MISMATCH WPN-KNF-001 AFF-P-001 tier=5
RANGE_MISMATCH WPN-KNF-001 AFF-P-002 tier=1
RANGE_MISMATCH WPN-KNF-001 AFF-P-002 tier=2
RANGE_MISMATCH WPN-KNF-001 AFF-P-002 tier=3
FAIL original template lookup WPN-KNF-002
FAIL original template lookup WPN-KNF-003
FAIL original template lookup WPN-DAO-001
FAIL original template lookup WPN-DAO-002
FAIL original template lookup WPN-DAO-003
FAIL original template lookup WPN-SWD-001
FAIL original template lookup WPN-SWD-002
FAIL original template lookup WPN-SWD-003
FAIL original template lookup WPN-GSW-001
FAIL original template lookup WPN-GSW-002
FAIL original template lookup WPN-GSW-003
FAIL original template lookup WPN-SPR-001
FAIL original template lookup WPN-SPR-002
FAIL original template lookup WPN-SPR-003
FAIL original template lookup WPN-HAL-001
FAIL original template lookup WPN-HAL-002
FAIL original template lookup WPN-HAL-003
FAIL original template lookup WPN-XBW-001
FAIL original template lookup WPN-XBW-002
FAIL original template lookup WPN-XBW-003
FAIL original template lookup WPN-PST-001
FAIL original template lookup WPN-PST-002
FAIL original template lookup WPN-PST-003
FAIL original template lookup WPN-SGN-001
FAIL original template lookup WPN-SGN-002
FAIL original template lookup WPN-SGN-003
FAIL original template lookup WPN-RFL-001
FAIL original template lookup WPN-RFL-002
FAIL original template lookup WPN-RFL-003
FAIL original template lookup WPN-STF-001
FAIL original template lookup WPN-STF-002
FAIL original template lookup WPN-STF-003
FAIL original template lookup ARM-LGT-001
FAIL original template lookup ARM-LGT-002
FAIL original template lookup ARM-LGT-003
FAIL original template lookup ARM-MED-001
FAIL original template lookup ARM-MED-002
FAIL original template lookup ARM-MED-003
FAIL original template lookup ARM-HVY-001
FAIL original template lookup ARM-HVY-002
FAIL original template lookup ARM-HVY-003
FAIL original template lookup ARM-ROB-001
FAIL original template lookup ARM-ROB-002
FAIL original template lookup ARM-ROB-003
FAIL 45 x 36 x I-V source-authored eligibility cells
FAIL light armor negative IV clipped to14 and V empty
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL first batch 5weapon x4armor base combinations
FAIL base direct segment preserved
FAIL full talents unarmored HP protection and crit
FAIL full talents cumulative ranks contribute once
FAIL partial talent snapshot
FAIL grade15 affix25 talent8 summed rather than multiplied
FAIL same stat capped once after all sources
FAIL grade original14 times .15 flat plus guard does not expand negative eligibility
FAIL heavy grade based on85 not current enchanted armor
FAIL inactive weapon growth and enchant dormant
FAIL existing negative can reduce current defense to0 without invalidating original roll
FAIL workshop chapter caps
FAIL natural drop caps separate from enchanting tier
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL every positive global stat cap
FAIL every negative global stat cap
FAIL move stat cap then armor derived cap then existing air constraint
FAIL maxHP change clips only once after talent12 and curse20
FAIL no intermediate cap80 truncation before talent contribution
FAIL maxHP increase gives no free heal
FAIL maxHP increase cannot revive
FAIL no artificial minimum1 HP
FAIL reload talent does not change attack timeline
FAIL reload summed34 capped25
FAIL reload talent does not create sword reload
FAIL good staff focus negative sign
FAIL bad staff focus positive sign
FAIL robe regeneration base14 plus talent9pct
FAIL conditional20 replaces14 without resetting clock
FAIL conditional movement replaces1.04 by1.12
FAIL defense150 and mitigation60pct cap
FAIL crit base5 affix15 talent2 capped20
FAIL stagger25 plus talent6 cap25
FAIL good cooldown reduces duration
FAIL bad cooldown increases duration
FAIL actual healing efficiency before source and missingHP caps
FAIL lifesteal post efficiency attack and rolling budget caps
FAIL unknown active instance rejected
FAIL armor in weapon slot rejected
FAIL grade4 rejected
FAIL negative grade rejected
FAIL negative previousHP rejected
FAIL NaN previousHP rejected
FAIL infinite contribution rejected
FAIL negative state movement constraint rejected
FAIL talent over maximum rejected
FAIL invalid prerequisite snapshot rejected
FAIL original integer bucket midpoint3of10
FAIL upgrade uses original q across tiers
FAIL fixed interval midpoint1of2
CHECKS=186 FAILURES=176; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=1
```

### 20261015-004017-391-GREEN

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004017-391-GREEN\standalone.log`；244 bytes；SHA256 `5c8ded5e52881ba00a326d2a7d20280840b65ed58b2f3b0d0a5452845a0952a0`。

```text
PHASE=GREEN; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=8412 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```

### 20261015-004144-525-RED

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004144-525-RED\standalone.log`；1171 bytes；SHA256 `632f2a85f1020b0851b3a1d313bcdff46867e6e26b92d218b98ff2d90b3c92cf`。

```text
PHASE=RED; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\DungeonEquipmentStatsStandalone.cpp(957): error C2660: “DungeonEquipmentStats::LifestealAmount”: 函数不接受 5 个参数
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\../DungeonEquipmentStats.h(385): note: 参见“DungeonEquipmentStats::LifestealAmount”的声明
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\DungeonEquipmentStatsStandalone.cpp(957): note: 尝试匹配参数列表“(DungeonEquipmentStats::FResolved, int, int, int, int)”时
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\DungeonEquipmentStatsStandalone.cpp(957): error C2660: “DungeonEquipmentStats::LifestealAmount”: 函数不接受 5 个参数
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\../DungeonEquipmentStats.h(385): note: 参见“DungeonEquipmentStats::LifestealAmount”的声明
F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\DungeonEquipmentStatsStandalone.cpp(957): note: 尝试匹配参数列表“(DungeonEquipmentStats::FResolved, int, int, int, int)”时
COMPILE_EXIT=2
EXIT_CODE=2
```

### 20261015-004155-110-RED

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004155-110-RED\standalone.log`；323 bytes；SHA256 `c63c20bfa7837cd2b5390acd50e601bae896202f12fb907a1d3a33a65d5fcfc6`。

```text
PHASE=RED; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
FAIL lifesteal must read actual HP at heal point instead of earlier snapshot HP
CHECKS=8417 FAILURES=1; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=1
```

### 20261015-004226-602-GREEN

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004226-602-GREEN\standalone.log`；244 bytes；SHA256 `ce1537de9c3d9bd5d8c73f659b2514c29806b0aeecbe977d6d653d6b83941a66`。

```text
PHASE=GREEN; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=8417 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```

### 20261015-004405-514-VERIFY

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004405-514-VERIFY\standalone.log`；320 bytes；SHA256 `110d6739c7e288aa541060688202654e942898dd55b1794ef629ece80664d435`。

```text
PHASE=VERIFY; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=8417 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```

### 20261015-004620-649-VERIFY

原件：`C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-004620-649-VERIFY\standalone.log`；321 bytes；SHA256 `9a53f7d156453a3fee578078274638fbbddf29c0f925de768fb1de925aae1603`。

```text
PHASE=VERIFY; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=16405 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```

## 只读审查 P2 修复：吸血双时点

stats_review独立确认并复现：吸血率属攻击锁点快照，healing/maxHP属实际治疗点当前接收者。旧helper同一R取两者无法表达换装后的旧弹。新增独立 `SnapshotLifestealPct` 必填参数；无旧单时点wrapper，避免继续误用。最终签名 `LifestealAmount(const FResolved& CurrentRecipient, double SnapshotLifestealPct, double EligibleDirectHPLoss, double AttackRemaining, double RollingRemaining, double ActualHP)`。冻结率必须有限且0..5；当前接收者属性和HP仍在治疗点读取，预算消费仍外层。

独立回归：旧XBW锁汲血V5%，命中前换无吸血SWD且当前甲healing+25%，实扣20、HP50，正确1.25；旧实现传当前R是0，传旧R是1。可编译RED 16,406/1 → GREEN 16,406/0，未改来源或UE文件。此前16,405/0为审查前历史结果，不回写为已覆盖此缺口。

修复后 `UnrealGame/Source/CodexDungeon/DungeonEquipmentStats.h` SHA256 `c33671c5a4fd6cf0c68ede77c473d649692dc9718f7fbd3fb9a1896a26dcb9e7`。

修复后 `UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentStatsStandalone.cpp` SHA256 `275dabc8a56a30b2470237c6b1cdd1147284fa27244b04a69e21c91cbe610aba`。

原日志 `C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-005130-634-VERIFY\standalone.log`（321bytes，SHA256 `9a53f7d156453a3fee578078274638fbbddf29c0f925de768fb1de925aae1603`）：

```text
PHASE=VERIFY; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=16405 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```

原日志 `C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-005334-817-RED\standalone.log`（409bytes，SHA256 `d684a6e2fb53853b870a38a81486104b08fabc2f4cbc873625b5148c46416320`）：

```text
PHASE=RED; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
FAIL old projectile keeps locked5pct lifesteal while new armor gives current25pct healing
CHECKS=16406 FAILURES=1; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=1
```

原日志 `C:\Users\22499\AppData\Local\Temp\OurgameEquipmentStats\20261015-005418-991-GREEN\standalone.log`（320bytes，SHA256 `9cce121c472c5b1cf392cc3b8bd54ee2e5acefad1f16c52f31042b8df52c7bab`）：

```text
PHASE=GREEN; standalone C++17 equipment stats only; no UE build/runtime acceptance.
DungeonEquipmentStatsStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonEquipmentStatsStandalone.cpp
COMPILE_EXIT=0
CHECKS=16406 FAILURES=0; original eligibility cells=8100; active first batch combinations=20
EXIT_CODE=0
```
