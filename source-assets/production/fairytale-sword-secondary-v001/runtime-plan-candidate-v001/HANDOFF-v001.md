# 军剑 K Secondary8 未准入源码候选 v001

**FinalAccepted=false；runtime_not_ready=true；ReadyForAdmission=false。** 本目录仅为 Root 复合／补真实数据／复核所用。没有 actual Source/Content 修改，没有 UE 编译／启动、原生捕获、图像生成或 View。135 项主机检查不等于 UE/native 通过。

## 已制作的代码

- 新 `projected/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordSecondaryPlanV001.h`：直接消费实际 `DungeonWeaponActions::FAction`，输出与原动作共用的 3/2/3 八帧采样；不读取 J.Stage/AttackId，不用固定 FPS／0.68 新钟。边界为 Start、LockAt、LockAt 到 ActiveAt 的中点、ActiveAt、有效中点、ActiveEnd、收势 12/38／25/38、End，End 半开。速度仅通过实际绝对 deadline 体现。
- 新 `DungeonFairytaleSwordSecondaryDrawStateV001.h`：同 callback 的真实 FAction、binding、采样、57 资源就绪事实、8 槽中是否被选以及实际提交的 float 几何；没有 observer 重算“应该画了”。DrawId 保留单调值，其余在 DrawHUD 早退前、Death/Hurt 前及 restore 附着时清理。
- 新 `DungeonFairytaleSwordSecondaryPresentationV001.cpp`：新 opt-in 且真实 committed SWD+None/LGT 才拥有 K；一次 actual resolver 控制身体与甲，57 全闭包预检后才有任何 DrawTexture。None 跳过三个甲槽，实际 5 槽；LGT 为 8 槽。全缓存强引用采用已有 UPROPERTY Frames，加载只在 BeginPlay 中，放现有 FinishCompilation 前，原 startup Flush 保持不动。身体跟实际 actor root，代码没有画布内前移／收势倒退。独立剑复用 .50、(99,256)，一次 UV 镜像，近手最后盖柄。

**新增 Source 为 3 个文件。** 若在原 Source303 上准入，本模块成为 Source306；不为了旧数量断言缩并或伪装。所有源代码投影都仍在此 NEW 目录。

## Root 必须先补齐的真实数据

新 CPP 的 `Profile()` 故意返回完整空 `static const FProfile NotAdmitted;`，RuntimeReady 为 false，真实支持身份会 closed 零绘制，不能退回 Ready/J 冒充完成。**不能只翻 RuntimeReady。** Root 在实际图稿／分层／透明重构／整数装配审阅通过后，用真实完整 FProfile 替换这个整值，再做 fresh review：

1. 真实 ProfileId 和最终 source-contract JSON 的 SHA256。
2. K0…K7 每帧 Root=(256,464)、独立实测 Grip/Axis；禁止复制 258/J 标记。固定 512 作者画布、72/416 显示缩比。
3. 每帧 7 层按固定次序：BodyRest、ShoulderFar、Chest、NearArmWithoutHand、ShoulderNear、HelmetForeground、NearHand。每项都要 full object path、source-assets 相对 PNG 路径、实际 bytes、64 位小写 SHA256，共 56 条。独立剑是第 57 个闭包项，不导入 8 张不渲染的 whole Body。
4. 独立剑真实复用身份：object path `/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002`；PNG `source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png`，31902 bytes，SHA256 `2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a`。

`ProfileValid` 只校验编译 metadata 的完整性／有限标记／路径和 pin 形状，**不是文件 SHA 或 GPU 像素证明**；Root 资源准入仍必须核每个实际源文件与 uasset，随后做真正的 57 资源／实际像素原生核验。默认空 Profile 没有伪造 path、SHA、Grip 或可被误准入的 freeze。

## 与音效候选复合，禁止整文件覆盖

`exact-seams-v001.json` 是 10 个纯 insert seam，基于 CM `e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564`。投影 HUD.h／HUD.cpp／SwordPresentation 只是审阅方便；`source-roundtrip-v001.json` 证明逆移除全部插入后逐字节回到这三个原基线。**Root 正在单独接入音效候选，随后 HUD.cpp 基线会改变，不能拿本目录旧完整 HUD.cpp 覆盖 actual。** 应在音效新基线上逐条严格 count=1 插入，并再次做 compose/inverse/hash 复核。音效的 preload/gain／WorldProjectiles/ActionAudioFeedback seam 没有被本候选修改。

10 个 seam：HUD.h include、UTexture forward declaration、const trace getter、flag/trace/helper 声明；HUD.cpp 新 flag、Dodge preload 后且原 FinishCompilation 前 preload、restore 清 trace、DrawHUD 首段清 trace；SwordPresentation 在早期死亡／受击前清 trace、Air 试选后且旧 J 分支前分发。新 flag 为 `-DungeonFairytaleSwordSecondaryPreview`，还要求原 EquipmentBound flag。新 flag off 时不加载 K 数据、不改变原绘制分支。

现有 Death → Hurt → 地面 Dodge 试选 → Air 试选的实际顺序完全保留；K 在其后，J/258/Ready/Walk 在 K 之后。真正中断导致 WA.Active=false 时不复活 K；active 但过 End、坏时钟／阶段、air、死亡／hurt／dodge／换装／J 冲突，都不采样。普通 HitFlash 沿用原 tint，不新增中断。业务输入、时间、30 cm 前踏解析、伤害与接触数均未写入本模块。

## 验证事实与边界

- RED：最初 unsupported sampler 为 74 checks/55 failures；加 profile 验证后 79/56。编译环境路径和错误测试武器枚举曾各失败一次，原日志保留，不计作行为 RED。
- GREEN：`tests/run-green.cmd` 用真实 MSVC 14.38 x64、C++17、/W4 /WX 编译本候选 portable header 和实际 DungeonWeaponActions.h 依赖。`verification/green-v006-absolute-clock.txt` 为 **135 checks / 0 failures，exit0**。覆盖 base 边界、±20%真实 deadline、非零绝对 Start、End、坏钟、错误 instance/weapon、优先级与地面、None5/LGT8 选择、未来 K7 层／剑缺失导致整闭包 predicate false、未准入 profile、一次镜像几何，以及真实公开 WA kernel 的 -20/0/+20 三条八帧／完成及破韧结果。
- `verification/mutation-results-v001.json`：故意把收势 12/38 改成 11/38、跳过未来资源检查、忽略新 flag 三个独立源码副本均编译后 exit1，分别被边界／缺未来层与剑／default-off 检查发现；原候选未变。
- 一个测试 fixture 曾把理想 `.42/1.2` 当作真实收势分界，实际算式分界比它晚一个 ULP；保留失败诊断，不用 epsilon 改写半开区间，变速测试改核真实 LockAt/ActiveAt/ActiveEnd/End 和明确相内时刻。
- 主机 tests 对资源闭包只证明真实 `AllResident` predicate 的 all-or-nothing 行为；实际 UE cache、零 quad 提交、源像素、8 帧视觉衔接／观感和全混音均尚无新运行证明。新 UE CPP 也尚未由 Unreal 编译。Root 只在补真实 Profile 后做相应编译／原203原样回归／正常 K 左右、End 回接、受阻0前踏等原生测试。

没有 `candidate-freeze`，本目录只能作为**未准入输入**，不应被资源／源码准入工具自动视为 Approved。最终 Profile 会改变新增 CPP 与资产闭包，届时必须冻结真实新版本并 fresh review。
