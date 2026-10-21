# 17条候选音效复核与首单元事件映射

日期：2026-10-14。**实际听过0条。** 本轮只有真实源文件读取、确定性波形/频谱分析和内存重叠计算；没有新生成声音、外部API、UE运行或游戏代码改动。以下映射与预算均为待试听提案，不能标完整声包已完成。

## 事实、推理与风险

- 事实：17条原件哈希全部匹配audio-v001 manifest，仍为48kHz mono PCM16、无采样削波、首尾0值。Windows System.Media.SoundPlayer已成功Load已有WAV；没有调用Play/PlaySync，当前工具没有本地听感回传能力。
- 推理：军剑三段可以按真实ActiveWindow分别消费三条短破风；石像苏醒/运动/刹停有材料候选。关键锁线、正式死亡与破韧区别仍没有完整成品，不能只凭17个文件宣布完整单元声音达标。
- 风险：两条满增益重剑重复播放已能数值超满幅；单条5dB以上余量不代表叠层安全。零首尾只帮助有限one-shot，不证明燃烧或石翼适合循环。内部最大采样跳变主要含有噪声频率，不能当作已听见爆音。

## 逐文件数值与语义

原件目录：`source-assets/production/audio-v001`。首尾1ms幅度、频谱质心、能量分位时刻及全部SHA256见JSON。频谱/波形指标不等于音色评价。

| 候选 | 时长ms | 采样峰值dBFS | 能量中心ms | 最大相邻采样差 | 循环/用途边界 |
| --- | --- | --- | --- | --- | --- |
| AUD-SWD-WHOOSH-01 | 190 | -6.376 | 87.6 | 0.3234 | 仅有限事件one-shot，不循环 |
| AUD-GSW-WHOOSH-01 | 340 | -5.515 | 162.9 | 0.1693 | 仅有限事件one-shot，不循环 |
| AUD-SPR-THRUST-01 | 75 | -6.936 | 35.8 | 0.4667 | 仅有限事件one-shot，不循环 |
| AUD-SWD-WHOOSH-02 | 210 | -6.376 | 97.7 | 0.3084 | 仅有限事件one-shot，不循环 |
| AUD-GSW-WHOOSH-02 | 380 | -5.515 | 179.6 | 0.1784 | 仅有限事件one-shot，不循环 |
| AUD-SPR-THRUST-02 | 85 | -6.936 | 39.8 | 0.4247 | 仅有限事件one-shot，不循环 |
| AUD-SWD-WHOOSH-03 | 230 | -6.376 | 108.1 | 0.3905 | 仅有限事件one-shot，不循环 |
| AUD-GSW-WHOOSH-03 | 420 | -5.515 | 199.2 | 0.2030 | 仅有限事件one-shot，不循环 |
| AUD-SPR-THRUST-03 | 90 | -6.936 | 41.7 | 0.4580 | 仅有限事件one-shot，不循环 |
| AUD-XBW-RELEASE-01 | 200 | -6.021 | 16.0 | 0.1226 | 仅有限事件one-shot，不循环 |
| AUD-FIRE-LAUNCH-01 | 300 | -6.376 | 135.9 | 0.3163 | 仅有限事件one-shot，不循环 |
| AUD-FIRE-BURN-SHORT-01 | 480 | -7.959 | 234.3 | 0.2741 | 原有燃烧tick短纹理；不当连续火层/新伤害 |
| AUD-STONE-AWAKE-01 | 650 | -6.021 | 73.0 | 0.2037 | 仅有限事件one-shot，不循环 |
| AUD-STONE-WING-01 | 280 | -6.559 | 132.9 | 0.2253 | 石翼动作，不借用为盾击成品 |
| AUD-STONE-ARMOR-SCRAPE-01 | 320 | -6.745 | 36.8 | 0.4028 | 仅有限事件one-shot，不循环 |
| AUD-STONE-CHARGE-BRAKE-01 | 340 | -5.680 | 41.2 | 0.1873 | 仅有限事件one-shot，不循环 |
| AUD-STONE-FRACTURE-01 | 500 | -5.515 | 54.3 | 0.4211 | 死亡/破韧共享材料，正式区别仍缺 |

各文件0→0边界没有原始端点台阶，但重复循环会反复出现8/15ms包络及静段，可能形成抽吸/拍动；本轮没有听感证据，17条全部保留`loop_approved=false`。破风能量中心晚于事件起点是包络事实，不能拿破风最响处代替敌人50%锁定信号。

## 内存重叠计算

下列均未输出音频文件，不是运行混音。CC0素材按均值转mono/线性插值，仅作近似；UE的pitch、空间、总线与编码未模拟。

| 场景 | 浮点和峰值dBFS | 超满幅采样数 | 最大重叠声部 | 所有单峰相加的保守上界dBFS |
| --- | --- | --- | --- | --- |
| duplicate_heavy_full_gain | 0.506 | 2 | 2 | 0.506 |
| all17_full_gain_same_time | 6.330 | 124 | 17 | 18.318 |
| sword_ground_chain_base | -18.417 | 0 | 1 | -8.874 |
| spear_secondary_base_three_subhits | -18.977 | 0 | 1 | -9.435 |
| sword_and_one_generic_contact_current_scalars | -8.197 | 0 | 2 | -5.862 |
| wake_sword_two_stone_contacts_budget_scalars | -14.550 | 0 | 4 | -6.459 |

首个重复重剑场景故意模拟去重失效；全17同点是极端压力而不是合法连招。军剑v2连续基础击出时刻为0.17/0.75/1.36s，枪技能子击为0.18/0.28/0.38s；这只是未修饰设计时轴，正式以已接纳最终动作事件为准。

## 首个军剑／轻甲／石骑逐事件建议

### WPN-SWD-001

| 权威来源 / D12事件 | 候选 | 建议线性增益上限 | 触发与缺口 |
| --- | --- | --- | --- |
| DungeonContentCombat::Started / AUD-WPN-PREP | CC0-PREP | 0.18 | Accepted action starts; once per AttackID；drawKnife1峰值很低且0.400s长；仅材质候选，未确认适合作170/150/220ms前摇，不应盲目抬总线。 |
| DungeonContentCombat::ActiveWindow / AUD-WPN-SWING | AUD-SWD-WHOOSH-01, AUD-SWD-WHOOSH-02, AUD-SWD-WHOOSH-03 | 0.25 | Ground combo stage1/2/3 respectively; once per real AttackID/SubhitID；基础时轴击出在0.17/0.75/1.36s；实际使用已接纳最终时轴。空挥也有声，不能由命中或动画帧再发。 |
| WPN-SWD-001 secondary accepted active window / AUD-WPN-SWING | AUD-SWD-WHOOSH-02 | 0.25 | One actual secondary active window; unmodified onset0.20s；进身斜斩暂选第二段材料；不加位移/范围/额外伤害，正式技与普攻音色仍待听感区分。 |
| Airborne primary actual first active window / AUD-WPN-SWING | AUD-SWD-WHOOSH-01 | 0.25 | One first-stage attack per original airborne allowance；空中不连续接三段，不因落地补播第二次；仍用真实AttackID去重。 |
| Accepted effective damage receipt on target / AUD-DAMAGE-DIRECT | CC0-STONE-CONTACT, CC0-SOFT-CONTACT | 0.15 | actualDamage>0; choose exactly one target-material main contact；打石骑选石体、软体选软体；同段多目标40ms聚合最多2声，不能合并伤害收据。当前代码通用ImpactLight仍只是原型。 |
| Original attack segment ends with no accepted hits / AUD-WPN-MISS | 静音/缺口 | 0.00 | Optional cosmetic only；建议静音，不能播碎裂/撞击假装命中；退出清理不是落空。 |
| Actual inventory/switch commit / AUD-WEAPON-SWITCH | CC0-CLOTH | 0.08 | Ownership/active weapon change committed；布料是换装材料，尚未定稿鞘/扣音；槽位预览不成功。 |

### ARM-LGT-001

| 权威来源 / D12事件 | 候选 | 建议线性增益上限 | 触发与缺口 |
| --- | --- | --- | --- |
| D04 actual equip/drop/ownership commit / AUD-INVENTORY-COMMIT | CC0-CLOTH | 0.08 | Actual LGT001 equip commit only；行路短衣轻步为常驻属性，保持静音；不能新造proc或换装回资源声。 |
| Accepted effective player damage after invulnerability / AUD-PLAYER-HURT | CC0-SOFT-CONTACT | 0.15 | Actual hurt receipt, not every incoming collision；只有接触材料，没有非语言呼吸成品；若已播主接触则不再叠同一软体声。 |

### ENM-STN-001

| 权威来源 / D12事件 | 候选 | 建议线性增益上限 | 触发与缺口 |
| --- | --- | --- | --- |
| DungeonStoneKnight::WakeStarted / AUD-DORMANT-AWAKE | AUD-STONE-AWAKE-01 | 0.18 | One actual wake event; warning lasts0.85s；声长0.65s，尾部静段不缩短0.85s可视苏醒；真实受伤/近触/兜底共用同WakeEventID。 |
| DungeonStoneKnight::WakeCompleted / 新增展示路由待明确 | 静音/缺口 | 0.00 | Original wake completed；不再播苏醒、攻击或掉落成功。 |
| DungeonStoneKnight::AttackStarted / AUD-ENEMY-TELL-START | AUD-STONE-ARMOR-SCRAPE-01 | 0.20 | A1/A2 real windup begins；0.32s刮擦仅材质；A1锁点0.45s/A2锁点0.35s，不能把开始音当锁定。 |
| DungeonStoneKnight::AimLocked / AUD-ENEMY-LOCK | 静音/缺口 | 0.20 | Exactly A1 start+0.45s or A2 start+0.35s；仍缺独立稳定短锁线音，不能用死亡碎裂或刹停冒充；视觉锁线必须可读。 |
| DungeonStoneKnight::ChargeStarted / 新增展示路由待明确 | AUD-STONE-ARMOR-SCRAPE-01 | 0.18 | Actual A1 charge starts at base0.90s; once；可暂用有限运动材料；不能按高频Movement或动画帧重复触发，不声明循环。 |
| DungeonStoneKnight::Movement / 新增展示路由待明确 | 静音/缺口 | 0.00 | Numerous authoritative movement updates；此高频事件禁止默认一条一声。脚步/持续运动另需明确展示钩子。 |
| DungeonStoneKnight::ActiveWindow for Shield / AUD-WPN-SWING | AUD-STONE-ARMOR-SCRAPE-01 | 0.18 | Actual A2 shield sweep at base0.70s; once；只能作为盾体运动材料，不拿石翼音当盾撞成品；真实玩家命中另走接触声。 |
| DungeonStoneKnight::Hit then accepted player damage receipt / AUD-DAMAGE-DIRECT | CC0-SOFT-CONTACT | 0.15 | Only effective target damage; target armor may change material selection；撞墙/碰盟友不产生玩家伤害音；轻甲没有新增格挡/反伤。 |
| DungeonStoneKnight::ChargeStopped / 新增展示路由待明确 | AUD-STONE-CHARGE-BRAKE-01 | 0.18 | One actual early stop or normal end; wall/body/valid-hit facts kept separate；刹停声不是命中或收益；停止先前运动尾声后播，不能同点同时叠整条刮擦和刹停。 |
| DungeonStoneKnight::RecoveryStarted / AUD-RECOVERY-OPEN | 静音/缺口 | 0.00 | Only true recovery starts；可静音；A1完整1.60s/A2完整0.90s反击窗口不受声长影响。 |
| DungeonStoneKnight::Damaged with accepted effective loss / AUD-DAMAGE-DIRECT | CC0-STONE-CONTACT | 0.15 | Stone target actualDamage>0; one main contact；不套额外通用ImpactLight，不以每次削韧伪报破韧。 |
| DungeonStoneKnight::PoiseBroken / AUD-POISE-BREAK | AUD-STONE-FRACTURE-01 | 0.18 | Actual accepted break, not poise damage during protection；碎裂仅共享材质；死亡和破韧尚未做出稳定区别，完整声包仍有缺口。 |
| DungeonStoneKnight::Died / AUD-ACTOR-DEATH | AUD-STONE-FRACTURE-01 | 0.18 | Authoritative terminal death after same-time damage；同点死亡优先声部并取消破韧尾声，不叠两遍同文件；不等于奖励/清房/Boss胜利。 |

候选路径：17条ID对应同名`__v001.wav`；CC0标记对应JSON `selected_CC0_materials`中的精确原路径与hash。它们沿用本地包许可，不把工具许可或原作素材引入项目。

## 首单元试听台声部预算提案

只适用于一名军剑玩家+一只石骑、无音乐/环境层的小试听台；不覆盖D12全游戏24非关键世界声/2UI/3音乐层的长期建议。8声上限及以下增益尚未实现或运行验证。

| 分组 | 最大声部 | 线性增益上限 | 假定源采样峰值上限 | 策略 |
| --- | --- | --- | --- | --- |
| critical_warning | 2 | 0.20 | 0.53 | highest; reserve source identity; stable distinct cue still missing |
| player_swing | 1 | 0.25 | 0.48 | one per AttackID/Subhit; cosmetics cannot consume combat RNG |
| main_contacts | 2 | 0.15 | 0.90 | 40ms similar-material grouping; never merge damage receipts |
| stone_motion | 1 | 0.18 | 0.53 | per actor one; stop/fade previous movement before brake/wake tail |
| hurt_break_death | 1 | 0.18 | 0.53 | per actor terminal death > true poise break > hurt; no duplicate fracture |
| ui_commit | 1 | 0.08 | 0.90 | neutral/equip cosmetic; success only actual receipt |

若所有源峰值/增益/并发帽都实际满足，无后级EQ/增益提升，保守同相和上界为0.8648，即-1.262dBFS。此值只是采样峰值算术，不是dBTP保证；加入其他敌人/音乐/后期处理后不再成立。预警仍应按D12建议对非关键战斗压3dB、音乐压6dB，20ms起/180ms回，最终需试听，不能靠本表宣称可听清。

## 当前实现与后续边界

当前Fighter静态源码在真实ActiveWindow选择三段破风，以PlaySound2D/0.25播放；通用受击仍是历史ImpactLight/0.45并有pitch变化，不等于已完成目标材质或石骑声包。历史导入报告把该UAsset溯源到impactGeneric_light_000.ogg，本轮只读了本地原OGG，未解码当前UAsset。纯石骑核已有WakeStarted/AimLocked/ChargeStarted/ChargeStopped等事件，但不证明其UE演员音频适配已经接通。

后续先解决独立锁线签名与死亡/破韧区分，再验事件去重、可控运动声部、静音视觉冗余、暂停/恢复游标及取消/死亡/跨房清理。高频Movement不能每条一声；普通死亡不清已发弹；同点死亡/奖励严格沿权威结果。未消费的提示不能提前泄露休眠/future。

可重跑分析：

```powershell
& 'C:/Users/22499/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'F:/Ourgame/tools/scripts/audit-first-content-sfx.py'
```

机器记录：[audio-event-map.json](audio-event-map.json)。重跑只更新本MD/JSON，不产生WAV或改变原始素材。
