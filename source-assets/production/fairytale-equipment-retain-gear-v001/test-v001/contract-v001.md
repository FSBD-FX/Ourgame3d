# Retain committed gear during actual pickup — contract / Stage0 test v001

事实：Root实际v117→v118修正了 NoArmor／LGT／MED 的真实装备显示绑定；新实录完整流程通过旧期望。但 Root 独立审图发现待提交拾取期间 Ready0 暂时无剑无甲。正确的装备ID没有直接证明装备持续可见。此新要求纠正该显示缺口，不把现有 GREEN 倒写成完成换装动作。

边界：仅显式 Bound 模式、同次有效真实绑定、当前已提交 SWD＋None或LGT，且实际 View.Action.Active 的 PickupArmor／PickupWeapon、在地面活着、没有 melee／skill／dodge，动画名为对应 equip_armor／equip_weapon 时，允许 **Ready0 gear identity placeholder**。剑仍是旧已提交实例；实际 LGT 保持 Ready0 甲，None绝不穿甲。候选目标/source/pendingInstance不能决定外观；只有真实提交改变当前装备。动作姿态仍 unsupported，后续 process-only ActionPoseSupported=false、GearPlaceholder=true 明示区别。已有 Supported 保持动作支持语义，不能为了画装备把动作伪称支持。

MED 当前缺素材且 resolver 明确 unsupported，所以 MED→原LGT 的待提交窗口继续 unsupported 无授权替身；只在重新提交LGT后显示。原实录四个 pending 窗口中，旧装备仍为合法None/LGT的前三个是本轮要保留的对象；旧MED那一个不是已识别轻甲。不会泛化walk/air/dead/hurt/skill/普通switch，也不开放非LGT或不合法实例。将来它们仍需各自动作与装备适配。

先测试：本版本只改 NativeProbe ScreenshotProcessed 的独立期望，不读未来 DrawState 新字段，不调用 resolver 当oracle，故可在真实v118旧DrawState编译。现有 NoArmor不甲、LGT supported相匹配、MED unsupported、镜像/实例/版本/clock/UI和资源检查全部保留。原 unsupported leakage 仅对严格真实 pending eligibility 改成更强规则：Supported仍false；Ready0 frame0；当前剑可见/实例正确；LGT甲7层可见；None无甲且3条body/sword/hand记录。非法或其他unsupported姿态原拒绝规则保留。

真实流程仍 E/A/E→LGT ordinary J三连→MED E+freshEnter→原LGT E+freshEnter。Tick、按键、时间、注册/提交/取消/重拾代码逐段相同。v118预期新增 pending 缺剑/缺甲语义RED；scene/输入/编译错误不能当RED。无display mismatch中止流程，保全全部phase和图；结果尚未运行，不能报真实RED。PickupWeapon被同样契约覆盖，但当前实际flow只执行PickupArmor；其真实weapon拾取证明仍null。

后续生产（等Root实际干净nativeRED再写）：只在同次合法Binding + 本契约pending成立时取现有Ready0身体/握点与甲层，通过局部 DrawGear = Supported || GearPlaceholder 使用原剑资源/绘制路径；ActionPoseSupported保留false，现有Supported不改真值。ArmorPhase仅有效LGT且StableIdle／实际Primary／GearPlaceholder，未知动作仍封闭。新字段仅process-only，不改SaveSchema/旧flags/V001/V002数据/Scale/UV/内核/时钟/SFX/输入。禁止回写整HUD或Presentation；Root独占实际Source/UE/UBT。此包没有生产实现，保留TDD实际RED→再实现次序。
