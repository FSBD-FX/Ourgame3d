# 钟盔玩家／军剑／轻甲音频缺口只读审计 v001

日期：2026-10-19（Asia/Shanghai）。范围仅为当前玩家动作、现有声音来源和恢复后消费边界。没有运行 UE、播放声音、调用供应商、生成音频或修改 Source／Content／工具／媒体／冻结／账本；本文件是本子任务唯一新增文件。不能将源码事件、PlaySound2D 请求或 PCM 非零等同于已试听或最终混音验收。

当前编译来源：`F:/Ourgame/source-assets/production/backups/v143-HeroLandingPriority298-203GREEN-v001/compiled-source-manifest.json`，581202 字节，SHA256 `5ddd83f5a16919c084870a29705ee1c0da3fbd13dec7f480330d8e61a4ac95ee`。Source 298／Production 1419 是 Root 提供且该 manifest 记录的检查点；本轮只核对以下相关实际文件，不重跑完整 203 项。

## 事实：逐状态现状

下列路径均相对 `F:/Ourgame/UnrealGame/Source/CodexDungeon/`；行号是本轮实际读取的当前文件。

| 玩家状态 | 实际事件与播放路由 | 资源及缺口 |
| --- | --- | --- |
| Ready／idle | `DungeonFighter.cpp:2068` 选择 idle；HUD 仅消费新增 journal，没有待机声产生器 | 当前无玩家呼吸、盔甲待机或循环路由；无该专属已导入声音。维持静音本身合理。 |
| Walk | `DungeonFighter.cpp:1272` 起记录合法地面移动，`:1308` 发布真实位移；`:2073`–`:2080` 按实际距离推进 gait | 没有玩家脚步声音事件／播放调用。`DungeonGroundWalkPhase.h:26` 的 Advance 仅输出取模相位，没有足落事件或跨周期计数；不能把相同动画帧每次渲染都播一声。现有 Guard STEP 是敌人石体材料，不是玩家脚步成品。 |
| 起跳 | `DungeonFighter.cpp:1313`–`:1322` 在真实请求通过后置速度 630，通知 Combat／WeaponSkills Takeoff | 没有声音 append／play，未见专属玩家起跳已导入声音。当前 StartJump 不是音频事件。 |
| 上升／Apex／下落 | `DungeonFighter.cpp:2019`–`:2022` 原重力推进；`DungeonHeroAirPresentation.h:4` 明确该 sample 是 completed owner read，不是新事件／时钟 | 当前均无声音触发。三种空中姿态不应默认各播一次；不存在已完成的玩家飞行循环声。 |
| 落地第一帧 Land4 | 实际统一批次边界为 `DungeonGameMode.cpp:1963`–`:1967`：真正从空中到 H=0，置 V=0、LandingVisualAge=0、NotifyLand。旧非绑定路径另见 `DungeonFighter.cpp:2023`–`:2029` | 两处均无声音。缺专属落地资源和单次落地事件适配。未来应在真实接地边界产生一次，不能等待截图 callback 才产生。 |
| 落地第二帧 Land5 | `DungeonFighter.cpp:1997` 仅增长 LandingVisualAge；`:1368` 把小于 .12 的地面 sample 作为 landing 展示 | 没有第二个真实接地事实。缺的是完整落地声设计；不能因 Land5 再播同一撞地声。 |
| Primary1／2／3 连击 | `DungeonFighter.cpp:664`–`:689` 消费 Combat 的真实 ActiveWindow，以 Stage+1 选择 SWD_WHOOSH_01／02／03；装备绑定时由 GameMode AppendActionAudio，旧 unbound 原型才直接 PlaySound2D | 已有三条独立 WAV／SoundWave。HUD `DungeonHUD.cpp:254`–`:261` 预载，`:365`–`:379` 按 sequence／room／年龄最多 .25s 消费，音量 .25、pitch 1。不是每个姿态帧一声，也不因 Ready 或接招重复播放。声音品质／三段重量区别仍未本轮试听。 |
| 军剑技能（相邻审计边界） | `DungeonWorldProjectiles.cpp:272`–`:330` 按 LastSkillEventId、实际新 WindowCreated 去重，`:325`–`:327` 对军剑技能复用 SWD_WHOOSH_03 | 技能有真实出手路由，但没有独立军剑技能音色。不能把复用第三段资源登记为新成品。 |
| 闪避 | `DungeonFighter.cpp:766`–`:790` 通过 Dodge.TryStart 后处理取消／Sync；`DungeonDodge.h:40`、`:146` 已有真实 Started EventId／OwnerId／ActionId | 没有 Dodge Started 到音频 journal 的消费器，也未见玩家闪避专属已导入声音。`:787` 调 ObservePendingActionAudio 只处理被取消的武器装填，不是闪避声。 |
| 受伤 | 真实非 DOT 伤害通过后，`DungeonFighter.cpp:1668`–`:1669` 直接播放 ThirdParty 的 SW_ImpactLight，音量 .45，玩家 pitch .9；`:1683`–`:1695` 再决定是否破韧／hurt 动作 | 当前是通用接触材料，不是轻甲专属撞击、独立痛呼或破韧成品。只受伤但未破韧也会播；不能按 hurt 帧再触发。DOT 在 `:1655`–`:1666` 提前 return，不播该直接接触。 |
| 死亡 | 直接致命伤仍可能播放上行通用 ImpactLight，随后 `DungeonFighter.cpp:1703`–`:1708`／GameMode OnFighterDied 处理死亡；DOT 致死 `:1660`–`:1664` 没有声音 | 未见玩家独立死亡声音事件／已导入资源。直接伤害的撞击声不是死亡完成；Guard DEATH 是敌人，不能替代玩家死亡。 |
| 换轻甲 | `DungeonGameMode.cpp:1141`–`:1149` 仅真实 PickupArmor 成功提交、非 Replayed、slot=2、实例／模板一致后产生 EQUIP_ARMOR_CLOTH_01 | 已有 cloth2.ogg 派生的 .40s 资源，轻甲与法袍同路由；中／重甲为 METAL，.32s。取消、菜单预览、重复提交不会在该分支产生成功声。完整拿取／穿甲多阶段声音仍没有。 |

## 事实：真实资源、导入和材料身份

### 军剑三段

本轮打开 WAV header 并完整读取文件 SHA，三条均与本地 manifest 相同；48kHz／mono／PCM16：

| 源文件（`F:/Ourgame/source-assets/production/audio-v001/`） | 时长／PCM 帧 | SHA256 |
| --- | --- | --- |
| AUD-SWD-WHOOSH-01__v001.wav | .190s／9120 | `6b02b1e1c2e34684151202bef53f092ba9b2350ff578ba3dbb8096fbb17f8a09` |
| AUD-SWD-WHOOSH-02__v001.wav | .210s／10080 | `c9becad05f048714bd5d3a02aeec3ba2758976bbb232431478b0001ce09453f9` |
| AUD-SWD-WHOOSH-03__v001.wav | .230s／11040 | `4b61b6c26505d5a0db6396dce7b1792f428ccb4a89de8a847abb00d6a57a6304` |

`audio-v001/manifest.json:22`–`:27` 记本地原创程序合成、无 Lost Castle／第三方采样／TTS，`:89` 标 original_procedural_local_synthesis。这是来源记录，不是对全球版权资格的外推。历史导入证据为 `F:/Ourgame/UnrealGame/Saved/Bootstrap/content-audio-v001-import.json:4`、`:29`、`:53`，结尾 `:141`–`:142` 记 17 条成功；当前实际对应 `.uasset` 文件存在。对象路径为 `/Game/Production/FirstBatch/v001/Audio/SW_AUD_SWD_WHOOSH_0N_v001.SW_AUD_SWD_WHOOSH_0N_v001`，N=1、2、3。

### 换甲

- 轻甲／法袍：`F:/Ourgame/source-assets/production/first-batch-audio-v002/wav/AUD-EQUIP-ARMOR-CLOTH-01__v002.wav`，48kHz mono PCM16／19200 帧／.40s，SHA `2c220a53e23995bdaa9d1300819440ab277a93e00b5a74c89ebbeb7dee7d49f0`。`manifest.json:552`–`:572` 的源是 Kenney RPG `cloth2.ogg`；本轮 retained OGG 与 license-copy SHA 均匹配。
- 中甲／重甲：同目录 `AUD-EQUIP-ARMOR-METAL-01__v002.wav`，48kHz mono PCM16／15360 帧／.32s，SHA `9a23a15621d072039ccec09629e4d504496c0e2e487f1d0ed0e2623885901139`。`manifest.json:733`–`:753` 的源是 Kenney Impact `impactPlate_light_000.ogg`；retained OGG／license-copy SHA 均匹配。
- 两个本地许可副本分别是 `first-batch-audio-v002/licenses/Kenney-rpg-License.txt:9`–`:13`、`Kenney-impact-License.txt:10`–`:13`，记录 CC0 和商业使用许可。本轮不联网，不作超出副本内容的许可判断。
- 实际后续导入收据 `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-batch-audio-v002-import-20261015-102740-981456.json:7`–`:10` 记 5／5 saved、success=true；`:130`／`:169` 起为两条换甲，`:162`／`:201` 记 looping=false。实际 SoundWave 文件存在，对象位于 `/Game/Production/FirstBatch/v024/AudioDedicated/`。
- 早期 source manifest 的 `engine_imported:false`／`runtime_bound:false` 是当时冻结的准备状态，不能覆盖后来的真实导入收据和当前源码路由，也不要回写历史 manifest。

### 当前受伤接触

实际直接播放对象是 `/Game/ThirdParty/Kenney/ImpactSounds/ImpactLight/SW_ImpactLight.SW_ImpactLight`；当前文件存在。`F:/Ourgame/tools/scripts/ue-import-prepared-assets.py:67` 把该对象源指向 `impactGeneric_light_000.ogg`；`F:/Ourgame/tools/scripts/audit-first-content-sfx.py:278` 也明确这条历史溯源与“没有解码当前 UAsset”的边界。本轮不解码 UAsset，也不把名称 ImpactLight 当作已证实的肉体／皮革／金属成品。

## 事实：保存的 continuation 与避免历史重播

1. `DungeonActionAudioFeedback.h:7`–`:22` 的输出 journal 保存 sequence／cue／时间／run／room／owner／action／instance／operation／revision。`DungeonGameMode.cpp:526`–`:539` 要求非零 ActionId、InstanceId、Revision，最多留 256 条；不能给跳跃虚构一个战斗 ActionId 来绕过门。
2. `DungeonRunSnapshot.h:39`–`:49` 只序列化 producer continuation／consumer history seeds：NextActionSequence、WorldHistoryThrough、WeaponCursors、StoneSeeds；不保存声音队列、播放收据、资源 UObject、墙钟或展示 epoch。
3. `DungeonRunAggregate.cpp:189`–`:194` 捕获这些游标；`:58`–`:86` 验 run／room／owner、world tail、完整 weapon event／receipt／time、已消费装填阶段与 Knight seed。`DungeonRunSnapshotCodec.cpp:883`–`:899` 精确编解码。不能为了新增声音清零这些游标。
4. `DungeonRunInstaller.cpp:134`–`:140` 要求 staging ActionAudio.Records 为空并核对游标；`:220`–`:221` 装入已保存 NextSequence／weapon cursors。`DungeonGameMode.cpp:351`–`:356` 进入 AwaitExplicitContinue、新 presentation epoch 并调用 HUD Attach。
5. `DungeonHUD.cpp:332`–`:349` 同 epoch 重复 Attach 是 no-op；新 epoch 把 ActionAudioCursor=NextActionSequence−1、WorldWeaponCursor=WorldHistoryThrough，并给 Knight 置 NextEventId−1。`:356`–`:360` 新 HUD／新 run 首次接入也从现有 tail 开始，明文禁止 replay existing journal。
6. 正常未来事件仍可播放：HUD `:365`–`:379` 先推进 sequence，再过滤 room／age／missing asset；不会下一帧重试旧记录。World 消费器 `DungeonWeaponPresentation.inl:14`–`:28` 同样先推进 cursor；仅真实射弹／火焰／有效燃烧会请求声音。
7. Guard 另有 `DungeonStoneGuardFeedback.h:92`–`:102` 的 Begin(saved)：历史只用于重建位置，明确不生成历史输出／pending Hit 授权；HUD `DungeonStoneGuardFeedbackPresentation.cpp:30`–`:37` seed 当前 LastSequence、停止旧 windup component，`:54` advance 即便 stale／missing asset。

据此，磁盘恢复不会补播已发生的换甲、三段出手、Knight 苏醒／伤害或 world emission。恢复中装填未来阶段则按原 deadline／未消费位继续产生，这是合法未来事件，不是历史重播。通用玩家受伤 PlaySound2D 本身没有 saved queue：只有未来再次实际 ApplyCombatHitInternal 才调用，恢复不会重新调用过去伤害来播放声音。本轮不宣称已有长 one-shot 会跨进程续播；PCM／音频组件游标不在存档。

## v144 target 的合法沉默与旧检查器限制

事实：当前自然下落／Land4／Land5／Ready 没有玩家音频产生器。角色在 Apex 恢复，等待、中性新 Enter、自然接地，期间不执行 E／Space／J／移动／Guard 诊断且无新的受伤或敌人声音事件时，MainSubmix 可以全程为零。Walk 本身也没有声音，source 的非零应来自真实 E 成功提交等已有声音，不能归因脚步。

全当前 Source 的真实播放入口只在 Fighter／GameMode／HUD／WeaponPresentation／GuardFeedback 中检出，没有检出 ambient／music／DustyMemories 的播放调用。默认 FirstRoom 为 `F:/Ourgame/UnrealGame/Config/DefaultEngine.ini:2`–`:3`；本地虽有第三方音乐 SoundWave，但存在资源不等于实际播放。当前 FirstRoom.umap 6756 字节的可读 name tokens 未见 Audio／Sound／Ambient／Music；这是补充静态线索，不是 UE 运行中 actor／组件枚举证明。不能承诺所有情况必然静音：Knight 靠近／原 12s fallback 会产生真实新声（`DungeonStoneKnight.h:51`、`:111`–`:115`），敌人未来攻击／伤害也可能发声；实际 target 必须报告真实新增事件与收据。

旧硬门位于 `F:/Ourgame/source-assets/production/fairytale-hero-air-v001/audio-capture-helper-candidate-v001/tooling/check-native-main-submix-v001.py`：

- `:37` 的 validate_pcm_bytes 有 require_non_silent=True 参数。
- `:46`–`:51` 对完整实际 PCM 计算 peak／RMS；要求 peak≥.001 且 RMS≥.00001（约 −60／−100dBFS）。全零因此失败。
- `:85`–`:96` 的 audit 没有把场景策略传入，`:96` 固定走默认非零要求。
- 原 UE helper `DungeonNativeMainSubmixCaptureV001.cpp:229`–`:246` 仅要求非空、完整合法 PCM 格式／大小、canonical 仅修 header BlockAlign、PCM payload 不变；它本来允许全零。

推理：NEW v144 checker 应为合法 target 明确声明“允许真实沉默”，仍完整保留原始与 canonical 字节、全部 PCM 解码、精确路径／SHA、capture controls 恢复、时长≤原 150ms 差、原帧时序，以及 target 真实新增音频事件／请求计数。可复用旧 validate_pcm_bytes(..., require_non_silent=False) 的纯检查函数，但 NEW audit 必须保留其余全部 receipt／timing 门，旧冻结文件保持不变。输出应区分 `non_silent=false` 与 `capture_valid=true`，不能声称声音反馈完成。source 若有预期真实 E 声，仍按它自己的既有信号要求验证；source 声音不能代替 target 的事件证明。禁止测试音、伪事件、补音、离线合成或以增益把沉默变非零来过门。

## 风险：Guard 命中玩家存在两条主接触路由

这是代码可见的叠层风险，未运行复现／试听，不能声称已经听到重叠：

1. `DungeonGameMode.cpp:1614` 先对玩家调用 ApplyCombatHitInternal，走 `DungeonFighter.cpp:1668`–`:1669` 的通用 ImpactLight／.45。
2. 同次实际 HP Loss>0，若 Attacker 是 Guard 且 GuardFeedbackEventId 有效，`DungeonGameMode.cpp:1616`–`:1623` 又 ConfirmHit；目标为中／重甲取 Metal，石体取 Stone，其他含无甲／轻甲／法袍取 FleshLeather。
3. `DungeonStoneGuardFeedback.h:114`–`:122` 消费同一 pending Hit 后产生专属 GUARD_HIT_FLESH_LEATHER／METAL／STONE；`DungeonStoneGuardFeedbackPresentation.cpp:70`–`:80` 再发 PlaySound2D 请求。

它们是两份不同路由的主接触层，不是 journal 重播；给玩家再加一条相同接触“hurt”会形成第三层。未来明确一次有效伤害的主接触归属，只把独立非语言痛呼作为可选另一声部。不要在本 v144 磁盘继续证明里顺带修 Guard 混音。

## 推理：后续最小兼容实施入口

这部分是实施建议，尚未改码或测试：

- 已有 Primary／技能／换甲继续使用现有 journal、原真实 Action／Instance／Operation 和所有 cursor。不要重复添加 animation-frame 回调；missing cue 不回放旧记录。
- 新闪避声音绑定真实 Dodge Started（OwnerId／ActionId／EventId／AtTime）；跳跃／落地绑定真实起跳通过和接地边界。Ready／Apex／Land5 默认没有新 one-shot 义务，先定义可听目的再增资源。
- 单独新增有明确事件种类的玩家反馈 producer／transient journal 比给跳跃伪造武器 ActionId 更兼容。保留新 producer 的 tail／last-consumed Dodge id／真实 jump-cycle 与 landing-consumed 标记；消费者只播新事件、不保存声音队列。若这些连续状态进入 Audio continuation，必须显式增加新版本／严格 codec／capture／aggregate／installer 验证与旧档策略，不能悄悄改 Schema1。
- 跳跃在 Apex 保存时应保存“此跳已起跳，尚未接地”的连续事实，恢复不播起跳，自然接地只产生一次新的落地。当前只有 H/V/LandingVisualAge，没有独立 jump-cycle event identity；HUD 观察姿态不能补造它。
- 脚步以 `DungeonFighter.cpp:1209` 的真实合格 ground distance 累积为入口，额外保存未取模的 footfall 进度／已消费 footfall cursor。当前 gait Advance 对 distance 取模会丢完整圈数，直接比较前后帧会在低帧／大步长漏声或重播；恢复 actor 的 XY install 也必须继续排除（`:553` InvalidateGroundMotion）。
- 新资源应分别准备脚步／cloth-plate movement、起跳／落地、dodge、hurt vocal／death，并保留材料选择和唯一触发。资源获取／声音制作／试听／混音是后续任务，本轮没有生成或批准新声音。

## 本轮相关实际 Source SHA256

| 文件 | 字节 | SHA256 |
| --- | --- | --- |
| DungeonFighter.cpp | 133898 | `c90846cf6255e57a96f3c66f4880d1af0a8271ff934bcaf0187698f3066c1713` |
| DungeonGameMode.cpp | 151783 | `de8dfa9fb95e213a73d5141f05637d7eb95b0aa061c61f92268237ff294570cb` |
| DungeonHUD.cpp | 123582 | `2ac1fd6393eec81245a04653f21bc6ce26bde2ce14f50ce34d847fa2f9f07b5d` |
| DungeonActionAudioFeedback.h | 1042 | `06db7fb74adf07a953c0a1046156567e6368c40958136b791da240ed44bf33d5` |
| DungeonRunAggregate.cpp | 21778 | `b9b3b9729cf05f1f4f6f696b95d6da07e5e1daad84d272aa320660b3ff138f20` |
| DungeonRunInstaller.cpp | 17028 | `0514a7ef341532d7bd22a7669a041b22fb9434a1103a6dea333bd849301a1b16` |
| DungeonRunSnapshot.h | 2990 | `34f9d5fbdf07e07c6e79aba725438146d76bb5e511f9e7826510fe1398f45771` |
| DungeonRunSnapshotCodec.cpp | 74800 | `205a7df386c440db98f8bc1afd21e5a6100b70eeca3bb050f19c08c1989c4095` |
| DungeonNativeMainSubmixCaptureV001.cpp | 22991 | `887b9ea4a6cb61319941cc7861f7dfcbc6a17ba2f4dd49c0c0a5092001e9dd2f` |
| DungeonStoneGuardFeedbackPresentation.cpp | 7002 | `e14c27facc67710e0a7343ee2a248b890f5fc1dfd9f4f3f517dffb1ca00b7cc5` |
| DungeonStoneGuardFeedback.h | 7029 | `509d352d083f004c1c1d41fc30f500605f253c685e385b01b5c3e28e53129866` |
| DungeonGroundWalkPhase.h | 1731 | `ee5a48cbb4302fbef71fbc2e9793fab52c6671bb4bd7a7c381d881cff1e63084` |
| DungeonDodge.h | 14663 | `375ee1aa3d83612a3c686f0b1a6a6d322c97e247ea957c3d7380dcd431fd9ec2` |
| DungeonHeroAirPresentation.h | 475 | `c57702242a06e748c46d189114acff292396a2515755eb1778d313e2f3685bdc` |
| DungeonWorldProjectiles.cpp | 25886 | `e3643e5f45a4339dfc7c27a5843435cd2229b9cc6c8ea04ea25815d605db8fcc` |
| DungeonWeaponPresentation.inl | 7159 | `e67750434111d2ebf9ef1add6b170dc91ae046e60214383f42808796811ea714` |

结论边界：这是静态源码／本地文件来源审计。没有 UE 新运行、设备听感、各 cue 完整信号关联或最终音频验收，正式完整单元计数不因本报告增加。
