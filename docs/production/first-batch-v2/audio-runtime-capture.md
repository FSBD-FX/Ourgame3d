# 游戏混音运行录像接入

更新：2026-10-15（Asia/Shanghai）。v003/v004失败保留；v005已由根代理真实运行并通过自动音频/同步/九项玩法门。本子任务随后新增FirstUnit分支，**未build、未启动Editor/UE、未产生FirstUnit录音**。新增流程须根代理统一构建和实跑。导出、完整解码、非静音、音画时间检查与人工看片听音分别验收。

## 事实、推理与风险

- 事实：录制使用当前游戏世界的 UE 主输出 submix，不调用麦克风、系统 loopback 或其他应用音频输入。WavFile 异步导出正常返回也是 nullptr；完成回调本身不能代替文件检查。
- 推理：在独立 QA 进程中预热后开始混音与截图，按实际墙钟排列截图，展示 MP4 只使用同次运行 WAV。原始导出与规范副本均保留，副本只修已核实的 BlockAlign 头字段，PCM负载必须完全相同。
- 风险：音频线程真正开始写样本与游戏线程请求之间有延迟。截图处理回调在图像写入路径之后，也不是 GPU 呈现时刻或 sample-accurate 标记。严格时长差、首帧偏移、帧数与递增检查不变；超限即失败，不拉伸声音。仍需看片听音，不能据此认定正式美术或完整内容单元验收通过。

## v003 实证失败

保留目录：`F:/Ourgame/过程图稿与视频/2026-10-14_三近战连段运行_v003`。324张PNG、九项玩法检查通过、进程exit0，但音频及同步失败；未改写原件或旧index。

| 证据 | 实际值 | 结论 |
| --- | --- | --- |
| 原 WAV PCM fmt | PCM1、2ch、48000Hz、ByteRate192000、BlockAlign2、16bit | stereo PCM16应为BlockAlign4；严格解析器拒绝正确 |
| 原件 SHA256 | `c2be1669f9a25d9c510b12405268b8d826247a37519bff26e5f8827edaa4e914` | 修复前后只读核对一致 |
| PCM payload | 696320bytes、174080stereo frames、3.626666667s，全部样本为0 | 修头也不能通过非静音和时长门 |
| PCM SHA256 | `4de4587a2d6c66b26de7180a2fb6fd357f2bdc3b8fbe097db00049a354b8cb1f` | 内存只改byte32后完整读取，负载哈希一致；未保存v003副本 |
| 请求墙钟时长 | 12.203295100480318s | 与音频差约8.5766s，远超150ms |
| 帧/时间戳 | 324/324；开头`[0,0,1.3621548004448414]` | 数量一致但第二个戳重复；最大间隔1.3621548s |

本机UE源码确实把导出BlockAlign写死为2；主submix自动睡眠早退在录制追加样本之前，会跳过静音缓冲；后台窗口音量也可能由失焦乘数归零。后两项是与实证相符的机制解释，修复效果必须看v004实际样本、时长与PrimaryVolume，不能提前宣称声音已恢复。

## v004 实证及首截图修复

v004保留原目录，真实游戏混音已通过完整解码和非静音：48000Hz stereo PCM16、528384帧、11.008s，墙钟11.015574298799038s，差7.574ms；峰值−10.852912dBFS、RMS−40.175310dBFS、无满幅样本。原件`022B3468…F91E3C4`与规范副本`4D36C94A…D5C746C`仅byte32不同；两份PCM SHA256均为`8BEDE8A0A22DE386C8ABCCD2AC32F6651FD47D11DF64C8080F695F8205A0B024`。实际音量旁路/PrimaryVolume均1，CVar恢复回执为true；仍不能代替试听。

失败仍真实存在：312截图/312戳严格递增，最大间隔45.480ms，但首戳399.169ms超过100ms门；首条fixture trace也因累计上一帧包含预热的Delta到约399.987ms，漏过300–350ms首输入，军剑两项检查失败，其余七项通过。不得只剪掉PCM或改offset来通过。

v005改为：先保持玩法暂停，实际请求一张单独的`prewarm-viewport.png`，等截图处理完成且文件确实存在后，**在该回调中才真正调用StartRecordingOutput并设定新的单调墙钟origin**。预热PNG保留并独立记录请求/完成时刻及哈希，不计入录制帧或concat。此后首张实际录制帧保持idle，正常采集音频/戳；收到这张真实帧后再释放fixture，避免预热inclusive的首个引擎Delta参与动作。fixture输入时间每Tick直接取当前墙钟减真实录制起点，不再累计旧Delta。真实首帧仍须≤100ms，所有原阈值保持。

## 本地 API 和源码依据

均读取已安装UE5.5.4源码：

- `G:/UE_5.5/Engine/Source/Runtime/AudioMixer/Public/AudioMixerBlueprintLibrary.h:280`：`StartRecordingOutput(const UObject*, float ExpectedDuration, USoundSubmix* = nullptr)`；null目标表示主输出。284行：`StopRecordingOutput(const UObject*, EAudioRecordingExportType, const FString& Name, FString Path, USoundSubmix* = nullptr, USoundWave* = nullptr)`。
- `AudioMixer/Private/AudioMixerBlueprintLibrary.cpp:296`：WavFile调用`BeginWriteToWavFile`；仅明确传入的submix会广播回调。Start用nullptr，Stop用同一Mixer的`GetMainSubmixObject()`。
- `Engine/Private/SampleBufferIO.cpp:732`：完成回调派回GameThread，必须另查实际文件。
- `Engine/Private/Audio.cpp:2045`：ByteRate按采样率×声道×2计算；2051行BlockAlign却写死2。只允许独立副本修此已确认字段。
- `AudioMixer/Private/AudioMixerSubmix.cpp:1260`：自动睡眠早退在1489行录制追加之前。`AudioMixerDevice.cpp:1651`的`SetSubmixAutoDisable`只作用于实例，排队至音频及渲染线程，不改资产配置。
- `Engine/Private/AudioDevice.cpp:4640`：`au.DisableAppVolume=1`旁路应用失焦音量乘数。没有调用会写用户配置的`FApp::SetUnfocusedVolumeMultiplier`。
- `Engine/Private/UnrealEngine.cpp:2655`：固定步长分支跳过最大帧率等待，故不用`-UseFixedTimeStep/-FPS/-SECONDS`。
- `Engine/Private/GameViewportClient.cpp:2200`：图像处理后广播截图回调。`UnrealClient.cpp:1730`/`GameViewportClient.cpp:2131`直接检查`GIsDumpingMovie`，可由Probe预热后启动，无需加载阶段启用命令行截图。

## 修复版 Probe 行为

1. 拒绝覆盖已有runtime-report、引擎原WAV或规范WAV。保留九项原玩法检查。
2. 仅当前QA进程设置`au.DisableAppVolume=1`并保存原值；主submix实例请求`SetSubmixAutoDisable(false)`并保存原配置布尔值。未改用户INI、系统音量或资产默认值。
3. 预热至少2墙钟秒且3个Tick，保持QA玩法暂停；请求并永久保留独立预热PNG，最多等待15墙钟秒。命令行不提前启用DUMPMOVIE，避免加载阶段产生无对应戳的截图。
4. 独立预热截图实际完成后，在回调中记录新的单调起点、音频时钟、实际CVar与PrimaryVolume，真正开始主混音并启用`GIsDumpingMovie=-1`。ExpectedDuration12只是预分配提示。每次录制截图回调即时读取单调墙钟，预热图不生成录制戳；fixture时钟直接取该起点后的真实墙钟差，首张实际录制画面前继续暂停玩法。
5. 约11秒实际游戏时间后记录墙钟/音频时钟/PrimaryVolume，停止截图，请求异步原始导出`runtime-mix-engine-export.wav`。最多等待10墙钟秒；缺Mixer、超时、无文件、中断均保留失败原因。
6. 回调核对固定44字节PCM头、RIFF/data长度、PCM16/声道/采样率/ByteRate/负载对齐，只接受正确BlockAlign或已确认引擎值2。另一个数组仅修32/33字节至声道×2，确认PCM不变后写`runtime-mix.wav`。本机stereo对应4。`audio_recorded=true`仅表示取得原始与规范文件；脚本继续验完整解码及非静音。
7. 正常、失败、EndPlay均请求恢复音频控制。记录实际旁路值/PrimaryVolume、原配置、恢复请求及CVar恢复结果。submix公开API没有自动睡眠getter/完成回执，明确记为排队请求，**不伪称读到生效值**；实际完整WAV时长仍是必要实证。实例恢复也仅记排队。

## 脚本验收及版本记录

- 严格RIFF/PCM16解析不变：检查每块、全部样本、ByteRate/BlockAlign、完整负载、时长、峰值/RMS/满幅数和SHA256。非静音门仍为采样峰值≥−60dBFS且全文件RMS≥−100dBFS，不是听感验收。
- `Test-EngineExportReceipt`读取永久保留的引擎原件及规范副本，要求等长、除32/33字节外所有字节逐项相同、修正前后值合理；计算两份PCM SHA256并要求一致，两个完整文件SHA256也入index。还必须与UE文件名/修头/payload不变回执一致。
- 新增独立预热PNG签名/哈希和UE请求/完成回执核查，要求真实录制起点不早于预热完成；该图明确不是录制帧，不进入MovieFrame过滤或展示时间线。
- `audio_recorded`需完整解码、非静音、原件receipt、UE录制及完成回调同时成立。控制回执缺失、旁路未实际为1、PrimaryVolume非正、未请求恢复或未恢复CVar均单独失败。
- 时间门不放宽：真实delta；PNG与时间戳数量一致；逐项有限、非负、严格递增且在区间内；首帧偏移≤100ms；WAV与墙钟时长差≤150ms。保留原始差值、音频时钟、最大间隔，不修改旧index来“升级”历史失败。
- 按实际间隔构造concat时间线并采样30fps，首帧从请求起点保持。声音无增益/atempo/async resample/静音填充/离线替换。MP4使用与引擎原件完全相同的PCM，转AAC192k，再完整解码视频及音频两条stream。
- `[switch]CandidateSprites`默认false；开启只追加`-DungeonCandidateSprites`，index记录请求值和Probe实际解析值。v004先用基础音画。
- 最佳自动状态仍为`captured_pending_visual_audio_review`，不自动标人工看片/试听完成。不是性能测试。

## 已执行验证及待验项

- PowerShell Parser无语法错误。只读重验真实v003返回exit1，仍324帧、九项玩法通过、音频无效、时间戳不递增；新原件/控制receipt因旧版缺失也失败。原WAV哈希与此前一致，旧index未改写。
- 用真实v003 PCM在内存仅修已确认头字段，完整读取174080帧/3.626666667s且全零；负载哈希相同，仅byte32变化。未写新媒体，未拿此结果作通过证据。
- v004只读重验：PCM完整/非静音、原件receipt、真实控制值及恢复回执通过；首帧399ms和军剑两项失败原值保留。新增预热回执在旧版缺失，也正确失败，不改旧index。
- 本次没有新增mock测试。v004已实证通过音频导出/控制/规范副本成功分支；新预热截图流程、C++编译、首帧与fixture修复、最终mux仍等根代理统一build及v005实跑。

下一次由根代理统一build后执行：

```powershell
& 'F:/Ourgame/tools/scripts/verify-content-combat.ps1' -Version v005
```

只读复核，不启动UE、不编码、不修改旧索引：

```powershell
& 'F:/Ourgame/tools/scripts/verify-content-combat.ps1' -InspectArchive 'F:/Ourgame/过程图稿与视频/2026-10-14_三近战连段运行_v003'
```

v001失败、v002原型画面九项通过但silent、v003无效/静音/不同步、v004真实音频通过但首帧及两玩法检查失败，全部保留；后续失败仍显式递增版本。

## v005真实通过与画面范围修正

真实档案：`F:/Ourgame/过程图稿与视频/2026-10-15_三近战连段运行_v005/index.json`。329原帧/时间戳匹配、九项玩法全PASS；真实混音11.008s对墙钟11.000461801886559s，差7.538ms；首帧31.340ms、最大帧间隔41.646ms，无满幅样本，PCM完整非静音。原件与规范副本仅byte32变化，PCM SHA256同为`030576DA31163D8FB9EBA7E648A13F1DEB2B671FB62554255FC2AC54F001FE74`。展示MP4目标331帧，音视频双流完整解码。此后新脚本只读重验仍通过，原两WAV哈希不变。

v005开了CandidateSprites，实际军剑英雄已是候选画面，GSW/SPR仍是占位；旧版index.scope中的通用“原型”文字不准确，旧原件/索引保留不改。本次修正未来索引、runtime scope及QA LastMessage：按参数明确“军剑候选英雄”和“重剑/枪占位”，不靠更换标签修改模拟，不把候选预览记为正式美术验收。音频只做信号分析，未试听。

## 新增FirstUnit录制profile（尚未实跑）

仅`-FirstUnit`新增路径；默认benchmark的预热、主submix录制、原件/规范副本、哈希、非静音、100ms首帧/150ms时长门和mux机制保留。新增路径传`-DungeonFirstUnitProof -DungeonStoneKnightPreview`，复用同一个Probe。ExpectedDuration改为32秒预分配提示；30墙钟秒未完成必须FAIL并自然结束录制，不剪PCM、不伪造时间戳。

新档案主题为`日期_军剑轻甲单石骑状态驱动运行_版本`，与benchmark主题分别保留；源PNG、独立预热PNG、UE原WAV、规范WAV、报告及展示副本均不覆盖。独立profile要求16个明确命名检查各出现一次且全PASS，不能拿九项benchmark结果冒充。报告/索引记录实际profile、缺失或失败项、最终阶段、QA来源边界。

流程读取`Driver.State()`和`Game.GetSimulationTime()`：QA调用BeginArmorChange(LGT)等真实.5s完成；正常按D进入真实近距苏醒并等待完整.85s；冲锋锁后小幅Y位移验证不追踪，再正常Space跳跃，要求实际高度>65、仍在24半宽内、Body截停、无该AttackId命中且HP不失；等待真实ActiveEnd至RecoveryEnd满1.6s；首盾锁后正常W深入超过32半宽避开，S返回；第二盾锁后起正常J三连，按实际Recovery/AttackTime末100ms发后两次J，记录真实非破韧受击仍继续主攻、石骑第一轮48削韧不破60阈值及真实减伤；继续第二轮留下真实末击血量，正常跳跃下降时接纳空攻、尝试第二次空攻并观察未重启、落地后原动作继续自然击杀；正常左行与落地后的地面主攻衔接，检查死亡凭据及原型掉落保持一次。

按键以“按下请求→至少一个真实模拟批次推进→释放→状态确认”推进，不用固定50ms pulse。Trace区分正常controller按键请求和实际批次后的状态观察，读取精确deadline但不伪造子帧事件。实际没有命中、错过盾击/空攻时机、自然未杀死、阶段卡住或死亡均真实失败，不能直接造伤、Kill、回血或改敌人HP来通过。

边界：默认`sword`已经正常映射SWD001，没有QA强换武器。LGT仍是显式QA API换装，不能视作实际获取；奖励仍是旧原型coin/potion/axe，不按E拾取，避免自动药水回血/换斧。录制不重发OnFighterDied，死亡检查只覆盖真实死亡一次凭据与正常死后攻击期间奖励稳定，不能声称覆盖重复通知故障注入。实际来源链、存档IO、正式图声验收均未完成。

本子任务执行了PS Parser、16项C++/脚本名单只读一致性审查、owned空白/冲突检查及真实v005只读回归；这些不能代替新C++编译、FirstUnit操作成功或视觉/听感验收。根代理后续统一build后可显式运行：

```powershell
& 'F:/Ourgame/tools/scripts/verify-content-combat.ps1' -FirstUnit -CandidateSprites -Version v001
```

## FirstUnit v002 实证与新增 FirstUnitSkill（待统一编译实跑）

已只读复核真实 `F:/Ourgame/过程图稿与视频/2026-10-15_军剑轻甲单石骑状态驱动运行_v002/index.json`：原 FirstUnit 16 项全 PASS，429 原帧/戳一致，实际混音非静音且完整解码，墙钟 14.4949149005s，WAV 差 11.751766ms，首帧 27.247801ms，最大帧间隔 62.715601ms。原件、索引与展示副本保留未改；自动状态仍是 `captured_pending_visual_audio_review`，这些数据不代表人工看片或试听完成。

新增显式 `-FirstUnitSkill`，传 `-DungeonContentProof -DungeonFirstUnitProof -DungeonStoneKnightPreview -DungeonFirstUnitSkillProof`。profile 为 `first_unit_swd_skill_lgt_stone`，档案主题 `日期_军剑技能轻甲单石骑状态驱动运行_版本`，展示副本 `first-unit-swd-skill-lgt-stone.mp4`；与原 `-FirstUnit` 的主题、profile、16项名单及第二轮三连路线独立。两参数同时给出时技能 profile 优先，`-FirstUnitSkill` 自己就会启用完整 FirstUnit 基础流程。

技能分支仅在正常首三连结束后改变路线：正常 K 请求 SWD 武器技，读真实 `GetWeaponSkillAction()` 的 ActionId/Start/LockAt/ActiveAt/ActiveEnd/End/Locked/Phase；观察前锁 CD 为零，锁后绝对 deadline 为 Start+4.08；真实 recovery 中再给 fresh K，检查原 ActionId/Start/时间轴继续且未提前结束。技能完整 .68s 之后只一次正常地面 J 第一段，不缓冲后两段，再回原正常跳跃/下降空攻自然击杀/落地衔接/左行/奖励检查。

血量算术用于计划，不写入 Actor：原首三连后石骑约56.2068966HP，技能32/1.45后约34.1379310，单次J 26/1.45后约16.2068966，再由原真实下降空攻自然终结。没有直接 TryBeginWeaponSkill、ApplyHit、Kill、补血、改 HP、重新刷敌或换武器；唯一既有 QA API 例外仍是 BeginArmorChange(LGT)。单J若被中断、不是第一段、额外起段、未实际造成预期伤害或没有留下合法空攻目标，保留真实失败。

新名单为原16项加以下3项，共19项，CPP与PS已静态核对一致：

- `swd_skill_normal_k_accepted_real_timeline_and_lock_cooldown`：正常 K 接纳、实际 .08/.20/.30/.68 截止、前锁/锁后 CD 及 Start+4.08。
- `swd_skill_one_real_armored_hit_without_repeat`：真实 active 被观察、NextSubhit=1、ForwardStepIssued、独立技能期间实际石骑HP仅一次下降观察、合计32/1.45，未提前杀死目标。
- `swd_skill_full_recovery_and_fresh_k_rejected_same_action`：真实 recovery 被观察、End 前持续 active 且未授普通攻击准入、第二次 fresh K 后原 ActionId/Start 保持、完整结束且 Terminal=Completed。

`trace` 额外保存技能状态与真实 AnimationName/AnimationTime；`first_unit.swd_skill` 保存读取到的时点、实际HP前后值、单J ID与完成后HP。HP下降次数明确是 post-batch 观察，不能冒充子帧命中 receipt 或听感证据；若慢帧错过 unlocked/active/recovery 观察则真实失败，不补造事件。

验收脚本对现代 profile 要求实际检查数与明确名字各出现一次、declared名单一致、新技能 runtime flag=true；原16项不变。历史 v005 没有 profile/declared名单字段，继续按固定9个实际名字逐项检查；没有给新profile沿用该历史例外。实际只读复验 v005 benchmark9与FirstUnit v002的16项均通过。

录制6个核心函数（BeginAudioCapture/ScreenshotProcessed/RestoreAudioControls/FinishAudioCapture/AudioExported/EndPlay）与 v002 永久保存的 source snapshot 逐函数比较一致。音频/预热、原件PCM保全、非静音、100ms首帧/150ms时长差、30s失败截止和真实间隔 mux 均保留。PS Parser及19项名单检查通过；尚未运行新 C++/UE/新录制，没有新profile成功或视觉/声音验收结论。

供根代理在 Actor 技能适配与22项统一 headless GREEN 后执行：

```powershell
& 'F:/Ourgame/tools/scripts/verify-content-combat.ps1' -FirstUnitSkill -CandidateSprites -Version v001
```

FirstUnitSkill 源码冻结 SHA-256：Probe.h `6932AA7BA66E18B610C4E3B0EE519F57F2EDCA6189083BC1E287F69E084272A7`；Probe.cpp `80586B5ACC82819EDD6E34D87F9D80743DCA4FC6575A95180DAACB869692A5B7`；verify-content-combat.ps1 `87EDC805C1A943402A21ADC52F119E8AF16843D965034BF0E4A3ED58E8EDAFEB`。
