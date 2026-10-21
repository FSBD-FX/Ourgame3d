# v004 最小准入里程碑：已知44源 / 45logical 预览

事实：已冻 v003 本来已有独立 full-preview 所需实现，不必重新造一套。此次重新核了全部36冻结文件与递归69个源/注册pins；实际读取44个512 RGBA源的像素散列，与C++每帧objectpath/SHA/RGBA/floor/authority逐条一致。9个非alias行共44unique，Dormant仅Wake0 alias，合计45logical；13state契约仍57logical/56unique。16个旧Texture包存在且pin已留，另外28个目标包尚未导入。13行 full TrialAllowed/FinalAccepted 全false，无审批被补造。

Root报告现实际partial源码已严格181G，v009正常路线右侧native与v010独立核验通过；这不代表 full v003 已UE准入。原v003的standalone pure kernel RED/GREEN仅历史独立C++证据，不冒UE运行结果。旧partial selector/profile/三组测试与v009已通过路线不改。

推理：最小正确工作是复用 v003 五个production文件、相同三组 Stage0/production测试和已经存在的最小HUDpatch；本目录不复制这些文件。保留namespace/文件名 DungeonFairytaleGuardFullV003 与独立 `-DungeonFairytaleGuardFullPreview` 接口，避免无行为理由改名和再导入。新的v004是准入交付版本，不是重写运行时接口。

唯一代码delta为 patches/full-data-retain-StompRecovery225-explicit-gap-v004.patch：在Root复制原 FullDataV003.inl 后，把 StompRecovery.PendingNativeCandidateId 改225并准确说明其源pose已接受、注册/上游29.7px join仍关闭。NativeSourceId仍0，SourcePoseApproved仍false，Frames仍空，Trial/Final仍false。该pending字段只是诊断，绝不用于绑定纹理或runtime attack ordinal；Move6、StompActive2242、StompRecovery2254仍12个明确gap，不Ready兜底，不实施MoveRig。

prepared-import/import-manifest-28-PREPARED-NOT-APPROVED-v004.json 精确列新增28个原始PNG/sourceRGBA/objectpath/目标包/settings，以及复用16包。保持原声明 namespace GuardWhole_full_v003；现有原16 GuardWhole_v001不重导、不改路径。RootImportApproved=false，root record=null。Root需要生成自己的批准manifest与当时全部旧Production精确清单，实际native导入后证明对象路径/Texture2D类/512尺寸/UI无mip/sRGB/bilinear/原source filename/新包pins/旧全量两SHA不变。当前工具 `ue-import-guard-whole16-v001.py` 硬锁16与old1210，不能把新manifest交给它冒兼容；Root可按其已验证API实现/准入28版，这里未运行导入。

root-templates 两文件只提供字段形状：逐row trial=false/final=false/approval=null，compiled snapshot/count/hash/prereg=false或null。Root须独立授权各已知行以及Dormant alias，不能把旧partial三行授权当full授权。Death后五帧是artist standing-root propagation，不称隐藏脚、COM或骨；StompWU222是FAR抬脚/NEAR支撑，开WU不同时开224/225。源接受≠动态join/足锁/最终美术接受。

后续实际UE准入由Root执行（完整文件引用表见 actual-UE-admission-sequence-PREPARED-v004.json）：

1. 从v003只加FullProfile.h/DataV003.inl、Stage0 FullPoseV003.h和三组测试。测试cpp放模块Tests/；复制Data后apply本目录一行delta。暂不加FullPresentation/DrawState/HUDpatch。真实build后原生filter `CodexDungeon.Content.FairytaleGuardFullV003 -ExpectedTests 3`，保全三组selector witness语义RED；若前提失败，先修fixture，不冒生产RED。
2. 换同v003 production FullPose；新增DrawState/Presentation；应用原v003小HUDpatch。当前实际HUD上 `git -C UnrealGame apply --check -- ../source-assets/production/fairytale-guard-v001/presentation-full-candidate-v003/patches/minimal-HUD-full-versioned-entry-v003.patch` 已exit0，Root合并前仍须核最新源。新旧HUD不得整文件覆盖。
3. 同三组真实GREEN、原partial三组保持，再严格全回归。若Root当前registry仍181，则181+3=184是计划数；实际注册数与Root完整Source/DLL/Content/报告snapshot为准，不写未来hash或编译结论。三组已包含实际kernel split原窗/128acceptedpath与blocked/85stun优先与原IR/真实UWorld终末clock、wholeaxe镜像及legacyMissingMove隔离，不改旧断言。
4. Root完成实际导入/逐row试样批准/真实source开门与编译snapshot/prereg后才运行full-known预览。新Known44动作observer此里程碑仅设计，未来需独立可执行actor/核验器准入；旧partial actor/v010 checker只支持三行DTO，不能加fullflag拿来宣称45/57覆盖。设计含五个fresh process预算、相同事件epoch计数、schema跨工具门、正常WASD/J与真实receipt，Guard无public伤害API授权。

只读复核命令：

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-guard-v001/presentation-full-candidate-v004/verify-full-v003-inputs-v004.py'
```

风险：AxeActive每50ms帧必须真实捕获，不能拉长.2s；每行ONE body scale与artist floor不自动证明接续无pop。Stomp224上身相对NEAR支撑约29.7displaypx突进、225根/远脚变化仍是独立阻断；本阶段不准入这两行。未来五次25s、30fps lossless viewport原件粗估13.8GB，不含ZIP/副本，应在真实覆盖完成或一次窗口已错过时尽快结束。原生动作observer未实施、不宣称安全通关或音频验收。本目录没有实际Source/Content/tools/Rootdocs/status/ledger改动，没有UE/UBT/import或新媒体View，formal complete units=0。
