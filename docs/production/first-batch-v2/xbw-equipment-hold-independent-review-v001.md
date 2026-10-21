# 猎弩换甲持有身份回退：独立窄审查

## 真实缺陷与RED

v004 MovieFrame00942已实际view：换甲中显示白剑，真实held仍XBW2/Ammo1、旧MED4。原帧审查和19张选帧清单保留在 `xbw-four-armor-visual-review-v004.md`，不回填旧片。

root新独立post-trace门在旧v004真实记录上运行。已读取 `evidence/xbw-equipment-hold-v001/actual-v004-RED.json` 与修正筛选后的 `actual-v004-RED-v002.json`：四次.50事务分别29/28/29/28行，共114行，跨度.4778804/.4715233/.4788637/.4686890秒，全部缺少有效held-XBW ready clip/stack而失败。正常profile29本身仍通过，新增门没有更改正式29名称或55秒/global2预算。

## HUD最终冻结静态核对

实际 `DungeonHUD.cpp` SHA256 `1ebc5b524cee3f9af8c70588be187369c0f945c41624c17347bd3c81076c543c` 与root冻结值匹配。已对照v046旧文件读取差异：

- NativeXBWHeld仅在原ReloadBodyPreview打开、玩家真实WeaponId为XBW时成立。Bound equip_weapon/equip_armor再要求当前Actor socket Supported且Ready，才进入已有原生body/weapon/armor分层路径。
- 旧甲路径继续读当前F->ArmorId，没有读欲拾取的新来源甲来提前换衣。首甲为四层无甲，后续旧甲为六层；commit后由原Actor事实自然切新甲。
- 仍通过真实资源Ready和各纹理GetResource门、统一Root/Size与原绘制顺序；只在该native XBW模式阻止generic白剑fallback。没有交易/Actor属性/资源/时钟写入，默认与其他武器路径不变。

这是明确ready持弩占位表现，不能称已新增完整穿戴机械动作或XBW全状态美术；unsupported姿态、其他preview模式未由本次窄修验收。未发现阻止当前v005验证的确定HUD P1/P2。

## 新外部oracle审查与修正

初版脚本先用weapon_instance_id==2筛选事务行，可能跳过错误held实例的观测，余下行仍能满足span门，存在确定伪通过缺口。已向root提出，root修正并保留原RED版本，重新对同一真实v004报告跑RED-v002。

最终 `tools/scripts/verify-xbw-equipment-hold.py` SHA `1ab66f5469265840d4cd45725bf95f3169e2d43c0beeeea8b4d48da28942773b` 已只读核：仅phase5+equipment_action_active选择全部实际事务行；WA/slot实例2、实际.50时长、sourceId==variant+2、真实旧甲实例、Ammo1且WA action inactive都放入逐行valid。每行再检查HUD instance/action、朝向、状态、sampleTime与精确四/六layer stack，四组都须有观测及至少.35秒span。错误held行不再被筛除。

当前固定实例/source断言来自本独立29夹具，不能将它当成任意正式Run的通用ID规则。脚本只读archive/trace，结果只写新的docs evidence文件、拒绝覆盖；记录自身及runtime-report SHA，不写归档或运行UE。正常profile29与原生像素/音画门仍需分别通过。RED-v002使用脚本1ab66f及旧runtime-report `7abb08861dfbbfc1081efc38d73f16d10bac4b4cff8d4b30a909f34cfcc84860`，114/114仍实际失败，证明旧问题没有靠改变筛选藏掉。

新版oracle与HUD最终静态审查未见新的确定阻断P1/P2。未修改Source、脚本、旧测试、归档或门槛。

## 实际回归与未验证范围

root报告build163126 exit0；本审查已独立读取strictUE `FirstRoom-20261015-163306/index.json`：83 Success、0 Fail/warnings/notRun，报告SHA `6a94576cf5883e2c738596af90836f02e03799b40679e9fcf0bc861e1ba9680e`。这是Actor回归，并非新换甲显示门或v005录像通过。

此时尚未读取v005新trace或查看其原PNG，等待真实29+post-trace门+原生捕获/保全/独立原帧证据。v004白剑与地面标签叠印问题保持原记录；完整衣装覆盖、连续机械动作/足锁、其他状态、正式来源/D13、听感和15单元完成仍不据此认证。
