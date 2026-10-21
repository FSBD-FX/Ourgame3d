# 猎弩四甲29门独立接线审查

## 事实：producer最终Source静态审查

本审查只读草稿、实际装备/Actor/World源以及producer新录制器，不修改Source、旧测试、脚本或归档，不启动UE/UBT。未有本29录制结果，不宣称编译或运行通过。

已核最终两文件：

- `UnrealGame/Source/CodexDungeon/DungeonXBWArmorSocketProofState.h`：2,798B，SHA256 `62b58052889250a2e6a001d4494e1e423a746e71a5641e92e4506303c4fa6a30`。
- `UnrealGame/Source/CodexDungeon/DungeonXBWArmorSocketProof.inl`：37,792B，SHA256 `731838b987166e4dc0823d21719900d7f99f1c824f2fd624be87c9a3b5eb8fb8`。

与草稿State4410/Proof7615比较，仅注释和零速度前提/真实action时间/trace补强，没有扩大gameplay写权限。实际RequiredChecks展开为common3、四甲各6、历史1、总deadline1，合计29个不同名称。

phase0唯一初始化绑定IntegrationPreview Run、starterSWD、Ammo1猎弩来源、四甲来源和两个初始HP2000静态普通QA靶，并明确设置一次QA初始Enter门。后续只有正常Enter/E/Tab/A/D/J；不直接Select、装备/攻击、改liveHP/位置/弹药或写clock。

## 事实：属性、输入与观察门

当前四件ARM001、猎弩均默认Grade0/无附魔。GM583 `ResolveStats({},Health)`经EquipmentStats307–334合并其他值/天赋/当前装备词条；基础LGT移动、ROB专注恢复不生成ActionSpeed或ReloadSpeed。Fighter的两个context分别读取Final对应属性，WA按真实snapshot计算时间。因此本夹具`.68 primary/1.10 reload`合理，不应误报为甲基础加速导致的确定失败。最终Source显式核Final两项为0，accepted speed0、ActiveAt .16、ActiveEnd .20、End .68与reload speed0/1.10，并记录Final属性；未来附魔不在这29门范围。

Tab等待实际SelectedSourceId，E走真实来源；第一甲直接slot2拾取，后续占甲E只打开slot2选择层，另freshEnter才开始.50事务。旧ArmorId/slot2实例在整个观测到的pickup期间保持，到真实deadline才接受新实例。GM替换掉出的旧甲形成额外来源；草稿不按固定Tab次数猜目标，仍循环实际Eligible/Selected来源。

绘制只在该甲Committed后，且HUD实例匹配、DrawTime不超Now且不早于该甲pickup deadline才计mask。primary/reload匹配实际ActionId和半开时间，检查body_far → armor_far → weapon → body_support → armor_near → body_near六条完整路径、160尺寸和无melee trail，过期旧甲draw不计入新甲mask。

每shot等完整primary结束才观察自动reload，核未提前补弹、唯一Emission/ReloadCompleted资源receipt、唯一world emission/hit/stop、真实目标伤害与immutable射口/RangeAnchor。最终目标HP总账及同一猎弩实例/Run/Room收口。只允许缺mask时在有效完整reload后最多全局2次补拍，最终真实Shots==8+Retries且不超过10；不通过伪造mask、扩大55秒/12秒phase deadline或抹去失败补拍。

## 推理与剩余边界

以上静态主链未见新的确定P1/P2。55秒留有动作与正常输入余量，但20ms姿态能否进入实际HUD draw及保全PNG仍由运行、导出和逐帧审看决定；global两次预算耗尽就保留失败。六条路径存在不证明衣装覆盖/遮挡/轮廓美术通过；history门也不扩成D13持久化。

既有Actor83与无甲20的真实GREEN来源分别保留，不倒填为四甲29通过。

## 最终root hook冻结静态核对

已读取 `xbw-four-armor-proof-draft-v001/root-hook-source-freeze-v001.json`（SHA256 `9eeefb97dedd1c7f97eb30f94e47325d27b0356076970ac932dad5f424a900bd`）。清单5文件逐项实际size/SHA均匹配：上述State/Proof两文件，以及ContentProbe.h 8,043B / `44dcca654ed648a4f334948de0ca4a2b89f95fc2bc7b3ba7a93b6b1884981b95`、ContentProbe.cpp 88,732B / `18dac6da2631a90507228b650a494293c333dd8a38b57e22a6e10fee09ca7a29`、verify-content-combat.ps1 53,217B / `afc056f23e46fe6e26d157685f622de592e50546a69ad016fbb195cc80b8466e`。

独立从C++ State literal/循环和PowerShell AST的专用profile block分别展开必需名称：两边各29、各29唯一、名称集合零差；PowerShell仅ParseFile，0语法错误，没有执行录制脚本。C++ Save要求实际Results数相等、全部passed且每个必需名恰一次；PS也核实际/声明名称、唯一性及passed，不仅相信报告总布尔值。

- 路由：`DungeonXBWArmorSocketProof` → 专用Tick/RequiredChecks → runtime profile `xbw_four_armor_socket_normal_inputs`。PS专用开关/同名profile、外层allowlist、主题目录和`xbw-four-armor-socket-normal-inputs.mp4`分支均已接入，没有重现无甲v001漏白名单问题。
- 互斥：PS拒绝与所有旧proof开关同用，并要求CandidateSprites；专用Tick再拒绝旧proof flags。预览flag与录制flag分开，ArmorLayerPreview不会误启旧ArmorLayerProof分支。CLI传WeaponBodyPreview、XBWReloadBodyPreview、ArmorLayerPreview，runtime导出这些事实；PS要求三者与新proof为真及capture cap60。
- 时钟/音频：CPP与PS在新flag时均60fps上限，保留真实delta；无fixedstep/慢放。StartRecordingOutput给新profile预分配64秒，录制器仍55秒总门/12秒phase门。原有.1秒firstFrame、.15秒音画时长差、原生CRC/PCM保全与双流解码门未放宽。
- 来源：PS记录实际DLL、Source和自身脚本SHA，使用独立新版本目录并拒绝覆盖。与v042旧文件对比，旧profile的必需名称、报告范围及dispatch没有改写；新增cap/音频布尔分支在新flag关闭时保持旧值，无甲20白名单及runtime guard保留。

此最终冻结静态审查未发现确定阻塞P1/P2。root随后实际UBT/83回归和四甲29录制尚无本审查读到的结果；不能用上述哈希/ParseFile或既有GREEN冒充它们已通过。

## 后续实际83回归，四甲29仍待录制

root随后报告build145926 exit0，并保存v043 `source-assets/production/backups/2026-10-15_armor29-compiled-UE83-GREEN-v043`（root登记952files/67,024,137B）。本审查已独立读取 `UnrealGame/Saved/Automation/FirstRoom-20261015-150050/index.json`：83 Success、0 Fail、0 warnings、0 notRun，报告SHA256 `b46f27bee652099fed7bb936b87df1af3094ef886619ff8b38e64dca1f442d38`。这是接入录制器后的Actor回归通过；尚没有本四甲29的实际录制/保全/原帧审看结论，Source继续冻结。

## 两次normal29实际失败分类（仅报告，未审图）

已独立读取F批 `2026-10-15_猎弩四甲双向射击装填实际换装运行_v001`、`_v002` 的runtime-report/index，没有查看尚未获本轮开放的PNG。两次DLL均为 `6711f89515c1e735d10ea9402b17aab3e80d1dd8c4c9e1237b66910e1a7c8297`。

- v001：18项实际记录、16pass/2fail；LGT双侧各1shot完成63/15，MED右1/左3shots完成63/15，耗尽global2。HVY右第1shot ready63/primary59/reload15，缺bit2；7totalshots，ROB未进入。最后wall24.4907513秒。1050电影帧+预热共1051PNG CRC与音画门通过，最大sourcegap .0327808秒。runtime-report SHA `91d8620e9bd5bba387674e9323693913acbcd2a5fa0b473a4f89ae6a0a85c6e4`。
- v002：6项实际记录、4pass/2fail；LGT右1shot63/15，左3shots ready63/primary59/reload15，仍缺bit2，global2耗尽。4totalshots，后甲未进入，最后wall12.6358020秒。468电影帧+预热共469PNG CRC与音画门通过，最大sourcegap .162531398秒、最大PNGsave .1460563秒。runtime-report SHA `6853847e4709a80c3e1753b87f1466fe1489e63cb9b6e0e372216120208cce2c`。

两次失败名均为对应primary完整mask门及`completed_within_55s`。后者由通用Fail终止时记录，不能误写成两次确实跑满55秒超时。没有证据把未进入的后甲计为通过，也不因现有CRC/音画通过而称29整体验证通过。缺20ms姿态与当前采样间隔相容，但仅凭save/gap不能证明唯一根因；root拟以独立opt-in异步原生PNG保存降低GT等待，仍保29/55秒/global2和所有动作/资源规则。并发/生命周期静态审查及实际复录另记，不改既有失败来源。
