# 装备实例控制军剑与轻甲画面：执行计划

> 执行方式：Root 在当前工程逐步实施，辅助代理只写各自候选与复核；沿用用户自动授权与现有规格，不重复请求确认。

**Goal:** 让实际提交的军剑、无甲或轻甲控制当前钟盔画面，真实拾取取消、提交、替换、重拾前后画面相符；同时仅在新绑定模式修第三刀两处剑轴。

**Architecture:** 使用已经编译、三项真实测试通过的只读 resolver。HUD/Presentation 同次 Resolve 的结果控制武器与全部甲层，不由旧试装开关授权装备。新独立 QA Actor 用普通 Enter/E/A/J 和公开源注册 API 驱动实际事务；旧三段输入 Probe 和历史 V001 保留。

**Tech Stack:** UE5.5.4/C++，现有 1085 Production 包，1280×720 native BGRA lossless capture。

**Spec:** `evidence/sword-lightarmor-completion-gap-v001/equipment-binding-proposal-v001.md`；`source-assets/production/fairytale-sword-equipment-binding-v001/consumption-v001/README-consumption-v001.md`；EV048 与完整首批目标保持。

## Constraints and review focus

- 人物最高72px、独立剑.50、游戏UI隐藏；不改掌心、身体RGBA、帧时长、战斗时钟、ID/RNG或存档格式。
- 真实无甲不画甲；只有实际LGT且支持的状态才画其甲片；MED等未支持外观给明确钟盔占位，不能偷换轻甲或旧纯人类。
- 拾取进行中仍显示旧提交实例，取消不提前换皮；替换掉落后重拾保留实际实例身份与合法版本变化。
- 新Bound模式优先于旧美术开关；旧开关独立效果保留。只读resolver不打开Continue门，也不推进时钟或重播声音。
- 小比例剑轴CPU预测不能证明GPU无穿插；实际运行原图、连续片段和独立复核共同限定结论。

## Tasks

- [x] **1 Native RED:** 新增 `DungeonFairytaleEquipmentBoundProbe.h/.cpp` 和一个HUD显式spawn分支，候选先与v116旧DrawState兼容。保留before/候选freeze，真实编译；实际运行同一拾取流程，记录NoArmor被旧flag画甲等真实失败，而不是制造编译错误。RED快照明确没有当前full141声明。
- [x] **2 Actual consumer:** 复核14候选文件与10 baseline pins，对 `DungeonHUD.h/.cpp`、`DungeonFairytaleSwordPresentation.cpp`、`DungeonFairytaleSwordDrawState.h`、`DungeonFairytaleSwordProbe.cpp` 仅应用已审小hunks，手工保留任务1新spawn，旧Probe.Tick不变。
- [x] **3 Two-axis correction:** 新增 `DungeonFairytaleSwordPrimary3V002.inl`，仅Bound选择；Find复制V001 marker，仅phase1/3 directedaxis修正。旧V001及冻结marker文件不变。记录旧/新有符号基线余量与盔轮廓源样本重叠，未知握柄保持未知。
- [x] **4 Current GREEN:** 实际 `tools/scripts/unreal-build.ps1` exit0，然后 `tools/scripts/test-first-room.ps1` 完整141；逐项核Success/errors/warnings/notRun/inProcess。冻结当前Source/DLL/Production/候选、实际日志和测试报告。
- [x] **5 Same native flow:** 原probe原期望不改，运行同一流程；无甲/取消/提交/LGT三段/MED替换/同实例重拾的actualview、draw stack与原图相符。异常保留失败，不用元数据代替可见审图；未证的Continue/全状态/正式掉落保持未完成。
- [x] **6 Retain and review:** 原件、展示副本、版本来源索引先保存F/E新批次，再看原尺寸图及录像；更新README、需求台账和progress当前权威字段，不把任何单元提前计完整。

## Rulings

- 上一目标回合归类为progress：48新资源实际导入、三段实录与当前141检查，独立审图改变下一步（优先适配）；非状态复述。
- 当前已授权持续实现与自动决策；现有UE工程与快照作为执行位置。Root独占实际Source/UE/ledger，避免多个编译进程和固定路径副本混淆。不在本轮提交、推送、发布或清理历史。
- 新QA源只为复现实际公开事务，不冒称已经完成正式关卡掉落/商店获取。静音捕获也不冒音效验收。
- 灰甲与灰衣的大形对比仍需后续原生美术修改；本轮两轴修正只解决独立剑姿态，不用放大角色或重绘源图掩盖问题。
- 当前实际E剩余51.63GB、F剩余99.09GB。新批次E原始PNG使用无损ZIP保存原始文件字节，展示文件保持普通副本；逐项两遍解包校验大小/SHA，F原PNG与所有历史批次不删除。该存储方式符合E保存规则的原件/展示/来源保留要求，不改原像素或游戏时钟。

**Completion boundary:** 此计划完成也仅使完整首批目标更接近；5武器/4甲/5敌人/Boss、20搭配、全状态/特效/音效/完整存取与15依赖均保持原范围。

验收边界更新：以上六项仅绑定候选实施与受控验证完成；独立审图发现pending临时脱甲/消剑，下一轮先补，完整内容仍0/15。
